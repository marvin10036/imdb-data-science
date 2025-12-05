"""
DB Unifier - Otimizado para Performance e Confiabilidade

Script para coletar scores do Metacritic para filmes do catálogo IMDb.
Inclui: retry automático, checkpoint/resume, progress bars, logging estruturado.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from pandas import read_csv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm

from data_collection_scripts.metacritic_scraper import get_metacritic_critic_scores_from_id

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

MAX_WORKERS = 8  # Threads paralelas (ajuste conforme necessário)
SAVE_INTERVAL = 2  # Salvar a cada N filmes processados
RETRY_ATTEMPTS = 5  # Tentativas de retry
RETRY_MIN_WAIT = 10  # Segundos mínimos entre retries
RETRY_MAX_WAIT = 25  # Segundos máximos entre retries

CSV_FILE = "data/raw/movies_catalog_oscar_and_popular_2000_2025.csv"
OUTPUT_JSON = "data/processed/movie_scores.json"
ERROR_JSON = "data/errors/error_list.json"
ERROR_RETRY_JSON = "data/errors/error_list_from_error_list.json"
ERROR_RETRY_OUTPUT = "data/processed/movie_scores_from_error_list.json"

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configura logging estruturado com arquivo e console."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"db_unifier_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def load_existing_json(filepath: str) -> Dict:
    """Carrega JSON existente ou retorna dicionário vazio."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✓ Carregado {len(data)} registros de {filepath}")
                return data
        except json.JSONDecodeError:
            logger.warning(f"⚠ Arquivo {filepath} corrompido, iniciando do zero")
            return {}
    return {}

