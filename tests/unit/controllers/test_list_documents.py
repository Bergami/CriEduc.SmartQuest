"""
Testes unitários para o endpoint GET /analyze/documents

Cobre cenários de caminho feliz e casos de erro com validações.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from datetime import datetime, date, time

from app.api.controllers.analyze import list_documents
from app.dtos.responses.document_list_response_dto import DocumentListResponseDTO
from app.dtos.responses.analyze_document_response_dto import AnalyzeDocumentResponseDTO
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestListDocuments:
    """Testes para o endpoint GET /analyze/documents"""

    @pytest.fixture
    def mock_request(self):
        """Mock do request FastAPI"""
        request = Mock()
        return request

    @pytest.fixture
    def sample_dates(self):
        """Datas de exemplo para testes"""
        return {
            "start": date(2025, 1, 1),
            "end": date(2025, 12, 31),
        }

    @pytest.fixture
    def sample_documents(self):
        """Lista de documentos de exemplo"""
        return [
            AnalyzeDocumentRecord(
                id=f"doc_{i}",
                user_email="test@example.com",
                file_name=f"test_{i}.pdf",
                response={
                    "document_id": f"doc_{i}",
                    "email": "test@example.com",
                    "filename": f"test_{i}.pdf",
                    "questions": [],
                    "context_blocks": []
                },
                status=DocumentStatus.COMPLETED,
                created_at=datetime(2025, 1, i+1, 10, 30, 0)
            )
            for i in range(15)  # 15 documentos para testar paginação
        ]

    @pytest.fixture
    def mock_persistence_service(self):
        """Mock do serviço de persistência"""
        service = Mock()
        service.get_by_user_email_with_filters = AsyncMock()
        return service

    @pytest.fixture
    def mock_container(self, mock_persistence_service, monkeypatch):
        """Mock do DI Container"""
        with patch("app.core.di_container.container") as mock_cont:
            mock_cont.resolve = Mock(return_value=mock_persistence_service)
            yield mock_cont

    # ========================================================================
    # TESTES DE CAMINHO FELIZ
    # ========================================================================

    @pytest.mark.asyncio
    async def test_list_with_email_only_returns_paginated_results(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Listar documentos apenas com email (sem filtro de data)
        Deve retornar primeira página com 10 documentos e metadados corretos
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            sample_documents[:10],  # Primeira página (10 itens)
            15  # Total de documentos
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=10
        )
        
        # Assert
        assert isinstance(result, DocumentListResponseDTO)
        assert len(result.items) == 10
        assert result.pagination.current_page == 1
        assert result.pagination.page_size == 10
        assert result.pagination.total_items == 15
        assert result.pagination.total_pages == 2
        assert result.pagination.has_next is True
        assert result.pagination.has_previous is False
        
        # Verificar chamada ao service
        mock_persistence_service.get_by_user_email_with_filters.assert_called_once_with(
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=10
        )

    @pytest.mark.asyncio
    async def test_list_with_date_filter_returns_filtered_results(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Listar documentos com filtro de data
        Deve passar parâmetros de data ao service (agora aceita date e converte para datetime)
        """
        # Arrange
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            sample_documents[:5],  # 5 documentos no período
            5
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10
        )
        
        # Assert
        assert len(result.items) == 5
        assert result.pagination.total_items == 5
        assert result.pagination.total_pages == 1
        
        # Verificar que datas foram convertidas para datetime e passadas ao service
        # start_date = 00:00:00, end_date = 23:59:59.999999
        call_args = mock_persistence_service.get_by_user_email_with_filters.call_args
        assert call_args.kwargs["email"] == "test@example.com"
        assert call_args.kwargs["start_date"] == datetime.combine(start_date, time.min)
        assert call_args.kwargs["end_date"] == datetime.combine(end_date, time.max)
        assert call_args.kwargs["page"] == 1
        assert call_args.kwargs["page_size"] == 10

    @pytest.mark.asyncio
    async def test_pagination_second_page_returns_remaining_items(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Segunda página de paginação
        Deve retornar itens restantes e metadados corretos
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            sample_documents[10:15],  # Segunda página (5 itens restantes)
            15
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=2,
            page_size=10
        )
        
        # Assert
        assert len(result.items) == 5
        assert result.pagination.current_page == 2
        assert result.pagination.has_next is False
        assert result.pagination.has_previous is True

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty_with_correct_metadata(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ✅ Cenário: Usuário sem documentos
        Deve retornar lista vazia com metadados zerados
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            [],  # Nenhum documento
            0
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="newuser@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=10
        )
        
        # Assert
        assert len(result.items) == 0
        assert result.pagination.total_items == 0
        assert result.pagination.total_pages == 0
        assert result.pagination.has_next is False
        assert result.pagination.has_previous is False

    @pytest.mark.asyncio
    async def test_custom_page_size_respects_limit(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Page size personalizado (dentro do limite)
        Deve retornar quantidade solicitada
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            sample_documents[:5],
            15
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=5
        )
        
        # Assert
        assert len(result.items) == 5
        assert result.pagination.page_size == 5
        assert result.pagination.total_pages == 3  # 15 / 5 = 3 páginas

    # ========================================================================
    # TESTES DE VALIDAÇÃO E ERRO
    # ========================================================================

    @pytest.mark.asyncio
    async def test_missing_email_raises_400(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ❌ Cenário: Email vazio
        Deve retornar 400 Bad Request
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_documents(
                request=mock_request,
                email="",
                start_date=None,
                end_date=None,
                page=1,
                page_size=10
            )
        
        assert exc_info.value.status_code == 400
        assert "obrigatório" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_start_date_without_end_date_raises_400(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ❌ Cenário: start_date sem end_date
        Deve retornar 400 Bad Request
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_documents(
                request=mock_request,
                email="test@example.com",
                start_date=date(2025, 1, 1),
                end_date=None,
                page=1,
                page_size=10
            )
        
        assert exc_info.value.status_code == 400
        assert "data" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_end_date_without_start_date_raises_400(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ❌ Cenário: end_date sem start_date
        Deve retornar 400 Bad Request
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_documents(
                request=mock_request,
                email="test@example.com",
                start_date=None,
                end_date=date(2025, 1, 31),
                page=1,
                page_size=10
            )
        
        assert exc_info.value.status_code == 400
        assert "data" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_start_date_after_end_date_raises_400(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ❌ Cenário: start_date > end_date
        Deve retornar 400 Bad Request
        """
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_documents(
                request=mock_request,
                email="test@example.com",
                start_date=date(2025, 1, 31),
                end_date=date(2025, 1, 1),
                page=1,
                page_size=10
            )
        
        assert exc_info.value.status_code == 400
        assert "anterior" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_mongodb_error_raises_500(
        self,
        mock_request,
        mock_persistence_service,
        mock_container
    ):
        """
        ❌ Cenário: Erro no MongoDB
        Deve retornar 500 Internal Server Error
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.side_effect = Exception(
            "MongoDB connection failed"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_documents(
                request=mock_request,
                email="test@example.com",
                start_date=None,
                end_date=None,
                page=1,
                page_size=10
            )
        
        assert exc_info.value.status_code == 500
        assert "erro interno" in exc_info.value.detail.lower()

    # ========================================================================
    # TESTES DE CONVERSÃO DE DADOS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_documents_converted_to_dto_correctly(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Conversão de AnalyzeDocumentRecord para DTO
        Deve manter todos os campos corretamente
        """
        # Arrange
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            [sample_documents[0]],
            1
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=10
        )
        
        # Assert
        assert len(result.items) == 1
        item = result.items[0]
        assert isinstance(item, AnalyzeDocumentResponseDTO)
        assert item.user_email == "test@example.com"
        assert item.document_name == "test_0.pdf"
        assert item.status == "completed"

    @pytest.mark.asyncio
    async def test_pagination_metadata_calculated_correctly(
        self,
        mock_request,
        mock_persistence_service,
        mock_container,
        sample_documents
    ):
        """
        ✅ Cenário: Cálculo de metadados de paginação
        Deve calcular total_pages, has_next, has_previous corretamente
        """
        # Arrange: 25 documentos, page_size=10 -> 3 páginas
        mock_persistence_service.get_by_user_email_with_filters.return_value = (
            sample_documents[:10],
            25
        )
        
        # Act
        result = await list_documents(
            request=mock_request,
            email="test@example.com",
            start_date=None,
            end_date=None,
            page=1,
            page_size=10
        )
        
        # Assert
        assert result.pagination.total_pages == 3  # ceil(25/10) = 3
        assert result.pagination.has_next is True  # Página 1 de 3
        assert result.pagination.has_previous is False  # Primeira página
