# SmartQuest API Documentation

## Visão Geral da API

A SmartQuest API é um microserviço especializado na análise e classificação de avaliações educacionais. Utiliza **Dependency Injection**, cache transparente e persistência obrigatória no MongoDB.

### Arquitetura dos Endpoints

```
┌─────────────────────────────────────────────────┐
│                FastAPI Application              │
│                                                 │
│  📍 /health/          - Sistema de Saúde       │
│  📄 /analyze/         - Análise de Documentos   │
│  📖 /docs            - Documentação Swagger     │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│            Dependency Injection Container       │
│                                                 │
│  🔧 Resolve automaticamente todas as           │
│     dependências dos serviços                  │
│  🔄 Cache transparente para extração           │
│  💾 Persistência obrigatória no MongoDB        │
└─────────────────────────────────────────────────┘
```

---

## 1. Health Check Endpoint

### GET /health/

**Descrição:** Health check completo que executa verificações paralelas em todas as dependências do sistema.

#### Fluxo de Execução

```
1. Inicialização do HealthChecker
2. Verificações Paralelas:
   ├── MongoDB (CRÍTICO)
   ├── Azure Blob Storage (CRÍTICO)
   └── Azure Document Intelligence (NÃO CRÍTICO)
3. Cálculo do Status Geral
4. Resposta HTTP (200/503)
```

#### Dependências Verificadas

- ✅ **MongoDB** (CRÍTICO) - Persistência obrigatória
- ✅ **Azure Blob Storage** (CRÍTICO) - Armazenamento de imagens obrigatório
- ⚠️ **Azure Document Intelligence** (NÃO CRÍTICO) - Pode usar mock

#### Status Possíveis

- `healthy` - Todas as dependências funcionando
- `degraded` - Sistema funcionando mas com avisos (ex: Azure AI usando mock)
- `unhealthy` - Dependências críticas falharam (MongoDB ou Blob Storage indisponíveis)

#### Resposta de Sucesso (200 OK)

```json
{
  "status": "healthy",
  "message": "All systems operational",
  "timestamp": "2025-10-29T21:00:00.000000",
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
        "collections": ["azure_processing_data", "analyze_documents", "migrations"]
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
    "analyze": "/analyze/analyze_document - Document analysis endpoint",
    "retrieve": "/analyze/analyze_document/{id} - Document retrieval endpoint"
  }
}
```

#### Resposta de Falha (503 Service Unavailable)

```json
{
  "status": "unhealthy",
  "message": "Critical dependencies unavailable: MongoDB, Azure Blob Storage",
  "timestamp": "2025-10-29T21:00:00.000000",
  "service": {
    "name": "SmartQuest API",
    "version": "2.0.0",
    "description": "Microservice for analyzing and classifying educational assessments"
  },
  "environment": "local",
  "dependencies": {
    "mongodb": {
      "status": "unhealthy",
      "message": "MongoDB connection failed",
      "details": {"error": "Connection timeout"}
    }
  }
}
```

---

## 2. Document Analysis Endpoints

### POST /analyze/analyze_document

**Descrição:** Endpoint principal para análise completa de documentos PDF educacionais com persistência obrigatória.

#### Fluxo de Execução Detalhado

```
1. Validação de Entrada
   ├── Validação do email
   ├── Validação do arquivo PDF
   └── Verificação de formato/tamanho

2. Extração de Dados (com Cache)
   ├── Verifica cache existente
   ├── DocumentExtractionService
   └── Cache transparente dos resultados

3. Orquestração da Análise
   ├── AnalyzeService (via DI Container)
   ├── ImageCategorizationService
   ├── ImageExtractionOrchestrator
   ├── RefactoredContextBlockBuilder
   └── AzureFigureProcessor

4. Conversão para DTO
   ├── DocumentResponseDTO.from_internal_response()
   └── Compatibilidade da API

5. Persistência Obrigatória
   ├── AnalyzeDocumentRecord.create_from_request()
   ├── Salvar no MongoDB
   └── Gerar document_id único

6. Resposta Final
   └── DocumentResponseDTO completo
```

#### Parâmetros de Entrada

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `email` | Query String | ✅ | Email do usuário para análise |
| `file` | Form Data (File) | ✅ | Arquivo PDF para análise |

#### Dependências Críticas

- **MongoDB**: Persistência obrigatória (falha = erro 500)
- **Azure Blob Storage**: Armazenamento de imagens (crítico)
- **DI Container**: Resolução de toda árvore de dependências
- **Cache**: Otimização transparente da extração

#### Exemplo de Resposta (200 OK)

```json
{
  "document_id": "doc_20241029_abc123",
  "email": "usuario@escola.edu.br",
  "filename": "prova_matematica_9ano.pdf",
  "header": {
    "school": "UMEF Escola Municipal",
    "teacher": "Prof. Maria Silva",
    "subject": "Matemática",
    "student": "João Santos",
    "series": "9º Ano"
  },
  "questions": [
    {
      "number": 1,
      "question": "Calcule o valor de x na equação: 2x + 5 = 15",
      "alternatives": [
        {"letter": "A", "text": "x = 3"},
        {"letter": "B", "text": "x = 5"},
        {"letter": "C", "text": "x = 7"},
        {"letter": "D", "text": "x = 10"}
      ],
      "hasImage": false,
      "context_id": 1
    }
  ],
  "context_blocks": [
    {
      "id": 1,
      "type": ["text"],
      "title": "Equações do Primeiro Grau",
      "statement": "Resolva as equações apresentadas a seguir...",
      "hasImage": false,
      "images": [],
      "paragraphs": [
        "As equações do primeiro grau são fundamentais na álgebra.",
        "Para resolver uma equação, isolamos a incógnita."
      ]
    }
  ],
  "document_metadata": {
    "header_images": [],
    "processing_time": "2.45s",
    "cache_hit": true
  }
}
```

