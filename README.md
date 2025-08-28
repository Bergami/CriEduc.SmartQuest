## 🏗️ SmartQuest

SmartQuest is a microse│   ├── ⚙️ config/                   # Application configuration
││   ├── 🧠 services/                 # Business logic services
│   │   ├── 📦 __init__.py
│   │   ├── 🧠 analyze_service.py    # Main analysis orchestration (with Pydantic models)
│   │   ├── ☁️ azure_document_intelligence_service.py # Azure AI provider implementation
│   │   ├── 🏗️ document_extraction_factory.py # Provider factory service
│   │   ├── 🔧 mock_document_service.py # Mock service with refactored methods
│   │   ├── 📂 adapters/            # Provider adapters
│   │   ├── 🔧 base/                # Base interfaces and utilities
│   │   ├── 📂 providers/           # Document provider implementations
│   │   ├── 📂 storage/             # Document storage services
│   │   └── 🔧 utils/               # Service utilities 📦 __init__.py
│   │   └── ⚙️ settings.py           # App settings and configuration
│   │
│   ├── 🔧 core/                     # Core utilities and configurations
│   │   ├── 🔧 config.py             # Core configuration
│   │   ├── ⚠️ exceptions.py         # Custom exceptions
│   │   ├── 📋 logging.py            # Structured logging system
│   │   └── 🛠️ utils.py              # Utility functions
│   │
│   ├── 📊 data/                     # Static data and reference files
│   │   ├── 📦 __init__.py
│   │   ├── 🏙️ cities.py             # Brazilian cities data
│   │   ├── 🏫 institution_prefixes.py # Educational institution prefixes
│   │   └── 📚 subjects.py           # Academic subjects data
│   │
│   ├── 🏗️ models/                   # Data models and schemas
│   │   └── 📂 internal/             # Internal Pydantic models
│   │       ├── 📄 document_response.py # InternalDocumentResponse
│   │       └── 📄 document_metadata.py # InternalDocumentMetadata
│   │
│   ├── 🔄 adapters/                 # Response adapters
│   │   └── 📄 document_response_adapter.py # API response conversionhe CriEduc ecosystem, designed to intelligently extract, classify, and analyze educational assessments (exams, tests, quizzes) provided in PDF format. Its goal is to provide automated insights into the structure and content of educational materials using natural language processing and artificial intelligence.


## 📌 Features

| ✅ Feature | Description |
|-----------|------------|
| **Upload assessments** | Process educational assessments in **PDF format** |
| **Extract questions & answers** | Identify and extract **questions & answer choices** from documents |
| **Extract header images** | Automatically categorize and extract **images from document headers** |
| **Detect subjects/topics** | Recognize relevant **subjects and topics** covered in each question |
| **Classify question types** | Identify question formats like **multiple-choice, open-ended**, etc. |
| **Provider-agnostic storage** | Generic storage system supporting **multiple document providers** |
| **Generate feedback** *(future feature)* | Provide **potential commentary or analysis** based on content |
| **Machine-readable results** | Output structured **JSON-formatted data** for automation |



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
│   ├── � extracted_text/          # Extracted test text
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

## 🛠️ Tech Stack


| ✅ Technology | Description |
|--------------|------------|
| **Python 3.9+** | Tested on versions 3.9+ |
| **FastAPI** | High-performance web framework for building RESTful APIs |
| **Azure AI Document Intelligence** | Cloud-based document processing and extraction |
| **PyMuPDF (fitz)** | PDF image extraction and processing library |
| **Azure SDK for Python** | Integration with Azure cognitive services |
| **Pydantic** | Request validation and data modeling |
| **Pytest** | Unit testing framework |


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

📌 1. Clone the Repository

`````
git clone https://github.com/your-repository.git
cd CriEduc.SmartQuest
`````

📌 2. Create and Activate the Virtual Environment

````` 
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
````` 

📌 3. Configure Environment Variables

Create a `.env` file in the project root with your Azure AI Document Intelligence credentials:

````` 
# Azure AI Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key
USE_AZURE_AI=true

AZURE_DOCUMENT_INTELLIGENCE_MODEL=prebuilt-layout
AZURE_DOCUMENT_INTELLIGENCE_API_VERSION=2023-07-31

# App configuration
APP_NAME=SmartQuest API
DEBUG=false
````` 

📌 4. Install Dependencies

````` 
pip install -r requirements.txt
````` 

📌 5. Start the API

**Option 1: Direct Python**
````` 
python start_simple.py
````` 

**Option 2: Uvicorn**
````` 
uvicorn app.main:app --reload
````` 

**Option 3: PowerShell Script**
````` 
.\start.ps1
````` 

## 🧪 Testing

### 📊 **Test Statistics**
| Métrica | Valor | Status |
|---------|-------|--------|
| **Total de Testes** | 117 | ✅ 110 Passando, 7 Para Corrigir |
| **Cobertura de Código** | 50.58% | ✅ Meta alcançada |
| **Testes Unitários** | 85+ | ✅ Expandidos com novos componentes |
| **Integration Tests** | 29 | ✅ Completos |
| **Arquivos 100% Cobertos** | 19 | ✅ Excelente |

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
| Módulo | Testes | Status |
|--------|--------|--------|
| `parse_student.py` | 20 | ✅ 100% |
| `extract_city.py` | 5 | ✅ 100% |
| `parse_date.py` | 5 | ✅ 100% |
| `HeaderParser` | 15 | ✅ 100% |
| `QuestionParser` | 15 | ✅ 100% |
| `API Endpoints` | 14 | ✅ 100% |
| `Azure Integration` | 15 | ✅ 100% |

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

