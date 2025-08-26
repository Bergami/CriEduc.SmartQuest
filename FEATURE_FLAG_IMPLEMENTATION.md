# 🚩 Feature Flag Implementation - Análise Refatorada

## 📋 Visão Geral

Implementação de feature flag (`use_refactored`) para permitir rollout gradual das melhorias no sistema de análise de documentos. O sistema agora suporta duas versões:

- **Versão Padrão (Legado)**: `use_refactored=false` (padrão)
- **Versão Refatorada**: `use_refactored=true` (melhorias)

## 🔧 Implementação Técnica

### 1. Modificações no AnalyzeService

**Arquivo**: `app/services/analyze_service.py`

```python
async def process_document(
    file: UploadFile, 
    email: str, 
    use_json_fallback: bool = False,
    use_refactored: bool = False  # ← NOVA FLAG
) -> Dict[str, Any]:
```

**Comportamentos**:
- `use_refactored=False`: Usa processamento legado (backward compatible)
- `use_refactored=True`: Ativa melhorias refatoradas

### 2. Modificações na API

**Arquivo**: `app/api/controllers/analyze.py`

```python
@router.post("/analyze_document")
async def analyze_document(
    request: Request,
    email: str = Query(...),
    file: UploadFile = File(None),
    use_mock: bool = Query(False),
    use_refactored: bool = Query(False)  # ← NOVO PARÂMETRO
):
```

## 🆕 Melhorias da Versão Refatorada

### 1. Remoção de Campo Desnecessário
- **Problema**: Campo `associated_figures` poluindo JSON de resposta
- **Solução**: `RefactoredContextBlockBuilder.remove_associated_figures_from_result()`

### 2. Imagens em Context Blocks
- **Problema**: Imagens base64 não aparecendo nos context_blocks
- **Solução**: Inclusão automática de imagens nos context blocks avançados

### 3. Análise Dinâmica
- **Problema**: Lógica hardcoded para exame específico
- **Solução**: Sistema de enums e análise dinâmica genérica

### 4. Associação Espacial
- **Problema**: Textos descritivos não associados às figuras
- **Solução**: Algoritmo de proximidade espacial para associar textos

## 📊 Arquivos Envolvidos

### Arquivos Criados
```
app/core/constants/
├── instruction_patterns.py    # Padrões de detecção de instruções
└── content_types.py          # Sistema de enums

app/services/
└── refactored_context_builder.py  # Context builder refatorado
```

### Arquivos Modificados
```
app/services/analyze_service.py      # Feature flag logic
app/api/controllers/analyze.py       # API parameter
```

## 🧪 Como Testar

### 1. Via API (Recomendado)

**Versão Padrão:**
```bash
curl -X POST "http://localhost:8000/analyze/analyze_document" \
  -F "email=test@example.com" \
  -F "use_mock=true" \
  -F "use_refactored=false"
```

**Versão Refatorada:**
```bash
curl -X POST "http://localhost:8000/analyze/analyze_document" \
  -F "email=test@example.com" \
  -F "use_mock=true" \
  -F "use_refactored=true"
```

### 2. Via Script de Teste
```bash
python test_feature_flag.py
```

### 3. Via Exemplos da API
```bash
python api_test_examples.py
```

## 🔍 Validação das Melhorias

### Checklist de Testes
- [ ] ✅ Campo `associated_figures` removido (apenas versão refatorada)
- [ ] ✅ Imagens base64 presentes nos context_blocks
- [ ] ✅ Análise dinâmica funcionando (sem hardcoding)
- [ ] ✅ Sistema de enums ativo
- [ ] ✅ Associação espacial texto-figura
- [ ] ✅ Backward compatibility mantida

### Diferenças Esperadas

**Versão Padrão vs Refatorada:**

| Aspecto | Padrão | Refatorada |
|---------|--------|------------|
| `associated_figures` | Presente | **Removido** |
| Context block images | Básico | **Com base64** |
| Análise de conteúdo | Hardcoded | **Dinâmica** |
| Categorização | Manual | **Enum system** |
| Texto-figura | Básica | **Proximidade espacial** |

## 🚀 Plano de Rollout

### Fase 1: Teste Interno
- [ ] Validar feature flag em ambiente de desenvolvimento
- [ ] Executar testes automatizados
- [ ] Comparar resultados lado a lado

### Fase 2: Teste Beta
- [ ] Ativar para usuários específicos
- [ ] Coletar feedback e métricas
- [ ] Ajustar conforme necessário

### Fase 3: Rollout Gradual
- [ ] Aumentar porcentagem de usuários
- [ ] Monitorar performance
- [ ] Preparar para migração completa

### Fase 4: Migração Completa
- [ ] Trocar padrão para `use_refactored=true`
- [ ] Deprecar versão legado
- [ ] Remover código antigo

## 🔧 Manutenção

### Logs de Debug
A versão refatorada inclui logs específicos:
```
🔄 DEBUG: Usando versão REFATORADA com melhorias
✅ DEBUG: Campo 'associated_figures' removido do resultado
```

### Monitoramento
- Performance: Comparar tempo de processamento
- Qualidade: Validar precisão das melhorias
- Estabilidade: Monitorar erros e exceções

## 📚 Recursos Adicionais

- **Documentação técnica**: Ver arquivos de constants e builder
- **Testes**: Scripts de validação incluídos
- **Exemplos**: `api_test_examples.py` para referência
