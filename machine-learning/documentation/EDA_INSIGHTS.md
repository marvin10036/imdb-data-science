# Insights da Análise Exploratória de Dados (EDA)

## 📋 O que descobrimos:

### 1. **Balanceamento de Classes** ⚠️

- **Filmes não-indicados**: 2,995 (94.2%)
- **Filmes indicados**: 186 (5.8%)
- **Ratio de desbalanceamento**: 1:16 (muito desbalanceado!)
- **Ação necessária**: Aplicar técnicas de balanceamento (SMOTE, class_weight ou undersampling) na Fase 3.6

### 2. **Dados Faltantes** 📊

- **`metascore`**: 1 missing (0.03%) - praticamente completo ✅
- **`budget`**: 309 missing (9.7%) - precisa de imputação ⚠️
- **`worldwide_gross`**: 145 missing (4.6%) - aceitável
- **`domestic_gross`**: 243 missing (7.6%) - aceitável
- **`roi_worldwide`**: 369 missing (11.6%) - calculado, derivado de budget/gross
- **Features de rating samples**: 38 missing (1.2%) - excelente
- **Demais features**: completas (0% missing) ✅

### 3. **Features Numéricas Promissoras** ⭐

Baseado nas estatísticas descritivas:

- **`imdb_rating`**: Média 6.68 (range 1.7-9.1) - boa variabilidade
- **`imdb_votes`**: Média 213k - indica popularidade
- **`metascore`**: Média 58.5 (range 9-100) - críticas são importantes
- **`budget`**: Média $77M (outliers até $12.2B!) - precisa normalização
- **`worldwide_gross`**: Média $167M - sucesso comercial importa?
- **`roi_worldwide`**: Média 10.4x (max 12,890x!) - outliers extremos
- **Features Metacritic** (`mean_score`, `median_score`): Boas distribuições

### 4. **Features de Contagem** 📈

- **`num_genres`**: Média 2.69 (maioria tem 2-3 gêneros)
- **`num_countries`**: Média 2.03 (muitos são coproduções)
- **`num_languages`**: Média 1.93
- **`num_directors`**: Média 1.10 (maioria tem 1 diretor)
- **`num_writers`**: Média 2.65
- **`num_cast`**: Média 4.83 (sempre 5 atores principais)

### 5. **Insights Importantes para Feature Engineering** 💡

- **Outliers extremos** em `budget`, `worldwide_gross`, `roi_worldwide` → Aplicar transformação log
- **`metascore` quase completo** (99.97%) → Feature muito valiosa!
- **Ratings do Metacritic** (`mean_score`, `median_score`) → Alta qualidade dos dados
- **Features de pessoas** (`num_directors`, `num_writers`) → Podem ser úteis para prestígio
- **Período coberto**: 1999-2025 (26 anos) → Bom para split temporal

### 6. **Próximas Actions Críticas** 🎯

1. **Imputar** missing values de `budget`, `box_office`
2. **Normalizar/Padronizar** features numéricas (especialmente budget/gross)
3. **Criar features de prestígio**: histórico de indicações de diretores/atores
4. **One-hot encoding**: top gêneros, diretores, países
5. **Lidar com desbalanceamento**: SMOTE ou class_weight='balanced'

---

## 🎯 Próximos Passos (Seguir FOCUSED_ROADMAP):

1. ✅ **EDA Completa** - FEITO!
2. ⏭️ **Feature Engineering** (Fase 2)
   - 2.2: Features Derivadas Numéricas (ROI, market share, etc.)
   - 2.3: Histórico de Prestígio (indicações anteriores)
   - 2.4:One-Hot Encoding (gêneros, diretores, países)
3. ⏭️ **Preparação de Dados** (Fase 3)
   - 3.1: Tratamento de missing values
   - 3.3: Seleção final de features
   - 3.4: Split temporal (**CRÍTICO**)
   - 3.7: Consolidação
4. ⏭️ **Modelagem** (Fase 4 - testar vários algoritmos)
5. ⏭️ **Avaliação** (Fase 5.1-5.2)
6. 🎯 **PREDIÇÃO 2025** (Fase 6 - objetivo final!)

---

## 📝 Como usar este documento:

Cole este conteúdo na última célula markdown do notebook `01_eda.ipynb`, substituindo os placeholders `[PREENCHER APÓS...]`.
