# API Documentation

## Health Check Endpoint

### GET /health/

**Descrição:** Health check completo que verifica TODAS as dependências do sistema.

**Dependências Testadas:**

- ✅ **MongoDB** (CRÍTICO) - Persistência obrigatória
- ✅ **Azure Blob Storage** (CRÍTICO) - Armazenamento de imagens obrigatório
- ⚠️ **Azure Document Intelligence** (NÃO CRÍTICO) - Pode usar mock

**Status Possíveis:**

- `healthy` - Todas as dependências funcionando
- `degraded` - Sistema funcionando mas com avisos (ex: Azure AI usando mock)
- `unhealthy` - Dependências críticas falharam (MongoDB ou Blob Storage indisponíveis)

**Resposta de Sucesso (200 OK):**

```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-10-27T22:19:23.561090",
  "service": {
    "name": "SmartQuest API",
    "version": "2.0.0",
    "description": "Microservice for analyzing and classifying educational assessments"
  },
  "environment": "local",
  "dependencies": {
    "mongodb": {
      "status": "healthy",
      "message": "MongoDB connected and operational",
      "details": {
        "database": "smartquest",
        "collections_count": 3,
        "collections": [
          "azure_processing_data",
          "analyze_documents",
          "migrations"
        ]
      }
    },
    "azure_blob_storage": {
      "status": "healthy",
      "message": "Azure Blob Storage connected and operational",
      "details": {
        "service": "AzureImageUploadService",
        "azure_blob_enabled": true,
        "has_storage_url": true,
        "has_container_name": true,
        "has_sas_token": true
      }
    },
    "azure_document_intelligence": {
      "status": "healthy",
      "message": "Azure Document Intelligence configured",
      "details": {
        "enabled": true,
        "endpoint_configured": true,
        "key_configured": true
      }
    }
  },
  "endpoints": {
    "health": "/health/ - Complete health check with all dependencies",
    "analyze": "/analyze/analyze_document - Document analysis endpoint"
  }
}
```

**Resposta de Falha (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "message": "Critical dependencies unavailable: MongoDB, Azure Blob Storage",
  "...": "Same structure as success response"
}
```

## Document Analysis Endpoints

### POST /analyze/analyze_document

**Descrição:** Endpoint principal para análise de documentos PDF educacionais.

**Parâmetros:**

- `email` (query): Email do usuário
- `file` (form-data): Arquivo PDF para análise

**Resposta:** Objeto DocumentResponseDTO com questões extraídas e categorizadas.

### GET /analyze/analyze_document/{id}

**Descrição:** Recupera informações sobre um documento que já foi processado e armazenado.

**Parâmetros:**

- `id` (path): ID do documento no MongoDB (ObjectId ou UUID)

**Respostas:**

**Sucesso (200 OK):**
```json
{
  "_id": "49ad106b-787b-4c9a-80ac-4c81388355ca",
  "document_name": "example.pdf",
  "status": "completed",
  "analysis_results": {
    "document_id": "doc_12345",
    "email": "user@example.com",
    "filename": "example.pdf",
    "header": {
      "school": "UMEF Escola Exemplo",
      "teacher": "Professor Silva",
      "subject": "Matemática",
      "student": "João Santos",
      "series": "9º Ano"
    },
    "questions": [
      {
        "number": 1,
        "question": "Qual é o resultado de 2 + 2?",
        "alternatives": [
          {"letter": "A", "text": "3"},
          {"letter": "B", "text": "4"},
          {"letter": "C", "text": "5"}
        ],
        "hasImage": false,
        "context_id": 1
      }
    ],
    "context_blocks": [
      {
        "id": 1,
        "type": ["text"],
        "title": "Contexto Matemático",
        "hasImage": false,
        "images": [],
        "paragraphs": ["Texto do contexto..."]
      }
    ]
  },
  "created_at": "2024-10-28T10:30:00Z",
  "user_email": "user@example.com"
}
```

**Não Encontrado (404):**
```json
{
  "detail": "Documento não encontrado"
}
```

**ID Inválido (400):**
```json
{
  "detail": "ID do documento é obrigatório e não pode estar vazio"
}
```

**Erro Interno (500):**
```json
{
  "detail": "Erro interno ao buscar documento: [erro detalhado]"
}
```

---

## Mudanças Implementadas (FASE 1)

### ANTES:

- `/` (GET) - Root endpoint redundante
- `/health` (GET) - Health check específico
- Duplicação no router (health_router incluído 2x)

### DEPOIS:

- `/health/` (GET) - Endpoint consolidado único
- Informações mais estruturadas e completas
- Router limpo sem duplicações

### Benefícios:

✅ Redução de endpoints: 2 → 1 (-50%)  
✅ Padronização REST (health check em /health/)  
✅ Informações mais organizadas e completas  
✅ Eliminação de duplicação no router  
✅ Manutenibilidade melhorada
