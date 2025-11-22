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
│  📋 /analyze/documents - Listagem Paginada      │
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
    "analyze": "/analyze/analyze_document - Document analysis endpoint",
    "retrieve": "/analyze/analyze_document/{id} - Document retrieval endpoint",
    "list": "/analyze/documents - Paginated document list with filters"
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
      "details": { "error": "Connection timeout" }
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

| Parâmetro | Tipo             | Obrigatório | Descrição                     |
| --------- | ---------------- | ----------- | ----------------------------- |
| `email`   | Query String     | ✅          | Email do usuário para análise |
| `file`    | Form Data (File) | ✅          | Arquivo PDF para análise      |

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
        { "letter": "A", "text": "x = 3" },
        { "letter": "B", "text": "x = 5" },
        { "letter": "C", "text": "x = 7" },
        { "letter": "D", "text": "x = 10" }
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

| Parâmetro | Tipo           | Obrigatório | Descrição                        |
| --------- | -------------- | ----------- | -------------------------------- |
| `id`      | Path Parameter | ✅          | ID único do documento no MongoDB |

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
          { "letter": "A", "text": "x = 3" },
          { "letter": "B", "text": "x = 5" },
          { "letter": "C", "text": "x = 7" },
          { "letter": "D", "text": "x = 10" }
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

### GET /analyze/documents

**Descrição:** Lista documentos analisados com filtros e paginação, permitindo buscar documentos por email e período.

#### Fluxo de Execução

```
1. Validação de Entrada
   ├── Email obrigatório e não vazio
   ├── Validação de par de datas (ambas ou nenhuma)
   └── Validação de intervalo de datas (start <= end)

2. Conversão de Datas
   ├── Aceita formato simples YYYY-MM-DD
   ├── Converte start_date para datetime (00:00:00)
   └── Converte end_date para datetime (23:59:59.999999)

3. Resolução do Serviço
   ├── ISimplePersistenceService (via DI)
   └── MongoDB connection

4. Busca no MongoDB
   ├── Query por user_email
   ├── Filtro por intervalo de created_at (opcional)
   ├── Ordenação por created_at DESC
   └── Paginação com skip/limit

5. Contagem Total
   └── count_documents com os mesmos filtros

6. Conversão para DTOs
   ├── List[AnalyzeDocumentResponseDTO]
   └── PaginationMetadata

7. Resposta
   ├── 200: Lista retornada (pode ser vazia)
   ├── 400: Validação falhou
   └── 500: Erro interno
```

#### Parâmetros de Entrada

| Parâmetro    | Tipo         | Obrigatório | Padrão | Validação    | Descrição                                  |
| ------------ | ------------ | ----------- | ------ | ------------ | ------------------------------------------ |
| `email`      | Query String | ✅          | -      | Não vazio    | Email do usuário para filtrar documentos   |
| `start_date` | Query Date   | ❌          | None   | Formato date | Data início do filtro (YYYY-MM-DD)         |
| `end_date`   | Query Date   | ❌          | None   | Formato date | Data fim do filtro (YYYY-MM-DD)            |
| `page`       | Query Int    | ❌          | 1      | >= 1         | Número da página (1-indexed)               |
| `page_size`  | Query Int    | ❌          | 10     | >= 1 e <= 50 | Quantidade de itens por página (máximo 50) |

#### Regras de Validação

1. **Email obrigatório**: Deve ser fornecido e não pode estar vazio
2. **Par de datas**: Se informar `start_date`, deve informar `end_date` (e vice-versa)
3. **Intervalo válido**: `start_date` deve ser anterior ou igual a `end_date`
4. **Formato de data**: Aceita formato simples `YYYY-MM-DD` (ex: `2025-11-21`)
5. **Paginação**: `page` mínimo 1, `page_size` entre 1 e 50

#### Exemplo de Requisição

**Listar todos os documentos de um usuário:**

```http
GET /analyze/documents?email=usuario@escola.edu.br&page=1&page_size=10
```

**Listar documentos de um período específico:**

```http
GET /analyze/documents?email=usuario@escola.edu.br&start_date=2025-11-01&end_date=2025-11-30&page=1&page_size=20
```

**Segunda página de resultados:**

```http
GET /analyze/documents?email=usuario@escola.edu.br&page=2&page_size=10
```

#### Resposta de Sucesso (200 OK)

