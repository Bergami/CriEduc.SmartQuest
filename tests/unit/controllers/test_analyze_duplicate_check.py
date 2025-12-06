"""
Testes unitários para verificação de duplicatas no controller analyze_document

Valida o comportamento do endpoint quando documento duplicado é detectado.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import UploadFile
from io import BytesIO

from app.api.controllers.analyze import analyze_document
from app.models.persistence import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestAnalyzeDuplicateCheck:
    """Testes para verificação de duplicatas no endpoint."""

    @pytest.fixture
    def mock_file(self):
        """Mock de UploadFile."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        
        # Create a real BytesIO object for proper async file operations
        content = b"PDF content" * 100  # 1100 bytes
        file_obj = BytesIO(content)
        mock_file.file = file_obj
        
        # Mock async seek to work with the BytesIO object
        async def async_seek(offset, whence=0):
            file_obj.seek(offset, whence)
        
        mock_file.seek = AsyncMock(side_effect=async_seek)
        
        return mock_file

    @pytest.fixture
    def mock_request(self):
        """Mock de Request."""
        return MagicMock()

    @pytest.fixture
    def mock_existing_doc(self):
        """Mock de documento existente COMPLETED."""
        return AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=1100,
            status=DocumentStatus.COMPLETED,
            created_at=datetime(2025, 12, 1, 10, 30, 0),
            response={
                "document_id": "de8648f0-b36e-4513-9ca4-b11ad6cc2f25",
                "email": "test@example.com",
                "filename": "test.pdf",
                "header": {
                    "school": "Test School",
                    "teacher": "Test Teacher",
                    "subject": "Mathematics"
                },
                "questions": [
                    {
                        "number": 1,
                        "question": "What is 2+2?",
                        "alternatives": [
                            {"letter": "A", "text": "3"},
                            {"letter": "B", "text": "4"}
                        ],
                        "hasImage": False,
                        "context_id": 1
                    }
                ],
                "context_blocks": [
                    {
                        "id": 1,
                        "type": ["text"],
                        "title": "Context 1",
                        "hasImage": False,
                        "images": [],
                        "paragraphs": ["Test paragraph"]
                    }
                ]
            }
        )

    @pytest.mark.asyncio
    async def test_duplicate_completed_returns_existing_data(
        self, mock_request, mock_file, mock_existing_doc
    ):
        """✅ Retorna dados existentes quando documento COMPLETED é encontrado."""
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"):
            
            # Mock persistence service
            mock_persistence = AsyncMock()
            mock_persistence.check_duplicate_document = AsyncMock(return_value=mock_existing_doc)
            mock_container.resolve = MagicMock(return_value=mock_persistence)
            
            # Chamar endpoint
            result = await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_file
            )
            
            # Validar resultado
            assert result.status == "already_processed"
            assert "já foi processado anteriormente" in result.message
            assert result.document_id == "de8648f0-b36e-4513-9ca4-b11ad6cc2f25"  # ID do response, não do record
            assert result.from_database is True
            assert result.from_cache is False
            assert len(result.questions) == 1
            assert len(result.context_blocks) == 1

    @pytest.mark.asyncio
    async def test_duplicate_failed_allows_reprocessing(
        self, mock_request, mock_file
    ):
        """✅ Permite reprocessamento de documento com status FAILED."""
        mock_failed_doc = AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=1100,
            status=DocumentStatus.FAILED,
            created_at=datetime(2025, 12, 1, 10, 30, 0),
            response={}
        )
        
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"), \
             patch("app.api.controllers.analyze.DocumentExtractionService") as mock_extraction, \
             patch("app.api.controllers.analyze.DocumentResponseDTO") as mock_dto:
            
            # Mock persistence service
            mock_persistence = AsyncMock()
            mock_persistence.check_duplicate_document = AsyncMock(return_value=mock_failed_doc)
            mock_persistence.save_analysis_result = AsyncMock(return_value="new_doc_id")
            
            # Mock analyze service
            mock_analyze = AsyncMock()
            mock_internal_response = MagicMock()
            mock_internal_response.document_id = "new_doc_id"
            mock_internal_response.questions = []
            mock_internal_response.context_blocks = []
            mock_internal_response.document_metadata.header_images = []
            mock_analyze.process_document_with_models = AsyncMock(return_value=mock_internal_response)
            
            def resolve_service(interface):
                if interface.__name__ == "ISimplePersistenceService":
                    return mock_persistence
                elif interface.__name__ == "IAnalyzeService":
                    return mock_analyze
                return MagicMock()
            
            mock_container.resolve = MagicMock(side_effect=resolve_service)
            
            # Mock extraction
            mock_extraction.get_extraction_data = AsyncMock(return_value={"text": "data"})
            
            # Mock DTO
            mock_response = MagicMock()
            mock_response.dict = MagicMock(return_value={})
            mock_dto.from_internal_response = MagicMock(return_value=mock_response)
            
            # Chamar endpoint
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_file
            )
            
            # Verificar que documento foi reprocessado
            mock_extraction.get_extraction_data.assert_called_once()
            mock_analyze.process_document_with_models.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_duplicate_processes_normally(
        self, mock_request, mock_file
    ):
        """✅ Processa normalmente quando documento não existe."""
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"), \
             patch("app.api.controllers.analyze.DocumentExtractionService") as mock_extraction, \
             patch("app.api.controllers.analyze.DocumentResponseDTO") as mock_dto:
            
            # Mock persistence service (sem duplicata)
            mock_persistence = AsyncMock()
            mock_persistence.check_duplicate_document = AsyncMock(return_value=None)
            mock_persistence.save_analysis_result = AsyncMock(return_value="new_doc_id")
            
            # Mock analyze service
            mock_analyze = AsyncMock()
            mock_internal_response = MagicMock()
            mock_internal_response.document_id = "new_doc_id"
            mock_internal_response.questions = []
            mock_internal_response.context_blocks = []
            mock_internal_response.document_metadata.header_images = []
            mock_analyze.process_document_with_models = AsyncMock(return_value=mock_internal_response)
            
            def resolve_service(interface):
                if interface.__name__ == "ISimplePersistenceService":
                    return mock_persistence
                elif interface.__name__ == "IAnalyzeService":
                    return mock_analyze
                return MagicMock()
            
            mock_container.resolve = MagicMock(side_effect=resolve_service)
            
            # Mock extraction
            mock_extraction.get_extraction_data = AsyncMock(return_value={"text": "data"})
            
            # Mock DTO
            mock_response = MagicMock()
            mock_response.dict = MagicMock(return_value={})
            mock_dto.from_internal_response = MagicMock(return_value=mock_response)
            
            # Chamar endpoint
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_file
            )
            
            # Verificar processamento completo
            mock_persistence.check_duplicate_document.assert_called_once_with(
                email="test@example.com",
                filename="test.pdf",
                file_size=1100
            )
            mock_extraction.get_extraction_data.assert_called_once()
            mock_analyze.process_document_with_models.assert_called_once()
            mock_persistence.save_analysis_result.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_check_uses_file_size(
        self, mock_request, mock_file, mock_existing_doc
    ):
        """✅ Verificação de duplicata inclui file_size."""
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"):
            
            # Mock persistence service
            mock_persistence = AsyncMock()
            mock_persistence.check_duplicate_document = AsyncMock(return_value=mock_existing_doc)
            mock_container.resolve = MagicMock(return_value=mock_persistence)
            
            # Chamar endpoint
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_file
            )
            
            # Verificar que file_size foi passado
            mock_persistence.check_duplicate_document.assert_called_once()
            call_args = mock_persistence.check_duplicate_document.call_args
            assert call_args.kwargs["email"] == "test@example.com"
            assert call_args.kwargs["filename"] == "test.pdf"
            assert call_args.kwargs["file_size"] == 1100
