# SmartQuest API v2.0.0

Sistema de análise inteligente de documentos PDF educacionais com arquitetura moderna e persistência robusta.

## 🎯 Características Principais

### **Arquitetura Moderna v2.0.0**

- ✅ **Dependency Injection Container** nativo com auto-wiring completo
- ✅ **SOLID Principles** aplicados rigorosamente em toda a base de código
- ✅ **Clean Architecture** com separação clara de responsabilidades
- ✅ **MongoDB Persistence** obrigatória com models Pydantic e migrações versionadas
- ✅ **Type Safety** com Pydantic models em toda aplicação
- ✅ **Cache Transparente** para otimização de performance
- ✅ **Health Check Robusto** com monitoramento de todas as dependências

## 🏗️ Arquitetura do Sistema v2.0.0

```mermaid
graph TB
    subgraph "🌐 API Layer"
        A[Health Controller /health/]
        B[Analyze Controller /analyze/]
    end

    subgraph "🧠 Business Layer"
        C[AnalyzeService via DI]
        D[DocumentExtractionService]
        E[DocumentAnalysisOrchestrator]
    end

    subgraph "🔧 DI Container"
        F[Automatic Dependency Resolution]
        G[Service Lifecycle Management]
    end

    subgraph "💾 Persistence Layer"
        H[SimplePersistenceService]
        I[MongoDB Connection Service]
        J[(MongoDB smartquest)]
    end

    subgraph "☁️ Azure Services"
        K[Azure Document Intelligence]
        L[Azure Blob Storage]
        M[Cache System]
    end

    A --> I
    B --> C
    C --> D
    C --> E
    C --> H
    D --> M
    D --> K
    E --> L
    H --> I
    I --> J
    F --> C
    F --> H
    F --> I

    style J fill:#4CAF50
    style K fill:#0078D4
    style L fill:#0078D4
    style F fill:#FF9800
```

    style E fill:#FF9800

````

### **🔄 Fluxo de Persistência**

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant AnalyzeService
    participant PersistenceService
    participant MongoDB
    participant Azure

    Client->>API: POST /analyze_document
    API->>AnalyzeService: process_document()
    AnalyzeService->>Azure: extract_content()
    Azure-->>AnalyzeService: analysis_result
    AnalyzeService->>PersistenceService: save_analysis_result()
    PersistenceService->>MongoDB: insert_document()
    MongoDB-->>PersistenceService: document_id
    PersistenceService-->>AnalyzeService: saved_id
    AnalyzeService-->>API: complete_response
    API-->>Client: JSON Response + Auto-saved to DB
````

### **Tecnologias Utilizadas**

- **FastAPI** - Framework web moderno e rápido
- **Pydantic** - Validação de dados e serialização
- **MongoDB** - Banco de dados NoSQL para persistência
- **Azure Document Intelligence** - Extração de texto e layout
- **Docker** - Containerização e ambiente de desenvolvimento
- **Python 3.9+** - Linguagem base com type hints

### **Funcionalidades**

- ✅ Análise de documentos PDF
- ✅ Extração de questões e alternativas
- ✅ Categorização de imagens (header/content)
- ✅ Construção de context blocks estruturados
- ✅ **Persistência automática MongoDB** - Salvamento de todos os responses
- ✅ **Sistema de migrações versionadas** - Evolução controlada do banco
- ✅ **Health monitoring** - Monitoramento de saúde do banco de dados
- ✅ API REST completa com documentação automática
- ✅ Sistema de mock para desenvolvimento

## 🚀 Quick Start

### **🐳 Método Recomendado (Docker)**

```bash
# 1. Clonar repositório
git clone [repository-url]
cd CriEduc.SmartQuest

# 2. Configurar ambiente
cp .env.example .env
cp .env-local.example .env-local

# 3. Subir infraestrutura completa
docker-compose up -d

# 4. Aplicar migrações do banco
cd scripts
python run_migrations.py

# 5. Aplicação disponível em http://localhost:8000
```

### **🐍 Método Manual (Python)**

```bash
# 1. Configurar ambiente Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis
cp .env.example .env
cp .env-local.example .env-local

# 4. Executar aplicação
python start_simple.py
```

## 📁 Estrutura do Projeto

```
app/
├── api/                 # Endpoints e controllers
├── core/               # DI Container, interfaces, exceções
├── models/             # Modelos Pydantic (internal/api/persistence)
├── services/           # Serviços de negócio
│   ├── infrastructure/ # MongoDB connection service
│   └── persistence/    # Camada de persistência MongoDB
├── parsers/            # Parsers de texto
├── utils/              # Utilitários
└── main.py            # Aplicação principal

scripts/                # Scripts de infraestrutura
├── migrations/         # Migrações versionadas MongoDB
├── run_migrations.py   # Executor de migrações
└── mongo-init.js      # Script inicial Docker

tests/                  # Testes automatizados
docs/                   # Documentação técnica
docker-compose.yml      # Infraestrutura Docker
```

## 📚 Documentação

Para documentação técnica detalhada, consulte:

- [🏗️ Arquitetura](docs/ARCHITECTURE.md) - Visão detalhada da arquitetura
- [🔌 Dependency Injection](docs/DEPENDENCY_INJECTION.md) - Guia do DI Container
- [⚙️ Setup](docs/SETUP.md) - Configuração e instalação
- [� API](docs/API.md) - Documentação dos endpoints

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=app

