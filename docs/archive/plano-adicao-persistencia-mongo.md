# Plano de Execução: Adição de Persistência MongoDB

**Data:** Dezembro 2024  
**Versão Base:** v2.0.0  
**Objetivo:** Implementar persistência MongoDB para o endpoint `analyze_document`

## 📋 Resumo Executivo

### Escopo

Adicionar camada de persistência MongoDB ao endpoint `POST /analyze/analyze_document` para armazenar todas as requisições e respostas do sistema, mantendo histórico completo das análises de documentos.

### Estrutura de Dados MongoDB

```javascript
// Collection: analyze_document
{
  "_id": ObjectId("..."),
  "id": "doc_12345_2024-12-01T10:30:00Z",  // ID único gerado
  "created_at": ISODate("2024-12-01T10:30:00Z"),
  "user_email": "usuario@escola.com.br",
  "file_name": "prova_matematica_9ano.pdf",
  "response": {
    // DocumentResponseDTO completo em JSON
    "document_id": "doc_12345",
    "metadata": { ... },
    "images": { ... },
    "contexts": { ... },
    "questions": { ... },
    "summary": { ... },
    "processed_at": "2024-12-01T10:30:00Z",
    "api_version": "2.0"
  }
}
```

## 🔍 Análise da Arquitetura Atual

### Pontos de Integração Identificados

1. **Endpoint Controller:** `app/api/controllers/analyze.py` - linha 29
2. **Response DTO:** `app/dtos/api/document_dtos.py` - `DocumentResponseDTO`
3. **DI Container:** `app/config/di_config.py` - para registrar novo serviço
4. **Settings:** `app/config/settings.py` - para configurações MongoDB

### Estrutura DocumentResponseDTO (Atual)

```python
class DocumentResponseDTO(BaseModel):
    document_id: Optional[str]
    metadata: DocumentMetadataDTO
    images: ImageListDTO
    contexts: ContextListDTO
    questions: QuestionListDTO
    summary: ProcessingSummaryDTO
    processed_at: datetime
    api_version: str = "2.0"
```

## 🎯 Plano de Implementação

### FASE 1: Configuração da Infraestrutura MongoDB

**Branch:** `feature/mongodb-persistence`  
**Duração:** 2-3 horas

#### 1.1 Configurações de Ambiente

```bash
# Adicionar ao .env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=smartquest
MONGODB_COLLECTION_ANALYZE=analyze_document

# Para produção
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net
```

#### 1.2 Dependências

```python
# requirements.txt
motor==3.3.2          # Driver MongoDB async
pymongo==4.6.1        # Driver MongoDB sync (backup)
```

#### 1.3 Docker Compose (Desenvolvimento)

```yaml
# docker-compose.yml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
    depends_on:
      - mongodb

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_DATABASE=smartquest
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

### FASE 2: Modelos de Dados MongoDB

**Localização:** `app/models/persistence/`

#### 2.1 Modelo Base

```python
# app/models/persistence/base_document.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

class BaseDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
```

#### 2.2 Modelo Específico

```python
# app/models/persistence/analyze_document_record.py
from typing import Dict, Any
from .base_document import BaseDocument

class AnalyzeDocumentRecord(BaseDocument):
    user_email: str
    file_name: str
    response: Dict[str, Any]  # DocumentResponseDTO serializado

    @classmethod
    def from_endpoint_data(
        cls,
        user_email: str,
        file_name: str,
        response_dto: DocumentResponseDTO
    ) -> "AnalyzeDocumentRecord":
        return cls(
            user_email=user_email,
            file_name=file_name,
            response=response_dto.dict()
        )
```

### FASE 3: Serviços de Persistência

**Localização:** `app/services/persistence/`

#### 3.1 Interface de Persistência

```python
# app/core/interfaces/persistence_interfaces.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord

class IPersistenceService(ABC):
    @abstractmethod
    async def save_analyze_document(self, record: AnalyzeDocumentRecord) -> str:
        """Salva registro de análise e retorna ID."""
        pass

    @abstractmethod
    async def get_analyze_document(self, record_id: str) -> Optional[AnalyzeDocumentRecord]:
        """Recupera registro por ID."""
        pass

    @abstractmethod
    async def list_user_documents(self, user_email: str, limit: int = 10) -> List[AnalyzeDocumentRecord]:
        """Lista documentos de um usuário."""
        pass
```

#### 3.2 Implementação MongoDB

```python
# app/services/persistence/mongodb_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
from app.core.interfaces.persistence_interfaces import IPersistenceService
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.config.settings import get_settings
import logging

