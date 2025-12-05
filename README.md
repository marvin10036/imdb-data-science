# IMDb Oscar Prediction (INE5687)

Projeto da disciplina **INE5687 - Projeto em Ciência de Dados** cujo objetivo é prever quais filmes serão indicados ao Oscar (foco em Melhor Filme) a partir de dados do IMDb e das notas de críticos no Metacritic.

## Visão geral
- Coleta de dados do IMDb (API/CSV) e scraping do Metacritic para notas detalhadas de críticos.
- Construção de banco PostgreSQL com esquema normalizado e views específicas para Machine Learning.
- Pipeline de notebooks que cobre EDA, baselines, modelos avançados (XGBoost/CatBoost) e tuning final para gerar as previsões de 2025.
- ER model disponível em `docs/er_diagram.png` e diagramas de fluxo em `machine-learning/diagrams/`.

## Estrutura do projeto
- `data_base_construction/`: scripts de coleta (scraping), unificação e carga no PostgreSQL (`schema.sql`, `db_unifier.py`, `populate_db.py`, `data_loader.py`).
- `machine-learning/`: notebooks (`01_eda` … `05_master_pipeline`), utilitários (`src/utils.py`), documentação de EDA/feature set e figuras em `reports/figures/`.
- `docs/`: guias rápidos (`db_ml_setup_guide.md`, `db_unifier_guide.md`, `directory_structure.md`) e ER diagram.
- `requirements.txt`: dependências (pandas, scikit-learn, XGBoost, CatBoost, Playwright, etc.).

## Pipeline de dados
1. **Catálogo IMDb**  
   - Fonte: API/arquivos do IMDb (non-commercial datasets).  
   - Armazenado em `data/raw/movies_catalog_oscar_and_popular_2000_2025.csv`, cobrindo filmes populares e indicados de 2000–2025.
2. **Scraping Metacritic** (`data_base_construction/data_collection_scripts/`)  
   - `metacritic_scraper.py` + Playwright coletam todas as notas de críticos.  
   - `db_unifier.py`: execução paralela com retry/backoff, checkpoint/resume e logs; salva `data/processed/movie_scores.json` e `data/errors/error_list*.json`.  
   - `scores_processor.py`: limpa as notas e gera estatísticas robustas (trimmed mean, IQR, MAD, buckets por cor, entropia).
3. **Banco de dados** (`schema.sql`)  
   - Tabelas: `movies`, `movie_box_office`, `genres`, `movie_genres`, `people`, `movie_people`, `countries`, `languages`, `rating_samples`.  
   - Views derivadas:  
     - `movie_rating_stats`: estatísticas das notas do Metacritic.  
     - `ml_training_dataset`: features prontas para ML, incluindo:  
       - Popularidade: `imdb_rating`, `imdb_votes`, `box_office_rank_in_year`, z-scores por ano (`votes_normalized_by_year`, `rating_normalized_by_year`).  
       - Qualidade crítica: `n_samples`, `mean_score`, `median_score`, `stddev_score`, `p90_score`.  
       - Complexidade/escope: contagens de gêneros, países, idiomas, diretores, roteiristas e elenco.  
       - Pedigree: `director_prev_nominations`, `cast_prev_nominations`.  
       - Gêneros “Oscar-bait”: `is_drama`, `is_biography`, `is_history`.  
       - Rótulo: `label` (indicados = 1, não indicados = 0).  
     - Splits temporais para evitar data leakage: `ml_split_train (2000-2019)`, `ml_split_validation (2020-2022)`, `ml_split_test (2023-2024)`, `ml_split_prediction_2025`.
4. **Carga no banco** (`db_populate_scipts/populate_db.py`)  
   - Lê o CSV e as notas do Metacritic, resolve domínios (gêneros, países, idiomas, pessoas) e insere amostras de notas em `rating_samples`.
5. **Acesso aos dados** (`db_populate_scipts/data_loader.py`)  
   - Funções para conectar ao PostgreSQL e carregar `ml_training_dataset` e dados auxiliares diretamente nos notebooks; suporta `.env` (exemplo em `machine-learning/.env.example`).

