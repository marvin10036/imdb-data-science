# Análise: Features Derivadas - O Que Já Temos vs. O Que Falta

## 📊 Comparação Completa

### ✅ Features JÁ DISPONÍVEIS na View `ml_training_dataset`

#### 1. **ROI (Return on Investment)** ✅

```sql
-- Linha 134 do DDL:
(CASE WHEN mbo.budget > 0 THEN mbo.worldwide_gross / mbo.budget ELSE NULL END) AS roi_worldwide
```

**Status**: ✅ **JÁ EXISTE! Não precisa criar.**

---

### ❌ Features QUE PRECISAM SER CRIADAS (Fase 2.2)

#### 2. **`us_market_share`** ❌

```python
# Precisa criar:
us_market_share = domestic_gross / worldwide_gross
```

**Onde**: Não existe na view  
**Ação**: Criar via Python ou atualizar view SQL

**📌 Por Que Criar?**

> O Oscar é uma premiação **americana** (Academy of Motion Picture Arts and Sciences). Filmes com maior apelo no mercado doméstico (EUA) historicamente têm mais chances de indicação.

**🎯 Importância para Predição:**

- **Alta relevância** - Academia é composta majoritariamente por membros americanos
- Filmes "muito internacionais" (baixo market share nos EUA) podem ter menos visibilidade
- Exemplos: Filmes de estúdio americanos tendem a ter 40-60% de receita doméstica
- Filmes indie/internacionais podem ter <20% doméstica mas ainda assim ganhar (ex: Parasita)

**💡 Insight Esperado:**

- Filmes com `us_market_share` entre 30-70% podem ter maior probabilidade
- Muito baixo (<10%) ou muito alto (>90%) podem indicar nichos específicos

**✅ Recomendação: CRIAR** - Feature relevante e fácil de calcular

#### 3. **`revenue_per_minute`** ❌

```python
# Precisa criar:
revenue_per_minute = worldwide_gross / runtime_minutes
```

**Onde**: Não existe na view  
**Ação**: Criar via Python ou atualizar view SQL

**📌 Por Que Criar?**

> Mede "eficiência comercial" do filme - quanto ele fatura por minuto de duração. Pode indicar engajamento da audiência.

**🎯 Importância para Predição:**

- **Baixa-Média relevância** - Não é um fator direto para Academia
- Pode correlacionar indiretamente com "qualidade percebida" (filmes muito longos e pouco rentáveis podem ser enfadonhos)
- Filmes de Oscar tendem a ser mais longos (120-180 min), mas nem sempre mais rentáveis

**💡 Insight Esperado:**

- Feature pode ter poder discriminativo limitado
- Correlação com `roi_worldwide` pode ser alta (redundância)
- Blockbusters curtos (90min) com alta bilheteria vs. dramas longos (150min) com baixa bilheteria

**⚠️ Recomendação: AVALIAR** - Criar apenas se houver tempo. Testar correlação com ROI depois.

#### 4. **`votes_normalized_by_year`** ❌

```python
# Precisa criar (z-score):
votes_normalized_by_year = (imdb_votes - mean_votes_per_year) / std_votes_per_year
```

**Onde**: Não existe na view (precisa calcular por ano)  
**Ação**: Criar via Python (pandas groupby)

**📌 Por Que Criar?**

> Normalizar `imdb_votes` para comparar filmes entre diferentes anos. IMDb cresceu ao longo do tempo = mais votos em anos recentes.

**🎯 Importância para Predição:**

- **Alta relevância** - Votos do IMDb indicam **popularidade** e **awareness**
- Filmes de Oscar não precisam ser os mais populares, mas precisam ter visibilidade mínima
- Normalização por ano elimina viés temporal (filme de 2000 com 50k votos ≠ filme de 2023 com 50k votos)

**💡 Insight Esperado:**

- Filmes com z-score muito baixo (<-1.5) raramente são indicados (muito obscuros)
- Filmes com z-score muito alto (>2.0) podem ser blockbusters comerciais sem apelo artístico
- "Sweet spot" pode estar entre z-score 0 a 1.5

**✅ Recomendação: CRIAR** - Feature crítica para corrigir viés temporal!