# Executar teste específico
pytest tests/unit/test_services.py
```

## 📞 Suporte

Para questões técnicas:

1. Verifique o health check: `GET /health`
2. Consulte os logs em `logs/`
3. Execute os testes: `pytest`

---

**Versão:** 1.0.0  
**Status:** Produção Ready ✅
├── 📋 RELATORIO_LIMPEZA_TESTES.md # Test cleanup report
├── 📘 README.md # Main documentation (this file)
├── 🚀 start_simple.py # Simple startup script
├── 🔧 start.ps1 # PowerShell startup script
├── 🧪 run_tests.py # Test execution script
├── 🧪 run_tests.ps1 # PowerShell test script
├── 🧪 test_cache_system.py # **🆕 Cache system tests**
├── 🛠️ cache_manager_cli.py # **🆕 Cache management CLI**
├── 🔐 .env # Environment variables (local) │ ├── 📋 logging.py # Structured logging system
│ │ ├── 🔄 context.py # Request context management
│ │ ├── 💾 cache/ # **🆕 Document caching system**
│ │ │ ├── 📦 **init**.py
│ │ │ ├── 🗂️ cache_manager.py # Main cache interface
│ │ │ ├── 🗄️ cache_storage.py # File-based cache storage
│ │ │ ├── 🔑 cache_key_builder.py # Cache key generation
│ │ │ └── 🎯 cache_decorator.py # Cache decorators
│ │ ├── 🔧 middleware/ # **🆕 Request middleware**
│ │ │ ├── 📦 **init**.py
│ │ │ └── 🔄 context_middleware.py # Context tracking
│ │ └── 🛠️ utils.py # Utility functionsSmartQuest is a microse│ ├── ⚙️ config/ # Application configuration
││ ├── 🧠 services/ # Business logic services
│ │ ├── 📦 **init**.py
│ │ ├── 🧠 analyze_service.py # Main analysis orchestration (with Pydantic models)
│ │ ├── ☁️ azure_document_intelligence_service.py # Azure AI provider implementation
│ │ ├── 🏗️ document_extraction_factory.py # Provider factory service
│ │ ├── 🔧 mock_document_service.py # Mock service with refactored methods
│ │ ├── 📂 adapters/ # Provider adapters
│ │ ├── 🔧 base/ # Base interfaces and utilities
│ │ ├── 📂 providers/ # Document provider implementations
│ │ ├── 📂 storage/ # Document storage services
│ │ └── 🔧 utils/ # Service utilities 📦 **init**.py
│ │ └── ⚙️ settings.py # App settings and configuration
│ │
│ ├── 🔧 core/ # Core utilities and configurations
│ │ ├── 🔧 config.py # Core configuration
│ │ ├── ⚠️ exceptions.py # Custom exceptions
│ │ ├── 📋 logging.py # Structured logging system
│ │ └── 🛠️ utils.py # Utility functions
│ │
│ ├── 📊 data/ # Static data and reference files
│ │ ├── 📦 **init**.py
│ │ ├── 🏙️ cities.py # Brazilian cities data
│ │ ├── 🏫 institution_prefixes.py # Educational institution prefixes
│ │ └── 📚 subjects.py # Academic subjects data
│ │
│ ├── 🏗️ models/ # Data models and schemas
│ │ └── 📂 internal/ # Internal Pydantic models
│ │ ├── 📄 document_response.py # InternalDocumentResponse
│ │ └── 📄 document_metadata.py # InternalDocumentMetadata
│ │
│ ├── 🔄 adapters/ # Response adapters
│ │ └── 📄 document_response_adapter.py # API response conversionhe CriEduc ecosystem, designed to intelligently extract, classify, and analyze educational assessments (exams, tests, quizzes) provided in PDF format. Its goal is to provide automated insights into the structure and content of educational materials using natural language processing and artificial intelligence.

## 📌 Features

| ✅ Feature                               | Description                                                                     |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| **Upload assessments**                   | Process educational assessments in **PDF format**                               |
| **Extract questions & answers**          | Identify and extract **questions & answer choices** from documents              |
| **Extract header images**                | Automatically categorize and extract **images from document headers**           |
| **Detect subjects/topics**               | Recognize relevant **subjects and topics** covered in each question             |
| **Classify question types**              | Identify question formats like **multiple-choice, open-ended**, etc.            |
| **Provider-agnostic storage**            | Generic storage system supporting **multiple document providers**               |
| **Azure Document Intelligence Cache**    | **🆕 Smart caching system** to avoid redundant Azure API calls (7-day duration) |
| **Generate feedback** _(future feature)_ | Provide **potential commentary or analysis** based on content                   |
| **Machine-readable results**             | Output structured **JSON-formatted data** for automation                        |

## 🧠 Use Cases

- 🔹 Educational platforms aiming to automate test analysis
- 🔹 Teachers and schools that want fast classification of learning objectives
- 🔹 Data analysts needing to visualize assessment focus area

## 🧱 Project Structure

```
📁 CriEduc.SmartQuest/
│
├── 🛠️ .vscode/                      # VS Code environment settings
│
├── 🚀 app/                          # Main application code (FastAPI)
│   ├── 🏁 main.py                   # API entry point
│   ├── 📦 __init__.py
│
│   ├── 🌐 api/                      # API routes and controllers
│   │   ├── 📦 __init__.py
│   │   ├── 🗂️ routers.py            # API routes and endpoints
│   │   └── 📂 controllers/          # Request handlers and business logic
│   │       ├── 📦 __init__.py
│   │       └── 🧠 analyze.py        # Document analysis controller (simplified)
│   │
│   ├── ⚙️ config/                   # Application configuration
│   │   ├── 📦 __init__.py
│   │   └── ⚙️ settings.py           # App settings and configuration
│   │
│   ├── � core/                     # Core utilities and configurations
│   │   ├── � config.py             # Core configuration
│   │   ├── ⚠️ exceptions.py         # Custom exceptions
│   │   └── �️ utils.py              # Utility functions
│   │
│   ├── 📊 data/                     # Static data and reference files
│   │   ├── 📦 __init__.py
│   │   ├── 🏙️ cities.py             # Brazilian cities data
│   │   ├── 🏫 institution_prefixes.py # Educational institution prefixes
│   │   └── 📚 subjects.py           # Academic subjects data
│   │
│   ├── 🗂️ parsers/                  # Document parsing logic
│   │   ├── 📂 header_parser/        # Exam header extraction
│   │   │   ├── 📦 __init__.py
│   │   │   ├── 🔧 base.py           # Base parsing functionality
│   │   │   ├── �️ parse_city.py     # City name extraction
│   │   │   ├── 🎓 parse_class.py    # Class identifier parsing
│   │   │   ├── 📅 parse_date.py     # Date extraction
│   │   │   ├── 📝 parse_exam_title.py # Exam title parsing
│   │   │   ├── 🔢 parse_grade.py    # Grade/year extraction
│   │   │   ├── 📊 parse_grade_value.py # Grade value parsing
│   │   │   ├── 🌐 parse_network.py  # Education network detection
│   │   │   ├── 🏫 parse_school.py   # School name extraction
│   │   │   ├── 👤 parse_student.py  # Student name parsing
│   │   │   ├── 📚 parse_subject.py  # Subject identification
│   │   │   ├── �‍🏫 parse_teacher.py  # Teacher name extraction
│   │   │   └── 📅 parse_trimester.py # Trimester parsing
│   │   │
│   │   └── 📂 question_parser/      # Question and context parsing
│   │       ├── 📦 __init__.py
│   │       ├── 🔧 base.py           # Base question parsing
│   │       ├── � detect_context_blocks.py # Context block detection
│   │       ├── ❓ detect_questions.py # Question detection
│   │       ├── 🔗 match_context_to_questions.py # Context-question mapping
│   │       ├── 📝 extract_alternatives_from_lines.py # Alternative extraction
│   │       └── 📄 extract_alternatives_from_text.py # Text-based alternatives
│   │
│   ├── � schemas/                  # Request/Response DTOs
│   │   └── 📂 analyze_document/
│   │       └── 📄 upload.py         # Upload schemas
│   │
│   ├── 🧠 services/                 # Business logic services
│   │   ├── 📦 __init__.py
│   │   ├── 🧠 analyze_service.py    # Main analysis orchestration with image processing
│   │   ├── ☁️ azure_document_intelligence_service.py # Azure AI provider implementation
│   │   ├── 🏗️ document_extraction_factory.py # Provider factory service
│   │   ├── 📂 adapters/            # Provider adapters
│   │   ├── � base/                # Base interfaces and utilities
│   │   ├── 📂 providers/           # Document provider implementations
│   │   ├── 📂 storage/             # Document storage services
│   │   └── � utils/               # Service utilities
│   │
│   ├── �️ utils/                    # Utility modules
│   │   ├── 📦 __init__.py
│   │   └── 🏗️ final_result_builder.py # Response formatting
│   │
│   └── ✅ validators/               # Input validation
│       ├── � __init__.py
│       └── 🔍 analyze_validator.py  # Document analysis validation
│
├── 🧪 tests/                        # Test files organized by category
│   ├── 📋 conftest.py               # Pytest configuration
│   ├── 📄 pytest.ini               # Test settings
│   ├── 📚 COVERAGE_CONFIGURATION.md # Coverage setup guide
│   ├── 📚 QUICK_GUIDE.md            # Quick testing guide
│   ├── 📚 README.md                 # Testing documentation
│   ├── 📚 REORGANIZATION_SUMMARY.md # Test reorganization summary
│   ├── 📚 TEST_IMPROVEMENTS.md      # Test improvement notes
│   │
│   ├── 📂 unit/                     # Unit tests (organized & clean)
│   │   ├── 📂 test_adapters/        # DocumentResponseAdapter tests
│   │   ├── 📂 test_exceptions/      # Exception handling tests
│   │   ├── � test_models/          # Pydantic models tests
│   │   ├── 📂 test_parsers/         # Header & question parser tests
│   │   ├── 📂 test_services/        # Business service tests
│   │   ├── 📂 test_utils/           # Utility function tests
│   │   └── 📂 test_validators/      # Input validation tests
│   │
│   ├── 📂 integration/              # Integration tests
│   │   ├── 📂 test_api/            # API endpoint tests
│   │   └── 📂 test_azure/          # Azure integration tests
│   │
│   ├── 📂 debug_scripts/           # Organized debug scripts
│   │   ├── 📂 analysis_tools/      # Analysis and comparison tools
│   │   ├── 📂 azure_figure_extraction/ # Azure figure extraction tests
│   │   ├── 📂 data_validation/     # Data validation scripts
│   │   ├── 📂 figure_enumeration/  # Figure enumeration tests
│   │   └── 📂 parser_analysis/     # Parser analysis tools
│   │
│   ├── 📂 coverage/                # Coverage reports
│   │   ├── 📄 coverage.xml         # XML coverage report
│   │   └── 📂 html/                # HTML coverage report
│   │
│   ├── 📂 documents/               # Test documents
│   ├── 📂 extracted_images/        # Extracted test images
│   ├── 📂 fixtures/                # Test fixtures
│   ├── 📂 images/                  # Test images
│   └── 📂 responses/               # Mock responses
│
├── 🌐 venv/                         # Virtual environment (local)
├── 📦 requirements.txt              # Project dependencies
├── ⚙️ pyproject.toml                # Project configuration
├── 📚 docs/                         # Technical documentation
│   └── 📄 azure_document_intelligence_coordinates.md # Azure coordinates guide
├── 🏗️ ARCHITECTURE.md               # Architecture documentation
├── ⚙️ CONFIG.md                     # Configuration guide
├── 📋 CHANGELOG.md                  # Change log
├── � CONSTANTS_SYSTEM.md           # System constants documentation
├── 📋 MIGRATION_EXAMPLES.md         # Migration examples
├── 📋 RELATORIO_LIMPEZA_TESTES.md   # Test cleanup report
├── �📘 README.md                     # Main documentation (this file)
├── 🚀 start_simple.py               # Simple startup script
├── 🔧 start.ps1                     # PowerShell startup script
├── 🧪 run_tests.py                  # Test execution script
├── 🧪 run_tests.ps1                 # PowerShell test script
├── 🔐 .env                          # Environment variables (local)
├── 📋 .env.example                  # Environment template
├── 📋 .env-local.example            # Local environment template
├── 🔐 .env-local                    # Local environment (if exists)
└── 🙈 .gitignore                    # Git ignore rules
```

## 📑 Header Parsing

The metadata block at the top of each exam is parsed by small, focused
functions located under `app/parsers/header_parser/`. Each file is
responsible for extracting a single field, making the code easy to test
and extend.

**New**: Header parsing now includes automatic image categorization and extraction. Images found in the header area are automatically included in the `document_metadata.images` array.

```
app/parsers/header_parser/
├── base.py            # Entry point with image support
├── parse_network.py   # Detects the education network
├── parse_school.py    # Extracts the school name
├── parse_city.py      # Matches city names
├── parse_teacher.py   # Teacher name
├── parse_subject.py   # Subject taught
├── parse_exam_title.py# Exam title
├── parse_trimester.py # Trimester value
├── parse_grade.py     # Grade or school year
├── parse_class.py     # Class identifier
├── parse_student.py   # Student name
├── parse_grade_value.py# Expected grade value
└── parse_date.py      # Exam date
```

## 🗄️ Storage Architecture

SmartQuest now features a provider-agnostic storage architecture:

- **DocumentStorageService**: Generic storage service for document artifacts
- **BaseDocumentProvider**: Abstract base class for document analysis providers
- **Future-Ready**: Prepared for easy migration to database storage systems

This architecture separates storage concerns from document analysis, making it easier to integrate new storage backends in the future.

## 💾 MongoDB Persistence System

SmartQuest features a **comprehensive MongoDB persistence system** that automatically stores all document analysis results for future reference and analytics.

### 🎯 **Key Features**

| Feature                   | Description                                | Benefit                          |
| ------------------------- | ------------------------------------------ | -------------------------------- |
| **Automatic Persistence** | Transparently saves all analysis results   | Complete audit trail and history |
| **Pydantic Models**       | Type-safe document models with validation  | Data integrity and consistency   |
| **Migration System**      | Versioned database schema evolution        | Safe production deployments      |
| **Health Monitoring**     | Real-time database connectivity checks     | Operational reliability          |
| **Docker Integration**    | MongoDB containerized with automatic setup | Easy development and deployment  |

### 🗄️ **Data Models**

```python
# Core persistence models
AnalyzeDocumentRecord:
- user_email: str
- file_name: str
- response: Dict[str, Any]  # Complete API response
- status: DocumentStatus
- created_at: datetime

