# Plano de Implementação: Modelo de Predição de Indicações ao Oscar

## Objetivo

Desenvolver um modelo de Machine Learning para prever quais filmes serão indicados ao Oscar de Melhor Filme em 2025, utilizando dados históricos de 2000-2024.

## Contexto

O projeto já possui:

- ✅ Banco de dados PostgreSQL estruturado com filmes de 1980-2025
- ✅ Schema normalizado com tabelas de filmes, pessoas, gêneros, países, box office, etc.
- ✅ Dados do IMDb combinados com scores do Metacritic
- ✅ View SQL `ml_training_dataset` preparada para exportação

## Fases do Projeto

### Fase 1: Análise Exploratória de Dados (EDA)

**Objetivo**: Entender profundamente os dados antes de treinar qualquer modelo.

#### 1.1 Setup do Ambiente

- Criar diretório `notebooks/` para análise
- Configurar Jupyter Notebook
- Instalar bibliotecas necessárias (pandas, numpy, matplotlib, seaborn, scikit-learn, etc.)
- Criar conexão com banco PostgreSQL

#### 1.2 Extração de Dados

- Exportar view `ml_training_dataset` para CSV
- Carregar dados em Pandas DataFrame
- Criar backup dos dados brutos

#### 1.3 Análise Inicial

- **Dimensões do dataset**: Total de filmes, features, período coberto
- **Balanceamento de classes**: Ratio indicados vs não-indicados
- **Dados faltantes**: Identificar colunas com NULLs e percentuais
- **Tipos de dados**: Verificar se todas as features estão nos tipos corretos

#### 1.4 Análise Univariada

Para cada feature numérica:

- Estatísticas descritivas (média, mediana, std, min, max)
- Distribuições (histogramas)
- Identificação de outliers (boxplots)

#### 1.5 Análise Bivariada

- Correlação entre features numéricas
- Comparação de distribuições: indicados vs não-indicados
- Identificar features mais discriminativas

#### 1.6 Análise Temporal

- Distribuição de filmes por ano
- Evolução de indicações ao longo do tempo
- Sazonalidade (meses de lançamento)

#### 1.7 Análise de Features Categóricas

- Consultar banco para dados de gêneros, diretores, países
- Identificar gêneros/pessoas mais frequentes entre indicados
- Preparar para one-hot encoding

---

### Fase 2: Feature Engineering

**Objetivo**: Criar novas features que melhorem o poder preditivo do modelo.

#### 2.1 Features Temporais

- Mês de lançamento (filmes de final de ano têm mais chances?)
- Distância até a cerimônia do Oscar
- Diferença entre `release_year` e `oscar_ceremony_year`

#### 2.2 Features Derivadas Numéricas

- ROI (Return on Investment) - já existe na view
- Ratio `domestic_gross / worldwide_gross` (desempenho nos EUA)
- Índice de eficiência: `worldwide_gross / runtime_minutes`
- Normalização de ratings (z-score por ano)
- Ranking de bilheteria dentro do ano

#### 2.3 Features de Histórico (Prestígio)

- Número de indicações/vitórias anteriores do diretor
- Número de indicações/vitórias anteriores dos atores principais
- Estúdio/produtora com histórico de Oscar

#### 2.4 Features Categóricas Expandidas

- One-hot encoding para top N gêneros
- One-hot encoding para top N diretores
- One-hot encoding para países de produção
- Features booleanas: "Drama?", "Thriller?", "Biography?" etc.

#### 2.5 Features de Texto (Opcional/Avançado)

- TF-IDF da sinopse
- Análise de sentimento da sinopse
- Presença de palavras-chave ("based on true story", "war", etc.)

#### 2.6 Criação de Dataset Final

- Consolidar todas as features em um único DataFrame
- Documentar significado de cada coluna
- Salvar versão processada

---

### Fase 3: Preparação de Dados para ML

**Objetivo**: Preparar dados no formato adequado para treinamento.

#### 3.1 Tratamento de Valores Ausentes

- **Estratégia 1**: Imputação com mediana/média (features numéricas)
- **Estratégia 2**: Imputação com moda (features categóricas)
- **Estratégia 3**: Criar flag "missing" como feature adicional
- Documentar decisões de imputação

#### 3.2 Tratamento de Outliers