#### 5. **`rating_normalized_by_year`** ❌

```python
# Precisa criar (z-score):
rating_normalized_by_year = (imdb_rating - mean_rating_per_year) / std_rating_per_year
```

**Onde**: Não existe na view  
**Ação**: Criar via Python (pandas groupby)

**📌 Por Que Criar?**

> Normalizar `imdb_rating` para comparar **qualidade percebida** entre anos. Inflação de ratings ao longo do tempo existe.

**🎯 Importância para Predição:**

- **Média relevância** - Ratings do IMDb refletem gosto popular, não necessariamente da Academia
- Academia pode preferir filmes "difíceis" com ratings medianos (7.0-7.5) vs. blockbusters (8.0+)
- Normalização menos crítica que votes (ratings IMDb variam menos entre anos ~6.5-7.0)

**💡 Insight Esperado:**

- Correlação com `imdb_rating` bruto será alta (possível redundância)
- Benefício marginal pode ser pequeno
- Mais útil se houver mudanças drásticas na distribuição de ratings ao longo dos anos

**⚠️ Recomendação: OPCIONAL** - Criar se `votes_normalized` mostrar benefício. Senão, usar `imdb_rating` bruto mesmo.

#### 6. **`box_office_rank_in_year`** ❌

```python
# Precisa criar:
box_office_rank_in_year = rank() OVER (PARTITION BY release_year ORDER BY worldwide_gross DESC)
```

**Onde**: Não existe na view  
**Ação**: Criar via SQL (pode adicionar na view) ou Python (pandas rank)

**📌 Por Que Criar?**

> Captura **posição relativa** do filme no ano de lançamento. Melhor que valor absoluto de bilheteria (que varia com inflação).

**🎯 Importância para Predição:**

- **Alta relevância** - Filmes de Oscar geralmente estão entre os top 20-50 do ano em bilheteria
- Sucessos comerciais extremos (top 3) podem ser blockbusters sem qualidade artística
- Fracassos totais (rank >200) raramente são indicados (falta de alcance)
- Normaliza naturalmente para tamanho do mercado em cada ano

**💡 Insight Esperado:**

- Filmes indicados provavelmente terão `rank` entre 10-100
- Correlação negativa com indicação se rank < 5 (blockbusters puros)
- Correlação negativa se rank > 150 (filmes muito obscuros)
- Feature pode substituir `worldwide_gross` absoluto (menos afetado por inflação)

**✅ Recomendação: CRIAR** - Feature muito relevante e elimina viés de inflação!

#### 7. **`budget_category`** ❌

```python
# Precisa criar (low, medium, high):
budget_category = pd.cut(budget, bins=[0, 20M, 80M, inf], labels=['low', 'medium', 'high'])
```

**Onde**: Não existe na view  
**Ação**: Criar via Python

**📌 Por Que Criar?**

> Categorizar orçamento em faixas. Permite modelo capturar relações **não-lineares** entre budget e indicação ao Oscar.

**🎯 Importância para Predição:**

- **Média relevância** - Orçamento influencia qualidade de produção
- Filmes low-budget (<$20M) podem ganhar se forem "indie darlings" (Moonlight, Whiplash)
- Filmes high-budget (>$80M) tendem a ser blockbusters ou épicos (Duna, Avatar)
- Medium-budget ($20M-$80M) = sweet spot para dramas de prestígio?

**💡 Insight Esperado:**

- Categoria pode ajudar modelo a distinguir:
  - **Low**: Indie/arte (alta variância - alguns ganham, maioria não)
  - **Medium**: Dramas de estúdio (maior taxa de indicação?)
  - **High**: Blockbusters (menor taxa de indicação, salvo exceções técnicas)
- Feature categórica pode capturar padrões que `budget` numérico perde

**⚠️ Recomendação: OPCIONAL** - Criar se modelo for tree-based (RF, XGBoost). Menos útil para regressão logística.

---

## 📋 Resumo Executivo

