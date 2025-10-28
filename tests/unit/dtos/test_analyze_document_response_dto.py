"""
Testes unitários para AnalyzeDocumentResponseDTO
"""

import pytest
from datetime import datetime
from app.dtos.responses.analyze_document_response_dto import AnalyzeDocumentResponseDTO
from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestAnalyzeDocumentResponseDTO:
    """Testes para o DTO de resposta do documento analisado"""

    def test_from_mongo_record(self):
        """Teste de conversão de registro MongoDB para DTO"""
        # Arrange
        mongo_record = {
            "_id": "507f1f77bcf86cd799439011",
            "file_name": "test.pdf",
            "status": "completed",
            "response": {
                "document_id": "doc_123",
                "questions": [],
                "context_blocks": []
            },
            "created_at": datetime(2024, 10, 28, 10, 30, 0),
            "user_email": "test@example.com"
        }

        # Act
        dto = AnalyzeDocumentResponseDTO.from_mongo_record(mongo_record)

        # Assert
        assert dto.id == "507f1f77bcf86cd799439011"
        assert dto.document_name == "test.pdf"
        assert dto.status == "completed"
        assert dto.analysis_results == mongo_record["response"]
        assert dto.created_at == datetime(2024, 10, 28, 10, 30, 0)
        assert dto.user_email == "test@example.com"

    def test_from_analyze_document_record(self):
        """Teste de conversão de AnalyzeDocumentRecord para DTO"""
        # Arrange
        record = AnalyzeDocumentRecord(
            user_email="test@example.com",
            file_name="test.pdf",
            response={
                "document_id": "doc_123",
                "questions": [],
                "context_blocks": []
            },
            status=DocumentStatus.COMPLETED,
            created_at=datetime(2024, 10, 28, 10, 30, 0)
        )

        # Act
        dto = AnalyzeDocumentResponseDTO.from_analyze_document_record(record)

        # Assert
        assert dto.id == str(record.id)  # O ID é gerado automaticamente
        assert dto.document_name == "test.pdf"
        assert dto.status == "completed"
        assert dto.analysis_results == record.response
        assert dto.created_at == datetime(2024, 10, 28, 10, 30, 0)
        assert dto.user_email == "test@example.com"

    def test_from_mongo_record_missing_fields(self):
        """Teste com campos ausentes no registro MongoDB"""
        # Arrange
        mongo_record = {
            "_id": "507f1f77bcf86cd799439011",
            "file_name": "test.pdf",
            "created_at": datetime(2024, 10, 28, 10, 30, 0),
            "user_email": "test@example.com"
            # status e response ausentes
        }

        # Act
        dto = AnalyzeDocumentResponseDTO.from_mongo_record(mongo_record)

        # Assert
        assert dto.id == "507f1f77bcf86cd799439011"
        assert dto.document_name == "test.pdf"
        assert dto.status == "unknown"  # valor padrão
        assert dto.analysis_results == {}  # valor padrão
        assert dto.created_at == datetime(2024, 10, 28, 10, 30, 0)
        assert dto.user_email == "test@example.com"

    def test_dto_field_aliases(self):
        """Teste dos aliases de campos"""
        # Arrange
        data = {
            "_id": "507f1f77bcf86cd799439011",
            "file_name": "test.pdf",
            "status": "completed",
            "response": {"test": "data"},
            "created_at": datetime(2024, 10, 28, 10, 30, 0),
            "user_email": "test@example.com"
        }

        # Act
        dto = AnalyzeDocumentResponseDTO(**data)

        # Assert
        assert dto.document_name == "test.pdf"  # alias de file_name
        assert dto.analysis_results == {"test": "data"}  # alias de response

    def test_dto_json_serialization(self):
        """Teste de serialização JSON do DTO"""
        # Arrange
        dto = AnalyzeDocumentResponseDTO(
            id="507f1f77bcf86cd799439011",
            document_name="test.pdf",
            status="completed",
            analysis_results={"document_id": "doc_123"},
            created_at=datetime(2024, 10, 28, 10, 30, 0),
            user_email="test@example.com"
        )

        # Act
        json_data = dto.dict(by_alias=True)

        # Assert
        assert json_data["_id"] == "507f1f77bcf86cd799439011"  # usando alias
        assert json_data["file_name"] == "test.pdf"  # usando alias
        assert json_data["status"] == "completed"
        assert json_data["response"] == {"document_id": "doc_123"}  # usando alias
        assert json_data["user_email"] == "test@example.com"
        assert "created_at" in json_data

    def test_dto_with_enum_status(self):
        """Teste com status enum"""
        # Arrange
        record = AnalyzeDocumentRecord(
            user_email="test@example.com",
            file_name="test.pdf",
            response={},
            status=DocumentStatus.PENDING,
            created_at=datetime.now()
        )

        # Act
        dto = AnalyzeDocumentResponseDTO.from_analyze_document_record(record)

        # Assert
        assert dto.status == "pending"

    def test_dto_field_aliases(self):
        """Teste dos aliases de campos"""
        # Arrange
        data = {
            "_id": "507f1f77bcf86cd799439011",
            "file_name": "test.pdf",
            "status": "completed",
            "response": {"test": "data"},
            "created_at": datetime(2024, 10, 28, 10, 30, 0),
            "user_email": "test@example.com"
        }

        # Act
        dto = AnalyzeDocumentResponseDTO(**data)

        # Assert
        assert dto.document_name == "test.pdf"  # alias de file_name
        assert dto.analysis_results == {"test": "data"}  # alias de response
        assert dto.id == "507f1f77bcf86cd799439011"  # alias de _id