# 📋 Plano de Ação - Refatoração SOLID

## Branch: feature/remove-cache-add-duplicate-check

**Data de Criação:** 2025-12-06  
**Baseado em:** SONNET_CODE_REVIEW.md  
**Status:** 🟡 Em Execução

---

## 🎯 Objetivo

Completar a refatoração SOLID com foco em:

- ✅ Robustez (testes de borda e E2E)
- ✅ Segurança (corrigir migration destrutiva)
- ✅ Qualidade de código (dataclass, fixtures)
- ✅ Manutenibilidade (documentação)

---

## 📊 Resumo Executivo

| Prioridade    | Tarefas        | Tempo Total | Status      |
| ------------- | -------------- | ----------- | ----------- |
| 🔴 Crítica    | 4 tarefas      | 11h         | ⏳ Pendente |
| 🟡 Importante | 4 tarefas      | 3.5h        | ⏳ Pendente |
| 🟢 Desejável  | 2 tarefas      | 1h          | ⏳ Pendente |
| **TOTAL**     | **10 tarefas** | **15.5h**   | -           |

---

## 🔴 FASE 1: Crítico - Antes de Produção (11h)

### Tarefa 1.1: Corrigir Migration Destrutiva (2h) ⚠️ URGENTE

**Problema Identificado:**

- Migration atual deleta TODOS os documentos antigos
- Perda de dados em produção se deployar

**Arquivo:** `scripts/migrations/2025-12-06_001000_add_file_size_and_duplicate_index.js`

**Ação:**

```javascript
// ❌ REMOVER (linha ~15):
const deleteResult = db.analyze_documents.deleteMany({});

// ✅ ADICIONAR:
print("🔄 [UPDATE] Adicionando file_size aos documentos existentes...");
const updateResult = db.analyze_documents.updateMany(
  { file_size: { $exists: false } },
  { $set: { file_size: 0 } } // 0 = tamanho desconhecido (doc antigo)
);
print(
  `✅ [UPDATE] ${updateResult.modifiedCount} documentos atualizados com file_size=0`
);
print(
  "ℹ️ [INFO] Documentos antigos preservados. file_size=0 indica documento anterior à migration."
);
```

**Checklist:**

- [ ] Modificar migration script
- [ ] Testar migration em banco de desenvolvimento local
- [ ] Verificar que documentos antigos são preservados
- [ ] Confirmar que índice é criado corretamente
- [ ] Validar que duplicatas antigas não são detectadas (file_size diferente)
- [ ] Commit: `fix: Preservar documentos antigos na migration de file_size`

**Impacto:** CRÍTICO - Evita perda de dados

---

### Tarefa 1.2: Adicionar Testes de Borda (5h)

**Objetivo:** Cobrir casos de falha e erro não testados atualmente

**Arquivo:** `tests/unit/services/test_duplicate_check_service.py` (NOVO)

**Testes a Implementar:**

#### 1.2.1: MongoDB Connection Failure

```python
@pytest.mark.asyncio
async def test_duplicate_check_mongodb_connection_failure():
    """Testa comportamento quando MongoDB não está disponível."""
    # Mock: persistence_service.check_duplicate_document lança ConnectionFailure
    # Espera: Propagar exceção ou retornar should_process=True (fail-safe)
```

#### 1.2.2: Corrupted Document Record

```python
@pytest.mark.asyncio
async def test_duplicate_check_with_corrupted_document_record():
    """Testa registro no MongoDB com dados inválidos."""
    # Mock: existing_doc com response vazio/None
    # Espera: Processar documento normalmente (fail-safe)
```

#### 1.2.3: Invalid File Size

```python
@pytest.mark.asyncio
async def test_duplicate_check_with_invalid_file_size():
    """Testa file_size negativo ou zero."""
    # Mock: file.file.tell() retorna 0
    # Espera: Processar documento ou lançar validação
```

#### 1.2.4: Concurrent Duplicate Checks