## Pipeline de Machine Learning
- **01_eda.ipynb**: inspeção inicial (balanceamento 1:16 desfavorável aos indicados; quase nenhum missing; metascore e ratings do Metacritic bem completos).  
- **02_modeling_baseline.ipynb**: baseline com Logistic Regression e Random Forest; métricas em F1/ROC-AUC no split de validação.  
- **03_advanced_modeling.ipynb**: XGBoost e CatBoost comparados aos baselines.  
- **04_final_model_tuning.ipynb**: CatBoost refinado com threshold ótimo para maximizar Recall.  
- **05_master_pipeline.ipynb**: pipeline definitivo (treino 2000–2019, validação 2020–2022, teste 2023–2024, predição 2025).

### Conjunto de features (modelo final)
Referência em `machine-learning/documentation/FEATURE_ANALYSIS.md`:
- Popularidade normalizada por ano (`box_office_rank_in_year`, `votes_normalized_by_year`, `rating_normalized_by_year`).
- Complexidade/escopo (`num_genres`, `num_countries`, `num_languages`, `num_cast`).
- Pedigree (`director_prev_nominations`, `cast_prev_nominations`).
- Gêneros-chave (`is_drama`, `is_biography`, `is_history`).
- Consenso crítico (`n_samples`, `mean_score`, `median_score`, `stddev_score`, proporções por faixa de Metacritic).

### Resultados atuais (05_master_pipeline)
- **Validação (2020–2022):** ROC-AUC 0.9555; threshold ótimo ≈ 0.0752 garantindo Recall ≈ 0.88 (macro F1 ≈ 0.80).  
- **Teste holdout (2023–2024):** ROC-AUC 0.9595; Precision 0.34 / Recall 0.85 / F1 0.49 para indicados, Accuracy 0.88.  
- Modelo escolhido: **CatBoost**, priorizando Recall alto para não perder indicados num cenário de classes desbalanceadas.
- Predições 2025 são geradas dentro do notebook `05_master_pipeline.ipynb` (exporte para CSV se necessário).

## Como reproduzir
1. **Instalar dependências**
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```
2. **(Opcional) Recoletar notas do Metacritic**  
   ```bash
   python data_base_construction/db_populate_scipts/db_unifier.py
   # reprocessar erros:
   python data_base_construction/db_populate_scipts/db_unifier.py --retry-errors
   ```
3. **Subir o PostgreSQL com o schema**  
   ```bash
   docker run -d --name movies-postgres \\
     -e POSTGRES_DB=moviesdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \\
     -v \"$(pwd)/data_base_construction/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro\" \\
     -p 5432:5432 postgres:16
   ```
4. **Popular o banco**  
   ```bash
   python data_base_construction/db_populate_scipts/populate_db.py
   ```
5. **Testar conexão/carregamento**  
   ```bash
   python data_base_construction/db_populate_scipts/data_loader.py
   ```
6. **Rodar notebooks de ML**  
   - Garanta o `.env` (ver `machine-learning/.env.example`).  
   - Abra `machine-learning/notebooks/` e siga a ordem 01 → 05.  
   - `05_master_pipeline.ipynb` treina o modelo final e gera as previsões de 2025.

## Arquivos e diagramas úteis
- `docs/er_diagram.png`: modelo ER do banco.
- `machine-learning/documentation/EDA_INSIGHTS.md`: resumo da EDA e próximos passos.  
- `machine-learning/documentation/FEATURE_ANALYSIS.md`: descrição das features do modelo final.  
- `machine-learning/reports/figures/`: gráficos de EDA (correlação, balanceamento, distribuições).

## Fontes de dados
- IMDb Non-Commercial Datasets: https://datasets.imdbws.com  
- IMDbAPI (sem autenticação): https://api.imdbapi.dev  
- Metacritic (scraping via Playwright para notas de críticos).
