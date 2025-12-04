# Documentação da Estrutura de Diretórios

Este documento descreve a organização do projeto IMDb Data Science.

## Visão Geral

O projeto está organizado em diretórios lógicos separando código, dados, documentação e saídas. Esta estrutura torna a base de código mais fácil de manter, testar e entender.

## Layout do Diretório

```
imdb-data-science/
├── README.md                    # Documentação principal do projeto
├── requirements.txt             # Dependências Python
├── .gitignore                   # Padrões de ignore do Git
├── docs/                        # Arquivos de documentação
├── notebooks/                   # Notebooks Jupyter para análise
├── src/                         # Código fonte organizado por função
├── scripts/                     # Scripts executáveis
├── data/                        # Arquivos de dados (brutos, processados, erros, arquivos)
├── outputs/                     # Saídas geradas (figuras, relatórios)
├── tests/                       # Testes unitários e de integração
└── logs/                        # Logs de execução
```

## Detalhes do Diretório

### Nível Raiz

**README.md**

- Documentação principal do projeto
- Visão geral, instruções de configuração e exemplos de uso

**requirements.txt**

- Dependências de pacotes Python
- Instalar com: `pip install -r requirements.txt`

**.gitignore**

- Especifica arquivos a serem excluídos do controle de versão
- Configurado para ignorar grandes arquivos de dados, logs e cache Python

---

### docs/

Arquivos de documentação do projeto.

**Conteúdo:**

- `DB_UNIFIER_GUIDE.md` - Guia para usar o script unificador de banco de dados
- `directory_structure.md` - Este arquivo

**Objetivo:** Manter toda a documentação em um só lugar para fácil referência.

---

### notebooks/

Notebooks Jupyter para análise exploratória e visualização.

**Conteúdo:**

- `01_exploratory_analysis.ipynb` - Exploração inicial de dados

**Convenção de Nomenclatura:** Notebooks são numerados por ordem de execução (01*, 02*, etc.)

**Objetivo:** Análise interativa, experimentação e prototipagem.

---

### src/

Código fonte organizado em subpacotes por função.

**Estrutura:**

```
src/
├── __init__.py              # Torna src um pacote Python
├── scrapers/                # Módulos de web scraping
│   ├── __init__.py
│   └── metacritic_scraper.py
├── processors/              # Módulos de processamento de dados
│   ├── __init__.py
│   └── scores_processor.py
├── database/                # Scripts relacionados a banco de dados
│   ├── __init__.py
│   └── db_unifier.py
└── utils/                   # Funções utilitárias
    └── __init__.py
```