```python
@pytest.mark.asyncio
async def test_concurrent_duplicate_checks():
    """Testa race condition ao verificar duplicatas simultaneamente."""
    import asyncio
    # Simula 10 uploads simultâneos do mesmo documento
    # Espera: Todos retornam mesmo resultado (não criar duplicatas)
```

#### 1.2.5: Performance Validation

```python
@pytest.mark.asyncio
async def test_duplicate_check_performance():
    """Valida que verificação é rápida (< 100ms)."""
    import time
    # Mock: persistence retorna em < 50ms
    # Espera: check_and_handle_duplicate < 100ms total
```

**Checklist:**

- [ ] Criar arquivo `tests/unit/services/test_duplicate_check_service.py`
- [ ] Implementar 5 testes de borda
- [ ] Todos os testes passam
- [ ] Cobertura de `DuplicateCheckService` > 90%
- [ ] Commit: `test: Adicionar testes de borda para DuplicateCheckService`

---

### Tarefa 1.3: Adicionar Testes E2E (4h)

**Objetivo:** Validar fluxo completo com MongoDB real

**Arquivo:** `tests/integration/test_duplicate_flow_e2e.py` (NOVO)

**Estrutura:**

#### 1.3.1: Full Duplicate Flow

```python
@pytest.mark.integration
@pytest.mark.asyncio
class TestDuplicateFlowE2E:
    """Testes end-to-end com MongoDB real (testcontainers)."""

    async def test_upload_duplicate_full_flow(self, test_client, mongodb_container):
        """
        Fluxo completo:
        1. Upload documento → processamento completo
        2. Upload mesmo documento → retorna duplicata
        3. Modificar arquivo (size diferente) → reprocessa
        """
        # Upload 1: Novo documento (email=test@test.com, file=sample.pdf)
        response1 = await test_client.post("/analyze/analyze_document", ...)
        assert response1.status_code == 200
        doc_id_1 = response1.json()["document_id"]

        # Upload 2: Duplicata exata (mesmo email, file, size)
        response2 = await test_client.post("/analyze/analyze_document", ...)
        assert response2.status_code == 200
        assert response2.json()["status"] == "already_processed"
        assert response2.json()["document_id"] == doc_id_1  # Mesmo doc
        assert response2.json()["from_database"] == True

        # Verificar que apenas 1 documento no banco
        count = await mongodb_container.analyze_documents.count_documents({})
        assert count == 1

        # Upload 3: Arquivo modificado (size diferente)
        response3 = await test_client.post("/analyze/analyze_document", ...)
        assert response3.status_code == 200
        doc_id_3 = response3.json()["document_id"]
        assert doc_id_3 != doc_id_1  # Novo documento

        # Verificar que agora há 2 documentos
        count = await mongodb_container.analyze_documents.count_documents({})
        assert count == 2
```

#### 1.3.2: MongoDB Index Usage

```python
@pytest.mark.integration
async def test_mongodb_index_usage(self, mongodb_container):
    """Valida que query usa índice idx_duplicate_check."""
    collection = mongodb_container.analyze_documents

    # Verificar que índice existe
    indexes = await collection.list_indexes().to_list(length=None)
    assert any(idx["name"] == "idx_duplicate_check" for idx in indexes)

    # EXPLAIN plan da query
    explain = await collection.find({
        "user_email": "test@test.com",
        "file_name": "sample.pdf",
        "file_size": 1024
    }).explain()

    # Verificar que usa índice (não COLLSCAN)
    assert explain["executionStats"]["executionStages"]["stage"] == "IXSCAN"
    assert "idx_duplicate_check" in explain["executionStats"]["executionStages"]["indexName"]
```

#### 1.3.3: Failed Document Retry

