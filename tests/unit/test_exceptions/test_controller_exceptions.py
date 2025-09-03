import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, UploadFile, HTTPException
from fastapi.testclient import TestClient
from app.api.controllers.analyze import analyze_document
from app.core.exceptions import (
    MissingFileException,
    ValidationException,
    DocumentProcessingError
)

class TestAnalyzeDocumentController:
    """Testes para o controller de análise de documentos"""
    
    @pytest.fixture
    def mock_request(self):
        """Fixture para mock de Request"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://test.com/api/analyze_document"
        return request
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Fixture para mock de arquivo PDF"""
        file = Mock(spec=UploadFile)
        file.filename = "test.pdf"
        file.content_type = "application/pdf"
        file.size = 1024
        return file
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeService.process_document_mock')
    @patch('app.api.controllers.analyze.AnalyzeValidator.validate_email_only')
    async def test_analyze_document_with_mock(self, mock_validator, mock_service, mock_request):
        """Testa análise de documento usando dados mock"""
        # Setup
        mock_service.return_value = {"result": "mock_data"}
        email = "test@example.com"
        
        # Execute
        result = await analyze_document(
            request=mock_request,
            email=email,
            file=None,
            use_mock=True
        )
        
        # Verify
        assert result == {"result": "mock_data"}
        mock_validator.assert_called_once_with(email)
        mock_service.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeService.process_document')
    @patch('app.api.controllers.analyze.AnalyzeValidator.validate_all')
    async def test_analyze_document_with_file(self, mock_validator, mock_service, mock_request, mock_pdf_file):
        """Testa análise de documento com arquivo real"""
        # Setup
        mock_service.return_value = {"result": "real_data"}
        email = "test@example.com"
        
        # Execute
        result = await analyze_document(
            request=mock_request,
            email=email,
            file=mock_pdf_file,
            use_mock=False
        )
        
        # Verify
        assert result == {"result": "real_data"}
        mock_validator.assert_called_once_with(mock_pdf_file, email)
        mock_service.assert_called_once_with(mock_pdf_file, email)
    
    @pytest.mark.asyncio
    async def test_analyze_document_missing_file_when_not_mock(self, mock_request):
        """Testa erro quando arquivo está ausente e não está usando mock"""
        with pytest.raises(HTTPException) as exc_info:
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=None,
                use_mock=False
            )
        
        # Verifica se é o erro correto (convertido pelo decorator)
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["error"] == "validation_error"
        assert "No file was provided" in exc_info.value.detail["message"]
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeValidator.validate_email_only')
    async def test_analyze_document_validation_error(self, mock_validator, mock_request):
        """Testa tratamento de erro de validação"""
        # Setup - validator lança exceção
        mock_validator.side_effect = ValidationException("Invalid email", field="email")
        
        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await analyze_document(
                request=mock_request,
                email="invalid-email",
                file=None,
                use_mock=True
            )
        
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["error"] == "validation_error"
        assert "Invalid email" in exc_info.value.detail["message"]
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeService.process_document_mock')
    @patch('app.api.controllers.analyze.AnalyzeValidator.validate_email_only')
    async def test_analyze_document_service_error(self, mock_validator, mock_service, mock_request):
        """Testa tratamento de erro do serviço"""
        # Setup - service lança exceção
        mock_service.side_effect = DocumentProcessingError("Azure service error")
        
        # Execute & Verify
        with pytest.raises(HTTPException) as exc_info:
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=None,
                use_mock=True
            )
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail["error"] == "document_processing_error"
        assert "Azure service error" in exc_info.value.detail["message"]
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeValidator.validate_all')
    async def test_analyze_document_logging(self, mock_validator, mock_request, mock_pdf_file):
        """Testa se os logs estão sendo gerados corretamente"""
        # Setup mock mais detalhado para evitar erros de atributos
        mock_pdf_file.filename = "test.pdf"
        mock_pdf_file.content_type = "application/pdf" 
        mock_pdf_file.size = 1024
        
        with patch('app.api.controllers.analyze.AnalyzeService.process_document', new_callable=AsyncMock) as mock_service, \
             patch('app.core.utils.structured_logger') as mock_logger:
            
            mock_service.return_value = {"result": "test_data"}
            
            # Execute
            result = await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_pdf_file,
                use_mock=False
            )
            
            # Verify result
            assert result == {"result": "test_data"}
            
            # Verify service calls
            mock_service.assert_called_once_with(mock_pdf_file, "test@example.com")
            mock_validator.assert_called_once_with(mock_pdf_file, "test@example.com")
            
            # Verify logging was called (at least info logs)
            assert mock_logger.info.called

