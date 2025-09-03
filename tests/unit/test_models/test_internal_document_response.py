"""
Testes unitários para InternalDocumentResponse
"""

import pytest
from pydantic import ValidationError
from app.models.internal.document_models import InternalDocumentResponse, InternalDocumentMetadata


class TestInternalDocumentResponse:
    """Testes para o modelo InternalDocumentResponse"""
    
    def test_create_with_valid_data(self):
        """Testa criação com dados válidos"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="João Silva",
            student_code="12345",
            evaluation_date="2024-01-15",
            subject="Matemática",
            institution="UFMG",
            city="Belo Horizonte"
        )
        
        # Act
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[
                {
                    "number": 1,
                    "text": "Qual é a soma de 2 + 2?",
                    "alternatives": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "topic": "Aritmética"
                }
            ],
            context_blocks=[
                {
                    "type": "instruction",
                    "content": "Resolva as questões a seguir",
                    "page": 1
                }
            ],
            extracted_images=[
                {
                    "filename": "figure_1.png",
                    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                    "page": 1,
                    "dimensions": {"width": 100, "height": 80},
                    "source": "manual_extraction"
                }
            ],
            processing_metadata={
                "total_pages": 2,
                "processing_time_seconds": 1.5,
                "extraction_method": "mock_with_images",
                "figures_found": 1,
                "questions_extracted": 1,
                "context_blocks_found": 1
            }
        )
        
        # Assert
        assert response.metadata == metadata
        assert len(response.questions) == 1
        assert response.questions[0]["number"] == 1
        assert len(response.context_blocks) == 1
        assert response.context_blocks[0]["type"] == "instruction"
        assert len(response.extracted_images) == 1
        assert response.extracted_images[0]["filename"] == "figure_1.png"
        assert response.processing_metadata["total_pages"] == 2
    
    def test_create_with_empty_lists(self):
        """Testa criação com listas vazias"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Ana Costa",
            student_code="67890",
            evaluation_date="2024-01-16",
            subject="Física",
            institution="USP",
            city="São Paulo"
        )
        
        # Act
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 1,
                "processing_time_seconds": 0.5,
                "extraction_method": "mock_text_only",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Assert
        assert len(response.questions) == 0
        assert len(response.context_blocks) == 0
        assert len(response.extracted_images) == 0
        assert response.processing_metadata["figures_found"] == 0
    
    def test_create_with_multiple_questions(self):
        """Testa criação com múltiplas questões"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Carlos Oliveira",
            student_code="11111",
            evaluation_date="2024-01-17",
            subject="Química",
            institution="UNICAMP",
            city="Campinas"
        )
        
        questions = [
            {
                "number": 1,
                "text": "Primeira questão",
                "alternatives": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "topic": "Química Orgânica"
            },
            {
                "number": 2,
                "text": "Segunda questão",
                "alternatives": ["1", "2", "3", "4"],
                "correct_answer": "3",
                "topic": "Química Inorgânica"
            },
            {
                "number": 3,
                "text": "Terceira questão",
                "alternatives": ["Sim", "Não", "Talvez", "Depende"],
                "correct_answer": "Sim",
                "topic": "Química Analítica"
            }
        ]
        
        # Act
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=questions,
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 3,
                "processing_time_seconds": 2.1,
                "extraction_method": "azure_document_intelligence",
                "figures_found": 0,
                "questions_extracted": 3,
                "context_blocks_found": 0
            }
        )
        
        # Assert
        assert len(response.questions) == 3
        assert response.questions[0]["number"] == 1
        assert response.questions[1]["number"] == 2
        assert response.questions[2]["number"] == 3
        assert response.questions[0]["topic"] == "Química Orgânica"
        assert response.questions[1]["topic"] == "Química Inorgânica"
        assert response.questions[2]["topic"] == "Química Analítica"
    
    def test_create_with_multiple_context_blocks(self):
        """Testa criação com múltiplos blocos de contexto"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Maria Santos",
            student_code="22222",
            evaluation_date="2024-01-18",
            subject="Biologia",
            institution="UFRJ",
            city="Rio de Janeiro"
        )
        
        context_blocks = [
            {
                "type": "instruction",
                "content": "Leia atentamente as instruções",
                "page": 1
            },
            {
                "type": "explanation",
                "content": "As questões seguem um padrão específico",
                "page": 1
            },
            {
                "type": "example",
                "content": "Exemplo: Uma célula eucarionte...",
                "page": 2
            },
            {
                "type": "note",
                "content": "Observação importante sobre mitose",
                "page": 2
            }
        ]
        
        # Act
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=context_blocks,
            extracted_images=[],
            processing_metadata={
                "total_pages": 2,
                "processing_time_seconds": 1.8,
                "extraction_method": "manual_extraction",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 4
            }
        )
        
        # Assert
        assert len(response.context_blocks) == 4
        assert response.context_blocks[0]["type"] == "instruction"
        assert response.context_blocks[1]["type"] == "explanation"
        assert response.context_blocks[2]["type"] == "example"
        assert response.context_blocks[3]["type"] == "note"
        assert all(block["page"] in [1, 2] for block in response.context_blocks)
    
    def test_create_with_multiple_images(self):
        """Testa criação com múltiplas imagens"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Pedro Lima",
            student_code="33333",
            evaluation_date="2024-01-19",
            subject="História",
            institution="UFPE",
            city="Recife"
        )
        
        images = [
            {
                "filename": "mapa_1.png",
                "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "page": 1,
                "dimensions": {"width": 400, "height": 300},
                "source": "azure_extraction"
            },
            {
                "filename": "grafico_2.jpg",
                "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/4",
                "page": 2,
                "dimensions": {"width": 350, "height": 250},
                "source": "manual_extraction"
            },
            {
                "filename": "diagrama_3.png",
                "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAYAAABWKLW/AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAdSURBVAiZY2RgYPgPBAxAwMgABP//MzJgAzAODAAAaAYHA7r0XJUAAAAASUVORK5CYII=",
                "page": 3,
                "dimensions": {"width": 200, "height": 180},
                "source": "hybrid"
            }
        ]
        
        # Act
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=[],
            extracted_images=images,
            processing_metadata={
                "total_pages": 3,
                "processing_time_seconds": 4.2,
                "extraction_method": "hybrid",
                "figures_found": 3,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Assert
        assert len(response.extracted_images) == 3
        assert response.extracted_images[0]["filename"] == "mapa_1.png"
        assert response.extracted_images[1]["filename"] == "grafico_2.jpg"
        assert response.extracted_images[2]["filename"] == "diagrama_3.png"
        assert response.extracted_images[0]["source"] == "azure_extraction"
        assert response.extracted_images[1]["source"] == "manual_extraction"
        assert response.extracted_images[2]["source"] == "hybrid"
    
    def test_validation_requires_metadata(self):
        """Testa que metadata é obrigatório"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                questions=[],
                context_blocks=[],
                extracted_images=[],
                processing_metadata={}
            )
        
        assert "metadata" in str(exc_info.value)
    
    def test_validation_requires_processing_metadata(self):
        """Testa que processing_metadata é obrigatório"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Teste",
            student_code="12345",
            evaluation_date="2024-01-01",
            subject="Teste",
            institution="Teste",
            city="Teste"
        )
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                metadata=metadata,
                questions=[],
                context_blocks=[],
                extracted_images=[]
            )
        
        assert "processing_metadata" in str(exc_info.value)
    
    def test_to_dict_method(self):
        """Testa o método to_dict se existir"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Teste Dict",
            student_code="99999",
            evaluation_date="2024-01-20",
            subject="Teste",
            institution="Teste Dict",
            city="Cidade Teste"
        )
        
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[
                {
                    "number": 1,
                    "text": "Questão teste",
                    "alternatives": ["A", "B"],
                    "correct_answer": "A",
                    "topic": "Teste"
                }
            ],
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 1,
                "processing_time_seconds": 1.0,
                "extraction_method": "test",
                "figures_found": 0,
                "questions_extracted": 1,
                "context_blocks_found": 0
            }
        )
        
        # Act
        if hasattr(response, 'to_dict'):
            result_dict = response.to_dict()
            
            # Assert
            assert isinstance(result_dict, dict)
            assert "metadata" in result_dict
            assert "questions" in result_dict
            assert "context_blocks" in result_dict
            assert "extracted_images" in result_dict
            assert "processing_metadata" in result_dict
        else:
            # Se não tem to_dict, usar dict() do Pydantic
            result_dict = response.model_dump()
            assert isinstance(result_dict, dict)
    
    def test_model_serialization(self):
        """Testa serialização do modelo"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Serialization Test",
            student_code="77777",
            evaluation_date="2024-01-21",
            subject="Serialização",
            institution="Teste Univ",
            city="Test City"
        )
        
        response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 1,
                "processing_time_seconds": 0.5,
                "extraction_method": "test_serialization",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Act
        json_str = response.model_dump_json()
        
        # Assert
        assert isinstance(json_str, str)
        assert "metadata" in json_str
        assert "Serialization Test" in json_str
        assert "test_serialization" in json_str
