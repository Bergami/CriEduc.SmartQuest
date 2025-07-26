# SmartQuest Architecture

## 🏗️ **Architecture Overview**

SmartQuest is a microservice designed to intelligently extract, classify, and analyze educational assessments (PDFs) using Azure Document Intelligence and advanced parsing techniques. The system is built with a modular, extensible architecture that allows for easy integration of new document processing providers.

## 📋 **Core Components**

### **1. Document Provider Layer**
- `BaseDocumentProvider` - Abstract base class for document analysis providers
- `AzureDocumentIntelligenceService` - Azure Document Intelligence implementation
- `DocumentStorageService` - Generic document artifact storage service
- *Future*: `GoogleVisionProvider`, `TesseractProvider`, etc.

### **2. Document Extraction Abstraction Layer**
- `DocumentExtractionInterface` - Base contract for all extraction providers
- `TextNormalizer` - Centralized text cleaning and normalization
- `DocumentExtractionFactory` - Provider management and selection

### **3. Provider Adapters**
- `AzureExtractionAdapter` - Azure Document Intelligence integration
- *Future*: `TesseractAdapter`, `GoogleVisionAdapter`, etc.

### **4. Document Analysis Pipeline**
- `AnalyzeService` - Main orchestration service with image categorization
- `HeaderParser` - Exam metadata extraction with image support
- `QuestionParser` - Question and context block detection
- `ContextQuestionMapper` - Intelligent question-context association

### **5. Specialized Parsers**
- **Header Parser**: Modular extraction of exam metadata with image categorization
- **Question Parser**: Context blocks and question detection
- **Context Detection**: Image and text context identification
- **Image Processing**: Header vs content image categorization using PyMuPDF

## 🧱 **Project Structure**

### **Services Layer** (`app/services/`)
```
services/
├── base/                           # Core interfaces and utilities
│   ├── document_extraction_interface.py # Provider interface
│   └── text_normalizer.py          # Text cleaning utilities
├── adapters/                       # Provider implementations
│   └── azure_extraction_adapter.py # Azure Document Intelligence
├── providers/                      # Document provider implementations
│   └── base_document_provider.py   # Abstract document provider
├── storage/                        # Document storage services
│   └── document_storage_service.py # Generic document artifact storage
├── analyze_service.py              # Main analysis orchestration with image categorization
├── azure_document_intelligence_service.py # Azure provider implementation
├── document_extraction_factory.py  # Provider factory
├── adapters/                       # Provider adapters
├── base/                          # Base interfaces and utilities
├── providers/                     # Document provider implementations
├── storage/                       # Document storage services
└── utils/                         # Service utilities
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

### **Core Infrastructure** (`app/core/`)
```
core/
├── config.py                       # Application configuration
├── exceptions.py                   # Professional exception handling system
├── logging.py                      # Structured logging implementation
└── utils.py                        # Utilities and exception decorator
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

## �️ **Storage Architecture**

### **DocumentStorageService**
Generic storage service that handles document artifacts independently of specific providers:

```python
from app.services.storage.document_storage_service import DocumentStorageService

# Initialize storage service
storage_service = DocumentStorageService()

# Save analysis response
await storage_service.save_analysis_response(document_id, response_data)

# Save extracted images
await storage_service.save_images(document_id, images)

# Save extracted text
await storage_service.save_text(document_id, text_content)

# Save original document
await storage_service.save_original_document(document_id, file_content)
```

### **BaseDocumentProvider**
Abstract base class for document analysis providers with integrated storage:

```python
from app.services.providers.base_document_provider import BaseDocumentProvider

class CustomDocumentProvider(BaseDocumentProvider):
    def __init__(self, storage_service: DocumentStorageService):
        super().__init__(storage_service)
    
    async def analyze_document(self, file: UploadFile, document_id: str) -> Dict[str, Any]:
        # Implement document analysis
        result = await self._analyze_document_content(file)
        
        # Storage is handled automatically by base class
        return result
```

### **Benefits of Storage Architecture**
- **Provider Independence**: Storage logic is separated from document analysis
- **Future-Ready**: Easy migration to database storage systems
- **Consistent Interface**: All providers use the same storage methods
- **Artifact Management**: Organized storage of responses, images, text, and original documents

## �🔄 **Adding New Providers**

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

## 🛡️ **Professional Exception Handling System**

The SmartQuest application implements a comprehensive, enterprise-grade exception handling system designed for production reliability and maintainability.

