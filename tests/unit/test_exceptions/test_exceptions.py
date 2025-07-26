import pytest
import json
from datetime import datetime
from fastapi import HTTPException
from app.core.exceptions import (
    SmartQuestException,
    ValidationException,
    InvalidDocumentFormatException,
    MissingFileException,
    InvalidEmailException,
    MultipleValidationException,
    DocumentProcessingError,
    AzureServiceError,
    MockDataError
)

class TestSmartQuestException:
    """Testes para a classe base SmartQuestException"""
    
    def test_basic_exception_creation(self):
        """Testa criação básica de exceção"""
        exception = SmartQuestException("Test message")
        
        assert exception.message == "Test message"
        assert exception.status_code == 500
        assert exception.error_type == "generic_error"
        assert exception.context == {}
        assert isinstance(exception.timestamp, str)
    
    def test_exception_with_custom_parameters(self):
        """Testa exceção com parâmetros customizados"""
        context = {"user_id": "123", "operation": "test"}
        exception = SmartQuestException(
            message="Custom error",
            status_code=400,
            error_type="custom_error",
            context=context
        )
        
        assert exception.message == "Custom error"
        assert exception.status_code == 400
        assert exception.error_type == "custom_error"
        assert exception.context == context
    
    def test_to_http_exception(self):
        """Testa conversão para HTTPException"""
        context = {"field": "email"}
        exception = SmartQuestException(
            message="Test error",
            status_code=422,
            error_type="validation_error",
            context=context
        )
        
        http_exception = exception.to_http_exception()
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == 422
        assert http_exception.detail["error"] == "validation_error"
        assert http_exception.detail["message"] == "Test error"
        assert http_exception.detail["context"] == context
        assert "timestamp" in http_exception.detail
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        context = {"operation": "test"}
        exception = SmartQuestException(
            message="Test message",
            status_code=400,
            error_type="test_error",
            context=context
        )
        
        exception_dict = exception.to_dict()
        
        assert exception_dict["error_type"] == "test_error"
        assert exception_dict["message"] == "Test message"
        assert exception_dict["status_code"] == 400
        assert exception_dict["context"] == context
        assert "timestamp" in exception_dict

class TestValidationException:
    """Testes para ValidationException"""
    
    def test_basic_validation_exception(self):
        """Testa criação básica de ValidationException"""
        exception = ValidationException("Invalid input")
        
        assert exception.message == "Invalid input"
        assert exception.status_code == 422
        assert exception.error_type == "validation_error"
    
    def test_validation_exception_with_field(self):
        """Testa ValidationException com campo específico"""
        exception = ValidationException("Invalid value", field="email", value="invalid-email")
        
        assert exception.context["field"] == "email"
        assert exception.context["invalid_value"] == "invalid-email"
    
    def test_invalid_document_format_exception(self):
        """Testa InvalidDocumentFormatException"""
        exception = InvalidDocumentFormatException("doc")
        
        assert "Only PDF files are supported" in exception.message
        assert exception.context["expected_format"] == "PDF"
        assert exception.context["received_format"] == "doc"
        assert exception.status_code == 422
    
    def test_missing_file_exception(self):
        """Testa MissingFileException"""
        exception = MissingFileException()
        
        assert "No file was provided" in exception.message
        assert exception.context["field"] == "file"
        assert exception.status_code == 422
    
    def test_invalid_email_exception(self):
        """Testa InvalidEmailException"""
        invalid_email = "invalid-email"
        exception = InvalidEmailException(invalid_email)
        
        assert "Invalid email format" in exception.message
        assert exception.context["field"] == "email"
        assert exception.context["invalid_value"] == invalid_email
        assert exception.status_code == 422
    
    def test_multiple_validation_exception(self):
        """Testa MultipleValidationException"""
        errors = ["Invalid email", "Missing file", "Invalid format"]
        exception = MultipleValidationException(errors)
        
        assert "Multiple validation errors" in exception.message
        assert exception.context["validation_errors"] == errors
        assert exception.status_code == 422

class TestDocumentProcessingError:
    """Testes para DocumentProcessingError"""
    
    def test_basic_document_processing_error(self):
        """Testa criação básica de DocumentProcessingError"""
        exception = DocumentProcessingError("Processing failed")
        
        assert "Document processing failed" in exception.message
        assert exception.status_code == 500
        assert exception.error_type == "document_processing_error"
        assert exception.context["provider"] == "unknown"
        assert exception.context["operation"] == "processing"
    
    def test_document_processing_error_with_provider(self):
        """Testa DocumentProcessingError com provedor específico"""
        exception = DocumentProcessingError(
            "API Error", 
            provider="azure", 
            operation="analysis"
        )
        
        assert "Document processing failed (azure)" in exception.message
        assert exception.context["provider"] == "azure"
        assert exception.context["operation"] == "analysis"
    
    def test_azure_service_error(self):
        """Testa AzureServiceError"""
        exception = AzureServiceError("Service unavailable", "AZ001")
        
        assert "Service unavailable" in exception.message
        assert exception.context["provider"] == "azure_document_intelligence"
        assert exception.context["operation"] == "document_analysis"
        assert exception.context["azure_error_code"] == "AZ001"
    
    def test_mock_data_error(self):
        """Testa MockDataError"""
        exception = MockDataError("Mock file not found", "test_mock.json")
        
        assert "Mock data error: Mock file not found" in exception.message
        assert exception.context["mock_file"] == "test_mock.json"
        assert exception.status_code == 500
        assert exception.error_type == "mock_data_error"

class TestExceptionIntegration:
    """Testes de integração do sistema de exceções"""
    
    def test_exception_hierarchy(self):
        """Testa hierarquia de exceções"""
        validation_exc = ValidationException("Test")
        document_exc = DocumentProcessingError("Test")
        
        # Ambas devem herdar de SmartQuestException
        assert isinstance(validation_exc, SmartQuestException)
        assert isinstance(document_exc, SmartQuestException)
        
        # Mas não devem ser do mesmo tipo
        assert not isinstance(validation_exc, DocumentProcessingError)
        assert not isinstance(document_exc, ValidationException)
    
    def test_http_exception_conversion_consistency(self):
        """Testa consistência na conversão para HTTPException"""
        exceptions = [
            ValidationException("Invalid input"),
            DocumentProcessingError("Processing failed"),
            InvalidEmailException("test@invalid")
        ]
        
        for exc in exceptions:
            http_exc = exc.to_http_exception()
            
            assert isinstance(http_exc, HTTPException)
            assert http_exc.status_code == exc.status_code
            assert isinstance(http_exc.detail, dict)
            assert "error" in http_exc.detail
            assert "message" in http_exc.detail
            assert "timestamp" in http_exc.detail
    
    def test_exception_logging_format(self):
        """Testa formato de exceção para logs"""
        context = {"user_id": "123", "file_name": "test.pdf"}
        exception = DocumentProcessingError(
            "Azure service error",
            provider="azure",
            operation="analysis"
        )
        exception.context.update(context)
        
        log_dict = exception.to_dict()
        
        # Deve ser serializável para JSON
        json_str = json.dumps(log_dict, default=str)
        parsed = json.loads(json_str)
        
        assert parsed["error_type"] == "document_processing_error"
        assert parsed["status_code"] == 500
        assert "user_id" in parsed["context"]
        assert "provider" in parsed["context"]