def save_json(data: Dict, filepath: str):
    """Salva dados em JSON de forma segura."""
    temp_file = f"{filepath}.tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, filepath)  # Atomic replace
    except Exception as e:
        logger.error(f"✗ Erro ao salvar {filepath}: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

def validate_csv(csv_path: str) -> Tuple[bool, str]:
    """Valida se o CSV existe e tem a coluna necessária."""
    if not os.path.exists(csv_path):
        return False, f"Arquivo {csv_path} não encontrado"
    
    try:
        df = read_csv(csv_path, nrows=1)
        if "ID IMDb" not in df.columns:
            return False, f"Coluna 'ID IMDb' não encontrada. Colunas: {list(df.columns)}"
        return True, "OK"
    except Exception as e:
        return False, f"Erro ao ler CSV: {e}"

# ============================================================================
# FUNÇÃO PRINCIPAL DE SCRAPING (com retry)
# ============================================================================

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
def fetch_one(imdb_id: str) -> Tuple[str, str, List[int]]:
    """
    Busca scores do Metacritic para um filme.
    
    Inclui retry automático para erros de conexão/timeout.
    
    Returns:
        (imdb_id, movie_name, scores_list)
    """
    name, scores = get_metacritic_critic_scores_from_id(imdb_id)
    return imdb_id, name, scores

# ============================================================================
# FUNÇÃO PRINCIPAL - PROCESSAR TODOS OS FILMES
# ============================================================================

def get_all_movies_scores():
    """
    Processa todos os filmes do CSV, coletando scores do Metacritic.
    
    Features:
    - Checkpoint/Resume: continua de onde parou
    - Retry automático: 3 tentativas com backoff exponencial
    - Progress bar: visualização do progresso
    - I/O otimizado: salva apenas a cada N filmes
    - Logging estruturado: arquivo + console
    """
    logger.info("=" * 60)
    logger.info("INICIANDO COLETA DE SCORES DO METACRITIC")
    logger.info("=" * 60)
    
    # 1. Validar CSV
    valid, msg = validate_csv(CSV_FILE)
    if not valid:
        logger.error(f"✗ Validação falhou: {msg}")
        return
    logger.info(f"✓ CSV validado: {CSV_FILE}")
    
    # 2. Carregar dados existentes (checkpoint)
    current_json = load_existing_json(OUTPUT_JSON)
    error_list = list(load_existing_json(ERROR_JSON).keys()) if os.path.exists(ERROR_JSON) else []
    
    # 3. Ler lista de IDs do CSV
    df = read_csv(CSV_FILE)
    all_imdb_ids = df["ID IMDb"].dropna().astype(str).tolist()
    logger.info(f"✓ Total de filmes no CSV: {len(all_imdb_ids)}")
    
    # 4. Filtrar IDs já processados
    ids_to_process = [
        imdb_id for imdb_id in all_imdb_ids 
        if imdb_id not in current_json
    ]
    logger.info(f"✓ Filmes já processados: {len(all_imdb_ids) - len(ids_to_process)}")
    logger.info(f"✓ Filmes restantes: {len(ids_to_process)}")
    
    if not ids_to_process:
        logger.info("✓ Todos os filmes já foram processados!")
        return
    
    # 5. Processar em paralelo com progress bar
    start_time = datetime.now()
    success_count = 0
    error_count = len(error_list)
    save_counter = 0
    
    max_workers = min(MAX_WORKERS, len(ids_to_process))
    logger.info(f"✓ Iniciando processamento com {max_workers} threads")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in ids_to_process}
        
        with tqdm(total=len(ids_to_process), desc="🎬 Processando filmes", unit="filme") as pbar:
            for future in as_completed(futures):
                imdb_id = futures[future]
                
                try:
                    imdb_id, name, scores = future.result()
                    current_json[imdb_id] = scores
                    success_count += 1
                    save_counter += 1
                    
                    pbar.set_postfix({
                        'sucesso': success_count,
                        'erros': error_count,
                        'nome': name[:30] if name else 'N/A'
                    })
                    
                    # Salvar periodicamente
                    if save_counter >= SAVE_INTERVAL:
                        save_json(current_json, OUTPUT_JSON)
                        save_counter = 0
                    
                except ConnectionError as e:
                    logger.warning(f"⚠ Erro de conexão em {imdb_id} após {RETRY_ATTEMPTS} tentativas: {e}")
                    error_list.append(imdb_id)
                    error_count += 1
                    
                except TimeoutError as e:
                    logger.warning(f"⚠ Timeout em {imdb_id} após {RETRY_ATTEMPTS} tentativas: {e}")
                    error_list.append(imdb_id)
                    error_count += 1
                    
                except ValueError as e:
                    logger.error(f"✗ Erro de dados em {imdb_id}: {e}")
                    error_list.append(imdb_id)
                    error_count += 1
                    
                except Exception as e:
                    logger.error(f"✗ Erro inesperado em {imdb_id}: {e}")
                    error_list.append(imdb_id)
                    error_count += 1
                
                pbar.update(1)
    
    # 6. Salvar resultados finais
    save_json(current_json, OUTPUT_JSON)
    
    if error_list:
        error_dict = {imdb_id: None for imdb_id in error_list}
        save_json(error_dict, ERROR_JSON)
    
    # 7. Estatísticas finais
    elapsed = datetime.now() - start_time
    total_processed = success_count + error_count
    success_rate = (success_count / total_processed * 100) if total_processed > 0 else 0
    
    logger.info("=" * 60)
    logger.info("PROCESSAMENTO CONCLUÍDO")
    logger.info("=" * 60)
    logger.info(f"✓ Tempo total: {elapsed}")
    logger.info(f"✓ Filmes processados: {total_processed}")
    logger.info(f"✓ Sucessos: {success_count}")
    logger.info(f"✗ Erros: {error_count}")
    logger.info(f"✓ Taxa de sucesso: {success_rate:.1f}%")
    logger.info(f"✓ Velocidade: {total_processed / elapsed.total_seconds():.2f} filmes/segundo")
    logger.info(f"✓ Resultados salvos em: {OUTPUT_JSON}")
    if error_list:
        logger.info(f"⚠ Lista de erros salva em: {ERROR_JSON}")

