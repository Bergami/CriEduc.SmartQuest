"""
Testes unitários para verificação de duplicatas no MongoDB

Valida o método check_duplicate_document do MongoDBPersistenceService.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.persistence.mongodb_persistence_service import MongoDBPersistenceService
from app.models.persistence import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestDuplicateCheck:
    """Testes para verificação de duplicatas."""

    @pytest.fixture
    def mock_connection_service(self):
        """Mock do serviço de conexão MongoDB."""
        mock_service = AsyncMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_service.get_database = AsyncMock(return_value=mock_db)
        
        return mock_service, mock_collection

    @pytest.fixture
    def persistence_service(self, mock_connection_service):
        """Instância do serviço de persistência com mock."""
        mock_service, _ = mock_connection_service
        return MongoDBPersistenceService(mock_service)

    @pytest.mark.asyncio
    async def test_check_duplicate_returns_none_when_not_exists(
        self, persistence_service, mock_connection_service
    ):
        """✅ Retorna None quando documento não existe."""
        _, mock_collection = mock_connection_service
        mock_collection.find_one = AsyncMock(return_value=None)
        
        result = await persistence_service.check_duplicate_document(
            email="test@example.com",
            filename="test.pdf",
            file_size=1024
        )
        
        assert result is None
        mock_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_duplicate_returns_record_when_exists_completed(
        self, persistence_service, mock_connection_service
    ):
        """✅ Retorna record quando documento existe com status COMPLETED."""
        _, mock_collection = mock_connection_service
        
        # Mock documento MongoDB
        mock_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "user_email": "test@example.com",
            "file_name": "test.pdf",
            "file_size": 1024,
            "status": DocumentStatus.COMPLETED.value,
            "created_at": datetime.now(),
            "response": {"document_id": "123", "questions": []}
        }
        
        mock_collection.find_one = AsyncMock(return_value=mock_doc)
        
        result = await persistence_service.check_duplicate_document(
            email="test@example.com",
            filename="test.pdf",
            file_size=1024
        )
        
        assert result is not None
        assert isinstance(result, AnalyzeDocumentRecord)
        assert result.user_email == "test@example.com"
        assert result.file_name == "test.pdf"
        assert result.file_size == 1024

    @pytest.mark.asyncio
    async def test_check_duplicate_ignores_failed_documents(
        self, persistence_service, mock_connection_service
    ):
        """✅ Ignora documentos com status FAILED (permite retry)."""
        _, mock_collection = mock_connection_service
        
        # Query deve filtrar por status COMPLETED
        mock_collection.find_one = AsyncMock(return_value=None)
        
        await persistence_service.check_duplicate_document(
            email="test@example.com",
            filename="failed.pdf",
            file_size=2048
        )
        
        # Verificar que query inclui status COMPLETED
        call_args = mock_collection.find_one.call_args
        query = call_args[0][0]
        
        assert query["status"] == DocumentStatus.COMPLETED.value
        assert query["user_email"] == "test@example.com"
        assert query["file_name"] == "failed.pdf"
        assert query["file_size"] == 2048

    @pytest.mark.asyncio
    async def test_check_duplicate_uses_file_size(
        self, persistence_service, mock_connection_service
    ):
        """✅ Usa file_size na verificação (mesmo email+filename, size diferente = não duplicado)."""
        _, mock_collection = mock_connection_service
        mock_collection.find_one = AsyncMock(return_value=None)
        
        # Buscar com file_size específico
        await persistence_service.check_duplicate_document(
            email="test@example.com",
            filename="document.pdf",
            file_size=5000
        )
        
        # Verificar que file_size está na query
        call_args = mock_collection.find_one.call_args
        query = call_args[0][0]
        
        assert "file_size" in query
        assert query["file_size"] == 5000

    @pytest.mark.asyncio
    async def test_check_duplicate_handles_error_gracefully(
        self, persistence_service, mock_connection_service
    ):
        """✅ Retorna None em caso de erro (fail-safe)."""
        _, mock_collection = mock_connection_service
        mock_collection.find_one = AsyncMock(side_effect=Exception("Database error"))
        
        result = await persistence_service.check_duplicate_document(
            email="test@example.com",
            filename="test.pdf",
            file_size=1024
        )
        
        # Deve retornar None para permitir processamento
        assert result is None
