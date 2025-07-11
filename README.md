## 🏗️ SmartQuest

SmartQuest is a microservice within the CriEduc ecosystem, designed to intelligently extract, classify, and analyze educational assessments (exams, tests, quizzes) provided in PDF format. Its goal is to provide automated insights into the structure and content of educational materials using natural language processing and artificial intelligence


## 📌 Features

| ✅ Feature | Description |
|-----------|------------|
| **Upload assessments** | Process educational assessments in **PDF format** |
| **Extract questions & answers** | Identify and extract **questions & answer choices** from documents |
| **Detect subjects/topics** | Recognize relevant **subjects and topics** covered in each question |
| **Classify question types** | Identify question formats like **multiple-choice, open-ended**, etc. |
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
│   │   ├── 🧠 analyze_service.py    # Main analysis orchestration
│   │   ├── ☁️ azure_document_intelligence_service.py # Azure AI integration
│   │   └── ❤️ health_service.py     # Health check service
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
├── 🏗️ ARCHITECTURE.md               # Architecture documentation
├── ⚙️ CONFIG.md                     # Configuration guide
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

```
app/parsers/header_parser/
├── base.py            # Entry point used by services
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

## 🛠️ Tech Stack


| ✅ Technology | Description |
|--------------|------------|
| **Python 3.9+** | Tested on versions 3.9+ |
| **FastAPI** | High-performance web framework for building RESTful APIs |
| **Azure AI Document Intelligence** | Cloud-based document processing and extraction |
| **Azure SDK for Python** | Integration with Azure cognitive services |
| **Pydantic** | Request validation and data modeling |
| **Pytest** | Unit testing framework |



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

### Available Test Files
| File | Purpose |
|------|---------|
| `test_azure_detailed.py` | Detailed Azure AI integration testing |
| `test_azure_only.py` | Basic Azure AI integration test |
| `tests/modelo-completo-prova.pdf` | Complete exam test document |
| `tests/RetornoProcessamento.json` | Mock response data for testing |

### Running Tests
```powershell
# Test Azure AI integration (detailed)
python test_azure_detailed.py

# Test Azure AI integration (basic)
python test_azure_only.py

# Test API with mock data
curl -X POST "http://127.0.0.1:8000/analyze/analyze_document?email=test@example.com&use_mock=true"
```

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


## 📚 Future Roadmap

🔹 Short-Term Improvements
- [ ] Integrate SmartQuest with the CriEduc core platform (REST API)
- [ ] Develop a dashboard for previewing parsed content
🔹 Long-Term Vision
- [ ] Classify question topics using LLMs (Large Language Models)
- [ ] Support scanned PDFs with OCR fallback
- [ ] Implement automatic difficulty level detectio

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
