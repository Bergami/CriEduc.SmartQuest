# Testes de Integração E2E - Duplicate Flow

## 📋 Descrição

Testes end-to-end do fluxo completo de verificação de duplicatas, incluindo:

- ✅ Upload de documento novo → processamento completo
- ✅ Upload de duplicata exata → retorna documento existente
- ✅ Upload com tamanho diferente → reprocessa
- ✅ Retry de documentos com status FAILED
- ✅ Verificação de uso do índice MongoDB
- ✅ Testes de concorrência (múltiplas requisições simultâneas)
- ✅ Caracteres especiais em filenames
- ⏱️ Testes de performance com 1000+ documentos

## 🔧 Pré-requisitos

### MongoDB Local

Os testes E2E requerem MongoDB rodando localmente:

```powershell
# Opção 1: Docker (recomendado)
docker run -d -p 27017:27017 --name mongodb-test mongo:latest

# Opção 2: MongoDB instalado localmente
# Garantir que está rodando na porta padrão 27017
```

### Dependências Python

```powershell
pip install motor pytest-asyncio
```

## 🚀 Rodando os Testes

### Todos os Testes E2E

```powershell
# No ambiente virtual
python -m pytest tests/integration/test_duplicate_flow_e2e.py -v
```

### Apenas Testes Rápidos (sem performance)

```powershell
python -m pytest tests/integration/test_duplicate_flow_e2e.py -v -m "not slow"
```

### Teste Específico

```powershell
# Teste de fluxo completo
python -m pytest tests/integration/test_duplicate_flow_e2e.py::TestDuplicateFlowE2E::test_upload_duplicate_full_flow -v

# Teste de índice MongoDB
python -m pytest tests/integration/test_duplicate_flow_e2e.py::TestDuplicateFlowE2E::test_mongodb_index_usage -v

# Teste de concorrência
python -m pytest tests/integration/test_duplicate_flow_e2e.py::TestDuplicateFlowE2E::test_concurrent_duplicate_checks -v
```

### Testes de Performance

```powershell
python -m pytest tests/integration/test_duplicate_flow_e2e.py::TestDuplicatePerformance -v -s
```

## 📊 Cobertura de Cenários

### TestDuplicateFlowE2E

| Teste                                  | Cenário                           | Tempo Esperado |
| -------------------------------------- | --------------------------------- | -------------- |
| `test_upload_duplicate_full_flow`      | Fluxo completo upload → duplicata | ~500ms         |
| `test_different_file_size_reprocesses` | Tamanho diferente = reprocessa    | ~300ms         |
| `test_failed_document_allows_retry`    | Status FAILED permite retry       | ~100ms         |
| `test_mongodb_index_usage`             | Verifica uso de índice IXSCAN     | ~50ms          |
| `test_concurrent_duplicate_checks`     | 10 verificações paralelas         | ~200ms         |
| `test_special_characters_in_filename`  | Unicode, acentos, etc.            | ~100ms         |

### TestDuplicatePerformance

| Teste                                                  | Cenário                  | Tempo Esperado                 |
| ------------------------------------------------------ | ------------------------ | ------------------------------ |
| `test_duplicate_check_performance_with_many_documents` | 1000 docs, query < 100ms | ~2s (insert) + < 100ms (query) |

## 🔍 Verificando Índices MongoDB

### Via MongoDB Shell

```javascript
// Conectar ao database de teste
use smartquest_test_e2e

// Listar índices
db.analyze_documents.getIndexes()

// Deve mostrar:
// [
//   { v: 2, key: { _id: 1 }, name: "_id_" },
//   { v: 2, key: { user_email: 1, file_name: 1, file_size: 1 }, name: "idx_duplicate_check" }
// ]

// Verificar uso do índice em query
db.analyze_documents.find({
  user_email: "test@example.com",
  file_name: "test.pdf",
  file_size: 1024
}).explain("executionStats")

// Deve mostrar "IXSCAN" (index scan) ao invés de "COLLSCAN" (collection scan)
```