| Feature                     | Status    | Onde Está                         | Ação Necessária |
| --------------------------- | --------- | --------------------------------- | --------------- |
| `roi_worldwide`             | ✅ EXISTE | `ml_training_dataset` view (L134) | Nenhuma         |
| `us_market_share`           | ❌ FALTA  | -                                 | Criar           |
| `revenue_per_minute`        | ❌ FALTA  | -                                 | Criar           |
| `votes_normalized_by_year`  | ❌ FALTA  | -                                 | Criar (z-score) |
| `rating_normalized_by_year` | ❌ FALTA  | -                                 | Criar (z-score) |
| `box_office_rank_in_year`   | ❌ FALTA  | -                                 | Criar (rank)    |
| `budget_category`           | ❌ FALTA  | -                                 | Criar (binning) |

**Total**: 1/7 existente (14%) | **6 precisam ser criadas** (86%)

---

## 📚 FEATURES IMPLEMENTADAS - GUIA DE INTERPRETAÇÃO

### ✅ **Feature 1: `roi_worldwide`** (JÁ EXISTIA)

**Fórmula SQL:**

```sql
(CASE WHEN budget > 0 THEN worldwide_gross / budget ELSE NULL END) AS roi_worldwide
```

**O que significa:**

- **ROI = Return on Investment** (Retorno sobre Investimento)
- Quantas vezes o filme retornou o investimento inicial

**Como interpretar:**

| Valor ROI      | Significado                     | Exemplo                                      |
| -------------- | ------------------------------- | -------------------------------------------- |
| **< 1.0**      | Prejuízo (não recuperou budget) | Flop comercial                               |
| **1.0 - 2.0**  | Recuperou budget, lucro modesto | Break-even                                   |
| **2.0 - 5.0**  | Lucro bom                       | Sucesso comercial                            |
| **5.0 - 10.0** | Lucro muito bom                 | Grande sucesso                               |
| **> 10.0**     | Lucro excepcional               | Fenômeno (ex: baixo budget, alta bilheteria) |

**Valores normais:**

- **Filmes de Oscar**: ROI entre 1.5 - 5.0 (lucro moderado)
- **Blockbusters**: ROI entre 2.0 - 4.0
- **Indies de sucesso**: ROI pode ser > 10.0 (budget baixo, retorno alto)

**Exemplo real:**

- **Get Out (2017)**: Budget $4.5M, Gross $255M → ROI = **56.7** (fenômeno!)
- **Avatar (2009)**: Budget $237M, Gross $2.9B → ROI = **12.2** (blockbuster épico)

---

### ✅ **Feature 2: `us_market_share`** (IMPLEMENTADA)

**Fórmula SQL:**

```sql
(CASE WHEN worldwide_gross > 0 THEN domestic_gross / worldwide_gross ELSE NULL END) AS us_market_share
```

**O que significa:**

- **Percentual da bilheteria total que veio do mercado doméstico (EUA)**
- Indica se o filme teve apelo mais americano ou internacional

**Como interpretar:**

| Valor         | Significado                    | Perfil do Filme                                              |
| ------------- | ------------------------------ | ------------------------------------------------------------ |
| **< 20%**     | Muito internacional            | Franquias globais (Fast & Furious, Transformers)             |
| **20% - 30%** | Internacional com presença USA | Blockbusters globais                                         |
| **30% - 40%** | Balanceado                     | Filmes de amplo apelo                                        |
| **40% - 60%** | Forte apelo doméstico          | Filmes americanos de estúdio                                 |
| **> 60%**     | Muito doméstico                | Comédias/dramas americanos, pouca distribuição internacional |

**Valores normais:**

- **Filmes de Oscar**: 30-50% (boa presença nos EUA, mas distribuição global)
- **Comédias americanas**: 60-80% (humor local)
- **Franquias de ação**: 15-30% (mercado global)

**Exemplos reais (2023):**

- **Barbie**: 44.0% (blockbuster americano com apelo global)
- **Oppenheimer**: 33.8% (drama de prestígio, forte fora dos EUA)
- **Fast X**: 20.7% (franquia global, baixa dependência dos EUA)

---

### ✅ **Feature 3: `box_office_rank_in_year`** (IMPLEMENTADA)

**Fórmula SQL:**

```sql
RANK() OVER (PARTITION BY release_year ORDER BY worldwide_gross DESC NULLS LAST) AS box_office_rank_in_year
```

**O que significa:**

