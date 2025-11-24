# Task Checklist: Projeto de ML para Predição de Oscar

## Fase 1: Análise Exploratória de Dados (EDA)

### 1.1 Setup do Ambiente

- [x] Criar diretório `notebooks/` no projeto
- [x] Criar diretório `data/raw/`, `data/processed/`, `data/predictions/`
- [x] Criar diretório `src/` para código reutilizável
- [x] Criar diretório `models/trained_models/`
- [x] Criar diretório `reports/figures/`
- [x] Criar `requirements.txt` com bibliotecas necessárias
- [x] Instalar dependências Python
- [x] Criar arquivo `.env` com credenciais do PostgreSQL
- [x] Testar conexão com banco de dados

### 1.2 Extração de Dados

- [x] Criar script Python para conexão com PostgreSQL
- [x] Exportar view `ml_training_dataset` para CSV
- [x] Exportar dados de gêneros (tabela `genres` + `movie_genres`)
- [x] Exportar dados de pessoas (diretores, roteiristas, elenco)
- [x] Exportar dados de países e idiomas
- [x] Salvar CSVs em `data/raw/`
- [x] Verificar integridade dos dados exportados

### 1.3 Criar Notebook de EDA

- [x] Criar `notebooks/01_eda.ipynb`
- [x] Carregar dados em Pandas DataFrame
- [x] Exibir dimensões do dataset (shape)
- [ ] Exibir primeiras linhas (head)
- [ ] Exibir info geral (dtypes, memory usage)
- [ ] Exibir estatísticas descritivas (describe)

### 1.4 Análise de Balanceamento

- [ ] Contar filmes indicados vs não-indicados
- [ ] Calcular percentual de cada classe
- [ ] Criar visualização de balanceamento (bar chart)
- [ ] Analisar distribuição por ano

### 1.5 Análise de Dados Faltantes

- [ ] Identificar colunas com valores NULL
- [ ] Calcular percentual de missing por coluna
- [ ] Criar heatmap de missing values
- [ ] Documentar padrões de dados faltantes

### 1.6 Análise Univariada - Features Numéricas

- [ ] `imdb_rating`: distribuição, média, mediana
- [ ] `imdb_votes`: distribuição, outliers
- [ ] `runtime_minutes`: distribuição
- [ ] `metascore`: distribuição, missing rate
- [ ] `budget`: distribuição, outliers, missing rate
- [ ] `worldwide_gross`: distribuição, outliers
- [ ] `domestic_gross`: distribuição
- [ ] `roi_worldwide`: distribuição, outliers
- [ ] Features de rating samples (mean_score, median_score, etc.)
- [ ] Criar histogramas para todas as features numéricas
- [ ] Criar boxplots para identificar outliers

### 1.7 Análise Bivariada

- [ ] Calcular matriz de correlação entre features numéricas
- [ ] Criar heatmap de correlação
- [ ] Comparar distribuições: indicados vs não-indicados (violinplot)
- [ ] Testar significância estatística (t-test) para features principais
- [ ] Identificar features mais discriminativas

### 1.8 Análise Temporal

- [ ] Distribuição de filmes por ano (line chart)
- [ ] Percentual de indicados por ano
- [ ] Evolução de ratings ao longo do tempo
- [ ] Evolução de budget/box office ao longo do tempo
- [ ] Identificar tendências temporais

### 1.9 Análise de Features Categóricas

- [ ] Carregar dados de gêneros
- [ ] Top 10 gêneros mais frequentes
- [ ] Gêneros mais comuns entre indicados
- [ ] Carregar dados de diretores
- [ ] Top 20 diretores com mais indicações
- [ ] Carregar dados de países
- [ ] Países com mais filmes indicados
- [ ] Idiomas mais comuns

### 1.10 Documentação de Descobertas

- [ ] Resumir principais insights
- [ ] Identificar problemas de qualidade de dados
- [ ] Listar features promissoras
- [ ] Listar features problemáticas
- [ ] Decidir próximos passos

---

## Fase 2: Feature Engineering

### 2.1 Features Temporais

- [ ] Criar feature: `release_month`
- [ ] Criar feature: `is_late_year_release` (Out-Dez)
- [ ] Criar feature: `days_to_oscar_ceremony`
- [ ] Criar feature: `ceremony_delay` (difference between release and ceremony)

### 2.2 Features Derivadas Numéricas

- [ ] Verificar/corrigir cálculo de `roi_worldwide`
- [ ] Criar: `us_market_share` (domestic/worldwide)
- [ ] Criar: `revenue_per_minute` (gross/runtime)
- [ ] Criar: `votes_normalized_by_year` (z-score)
- [ ] Criar: `rating_normalized_by_year` (z-score)
- [ ] Criar: `box_office_rank_in_year`
- [ ] Criar: `budget_category` (low, medium, high)

### 2.3 Features de Histórico (Prestígio)

- [ ] SQL: Criar query para indicações anteriores por diretor
- [ ] SQL: Criar query para vitórias anteriores por diretor
- [ ] SQL: Criar query para indicações anteriores por atores principais
- [ ] Integrar features de prestígio ao dataset
- [ ] Criar: `director_previous_nominations`
- [ ] Criar: `director_previous_wins`
- [ ] Criar: `cast_previous_nominations`

