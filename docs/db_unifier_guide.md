# DB Unifier - Guia de Uso

## 📦 Instalação de Dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

## 🚀 Como Usar

### Primeira Execução - Processar Todos os Filmes

```bash
python3 db_unifier.py
```

O script irá:

- ✅ Validar o arquivo CSV
- ✅ Carregar progresso anterior (se existir)
- ✅ Processar apenas filmes não processados
- ✅ Salvar resultados a cada 10 filmes
- ✅ Exibir barra de progresso visual
- ✅ Gerar logs em `logs/db_unifier_TIMESTAMP.log`
- ✅ Salvar resultados em `movie_scores.json`
- ✅ Salvar lista de erros em `error_list.json`

### Reprocessar Filmes com Erro

```bash
# 1. Renomeie o arquivo de erros
mv error_list.json error_list_from_error_list.json

# 2. Execute em modo retry
python3 db_unifier.py --retry-errors
```

## ⚙️ Configurações

No topo do arquivo `db_unifier.py`:

```python
MAX_WORKERS = 16        # Threads paralelas (padrão: 16)
SAVE_INTERVAL = 10      # Salvar a cada N filmes (padrão: 10)
RETRY_ATTEMPTS = 3      # Tentativas de retry (padrão: 3)
RETRY_MIN_WAIT = 2      # Segundos mínimos entre retries (padrão: 2)
RETRY_MAX_WAIT = 10     # Segundos máximos entre retries (padrão: 10)
```

### Ajuste de Performance

**Sistema rápido / boa conexão:**

```python
MAX_WORKERS = 32        # Mais threads
SAVE_INTERVAL = 20      # Salvar menos frequentemente
```

**Sistema lento / conexão instável:**

```python
MAX_WORKERS = 8         # Menos threads
SAVE_INTERVAL = 5       # Salvar mais frequentemente
RETRY_ATTEMPTS = 5      # Mais tentativas
```

## 📊 Arquivos Gerados

| Arquivo                             | Descrição                          |
| ----------------------------------- | ---------------------------------- |
| `movie_scores.json`                 | Scores coletados com sucesso       |
| `error_list.json`                   | IDs que falharam após 3 tentativas |
| `logs/db_unifier_*.log`             | Logs detalhados de execução        |
| `movie_scores_from_error_list.json` | Scores recuperados no retry        |

## ✨ Recursos Implementados

### 1. **Checkpoint/Resume**

- Interrompa o script a qualquer momento (Ctrl+C)
- Execute novamente - continua de onde parou
- Progresso salvo automaticamente

### 2. **Retry Automático**

- 3 tentativas para erros de conexão/timeout
- Backoff exponencial (espera crescente entre tentativas)
- Apenas erros recuperáveis são retry

### 3. **Progress Bar Visual**

```
🎬 Processando filmes: 45%|████████  | 450/1000 [05:23<06:35, 1.39filme/s]
sucesso: 445, erros: 5, nome: The Shawshank Redemption
```

### 4. **Logging Estruturado**

```
2025-11-23 21:15:32 - INFO - ✓ Total de filmes no CSV: 1000
2025-11-23 21:15:32 - INFO - ✓ Filmes já processados: 450
2025-11-23 21:15:32 - INFO - ✓ Filmes restantes: 550
```

### 5. **Estatísticas Finais**

```
✓ Tempo total: 0:15:42
✓ Filmes processados: 1000
✓ Sucessos: 985
✗ Erros: 15
✓ Taxa de sucesso: 98.5%
✓ Velocidade: 1.06 filmes/segundo
```

## 🔧 Troubleshooting

### Erro: "Arquivo CSV não encontrado"

- Verifique se `movies_catalog_oscar_and_popular_2000_2025.csv` está no diretório

### Erro: "Coluna 'ID IMDb' não encontrada"

- Verifique o nome exato da coluna no CSV
- Altere `CSV_FILE` no script se necessário

### Script muito lento

- Reduza `MAX_WORKERS` (pode estar sobrecarregando o site)
- Verifique sua conexão de internet
- Analise os logs para identificar gargalos

### Muitos erros de conexão

- Aumente `RETRY_MIN_WAIT` e `RETRY_MAX_WAIT`
- Reduza `MAX_WORKERS`
- Verifique se o Metacritic está bloqueando requisições

## 📈 Melhorias de Performance

Comparado com a versão original:

| Métrica    | Antes        | Depois              | Melhoria             |
| ---------- | ------------ | ------------------- | -------------------- |
| I/O disk   | A cada filme | A cada 10 filmes    | **10x menos I/O**    |
| Threads    | 8            | 16                  | **2x paralelismo**   |
| Retry      | Nenhum       | 3 tentativas        | **Menos erros**      |
| Checkpoint | Não          | Sim                 | **Resume funcional** |
| Logging    | Print básico | Arquivo estruturado | **Debugging fácil**  |

**Tempo estimado** (1000 filmes):

- Antes: ~2-4 horas
- Depois: ~20-40 minutos

## 🎯 Próximos Passos

Após coletar todos os scores, você pode:

1. **Processar os dados estatísticos:**

```python
from scores_processor import features_from_scores_map
import json

with open('movie_scores.json') as f:
    scores_by_film = json.load(f)

df_features = features_from_scores_map(scores_by_film)
print(df_features.round(3))
```

2. **Exportar para CSV:**

```python
df_features.to_csv('movie_features.csv')
```

3. **Análise de dados com pandas/matplotlib**