- Identificar outliers extremos
- Decidir: remover, winsorizar ou manter?
- Aplicar transformações (log, sqrt) se necessário

#### 3.3 Codificação de Variáveis Categóricas

- One-hot encoding para gêneros, países, etc.
- Label encoding onde apropriado
- Garantir que categorias de treino/teste sejam consistentes

#### 3.4 Normalização/Padronização

- StandardScaler para features com distribuição normal
- MinMaxScaler para features com limites claros
- RobustScaler para features com outliers
- Aplicar apenas após split treino/teste (evitar data leakage)

#### 3.5 Split Temporal do Dataset

**CRÍTICO**: Respeitar temporalidade!

```
Treino:    2000-2019 (20 anos)
Validação: 2020-2022 (3 anos)
Teste:     2023-2024 (2 anos)
Predição:  2025 (futuro real)
```

Não usar `train_test_split` aleatório!

#### 3.6 Balanceamento de Classes

Testar estratégias:

- **Baseline**: Dados desbalanceados + class_weight
- **Undersampling**: RandomUnderSampler
- **Oversampling**: SMOTE (Synthetic Minority Over-sampling)
- **Hybrid**: Combinação de ambos

---

### Fase 4: Modelagem e Treinamento

**Objetivo**: Treinar e comparar diferentes modelos de ML.

#### 4.1 Baseline: Modelo Dummy

- `DummyClassifier` (estratified)
- Estabelecer performance mínima aceitável

#### 4.2 Modelos Lineares

- Logistic Regression
- Regularização (L1, L2, ElasticNet)
- Interpretação de coeficientes

#### 4.3 Modelos Baseados em Árvores

- Decision Tree (baseline)
- Random Forest (ensemble)
- Extra Trees

#### 4.4 Gradient Boosting

- XGBoost
- LightGBM
- CatBoost (bom para categóricas)

#### 4.5 Outros Algoritmos

- Support Vector Machines (SVM)
- K-Nearest Neighbors (KNN)
- Naive Bayes

#### 4.6 Tuning de Hiperparâmetros

- Grid Search ou Random Search
- Cross-validation temporal (TimeSeriesSplit adaptado)
- Otimizar para F1-Score ou AUC-ROC

#### 4.7 Ensemble de Modelos

- Voting Classifier
- Stacking
- Blending

---

### Fase 5: Avaliação e Interpretação

**Objetivo**: Avaliar modelos e entender as predições.

#### 5.1 Métricas de Performance

Para dados desbalanceados, avaliar:

- **Precision**: Dos que prevemos como indicados, quantos realmente foram?
- **Recall**: Dos que foram indicados, quantos conseguimos prever?
- **F1-Score**: Média harmônica de precision e recall
- **AUC-ROC**: Capacidade de discriminação
- **Confusion Matrix**: Análise de erros (FP, FN)
- **PR Curve**: Precision-Recall curve

#### 5.2 Validação no Conjunto de Teste

- Aplicar melhor modelo em dados 2023-2024
- Comparar com indicações reais conhecidas
- Análise de erros: quais filmes erramos e por quê?

#### 5.3 Feature Importance

- Identificar features mais importantes
- SHAP values (explicabilidade)
- Permutation importance
- Visualizar contribuições

#### 5.4 Análise de Casos

- **True Positives**: Filmes corretamente preditos como indicados
- **False Positives**: Filmes que previmos mas não foram indicados (por quê?)
- **False Negatives**: Filmes indicados que não previmos (o que faltou?)
- **True Negatives**: Validar se são realmente improváveis

#### 5.5 Calibração de Probabilidades

- Reliability diagram
- Calibração de Platt ou isotônica
- Interpretar scores de probabilidade

---

### Fase 6: Predição para 2025

**Objetivo**: Gerar predições reais para filmes de 2025.

#### 6.1 Preparação de Dados 2025

- Filtrar filmes com `release_year = 2025`
- Verificar completude de features
- Aplicar mesmas transformações/normalizações

#### 6.2 Geração de Predições

- Aplicar modelo treinado
- Gerar probabilidades de indicação
- Rankear filmes por probabilidade

#### 6.3 Análise de Resultados

- Top 10 filmes com maior probabilidade
- Top 20 para margem de segurança
- Identificar features que mais influenciaram