AzureProcessingDataRecord:
- operation_id: str
- model_id: str
- api_version: str
- response: Dict[str, Any]  # Azure raw response
- metrics: ProcessingMetrics
- created_at: datetime
```

### 🔄 **Migration System**

```bash
# Apply database migrations
cd scripts
python run_migrations.py

# Current migrations:
- 2025-10-14_001000: Create initial collections
- 2025-10-14_002000: Add enhanced status field
- 2025-10-18_001000: Remove duplicate collections
```

### 📊 **MongoDB Collections**

| Collection              | Purpose                  | Documents |
| ----------------------- | ------------------------ | --------- |
| `analyze_documents`     | Analysis results storage | Main data |
| `azure_processing_data` | Azure processing metrics | Analytics |
| `migrations`            | Schema version control   | System    |

### ⚙️ **Configuration**

Persistence is controlled via environment variables:

```bash
# .env-local configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=smartquest
MONGODB_DOCKER_CONTAINER=smartquest-mongodb

# Note: MongoDB persistence is now MANDATORY (no feature flag needed)
```

### 📈 **Performance**

- **Async Operations**: Non-blocking database operations
- **Connection Pooling**: Efficient MongoDB connections via Motor
- **Error Handling**: Graceful fallback if database unavailable
- **Health Checks**: Real-time monitoring via `/health/database`

## 💾 Azure Document Intelligence Cache System

SmartQuest features an **intelligent caching system** that automatically stores Azure Document Intelligence responses to avoid redundant API calls and improve performance.

### 🎯 **Key Features**

| Feature                   | Description                                         | Benefit                              |
| ------------------------- | --------------------------------------------------- | ------------------------------------ |
| **Automatic Caching**     | Transparently caches Azure extraction results       | Faster response times, reduced costs |
| **Smart Cache Keys**      | Uses `{email}_{filename}_{file_size}_{hash}` format | Prevents cache collisions            |
| **7-Day Duration**        | Configurable cache expiration (default: 1 week)     | Balances freshness with performance  |
| **File-Based Storage**    | Persistent JSON-based cache storage                 | Works without external dependencies  |
| **Isolated Architecture** | Decoupled from main processing logic                | Easy to enable/disable or replace    |

### 🔄 **How It Works**

```mermaid
graph TD
    A[Document Upload] --> B{Check Cache}
    B -->|Cache Hit| C[Return Cached Data]
    B -->|Cache Miss| D[Call Azure API]
    D --> E[Store in Cache]
    E --> F[Return Fresh Data]
    C --> G[Continue Processing]
    F --> G
