# Cronograma Focado: Predição Oscar 2025

## 🎯 Objetivo

Criar modelo de ML para prever top 10 filmes indicados ao Oscar 2025, seguindo um caminho direto e eficiente.

---

## ✅ Fase 1: EDA (Em Andamento)

**Status**: Notebook criado, carregando dados

- [x] Setup do ambiente
- [x] Exportação de dados
- [x] Criação do notebook `01_eda.ipynb`
- [ ] Executar análise exploratória completa
- [ ] Documentar insights principais

---

## 📊 Fase 2: Feature Engineering (Essenciais)

### 2.2 Features Derivadas Numéricas ⭐

- ROI (Return on Investment) - já existe
- `us_market_share` = domestic_gross / worldwide_gross
- `revenue_per_minute` = worldwide_gross / runtime
- `votes_normalized_by_year` (z-score)
- `rating_normalized_by_year` (z-score)
- `box_office_rank_in_year`
- `budget_category` (low, medium, high)

### 2.3 Features de Histórico (Prestígio) ⭐

- `director_previous_nominations` - Indicações anteriores do diretor
- `director_previous_wins` - Vitórias anteriores do diretor
- `cast_previous_nominations` - Indicações anteriores dos atores principais

**Como fazer**: Criar queries SQL para calcular histórico até o ano anterior ao filme

### 2.4 Features Categóricas - One-Hot Encoding ⭐

- Top 15 gêneros mais frequentes → one-hot
- Top 20 diretores mais frequentes → one-hot
- Top 5 países → one-hot
- Features booleanas: `is_drama`, `is_biography`, `is_thriller`

---

## 🔧 Fase 3: Preparação de Dados

### 3.1 Tratamento de Valores Ausentes ⭐

- Decidir estratégia para cada feature com NULLs
- Imputação para `metascore`, `budget`, `box_office`
- Criar flags de missing quando apropriado
- Documentar decisões

### 3.3 Seleção Final de Features ⭐

- Listar todas as features disponíveis
- Remover features com alta correlação (redundantes)
- Remover features com muitos missing values
- Criar lista final de features para modelo

### 3.4 Split Temporal do Dataset ⭐ **CRÍTICO**

```
Treino:    2000-2019 (20 anos)
Validação: 2020-2022 (3 anos)
Teste:     2023-2024 (2 anos)
Predição:  2025 (futuro real)
```

**NÃO usar split aleatório!** Respeitar temporalidade é essencial.

### 3.7 Consolidação ⭐

- Criar pipeline de pré-processamento
- Salvar dados finais prontos para ML
- Salvar artifacts (scaler, encoder, etc.)

> **⚠️ DECISÕES PENDENTES**:
>
> - **3.5 Normalização/Padronização**: Estudar e decidir se aplicar
> - **3.6 Balanceamento de Classes**: Avaliar relevância para nossos dados (186 indicados vs 2,995 não-indicados)

---

## 🤖 Fase 4: Modelagem e Treinamento (COMPLETA)

### 4.1 Setup de Avaliação ⭐

- Métricas: F1, Precision, Recall, AUC-ROC
- Função de avaliação reutilizável
- Validação cruzada temporal

### 4.2 Baseline: Dummy Classifier ⭐

- DummyClassifier (stratified)
- Performance mínima aceitável

### 4.3 Logistic Regression ⭐

- Modelo básico
- Regularização (L1, L2, ElasticNet)
- Tuning de hiperparâmetro C
- Interpretação de coeficientes

### 4.4 Random Forest ⭐

- Modelo básico
- Tuning: n_estimators, max_depth, min_samples_split
- Feature importance

### 4.5 XGBoost ⭐

- Modelo básico
- Tuning: learning_rate, max_depth, n_estimators, subsample
- Early stopping
- Feature importance

### 4.6 LightGBM ⭐

- Modelo básico
- Tuning de hiperparâmetros
- Feature importance

### 4.7 Outros Modelos (Opcional)

- CatBoost (bom para categóricas)

### 4.8 Comparação de Modelos ⭐

- Tabela comparativa de métricas
- ROC curves
- Precision-Recall curves
- **Selecionar melhor modelo**

### 4.9 Ensemble (Opcional)

- Voting Classifier
- Avaliar se melhora performance

### 4.10 Consolidação ⭐

- Salvar melhor modelo
- Documentar hiperparâmetros finais

---

## 📈 Fase 5: Avaliação (Essencial)

