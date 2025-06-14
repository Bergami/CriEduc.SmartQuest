# SmartQuest

**SmartQuest** is a microservice of the CriEduc ecosystem, designed to intelligently extract, classify, and analyze educational assessments (exams, tests, quizzes) provided in PDF format. Its goal is to provide automated insights about the structure and content of educational materials using natural language processing and artificial intelligence.

## 📌 Features

- Upload and process school assessments (PDF)
- Extract questions and answer choices
- Identify relevant subjects/topics covered in each question
- Classify question types (e.g. multiple choice, open-ended)
- Generate potential feedback or commentary (optional/future)
- Provide results in structured, machine-readable formats (JSON, etc.)

## 🧠 Use Cases

- Educational platforms looking to automate test analysis
- Teachers and schools that want quick classification of learning objectives
- Data analysts wanting to visualize the focus areas of their assessments

## 🧱 Project Structure

```text
📁 CriEduc.SmartQuest/
│
├── 🛠️ .vscode/                      
│   └── 🐞 launch.json                # Configuração de debug (VS Code)
│
├── 🚀 app/                           # Código da aplicação (FastAPI)
│   ├── 🏁 main.py                    # Ponto de entrada da API
│   ├── 📦 __init__.py
│
│   ├── 🌐 api/                       # Rotas e controladores
│   │   ├── 📦 __init__.py            # Monta o APIRouter principal
│   │   ├── ❤️ health_controller.py   # Rota: GET /health
│   │   └── 🧠 analyze_controller.py  # Rota: POST /analyze
│
│   ├── 🧾 schemas/                   # DTOs (entrada e saída)
│   │   └── 📂 analyze_document/
│   │       └── 📄 upload.py          # UploadRequest & Response
│
│   ├── 🧠 services/                  # Lógica de negócio e orquestração
│   ├── 🏗️ models/                    # Entidades do domínio / ORM
│   ├── ⚙️ core/                      # Configs, middlewares, utils
│   ├── 📚 extractors/                # Leitura de PDFs, OCR, parser de texto
│   └── 🤖 ia/                        # Modelos de IA e classificação de assuntos
│
├── 🧪 tests/                         # Testes unitários e de integração
├── 📂 data/                          # Arquivos de entrada para testes (PDFs etc.)
├── 📓 notebooks/                     # Experimentações (ML, NLP, protótipos)
├── 📦 requirements.txt               # Dependências do projeto
├── 📘 README.md                      # Documentação inicial
└── 🔐 .env                           # Variáveis de ambiente (tokens, configs)


## 🛠️ Tech Stack

- **Python 3.13+** — tested on version 3.13.4
- **FastAPI** — for building RESTful APIs
- **pdfplumber / PyMuPDF** — PDF reading and layout extraction
- **spaCy / Transformers / Tesseract** — NLP, semantic analysis, OCR (when necessary)
- **Pydantic** — request/response validation and data modeling
- **Pytest** — testing framework

## 🚀 Getting Started

> Coming soon: setup instructions and example usage...

## 📚 Future Roadmap

- [ ] Classification of question topics with LLMs
- [ ] Integration with CriEduc core platform via REST
- [ ] Dashboard for previewing parsed content
- [ ] Support for scanned PDF with OCR fallback
- [ ] Auto-detection of difficulty levels

## 💡 Inspiration

SmartQuest is part of a larger vision that began with [CriEduc](https://repositorio.ufes.br/items/55cebe33-b582-4c95-818e-dc661346fab5/full), an educational platform created during a Master's thesis to support georeferenced and interactive learning experiences.

## 👨‍💻 Author

Created by **Wander Vinicius Bergami** as part of the CriEduc ecosystem.  
Let’s build the future of smart education.
