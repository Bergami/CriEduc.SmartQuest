"""
Testes unitários para novos métodos do AnalyzeService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.analyze_service import AnalyzeService
from app.models.internal.document_models import InternalDocumentResponse, InternalDocumentMetadata


class TestAnalyzeServiceWithModels:
    """Testes para os novos métodos do AnalyzeService usando modelos Pydantic"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.analyze_service = AnalyzeService()
    
    @patch('app.services.analyze_service.AnalyzeService._get_document_service')
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_mock_text_only(self, mock_extract_metadata, mock_get_service):
        """Testa process_document_with_models com mock text only"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "test_document.pdf"
        mock_file.read.return_value = b"PDF content"
        
        # Mock metadata extraction
        mock_extract_metadata.return_value = {
            "student_name": "João Silva",
            "student_code": "12345",
            "evaluation_date": "2024-01-15",
            "subject": "Matemática",
            "institution": "UFMG",
            "city": "Belo Horizonte"
        }
        
        # Mock document service
        mock_document_service = Mock()
        mock_document_service.process_document_mock_text_only.return_value = {
            "questions": [
                {
                    "number": 1,
                    "text": "Qual é a soma de 2 + 2?",
                    "alternatives": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "topic": "Aritmética"
                }
            ],
            "context_blocks": [
                {
                    "type": "instruction",
                    "content": "Resolva as questões a seguir",
                    "page": 1
                }
            ],
            "extracted_images": [],
            "processing_metadata": {
                "total_pages": 1,
                "processing_time_seconds": 1.2,
                "extraction_method": "mock_text_only",
                "figures_found": 0,
                "questions_extracted": 1,
                "context_blocks_found": 1
            }
        }
        mock_get_service.return_value = mock_document_service
        
        # Act
        result = self.analyze_service.process_document_with_models(
            file=mock_file,
            use_mock=True,
            include_images=False
        )
        
        # Assert
        assert isinstance(result, InternalDocumentResponse)
        assert isinstance(result.metadata, InternalDocumentMetadata)
        
        # Verificar metadata
        assert result.metadata.student_name == "João Silva"
        assert result.metadata.student_code == "12345"
        assert result.metadata.evaluation_date == "2024-01-15"
        assert result.metadata.subject == "Matemática"
        assert result.metadata.institution == "UFMG"
        assert result.metadata.city == "Belo Horizonte"
        
        # Verificar questions
        assert len(result.questions) == 1
        assert result.questions[0]["number"] == 1
        assert result.questions[0]["text"] == "Qual é a soma de 2 + 2?"
        
        # Verificar context_blocks
        assert len(result.context_blocks) == 1
        assert result.context_blocks[0]["type"] == "instruction"
        
        # Verificar extracted_images
        assert len(result.extracted_images) == 0
        
        # Verificar processing_metadata
        assert result.processing_metadata["extraction_method"] == "mock_text_only"
        assert result.processing_metadata["figures_found"] == 0
        assert result.processing_metadata["questions_extracted"] == 1
        
        # Verificar chamadas dos mocks
        mock_document_service.process_document_mock_text_only.assert_called_once()
        mock_extract_metadata.assert_called_once()
    
    @patch('app.services.analyze_service.AnalyzeService._get_document_service')
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_mock_with_images(self, mock_extract_metadata, mock_get_service):
        """Testa process_document_with_models com mock incluindo imagens"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "test_document_with_images.pdf"
        mock_file.read.return_value = b"PDF content with images"
        
        # Mock metadata extraction
        mock_extract_metadata.return_value = {
            "student_name": "Ana Costa",
            "student_code": "67890",
            "evaluation_date": "2024-01-16",
            "subject": "Física",
            "institution": "USP",
            "city": "São Paulo"
        }
        
        # Mock document service
        mock_document_service = Mock()
        mock_document_service.process_document_mock_images_only.return_value = {
            "questions": [
                {
                    "number": 1,
                    "text": "Analise o gráfico abaixo:",
                    "alternatives": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "topic": "Cinemática"
                }
            ],
            "context_blocks": [
                {
                    "type": "explanation",
                    "content": "Use o gráfico para responder",
                    "page": 1
                }
            ],
            "extracted_images": [
                {
                    "filename": "figure_1.png",
                    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                    "page": 1,
                    "dimensions": {"width": 300, "height": 200},
                    "source": "manual_extraction"
                }
            ],
            "processing_metadata": {
                "total_pages": 1,
                "processing_time_seconds": 2.5,
                "extraction_method": "mock_with_images",
                "figures_found": 1,
                "questions_extracted": 1,
                "context_blocks_found": 1
            }
        }
        mock_get_service.return_value = mock_document_service
        
        # Act
        result = self.analyze_service.process_document_with_models(
            file=mock_file,
            use_mock=True,
            include_images=True
        )
        
        # Assert
        assert isinstance(result, InternalDocumentResponse)
        
        # Verificar metadata
        assert result.metadata.student_name == "Ana Costa"
        assert result.metadata.subject == "Física"
        
        # Verificar extracted_images
        assert len(result.extracted_images) == 1
        assert result.extracted_images[0]["filename"] == "figure_1.png"
        assert result.extracted_images[0]["source"] == "manual_extraction"
        
        # Verificar processing_metadata
        assert result.processing_metadata["extraction_method"] == "mock_with_images"
        assert result.processing_metadata["figures_found"] == 1
        
        # Verificar chamadas dos mocks
        mock_document_service.process_document_mock_images_only.assert_called_once()
    
    @patch('app.services.analyze_service.AnalyzeService._get_document_service')
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_azure_service(self, mock_extract_metadata, mock_get_service):
        """Testa process_document_with_models com Azure Document Intelligence"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "azure_test_document.pdf"
        mock_file.read.return_value = b"PDF content for Azure"
        
        # Mock metadata extraction
        mock_extract_metadata.return_value = {
            "student_name": "Carlos Oliveira",
            "student_code": "11111",
            "evaluation_date": "2024-01-17",
            "subject": "Química",
            "institution": "UNICAMP",
            "city": "Campinas"
        }
        
        # Mock document service (Azure)
        mock_document_service = Mock()
        mock_document_service.process_document.return_value = {
            "questions": [
                {
                    "number": 1,
                    "text": "Qual é a fórmula da água?",
                    "alternatives": ["H2O", "CO2", "NaCl", "CaCO3"],
                    "correct_answer": "H2O",
                    "topic": "Química Básica"
                },
                {
                    "number": 2,
                    "text": "Quantos átomos tem o metano?",
                    "alternatives": ["3", "4", "5", "6"],
                    "correct_answer": "5",
                    "topic": "Química Orgânica"
                }
            ],
            "context_blocks": [
                {
                    "type": "instruction",
                    "content": "Responda as questões sobre química",
                    "page": 1
                },
                {
                    "type": "note",
                    "content": "Considere as fórmulas moleculares",
                    "page": 1
                }
            ],
            "extracted_images": [
                {
                    "filename": "molecular_structure.png",
                    "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAMAAAADCAYAAABWKLW/AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAAdSURBVAiZY2RgYPgPBAxAwMgABP//MzJgAzAODAAAaAYHA7r0XJUAAAAASUVORK5CYII=",
                    "page": 1,
                    "dimensions": {"width": 250, "height": 180},
                    "source": "azure_extraction"
                }
            ],
            "processing_metadata": {
                "total_pages": 1,
                "processing_time_seconds": 4.2,
                "extraction_method": "azure_document_intelligence",
                "figures_found": 1,
                "questions_extracted": 2,
                "context_blocks_found": 2
            }
        }
        mock_get_service.return_value = mock_document_service
        
        # Act
        result = self.analyze_service.process_document_with_models(
            file=mock_file,
            use_mock=False,
            include_images=True
        )
        
        # Assert
        assert isinstance(result, InternalDocumentResponse)
        
        # Verificar metadata
        assert result.metadata.student_name == "Carlos Oliveira"
        assert result.metadata.subject == "Química"
        
        # Verificar questions
        assert len(result.questions) == 2
        assert result.questions[0]["topic"] == "Química Básica"
        assert result.questions[1]["topic"] == "Química Orgânica"
        
        # Verificar context_blocks
        assert len(result.context_blocks) == 2
        
        # Verificar extracted_images
        assert len(result.extracted_images) == 1
        assert result.extracted_images[0]["source"] == "azure_extraction"
        
        # Verificar processing_metadata
        assert result.processing_metadata["extraction_method"] == "azure_document_intelligence"
        assert result.processing_metadata["questions_extracted"] == 2
        
        # Verificar chamadas dos mocks
        mock_document_service.process_document.assert_called_once()
    
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_handles_metadata_extraction_error(self, mock_extract_metadata):
        """Testa tratamento de erro na extração de metadata"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "error_document.pdf"
        mock_file.read.return_value = b"PDF content"
        
        # Mock erro na extração de metadata
        mock_extract_metadata.side_effect = Exception("Erro na extração de metadata")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.analyze_service.process_document_with_models(
                file=mock_file,
                use_mock=True,
                include_images=False
            )
        
        assert "Erro na extração de metadata" in str(exc_info.value)
    
    @patch('app.services.analyze_service.AnalyzeService._get_document_service')
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_handles_processing_error(self, mock_extract_metadata, mock_get_service):
        """Testa tratamento de erro no processamento do documento"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "error_processing.pdf"
        mock_file.read.return_value = b"PDF content"
        
        # Mock metadata extraction
        mock_extract_metadata.return_value = {
            "student_name": "Teste Erro",
            "student_code": "ERROR-001",
            "evaluation_date": "2024-01-18",
            "subject": "Teste",
            "institution": "Teste",
            "city": "Teste"
        }
        
        # Mock erro no document service
        mock_document_service = Mock()
        mock_document_service.process_document_mock_text_only.side_effect = Exception("Erro no processamento")
        mock_get_service.return_value = mock_document_service
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.analyze_service.process_document_with_models(
                file=mock_file,
                use_mock=True,
                include_images=False
            )
        
        assert "Erro no processamento" in str(exc_info.value)
    
    @patch('app.services.analyze_service.AnalyzeService._get_document_service')
    @patch('app.services.analyze_service.AnalyzeService._extract_document_metadata')
    def test_process_document_with_models_creates_valid_pydantic_objects(self, mock_extract_metadata, mock_get_service):
        """Testa que o método cria objetos Pydantic válidos"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "validation_test.pdf"
        mock_file.read.return_value = b"PDF content"
        
        # Mock metadata extraction
        mock_extract_metadata.return_value = {
            "student_name": "Validation Test",
            "student_code": "VAL-001",
            "evaluation_date": "2024-01-19",
            "subject": "Validação",
            "institution": "Test University",
            "city": "Test City"
        }
        
        # Mock document service
        mock_document_service = Mock()
        mock_document_service.process_document_mock_text_only.return_value = {
            "questions": [],
            "context_blocks": [],
            "extracted_images": [],
            "processing_metadata": {
                "total_pages": 1,
                "processing_time_seconds": 1.0,
                "extraction_method": "mock_text_only",
                "figures_found": 0,
                "questions_extracted": 0,
                "context_blocks_found": 0
            }
        }
        mock_get_service.return_value = mock_document_service
        
        # Act
        result = self.analyze_service.process_document_with_models(
            file=mock_file,
            use_mock=True,
            include_images=False
        )
        
        # Assert
        # Verificar que são objetos Pydantic válidos
        assert hasattr(result, 'model_dump')  # Método do Pydantic
        assert hasattr(result, 'model_validate')  # Método do Pydantic
        assert hasattr(result.metadata, 'model_dump')  # Método do Pydantic
        
        # Verificar que podem ser serializados
        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        assert "Validation Test" in json_str
        
        # Verificar que podem ser convertidos para dict
        dict_data = result.model_dump()
        assert isinstance(dict_data, dict)
        assert "metadata" in dict_data
        assert "questions" in dict_data