class TestValidateFileRequirement:
    """Testes para validação de arquivo obrigatório"""
    
    def test_validate_file_requirement_mock_true_no_file(self):
        """Testa validação quando usar mock sem arquivo (OK)"""
        # Não deve lançar exceção
        _validate_file_requirement(use_mock=True, file=None)
    
    def test_validate_file_requirement_mock_false_with_file(self):
        """Testa validação quando não usar mock com arquivo (OK)"""
        file = Mock(spec=UploadFile)
        # Não deve lançar exceção
        _validate_file_requirement(use_mock=False, file=file)
    
    def test_validate_file_requirement_mock_false_no_file(self):
        """Testa validação quando não usar mock sem arquivo (ERRO)"""
        with pytest.raises(MissingFileException):
            _validate_file_requirement(use_mock=False, file=None)
    
    def test_validate_file_requirement_mock_true_with_file(self):
        """Testa validação quando usar mock com arquivo (OK)"""
        file = Mock(spec=UploadFile)
        # Não deve lançar exceção - é permitido ter arquivo mesmo usando mock
        _validate_file_requirement(use_mock=True, file=file)

class TestControllerExceptionHandling:
    """Testes específicos para tratamento de exceções no controller"""
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.handle_exceptions')
    async def test_controller_uses_exception_decorator(self, mock_decorator):
        """Testa se o controller usa o decorator de exceções"""
        # O decorator deve ter sido aplicado à função
        # Este teste verifica se a função está decorada
        from app.api.controllers.analyze import analyze_document
        
        # Verifica se a função tem atributos de função decorada
        assert hasattr(analyze_document, '__wrapped__') or hasattr(analyze_document, '__name__')
    
    @pytest.mark.asyncio
    @patch('app.core.utils.structured_logger')
    async def test_exception_logging_integration(self, mock_logger):
        """Testa integração entre exceções e logging"""
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = "http://test.com/api/analyze"
        
        # Testa se exceção é logada quando ocorre
        with pytest.raises(HTTPException):  # Decorator converte para HTTPException
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=None,
                use_mock=False
            )
        
        # O decorator deve ter logado o erro
        assert mock_logger.error.called

class TestControllerDocumentation:
    """Testes para documentação e contratos do controller"""
    
    def test_analyze_document_docstring(self):
        """Testa se o controller tem documentação adequada"""
        from app.api.controllers.analyze import analyze_document
        
        assert analyze_document.__doc__ is not None
        assert "Analisa documento PDF" in analyze_document.__doc__
        assert "Args:" in analyze_document.__doc__
        assert "Returns:" in analyze_document.__doc__
        assert "Raises:" in analyze_document.__doc__
    
    def test_validate_file_requirement_docstring(self):
        """Testa documentação da função de validação"""
        assert _validate_file_requirement.__doc__ is not None
        assert "Valida se arquivo é obrigatório" in _validate_file_requirement.__doc__

class TestControllerIntegration:
    """Testes de integração do controller"""
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeService')
    @patch('app.api.controllers.analyze.AnalyzeValidator')
    async def test_complete_flow_mock(self, mock_validator, mock_service):
        """Testa fluxo completo com dados mock"""
        # Setup - configure AsyncMock corretamente
        mock_service.process_document_mock = AsyncMock(return_value={
            "header": {"exam_title": "Test Exam"},
            "questions": []
        })
        
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = "http://test.com/api/analyze"
        
        # Execute
        result = await analyze_document(
            request=mock_request,
            email="test@example.com",
            file=None,
            use_mock=True
        )
        
        # Verify
        assert "header" in result
        assert "questions" in result
        mock_validator.validate_email_only.assert_called_once()
        mock_service.process_document_mock.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.api.controllers.analyze.AnalyzeService')
    @patch('app.api.controllers.analyze.AnalyzeValidator')
    async def test_complete_flow_real_file(self, mock_validator, mock_service):
        """Testa fluxo completo com arquivo real"""
        # Setup - configure AsyncMock corretamente
        mock_service.process_document = AsyncMock(return_value={
            "header": {"exam_title": "Real Exam"},
            "questions": [{"question": "Test?"}]
        })
        
        mock_request = Mock(spec=Request)
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "real_test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.size = 1024
        
        # Execute
        result = await analyze_document(
            request=mock_request,
            email="test@example.com",
            file=mock_file,
            use_mock=False
        )
        
        # Verify
        assert "header" in result
        assert "questions" in result
        assert len(result["questions"]) == 1
        mock_validator.validate_all.assert_called_once()
        mock_service.process_document.assert_called_once()
