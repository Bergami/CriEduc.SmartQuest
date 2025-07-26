## 🏗️ SmartQuest

SmartQuest is a microservice within the CriEduc ecosystem, designed to intelligently extract, classify, and analyze educational assessments (exams, tests, quizzes) provided in PDF format. Its goal is to provide automated insights into the structure and content of educational materials using natural language processing and artificial intelligence.


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
│   │   └── 🗂️ routers.py            # API routes and endpoints
│   │
│   ├── 🎛️ controllers/              # Request handlers and business logic
│   │   ├── 📦 __init__.py
│   │   ├── 🧠 analyze.py            # Document analysis controller
│   │   └── ❤️ health.py             # Health check controller
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
├── 🧪 tests/                        # Test files and test data
│   ├── 📄 modelo-completo-prova.pdf # Complete exam test file
│   ├── 📄 modelo-prova-completa.pdf # Alternative test file
│   ├── 📄 modelo-prova.pdf          # Basic test file
│   └── 📋 RetornoProcessamento.json # Mock response data
│
├── 🌐 venv/                         # Virtual environment (local)
├── 📦 requirements.txt              # Project dependencies
├── 📚 docs/                         # Technical documentation
│   └── 📄 azure_document_intelligence_coordinates.md # Azure coordinates guide
├── 🏗️ ARCHITECTURE.md               # Architecture documentation
├── ⚙️ CONFIG.md                     # Configuration guide
├── 📋 CHANGELOG.md                  # Change log
├── 📘 README.md                     # Main documentation
├── 🚀 start_simple.py               # Simple startup script
├── 🔧 start.ps1                     # PowerShell startup script
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
| **Total de Testes** | 119 | ✅ 100% Passando |
| **Cobertura de Código** | 50.58% | ✅ Meta alcançada |
| **Testes Unitários** | 74 | ✅ Completos |
| **Integration Tests** | 29 | ✅ Complete |
| **Arquivos 100% Cobertos** | 19 | ✅ Excelente |

### 🏗️ **Estrutura de Testes**
```
tests/
├── unit/                    # Unit tests (74 tests)
│   ├── test_parsers/        # HeaderParser, QuestionParser, etc.
│   ├── test_services/       # Business services
│   ├── test_validators/     # Input validators
│   └── test_utils/          # Utilities (extract_city, etc.)
├── integration/             # Integration tests (29 tests)
│   ├── test_api/            # API endpoints
│   └── test_azure/          # Azure integration
├── fixtures/                # Reusable test data
└── debug_scripts/           # Debug scripts (16 tests)
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
| **POST** | `/analyze_document` | Uploads and analyzes a document |

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

## 🔄 Recent Updates (July 2025)

### ✅ **New Features**
- **Professional Exception Handling**: Enterprise-grade exception system with custom hierarchy
- **Structured Logging**: JSON-formatted logging with request context tracking
- **Automatic Error Handling**: `@handle_exceptions` decorator for clean controller code
- **Project Cleanup**: Removed unused files and standardized documentation

### 🛠️ **Technical Improvements**
- Implemented `SmartQuestException` hierarchy with automatic HTTP response conversion
- Added `StructuredLogger` with JSON formatting and request context
- Reorganized project structure and removed empty/unused files
- Standardized all documentation in English
- Enhanced test coverage with 169 passing tests (100% success rate)
- Improved code maintainability with clean separation of concerns

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