```

### 🗂️ **Cache Key Format**

The cache system generates unique keys based on:

- **User Email**: Ensures user isolation
- **Filename**: Identifies the document
- **File Size**: Detects file changes with same name
- **Hash Suffix**: Prevents key collisions

Example: `user_example_com_document_pdf_1024_abc12345.json`

### 📊 **Cache Performance**

When cache is enabled, typical performance improvements:

- **First Request**: Normal Azure processing time (~10-30 seconds)
- **Subsequent Requests**: **~50ms** (cached response)
- **Cost Savings**: Up to **95% reduction** in Azure API calls

### 🛠️ **Configuration**

Cache is automatically enabled for all Azure Document Intelligence calls. No configuration required!

**Optional Configuration:**

```python
# Custom cache duration
cache_manager = DocumentCacheManager(cache_duration_days=14)

# Custom cache directory
cache_manager = DocumentCacheManager(cache_dir="custom_cache")
```

### 🔧 **Cache Management**

Use the included CLI tool for cache management:

```bash
# View cache statistics
python cache_manager_cli.py stats

# Clean expired entries
python cache_manager_cli.py cleanup

# List cached documents
python cache_manager_cli.py list --limit 10

# Inspect specific cache entry
python cache_manager_cli.py inspect {cache_key}

# Clear all cache (use with caution)
python cache_manager_cli.py clear
```

### 📈 **Cache Statistics Example**

```bash
$ python cache_manager_cli.py stats