### 5.1 Avaliação no Conjunto de Validação ⭐

- Aplicar melhor modelo em dados 2020-2022
- Calcular todas as métricas
- Confusion Matrix
- Precision, Recall, F1
- AUC-ROC

### 5.2 Avaliação no Conjunto de Teste ⭐

- Aplicar modelo em dados 2023-2024
- Comparar com indicações reais conhecidas
- Verificar overfitting
- Documentar performance final

> **⚠️ DECISÕES PENDENTES**:
>
> - **5.3 Análise de Erros**: Avaliar se é necessário aprofundar
> - **5.4 Feature Importance**: Pode ser útil para interpretabilidade
> - **5.5 Calibração de Probabilidades**: Avaliar necessidade

---

## 🎬 Fase 6: Predição para 2025 (COMPLETA - OBJETIVO FINAL)

### 6.1 Preparação de Dados 2025 ⭐

- Filtrar filmes com `release_year = 2025`
- Verificar completude de features
- Aplicar mesmas transformações/normalizações

### 6.2 Geração de Predições ⭐

- Carregar modelo treinado final
- Aplicar modelo aos dados de 2025
- Gerar probabilidades de indicação
- **Rankear filmes por probabilidade**

### 6.3 Análise de Resultados ⭐

- **Top 10 filmes** com maior probabilidade
- Top 20 para margem de segurança
- Features mais importantes de cada filme
- Identificar "surpresas"

### 6.4 Validação de Sanity ⭐

- Predições fazem sentido?
- Filmes conhecidos estão bem posicionados?
- Há surpresas interessantes?

### 6.5 Documentação de Predições ⭐

- Relatório final com:
  - Top N filmes preditos
  - Probabilidades
  - Features mais importantes
  - Justificativas do modelo

### 6.6 Consolidação ⭐

- Exportar resultados em formatos compartilháveis
- Criar visualizações

---

## 📅 Cronograma Estimado (Versão Focada)

| Fase                   | Tempo Estimado | Prioridade |
| ---------------------- | -------------- | ---------- |
| 1. EDA (finalizar)     | 1 sessão       | ✅ Alta    |
| 2. Feature Engineering | 2 sessões      | ⭐ Alta    |
| 3. Preparação de Dados | 1-2 sessões    | ⭐ Alta    |
| 4. Modelagem Completa  | 3 sessões      | ⭐ Alta    |
| 5. Avaliação Essencial | 1 sessão       | ⭐ Alta    |
| 6. Predição 2025       | 1 sessão       | 🎯 CRÍTICA |

**Total: 9-11 sessões** (vs. 11-18 do plano original)

---

## 🚀 Próximos Passos Imediatos

1. ✅ **Finalizar EDA** - Executar notebook `01_eda.ipynb` completamente
2. ⏭️ **Feature Engineering** - Criar features derivadas, histórico, one-hot encoding
3. ⏭️ **Preparação** - Tratar missing, split temporal, consolidar
4. ⏭️ **Modelagem** - Testar modelos e selecionar melhor
5. ⏭️ **Avaliação** - Validar performance
6. 🎯 **PREDIÇÃO 2025** - Resultado final!

---

## 📝 Decisões a Tomar Durante o Processo

1. **Normalização (3.5)**: Estudar e decidir se StandardScaler/MinMaxScaler são necessários
2. **Balanceamento (3.6)**: Avaliar se SMOTE ou class_weight são necessários dado nosso ratio 1:16
3. **Análise de Erros (5.3)**: Avaliar profundidade da análise de erros
4. **Modelos opcionais**: Decidir se testa SVM, Neural Networks, ou apenas tree-based models

---

## 💡 Principais Diferenças do Plano Original

**Removido/Simplificado:**

- ❌ Features temporais (2.1)
- ❌ Features de texto/NLP (2.5)
- ❌ Tratamento de outliers (3.2)
- ❌ Análise aprofundada de erros (5.3-5.6, opcional)
- ❌ Documentação final formal (Fase 7)

**Mantido como essencial:**

- ✅ Features numéricas derivadas
- ✅ Histórico de prestígio
- ✅ One-hot encoding de categóricas
- ✅ Split temporal CRÍTICO
- ✅ Modelagem completa (testar vários algoritmos)
- ✅ Avaliação no conjunto de validação e teste
- ✅ **Predição 2025 completa**

---

**Foco**: Chegar em predições confiáveis para 2025 o mais rápido possível, mantendo qualidade técnica! 🎯
