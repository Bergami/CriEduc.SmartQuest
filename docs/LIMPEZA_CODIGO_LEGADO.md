# 🧹 Plano de Limpeza de Código Legado

**Data**: 2025-12-06  
**Branch**: feature/remove-cache-add-duplicate-check

---

## 📋 Resumo Executivo

Após análise completa, identificamos **3 classes não utilizadas** e **diretórios de teste obsoletos** que podem ser removidos com segurança.

---

## 🔴 Classes LEGADAS (Não Usadas)

### 1. `CentralizedFileManager`
- **Arquivo**: `app/services/utils/centralized_file_manager.py`
- **Status**: ❌ **NÃO USADO** na API atual
- **Uso atual**: Apenas em testes unitários e scripts de migração
- **Função**: Salvamento local de PDFs e JSONs em `tests/documents/`
- **Substituído por**: Sistema de persistência MongoDB

**Impacto da Remoção**: ✅ **SEGURO**
- Nenhum endpoint usa
- Nenhum serviço de produção depende
- Apenas testes unitários afetados

---

### 2. `DocumentStorageService`
- **Arquivo**: `app/services/storage/document_storage_service.py`
- **Status**: ❌ **NÃO USADO** na API atual
- **Uso aparente**: Importado em `BaseDocumentProvider`
- **MAS**: `BaseDocumentProvider` também não é usado!
- **Função**: Salvamento local de PDFs e respostas Azure
- **Substituído por**: MongoDB + Azure Blob Storage

**Impacto da Remoção**: ✅ **SEGURO**
- `BaseDocumentProvider` é abstração antiga não utilizada
- API atual usa serviços especializados diretos
- Nenhuma dependência ativa

---

### 3. `ImageSavingService`
- **Arquivo**: `app/services/utils/image_saving_service.py`
- **Status**: ⚠️ **IMPORTADO MAS NÃO USADO**
- **Importado em**: `AzureFiguresExtractor`, `ManualPDFExtractor`
- **MAS**: Método `save_images_from_extraction()` **nunca é chamado**
- **Função**: Salvamento local de imagens em `tests/images/`
- **Substituído por**: Azure Blob Storage direto

**Impacto da Remoção**: ✅ **SEGURO**
- Importações podem ser removidas
- Nenhum salvamento local acontece
- Imagens vão direto para Azure

---

## 📂 Diretórios Obsoletos

### 1. `tests/documents/` (16 arquivos)
- **Conteúdo**: PDFs de teste antigos
- **Criado por**: `DocumentStorageService`, `CentralizedFileManager`
- **Usado por**: Scripts de migração obsoletos
- **Ação**: ✅ **DELETAR** ou mover para `tests/fixtures/legacy_pdfs/`

### 2. `tests/images/` (subdiretórios vazios/antigos)
- **Conteúdo**: 
  - `by_provider/azure/` - Imagens de teste antigas
  - `by_document/` - Diretórios de teste por documento
- **Criado por**: `ImageSavingService`, `DocumentStorageService`
- **Usado por**: Nenhum código ativo
- **Ação**: ✅ **DELETAR** ou mover para `tests/fixtures/legacy_images/`

---

## 🗂️ Documentos .md na Raiz (Mover para docs/archive/)

### Análises Antigas Concluídas:
- ✅ `analise-revisao-completa.md` → `docs/archive/`
- ✅ `ANALISE_LEGACY_REFACTORED.md` → `docs/archive/`
- ✅ `REVIEW_REPORT.md` → `docs/archive/`

### Planos Executados:
- ✅ `plano-adicao-persistencia-mongo.md` → `docs/archive/`
- ✅ `PLANO_RENOMEACAO_LEGACY.md` → `docs/archive/`

### Manter na Raiz (Em Andamento):
- ⚠️ `PLANO_REFATORACAO.md` - Atual
- ⚠️ `SONNET_CODE_REVIEW.md` - Atual
- ⚠️ `CHANGELOG.md` - Vivo
- ⚠️ `README.md` - Principal

---

## 📁 Diretório Vazio

### `app/adapters/`
- **Conteúdo**: Apenas `__init__.py` vazio
- **Usado por**: Nenhum código
- **Ação**: ✅ **DELETAR** completamente