# ============================================================================
# FUNÇÃO SECUNDÁRIA - REPROCESSAR ERROS
# ============================================================================

def get_movies_scores_that_return_an_error():
    """
    Reprocessa apenas os filmes que deram erro anteriormente.
    
    Lê ERROR_RETRY_JSON e tenta processar novamente com retry.
    """
    logger.info("=" * 60)
    logger.info("REPROCESSANDO FILMES COM ERRO")
    logger.info("=" * 60)
    
    if not os.path.exists(ERROR_RETRY_JSON):
        logger.error(f"✗ Arquivo {ERROR_RETRY_JSON} não encontrado")
        logger.info(f"Dica: Renomeie {ERROR_JSON} para {ERROR_RETRY_JSON}")
        return
    
    # Carregar listas
    with open(ERROR_RETRY_JSON, 'r', encoding='utf-8') as f:
        error_dict = json.load(f)
        error_ids = list(error_dict.keys())
    
    current_json = load_existing_json(ERROR_RETRY_OUTPUT)
    
    logger.info(f"✓ Total de erros a reprocessar: {len(error_ids)}")
    
    # Filtrar já processados
    ids_to_retry = [imdb_id for imdb_id in error_ids if imdb_id not in current_json]
    logger.info(f"✓ Já reprocessados: {len(error_ids) - len(ids_to_retry)}")
    logger.info(f"✓ Restantes: {len(ids_to_retry)}")
    
    if not ids_to_retry:
        logger.info("✓ Todos os erros já foram reprocessados!")
        return
    
    # Processar
    start_time = datetime.now()
    success_count = 0
    error_count = 0
    remaining_errors = []
    save_counter = 0
    
    max_workers = min(MAX_WORKERS, len(ids_to_retry))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in ids_to_retry}
        
        with tqdm(total=len(ids_to_retry), desc="🔄 Reprocessando erros", unit="filme") as pbar:
            for future in as_completed(futures):
                imdb_id = futures[future]
                
                try:
                    imdb_id, name, scores = future.result()
                    current_json[imdb_id] = scores
                    success_count += 1
                    save_counter += 1
                    
                    pbar.set_postfix({
                        'recuperados': success_count,
                        'ainda com erro': error_count
                    })
                    
                    if save_counter >= SAVE_INTERVAL:
                        save_json(current_json, ERROR_RETRY_OUTPUT)
                        save_counter = 0
                    
                except Exception as e:
                    logger.error(f"✗ Erro persistente em {imdb_id}: {e}")
                    remaining_errors.append(imdb_id)
                    error_count += 1
                
                pbar.update(1)
    
    # Salvar resultados
    save_json(current_json, ERROR_RETRY_OUTPUT)
    
    if remaining_errors:
        error_dict = {imdb_id: None for imdb_id in remaining_errors}
        save_json(error_dict, ERROR_RETRY_JSON)
    
    # Estatísticas
    elapsed = datetime.now() - start_time
    total = success_count + error_count
    recovery_rate = (success_count / total * 100) if total > 0 else 0
    
    logger.info("=" * 60)
    logger.info("REPROCESSAMENTO CONCLUÍDO")
    logger.info("=" * 60)
    logger.info(f"✓ Tempo total: {elapsed}")
    logger.info(f"✓ Filmes recuperados: {success_count}")
    logger.info(f"✗ Ainda com erro: {error_count}")
    logger.info(f"✓ Taxa de recuperação: {recovery_rate:.1f}%")
    logger.info(f"✓ Resultados salvos em: {ERROR_RETRY_OUTPUT}")
    if remaining_errors:
        logger.info(f"⚠ Erros persistentes salvos em: {ERROR_RETRY_JSON}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--retry-errors":
        get_movies_scores_that_return_an_error()
    else:
        get_all_movies_scores()