```python
@pytest.mark.integration
async def test_failed_document_allows_retry(self, test_client, mongodb_container):
    """Valida que documentos FAILED podem ser reprocessados."""
    # 1. Inserir documento FAILED manualmente no MongoDB
    await mongodb_container.analyze_documents.insert_one({
        "user_email": "test@test.com",
        "file_name": "failed.pdf",
        "file_size": 2048,
        "status": "FAILED",
        "created_at": datetime.now()
    })

    # 2. Upload mesmo documento
    response = await test_client.post("/analyze/analyze_document", ...)

    # 3. Deve reprocessar (não retornar duplicata)
    assert response.status_code == 200
    assert response.json()["status"] != "already_processed"

    # 4. Verificar que documento foi atualizado para COMPLETED
    doc = await mongodb_container.analyze_documents.find_one({
        "user_email": "test@test.com",
        "file_name": "failed.pdf"
    })
    assert doc["status"] == "COMPLETED"
```

**Requisitos Técnicos:**

- Usar `pytest-asyncio` para testes async
- Usar `testcontainers-python` para MongoDB real
- Fixtures para setup/teardown de banco
- Marcador `@pytest.mark.integration` para execução seletiva

**Checklist:**

- [ ] Instalar `testcontainers[mongodb]`
- [ ] Criar fixtures para MongoDB container
- [ ] Implementar 3 testes E2E
- [ ] Todos os testes passam
- [ ] Documentar como rodar testes de integração
- [ ] Commit: `test: Adicionar testes E2E com MongoDB real`

---

### Tarefa 1.4: Decisão sobre `from_cache` (1h)

**Problema:** Field deprecated ainda presente no código

**Arquivo:** `app/dtos/responses/document_response_dto.py`

**Opções:**

#### Opção A: Remover Completamente (Breaking Change)

```python
# REMOVER campo:
from_cache: Optional[bool] = Field(...)

# Atualizar CHANGELOG.md:
## [2.0.0] - BREAKING CHANGES
- Removed deprecated field `from_cache` from DocumentResponseDTO
```

#### Opção B: Manter com Warning (Recomendado)

```python
from pydantic import field_validator
import warnings

from_cache: Optional[bool] = Field(
    default=False,
    description="DEPRECATED - Will be removed in v2.0. Always returns False."
)

@field_validator('from_cache')
def warn_deprecated(cls, v):
    warnings.warn(
        "Field 'from_cache' is deprecated and will be removed in v2.0",
        DeprecationWarning,
        stacklevel=2
    )
    return False  # Sempre retorna False
```

**Decisão:**

- [ ] Escolher Opção A ou B
- [ ] Implementar mudança
- [ ] Atualizar documentação da API
- [ ] Atualizar CHANGELOG.md
- [ ] Commit: `feat: Deprecar campo from_cache com warning` OU `feat!: Remover campo from_cache (BREAKING)`

---

## 🟡 FASE 2: Importante - Qualidade de Código (3.5h)

### Tarefa 2.1: Refatorar DuplicateCheckResult para @dataclass (1h)

**Objetivo:** Eliminar boilerplate e melhorar testabilidade

**Arquivo:** `app/services/core/duplicate_check_service.py`

**Antes:**

```python
class DuplicateCheckResult:
    """Resultado da verificação de duplicatas."""

    def __init__(
        self,
        is_duplicate: bool,
        should_process: bool,
        existing_response: Optional[DocumentResponseDTO] = None,
        file_size: int = 0,
        existing_document_id: Optional[str] = None,
        processed_at: Optional[datetime] = None
    ):
        self.is_duplicate = is_duplicate
        self.should_process = should_process
        self.existing_response = existing_response
        self.file_size = file_size
        self.existing_document_id = existing_document_id
        self.processed_at = processed_at
```

**Depois:**

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class DuplicateCheckResult:
    """Resultado da verificação de duplicatas."""
    is_duplicate: bool
    should_process: bool
    file_size: int = 0
    existing_response: Optional[DocumentResponseDTO] = None
    existing_document_id: Optional[str] = None
    processed_at: Optional[datetime] = None
