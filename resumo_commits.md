# Relatório Detalhado de Alterações

## 1. `chore: adiciona arquivo .gitignore`

- **[Adicionado]** `.gitignore`

## 2. `refactor: reestrutura código fonte para arquitetura modular`

- **[Deletado]** `db_unifier.py`
- **[Renomeado]** `main.py` → `scripts/main.py`
- **[Adicionado]** `scripts/populate_db.py`
- **[Adicionado]** `src/__init__.py`
- **[Adicionado]** `src/database/__init__.py`
- **[Adicionado]** `src/database/db_unifier.py`
- **[Adicionado]** `src/processors/__init__.py`
- **[Renomeado]** `scores_processor.py` → `src/processors/scores_processor.py`
- **[Adicionado]** `src/scrapers/__init__.py`
- **[Renomeado]** `metacritic_scrapper.py` → `src/scrapers/metacritic_scraper.py`
- **[Adicionado]** `src/utils/__init__.py`

## 3. `chore: organiza arquivos de dados e assets`

- **[Renomeado]** `extractor_imdb.zip` → `data/archives/extractor_imdb.zip`
- **[Renomeado]** `imdb-rails.zip` → `data/archives/imdb-rails.zip`
- **[Adicionado]** `data/errors/error_list_from_error_list.json`
- **[Renomeado]** `movie_scores.json` → `data/processed/movie_scores.json`
- **[Renomeado]** `movies_catalog_oscar_and_popular_2000_2025.csv` → `data/raw/movies_catalog_oscar_and_popular_2000_2025.csv`
- **[Deletado]** `unavailable_metacritic_list.json`

## 4. `feat: adiciona estrutura e notebooks do módulo de machine learning`

- **[Adicionado]** `machine-learning/.env.example`
- **[Adicionado]** `machine-learning/diagrams/diagrama-de-fluxo-completo.mmd`
- **[Adicionado]** `machine-learning/documentation/EDA_INSIGHTS.md`
- **[Adicionado]** `machine-learning/documentation/FEATURE_ANALYSIS.md`
- **[Adicionado]** `machine-learning/documentation/FOCUSED_ROADMAP.md`
- **[Adicionado]** `machine-learning/documentation/diagrams/01_er_diagram.mmd`
- **[Adicionado]** `machine-learning/documentation/diagrams/02_data_flow.mmd`
- **[Adicionado]** `machine-learning/documentation/diagrams/03_ml_pipeline.mmd`
- **[Adicionado]** `machine-learning/documentation/tasks/implementation_plan.md`
- **[Adicionado]** `machine-learning/documentation/tasks/task_checklist.md`
- **[Adicionado]** `machine-learning/notebooks/01_eda.ipynb`
- **[Adicionado]** `machine-learning/reports/figures/class_balance.png`
- **[Adicionado]** `machine-learning/reports/figures/correlation_matrix.png`
- **[Adicionado]** `machine-learning/reports/figures/missing_values.png`
- **[Adicionado]** `machine-learning/reports/figures/nominated_vs_not_nominated.png`
- **[Adicionado]** `machine-learning/reports/figures/numeric_distributions.png`
- **[Adicionado]** `machine-learning/reports/figures/temporal_distribution.png`
- **[Adicionado]** `machine-learning/reports/figures/top_genres.png`
- **[Adicionado]** `machine-learning/src/__init__.py`
- **[Adicionado]** `machine-learning/src/data_loader.py`
- **[Adicionado]** `machine-learning/src/utils.py`

## 5. `feat: adiciona scripts SQL de esquema do banco`

- **[Adicionado]** `sql/schema.sql`

## 6. `docs: adiciona documentação técnica e diagramas`

- **[Adicionado]** `docs/db_unifier_guide.md`
- **[Adicionado]** `docs/directory_structure.md`
- **[Adicionado]** `docs/er_diagram.png`

## 7. `build: atualiza lista de dependências do projeto`

- **[Adicionado]** `requirements.txt`

## 8. `chore: reorganiza notebooks de análise e testes`

- **[Renomeado]** `Inicial.ipynb` → `notebooks/01_exploratory_analysis.ipynb`
- **[Adicionado]** `tests/__init__.py`

## 9. `chore: limpeza de arquivos temporários e caches antigos`

- **[Deletado]** `__pycache__/metacritic_scrapper.cpython-313.pyc`
- **[Deletado]** `__pycache__/scores_processor.cpython-313.pyc`