#### 6.4 Validação de Sanity

- Predições fazem sentido?
- Filmes conhecidos estão bem posicionados?
- Há surpresas interessantes?

#### 6.5 Documentação de Predições

- Criar relatório com:
  - Top N filmes preditos
  - Probabilidades
  - Features mais importantes de cada filme
  - Justificativas do modelo

---

### Fase 7: Documentação e Próximos Passos

**Objetivo**: Consolidar aprendizados e preparar para futuro.

#### 7.1 Documentação Técnica

- Notebook final limpo e comentado
- README do projeto
- Instruções para reproduzir
- Requisitos e dependências

#### 7.2 Visualizações e Dashboard

- Criar visualizações das predições
- Dashboard interativo (Streamlit/Gradio?)
- Exportar para formatos compartilháveis

#### 7.3 Aprendizados e Limitações

- O que funcionou bem?
- O que não funcionou?
- Limitações do modelo
- Vieses identificados

#### 7.4 Melhorias Futuras

- Coletar mais dados (streaming numbers, redes sociais)
- Incorporar dados de festivais (Cannes, Venice, TIFF)
- Adicionar categorias específicas (Ator, Diretor, etc.)
- Modelo temporal sequencial (LSTM, Transformer)
- Atualizar modelo anualmente

---

## Cronograma Estimado

| Fase                   | Tempo Estimado | Status      |
| ---------------------- | -------------- | ----------- |
| 1. EDA                 | 2-3 sessões    | 🔄 Próxima  |
| 2. Feature Engineering | 2-3 sessões    | ⏳ Pendente |
| 3. Preparação de Dados | 1-2 sessões    | ⏳ Pendente |
| 4. Modelagem           | 3-4 sessões    | ⏳ Pendente |
| 5. Avaliação           | 1-2 sessões    | ⏳ Pendente |
| 6. Predição 2025       | 1 sessão       | ⏳ Pendente |
| 7. Documentação        | 1 sessão       | ⏳ Pendente |

**Total**: ~11-18 sessões de trabalho

---

## Tecnologias e Bibliotecas

### Ambiente

- Python 3.8+
- Jupyter Notebook / JupyterLab
- PostgreSQL (já configurado)

### Bibliotecas Principais

```python
# Manipulação de dados
pandas, numpy

# Visualização
matplotlib, seaborn, plotly

# Conexão com banco
psycopg2-binary, sqlalchemy

# Machine Learning
scikit-learn, xgboost, lightgbm, catboost

# Interpretabilidade
shap

# Balanceamento
imbalanced-learn

# Utilitários
joblib (salvar modelos), python-dotenv (env vars)
```

---

## Estrutura de Diretórios Proposta

```
oscar_movie_database/
├── data/
│   ├── raw/                    # Dados brutos exportados
│   ├── processed/              # Dados processados
│   └── predictions/            # Predições finais
├── notebooks/
│   ├── 01_eda.ipynb           # Análise exploratória
│   ├── 02_feature_engineering.ipynb
│   ├── 03_data_preparation.ipynb
│   ├── 04_modeling.ipynb
│   ├── 05_evaluation.ipynb
│   └── 06_predictions_2025.ipynb
├── src/
│   ├── data_loader.py         # Funções de carregamento
│   ├── feature_engineering.py # Criação de features
│   ├── preprocessing.py       # Pipelines de pré-processamento
│   └── utils.py               # Utilitários
├── models/
│   └── trained_models/        # Modelos salvos (.joblib)
├── reports/
│   ├── figures/               # Gráficos e visualizações
│   └── predictions_2025.csv   # Predições finais
├── requirements.txt
├── README.md
└── (arquivos existentes: scripts SQL, populate, etc.)
```

---

## Próximos Passos Imediatos

Vamos começar com a **Fase 1: EDA**. Os primeiros passos concretos são:

1. ✅ Criar estrutura de diretórios
2. ✅ Configurar ambiente Python (requirements.txt)
3. ✅ Exportar dados do PostgreSQL
4. ✅ Criar primeiro notebook de EDA
5. ✅ Análise inicial dos dados

---

> [!IMPORTANT]
> Este plano é iterativo! Vamos ajustar conforme descobrimos características dos dados e resultados dos modelos.