### Via Pytest com Output Verboso

```powershell
python -m pytest tests/integration/test_duplicate_flow_e2e.py::TestDuplicateFlowE2E::test_mongodb_index_usage -v -s
```

## 🧪 Estrutura dos Testes

### Fixtures Principais

- `client`: TestClient FastAPI
- `mongodb_database`: Database MongoDB de teste (cleanup automático)
- `sample_pdf_bytes`: Bytes de PDF válido (1024 bytes)
- `mock_analyze_service_response`: Mock da resposta do AnalyzeService

### Fluxo de Setup/Teardown

```python
@pytest.fixture
async def mongodb_database():
    # Setup: Conectar, limpar collection, criar índice
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["smartquest_test_e2e"]
    await db.analyze_documents.delete_many({})
    await db.analyze_documents.create_index(...)

    yield db  # Testes rodam aqui

    # Teardown: Limpar collection, fechar conexão
    await db.analyze_documents.delete_many({})
    client.close()
```

## ⚠️ Troubleshooting

### Erro: "Connection refused" ou "Cannot connect to MongoDB"

```powershell
# Verificar se MongoDB está rodando
docker ps | Select-String mongodb

# Se não estiver rodando, iniciar:
docker start mongodb-test

# Ou criar novo container:
docker run -d -p 27017:27017 --name mongodb-test mongo:latest
```

### Erro: "Collection not found" ou "Index not created"

Os testes fazem cleanup e recreiam o índice automaticamente. Se persistir:

```javascript
// Via MongoDB shell
use smartquest_test_e2e
db.analyze_documents.drop()

// Recriar collection e índice
db.analyze_documents.createIndex({
  user_email: 1,
  file_name: 1,
  file_size: 1
}, { name: "idx_duplicate_check" })
```

### Testes Lentos

```powershell
# Rodar sem testes de performance
python -m pytest tests/integration/test_duplicate_flow_e2e.py -v -m "not slow"

# Ou aumentar timeout
python -m pytest tests/integration/test_duplicate_flow_e2e.py -v --timeout=60
```

## 🐳 CI/CD com Docker Compose

Para rodar em CI/CD, criar `docker-compose.test.yml`:

```yaml
version: "3.8"
services:
  mongodb-test:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: smartquest_test_e2e
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 5s
      retries: 5

  pytest:
    build: .
    depends_on:
      mongodb-test:
        condition: service_healthy
    environment:
      MONGODB_URI: mongodb://mongodb-test:27017
    command: python -m pytest tests/integration/test_duplicate_flow_e2e.py -v
```

```powershell
# Rodar testes em CI/CD
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Métricas de Sucesso

### Performance

- ✅ Query de duplicata com índice: **< 100ms** (mesmo com 1000+ docs)
- ✅ Fluxo completo upload: **< 1s**
- ✅ Verificações concorrentes: **< 500ms** (10 paralelas)

### Cobertura

- ✅ **7 testes E2E** cobrindo todos os fluxos críticos
- ✅ **1 teste de performance** validando escalabilidade
- ✅ **100% dos cenários** de duplicata testados

### Confiabilidade

- ✅ Testes isolados (cleanup entre execuções)
- ✅ Database de teste separado
- ✅ Idempotência garantida

## 📝 Próximos Passos

1. ⏳ Adicionar testcontainers-python para MongoDB (evitar depender de MongoDB local)
2. ⏳ Testes de carga (100+ requisições simultâneas)
3. ⏳ Testes de migração (validar índice após migration)
4. ⏳ Métricas de tempo de resposta (percentis p50, p95, p99)

## 🔗 Links Úteis

- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Indexes](https://www.mongodb.com/docs/manual/indexes/)
- [Pytest Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testcontainers Python](https://testcontainers-python.readthedocs.io/)
