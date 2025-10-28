"""
Testes de integração para o endpoint GET /analyze/analyze_document/{id}
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestGetAnalyzeDocumentIntegration:
    """Testes de integração para o endpoint GET /analyze/analyze_document/{id}"""

    @pytest.fixture
    def client(self):
        """Cliente de teste para a API"""
        return TestClient(app)

    @pytest.fixture
    def sample_document_record(self):
        """Registro de documento de exemplo"""
        return AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="integration@test.com",
            file_name="integration_test.pdf",
            response={
                "document_id": "doc_integration_123",
                "email": "integration@test.com",
                "filename": "integration_test.pdf",
                "header": {
                    "school": "Test School",
                    "teacher": "Test Teacher",
                    "subject": "Test Subject"
                },
                "questions": [
                    {
                        "number": 1,
                        "question": "Test question?",
                        "alternatives": [
                            {"letter": "A", "text": "Option A"},
                            {"letter": "B", "text": "Option B"}
                        ],
                        "hasImage": False,
                        "context_id": 1
                    }
                ],
                "context_blocks": [
                    {
                        "id": 1,
                        "type": ["text"],
                        "title": "Test Context",
                        "hasImage": False,
                        "images": [],
                        "paragraphs": ["Test paragraph"]
                    }
                ]
            },
            status=DocumentStatus.COMPLETED,
            created_at=datetime(2024, 10, 28, 10, 30, 0)
        )

    @patch('app.core.di_container.container')
    def test_get_analyze_document_success_integration(
        self, 
        mock_container,
        client,
        sample_document_record
    ):
        """Teste de integração completo - sucesso"""
        # Arrange
        mock_persistence_service = AsyncMock()
        mock_persistence_service.get_by_document_id.return_value = sample_document_record
        mock_container.resolve.return_value = mock_persistence_service

        document_id = "507f1f77bcf86cd799439011"

        # Act
        response = client.get(f"/analyze/analyze_document/{document_id}")

        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert data["_id"] == str(sample_document_record.id)
        assert data["document_name"] == sample_document_record.file_name
        assert data["user_email"] == sample_document_record.user_email
        assert data["status"] == sample_document_record.status.value
        assert data["analysis_results"] == sample_document_record.response
        assert "created_at" in data

        # Verificar estrutura completa dos dados
        analysis_results = data["analysis_results"]
        assert "questions" in analysis_results
        assert "context_blocks" in analysis_results
        assert "header" in analysis_results
        assert len(analysis_results["questions"]) == 1
        assert len(analysis_results["context_blocks"]) == 1

    @patch('app.core.di_container.container')
    def test_get_analyze_document_not_found_integration(
        self,
        mock_container,
        client
    ):
        """Teste de integração - documento não encontrado"""
        # Arrange
        mock_persistence_service = AsyncMock()
        mock_persistence_service.get_by_document_id.return_value = None
        mock_container.resolve.return_value = mock_persistence_service

        document_id = "507f1f77bcf86cd799439012"

        # Act
        response = client.get(f"/analyze/analyze_document/{document_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Documento não encontrado" in data["detail"]

    def test_get_analyze_document_invalid_id_integration(self, client):
        """Teste de integração - ID inválido"""
        # Act & Assert
        
        # Teste ID vazio
        response = client.get("/analyze/analyze_document/")
        assert response.status_code == 404  # FastAPI rota não encontrada

        # Teste ID com espaços
        response = client.get("/analyze/analyze_document/   ")
        assert response.status_code == 400
        data = response.json()
        assert "ID do documento é obrigatório" in data["detail"]

    @patch('app.core.di_container.container')
    def test_get_analyze_document_service_error_integration(
        self,
        mock_container,
        client
    ):
        """Teste de integração - erro do serviço"""
        # Arrange
        mock_persistence_service = AsyncMock()
        mock_persistence_service.get_by_document_id.side_effect = Exception("Database error")
        mock_container.resolve.return_value = mock_persistence_service

        document_id = "507f1f77bcf86cd799439011"

        # Act
        response = client.get(f"/analyze/analyze_document/{document_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "Erro interno ao buscar documento" in data["detail"]

    @patch('app.core.di_container.container')
    def test_get_analyze_document_different_statuses(
        self,
        mock_container,
        client
    ):
        """Teste de integração com diferentes status de documento"""
        mock_persistence_service = AsyncMock()
        mock_container.resolve.return_value = mock_persistence_service

        # Test PENDING status
        pending_record = AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="test@example.com",
            file_name="pending.pdf",
            response={},
            status=DocumentStatus.PENDING,
            created_at=datetime.now()
        )
        
        mock_persistence_service.get_by_document_id.return_value = pending_record
        response = client.get("/analyze/analyze_document/507f1f77bcf86cd799439011")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

        # Test FAILED status
        failed_record = AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439012",
            user_email="test@example.com",
            file_name="failed.pdf",
            response={},
            status=DocumentStatus.FAILED,
            created_at=datetime.now()
        )
        
        mock_persistence_service.get_by_document_id.return_value = failed_record
        response = client.get("/analyze/analyze_document/507f1f77bcf86cd799439012")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"

    @patch('app.core.di_container.container')
    def test_get_analyze_document_complex_response_structure(
        self,
        mock_container,
        client
    ):
        """Teste com estrutura complexa de resposta"""
        # Arrange
        complex_record = AnalyzeDocumentRecord(
            id="507f1f77bcf86cd799439011",
            user_email="complex@test.com",
            file_name="complex_test.pdf",
            response={
                "document_id": "doc_complex_123",
                "email": "complex@test.com",
                "filename": "complex_test.pdf",
                "header": {
                    "school": "Complex Test School",
                    "teacher": "Dr. Complex Teacher",
                    "subject": "Advanced Mathematics",
                    "student": "Complex Student",
                    "series": "12th Grade"
                },
                "questions": [
                    {
                        "number": i,
                        "question": f"Complex question {i}?",
                        "alternatives": [
                            {"letter": "A", "text": f"Option A for question {i}"},
                            {"letter": "B", "text": f"Option B for question {i}"},
                            {"letter": "C", "text": f"Option C for question {i}"},
                            {"letter": "D", "text": f"Option D for question {i}"}
                        ],
                        "hasImage": i % 2 == 0,
                        "context_id": i
                    }
                    for i in range(1, 6)  # 5 questões
                ],
                "context_blocks": [
                    {
                        "id": i,
                        "type": ["text", "image"] if i % 2 == 0 else ["text"],
                        "title": f"Context Block {i}",
                        "hasImage": i % 2 == 0,
                        "images": [f"image{i}.jpg"] if i % 2 == 0 else [],
                        "paragraphs": [f"Paragraph {j} for context {i}" for j in range(1, 4)]
                    }
                    for i in range(1, 6)  # 5 contextos
                ]
            },
            status=DocumentStatus.COMPLETED,
            created_at=datetime(2024, 10, 28, 15, 45, 30)
        )

        mock_persistence_service = AsyncMock()
        mock_persistence_service.get_by_document_id.return_value = complex_record
        mock_container.resolve.return_value = mock_persistence_service

        # Act
        response = client.get("/analyze/analyze_document/507f1f77bcf86cd799439011")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        analysis_results = data["analysis_results"]
        assert len(analysis_results["questions"]) == 5
        assert len(analysis_results["context_blocks"]) == 5
        
        # Verificar estrutura das questões
        for i, question in enumerate(analysis_results["questions"], 1):
            assert question["number"] == i
            assert len(question["alternatives"]) == 4
            assert question["hasImage"] == (i % 2 == 0)
        
        # Verificar estrutura dos contextos
        for i, context in enumerate(analysis_results["context_blocks"], 1):
            assert context["id"] == i
            assert context["hasImage"] == (i % 2 == 0)
            assert len(context["paragraphs"]) == 3