# Documentação: Features do Modelo Final (Oscar Prediction)

Este documento detalha as features selecionadas para o pipeline final (`05_master_pipeline.ipynb`), explicando sua lógica, importância e interpretação.

## 1. Features de Popularidade e Bilheteria (Normalizadas)

### ✅ **Feature: `box_office_rank_in_year`**

**O que significa:**
- **Posição do filme no ano** ordenado por bilheteria mundial.
- Rank 1 = maior bilheteria do ano.

**Por que é importante:**
- Elimina o viés da inflação (comparar bilheteria de 2000 com 2024 é injusto, mas comparar o "Top 10" de cada ano é justo).
- Filmes de Oscar geralmente não são os #1 de bilheteria (blockbusters puros), mas também não são obscuros (rank > 200). Existe um "sweet spot".

**Interpretação:**
| Rank       | Significado     | Probabilidade Oscar                   |
| ---------- | --------------- | ------------------------------------- |
| **1-5**    | Top 5 do ano    | Baixa (geralmente blockbusters de ação) |
| **6-50**   | Top 50          | **Alta** (filmes de prestígio com público) |
| **> 100**  | Fora do top 100 | Baixa (pouca visibilidade)            |

### ✅ **Feature: `votes_normalized_by_year`**

**O que significa:**
- **Z-score de votos do IMDb** comparado à média do ano.
- Mede a popularidade relativa do filme dentro do seu ano de lançamento.

**Por que é importante:**
- O número de usuários do IMDb cresceu exponencialmente. Um filme com 50k votos em 2000 era um fenômeno; em 2024 é comum.
- A normalização (Z-score) coloca todos os anos na mesma escala.

**Interpretação:**
- **Z > 2.0**: Filme muito popular (Blockbuster ou Viral).
- **Z entre 0 e 2.0**: Filme conhecido, público saudável.
- **Z < -1.0**: Filme obscuro/nicho.

### ✅ **Feature: `rating_normalized_by_year`**

**O que significa:**
- **Z-score da nota (rating) do IMDb** comparado à média do ano.

**Por que é importante:**
- Existe uma "inflação de notas" ou mudanças de comportamento dos usuários ao longo das décadas.
- Identifica filmes que se destacaram qualitativamente *em relação aos seus contemporâneos*.

---

## 2. Features de Complexidade e Escopo

### ✅ **Features: `num_genres`, `num_countries`, `num_languages`, `num_cast`**

**O que significa:**
- Contagem simples da quantidade de gêneros associados, países de produção, idiomas falados e tamanho do elenco principal creditado.

**Por que é importante:**
- **Complexidade**: Filmes de Oscar ("Best Picture") tendem a ser produções complexas, épicas ou dramas densos.
- **`num_cast`**: Elencos grandes (*ensemble cast*) são comuns em filmes premiados (ex: *Spotlight*, *Oppenheimer*, *Crash*).
- **`num_countries` / `num_languages`**: Indica co-produções internacionais ou filmes que buscam autenticidade cultural, características valorizadas pela Academia moderna.

**Interpretação:**
- **num_cast alto**: Produção de grande porte ou foco em múltiplos personagens.
- **num_languages > 1**: Maior sofisticação ou realismo.

---

## 3. Features de Histórico (Past Success)

### ✅ **Features: `director_prev_nominations`, `cast_prev_nominations`**

**O que significa:**
- **`director_prev_nominations`**: Quantas vezes o diretor já foi indicado ao Oscar (em qualquer categoria ou especificamente direção) *antes* do lançamento deste filme.
- **`cast_prev_nominations`**: Soma das indicações passadas dos atores principais do elenco.

**Por que é importante:**
- **Viés de Status**: A Academia tende a reconhecer nomes familiares. Diretores e atores consagrados têm um "imã" para novas indicações (o "efeito halo").
- Um filme mediano de um diretor lendário (ex: Spielberg, Scorsese) tem mais chance de ser visto e votado do que um filme excelente de um desconhecido.

**Interpretação:**
- **0**: Novato ou talento ainda não reconhecido pela Academia.
- **> 0**: Veterano da indústria.
- **Valores altos**: Indicam "Pedigree" de Oscar.

---

## 4. Features de Gênero (Genre Flags)

### ✅ **Features: `is_drama`, `is_biography`, `is_history`**

**O que significa:**
- Flags binárias (0 ou 1) indicando se o filme pertence a esses gêneros específicos.

**Por que é importante:**
- **Oscar Bait**: A Academia tem um viés histórico documentado a favor de Dramas, Biografias e Filmes Históricos.
- Gêneros como Terror, Ficção Científica e Comédia são historicamente sub-representados nas categorias principais.
- Essas features ajudam o modelo a aprender esse "preconceito" da Academia.

**Interpretação:**
- **1**: O filme se encaixa no perfil temático clássico da Academia.

---

## 5. Features de Consenso e Buzz (Pedigree)

### ✅ **Features: `n_samples`, `mean_score`, `median_score`, `stddev_score`**

**O que significa:**
- Estatísticas derivadas de agregações de críticas ou avaliações detalhadas.
- **`n_samples`**: Quantidade de avaliações consideradas (robustez da amostra).
- **`mean_score` / `median_score`**: A tendência central da qualidade percebida.
- **`stddev_score`**: O desvio padrão das avaliações (mede o consenso).

**Por que é importante:**
- **Qualidade vs. Polêmica**:
    - **`stddev_score` baixo**: Consenso. Todo mundo concorda que o filme é bom (ou ruim).
    - **`stddev_score` alto**: Filme "ame ou odeie" (polarizante). Filmes polarizantes têm mais dificuldade em ganhar no sistema de voto preferencial da Academia, que favorece filmes de amplo consenso.
- **`mean_score`**: Proxy direto para qualidade crítica.

---

## ❌ Features Removidas / Não Utilizadas

As seguintes features foram analisadas mas **não incluídas** no modelo final:

1.  **`roi_worldwide`**: Focamos em `box_office_rank` para evitar distorções de orçamento e inflação. O lucro percentual (ROI) é mais relevante para investidores do que para a Academia.
2.  **`us_market_share`**: Dados nem sempre disponíveis ou confiáveis para todos os filmes históricos, e a Academia tem se tornado mais internacional.
3.  **`revenue_per_minute`**: Testes mostraram baixa correlação com indicações.
4.  **`budget_category`**: Substituído por features contínuas e proxies de produção (`num_cast`, etc).