- **Posição do filme no ano** ordenado por bilheteria mundial
- Rank 1 = maior bilheteria do ano

**Como interpretar:**

| Rank       | Significado     | Probabilidade Oscar                   |
| ---------- | --------------- | ------------------------------------- |
| **1-5**    | Top 5 do ano    | Baixa (blockbusters comerciais puros) |
| **6-20**   | Top 20          | Média (alguns são de prestígio)       |
| **21-50**  | Top 50          | Alta (sweet spot para Oscar)          |
| **51-100** | Top 100         | Média (ainda viável)                  |
| **> 100**  | Fora do top 100 | Baixa (pouca visibilidade)            |

**Por que normaliza melhor que bilheteria bruta:**

- Elimina viés de inflação (filmes de 2000 vs 2023)
- Captura posição relativa no ano
- Filmes #1 de 1999 vs #1 de 2023 são comparáveis

**Valores normais:**

- **Filmes de Oscar**: Rank 10-100 (nem muito comercial, nem obscuro)
- **Vencedor Best Picture**: Geralmente rank 20-80

**Exemplos reais (2023):**

1. Barbie ($1.4B)
2. Super Mario Bros ($1.4B)
3. Oppenheimer ($975M) ← **Candidato a Oscar no top 3!**
4. Guardians Vol. 3 ($845M)
5. Fast X ($714M)

---

### ✅ **Feature 4: `votes_normalized_by_year`** (IMPLEMENTADA)

**Fórmula SQL:**

```sql
(CASE
    WHEN STDDEV(imdb_votes) OVER (PARTITION BY release_year) > 0
    THEN (imdb_votes - AVG(imdb_votes) OVER (PARTITION BY release_year))
         / STDDEV(imdb_votes) OVER (PARTITION BY release_year)
    ELSE NULL
END) AS votes_normalized_by_year
```

**O que significa:**

- **Z-score de votos do IMDb** comparado à média do ano
- Quantos desvios-padrão acima/abaixo da média

**Como interpretar:**

| Z-Score         | Percentil | Significado         | Perfil do Filme                       |
| --------------- | --------- | ------------------- | ------------------------------------- |
| **< -2.0**      | Bottom 2% | Muito obscuro       | Filme indie/nicho, pouca visibilidade |
| **-2.0 a -1.0** | 2-16%     | Abaixo da média     | Pouca popularidade                    |
| **-1.0 a 0**    | 16-50%    | Mediano baixo       | Popularidade moderada-baixa           |
| **0**           | 50%       | Exatamente na média | Filme mediano em popularidade         |
| **0 a 1.0**     | 50-84%    | Mediano alto        | Popularidade moderada-alta            |
| **1.0 a 2.0**   | 84-98%    | Popular             | Bom awareness                         |
| **2.0 a 3.0**   | 98-99.7%  | Muito popular       | Alto awareness                        |
| **> 3.0**       | Top 0.3%  | Extremo outlier     | Fenômeno/blockbuster extremo          |

**Por que é importante:**

- **IMDb cresceu** ao longo do tempo (mais usuários = mais votos)
- Filme de 2000 com 50k votos ≠ filme de 2023 com 50k votos
- Z-score normaliza para comparar entre anos diferentes

**Valores normais:**

- **Filmes de Oscar**: Z-score 0.5 a 2.5 (popular mas não extremo)
- **Blockbusters**: Z-score 2.0 a 4.0+ (muito populares)
- **Indies obscuros**: Z-score < -1.0

**Exemplos reais (2023):**

- **Oppenheimer**: Z = 6.38 (**extremo outlier** - fenômeno viral)
- **Barbie**: Z = 3.84 (top 0.01% - muito popular)
- **Guardians Vol. 3**: Z = 2.40 (top 1% - popular)
- **Super Mario Bros**: Z = 1.03 (top 15% - acima da média)
- **Fast X**: Z = -0.07 (mediano - exatamente na média do ano)

**Validação dos seus dados:**

- Valores entre -3 e +3 = **95% dos dados** (normal!)
- Alguns outliers (4.5, 6.0) = **esperado** (blockbusters extremos)
- Maioria próxima de zero = **esperado** (filmes medianos)

