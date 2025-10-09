"""
Testes unitários para o método extract_with_fallback do ImageExtractionOrchestrator.
Transferido do AnalyzeService para o orquestrador na Fase 2.5.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile
from io import BytesIO
from app.services.image.extraction import ImageExtractionOrchestrator


class TestImageExtractionOrchestrator:
    """Testes para extract_with_fallback - método transferido do AnalyzeService"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.mock_file = MagicMock(spec=UploadFile)
        self.mock_file.filename = "test_document.pdf"
        self.mock_file.seek = AsyncMock()
        
        self.sample_azure_result = {
            "analyze_result": {
                "pages": [{"pageNumber": 1}],
                "figures": []
            }
        }
        
        self.document_id = "test_doc_123"

    @pytest.mark.asyncio
    @patch('app.services.image.extraction.image_extraction_orchestrator.ImageExtractionOrchestrator.extract_images_single_method')
    async def test_extract_with_fallback_success_manual_pdf(self, mock_extract_method):
        """
        Testa extração bem-sucedida com método principal (Manual PDF) - sem fallback necessário
        """
        # Arrange
        orchestrator = ImageExtractionOrchestrator()
        expected_images = {
            "image_1": "base64_encoded_image_1",
            "image_2": "base64_encoded_image_2"
        }
        mock_extract_method.return_value = expected_images
        
        # Act
        result = await orchestrator.extract_with_fallback(
            file=self.mock_file,
            document_analysis_result=self.sample_azure_result,
            document_id=self.document_id
        )
        
        # Assert
        assert result == expected_images
        assert mock_extract_method.call_count == 1
        
        # Verifica que o arquivo foi resetado
        assert self.mock_file.seek.call_count >= 2  # seek(0) inicial + após sucesso

    @pytest.mark.asyncio
    @patch('app.services.image.extraction.image_extraction_orchestrator.ImageExtractionOrchestrator.extract_images_single_method')
    async def test_extract_with_fallback_uses_azure_fallback(self, mock_extract_method):
        """
        Testa que usa fallback Azure quando método principal falha
        """
        # Arrange
        orchestrator = ImageExtractionOrchestrator()
        expected_azure_images = {
            "figure_1": "base64_azure_figure_1",
            "figure_2": "base64_azure_figure_2"
        }
        
        # Manual PDF retorna vazio, Azure Figures retorna imagens
        async def side_effect(*args, **kwargs):
            method_name = kwargs.get('method').name
            if method_name == 'MANUAL_PDF':
                return {}  # Manual PDF - vazio
            elif method_name == 'AZURE_FIGURES':
                return expected_azure_images  # Azure Figures - sucesso
        
        mock_extract_method.side_effect = side_effect
        
        # Act
        result = await orchestrator.extract_with_fallback(
            file=self.mock_file,
            document_analysis_result=self.sample_azure_result,
            document_id=self.document_id
        )
        
        # Assert
        assert result == expected_azure_images
        assert mock_extract_method.call_count == 2

    @pytest.mark.asyncio
    @patch('app.services.image.extraction.image_extraction_orchestrator.ImageExtractionOrchestrator.extract_images_single_method')
    async def test_extract_with_fallback_both_methods_fail(self, mock_extract_method):
        """
        Testa comportamento quando ambos os métodos falham - deve retornar dicionário vazio
        """
        # Arrange
        orchestrator = ImageExtractionOrchestrator()
        
        # Ambos os métodos retornam vazio
        mock_extract_method.return_value = {}
        
        # Act
        result = await orchestrator.extract_with_fallback(
            file=self.mock_file,
            document_analysis_result=self.sample_azure_result,
            document_id=self.document_id
        )
        
        # Assert
        assert result == {}
        assert mock_extract_method.call_count == 2

    @pytest.mark.asyncio  
    @patch('app.services.image.extraction.image_extraction_orchestrator.ImageExtractionOrchestrator.extract_images_single_method')
    async def test_extract_with_fallback_file_seek_calls(self, mock_extract_method):
        """
        Testa que o arquivo é resetado corretamente durante o processo
        """
        # Arrange
        orchestrator = ImageExtractionOrchestrator()
        mock_extract_method.return_value = {"image_1": "base64_image"}
        
        # Act
        await orchestrator.extract_with_fallback(
            file=self.mock_file,
            document_analysis_result=self.sample_azure_result,
            document_id=self.document_id
        )
        
        # Assert - verifica que seek(0) foi chamado múltiplas vezes
        assert self.mock_file.seek.call_count >= 2
        # Todas as chamadas devem ser seek(0)
        for call in self.mock_file.seek.call_args_list:
            assert call[0][0] == 0

    @pytest.mark.asyncio
    @patch('app.services.image.extraction.image_extraction_orchestrator.ImageExtractionOrchestrator.extract_images_single_method')
    async def test_extract_with_fallback_azure_result_passed_correctly(self, mock_extract_method):
        """
        Testa que o azure_result é passado corretamente
        """
        # Arrange
        orchestrator = ImageExtractionOrchestrator()
        mock_extract_method.return_value = {"image_1": "base64"}
        
        # Act
        await orchestrator.extract_with_fallback(
            file=self.mock_file,
            document_analysis_result=self.sample_azure_result,
            document_id=self.document_id
        )
        
        # Assert - verifica que azure_result foi passado corretamente
        call_args = mock_extract_method.call_args
        passed_azure_result = call_args[1]['document_analysis_result']
        assert passed_azure_result == self.sample_azure_result