---

## 🗑️ Arquivos Temporários

- ✅ `test_logs.txt` - Log temporário
- ✅ `test_output.txt` - Output temporário

---

## 🎯 Plano de Execução

### Fase 1: Documentação (Seguro - Reversível)
```powershell
# Criar diretório de arquivo
New-Item -ItemType Directory -Force -Path "docs\archive"

# Mover documentos antigos
Move-Item "analise-revisao-completa.md" "docs\archive\"
Move-Item "ANALISE_LEGACY_REFACTORED.md" "docs\archive\"
Move-Item "plano-adicao-persistencia-mongo.md" "docs\archive\"
Move-Item "PLANO_RENOMEACAO_LEGACY.md" "docs\archive\"
Move-Item "REVIEW_REPORT.md" "docs\archive\"
```

### Fase 2: Arquivos Temporários (Seguro)
```powershell
Remove-Item "test_logs.txt"
Remove-Item "test_output.txt"
```

### Fase 3: Diretório Vazio (Seguro)
```powershell
Remove-Item -Recurse -Force "app\adapters\"
```

### Fase 4: Classes Legadas (ATENÇÃO: Testar antes)
```powershell
# Opcional: Mover para legacy/ antes de deletar
New-Item -ItemType Directory -Force -Path "app\legacy"
Move-Item "app\services\utils\centralized_file_manager.py" "app\legacy\"
Move-Item "app\services\storage\document_storage_service.py" "app\legacy\"
Move-Item "app\services\utils\image_saving_service.py" "app\legacy\"
Move-Item "app\services\providers\base_document_provider.py" "app\legacy\"

# Atualizar imports nos extractors (remover ImageSavingService)
```

### Fase 5: Diretórios de Teste (CUIDADO)
```powershell
# Opção A: Deletar completamente
Remove-Item -Recurse -Force "tests\documents\"
Remove-Item -Recurse -Force "tests\images\"

# Opção B: Arquivar (mais seguro)
New-Item -ItemType Directory -Force -Path "tests\fixtures\legacy"
Move-Item "tests\documents\" "tests\fixtures\legacy\"
Move-Item "tests\images\" "tests\fixtures\legacy\"
```

---

## ✅ Checklist de Validação

Antes de deletar, verificar:

- [ ] Rodar todos os testes: `pytest tests/`
- [ ] Verificar imports quebrados: `python -m py_compile app/**/*.py`
- [ ] Testar endpoint principal: `POST /analyze/analyze_document`
- [ ] Verificar logs de erro: Nenhum `ModuleNotFoundError`
- [ ] Git status limpo antes da limpeza

---

## 🔄 Rollback (Se Necessário)

```powershell
# Reverter movimentações
git checkout -- .

# Restaurar de docs/archive/
Move-Item "docs\archive\*" "."

# Restaurar de app/legacy/
Move-Item "app\legacy\*" "app\services\utils\"
```

---

## 📊 Impacto Estimado

| Item | Ação | Risco | Espaço Liberado |
|------|------|-------|-----------------|
| Docs .md | Mover | ✅ Zero | ~500 KB |
| Arquivos temp | Deletar | ✅ Zero | ~100 KB |
| app/adapters/ | Deletar | ✅ Zero | 1 KB |
| Classes legadas | Arquivar | ⚠️ Baixo | ~30 KB |
| tests/documents/ | Arquivar | ⚠️ Médio | ~5 MB |
| tests/images/ | Arquivar | ⚠️ Médio | ~20 MB |

**Total**: ~25 MB liberados

---

## 🎓 Conclusão

O sistema **não precisa mais** de salvamento local de arquivos porque:

1. **PDFs originais**: Armazenados no Azure Blob Storage
2. **Respostas de análise**: Persistidas no MongoDB
3. **Imagens extraídas**: Enviadas direto para Azure Blob Storage
4. **Metadados**: MongoDB (collection `analyze_documents`)

O código de salvamento local (`CentralizedFileManager`, `DocumentStorageService`, `ImageSavingService`) é **LEGADO** da arquitetura antiga pré-MongoDB.

---

**Recomendação**: Executar **Fases 1-3** imediatamente (seguro). Fases 4-5 após validação em ambiente de desenvolvimento.