---

### ✅ **Feature 5: `rating_normalized_by_year`** (IMPLEMENTADA)

**Fórmula SQL:**

```sql
(CASE
    WHEN STDDEV(imdb_rating) OVER (PARTITION BY release_year) > 0
    THEN (imdb_rating - AVG(imdb_rating) OVER (PARTITION BY release_year))
         / STDDEV(imdb_rating) OVER (PARTITION BY release_year)
    ELSE NULL
END) AS rating_normalized_by_year
```

**O que significa:**

- **Z-score de rating do IMDb** comparado à média do ano
- Quantos desvios-padrão acima/abaixo da média de rating

**Como interpretar:**

| Z-Score         | Rating Típico | Significado   | Qualidade Percebida        |
| --------------- | ------------- | ------------- | -------------------------- |
| **< -2.0**      | < 5.0         | Muito ruim    | Bottom 2% do ano           |
| **-2.0 a -1.0** | 5.0 - 6.0     | Ruim          | Abaixo da média            |
| **-1.0 a 0**    | 6.0 - 6.5     | Mediano baixo | Levemente abaixo da média  |
| **0**           | ~6.7          | Mediano       | Exatamente na média do ano |
| **0 a 1.0**     | 6.8 - 7.3     | Mediano alto  | Acima da média             |
| **1.0 a 2.0**   | 7.4 - 8.0     | Bom           | Top 16% do ano             |
| **2.0 a 3.0**   | 8.0 - 8.5     | Muito bom     | Top 2% do ano              |
| **> 3.0**       | > 8.5         | Excepcional   | Top 0.3% (obras-primas)    |

**Por que é importante:**

- Inflação de ratings ao longo do tempo (médias variam por ano)
- Academia pode preferir filmes "difíceis" (Z~1.0) vs blockbusters "fáceis" (Z~0)

**Valores normais:**

- **Filmes de Oscar**: Z-score 1.0 a 2.5 (bem avaliados, top 2-16%)
- **Blockbusters comerciais**: Z-score -0.5 a 1.0 (medianos a bons)
- **Filmes ruins**: Z-score < -1.0

**Exemplos reais (2023):**

- **Oppenheimer** (rating 8.3): Z = 2.13 (top 2% - qualidade excepcional)
- **Guardians Vol. 3** (7.9): Z = 1.62 (top 5% - muito bom)
- **Super Mario Bros** (7.1): Z = 0.48 (acima da média)
- **Barbie** (6.8): Z = 0.22 (na média)
- **Fast X** (5.8): Z = -1.18 (abaixo da média - bottom 15%)

**Validação dos seus dados:**

- Valores entre -3 e +3 = **normal** (95% dos dados)
- Valores próximos de zero (0.335, -0.481) = **filmes medianos** (esperado!)
- Alguns negativos extremos (-2.347) = **filmes ruins** (também esperado)

---

## ✅ Checklist de Validação dos Dados

Seus dados estão corretos se:

- [x] **Z-scores têm valores positivos E negativos** ✅
- [x] **Maioria dos z-scores está entre -3 e +3** ✅ (95% dos dados)
- [x] **Alguns outliers existem** (z > 3 ou z < -3) ✅ (blockbusters/flops extremos)
- [x] **US Market Share está entre 0 e 1** (0% a 100%) ✅
- [x] **ROI maioria é > 0** (filmes que tiveram bilheteria) ✅
- [x] **Box Office Rank começa em 1** (maior bilheteria do ano) ✅

**Se seus dados têm essas características, está tudo PERFEITO!** 🎯

---

## 🔧 Recomendação de Implementação

### **Opção 1: Atualizar View SQL** (Recomendado para features simples)

Adicionar na view `ml_training_dataset`:

```sql
-- Adicionar após roi_worldwide:
(CASE WHEN mbo.worldwide_gross > 0
    THEN mbo.domestic_gross / mbo.worldwide_gross
    ELSE NULL END) AS us_market_share,

(CASE WHEN m.runtime_minutes > 0
    THEN mbo.worldwide_gross / m.runtime_minutes
    ELSE NULL END) AS revenue_per_minute,

RANK() OVER (PARTITION BY m.release_year
             ORDER BY mbo.worldwide_gross DESC NULLS LAST) AS box_office_rank_in_year
```