```

**Benefícios:**

- ✅ `__repr__` automático para debug
- ✅ `__eq__` automático para comparações em testes
- ✅ Type hints consistentes
- ✅ Menos código (12 linhas → 7 linhas)

**Checklist:**

- [ ] Converter classe para @dataclass
- [ ] Rodar testes unitários (garantir que tudo passa)
- [ ] Verificar que `__repr__` funciona em logs
- [ ] Commit: `refactor: Converter DuplicateCheckResult para dataclass`

---

### Tarefa 2.2: Extrair Método `_get_file_size()` (0.5h)

**Objetivo:** Encapsular lógica de file seek e reduzir comentários

**Arquivo:** `app/services/core/duplicate_check_service.py`

**Antes (linhas ~70-73):**

```python
# Obter tamanho do arquivo
# FastAPI's UploadFile.seek() only accepts one argument (position)
# We need to use the underlying file object for seek operations
file.file.seek(0, 2)  # Ir para o final (usando file.file, não await)
file_size = file.file.tell()  # Obter posição (tamanho)
file.file.seek(0)  # Voltar ao início (usando file.file, não await)
```

**Depois:**

```python
from io import SEEK_SET, SEEK_END

def _get_file_size(self, file: UploadFile) -> int:
    """
    Extract file size from UploadFile.

    Note: FastAPI's UploadFile.seek() is async and only accepts position.
    We use the underlying SpooledTemporaryFile (file.file) which has
    synchronous seek(offset, whence) method.

    Args:
        file: FastAPI UploadFile instance

    Returns:
        File size in bytes
    """
    file.file.seek(0, SEEK_END)  # Move to end
    size = file.file.tell()       # Get position (= size)
    file.file.seek(0, SEEK_SET)   # Reset to start
    return size

# Uso:
file_size = self._get_file_size(file)
```

**Benefícios:**

- ✅ Lógica encapsulada
- ✅ Reutilizável
- ✅ Testável isoladamente
- ✅ Sem magic numbers (usa SEEK_END/SEEK_SET)

**Checklist:**

- [ ] Criar método privado `_get_file_size()`
- [ ] Substituir código inline por chamada ao método
- [ ] Adicionar teste unitário do método (opcional)
- [ ] Commit: `refactor: Extrair método _get_file_size em DuplicateCheckService`

---

### Tarefa 2.3: Criar Fixtures Reutilizáveis em Testes (1h)

**Objetivo:** Eliminar duplicação em testes

**Arquivo:** `tests/unit/controllers/test_analyze_duplicate_check.py`

**Problema:** Mock repetido em 4 testes

**Solução:**

```python
import pytest
from unittest.mock import AsyncMock
from app.services.core.duplicate_check_service import DuplicateCheckResult
from app.dtos.responses.document_response_dto import DocumentResponseDTO

class TestAnalyzeDuplicateCheck:

    @pytest.fixture
    def mock_duplicate_result_completed(self, mock_existing_doc):
        """Fixture: DuplicateCheckResult para documento COMPLETED."""
        response_data = mock_existing_doc.response.copy()
        response_data.update({
            "status": "already_processed",
            "message": f"Documento já foi processado anteriormente em {mock_existing_doc.created_at.isoformat()}",
            "from_database": True
        })
        existing_response = DocumentResponseDTO(**response_data)

        return DuplicateCheckResult(
            is_duplicate=True,
            should_process=False,
            existing_response=existing_response,
            file_size=1100,
            existing_document_id=mock_existing_doc.id,
            processed_at=mock_existing_doc.created_at
        )

    @pytest.fixture
    def mock_duplicate_result_failed(self, mock_existing_doc):
        """Fixture: DuplicateCheckResult para documento FAILED."""
        return DuplicateCheckResult(
            is_duplicate=True,
            should_process=True,  # Permite reprocessamento
            existing_response=None,
            file_size=1100,
            existing_document_id=mock_existing_doc.id,
            processed_at=mock_existing_doc.created_at
        )

    @pytest.fixture
    def mock_di_container(self):
        """Fixture: Mock do DI Container."""
        from unittest.mock import patch, MagicMock
        with patch("app.core.di_container.container") as container:
            yield container