📊 Cache Statistics
========================================
📁 Cache Directory: ./cache
📄 Total Files: 25
✅ Valid Files: 23
❌ Expired Files: 2
💾 Total Size: 15.2 MB
🎯 Cache Hit Rate: 92.0%
```

### 🧪 **Testing the Cache System**

Run the comprehensive cache test suite:

```bash
# Test all cache functionality
python test_cache_system.py

# Expected output:
🧪 Testing Document Cache System
==================================================
📧 Email: test@example.com
📄 Filename: test_document.pdf
📊 File size: 28 bytes

1️⃣ Testing cache key generation...
✅ Generated cache key: test_example_com_test_document_pdf_28_a1b2c3d4

2️⃣ Testing cache miss...
✅ Cache miss detected (expected)

3️⃣ Testing cache storage...
✅ Data cached successfully

4️⃣ Testing cache hit...
✅ Cache hit detected
✅ Cached data matches original

5️⃣ Testing cache statistics...
✅ Cache stats: {...}

🎉 Cache system test completed!
```

### 🔐 **Security & Privacy**

- **User Isolation**: Each user's cache is completely separate
- **Local Storage**: Cache files stored locally, not in cloud
- **Automatic Cleanup**: Expired entries automatically removed
- **No Sensitive Data**: Only document extraction results cached

### ⚡ **Cache Endpoints Integration**

The cache system is automatically integrated into these endpoints:

- ✅ `/analyze_document` - Full caching support
- ✅ `/analyze_document_with_figures` - Full caching support
- ❌ `/analyze_document_mock` - No caching (uses mock data)

### 🔄 **Cache Invalidation**

Cache entries are automatically invalidated when:

- **7 days have passed** (configurable)
- **File content changes** (detected by size difference)
- **Manual cleanup** via CLI tool

### 🚨 **Troubleshooting**

**Cache not working?**

- Check if email is provided in the request
- Verify cache directory permissions
- Review logs for cache-related errors

**Performance issues?**

- Run `cache_manager_cli.py cleanup` to remove expired entries
- Check cache directory disk space
- Monitor cache hit rates in logs

**Need to reset cache?**

- Use `cache_manager_cli.py clear` to remove all entries
- Or manually delete the `cache/` directory

## 🛠️ Tech Stack

| ✅ Technology                      | Description                                              |
| ---------------------------------- | -------------------------------------------------------- |
| **Python 3.9+**                    | Tested on versions 3.9+                                  |
| **FastAPI**                        | High-performance web framework for building RESTful APIs |
| **MongoDB 7.0**                    | **🆕 NoSQL database for document persistence**           |
| **PyMongo/Motor**                  | **🆕 MongoDB drivers (sync/async)**                      |
| **Docker & Docker Compose**        | **🆕 Containerization and infrastructure**               |
| **Azure AI Document Intelligence** | Cloud-based document processing and extraction           |
| **PyMuPDF (fitz)**                 | PDF image extraction and processing library              |
| **Azure SDK for Python**           | Integration with Azure cognitive services                |
| **Pydantic**                       | Request validation and data modeling                     |
| **Pytest**                         | Unit testing framework                                   |
| **File-based Caching**             | JSON-based cache system for Azure API responses          |

## 🛡️ Professional Exception Handling

SmartQuest features a **professional-grade exception handling system** designed for enterprise applications:

### 🎯 **Exception Hierarchy**

- **SmartQuestException**: Base class for all custom exceptions
- **ValidationException**: Input validation errors (422 status)
- **DocumentProcessingError**: Document analysis failures (500 status)
- **Specialized Exceptions**: InvalidEmailException, MissingFileException, etc.

### 📝 **Structured Logging**

```python
# Automatic structured logs with context
structured_logger.info("Document analysis started", context={
    "email": "user@example.com",
    "filename": "exam.pdf",
    "use_mock": False
})
```

### 🎭 **Exception Decorator**

Controllers use the `@handle_exceptions` decorator for automatic error handling:

```python
@router.post("/analyze_document")
@handle_exceptions("document_analysis")
async def analyze_document(...):
    # Clean business logic without try/catch blocks
    return await process_document()
```

### ✅ **Benefits**

- **Automatic error logging** with request context
- **Consistent HTTP responses** with structured error details
- **Request timing** and performance monitoring
- **Clean controller code** without repetitive error handling
- **Enterprise-grade reliability** with comprehensive error coverage

## 🚀 Getting Started

### **🐳 Recommended: Docker Setup (Complete Infrastructure)**

📌 1. Clone the Repository

```bash
git clone https://github.com/your-repository.git
cd CriEduc.SmartQuest
```

📌 2. Configure Environment Variables

Create environment files from templates:

```bash
cp .env.example .env
cp .env-local.example .env-local
```

Edit `.env-local` with your Azure credentials:

```bash
# Azure AI Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key

# MongoDB (Docker will handle this automatically - MANDATORY)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=smartquest
```

📌 3. Start Complete Infrastructure

```bash
# Start API + MongoDB with Docker
docker-compose up -d