### **Opção 2: Criar via Python** (Recomendado para z-scores e binning)

No notebook de Feature Engineering:

```python
# Z-scores por ano
df['votes_normalized_by_year'] = df.groupby('release_year')['imdb_votes'].transform(
    lambda x: (x - x.mean()) / x.std()
)

df['rating_normalized_by_year'] = df.groupby('release_year')['imdb_rating'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Budget category
df['budget_category'] = pd.cut(
    df['budget'],
    bins=[0, 20_000_000, 80_000_000, float('inf')],
    labels=['low', 'medium', 'high']
)
```

---

## 💡 **Minha Recomendação**

**Abordagem Híbrida**:

1. ✅ **Manter `roi_worldwide` da view** (já existe)
2. 🔧 **Criar as 3 features simples** via SQL (atualizar view):
   - `us_market_share`
   - `revenue_per_minute`
   - `box_office_rank_in_year`
3. 🐍 **Criar as 3 features complexas** via Python:
   - `votes_normalized_by_year` (z-score)
   - `rating_normalized_by_year` (z-score)
   - `budget_category` (binning)

**Por quê?**

- SQL é mais rápido para cálculos simples
- Python pandas é melhor para z-scores (groupby + transform)
- Fica tudo consolidado no banco, exceto operações estatísticas por grupo

---

## 🎯 Decisão Final: Quais Features Criar?

### **Features ESSENCIAIS** ✅ (Alta Prioridade)

| Feature                    | Relevância | Esforço  | Decisão   |
| -------------------------- | ---------- | -------- | --------- |
| `us_market_share`          | 🔥 Alta    | ⚡ Baixo | **CRIAR** |
| `votes_normalized_by_year` | 🔥 Alta    | ⚡ Médio | **CRIAR** |
| `box_office_rank_in_year`  | 🔥 Alta    | ⚡ Baixo | **CRIAR** |

**Justificativa**: Essas 3 features têm **alto impacto** para predição do Oscar e são relativamente **fáceis** de criar.

---

### **Features OPCIONAIS** ⚠️ (Baixa-Média Prioridade)

| Feature                     | Relevância | Esforço  | Decisão                                   |
| --------------------------- | ---------- | -------- | ----------------------------------------- |
| `rating_normalized_by_year` | 🟡 Média   | ⚡ Médio | **AVALIAR** (criar se houver tempo)       |
| `budget_category`           | 🟡 Média   | ⚡ Baixo | **AVALIAR** (útil para tree-based models) |
| `revenue_per_minute`        | 🟠 Baixa   | ⚡ Baixo | **PULAR** (redundância com ROI)           |

**Justificativa**: Benefício marginal pequeno ou potencial redundância com features existentes.

---

### **Recomendação Mínima Viável** (MVP):

**Criar APENAS as 3 essenciais**: ✅ `us_market_share`, `votes_normalized_by_year`, `box_office_rank_in_year`

**Tempo estimado**: 1-2 horas
**Impacto esperado**: Alto

### **Recomendação Completa** (se houver tempo):

**Criar todas exceto** `revenue_per_minute`: 5 features (2, 4, 5, 6, 7)

**Tempo estimado**: 2-3 horas
**Impacto esperado**: Alto a médio

---

## 📊 Resumo Visual

```
Impacto na Predição vs. Esforço de Implementação:

Alta Relevância  │
                 │  ✅ us_market_share
                 │  ✅ votes_normalized
                 │  ✅ box_office_rank
                 │
Média Relevância │     ⚠️ rating_normalized
                 │     ⚠️ budget_category
                 │
Baixa Relevância │        ❌ revenue_per_minute
                 │
                 └─────────────────────────────
                   Baixo    Médio    Alto
                        Esforço
```

---

## 🎯 Próximo Passo

Quer que eu:

1. **Crie apenas as 3 ESSENCIAIS** (MVP - 1-2h de trabalho)?
2. **Crie as 5 recomendadas** (completo, exceto revenue_per_minute)?
3. **Crie todas as 6** (incluindo opcionais)?

Qual prefere?
