"""
Testes unitários para o endpoint GET /analyze/analyze_document/{id}
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException
from datetime import datetime

from app.api.controllers.analyze import get_analyze_document
from app.dtos.responses.analyze_document_response_dto import AnalyzeDocumentResponseDTO
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestGetAnalyzeDocument:
    """Testes para o endpoint GET /analyze/analyze_document/{id}"""

    @pytest.fixture
    def mock_request(self):
        """Mock do request FastAPI"""
        request = Mock()
        return request

    @pytest.fixture
    def sample_document_record(self):
        """Registro de documento de exemplo"""
        return AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="test@example.com",
            file_name="test.pdf",
            response={
                "document_id": "doc_123",
                "email": "test@example.com",
                "filename": "test.pdf",
                "questions": [],
                "context_blocks": []
            },
            status=DocumentStatus.COMPLETED,
            created_at=datetime(2024, 10, 28, 10, 30, 0)
        )

    @pytest.fixture
    def mock_persistence_service(self):
        """Mock do serviço de persistência"""
        service = Mock()
        service.get_by_document_id = AsyncMock()
        return service

    @pytest.fixture
    def mock_container(self, mock_persistence_service, monkeypatch):
        """Mock do DI Container"""
        container = Mock()
        container.resolve.return_value = mock_persistence_service
        
        # Patch do import do container no ponto correto
        monkeypatch.setattr("app.core.di_container.container", container)
        return container

    @pytest.mark.asyncio
    async def test_get_analyze_document_success(
        self, 
        mock_request, 
        sample_document_record, 
        mock_persistence_service,
        mock_container
    ):
        """Teste de sucesso - documento encontrado"""
        # Arrange
        document_id = "507f1f77bcf86cd799439011"
        mock_persistence_service.get_by_document_id.return_value = sample_document_record

        # Act
        result = await get_analyze_document(document_id, mock_request)

        # Assert
        assert isinstance(result, AnalyzeDocumentResponseDTO)
        assert result.id == str(sample_document_record.id)
        assert result.document_name == sample_document_record.file_name
        assert result.user_email == sample_document_record.user_email
        assert result.status == sample_document_record.status.value
        assert result.analysis_results == sample_document_record.response
        
        # Verificar chamadas
        mock_persistence_service.get_by_document_id.assert_called_once_with(document_id)
        mock_container.resolve.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_analyze_document_not_found(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """Teste de documento não encontrado - deve retornar 404"""
        # Arrange
        document_id = "507f1f77bcf86cd799439012"
        mock_persistence_service.get_by_document_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_analyze_document(document_id, mock_request)

        assert exc_info.value.status_code == 404
        assert "Documento não encontrado" in exc_info.value.detail
        mock_persistence_service.get_by_document_id.assert_called_once_with(document_id)

    @pytest.mark.asyncio
    async def test_get_analyze_document_empty_id(
        self,
        mock_request,
        mock_container
    ):
        """Teste com ID vazio - deve retornar 400"""
        # Test empty string
        with pytest.raises(HTTPException) as exc_info:
            await get_analyze_document("", mock_request)
        
        assert exc_info.value.status_code == 400
        assert "ID do documento é obrigatório" in exc_info.value.detail

        # Test whitespace only
        with pytest.raises(HTTPException) as exc_info:
            await get_analyze_document("   ", mock_request)
        
        assert exc_info.value.status_code == 400
        assert "ID do documento é obrigatório" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_analyze_document_service_error(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """Teste de erro interno do serviço - deve retornar 500"""
        # Arrange
        document_id = "507f1f77bcf86cd799439011"
        mock_persistence_service.get_by_document_id.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_analyze_document(document_id, mock_request)

        assert exc_info.value.status_code == 500
        assert "Erro interno ao buscar documento" in exc_info.value.detail
        mock_persistence_service.get_by_document_id.assert_called_once_with(document_id)

    @pytest.mark.asyncio
    async def test_get_analyze_document_various_id_formats(
        self,
        mock_request,
        sample_document_record,
        mock_persistence_service,
        mock_container
    ):
        """Teste com diferentes formatos de ID válidos"""
        # Arrange
        mock_persistence_service.get_by_document_id.return_value = sample_document_record
        
        # Test MongoDB ObjectId format
        object_id = "507f1f77bcf86cd799439011"
        result = await get_analyze_document(object_id, mock_request)
        assert isinstance(result, AnalyzeDocumentResponseDTO)

        # Test UUID format (caso seja usado)
        uuid_id = "550e8400-e29b-41d4-a716-446655440000"
        result = await get_analyze_document(uuid_id, mock_request)
        assert isinstance(result, AnalyzeDocumentResponseDTO)

        # Verificar que o serviço foi chamado com os IDs corretos
        calls = mock_persistence_service.get_by_document_id.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == object_id
        assert calls[1][0][0] == uuid_id