# Apply database migrations
cd scripts
python run_migrations.py

# API available at: http://localhost:8000
# MongoDB available at: localhost:27017
```

### **🐍 Alternative: Manual Python Setup**

📌 1. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

📌 2. Configure Environment Variables

Create a `.env-local` file in the project root:

```bash
# Azure AI Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key
AZURE_DOCUMENT_INTELLIGENCE_MODEL=prebuilt-layout
AZURE_DOCUMENT_INTELLIGENCE_API_VERSION=2023-07-31

# MongoDB Configuration (requires local MongoDB installation - MANDATORY)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=smartquest

# App configuration
APP_NAME=SmartQuest API
DEBUG=false
```

📌 4. Install Dependencies

```
pip install -r requirements.txt
```

📌 5. Start the API

**Option 1: Direct Python**

```
python start_simple.py
```

**Option 2: Uvicorn**

```
uvicorn app.main:app --reload
```

**Option 3: PowerShell Script**

```
.\start.ps1
```

## 🧪 Testing

### 📊 **Test Statistics**

| Métrica                    | Valor  | Status                              |
| -------------------------- | ------ | ----------------------------------- |
| **Total de Testes**        | 117    | ✅ 110 Passando, 7 Para Corrigir    |
| **Cobertura de Código**    | 50.58% | ✅ Meta alcançada                   |
| **Testes Unitários**       | 85+    | ✅ Expandidos com novos componentes |
| **Integration Tests**      | 29     | ✅ Completos                        |
| **Arquivos 100% Cobertos** | 19     | ✅ Excelente                        |

### 🏗️ **Estrutura de Testes (ATUALIZADA)**

```
tests/
├── unit/                    # Unit tests (85+ tests, expandido)
│   ├── test_adapters/       # DocumentResponseAdapter (NOVO)
│   ├── test_models/         # Pydantic models (NOVO)
│   ├── test_parsers/        # HeaderParser, QuestionParser, etc.
│   ├── test_services/       # Business services (expandido)
│   ├── test_validators/     # Input validators
│   ├── test_exceptions/     # Exception handling
│   └── test_utils/          # Utilities (extract_city, etc.)
├── integration/             # Integration tests (29 tests)
│   ├── test_api/            # API endpoints
│   └── test_azure/          # Azure integration
├── debug_scripts/           # Organized debug scripts (LIMPO)
│   ├── analysis_tools/      # Analysis and comparison
│   ├── azure_figure_extraction/ # Azure extraction tests
│   ├── data_validation/     # Data validation
│   ├── figure_enumeration/  # Figure enumeration
│   └── parser_analysis/     # Parser analysis
├── fixtures/                # Reusable test data
└── coverage/                # Coverage reports (HTML/XML)
```

### 🚀 **Running Tests**

#### **Main Command (Recommended)**

```bash
# Run all tests with coverage
python run_tests.py --coverage
```

#### **Specific Commands**

```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# Specific test with coverage
python -m pytest tests/unit/test_parsers/test_parse_student.py --cov=app

# HTML coverage report
python -m pytest --cov=app --cov-report=html
```

#### **Legacy Tests (Azure)**

```powershell
# Test Azure AI integration (detailed)
python test_azure_detailed.py

# Test Azure AI integration (basic)
python test_azure_only.py
```

### 🎯 **Tests with 100% Coverage**

| Módulo              | Testes | Status  |
| ------------------- | ------ | ------- |
| `parse_student.py`  | 20     | ✅ 100% |
| `extract_city.py`   | 5      | ✅ 100% |
| `parse_date.py`     | 5      | ✅ 100% |
| `HeaderParser`      | 15     | ✅ 100% |
| `QuestionParser`    | 15     | ✅ 100% |
| `API Endpoints`     | 14     | ✅ 100% |
| `Azure Integration` | 15     | ✅ 100% |

### 📈 **Coverage Reports**

- **Terminal**: Summary report after execution
- **HTML**: `tests/coverage/html/index.html` (navegador)
- **XML**: `tests/coverage/coverage.xml` (CI/CD)

### 🔧 **Configuration**

Test configuration is optimized in `pyproject.toml`:

- Exclui arquivos `__init__.py` da cobertura
- Foca apenas no código de negócio
- Clean and useful reports

## 🐛 Debugging in VS Code

The project includes debug configurations in `.vscode/launch.json`:

- **🚀 SmartQuest API - Direct Run**: Run main.py directly
- **🔍 FastAPI with Uvicorn**: Run with uvicorn and auto-reload
- **🐛 Debug Specific Process**: For debugging specific processes
- **🧪 Test Azure AI**: For testing Azure AI scripts

### Debug Setup

1. Open VS Code in the project folder
2. Press `F5` to start debugging
3. Select the appropriate debug configuration
4. Set breakpoints as needed

## 🔧 Troubleshooting

### Common Issues

**Azure AI Connection Failed**

- Verify your credentials in `.env`
- Check if your Azure service is active
- Ensure endpoint URL is correct

**Import Errors**

- Activate virtual environment: `.venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python interpreter in VS Code

**PDF Processing Fails**

- Verify PDF file exists in `tests/modelo-prova.pdf`
- Check Azure AI quota and limits
- Review error logs for specific issues

## 📡 Available Endpoints v2.0.0

| Method   | Endpoint                         | Description                            | Status |
| -------- | -------------------------------- | -------------------------------------- | ------ |
| **GET**  | `/health/`                       | Sistema de health check completo       | ✅     |
| **POST** | `/analyze/analyze_document`      | Análise de documentos com persistência | ✅     |
| **GET**  | `/analyze/analyze_document/{id}` | Recuperação de documentos por ID       | ✅     |
| **GET**  | `/docs`                          | Documentação Swagger UI interativa     | ✅     |

