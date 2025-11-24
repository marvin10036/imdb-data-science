# DB para Notebooks de ML - Guia de Uso

Guia rápido para criar e popular o PostgreSQL que alimenta `machine-learning/notebooks/01_eda.ipynb`.

## 📦 Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ e virtualenv ativada (`.venv`)
- Dependências: `pip install -r requirements.txt`
- Dados já coletados:
  - `data/raw/movies_catalog_oscar_and_popular_2000_2025.csv`
  - `data/processed/movie_scores.json` (gerado pelo `src/database/db_unifier.py`)
  - `data/errors/error_list_from_error_list.json` (se existir, para ignorar IDs problemáticos)

## 🐘 Subir o PostgreSQL com schema

Execute na raiz do projeto:

```bash
docker run -d \
  --name movies-postgres \
  -e POSTGRES_DB=moviesdb \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -v "$(pwd)/sql/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro" \
  -p 5432:5432 \
  postgres:16
```

- O `schema.sql` cria tabelas, índices e views (`ml_training_dataset`, `ml_split_*`).
- Verifique se está rodando: `docker ps --filter name=movies-postgres`.

## 🗄️ Popular o banco

Ainda na raiz, com o container ativo:

```bash
source .venv/bin/activate  # se ainda não estiver
python scripts/populate_db.py
```

O script:
- Lê o CSV, o JSON de notas e ignora IDs presentes em `data/errors/error_list_from_error_list.json`.
- Insere domínios (gêneros, países, idiomas, pessoas) e relacionamentos.
- Insere amostras de notas em `rating_samples`.
- Cria o dataset de features via views (ex.: `ml_training_dataset`).

## 🔌 Variáveis de ambiente (.env)

`machine-learning/src/data_loader.py` lê estas variáveis (com defaults mostrados):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=moviesdb
DB_USER=postgres
DB_PASSWORD=postgres
```

Crie um `.env` na raiz se precisar de credenciais diferentes.

## ✅ Testar conexão e contagem básica

```bash
python machine-learning/src/data_loader.py
```

Saída esperada (resumo):
- Versão do PostgreSQL
- Contagem de filmes (`movies`)
- Contagem de indicados ao Oscar
- Faixa de anos

## 📒 Usar no notebook `01_eda.ipynb`

1. Certifique-se de que o container `movies-postgres` está rodando e o `.env` está configurado.
2. Abra o notebook: `jupyter notebook machine-learning/notebooks/01_eda.ipynb`.
3. As células que chamam `load_ml_dataset()` e demais funções em `machine-learning/src/data_loader.py` irão puxar direto da view `ml_training_dataset`.
4. Se quiser cachear para CSV durante a EDA, use `load_ml_dataset(cache_csv=True)` (salva em `data/processed/ml_dataset_cache.csv`).

## 🛠️ Troubleshooting

- **Porta 5432 em uso:** altere `-p 5432:5432` para outra porta e ajuste `DB_PORT` no `.env`.
- **Falha de autenticação:** confira `POSTGRES_USER/POSTGRES_PASSWORD` no `docker run` e no `.env`.
- **Schema não carregado:** remova o container (`docker rm -f movies-postgres`) e recrie com o bind do `sql/schema.sql`.
- **Dados ausentes na EDA:** confirme que `scripts/populate_db.py` rodou sem erros e que `data/processed/movie_scores.json` existe.
