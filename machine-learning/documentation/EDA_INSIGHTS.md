# Insights da Análise Exploratória de Dados (EDA)

## 📋 O que descobrimos:

### 1. **Balanceamento de Classes** ⚠️

- **Filmes não-indicados**: 2,995 (94.2%)
- **Filmes indicados**: 186 (5.8%)
- **Ratio de desbalanceamento**: 1:16 (muito desbalanceado!)
- **Ação necessária**: Aplicar técnicas de balanceamento (SMOTE, class_weight ou undersampling) na Fase 3.6

### 2. **Dados Faltantes** 📊

- **`metascore`**: 1 missing (0.03%) - praticamente completo ✅
- **Features de rating samples**: 38 missing (1.2%) - excelente
- **Demais features**: completas (0% missing) ✅

### 3. **Features Numéricas Promissoras** ⭐

Baseado nas estatísticas descritivas:

- **`imdb_rating`**: Média 6.68 (range 1.7-9.1) - boa variabilidade
- **`imdb_votes`**: Média 213k - indica popularidade
- **`metascore`**: Média 58.5 (range 9-100) - críticas são importantes
- **Features Metacritic** (`mean_score`, `median_score`): Boas distribuições

### 4. **Features de Contagem** 📈

- **`num_genres`**: Média 2.69 (maioria tem 2-3 gêneros)
- **`num_countries`**: Média 2.03 (muitos são coproduções)
- **`num_languages`**: Média 1.93
- **`num_directors`**: Média 1.10 (maioria tem 1 diretor)
- **`num_writers`**: Média 2.65
- **`num_cast`**: Média 4.83 (sempre 5 atores principais)

### 5. **Insights Importantes para Feature Engineering** 💡

- **`metascore` quase completo** (99.97%) → Feature muito valiosa!
- **Ratings do Metacritic** (`mean_score`, `median_score`) → Alta qualidade dos dados
- **Features de pessoas** (`num_directors`, `num_writers`) → Podem ser úteis para prestígio
- **Período coberto**: 1999-2025 (26 anos) → Bom para split temporal

### 6. **Próximas Actions Críticas** 🎯

1. **Criar features de prestígio**: histórico de indicações de diretores/atores
2. **One-hot encoding**: top gêneros, diretores, países
3. **Lidar com desbalanceamento**: SMOTE ou class_weight='balanced'
