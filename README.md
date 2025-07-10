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
│   └── 🐞 launch.json               # Debugging configuration for FastAPI
│
├── 🚀 app/                          # Main application code (FastAPI)
│   ├── 🏁 main.py                   # API entry point
│   ├── 📦 __init__.py
│
│   ├── 🌐 api/                      # API routes and controllers
│   │   ├── 📦 __init__.py           # Main APIRouter assembly
│   │   ├── ❤️ health_controller.py  # Endpoint: GET /health
│   │   └── 🧠 analyze_controller.py # Endpoint: POST /analyze_document
│
│   ├── 🧾 schemas/                  # Request/Response DTOs
│   │   └── 📂 analyze_document/     # AnalyzeDocument domain schemas
│   │       └── 📄 upload.py         # Upload request & response schemas
│
│   ├── 🧠 services/                 # Business logic and orchestration
│   ├── 🗂️ parsers/                  # Text parsing utilities
│   │   └── 📂 header_parser/       # Modular exam header extraction
│   ├── 🏗️ models/                   # Domain entities / ORM models
│   ├── ⚙️ core/                     # Configurations, middlewares, utilities
│   ├── 📚 extractors/               # PDF parsing, OCR, text processing
│   └── 🤖 ia/                       # AI models and classification logic
│
├── 🧪 tests/                        # Unit and integration tests
├── 📂 data/                         # Input files for testing (PDFs, etc.)
├── 📓 notebooks/                    # Research and experimentation (ML, NLP)
├── 📦 requirements.txt              # Project dependencies
├── 📘 README.md                     # Documentation
└── 🔐 .env                          # Environment variables (tokens, configs)
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

### Available Test Scripts
| Script | Purpose |
|--------|---------|
| `test_azure_only.py` | Complete Azure AI integration test |
| `tests/test_analyze_service.py` | Unit tests for analyze service |

### Running Tests
```powershell
# Test Azure AI integration
python test_azure_only.py

# Run unit tests
python -m pytest tests/
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