```json
{
  "items": [
    {
      "_id": "423a02fd-a0e0-4392-b66a-a43250e51ac3",
      "document_name": "Recuperacao.pdf",
      "status": "completed",
      "analysis_results": {
        "document_id": "de8648f0-b36e-4513-9ca4-b11ad6cc2f25",
        "email": "wander.bergami@gmail.com",
        "filename": "Recuperacao.pdf",
        "header": {
          "school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
          "teacher": "Danielle",
          "subject": "Língua Portuguesa",
          "student": null,
          "series": null
        },
        "questions": [
          {
            "number": 1,
            "question": "O texto de Marina Colasanti descreve...",
            "alternatives": [
              {
                "letter": "a",
                "text": "da velocidade com que a tecnologia..."
              },
              { "letter": "b", "text": "do desrespeito do ser humano..." }
            ],
            "hasImage": false,
            "context_id": 1
          }
        ],
        "context_blocks": [
          {
            "id": 1,
            "type": ["text"],
            "title": "Eu sei, mas não devia (Marina Colasanti)",
            "statement": "LEIA O TEXTO A SEGUIR",
            "hasImage": false,
            "images": [],
            "paragraphs": ["Eu sei que a gente se acostuma..."]
          }
        ]
      },
      "created_at": "2025-11-21T21:38:26.319Z",
      "user_email": "wander.bergami@gmail.com"
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 15,
    "total_pages": 2,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Resposta de Lista Vazia (200 OK)

Quando não há documentos correspondentes aos filtros:

```json
{
  "items": [],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 0,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

#### Erros de Validação (400 Bad Request)

**Email vazio:**

```json
{
  "detail": "Email é obrigatório e não pode estar vazio"
}
```

**Par de datas incompleto:**

```json
{
  "detail": "Se informar data de início, deve informar data de fim (e vice-versa)"
}
```

**Intervalo de datas inválido:**

```json
{
  "detail": "Data de início deve ser anterior ou igual à data de fim"
}
```

#### Erro de Formato de Data (422 Unprocessable Entity)

Quando o formato da data está incorreto:

```json
{
  "detail": [
    {
      "loc": ["query", "start_date"],
      "msg": "invalid date format",
      "type": "value_error.date"
    }
  ]
}
```

#### Estrutura do PaginationMetadata

```typescript
{
  "current_page": number,      // Página atual (1-indexed)
  "page_size": number,          // Itens por página
  "total_items": number,        // Total de itens encontrados
  "total_pages": number,        // Total de páginas (calculado automaticamente)
  "has_next": boolean,          // Existe próxima página?
  "has_previous": boolean       // Existe página anterior?
}
```

#### Casos de Uso

1. **Listar todos os documentos de um usuário**: Ideal para dashboards e histórico completo
2. **Filtrar por período**: Útil para relatórios mensais, trimestrais ou anuais
3. **Paginação**: Navegação eficiente em grandes volumes de documentos
4. **Busca específica por dia**: Usando mesma data em start_date e end_date

#### Observações Técnicas

- ✅ **Ordenação**: Sempre retorna documentos mais recentes primeiro (`created_at DESC`)
- ✅ **Conversão de datas**: Aceita formato simples `YYYY-MM-DD` e converte internamente para datetime
- ✅ **Inclusão de intervalo**: `start_date` às 00:00:00 e `end_date` às 23:59:59.999999
- ✅ **Performance**: Usa índices MongoDB em `user_email` e `created_at` para otimização
- ✅ **Paginação eficiente**: Consulta separada para contagem total antes da paginação
- ✅ **Limite de segurança**: Máximo de 50 itens por página para evitar sobrecarga

---

## 3. Códigos de Status HTTP

| Código  | Endpoint                         | Significado                             |
| ------- | -------------------------------- | --------------------------------------- |
| **200** | `/health/`                       | Sistema saudável ou degradado           |
| **200** | `/analyze/analyze_document`      | Análise concluída com sucesso           |
| **200** | `/analyze/analyze_document/{id}` | Documento encontrado                    |
| **200** | `/analyze/documents`             | Lista retornada (pode ser vazia)        |
| **400** | `/analyze/analyze_document/{id}` | ID inválido ou malformado               |
| **400** | `/analyze/documents`             | Validação de parâmetros falhou          |
| **404** | `/analyze/analyze_document/{id}` | Documento não encontrado                |
| **422** | `/analyze/analyze_document`      | Dados de entrada inválidos              |
| **422** | `/analyze/documents`             | Formato de data ou parâmetros inválidos |
| **500** | Todos                            | Erro interno do servidor                |
| **503** | `/health/`                       | Dependências críticas indisponíveis     |

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

✅ **Endpoints Consolidados**: 4 endpoints principais  
✅ **Dependency Injection**: Container IoC completo  
✅ **Persistência Obrigatória**: MongoDB para todos os documentos  
✅ **Cache Transparente**: Otimização automática  
✅ **Health Check Robusto**: Verificação de todas as dependências  
✅ **Listagem Paginada**: Busca eficiente com filtros e paginação

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