**scrapers/**

- Funcionalidade de web scraping
- `metacritic_scraper.py` - Coleta pontuações de filmes do Metacritic

**processors/**

- Transformação e processamento de dados
- `scores_processor.py` - Processa e analisa dados de pontuação

**database/**

- Operações de banco de dados e coleta de dados
- `db_unifier.py` - Script principal para coletar e unificar pontuações de filmes

**utils/**

- Funções utilitárias compartilhadas
- Atualmente vazio, pronto para adições futuras

**Objetivo:** Módulos de código organizados e reutilizáveis que podem ser importados em todo o projeto.

---

### scripts/

Scripts executáveis que usam os módulos src.

**Conteúdo:**

- `main.py` - Script de execução principal para coleta de pontuações

**Uso:**

```bash
python scripts/main.py
```

**Objetivo:** Pontos de entrada para executar fluxos de trabalho do projeto. Scripts importam de pacotes `src/`.

---

### data/

Todos os arquivos de dados organizados por estágio e tipo.

**Estrutura:**

```
data/
├── raw/                     # Dados originais, não modificados
├── processed/               # Dados processados e limpos
├── errors/                  # Arquivos de rastreamento de erros
└── archives/                # Arquivos compactados
```

**raw/**

- Arquivos de dados originais, nunca modificados
- `movies_catalog_oscar_and_popular_2000_2025.csv` - Catálogo de filmes fonte

**processed/**

- Dados que foram transformados ou enriquecidos
- `movie_scores.json` - Pontuações de filmes coletadas
- `movies_scores_minify.json` - Versão minificada das pontuações
- `movie_scores_from_error_list.json` - Pontuações recuperadas de novas tentativas

**errors/**

- Arquivos rastreando erros de processamento
- `error_list.json` - Lista de filmes que falharam no processamento
- `error_list_from_error_list.json` - Erros de tentativas de reprocessamento

**archives/**

- Arquivos compactados e backups
- `imdb-rails.zip` - Arquivo do projeto Rails
- `extractor_imdb.zip` - Arquivo do extrator IMDb

**Objetivo:** Separação clara de dados por estágio de processamento, facilitando o rastreamento do fluxo de dados.

---

### outputs/

Saídas de análise geradas.

**Estrutura:**

```
outputs/
├── figures/                 # Gráficos e visualizações gerados
└── reports/                 # Relatórios e resumos gerados
```

**Objetivo:** Armazenar resultados de análise separadamente dos dados fonte. Atualmente vazio.

---

### tests/

Testes unitários e de integração para o projeto.

**Estrutura:**

```
tests/
└── __init__.py
```

**Objetivo:** Cobertura de testes para módulos de código fonte. Atualmente vazio, pronto para implementação de testes.

---

### logs/

Logs de execução de scripts.

**Conteúdo:**

- Arquivos de log gerados por `db_unifier.py` com nomeação por timestamp
- Formato: `db_unifier_YYYYMMDD_HHMMSS.log`

**Objetivo:** Rastrear execução de scripts, erros e informações de depuração.

---

## Convenções de Importação

Como `src/` é organizado como um pacote Python, as importações devem usar o caminho completo do pacote:

```python
# Importar de scrapers
from src.scrapers.metacritic_scraper import get_metacritic_critic_scores_from_id

# Importar de processors
from src.processors.scores_processor import features_from_scores_map

# Importar de database
from src.database.db_unifier import get_all_movies_scores
```

## Executando Scripts

Os scripts devem ser executados a partir do diretório raiz do projeto:

```bash
# Da raiz do projeto
python scripts/main.py

# Executar unificador de banco de dados
python -m src.database.db_unifier

# Executar com modo de nova tentativa (retry)
python -m src.database.db_unifier --retry-errors
```

## Estratégia de Git Ignore

O arquivo `.gitignore` está configurado para:

- Excluir todos os arquivos de dados em `data/raw/`, `data/processed/` e `data/errors/`
- Excluir arquivos de log em `logs/`
- Excluir cache Python (`__pycache__/`, `*.pyc`)
- Excluir ambientes virtuais (`.venv/`, `venv/`)
- Excluir checkpoints de notebooks Jupyter

Isso mantém o repositório limpo enquanto preserva a estrutura de diretórios.

## Adicionando Novos Componentes

**Novo scraper:**

1. Adicionar em `src/scrapers/`
2. Importar em `src/scrapers/__init__.py` se necessário
3. Criar testes correspondentes em `tests/test_scrapers.py`

**Novo processor:**

1. Adicionar em `src/processors/`
2. Importar em `src/processors/__init__.py` se necessário
3. Criar testes correspondentes em `tests/test_processors.py`

**Novo notebook:**

1. Adicionar em `notebooks/` com prefixo numerado
2. Usar nome descritivo indicando o objetivo

**Nova fonte de dados:**

1. Colocar em `data/raw/`
2. Documentar no README.md ou em `docs/`

## Benefícios Desta Estrutura

1. **Separação clara de responsabilidades** - Código, dados, docs e saídas são isolados
2. **Escalável** - Fácil de adicionar novos módulos sem bagunça
3. **Profissional** - Segue as melhores práticas Python para estrutura de pacotes
4. **Manutenível** - Fácil de encontrar e atualizar componentes específicos
5. **Testável** - Estrutura clara suporta testes abrangentes
6. **Amigável ao controle de versão** - Dados sensíveis e saídas excluídos do git