```

**Checklist:**

- [ ] Criar 3 fixtures reutilizáveis
- [ ] Refatorar 4 testes para usar fixtures
- [ ] Rodar testes (garantir que tudo passa)
- [ ] Commit: `test: Criar fixtures reutilizáveis para testes de duplicata`

---

### Tarefa 2.4: Documentar Breaking Changes (1h)

**Objetivo:** Comunicar mudanças para usuários da API

**Arquivos a Atualizar:**

#### 1. CHANGELOG.md

```markdown
## [Unreleased]

### 🔴 BREAKING CHANGES

- Migration deleta documentos antigos sem `file_size` (criar backup antes!)
- [SE OPÇÃO A] Campo `from_cache` removido de DocumentResponseDTO

### ✨ Features

- Adicionado DuplicateCheckService com verificação via MongoDB
- Índice composto `idx_duplicate_check` para performance O(1)
- Campo `file_size` adicionado ao modelo de persistência

### 🐛 Fixes

- [APÓS TAREFA 1.1] Migration agora preserva documentos antigos com file_size=0

### 🧪 Tests

- Adicionados 4 testes unitários para verificação de duplicatas
- Adicionados 5 testes de borda (falhas, erros, concorrência)
- Adicionados 3 testes E2E com MongoDB real

### 📚 Documentation

- Documentação completa de breaking changes
- Guia de migração para v2.0
```

#### 2. docs/MIGRATION_GUIDE.md (NOVO)

````markdown
# 🚀 Guia de Migração - v2.0

## Breaking Changes

### 1. Migration Script

**IMPORTANTE:** Execute backup antes de rodar migration!

```bash
# 1. Backup manual
mongodump --db smartquest --out ./backup

# 2. Executar migration
node scripts/migrations/2025-12-06_001000_add_file_size_and_duplicate_index.js

# 3. Verificar
mongo smartquest --eval "db.analyze_documents.find({file_size: 0}).count()"
```
````

### 2. API Response Changes

[SE OPÇÃO A]
Campo `from_cache` removido. Atualizar clientes:

```json
// ANTES:
{
  "document_id": "123",
  "from_cache": false  // ❌ Removido
}

// DEPOIS:
{
  "document_id": "123"
  // Campo não existe mais
}
```

````

**Checklist:**
- [ ] Atualizar CHANGELOG.md
- [ ] Criar MIGRATION_GUIDE.md
- [ ] Atualizar README.md (se necessário)
- [ ] Commit: `docs: Documentar breaking changes e guia de migração`

---

## 🟢 FASE 3: Desejável - Refinamentos (1h)

### Tarefa 3.1: Usar Constantes SEEK_SET/SEEK_END (0.5h)

**Objetivo:** Substituir magic numbers por constantes

**Arquivo:** `app/services/core/duplicate_check_service.py`

**Já implementado na Tarefa 2.2!** ✅

---

### Tarefa 3.2: Padronizar Formatação com Black (0.5h)

**Objetivo:** Consistência de estilo de código

**Comandos:**
```powershell
# Instalar Black (se não instalado)
pip install black isort

# Formatar código
black app/ tests/

# Ordenar imports
isort app/ tests/

# Verificar diferenças
git diff

# Commit se satisfeito
git add .
git commit -m "style: Formatar código com Black e isort"
````

**Configurar Pre-commit (Opcional):**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

**Checklist:**

- [ ] Instalar black e isort
- [ ] Executar formatação
- [ ] Revisar mudanças
- [ ] (Opcional) Configurar pre-commit
- [ ] Commit: `style: Aplicar Black e isort em toda codebase`

---

## 📅 Cronograma de Execução

### Sprint 1 (Dias 1-2): Crítico

**Tempo:** 11h