### **🆕 Endpoint Consolidado: Health Check Completo**

O endpoint `/health/` agora realiza verificação abrangente de todas as dependências:

#### **🔍 Dependências Monitoradas:**

- ✅ **MongoDB** (CRÍTICO) - Persistência obrigatória
- ✅ **Azure Blob Storage** (CRÍTICO) - Armazenamento de imagens
- ⚠️ **Azure Document Intelligence** (NÃO CRÍTICO) - Pode usar mock

#### **📊 Status Possíveis:**

- `200 healthy` - Todas as dependências funcionando
- `200 degraded` - Sistema operacional com avisos não-críticos
- `503 unhealthy` - Dependências críticas indisponíveis

### **🆕 Enhanced Document Analysis with Mandatory MongoDB Persistence**

O endpoint principal `/analyze/analyze_document` agora inclui **persistência obrigatória** de todos os resultados:

#### **🏗️ Características da Arquitetura:**

- ✅ **Pipeline em 4 Etapas**: Validação → Extração → Análise → Persistência
- ✅ **Cache Transparente**: Otimização automática da extração
- ✅ **DI Container**: Resolução automática de toda árvore de dependências
- ✅ **Type Safety**: Validação completa com Pydantic models
- ✅ **Error Handling**: Tratamento robusto de exceções

#### **📋 Request Format:**

```bash
POST /analyze/analyze_document
Content-Type: multipart/form-data

# Parâmetros obrigatórios:
# - email: Email do usuário (query string)
# - file: Arquivo PDF (form data)
```

#### **🎯 Pipeline de Processamento:**

```
1. Validação → AnalyzeValidator.validate_all()
2. Extração → DocumentExtractionService (com cache)
3. Análise → AnalyzeService via DI Container
4. Persistência → SimplePersistenceService (obrigatória)
```

### **🆕 Document Retrieval Endpoint**

O novo endpoint `GET /analyze/analyze_document/{id}` permite recuperar documentos processados:

#### **📝 Características:**

- ✅ **Busca por ID**: ID único gerado durante análise
- ✅ **Validação Robusta**: Verificação de formato e existência
- ✅ **Error Handling**: 400 (ID inválido), 404 (não encontrado), 500 (erro interno)
- ✅ **DTO Dedicado**: `AnalyzeDocumentResponseDTO` para resposta

#### **📊 Response Format:**

```json
{
  "email": "professor@escola.edu.br",
  "document_id": "32674f3c-b5c8-4cc3-8c76-d8c716132a60",
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
      "question": "O texto de Marina Colasanti descreve diversas situações...",
      "alternatives": [
        {
          "letter": "a",
          "text": "da velocidade com que a tecnologia influencia..."
        },
        {
          "letter": "b",
          "text": "do desrespeito do ser humano com a vida humilde..."
        }
      ],
      "hasImage": false,
      "context_id": null
    }
  ],
  "context_blocks": [
    {
      "id": 1,
      "type": ["text"],
      "source": "exam_document",
      "statement": "LEIA O TEXTO A SEGUIR",
      "title": "Eu sei, mas não devia (Marina Colasanti)",
      "hasImage": false,
      "images": [],
      "contentType": null,
      "paragraphs": ["Eu sei que a gente se acostuma..."],
      "sub_contexts": null
    }
  ]
}
```

```

## 🖼️ **Image Extraction Performance Analysis**

### **📊 Performance Comparison: Azure Figures vs Manual PDF Extraction**

We conducted a comprehensive analysis comparing two image extraction methods using a real educational document with 7 figures. The results reveal significant performance and quality differences:

#### **🚀 Performance Metrics**

| Method            | Processing Time | Speed Comparison | Extraction Success |
| ----------------- | --------------- | ---------------- | ------------------ |
| **Azure Figures** | 49.26 seconds   | Baseline         | ✅ 7/7 images      |
| **Manual PDF**    | 0.13 seconds    | **379x faster**  | ✅ 7/7 images      |

#### **🎯 Quality Analysis**

Both methods successfully extract all 7 figures, but with different quality characteristics:

| Aspect                 | Azure Figures        | Manual PDF            | Advantage              |
| ---------------------- | -------------------- | --------------------- | ---------------------- |
| **Average Resolution** | ~414×232 pixels      | ~596×334 pixels       | **Manual PDF (+107%)** |
| **File Format**        | PNG (lossless)       | JPEG (compressed)     | Azure Figures          |
| **File Size**          | Larger (~0.12MB avg) | Smaller (~0.08MB avg) | Manual PDF             |
| **Color Quality**      | RGB (full color)     | RGB (full color)      | Equal                  |

#### **📈 Detailed Resolution Comparison**

| Image    | Azure Dimensions | Manual Dimensions | Manual Advantage |
| -------- | ---------------- | ----------------- | ---------------- |
| Figure 1 | 142×48           | 203×69            | +105.5% pixels   |
| Figure 2 | 414×232          | 596×334           | +107.3% pixels   |
| Figure 3 | 405×218          | 584×314           | +107.7% pixels   |
| Figure 4 | 411×271          | 592×391           | +107.8% pixels   |
| Figure 5 | 334×405          | 480×582           | +106.5% pixels   |
| Figure 6 | 400×305          | 576×440           | +107.7% pixels   |
| Figure 7 | 533×219          | 767×316           | +107.6% pixels   |

#### **🏆 Key Findings**

✅ **Manual PDF Method Advantages:**

- **379x faster** processing time (0.13s vs 49.26s)
- **~107% higher resolution** on average
- **Smaller file sizes** due to JPEG compression
- **Same extraction success rate** (100%)

⚠️ **Azure Figures Method Advantages:**

- **PNG format** preserves image quality without compression
- **Official Azure API** with guaranteed support
- **Consistent formatting** across different document types

#### **🎯 Recommendations**

**For Production Use:**

- **Primary Method**: Manual PDF extraction for speed and higher resolution
- **Fallback Method**: Azure Figures for documents where manual extraction fails
- **Best Practice**: Implement both methods with automatic fallback strategy

**Performance vs Quality Trade-off:**

```

