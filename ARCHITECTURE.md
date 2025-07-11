# SmartQuest Architecture

## 🏗️ **Architecture Overview**

SmartQuest is a microservice designed to intelligently extract, classify, and analyze educational assessments (PDFs) using Azure Document Intelligence and advanced parsing techniques. The system is built with a modular, extensible architecture that allows for easy integration of new document processing providers.

## 📋 **Core Components**

### **1. Document Extraction Abstraction Layer**
- `DocumentExtractionInterface` - Base contract for all extraction providers
- `TextNormalizer` - Centralized text cleaning and normalization
- `DocumentExtractionFactory` - Provider management and selection

### **2. Provider Adapters**
- `AzureExtractionAdapter` - Azure Document Intelligence integration
- *Future*: `TesseractAdapter`, `GoogleVisionAdapter`, etc.

### **3. Document Analysis Pipeline**
- `AnalyzeService` - Main orchestration service
- `HeaderParser` - Exam metadata extraction
- `QuestionParser` - Question and context block detection
- `ContextQuestionMapper` - Intelligent question-context association

### **4. Specialized Parsers**
- **Header Parser**: Modular extraction of exam metadata
- **Question Parser**: Context blocks and question detection
- **Context Detection**: Image and text context identification

## 🧱 **Project Structure**

### **Services Layer** (`app/services/`)
```
services/
├── base/                           # Core interfaces and utilities
│   ├── document_extraction_interface.py # Provider interface
│   └── text_normalizer.py          # Text cleaning utilities
├── adapters/                       # Provider implementations
│   └── azure_extraction_adapter.py # Azure Document Intelligence
├── analyze_service.py              # Main analysis orchestration
├── azure_document_intelligence_service.py # Legacy Azure service
├── document_extraction_factory.py  # Provider factory
└── health_service.py              # Health check service
```

### **Parsers Layer** (`app/parsers/`)
```
parsers/
├── header_parser/                  # Exam metadata extraction
│   ├── base.py                     # Entry point
│   ├── parse_*.py                  # Individual field parsers
│   └── ...
└── question_parser/                # Question and context parsing
    ├── base.py                     # Entry point
    ├── detect_context_blocks.py    # Context block detection
    ├── detect_questions.py         # Question identification
    ├── match_context_to_questions.py # Context-question mapping
    └── extract_alternatives_*.py   # Answer choice extraction
```

### **API Layer** (`app/api/` and `app/controllers/`)
```
api/
└── routers.py                      # FastAPI route definitions

controllers/
├── analyze.py                      # Document analysis endpoints
└── health.py                      # Health check endpoints
```

## 🔧 **Usage**

### **Basic Usage**
```python
from app.services.document_extraction_factory import DocumentExtractionFactory

# Get default provider
extractor = DocumentExtractionFactory.get_provider()

# Extract document data
result = await extractor.extract_document_data(file)
```

### **Specific Provider**
```python
# Use specific provider
azure_extractor = DocumentExtractionFactory.get_provider("azure")
result = await azure_extractor.extract_document_data(file)
```

### **Environment Configuration**
```bash
# Set preferred provider (optional, defaults to azure)
DOCUMENT_EXTRACTION_PROVIDER=azure

# Azure credentials
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="your-endpoint"
AZURE_DOCUMENT_INTELLIGENCE_KEY="your-key"
```

## 📊 **Standardized Output Format**

All providers return a consistent structure:

```python
{
    "text": "Extracted document text",
    "confidence": 0.95,  # 0.0 to 1.0
    "page_count": 2,
    "metadata": {
        "provider": "azure",
        "raw_metadata": {...}  # Provider-specific data
    }
}
```

## 📊 **Data Structure**

### **API Response Format**
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
    "date": null
  },
  "context_blocks": [
    {
      "id": 0,
      "type": ["text"],
      "statement": "Após ler atentamente o texto a seguir, responda as três próximas questões.",
      "title": "FEIJÕES OU PROBLEMAS?",
      "paragraphs": ["Reza a lenda que um monge..."],
      "hasImage": false
    },
    {
      "id": 1, 
      "type": ["text", "image"],
      "statement": "Analise a imagem abaixo",
      "title": "FAVOR NÃO DEXAR OBIGETOS NO CORREDOR",
      "paragraphs": [],
      "hasImage": true
    }
  ],
  "questions": [
    {
      "number": 1,
      "question": "Nesse texto, o discípulo que venceu a prova porque",
      "alternatives": [
        {"letter": "A", "text": "colocou o feijão em um sapato."},
        {"letter": "B", "text": "cozinhou o feijão."},
        {"letter": "C", "text": "desceu a montanha correndo."},
        {"letter": "D", "text": "sumiu da vista do oponente."},
        {"letter": "E", "text": "tirou seu sapato."}
      ],
      "context_id": 0
    }
  ]
}
```

### **Context Block Types**
- **`["text"]`**: Pure text context blocks
- **`["image"]`**: Pure image context blocks  
- **`["text", "image"]`**: Mixed blocks with instruction text and image content

## 🧹 **Text Normalization**

The `TextNormalizer` handles:

### **Universal Cleaning**
- Excessive whitespace removal
- Empty line removal
- Quote and dash normalization

### **Provider-Specific Cleaning**
- **Azure**: Removes `:selected:` and `:unselected:` marks
- **Future providers**: Add specific cleaning rules as needed

## 🔄 **Adding New Providers**

### **1. Create Adapter**
```python
from app.services.base.document_extraction_interface import DocumentExtractionInterface

