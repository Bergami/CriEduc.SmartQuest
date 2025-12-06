# Plano de Renomeação de Nomenclatura "Legacy"

## 📋 Análise Completa

### Status Atual

Após a reversão emergencial, temos 2 arquivos modificados (DTO fix) e toda a nomenclatura "legacy" ainda presente no código.

### Arquivos Modificados (Manter)

```
M app/dtos/api/document_dtos.py       # Fix: options → alternatives
M app/dtos/responses/document_dtos.py # Fix: options → alternatives
```

---

## 🎯 Objetivos da Renomeação

1. **Eliminar termo "legacy"** de nomes de funções, métodos e variáveis
2. **Manter funcionalidade intacta** - zero quebras
3. **Preservar contratos de interface** - mesmas assinaturas onde necessário
4. **Testar cada camada** antes de prosseguir

---

## 📊 Inventário Completo de "Legacy"

### **Categoria 1: Arquivo `legacy_adapter.py`** ⚠️ CRÍTICO

**Localização:** `app/parsers/question_parser/legacy_adapter.py`

#### Impacto:

- ✅ **3 usages** de `extract_questions_from_paragraphs_legacy_compatible`
  - Import em `base.py` linha 6
  - Chamada em `base.py` linha 149
  - Definição em `legacy_adapter.py` linha 70

#### Renomeações Propostas:

```python
# ANTES (atual)
def extract_questions_from_paragraphs_legacy_compatible(paragraphs)

# DEPOIS (proposta)
def extract_questions_from_paragraphs(paragraphs)
```

**Razão:** Este arquivo é um **adapter** que já usa internamente a nova implementação. O nome "legacy_compatible" é enganoso - ele JÁ está usando código novo.

**Dependências:**

1. `app/parsers/question_parser/base.py` - linha 6 (import)
2. `app/parsers/question_parser/base.py` - linha 149 (chamada)
3. Testes de integração (se existirem)

---

### **Categoria 2: Métodos `from_legacy_*` em Models** ⚠️ CRÍTICO

#### 2.1 `InternalQuestion.from_legacy_question()`

**Localização:** `app/models/internal/question_models.py` linha 167

**Usages (grep encontrou 2):**

- `app/parsers/question_parser/base.py` linha 92
- `app/services/core/document_analysis_orchestrator.py` linha 288

**Proposta:**

```python
# ANTES
@classmethod
def from_legacy_question(cls, legacy_question: Dict[str, Any]) -> "InternalQuestion":

# DEPOIS
@classmethod
def from_dict(cls, question_dict: Dict[str, Any]) -> "InternalQuestion":
```

**Razão:** Não é "legacy", é um dict comum do Azure/extraction. O formato dict é permanente.

---

#### 2.2 `InternalAnswerOption.from_legacy_option()`

**Localização:** `app/models/internal/question_models.py` linha 40

**Usages:**

- Chamado por `from_legacy_question()` linha 186

**Proposta:**

```python
# ANTES
@classmethod
def from_legacy_option(cls, legacy_option: Dict[str, Any]) -> "InternalAnswerOption":

# DEPOIS
@classmethod
def from_dict(cls, option_dict: Dict[str, Any]) -> "InternalAnswerOption":
```

---

#### 2.3 `InternalQuestionContent.from_legacy_content()`

**Localização:** `app/models/internal/question_models.py` linha 86

**Usages:**

- Chamado por `from_legacy_question()` linha 178

**Proposta:**

```python
# ANTES
@classmethod
def from_legacy_content(cls, legacy_content: Any) -> "InternalQuestionContent":

# DEPOIS
@classmethod
def from_dict(cls, content_dict: Any) -> "InternalQuestionContent":
```

---

### **Categoria 3: ProcessingContext** ✅ SEGURO

#### 3.1 `ProcessingContext.from_legacy_dict()`

**Localização:** `app/models/internal/processing_context.py` linha 39

**Usages:** Não encontrado em grep (usado apenas em testes?)

**Proposta:**

```python
# ANTES
@classmethod
def from_legacy_dict(cls, legacy_context: Dict[str, Any]) -> 'ProcessingContext':

# DEPOIS
@classmethod
def from_dict(cls, context_dict: Dict[str, Any]) -> 'ProcessingContext':
```

---

#### 3.2 `ProcessingContext.to_legacy_dict()`

**Localização:** `app/models/internal/processing_context.py` linha 64

**Usages:**

- `app/services/core/document_analysis_orchestrator.py` linha 364

**Proposta:**

```python
# ANTES
def to_legacy_dict(self) -> Dict[str, Any]:

# DEPOIS
def to_dict(self) -> Dict[str, Any]:
```

---

### **Categoria 4: Função `convert_to_legacy_format()`** ⚠️ CRÍTICO

