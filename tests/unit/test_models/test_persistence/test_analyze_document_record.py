"""
Testes unitários para o modelo AnalyzeDocumentRecord

Testa funcionalidades do modelo simplificado conforme prompt original:
- user_email, file_name, response, status
- Métodos: create_from_request, mark_completed, mark_failed
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from app.models.persistence.analyze_document_record import AnalyzeDocumentRecord
from app.models.persistence.enums import DocumentStatus


class TestAnalyzeDocumentRecord:
    """Testes para a classe AnalyzeDocumentRecord."""
    
    def test_create_from_request_basic(self):
        """Testa criação de registro básico."""
        user_email = "test@example.com"
        file_name = "document.pdf"
        response = {
            "document_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "completed",
            "context_blocks": [],
            "questions": []
        }
        
        record = AnalyzeDocumentRecord.create_from_request(
            user_email=user_email,
            file_name=file_name,
            file_size=1024,
            response=response
        )
        
        assert record.user_email == user_email
        assert record.file_name == file_name
        assert record.response == response
        assert record.status == DocumentStatus.PENDING
        assert record.id is not None
        assert isinstance(record.created_at, datetime)
    
    def test_create_from_request_with_status(self):
        """Testa criação com status específico."""
        user_email = "test@example.com"
        file_name = "document.pdf"
        response = {"result": "success"}
        status = DocumentStatus.COMPLETED
        
        record = AnalyzeDocumentRecord.create_from_request(
            user_email=user_email,
            file_name=file_name,
            file_size=2048,
            response=response,
            status=status
        )
        
        assert record.status == status
    
    def test_mark_completed(self):
        """Testa marcação como completado."""
        record = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=512,
            response={"result": "test"}
        )
        
        # Status inicial deve ser PENDING
        assert record.status == DocumentStatus.PENDING
        
        # Marcar como completado
        result = record.mark_completed()
        
        assert record.status == DocumentStatus.COMPLETED
        assert result is record  # Retorna self para chaining
    
    def test_mark_failed(self):
        """Testa marcação como falhado."""
        record = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=256,
            response={"result": "test"}
        )
        
        # Status inicial deve ser PENDING
        assert record.status == DocumentStatus.PENDING
        
        # Marcar como falhado
        result = record.mark_failed()
        
        assert record.status == DocumentStatus.FAILED
        assert result is record  # Retorna self para chaining
    
    def test_required_fields(self):
        """Testa que campos obrigatórios são validados."""
        # Deve funcionar com campos obrigatórios
        record = AnalyzeDocumentRecord(
            user_email="test@example.com",
            file_name="test.pdf",
            response={"result": "test"},
            status=DocumentStatus.PENDING
        )
        assert record.user_email == "test@example.com"
        assert record.file_name == "test.pdf"
        
        # Deve falhar sem campo obrigatório
        with pytest.raises(Exception):  # ValidationError do Pydantic
            AnalyzeDocumentRecord(
                file_name="test.pdf",
                response={"result": "test"}
                # user_email faltando
            )
    
    def test_config_example_structure(self):
        """Testa que exemplo na configuração está bem estruturado."""
        config = AnalyzeDocumentRecord.Config
        
        assert hasattr(config, 'schema_extra')
        assert 'example' in config.schema_extra
        
        example = config.schema_extra['example']
        
        # Verifica campos essenciais no exemplo
        assert 'user_email' in example
        assert 'file_name' in example
        assert 'response' in example
        assert 'status' in example
        
        # Verifica que response tem estrutura esperada
        response = example['response']
        assert 'document_id' in response
        assert 'status' in response
        assert 'context_blocks' in response
        assert 'questions' in response
    
    def test_inheritance_from_base_document(self):
        """Testa que AnalyzeDocumentRecord herda funcionalidades de BaseDocument."""
        record = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=128,
            response={"result": "test"}
        )
        
        # Deve ter campos herdados de BaseDocument
        assert hasattr(record, 'id')
        assert hasattr(record, 'created_at')
        assert record.id is not None
        assert isinstance(record.created_at, datetime)
    
    def test_response_field_flexibility(self):
        """Testa que campo response aceita estruturas JSON variadas."""
        # Response simples
        record1 = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="test.pdf",
            file_size=100,
            response={"status": "ok"}
        )
        assert record1.response == {"status": "ok"}
        
        # Response complexo
        complex_response = {
            "document_id": "123",
            "status": "completed",
            "context_blocks": [
                {
                    "id": 1,
                    "content": "Some text",
                    "coordinates": {"x": 10, "y": 20}
                }
            ],
            "questions": [
                {
                    "id": 1,
                    "text": "What is this?",
                    "type": "multiple_choice"
                }
            ],
            "metadata": {
                "processing_time": 1.5,
                "confidence": 0.95
            }
        }
        
        record2 = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="complex.pdf",
            file_size=5000,
            response=complex_response
        )
        assert record2.response == complex_response
    
    def test_status_workflow(self):
        """Testa fluxo completo de status."""
        # Criar como PENDING
        record = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="workflow.pdf",
            file_size=3000,
            response={"initial": "data"}
        )
        assert record.status == DocumentStatus.PENDING
        
        # Pode marcar como completado
        record.mark_completed()
        assert record.status == DocumentStatus.COMPLETED
        
        # Pode criar já como falhado
        failed_record = AnalyzeDocumentRecord.create_from_request(
            user_email="test@example.com",
            file_name="failed.pdf",
            file_size=2500,
            response={"error": "processing failed"},
            status=DocumentStatus.FAILED
        )
        assert failed_record.status == DocumentStatus.FAILED
        
        # Pode marcar um completado como falhado
        failed_record.mark_failed()
        assert failed_record.status == DocumentStatus.FAILED