class NewProviderAdapter(DocumentExtractionInterface):
    async def extract_document_data(self, file: UploadFile) -> Dict[str, Any]:
        # Implementation here
        pass
    
    def get_provider_name(self) -> str:
        return "new_provider"
    
    def is_available(self) -> bool:
        # Check if provider is configured
        pass
```

### **2. Register in Factory**
```python
# In DocumentExtractionFactory
def _register_new_provider(cls):
    try:
        adapter = NewProviderAdapter()
        if adapter.is_available():
            cls._providers["new_provider"] = adapter
    except Exception as e:
        logger.warning(f"Failed to register new provider: {e}")
```

### **3. Add Text Cleaning Rules**
```python
# In TextNormalizer._apply_provider_specific_cleaning
elif provider_name == "new_provider":
    # Add provider-specific cleaning
    pass
```

## 🎯 **Benefits**

### **Flexibility**
- Easy provider switching via configuration
- Automatic fallback to available providers
- No changes needed in core application logic

### **Maintainability**
- Centralized text processing logic
- Consistent error handling
- Clear separation of concerns

### **Extensibility**
- Simple process to add new providers
- Standardized interface contract
- Provider-specific optimizations

## 🧪 **Testing**

### **Available Test Files**
```bash
# Test Azure AI integration (detailed)
python test_azure_detailed.py

# Test Azure AI integration (basic)  
python test_azure_only.py
```

### **API Testing**
```bash
# Test API with mock data
curl -X POST "http://127.0.0.1:8000/analyze/analyze_document?email=test@example.com&use_mock=true"

# Test health endpoint
curl -X GET "http://127.0.0.1:8000/health"
```

## 📝 **Migration Notes**

### **From Direct Azure Usage**
The new system is **backwards compatible**. Existing code continues to work without changes, but now uses the abstraction layer internally.

### **Environment Variables**
```bash
# Optional: Set preferred provider
DOCUMENT_EXTRACTION_PROVIDER=azure  # Default

# Existing Azure configs still work
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="..."
AZURE_DOCUMENT_INTELLIGENCE_KEY="..."
```

## 🚀 **Key Features**

### **Document Processing Pipeline**
1. **Document Upload** - FastAPI endpoint receives PDF files
2. **Text Extraction** - Azure Document Intelligence extracts raw text
3. **Header Parsing** - Modular extraction of exam metadata
4. **Context Detection** - Identifies text blocks and image contexts
5. **Question Detection** - Locates questions and answer choices
6. **Context Mapping** - Intelligently links questions to contexts
7. **Response Building** - Structured JSON output

### **Context Block Intelligence**
- **Dynamic Type Detection**: Automatically identifies `["text"]`, `["image"]`, or `["text", "image"]` blocks
- **Image Block Grouping**: Groups instruction text with extracted image content
- **Deduplication**: Removes duplicate context blocks
- **Smart Ordering**: Orders blocks by position in document

### **Question-Context Mapping**
- **Pattern Recognition**: Detects introduction patterns like "responda as três próximas questões"
- **Image Question Handling**: Special logic for image-related questions
- **Proximity Analysis**: Maps questions to nearest relevant context
- **Validation**: Ensures all questions have appropriate context assignments

## 🎯 **Current Implementation Status**

### ✅ **Completed Features**
- Document extraction abstraction layer
- Azure Document Intelligence integration
- Modular header parsing (all fields)
- Context block detection and classification
- Question detection and parsing
- Intelligent context-question mapping
- Image block special handling
- Mock data support for testing
- Comprehensive API endpoints

### 🚧 **Architecture Decisions**
- **Microservice Design**: Single-responsibility service
- **Provider Abstraction**: Easy integration of new document processors
- **Modular Parsing**: Each parser handles specific document elements
- **Intelligent Mapping**: Context-aware question association
- **Type Safety**: Pydantic models for request/response validation