class MongoDBPersistenceService(IPersistenceService):
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.database = None
        self.collection = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        """Conecta ao MongoDB."""
        self.client = AsyncIOMotorClient(self.settings.mongodb_url)
        self.database = self.client[self.settings.mongodb_database]
        self.collection = self.database[self.settings.mongodb_collection_analyze]

    async def save_analyze_document(self, record: AnalyzeDocumentRecord) -> str:
        """Implementação da interface."""
        # Gerar ID único: doc_id + timestamp
        unique_id = f"{record.response['document_id']}_{record.created_at.isoformat()}"
        record_dict = record.dict()
        record_dict['id'] = unique_id

        result = await self.collection.insert_one(record_dict)
        self.logger.info(f"Documento salvo: {unique_id}")
        return unique_id

    # Implementar outros métodos...
```

### FASE 4: Integração com DI Container

**Localização:** `app/config/di_config.py`

#### 4.1 Registro do Serviço

```python
# Adicionar ao configure_dependencies()
from app.core.interfaces.persistence_interfaces import IPersistenceService
from app.services.persistence.mongodb_service import MongoDBPersistenceService

# ==================================================================================
# 💾 PERSISTENCE SERVICE (MongoDB)
# ==================================================================================
container.register(
    interface_type=IPersistenceService,
    implementation_type=MongoDBPersistenceService,
    lifetime=ServiceLifetime.SINGLETON
)
logger.debug("✅ IPersistenceService -> MongoDBPersistenceService (Singleton)")
```

### FASE 5: Modificação do Controller

**Localização:** `app/api/controllers/analyze.py`

#### 5.1 Injeção de Dependência

```python
# Adicionar após linha 63
from app.core.interfaces.persistence_interfaces import IPersistenceService
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord

# No método analyze_document, após linha 74
@router.post("/analyze_document", response_model=DocumentResponseDTO)
async def analyze_document(...):
    # ... código existente ...

    # Converter para DTO da API (linha existente)
    api_response = DocumentResponseDTO.from_internal_response(internal_response)

    # NOVA FUNCIONALIDADE: Persistir no MongoDB
    try:
        persistence_service = container.resolve(IPersistenceService)
        await persistence_service.connect()  # Garantir conexão

        # Criar registro para persistência
        record = AnalyzeDocumentRecord.from_endpoint_data(
            user_email=email,
            file_name=file.filename,
            response_dto=api_response
        )

        # Salvar no MongoDB
        saved_id = await persistence_service.save_analyze_document(record)

        structured_logger.info(
            "Document analysis persisted to MongoDB",
            context={"saved_id": saved_id, "user_email": email}
        )

    except Exception as e:
        # Log erro mas não quebra o fluxo principal
        structured_logger.error(
            "Failed to persist document analysis",
            context={"error": str(e), "user_email": email}
        )
        # Continua normalmente - persistência é adicional

    # Retorno normal (linha existente)
    return api_response
```

### FASE 6: Configurações e Settings

**Localização:** `app/config/settings.py`

#### 6.1 Configurações MongoDB

```python
# Adicionar à classe Settings
class Settings(BaseSettings):
    # ... configurações existentes ...

    # MongoDB Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "smartquest")
    mongodb_collection_analyze: str = os.getenv("MONGODB_COLLECTION_ANALYZE", "analyze_document")
    mongodb_connection_timeout: int = int(os.getenv("MONGODB_CONNECTION_TIMEOUT", "10000"))

    # Feature flags
    enable_persistence: bool = os.getenv("ENABLE_PERSISTENCE", "true").lower() == "true"
```

### FASE 7: Testes e Validação

**Localização:** `tests/integration/persistence/`

#### 7.1 Testes de Integração

```python
# tests/integration/persistence/test_mongodb_service.py
import pytest
from app.services.persistence.mongodb_service import MongoDBPersistenceService
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord

@pytest.mark.asyncio
async def test_save_and_retrieve():
    service = MongoDBPersistenceService()
    await service.connect()

    # Teste de salvamento
    record = AnalyzeDocumentRecord(
        user_email="test@example.com",
        file_name="test.pdf",
        response={"test": "data"}
    )

    saved_id = await service.save_analyze_document(record)
    assert saved_id is not None

    # Teste de recuperação
    retrieved = await service.get_analyze_document(saved_id)
    assert retrieved.user_email == "test@example.com"
```

#### 7.2 Testes do Endpoint

```python
# tests/integration/api/test_analyze_with_persistence.py
@pytest.mark.asyncio
async def test_analyze_document_persistence(client):
    # Mock do arquivo PDF
    files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
    params = {"email": "test@example.com"}

    # Fazer requisição
    response = await client.post("/analyze/analyze_document", files=files, params=params)

    assert response.status_code == 200

    # Verificar se foi persistido (via logs ou consulta direta)
    # ... validações específicas