Manual PDF: ⚡ Ultra-fast + 📈 Higher resolution + 💾 Smaller files
Azure API: 🔄 Slower + 🎨 Lossless quality + 🛡️ Enterprise support

```

#### **🧪 Test Methodology**

This analysis was conducted using:

- **Test Document**: Real educational PDF with 7 figures
- **Measurement Tools**: Python PIL for image analysis, MD5 hashing for comparison
- **Metrics Collected**: Dimensions, file sizes, processing time, pixel count
- **Environment**: Local development environment with Azure AI Document Intelligence

> **Note**: Results may vary based on document complexity, network latency, and Azure service performance. The manual method consistently shows superior performance for typical educational documents.

## 📚 Future Roadmap

🔹 **Short-Term Improvements**

- [ ] Integrate SmartQuest with the CriEduc core platform (REST API)
- [ ] Develop a dashboard for previewing parsed content
- [x] **Implement database storage backend** - ✅ **COMPLETED (MongoDB)**
- [ ] Add support for additional image formats in header extraction
- [ ] **MongoDB Analytics Dashboard**: Query performance and usage metrics
- [ ] **Advanced MongoDB Features**: Aggregation pipelines, full-text search
- [ ] **Cache System Enhancements**: Redis support for distributed caching

🔹 **Long-Term Vision**

- [ ] Classify question topics using LLMs (Large Language Models)
- [ ] Support scanned PDFs with OCR fallback
- [ ] Implement automatic difficulty level detection
- [ ] Add support for multiple document analysis providers
- [ ] **MongoDB Scaling**: Sharding and replica sets for high availability
- [ ] **Data Analytics**: Historical analysis and reporting from MongoDB data
- [ ] **Intelligent Cache Invalidation**: Content-based cache invalidation using document fingerprinting

## 🔄 Recent Updates (October 2025)

### 💾 **MongoDB Persistence System Implementation (NEW)**

- **Complete MongoDB Integration**: Full persistence layer with Pydantic models
- **Migration System**: Versioned database schema evolution with automatic runners
- **Docker Infrastructure**: MongoDB containerized with automatic initialization
- **Health Monitoring**: Real-time database connectivity and performance monitoring
- **Type Safety**: Complete type safety with Pydantic models for database operations
- **DI Container Integration**: MongoDB services properly integrated into dependency injection
- **Automatic Persistence**: All `/analyze_document` responses automatically saved
- **Professional Architecture**: Clean separation between infrastructure, persistence, and business logic

## 🔄 Recent Updates (September 2025)

### 💾 **Azure Document Intelligence Cache System (NEW)**

- **Smart Caching**: Automatic caching of Azure API responses to avoid redundant calls
- **Performance Boost**: Up to 95% reduction in Azure API calls for repeated documents
- **7-Day Duration**: Configurable cache expiration with automatic cleanup
- **File-Based Storage**: Persistent JSON cache that works without external dependencies
- **Cache Management CLI**: Complete toolset for monitoring and managing cache (`cache_manager_cli.py`)
- **User Isolation**: Secure cache separation based on `{email}_{filename}_{file_size}` keys
- **Zero Configuration**: Automatically enabled for `/analyze_document` and `/analyze_document_with_figures` endpoints

### ✅ **Major Architectural Refactoring (September 2025)**

- **SOLID Principles**: Refactored services to follow the Single Responsibility Principle (SRP).
- **New `DocumentExtractionService`**: Created to handle all data extraction and caching logic, separating concerns from the analysis process.
- **Simplified `AnalyzeService`**: Now acts as a pure orchestrator for business logic, receiving pre-extracted data.
- **Simplified API**: Removed complex parameters from `/analyze_document` endpoint.
- **Pydantic Models**: Full type safety with `InternalDocumentResponse` and `InternalDocumentMetadata`.
- **Adapter Pattern**: Clean separation via `DocumentResponseAdapter` for API responses.
- **MockDocumentService**: Refactored with specialized methods (`process_document_mock_text_only`, `process_document_mock_images_only`).

### 🧹 **Project Cleanup (15 obsolete files removed)**

- **Test Structure**: Reorganized tests into clear categories (`unit/`, `integration/`, `debug_scripts/`)
- **Code Quality**: Removed obsolete debug scripts and temporary test files
- **Coverage**: Expanded unit tests for new components (adapters, models, refactored services)
- **Documentation**: Updated all documentation to reflect new architecture

### 🏗️ **New Components**

- `DocumentResponseAdapter`: Converts internal models to API responses
- `InternalDocumentResponse`/`InternalDocumentMetadata`: Type-safe internal processing
- Enhanced `AnalyzeService` with `process_document_with_models()` method
- Organized debug scripts in `tests/debug_scripts/` with clear categorization

### 📊 **Test Infrastructure**

- **110 passing tests** (7 require updates for removed methods)
- **Organized structure**: `test_adapters/`, `test_models/`, expanded service tests
- **Clean debug scripts**: Properly categorized in `tests/debug_scripts/`
- **Coverage reports**: HTML and XML formats available

## 💡 Background

SmartQuest is part of a larger vision that began with CriEduc, an educational platform initially developed during a Master's thesis, aiming to provide georeferenced and interactive learning experiences.

## 👨‍💻 Author

Developed by Wander Vinicius Bergami as part of the CriEduc ecosystem.'
Let's build the future of smart education together! 🚀

## 🎯 What Changed?

- ✅ Standardized everything in English for clarity
- ✅ Improved project structure descriptions for better readability
- ✅ Expanded the Getting Started section with install instructions
- ✅ Divided roadmap into short-term and long-term tasks for better planning
```