### 2.4 Features Categóricas - One-Hot Encoding

- [ ] Identificar top 15 gêneros mais frequentes
- [ ] One-hot encoding para top gêneros
- [ ] Identificar top 20 diretores mais frequentes
- [ ] One-hot encoding para top diretores
- [ ] One-hot encoding para top 5 países
- [ ] Criar features booleanas: `is_drama`, `is_biography`, `is_thriller`, etc.

### 2.5 Features de Contagem (já existem)

- [ ] Verificar: `num_genres`, `num_countries`, `num_languages`
- [ ] Verificar: `num_directors`, `num_writers`, `num_cast`

### 2.6 Features Opcionais Avançadas

- [ ] (Opcional) TF-IDF da sinopse
- [ ] (Opcional) Análise de sentimento da sinopse
- [ ] (Opcional) Presença de keywords ("true story", "war", etc.)

### 2.7 Consolidação

- [ ] Criar `notebooks/02_feature_engineering.ipynb`
- [ ] Implementar todas as features em código limpo
- [ ] Criar função reutilizável em `src/feature_engineering.py`
- [ ] Salvar dataset com features em `data/processed/dataset_with_features.csv`
- [ ] Documentar todas as features criadas

---

## Fase 3: Preparação de Dados para ML

### 3.1 Tratamento de Valores Ausentes

- [ ] Decidir estratégia para cada feature com NULLs
- [ ] Implementar imputação para `metascore`
- [ ] Implementar imputação para `budget`
- [ ] Implementar imputação para `box_office`
- [ ] Criar flags de missing quando apropriado
- [ ] Documentar decisões

### 3.2 Tratamento de Outliers

- [ ] Identificar outliers em `budget`
- [ ] Identificar outliers em `worldwide_gross`
- [ ] Identificar outliers em `roi_worldwide`
- [ ] Decidir: winsorização vs remoção vs manter
- [ ] Aplicar transformações log onde apropriado
- [ ] Documentar tratamento

### 3.3 Seleção Final de Features

- [ ] Listar todas as features disponíveis
- [ ] Remover features com alta correlação (redundantes)
- [ ] Remover features com muitos missing values
- [ ] Criar lista final de features para modelo

### 3.4 Split Temporal do Dataset

- [ ] Filtrar dados de treino: 2000-2019
- [ ] Filtrar dados de validação: 2020-2022
- [ ] Filtrar dados de teste: 2023-2024
- [ ] Separar dados de predição: 2025
- [ ] Verificar balanceamento em cada split
- [ ] Salvar splits separadamente

### 3.5 Normalização/Padronização

- [ ] Identificar features que precisam de scaling
- [ ] Fit StandardScaler apenas no conjunto de treino
- [ ] Transform treino, validação, teste
- [ ] Salvar scaler para uso futuro
- [ ] Documentar transformações aplicadas

### 3.6 Balanceamento de Classes

- [ ] Baseline: treinar com class_weight='balanced'
- [ ] Implementar RandomUnderSampler
- [ ] Implementar SMOTE
- [ ] Implementar estratégia híbrida
- [ ] Comparar estratégias (qual funciona melhor?)
- [ ] Documentar decisão final

### 3.7 Consolidação

- [ ] Criar `notebooks/03_data_preparation.ipynb`
- [ ] Criar pipeline de pré-processamento em `src/preprocessing.py`
- [ ] Salvar dados finais prontos para ML
- [ ] Salvar artifacts (scaler, encoder, etc.)

---

## Fase 4: Modelagem e Treinamento

### 4.1 Setup de Avaliação

- [ ] Definir métricas de avaliação (F1, Precision, Recall, AUC-ROC)
- [ ] Criar função de avaliação reutilizável
- [ ] Configurar validação cruzada temporal

### 4.2 Baseline: Dummy Classifier

- [ ] Treinar DummyClassifier (stratified)
- [ ] Avaliar performance baseline
- [ ] Documentar métricas baseline

### 4.3 Logistic Regression

- [ ] Treinar Logistic Regression básica
- [ ] Testar regularização L1, L2, ElasticNet
- [ ] Tuning de hiperparâmetro C
- [ ] Avaliar e documentar resultados
- [ ] Analisar coeficientes (feature importance)

### 4.4 Random Forest

- [ ] Treinar Random Forest básico
- [ ] Tuning: n_estimators, max_depth, min_samples_split
- [ ] Avaliar feature importance
- [ ] Documentar resultados

### 4.5 XGBoost

- [ ] Treinar XGBoost básico
- [ ] Tuning: learning_rate, max_depth, n_estimators, subsample
- [ ] Aplicar early stopping
- [ ] Avaliar feature importance
- [ ] Documentar resultados

### 4.6 LightGBM

- [ ] Treinar LightGBM básico
- [ ] Tuning de hiperparâmetros
- [ ] Avaliar feature importance
- [ ] Documentar resultados

### 4.7 Outros Modelos (Opcional)

- [ ] SVM (se viável)
- [ ] CatBoost
- [ ] Neural Network (MLP)

