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
| **Python 3.13+** | Tested on version 3.13.4 |
| **FastAPI** | High-performance web framework for building RESTful APIs |
| **pdfplumber / PyMuPDF** | PDF reading and layout extraction |
| **spaCy / Transformers / Tesseract** | NLP, semantic analysis, OCR (optional) |
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

📌 3. Install Dependencies

````` 
pip install -r requirements.txt
````` 
📌 4. Start the API

````` 
uvicorn app.main:app --reload
````` 

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
