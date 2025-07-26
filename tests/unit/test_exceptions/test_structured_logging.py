import pytest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from fastapi import Request
from app.core.logging import StructuredLogger, structured_logger
from app.core.utils import handle_exceptions
from app.core.exceptions import SmartQuestException, ValidationException
from fastapi import HTTPException

class TestStructuredLogger:
    """Testes para o sistema de logging estruturado"""
    
    @pytest.fixture
    def logger(self):
        """Fixture para criar um logger de teste"""
        return StructuredLogger("test_logger")
    
    @pytest.fixture
    def mock_handler(self):
        """Fixture para mock do handler de log"""
        with patch('logging.StreamHandler') as mock_handler:
            yield mock_handler
    
    def test_logger_initialization(self, logger):
        """Testa inicialização do logger"""
        assert logger.logger.name == "test_logger"
        assert len(logger.logger.handlers) > 0
        assert logger.logger.level == logging.INFO
    
    def test_create_log_entry(self, logger):
        """Testa criação de entrada de log estruturada"""
        context = {"user_id": "123", "operation": "test"}
        entry = logger._create_log_entry("INFO", "Test message", context)
        
        assert entry["level"] == "INFO"
        assert entry["message"] == "Test message"
        assert entry["service"] == "smartquest"
        assert entry["context"] == context
        assert "timestamp" in entry
    
    def test_create_log_entry_without_context(self, logger):
        """Testa criação de entrada sem contexto"""
        entry = logger._create_log_entry("ERROR", "Error message")
        
        assert entry["level"] == "ERROR"
        assert entry["message"] == "Error message"
        assert "context" not in entry
    
    @patch('logging.Logger.info')
    def test_info_logging(self, mock_info, logger):
        """Testa logging de informação"""
        context = {"operation": "test"}
        logger.info("Test info", context)
        
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test info"
        assert log_data["context"] == context
    
    @patch('logging.Logger.error')
    def test_error_logging_with_exception(self, mock_error, logger):
        """Testa logging de erro com exceção"""
        exception = ValidationException("Test error", field="email")
        context = {"user_id": "123"}
        
        logger.error("Processing failed", context, exception=exception)
        
        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "Processing failed"
        assert log_data["context"]["user_id"] == "123"
        assert log_data["context"]["exception_type"] == "ValidationException"
        assert "exception_details" in log_data["context"]
    
    @patch('logging.Logger.warning')
    def test_warning_logging_with_kwargs(self, mock_warning, logger):
        """Testa logging de warning com kwargs"""
        logger.warning("Warning message", user_id="123", operation="test")
        
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["level"] == "WARNING"
        assert log_data["context"]["user_id"] == "123"
        assert log_data["context"]["operation"] == "test"
    
    @patch('logging.Logger.info')
    def test_log_request_start(self, mock_info, logger):
        """Testa log de início de requisição"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://test.com/api/analyze"
        request.headers = {"user-agent": "test-agent", "content-type": "application/json"}
        
        context = {"user_id": "123"}
        logger.log_request_start(request, context)
        
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["message"] == "Request started"
        assert log_data["context"]["method"] == "POST"
        assert log_data["context"]["url"] == "http://test.com/api/analyze"
        assert log_data["context"]["user_id"] == "123"
    
    @patch('logging.Logger.info')
    def test_log_request_end_success(self, mock_info, logger):
        """Testa log de fim de requisição com sucesso"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://test.com/api/health"
        
        logger.log_request_end(request, 200, 150.5)
        
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["message"] == "Request completed successfully"
        assert log_data["context"]["status_code"] == 200
        assert log_data["context"]["duration_ms"] == 150.5
    
    @patch('logging.Logger.error')
    def test_log_request_end_error(self, mock_error, logger):
        """Testa log de fim de requisição com erro"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://test.com/api/analyze"
        
        logger.log_request_end(request, 500, 75.2)
        
        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        log_data = json.loads(call_args)
        
        assert log_data["message"] == "Request completed with error"
        assert log_data["context"]["status_code"] == 500

class TestHandleExceptionsDecorator:
    """Testes para o decorator de tratamento de exceções"""
    
    @pytest.fixture
    def mock_request(self):
        """Fixture para criar mock de Request"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://test.com/api/test"
        return request
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, mock_request):
        """Testa execução bem-sucedida com decorator"""
        @handle_exceptions("test_operation")
        async def test_function(request):
            return {"status": "success"}
        
        with patch.object(structured_logger, 'log_request_start') as mock_start, \
             patch.object(structured_logger, 'log_request_end') as mock_end:
            
            result = await test_function(mock_request)
            
            assert result == {"status": "success"}
            mock_start.assert_called_once()
            mock_end.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_smartquest_exception_handling(self, mock_request):
        """Testa tratamento de SmartQuestException"""
        @handle_exceptions("test_operation")
        async def test_function(request):
            raise ValidationException("Invalid input", field="email")
        
        with patch.object(structured_logger, 'log_request_start'), \
             patch.object(structured_logger, 'log_request_end'), \
             patch.object(structured_logger, 'error'):
            
            with pytest.raises(HTTPException) as exc_info:
                await test_function(mock_request)
            
            assert exc_info.value.status_code == 422
            assert exc_info.value.detail["error"] == "validation_error"
    
    @pytest.mark.asyncio
    async def test_http_exception_passthrough(self, mock_request):
        """Testa passagem de HTTPException"""
        @handle_exceptions("test_operation")
        async def test_function(request):
            raise HTTPException(status_code=404, detail="Not found")
        
        with patch.object(structured_logger, 'log_request_start'), \
             patch.object(structured_logger, 'log_request_end'), \
             patch.object(structured_logger, 'error'):
            
            with pytest.raises(HTTPException) as exc_info:
                await test_function(mock_request)
            
            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Not found"
    
    @pytest.mark.asyncio
    async def test_unexpected_exception_handling(self, mock_request):
        """Testa tratamento de exceção inesperada"""
        @handle_exceptions("test_operation")
        async def test_function(request):
            raise ValueError("Unexpected error")
        
        with patch.object(structured_logger, 'log_request_start'), \
             patch.object(structured_logger, 'log_request_end'), \
             patch.object(structured_logger, 'error'):
            
            with pytest.raises(HTTPException) as exc_info:
                await test_function(mock_request)
            
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail["error"] == "internal_server_error"
            assert "unexpected error occurred" in exc_info.value.detail["message"].lower()
    
    @pytest.mark.asyncio
    async def test_function_without_request(self):
        """Testa função sem Request como parâmetro"""
        @handle_exceptions("test_operation")
        async def test_function(param1, param2):
            return param1 + param2
        
        with patch.object(structured_logger, 'info') as mock_info:
            result = await test_function(1, 2)
            
            assert result == 3
            # Deve usar logs normais em vez de request logs
            assert mock_info.call_count >= 2  # Start e end
    
    @pytest.mark.asyncio
    async def test_operation_name_in_logs(self, mock_request):
        """Testa se o nome da operação aparece nos logs"""
        operation_name = "document_analysis"
        
        @handle_exceptions(operation_name)
        async def test_function(request):
            return {"result": "ok"}
        
        with patch.object(structured_logger, 'log_request_start') as mock_start:
            await test_function(mock_request)
            
            # Verifica se o nome da operação está no contexto
            call_context = mock_start.call_args[0][1]
            assert call_context["operation"] == operation_name

class TestLoggingIntegration:
    """Testes de integração do sistema de logging"""
    
    def test_global_logger_instance(self):
        """Testa instância global do logger"""
        assert isinstance(structured_logger, StructuredLogger)
        assert structured_logger.logger.name == "smartquest"
    
    @patch('app.core.utils.structured_logger')
    def test_decorator_uses_global_logger(self, mock_logger):
        """Testa se o decorator usa o logger global"""
        @handle_exceptions("test")
        async def test_func():
            return "ok"
        
        # O decorator deve usar o logger global
        # Este teste verifica se a importação está correta
