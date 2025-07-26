from typing import List, Dict, Any
from fastapi import HTTPException
from datetime import datetime

class SmartQuestException(Exception):
    """Classe base para exceções do SmartQuest"""
    
    def __init__(self, message: str, status_code: int = 500, error_type: str = "generic_error", context: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_http_exception(self) -> HTTPException:
        """Converte para HTTPException do FastAPI"""
        detail = {
            "error": self.error_type,
            "message": self.message,
            "type": self.error_type,
            "timestamp": self.timestamp
        }
        
        if self.context:
            detail["context"] = self.context
            
        return HTTPException(
            status_code=self.status_code,
            detail=detail
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte exceção para dicionário (útil para logs)"""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "timestamp": self.timestamp
        }

class ValidationException(SmartQuestException):
    """Exceção base para erros de validação"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["invalid_value"] = str(value)
            
        super().__init__(
            message=message,
            status_code=422,
            error_type="validation_error",
            context=context
        )

class InvalidDocumentFormatException(ValidationException):
    def __init__(self, received_format: str = None):
        context = {"expected_format": "PDF"}
        if received_format:
            context["received_format"] = received_format
            
        super().__init__(
            message="Only PDF files are supported",
            field="file",
            value=received_format
        )
        # Atualiza contexto após construção do pai
        self.context.update(context)

class MissingFileException(ValidationException):
    def __init__(self):
        super().__init__(
            message="No file was provided",
            field="file",
            value=None
        )

class InvalidEmailException(ValidationException):
    def __init__(self, email: str = None):
        super().__init__(
            message="Invalid email format.",
            field="email",
            value=email
        )

class MultipleValidationException(ValidationException):
    def __init__(self, errors: List[str]):
        super().__init__(
            message=f"Multiple validation errors: {', '.join(errors)}",
            field="multiple"
        )
        self.context["validation_errors"] = errors
    
    @property 
    def detail(self):
        """Propriedade para compatibilidade com testes antigos"""
        return {"errors": self.context["validation_errors"]}

class DocumentProcessingError(SmartQuestException):
    """Exception for errors in document processing"""
    
    def __init__(self, message: str, provider: str = "unknown", operation: str = "processing"):
        context = {
            "provider": provider,
            "operation": operation
        }
        
        super().__init__(
            message=f"Document processing failed ({provider}): {message}",
            status_code=500,
            error_type="document_processing_error",
            context=context
        )

class AzureServiceError(DocumentProcessingError):
    """Erro específico dos serviços Azure"""
    
    def __init__(self, message: str, azure_error_code: str = None):
        context = {"azure_error_code": azure_error_code} if azure_error_code else {}
        
        super().__init__(
            message=message,
            provider="azure_document_intelligence",
            operation="document_analysis"
        )
        self.context.update(context)

class MockDataError(SmartQuestException):
    """Erro relacionado a dados mock"""
    
    def __init__(self, message: str, mock_file: str = None):
        context = {"mock_file": mock_file} if mock_file else {}
        
        super().__init__(
            message=f"Mock data error: {message}",
            status_code=500,
            error_type="mock_data_error",
            context=context
        )