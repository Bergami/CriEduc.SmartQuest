"""
Testes unitários para DocumentResponseAdapter
"""

import pytest
from unittest.mock import Mock
from app.adapters.document_response_adapter import DocumentResponseAdapter
from app.models.internal.document_response import InternalDocumentResponse
from app.models.internal.document_metadata import InternalDocumentMetadata


class TestDocumentResponseAdapter:
    """Testes para o DocumentResponseAdapter"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.adapter = DocumentResponseAdapter()
    
    def test_to_api_response_with_complete_data(self):
        """Testa conversão com dados completos"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="João Silva",
            student_code="12345",
            evaluation_date="2024-01-15",
            subject="Matemática",
            institution="UFMG",
            city="Belo Horizonte"
        )
        
        internal_response = InternalDocumentResponse(
            metadata=metadata,
            questions=[
                {
                    "number": 1,
                    "text": "Qual é a soma de 2 + 2?",
                    "alternatives": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "topic": "Aritmética"
                },
                {
                    "number": 2, 
                    "text": "Resolva: 3 × 4",
                    "alternatives": ["10", "11", "12", "13"],
                    "correct_answer": "12",
                    "topic": "Multiplicação"
                }
            ],
            context_blocks=[
                {
                    "type": "instruction",
                    "content": "Resolva as questões a seguir",
                    "page": 1
                },
                {
                    "type": "explanation",
                    "content": "Lembre-se das operações básicas",
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
                "questions_extracted": 2,
                "context_blocks_found": 2
            }
        )
        
        # Act
        api_response = self.adapter.to_api_response(internal_response)
        
        # Assert
        assert "document_metadata" in api_response
        assert "questions" in api_response
        assert "context_blocks" in api_response
        assert "extracted_images" in api_response
        assert "processing_metadata" in api_response
        
        # Verificar metadata
        assert api_response["document_metadata"]["student_name"] == "João Silva"
        assert api_response["document_metadata"]["student_code"] == "12345"
        assert api_response["document_metadata"]["evaluation_date"] == "2024-01-15"
        assert api_response["document_metadata"]["subject"] == "Matemática"
        assert api_response["document_metadata"]["institution"] == "UFMG"
        assert api_response["document_metadata"]["city"] == "Belo Horizonte"
        
        # Verificar questions
        assert len(api_response["questions"]) == 2
        assert api_response["questions"][0]["number"] == 1
        assert api_response["questions"][0]["text"] == "Qual é a soma de 2 + 2?"
        assert api_response["questions"][1]["number"] == 2
        assert api_response["questions"][1]["text"] == "Resolva: 3 × 4"
        
        # Verificar context_blocks
        assert len(api_response["context_blocks"]) == 2
        assert api_response["context_blocks"][0]["type"] == "instruction"
        assert api_response["context_blocks"][1]["type"] == "explanation"
        
        # Verificar extracted_images
        assert len(api_response["extracted_images"]) == 1
        assert api_response["extracted_images"][0]["filename"] == "figure_1.png"
        assert api_response["extracted_images"][0]["source"] == "manual_extraction"
        
        # Verificar processing_metadata
        assert api_response["processing_metadata"]["total_pages"] == 2
        assert api_response["processing_metadata"]["processing_time_seconds"] == 1.5
        assert api_response["processing_metadata"]["extraction_method"] == "mock_with_images"
        assert api_response["processing_metadata"]["figures_found"] == 1
        assert api_response["processing_metadata"]["questions_extracted"] == 2
        assert api_response["processing_metadata"]["context_blocks_found"] == 2
    
    def test_to_api_response_with_minimal_data(self):
        """Testa conversão com dados mínimos"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Ana Costa",
            student_code="67890",
            evaluation_date="2024-01-16",
            subject="Física",
            institution="USP",
            city="São Paulo"
        )
        
        internal_response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 1,
                "processing_time_seconds": 0.8,
                "extraction_method": "mock_text_only",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Act
        api_response = self.adapter.to_api_response(internal_response)
        
        # Assert
        assert len(api_response["questions"]) == 0
        assert len(api_response["context_blocks"]) == 0
        assert len(api_response["extracted_images"]) == 0
        assert api_response["document_metadata"]["student_name"] == "Ana Costa"
        assert api_response["processing_metadata"]["figures_found"] == 0
    
    def test_to_api_response_preserves_data_types(self):
        """Testa que os tipos de dados são preservados corretamente"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Carlos Oliveira",
            student_code="11111",
            evaluation_date="2024-01-17",
            subject="Química",
            institution="UNICAMP",
            city="Campinas"
        )
        
        internal_response = InternalDocumentResponse(
            metadata=metadata,
            questions=[
                {
                    "number": 1,
                    "text": "Questão com número inteiro",
                    "alternatives": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "topic": "Química Orgânica"
                }
            ],
            context_blocks=[],
            extracted_images=[],
            processing_metadata={
                "total_pages": 3,
                "processing_time_seconds": 2.7,
                "extraction_method": "azure_document_intelligence",
                "figures_found": 0,
                "questions_extracted": 1,
                "context_blocks_found": 0
            }
        )
        
        # Act
        api_response = self.adapter.to_api_response(internal_response)
        
        # Assert
        # Verificar tipos de dados
        assert isinstance(api_response["questions"][0]["number"], int)
        assert isinstance(api_response["questions"][0]["text"], str)
        assert isinstance(api_response["questions"][0]["alternatives"], list)
        assert isinstance(api_response["processing_metadata"]["total_pages"], int)
        assert isinstance(api_response["processing_metadata"]["processing_time_seconds"], float)
        assert isinstance(api_response["processing_metadata"]["figures_found"], int)
    
    def test_to_api_response_with_image_data(self):
        """Testa conversão incluindo dados de imagem"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Maria Santos",
            student_code="22222",
            evaluation_date="2024-01-18",
            subject="Biologia",
            institution="UFRJ",
            city="Rio de Janeiro"
        )
        
        internal_response = InternalDocumentResponse(
            metadata=metadata,
            questions=[],
            context_blocks=[],
            extracted_images=[
                {
                    "filename": "diagram_1.png",
                    "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                    "page": 1,
                    "dimensions": {"width": 200, "height": 150},
                    "source": "azure_extraction"
                },
                {
                    "filename": "graph_2.jpg",
                    "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A==",
                    "page": 2,
                    "dimensions": {"width": 300, "height": 200},
                    "source": "manual_extraction"
                }
            ],
            processing_metadata={
                "total_pages": 2,
                "processing_time_seconds": 3.2,
                "extraction_method": "hybrid",
                "figures_found": 2,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Act
        api_response = self.adapter.to_api_response(internal_response)
        
        # Assert
        assert len(api_response["extracted_images"]) == 2
        
        # Verificar primeira imagem
        img1 = api_response["extracted_images"][0]
        assert img1["filename"] == "diagram_1.png"
        assert img1["page"] == 1
        assert img1["dimensions"]["width"] == 200
        assert img1["dimensions"]["height"] == 150
        assert img1["source"] == "azure_extraction"
        assert "base64" in img1
        
        # Verificar segunda imagem
        img2 = api_response["extracted_images"][1]
        assert img2["filename"] == "graph_2.jpg"
        assert img2["page"] == 2
        assert img2["dimensions"]["width"] == 300
        assert img2["dimensions"]["height"] == 200
        assert img2["source"] == "manual_extraction"
        assert "base64" in img2
    
    def test_to_api_response_handles_none_values(self):
        """Testa que valores None são tratados corretamente"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Pedro Lima",
            student_code="33333",
            evaluation_date="2024-01-19",
            subject="História",
            institution="UFPE",
            city="Recife"
        )
        
        # Simular resposta com alguns campos None
        internal_response = InternalDocumentResponse(
            metadata=metadata,
            questions=None,  # Testar None
            context_blocks=None,  # Testar None
            extracted_images=[],
            processing_metadata={
                "total_pages": 1,
                "processing_time_seconds": 1.0,
                "extraction_method": "mock_text_only",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        )
        
        # Act
        api_response = self.adapter.to_api_response(internal_response)
        
        # Assert
        # Deve converter None para listas vazias
        assert api_response["questions"] == []
        assert api_response["context_blocks"] == []
        assert isinstance(api_response["extracted_images"], list)
    
    def test_adapter_is_singleton_pattern(self):
        """Testa que o adapter pode ser reutilizado (padrão singleton-like)"""
        # Arrange
        adapter1 = DocumentResponseAdapter()
        adapter2 = DocumentResponseAdapter()
        
        # Act & Assert
        # Ambos devem funcionar independentemente
        assert adapter1 is not None
        assert adapter2 is not None
        assert hasattr(adapter1, 'to_api_response')
        assert hasattr(adapter2, 'to_api_response')
