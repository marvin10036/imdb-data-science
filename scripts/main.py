import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine

# Garantir que o diretório raiz do projeto esteja no sys.path para importar o pacote src
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.scrapers.metacritic_scraper import (  # noqa: E402
    get_metacritic_critic_scores_from_id,
    list_missing_scores_for_prediction,
)


def get_engine():
    db_uri = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost/moviesdb")
    return create_engine(db_uri)


if __name__ == "__main__":
    engine = get_engine()
    missing_ids = list_missing_scores_for_prediction(engine)

    if not missing_ids:
        print("Nenhum ID faltante em ml_split_prediction_2025 para scraping.")
        exit(0)

    print(f"Encontrados {len(missing_ids)} IDs faltantes para 2025. Iniciando scraping paralelo.")
    now = datetime.now()

    scores_json_path = "data/processed/movie_scores.json"
    error_list_path = "data/errors/error_list_from_error_list.json"

    try:
        with open(scores_json_path, "r", encoding="utf-8") as f:
            scores_data = json.load(f)
    except FileNotFoundError:
        scores_data = {}

    try:
        with open(error_list_path, "r", encoding="utf-8") as f:
            error_data = json.load(f)
    except FileNotFoundError:
        error_data = {}

    collected = []
    max_workers = min(8, len(missing_ids))

    def fetch_one(imdb_id: str):
        _, scores = get_metacritic_critic_scores_from_id(imdb_id)
        if not scores:
            raise ValueError("Scraping não retornou notas.")
        return imdb_id, scores

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in missing_ids}
        for future in as_completed(futures):
            imdb_id = futures[future]
            try:
                imdb_id, scores = future.result()
                scores_data[imdb_id] = scores
                collected.append(imdb_id)
                print(f"✅ {imdb_id}: {len(scores)} reviews")
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️  Falha ao coletar {imdb_id}: {exc}")
                error_data[imdb_id] = str(exc)

    # Persistir resultados
    with open(scores_json_path, "w", encoding="utf-8") as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)

    with open(error_list_path, "w", encoding="utf-8") as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)

    elapsed = datetime.now() - now
    print(f"Scraping concluído. Coletados {len(collected)} títulos em {elapsed}.")