## 📡 Available Endpoints  

| Method | Endpoint | Description |
|--------|---------|------------|
| **GET** | `/health` | Checks API health status |
| **POST** | `/analyze_document` | **SIMPLIFIED**: Clean document analysis with Pydantic models and automatic image extraction |

### **🆕 Simplified Document Analysis with Modern Architecture**

The main `/analyze_document` endpoint has been completely refactored with a modern, clean architecture:

#### **🏗️ New Architecture Features:**
- **Pydantic Models**: Type-safe internal processing with `InternalDocumentResponse` and `InternalDocumentMetadata`
- **Adapter Pattern**: Clean separation between internal models and API responses via `DocumentResponseAdapter`
- **Simplified Interface**: Removed complex parameters (`use_mock`, `use_refactored`, `image_extraction_method`)
- **Automatic Behavior**: Intelligent document processing with built-in fallback strategies

#### **📋 Simplified Request Format:**
```bash
POST /analyze_document
Content-Type: multipart/form-data

# Parameters:
# - file: PDF document (required)
# - Optional query parameters handled automatically
```

#### **🎯 Key Improvements:**
- **Type Safety**: Full Pydantic validation throughout the processing pipeline
- **Clean Code**: Separation of concerns with adapters and internal models
- **Maintainability**: Easier to test, modify, and extend
- **Backward Compatibility**: Same API response format maintained

### **Enhanced API Response Format**

The API now returns header images along with document metadata:

```json
{
  "document_metadata": {
    "network": "Prefeitura Municipal",
    "school": "UMEF Saturnino Rangel Mauro",
    "city": "Vila Velha",
    "teacher": "Danielle",
    "subject": "Língua Portuguesa",
    "exam_title": "Prova Trimestral",
    "trimester": "3º TRIMESTRE",
    "grade": "7º ano",
    "class": null,
    "student": null,
    "grade_value": "12,0",
    "date": null,
    "images": [
      {
        "content": "base64_encoded_image_data...",
        "page": 1,
        "position": {
          "x": 100,
          "y": 50,
          "width": 200,
          "height": 150
        }
      }
    ]
  },
  "context_blocks": [...],
  "questions": [...]
}
```

## 🖼️ **Image Extraction Performance Analysis**

### **📊 Performance Comparison: Azure Figures vs Manual PDF Extraction**

We conducted a comprehensive analysis comparing two image extraction methods using a real educational document with 7 figures. The results reveal significant performance and quality differences:

#### **🚀 Performance Metrics**

| Method | Processing Time | Speed Comparison | Extraction Success |
|--------|----------------|------------------|-------------------|
| **Azure Figures** | 49.26 seconds | Baseline | ✅ 7/7 images |
| **Manual PDF** | 0.13 seconds | **379x faster** | ✅ 7/7 images |

#### **🎯 Quality Analysis**

Both methods successfully extract all 7 figures, but with different quality characteristics:

| Aspect | Azure Figures | Manual PDF | Advantage |
|--------|---------------|------------|-----------|
| **Average Resolution** | ~414×232 pixels | ~596×334 pixels | **Manual PDF (+107%)**|
| **File Format** | PNG (lossless) | JPEG (compressed) | Azure Figures |
| **File Size** | Larger (~0.12MB avg) | Smaller (~0.08MB avg) | Manual PDF |
| **Color Quality** | RGB (full color) | RGB (full color) | Equal |

#### **📈 Detailed Resolution Comparison**

| Image | Azure Dimensions | Manual Dimensions | Manual Advantage |
|-------|-----------------|-------------------|------------------|
| Figure 1 | 142×48 | 203×69 | +105.5% pixels |
| Figure 2 | 414×232 | 596×334 | +107.3% pixels |
| Figure 3 | 405×218 | 584×314 | +107.7% pixels |
| Figure 4 | 411×271 | 592×391 | +107.8% pixels |
| Figure 5 | 334×405 | 480×582 | +106.5% pixels |
| Figure 6 | 400×305 | 576×440 | +107.7% pixels |
| Figure 7 | 533×219 | 767×316 | +107.6% pixels |

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
- [ ] Implement database storage backend for document artifacts
- [ ] Add support for additional image formats in header extraction

🔹 **Long-Term Vision**
- [ ] Classify question topics using LLMs (Large Language Models)
- [ ] Support scanned PDFs with OCR fallback
- [ ] Implement automatic difficulty level detection
- [ ] Add support for multiple document analysis providers

## 🔄 Recent Updates (August 2025)

### ✅ **Major Architectural Refactoring**
- **Simplified API**: Removed complex parameters from `/analyze_document` endpoint
- **Pydantic Models**: Full type safety with `InternalDocumentResponse` and `InternalDocumentMetadata`
- **Adapter Pattern**: Clean separation via `DocumentResponseAdapter` for API responses
- **MockDocumentService**: Refactored with specialized methods (`process_document_mock_text_only`, `process_document_mock_images_only`)

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