### **Exception Hierarchy**
```python
SmartQuestException (Base)
├── ValidationException          # Input validation errors
├── DocumentProcessingError      # Document processing failures
├── AzureServiceError           # Azure service specific errors
├── InvalidEmailException       # Email validation errors
├── FileProcessingError         # File operation errors
└── ConfigurationError          # Configuration issues
```

### **Structured Logging**
The system uses JSON-formatted structured logging for enterprise monitoring:

```python
# Automatic request context tracking
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "ERROR",
    "message": "Document processing failed",
    "request_id": "req_12345",
    "user_email": "user@example.com",
    "exception_type": "DocumentProcessingError",
    "exception_details": {...},
    "stack_trace": "..."
}
```

### **Automatic Exception Handling**
Controllers use the `@handle_exceptions` decorator for clean, consistent error handling:

```python
from app.core.utils import handle_exceptions

@handle_exceptions
async def analyze_document(file: UploadFile, email: str):
    # Business logic only - exceptions handled automatically
    return await service.process_document(file, email)
```

### **Benefits**
- **Consistent Error Responses**: All errors return standardized HTTP responses
- **Automatic Logging**: Exceptions are logged with full context automatically
- **Clean Controllers**: Business logic separated from error handling
- **Production Ready**: Structured logs for monitoring and debugging
- **Type Safety**: Custom exceptions provide clear error semantics

### **Usage Example**
```python
# Raising business exceptions
if not email_validator.is_valid(email):
    raise InvalidEmailException(f"Invalid email format: {email}")

# Automatic conversion to HTTP response
# Returns: {"detail": "Invalid email format: user@invalid", "error_code": "INVALID_EMAIL"}
```

## 🎯 **Benefits**

### **Flexibility**
- Easy provider switching via configuration
- Automatic fallback to available providers
- No changes needed in core application logic

### **Maintainability**
- Centralized text processing logic
- Professional exception handling with structured logging
- Clear separation of concerns
- Clean controller code with automatic error handling

### **Extensibility**
- Simple process to add new providers
- Standardized interface contract
- Provider-specific optimizations

### **Enterprise Reliability**
- Comprehensive exception hierarchy for all error scenarios
- Structured JSON logging for monitoring and debugging
- Automatic error handling with consistent HTTP responses
- Production-ready error management system

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
3. **Image Extraction** - PyMuPDF extracts images with positional data
4. **Header Parsing** - Modular extraction of exam metadata with image categorization
5. **Context Detection** - Identifies text blocks and image contexts
6. **Question Detection** - Locates questions and answer choices
7. **Context Mapping** - Intelligently links questions to contexts
8. **Response Building** - Structured JSON output with images

### **Image Processing Features**
- **Header Image Categorization**: Automatically identifies images in document headers
- **Position-Based Classification**: Uses Y-coordinate positioning for image categorization
- **Base64 Encoding**: Images are encoded for API transmission
- **Metadata Preservation**: Maintains image position and size information

### **Storage Architecture**
- **Provider-Agnostic Storage**: Generic `DocumentStorageService` supports multiple backends
- **Artifact Management**: Stores analysis responses, images, text, and original documents
- **Future-Ready**: Prepared for database migration from current filesystem approach

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
- **Header image categorization and extraction**
- Context block detection and classification
- Question detection and parsing
- Intelligent context-question mapping
- Image block special handling
- **Provider-agnostic storage architecture**
- **Document artifact storage service**
- **Professional exception handling system**
- **Structured logging with JSON formatting**
- **Automatic error handling decorators**
- Mock data support for testing
- Comprehensive API endpoints

### 🚧 **Architecture Decisions**
- **Microservice Design**: Single-responsibility service
- **Provider Abstraction**: Easy integration of new document processors
- **Storage Abstraction**: Generic storage service for future database migration
- **Exception Handling**: Enterprise-grade exception system with structured logging
- **Error Management**: Automatic exception handling with consistent responses
- **Image Processing**: Position-based header image categorization
- **Modular Parsing**: Each parser handles specific document elements
- **Intelligent Mapping**: Context-aware question association
- **Type Safety**: Pydantic models for request/response validation

### 🔧 **Recent Updates (December 2024)**
- **Added header image support**: Images are now categorized and included in header metadata
- **Implemented storage service**: Created provider-agnostic storage architecture
- **Refactored Azure service**: Now inherits from `BaseDocumentProvider`
- **Enhanced image processing**: Added position-based categorization logic
- **Professional exception handling**: Implemented enterprise-grade exception system
- **Structured logging**: Added JSON-formatted logging with request context
- **Automatic error handling**: Created decorators for clean controller code
- **Cleaned up unused code**: Removed unused schemas and obsolete files