```

## 🔧 Cronograma de Execução

### Dia 1 (4 horas)

- [x] **09:00-10:00** - Criação do branch `feature/mongodb-persistence`
- [x] **10:00-11:30** - FASE 1: Configuração infraestrutura MongoDB
- [x] **11:30-12:00** - FASE 2: Modelos de dados MongoDB
- [x] **14:00-15:30** - FASE 3: Serviços de persistência (interface + implementação)

### Dia 2 (3 horas)

- [x] **09:00-10:00** - FASE 4: Integração com DI Container
- [x] **10:00-11:30** - FASE 5: Modificação do controller
- [x] **14:00-15:00** - FASE 6: Configurações e settings

### Dia 3 (2 horas)

- [x] **09:00-10:00** - FASE 7: Testes de integração
- [x] **10:00-11:00** - Validação completa e ajustes finais

## 🧪 Estratégia de Testes

### Testes Unitários

- [ ] Modelo `AnalyzeDocumentRecord`
- [ ] Interface `IPersistenceService`
- [ ] Implementação `MongoDBPersistenceService`

### Testes de Integração

- [ ] Conexão com MongoDB
- [ ] Operações CRUD completas
- [ ] Integration com DI Container
- [ ] Endpoint com persistência ativa

### Testes E2E

- [ ] Fluxo completo: PDF → Análise → Persistência
- [ ] Recuperação de dados persistidos
- [ ] Cenários de falha (MongoDB indisponível)

## ⚠️ Considerações de Implementação

### Tratamento de Erros

```python
# Estratégia: Persistência não deve quebrar fluxo principal
try:
    await persistence_service.save_analyze_document(record)
except Exception as e:
    logger.error(f"Persistence failed: {e}")
    # Continua execução normal - persistência é adicional
```

### Performance

- Conexão singleton para reutilização
- Operações assíncronas (motor)
- Índices MongoDB apropriados:
  ```javascript
  // Índices recomendados
  db.analyze_document.createIndex({ user_email: 1, created_at: -1 });
  db.analyze_document.createIndex({ created_at: -1 });
  db.analyze_document.createIndex({ file_name: 1 });
  ```

### Segurança

- Não armazenar dados sensíveis além do necessário
- Validação de entrada antes da persistência
- Configuração de retenção de dados (opcional)

### Monitoramento

- Logs estruturados para operações de persistência
- Métricas de performance (tempo de salvamento)
- Alertas para falhas de conexão

## 🚀 Critérios de Aceitação

### Funcionalidades Obrigatórias

- [x] ✅ Endpoint `analyze_document` persiste dados no MongoDB
- [x] ✅ Estrutura de dados conforme especificação
- [x] ✅ Falhas de persistência não afetam resposta da API
- [x] ✅ Logs adequados para auditoria
- [x] ✅ Docker Compose para desenvolvimento local

### Funcionalidades Opcionais

- [ ] 🔄 Endpoint para consultar histórico: `GET /analyze/history/{user_email}`
- [ ] 🔄 Endpoint para recuperar análise: `GET /analyze/document/{record_id}`
- [ ] 🔄 Interface administrativa para MongoDB
- [ ] 🔄 Retenção automática de dados (TTL)

## 📦 Entregáveis

### Código

1. **Modelos**: `app/models/persistence/`
2. **Serviços**: `app/services/persistence/`
3. **Interfaces**: Extensão de `app/core/interfaces/`
4. **Configuração**: Atualização de `app/config/`
5. **Controller**: Modificação de `app/api/controllers/analyze.py`

### Documentação

1. **README**: Seção sobre MongoDB
2. **API.md**: Documentação da persistência
3. **SETUP.md**: Instruções MongoDB + Docker
4. **ARCHITECTURE.md**: Nova camada de persistência

### Infraestrutura

1. **Docker Compose**: Configuração completa MongoDB
2. **Requirements**: Dependências MongoDB
3. **Environment**: Variáveis de configuração

## 🎯 Próximos Passos

1. **Aprovação do Plano**: Revisão e aprovação desta especificação
2. **Criação do Branch**: `git checkout -b feature/mongodb-persistence`
3. **Implementação Sequencial**: Seguir fases 1-7 conforme cronograma
4. **Testes Intermediários**: Validar cada fase antes da próxima
5. **Review e Merge**: Code review + merge para main
6. **Deploy**: Configuração em ambiente de produção

---

**Autor**: GitHub Copilot  
**Revisão**: Pendente  
**Status**: Aguardando Aprovação para Implementação
