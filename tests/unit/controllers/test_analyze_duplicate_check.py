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
            
            # Mock DuplicateCheckService
            from app.services.core.duplicate_check_service import DuplicateCheckResult
            from app.dtos.responses.document_response_dto import DocumentResponseDTO
            
            mock_duplicate_service = AsyncMock()
            
            # Create expected response from existing document (same way DuplicateCheckService does)
            response_data = mock_existing_doc.response.copy()
            response_data.update({
                "status": "already_processed",
                "message": f"Documento já foi processado anteriormente em {mock_existing_doc.created_at.isoformat()}",
                "from_database": True
            })
            existing_response = DocumentResponseDTO(**response_data)
            
            mock_result = DuplicateCheckResult(
                is_duplicate=True,
                should_process=False,
                existing_response=existing_response,
                file_size=1100,
                existing_document_id=mock_existing_doc.id,
                processed_at=mock_existing_doc.created_at
            )
            mock_duplicate_service.check_and_handle_duplicate = AsyncMock(return_value=mock_result)
            
            mock_container.resolve = MagicMock(return_value=mock_duplicate_service)
            
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
            
            # Mock DuplicateCheckService - FAILED allows reprocessing
            from app.services.core.duplicate_check_service import DuplicateCheckResult
            
            mock_duplicate_service = AsyncMock()
            mock_result = DuplicateCheckResult(
                is_duplicate=True,
                should_process=True,  # FAILED status allows reprocessing
                existing_response=None,
                file_size=1100,
                existing_document_id=mock_failed_doc.id,
                processed_at=mock_failed_doc.created_at
            )
            mock_duplicate_service.check_and_handle_duplicate = AsyncMock(return_value=mock_result)
            
            # Mock persistence service
            mock_persistence = AsyncMock()
            mock_persistence.save_completed_analysis = AsyncMock(return_value="new_doc_id")
            
            # Mock analyze service
            mock_analyze = AsyncMock()
            mock_internal_response = MagicMock()
            mock_internal_response.document_id = "new_doc_id"
            mock_internal_response.questions = []
            mock_internal_response.context_blocks = []
            mock_internal_response.document_metadata.header_images = []
            mock_analyze.process_document_with_models = AsyncMock(return_value=mock_internal_response)
            
            def resolve_service(interface):
                from app.services.core.duplicate_check_service import DuplicateCheckService
                from app.services.persistence import ISimplePersistenceService
                from app.core.interfaces import IAnalyzeService
                
                if interface == DuplicateCheckService:
                    return mock_duplicate_service
                elif interface == ISimplePersistenceService:
                    return mock_persistence
                elif interface == IAnalyzeService:
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
            mock_persistence.save_completed_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_duplicate_processes_normally(
        self, mock_request, mock_file
    ):
        """✅ Processa normalmente quando documento não existe."""
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"), \
             patch("app.api.controllers.analyze.DocumentExtractionService") as mock_extraction, \
             patch("app.api.controllers.analyze.DocumentResponseDTO") as mock_dto:
            
            # Mock DuplicateCheckService - no duplicate found
            from app.services.core.duplicate_check_service import DuplicateCheckResult
            
            mock_duplicate_service = AsyncMock()
            mock_result = DuplicateCheckResult(
                is_duplicate=False,
                should_process=True,
                existing_response=None,
                file_size=1100,
                existing_document_id=None,
                processed_at=None
            )
            mock_duplicate_service.check_and_handle_duplicate = AsyncMock(return_value=mock_result)
            
            # Mock persistence service (sem duplicata)
            mock_persistence = AsyncMock()
            mock_persistence.save_completed_analysis = AsyncMock(return_value="new_doc_id")
            
            # Mock analyze service
            mock_analyze = AsyncMock()
            mock_internal_response = MagicMock()
            mock_internal_response.document_id = "new_doc_id"
            mock_internal_response.questions = []
            mock_internal_response.context_blocks = []
            mock_internal_response.document_metadata.header_images = []
            mock_analyze.process_document_with_models = AsyncMock(return_value=mock_internal_response)
            
            def resolve_service(interface):
                from app.services.core.duplicate_check_service import DuplicateCheckService
                from app.services.persistence import ISimplePersistenceService
                from app.core.interfaces import IAnalyzeService
                
                if interface == DuplicateCheckService:
                    return mock_duplicate_service
                elif interface == ISimplePersistenceService:
                    return mock_persistence
                elif interface == IAnalyzeService:
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
            mock_duplicate_service.check_and_handle_duplicate.assert_called_once_with(
                "test@example.com",
                mock_file
            )
            mock_extraction.get_extraction_data.assert_called_once()
            mock_analyze.process_document_with_models.assert_called_once()
            mock_persistence.save_completed_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_check_uses_file_size(
        self, mock_request, mock_file, mock_existing_doc
    ):
        """✅ Verificação de duplicata inclui file_size."""
        with patch("app.core.di_container.container") as mock_container, \
             patch("app.validators.analyze_validator.AnalyzeValidator.validate_all"):
            
            # Mock DuplicateCheckService
            from app.services.core.duplicate_check_service import DuplicateCheckResult
            from app.dtos.responses.document_response_dto import DocumentResponseDTO
            
            mock_duplicate_service = AsyncMock()
            
            # Create expected response from existing document (same way DuplicateCheckService does)
            response_data = mock_existing_doc.response.copy()
            response_data.update({
                "status": "already_processed",
                "message": f"Documento já foi processado anteriormente em {mock_existing_doc.created_at.isoformat()}",
                "from_database": True
            })
            existing_response = DocumentResponseDTO(**response_data)
            
            mock_result = DuplicateCheckResult(
                is_duplicate=True,
                should_process=False,
                existing_response=existing_response,
                file_size=1100,
                existing_document_id=mock_existing_doc.id,
                processed_at=mock_existing_doc.created_at
            )
            mock_duplicate_service.check_and_handle_duplicate = AsyncMock(return_value=mock_result)
            
            mock_container.resolve = MagicMock(return_value=mock_duplicate_service)
            
            # Chamar endpoint
            await analyze_document(
                request=mock_request,
                email="test@example.com",
                file=mock_file
            )
            
            # Verificar que file foi passado corretamente (service extrai file_size internamente)
            mock_duplicate_service.check_and_handle_duplicate.assert_called_once_with(
                "test@example.com",
                mock_file
            )
            
            # Verificar que result contém file_size
            assert mock_result.file_size == 1100