### 4.8 Comparação de Modelos

- [ ] Criar tabela comparativa de métricas
- [ ] Visualizar ROC curves
- [ ] Visualizar Precision-Recall curves
- [ ] Selecionar melhor(es) modelo(s)

### 4.9 Ensemble (Opcional)

- [ ] Voting Classifier
- [ ] Stacking
- [ ] Avaliar se ensemble melhora performance

### 4.10 Consolidação

- [ ] Criar `notebooks/04_modeling.ipynb`
- [ ] Salvar melhores modelos em `models/trained_models/`
- [ ] Documentar hiperparâmetros finais

---

## Fase 5: Avaliação e Interpretação

### 5.1 Avaliação no Conjunto de Validação

- [ ] Aplicar melhor modelo em dados de validação (2020-2022)
- [ ] Calcular todas as métricas
- [ ] Gerar Confusion Matrix
- [ ] Analisar precision, recall, F1
- [ ] Calcular AUC-ROC

### 5.2 Avaliação no Conjunto de Teste

- [ ] Aplicar modelo em dados de teste (2023-2024)
- [ ] Comparar resultados com validação
- [ ] Verificar se há overfitting
- [ ] Documentar performance final

### 5.3 Análise de Erros

- [ ] Listar False Positives (previmos como indicado, mas não foi)
- [ ] Listar False Negatives (foi indicado, mas não previmos)
- [ ] Analisar características dos erros
- [ ] Identificar padrões: por que o modelo errou?

### 5.4 Feature Importance

- [ ] Extrair feature importance do modelo final
- [ ] Criar visualização (bar chart)
- [ ] Calcular SHAP values (explicabilidade)
- [ ] Analisar contribuição de cada feature
- [ ] Documentar insights

### 5.5 Calibração de Probabilidades

- [ ] Verificar calibração das probabilidades
- [ ] Criar reliability diagram
- [ ] Aplicar calibração (Platt ou isotônica) se necessário
- [ ] Verificar se calibração melhora interpretação

### 5.6 Consolidação

- [ ] Criar `notebooks/05_evaluation.ipynb`
- [ ] Documentar todos os resultados
- [ ] Criar visualizações para relatório

---

## Fase 6: Predição para 2025

### 6.1 Preparação de Dados 2025

- [ ] Filtrar filmes com `release_year = 2025` do banco
- [ ] Verificar quais já têm dados completos
- [ ] Aplicar mesmas transformações de feature engineering
- [ ] Aplicar mesmos scalers/encoders
- [ ] Verificar se algum dado crítico está faltando

### 6.2 Geração de Predições

- [ ] Carregar modelo treinado final
- [ ] Aplicar modelo aos dados de 2025
- [ ] Gerar probabilidades de indicação
- [ ] Rankear filmes por probabilidade

### 6.3 Análise de Resultados

- [ ] Listar top 10 filmes com maior probabilidade
- [ ] Listar top 20 para margem de segurança
- [ ] Analisar features mais importantes de cada filme
- [ ] Identificar "surpresas" (filmes inesperados bem ranqueados)

### 6.4 Validação de Sanity

- [ ] Verificar se filmes conhecidos estão bem posicionados
- [ ] Verificar se resultados fazem sentido intuitivamente
- [ ] Comparar com buzz da indústria (se disponível)
- [ ] Identificar possíveis problemas

### 6.5 Documentação de Predições

- [ ] Criar relatório de predições
- [ ] Incluir: título, probabilidade, features principais
- [ ] Salvar em `data/predictions/oscar_2025_predictions.csv`
- [ ] Criar visualizações (gráficos, tabelas)
- [ ] Preparar apresentação dos resultados

### 6.6 Consolidação

- [ ] Criar `notebooks/06_predictions_2025.ipynb`
- [ ] Exportar resultados em formatos compartilháveis
- [ ] Criar relatório final

---

## Fase 7: Documentação e Próximos Passos

### 7.1 Documentação Técnica

- [ ] Limpar e comentar todos os notebooks
- [ ] Criar README.md do projeto
- [ ] Documentar como reproduzir o projeto
- [ ] Criar `requirements.txt` final
- [ ] Documentar estrutura de diretórios

### 7.2 Visualizações Finais

- [ ] Consolidar principais gráficos em `reports/figures/`
- [ ] Criar dashboard (Streamlit, Gradio ou HTML?)
- [ ] Preparar apresentação visual dos resultados

### 7.3 Relatório de Aprendizados

- [ ] Documentar o que funcionou bem
- [ ] Documentar o que não funcionou
- [ ] Listar limitações do modelo
- [ ] Identificar vieses
- [ ] Listar possíveis melhorias

### 7.4 Planejamento Futuro

- [ ] Definir como atualizar modelo após Oscar 2025
- [ ] Planejar coleta de dados adicionais
- [ ] Considerar outras categorias do Oscar
- [ ] Avaliar possibilidade de deploy (app web?)

---

## ✅ Status Geral do Projeto

**Fase atual**: 1.1 - Setup do Ambiente
**Próximo passo**: Criar estrutura de diretórios e requirements.txt