**Localização:** `app/parsers/question_parser/azure_paragraph_question_extractor.py` linha 482

**Usages:**

- Import em `legacy_adapter.py` linha 17
- Chamada em `legacy_adapter.py` linha 87

**Proposta:**

```python
# ANTES
def convert_to_legacy_format(extraction_result: ExtractionResult) -> List[Dict[str, Any]]:

# DEPOIS
def convert_to_dict_format(extraction_result: ExtractionResult) -> List[Dict[str, Any]]:
```

**Razão:** Converte `ExtractionResult` (Pydantic) para dict (formato API padrão).

---

### **Categoria 5: ContentType Enum** ✅ MANTER

#### `ContentType.from_legacy_type()`

**Localização:** `app/enums/content_enums.py` linha 44

**Decisão:** **MANTER ESTE NOME**

**Razão:** Este método REALMENTE lida com valores legacy/antigos (strings brutas do Azure). Faz sentido semântico manter "legacy" aqui.

**Usages:**

- `app/utils/content_type_converter.py` linha 63

---

### **Categoria 6: Variáveis e Comentários** ℹ️ BAIXA PRIORIDADE

Diversos comentários e variáveis com "legacy" que são apenas informativos:

- `legacy_options` → `alternatives` ou `options_list`
- Comentários em docstrings
- Mensagens de log

---

## 🔄 Estratégia de Execução Segura

### **Fase 1: Preparação e Validação**

1. ✅ **Commit atual** (DTO fix) para ter checkpoint limpo
2. ✅ **Rodar testes** completos para baseline
3. ✅ **Documentar estado atual** (este plano)

### **Fase 2: Renomear Camada de Conversão (Low-Risk)**

**Objetivo:** Renomear funções de conversão que têm poucos pontos de uso

**Arquivos:**

1. `azure_paragraph_question_extractor.py`

   - `convert_to_legacy_format()` → `convert_to_dict_format()`

2. `legacy_adapter.py`
   - Atualizar import da função acima
   - Atualizar chamada na linha 87
   - Variável `legacy_questions` → `questions_dict`

**Testes:**

- Rodar testes unitários do parser
- Rodar testes de integração
- Testar endpoint manualmente

**Rollback:** `git checkout -- app/parsers/question_parser/`

---

### **Fase 3: Renomear ProcessingContext (Medium-Risk)**

**Objetivo:** Renomear métodos de conversão em ProcessingContext

**Arquivos:**

1. `app/models/internal/processing_context.py`

   - `from_legacy_dict()` → `from_dict()`
   - `to_legacy_dict()` → `to_dict()`

2. `app/services/core/document_analysis_orchestrator.py`
   - Atualizar chamada `to_legacy_dict()` linha 364

**Testes:**

- Rodar testes do orchestrator
- Rodar testes de integração completos

**Rollback:** `git checkout -- app/models/internal/processing_context.py app/services/core/document_analysis_orchestrator.py`

---

### **Fase 4: Renomear Métodos Question Models (HIGH-RISK)** ⚠️

**Objetivo:** Renomear `from_legacy_*` em question_models.py

**⚠️ ESTA FOI A FASE QUE QUEBROU ANTERIORMENTE**

**Arquivos:**

1. `app/models/internal/question_models.py`

   - `from_legacy_question()` → `from_dict()`
   - `from_legacy_option()` → `from_dict()`
   - `from_legacy_content()` → `from_dict()`
   - Parâmetros: `legacy_question` → `question_dict`, etc.
   - Variáveis internas: `legacy_options` → `alternatives`

2. `app/parsers/question_parser/base.py`

   - Atualizar `from_legacy_question()` linha 92

3. `app/services/core/document_analysis_orchestrator.py`
   - Atualizar `from_legacy_question()` linha 288

**Testes CRÍTICOS:**

- ✅ Rodar testes unitários
- ✅ Rodar testes de integração
- ✅ **TESTAR ENDPOINT REAL COM Recuperacao.pdf**
- ✅ **VALIDAR QUE TODAS AS 7 QUESTÕES RETORNAM**
- ✅ Validar questões 1-3 TÊM alternativas
- ✅ Validar questões 4-7 NÃO têm alternativas

**Rollback:** `git checkout -- app/models/internal/question_models.py app/parsers/question_parser/base.py app/services/core/document_analysis_orchestrator.py`

---

### **Fase 5: Renomear Arquivo e Função Principal (FINAL)**

**Objetivo:** Renomear `legacy_adapter.py` e função principal

**Opção A - Conservadora (RECOMENDADA):**
Apenas renomear a função, manter o arquivo:

```python
# Em legacy_adapter.py
def extract_questions_from_paragraphs_legacy_compatible()
# ↓
def extract_questions_from_paragraphs()
```

**Opção B - Completa:**
Renomear arquivo também:

```
legacy_adapter.py → paragraph_adapter.py
```

**Arquivos afetados:**

1. `app/parsers/question_parser/base.py` - linha 6 (import)
2. `app/parsers/question_parser/base.py` - linha 149 (chamada)

**Testes:**

- Mesmos testes da Fase 4
- Validação completa do endpoint

---

## 📝 Checklist de Execução

### Antes de Começar

- [ ] Commit do DTO fix
- [ ] Rodar suite completa de testes (baseline)
- [ ] Anotar resultados: `____ testes passaram`
- [ ] Testar endpoint manualmente e salvar JSON de resposta

### Para Cada Fase

- [ ] Criar branch: `refactor/rename-legacy-phase-N`
- [ ] Fazer renomeações conforme plano
- [ ] Rodar testes unitários
- [ ] Rodar testes de integração
- [ ] **Testar endpoint real** (CRÍTICO para Fase 4+)
- [ ] Comparar JSON antes/depois
- [ ] Se OK: commit com mensagem descritiva
- [ ] Se FALHA: `git checkout -- <arquivos>` e investigar

### Após Todas as Fases

- [ ] Squash commits em um só (opcional)
- [ ] Atualizar documentação
- [ ] Criar PR para review

---

## ⚠️ Pontos de Atenção CRÍTICOS

### 1. **Questões com Alternativas Desaparecem**

**Sintoma anterior:** Após renomeação, questões 1-3 (com alternativas) sumiram.

**Hipótese:** O problema pode estar na conversão `from_dict_option()` onde:

```python
# Linha 184 de question_models.py
legacy_options = legacy_question.get("alternatives", [])
```

Se renomear para `alternatives = question_dict.get("alternatives", [])` mas o dict vier com outra key, pode falhar silenciosamente.

**Validação necessária:**

- Print do dict antes de `from_dict()`
- Verificar se chave é realmente `"alternatives"`
- Confirmar estrutura: `[{"letter": "a", "text": "..."}]`

### 2. **Testes Passam mas Runtime Falha**

**Causa:** Testes unitários não cobrem integração completa.

**Solução:** SEMPRE testar endpoint real após mudanças em question_models.py.

### 3. **Chain de Conversão Frágil**

```
Azure Paragraphs
  → extract_questions_from_azure_paragraphs()
  → convert_to_dict_format()
  → from_dict_question()
  → from_dict_option()
```

Qualquer quebra nessa cadeia = perda de dados.

---

## 🧪 Script de Teste Automatizado

Criar `tests/validate_rename.py`:

```python
"""
Script para validar que renomeação não quebrou extração de questões.
"""
import requests
import json

def test_endpoint_returns_7_questions():
    """Valida que Recuperacao.pdf retorna 7 questões."""
    # TODO: Implementar chamada ao endpoint
    # TODO: Validar response["questions"] tem len == 7
    # TODO: Validar questões 1-3 têm "alternatives"
    # TODO: Validar questões 4-7 têm "alternatives": []
    pass

def test_alternatives_structure():
    """Valida estrutura das alternativas."""
    # TODO: Validar cada alternativa tem {letter, text, isCorrect}
    pass

if __name__ == "__main__":
    test_endpoint_returns_7_questions()
    test_alternatives_structure()
    print("✅ Todos os testes passaram!")
```

---

## 📌 Decisão Final Recomendada

### Opção CONSERVADORA (Recomendada):

1. **Fazer apenas Fases 1-3** (baixo e médio risco)
2. **PARAR na Fase 4** (high-risk que quebrou antes)
3. **Deixar `from_legacy_question()` como está**
4. Viver com alguma nomenclatura "legacy" por ora

**Justificativa:** Sistema funcionando > nomenclatura perfeita

### Opção AGRESSIVA (Apenas se necessário):

1. Fazer todas as fases
2. **Investir em testes de integração robustos ANTES**
3. Adicionar logging detalhado em cada conversão
4. Testar exaustivamente

---

## 🎯 Próximos Passos Imediatos

1. **Commit do DTO fix** (já validado)
2. **Decidir:** Conservadora ou Agressiva?
3. **Se Conservadora:** Executar Fases 1-3
4. **Se Agressiva:** Criar testes de integração primeiro

---

## 📞 Pontos de Decisão

**PERGUNTAR AO USUÁRIO:**

1. Prefere abordagem **CONSERVADORA** (deixar alguns "legacy") ou **AGRESSIVA** (remover tudo)?

2. Quer que eu implemente **script de teste automatizado** antes de prosseguir?

3. Qual fase você quer começar? (Recomendo Fase 2)

---

## 📚 Referências

- Issue #10: Remoção de nomenclatura legacy
- Commit 9b38c57: Último estado estável
- Conversa anterior: Reversão de renomeação que quebrou questões 1-3