| Dia         | Tarefas                                 | Duração |
| ----------- | --------------------------------------- | ------- |
| Dia 1 Manhã | 1.1 Corrigir Migration                  | 2h      |
| Dia 1 Tarde | 1.2 Testes de Borda                     | 5h      |
| Dia 2 Manhã | 1.3 Testes E2E                          | 3h      |
| Dia 2 Tarde | 1.3 Testes E2E (cont.) + 1.4 from_cache | 2h      |

**Checkpoint:** Código production-ready com 80%+ cobertura

---

### Sprint 2 (Dia 3): Importante

**Tempo:** 3.5h

| Período | Tarefas                                | Duração |
| ------- | -------------------------------------- | ------- |
| Manhã   | 2.1 @dataclass + 2.2 \_get_file_size() | 1.5h    |
| Tarde   | 2.3 Fixtures + 2.4 Documentação        | 2h      |

**Checkpoint:** Código refatorado e documentado

---

### Sprint 3 (Dia 4): Desejável

**Tempo:** 0.5h (Tarefa 3.1 já feita em 2.2)

| Período | Tarefas         | Duração |
| ------- | --------------- | ------- |
| Manhã   | 3.2 Black/isort | 0.5h    |

**Checkpoint:** Código formatado e pronto para merge

---

## ✅ Critérios de Aceitação

### Antes do Merge para Main:

- [ ] Todos os 220 testes unitários passam
- [ ] 5 novos testes de borda passam
- [ ] 3 novos testes E2E passam
- [ ] Cobertura de código > 80%
- [ ] Migration testada em banco local
- [ ] Migration NÃO deleta documentos antigos
- [ ] Documentação atualizada (CHANGELOG, MIGRATION_GUIDE)
- [ ] Breaking changes comunicados
- [ ] Code review aprovado
- [ ] Zero erros de linting/formatação

---

## 🚨 Plano de Rollback

### Se Algo Der Errado:

#### Durante Development:

```powershell
# Reverter última alteração
git reset --hard HEAD~1

# Voltar para commit específico
git reset --hard <commit-hash>

# Criar branch de backup
git checkout -b backup-feature-remove-cache
```

#### Após Deploy (Produção):

```bash
# 1. Restaurar backup MongoDB
mongorestore --db smartquest ./backup/<timestamp>

# 2. Reverter deploy (código anterior)
git revert <commit-hash>
git push origin main

# 3. Verificar saúde da aplicação
curl http://api/health
```

---

## 📊 Métricas de Sucesso

### Antes da Refatoração:

- Cobertura: ~65%
- Testes: 220 (4 de duplicata)
- Complexidade Controller: ~20
- Linhas Controller: 200

### Depois da Refatoração (Alvo):

- Cobertura: **>80%** ✅
- Testes: **232** (4 duplicata + 5 borda + 3 E2E) ✅
- Complexidade Controller: **~5** ✅
- Linhas Controller: **80** ✅
- Migration Segura: **Preserva dados antigos** ✅

---

## 🎯 Próximos Passos (Pós-Refatoração)

1. **Code Review:** Solicitar revisão de 2+ desenvolvedores
2. **QA Testing:** Testar em ambiente de staging
3. **Performance Testing:** Validar query O(1) em produção
4. **Deploy Gradual:** Canary deployment (10% → 50% → 100%)
5. **Monitoramento:** Observar métricas por 48h
6. **Retrospectiva:** Documentar lições aprendidas

---

## 📞 Contato e Suporte

**Responsável:** Equipe de Desenvolvimento  
**Revisor Técnico:** Claude Sonnet 4.5 Agent  
**Documento Base:** SONNET_CODE_REVIEW.md

**Em caso de dúvidas:**

- Consultar SONNET_CODE_REVIEW.md (análise técnica completa)
- Consultar REVIEW_REPORT.md (análise do Code-Review-Bot)
- Abrir issue no repositório com tag `refactoring`

---

**Última Atualização:** 2025-12-06  
**Versão do Plano:** 1.0  
**Status:** 🟡 Pronto para Execução