### GET /analyze/analyze_document/{id}

**Descrição:** Recupera informações sobre um documento que já foi processado e armazenado no MongoDB.

#### Fluxo de Execução

```
1. Validação do ID
   ├── Verificação de formato
   └── ID não vazio

2. Resolução do Serviço
   ├── ISimplePersistenceService (via DI)
   └── MongoDB connection

3. Busca no MongoDB
   ├── Query por document_id
   └── Coleção: analyze_documents

4. Conversão para DTO
   ├── AnalyzeDocumentResponseDTO.from_analyze_document_record()
   └── Formatação da resposta

5. Resposta
   ├── 200: Documento encontrado
   ├── 404: Documento não encontrado
   └── 500: Erro interno
```

#### Parâmetros de Entrada

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `id` | Path Parameter | ✅ | ID único do documento no MongoDB |

#### Respostas da API

**Sucesso (200 OK):**
```json
{
  "_id": "49ad106b-787b-4c9a-80ac-4c81388355ca",
  "document_name": "prova_matematica_9ano.pdf",
  "status": "completed",
  "analysis_results": {
    "document_id": "doc_20241029_abc123",
    "email": "usuario@escola.edu.br",
    "filename": "prova_matematica_9ano.pdf",
    "header": {
      "school": "UMEF Escola Municipal",
      "teacher": "Prof. Maria Silva",
      "subject": "Matemática",
      "student": "João Santos",
      "series": "9º Ano"
    },
    "questions": [
      {
        "number": 1,
        "question": "Calcule o valor de x na equação: 2x + 5 = 15",
        "alternatives": [
          {"letter": "A", "text": "x = 3"},
          {"letter": "B", "text": "x = 5"},
          {"letter": "C", "text": "x = 7"},
          {"letter": "D", "text": "x = 10"}
        ],
        "hasImage": false,
        "context_id": 1
      }
    ],
    "context_blocks": [
      {
        "id": 1,
        "type": ["text"],
        "title": "Equações do Primeiro Grau",
        "statement": "Resolva as equações apresentadas a seguir...",
        "hasImage": false,
        "images": [],
        "paragraphs": [
          "As equações do primeiro grau são fundamentais na álgebra.",
          "Para resolver uma equação, isolamos a incógnita."
        ]
      }
    ],
    "document_metadata": {
      "header_images": [],
      "processing_time": "2.45s",
      "cache_hit": true
    }
  },
  "created_at": "2024-10-29T10:30:00Z",
  "user_email": "usuario@escola.edu.br"
}
```

**Documento Não Encontrado (404):**
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
  "detail": "Erro interno ao buscar documento: [detalhes do erro]"
}
```

---

## 3. Códigos de Status HTTP

| Código | Endpoint | Significado |
|--------|----------|-------------|
| **200** | `/health/` | Sistema saudável ou degradado |
| **200** | `/analyze/analyze_document` | Análise concluída com sucesso |
| **200** | `/analyze/analyze_document/{id}` | Documento encontrado |
| **400** | `/analyze/analyze_document/{id}` | ID inválido ou malformado |
| **404** | `/analyze/analyze_document/{id}` | Documento não encontrado |
| **422** | `/analyze/analyze_document` | Dados de entrada inválidos |
| **500** | Todos | Erro interno do servidor |
| **503** | `/health/` | Dependências críticas indisponíveis |

## 4. Tratamento de Erros

### Estrutura Padrão de Erro

```json
{
  "detail": "Mensagem descritiva do erro",
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2025-10-29T21:00:00.000000"
}
```

### Tipos de Erro Comuns

- **Validação**: Email inválido, arquivo não PDF, tamanho excedido
- **Persistência**: MongoDB indisponível, falha na gravação
- **Processamento**: Arquivo corrompido, falha na extração
- **Dependências**: Azure services indisponíveis

---

## 5. Evolução da API

### Versão Atual (v2.0.0)

✅ **Endpoints Consolidados**: 3 endpoints principais  
✅ **Dependency Injection**: Container IoC completo  
✅ **Persistência Obrigatória**: MongoDB para todos os documentos  
✅ **Cache Transparente**: Otimização automática  
✅ **Health Check Robusto**: Verificação de todas as dependências  

### Mudanças da v1.x para v2.0.0

**ANTES (v1.x):**
- Root endpoint redundante (`/`)
- Health check básico
- Múltiplos endpoints de análise (mock, with_figures)
- Duplicação no router

**DEPOIS (v2.0.0):**
- Endpoints consolidados e focados
- Health check completo com dependências
- Análise unificada com cache e persistência
- Router limpo e bem estruturado

### Benefícios da Consolidação

✅ **Redução de Complexidade**: Menos endpoints para manter  
✅ **Padronização REST**: Estrutura consistente  
✅ **Monitoramento Melhorado**: Health check abrangente  
✅ **Performance**: Cache transparente  
✅ **Confiabilidade**: Persistência obrigatória  
