"""
Unit tests for AnalyzeService
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.analyze_service import AnalyzeService
from app.core.exceptions import DocumentProcessingError
from tests.fixtures.test_data import TestDataProvider, TestValidators


class TestAnalyzeService(unittest.TestCase):
    """Test cases for AnalyzeService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = TestDataProvider()
        self.validators = TestValidators()
    
    def test_generate_mock_image_base64(self):
        """Test mock image generation"""
        mock_image = AnalyzeService._generate_mock_image_base64()
        
        self.assertIsInstance(mock_image, str)
        self.assertGreater(len(mock_image), 0)
        
        # Should be valid base64
        import base64
        try:
            base64.b64decode(mock_image)
        except Exception:
            self.fail("Generated mock image is not valid base64")
    
    def test_is_header_image_with_header_elements(self):
        """Test _is_header_image with header elements"""
        mock_figure = {
            "boundingRegions": [{"pageNumber": 1}],
            "spans": [{"offset": 0, "length": 10}]
        }
        
        mock_azure_result = {
            "paragraphs": [
                {"role": "pageHeader", "spans": [{"offset": 0, "length": 10}]}
            ]
        }
        
        result = AnalyzeService._is_header_image(mock_figure, mock_azure_result)
        self.assertTrue(result)
    
    def test_is_header_image_with_position_fallback(self):
        """Test _is_header_image with position fallback"""
        mock_figure = {
            "boundingRegions": [{
                "pageNumber": 1,
                "polygon": [0.1, 0.1, 0.9, 0.1, 0.9, 0.2, 0.1, 0.2]  # Top of page
            }]
        }
        
        mock_azure_result = {"paragraphs": []}  # No header elements
        
        result = AnalyzeService._is_header_image(mock_figure, mock_azure_result)
        self.assertTrue(result)
    
    def test_is_header_image_not_header(self):
        """Test _is_header_image with non-header image"""
        mock_figure = {
            "boundingRegions": [{
                "pageNumber": 1,
                "polygon": [0.1, 0.5, 0.9, 0.5, 0.9, 0.8, 0.1, 0.8]  # Middle of page
            }]
        }
        
        mock_azure_result = {"paragraphs": []}  # No header elements
        
        result = AnalyzeService._is_header_image(mock_figure, mock_azure_result)
        self.assertFalse(result)
    
    def test_is_header_image_no_bounding_regions(self):
        """Test _is_header_image with no bounding regions"""
        mock_figure = {}
        mock_azure_result = {"paragraphs": []}
        
        result = AnalyzeService._is_header_image(mock_figure, mock_azure_result)
        self.assertFalse(result)
    
    def test_is_header_image_not_first_page(self):
        """Test _is_header_image with image not on first page"""
        mock_figure = {
            "boundingRegions": [{"pageNumber": 2}]
        }
        
        mock_azure_result = {"paragraphs": []}
        
        result = AnalyzeService._is_header_image(mock_figure, mock_azure_result)
        self.assertFalse(result)
    
    @patch('app.services.analyze_service.DocumentExtractionFactory')
    @patch('app.services.analyze_service.HeaderParser')
    @patch('app.services.analyze_service.QuestionParser')
    async def test_process_document_success(self, mock_question_parser, mock_header_parser, mock_factory):
        """Test successful document processing"""
        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")
        mock_file.seek = AsyncMock()
        
        # Mock extractor
        mock_extractor = Mock()
        mock_extractor.extract_document_data = AsyncMock(return_value={
            "text": "Sample text",
            "image_data": {},
            "metadata": {}
        })
        mock_factory.get_provider.return_value = mock_extractor
        
        # Mock parsers
        mock_header_parser.parse.return_value = self.test_data.get_expected_parsed_header()
        mock_question_parser.extract.return_value = {
            "questions": self.test_data.get_expected_question_data(),
            "context_blocks": []
        }
        
        # Execute
        result = await AnalyzeService.process_document(mock_file, "test@example.com")
        
        # Verify
        self.assertIsInstance(result, dict)
        self.assertTrue(self.validators.is_valid_pdf_response(result))
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["filename"], "test.pdf")
    
    @patch('app.services.analyze_service.DocumentExtractionFactory')
    async def test_process_document_extraction_error(self, mock_factory):
        """Test document processing with extraction error"""
        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        
        # Mock extractor that raises exception
        mock_extractor = Mock()
        mock_extractor.extract_document_data = AsyncMock(side_effect=Exception("Extraction failed"))
        mock_factory.get_provider.return_value = mock_extractor
        
        # Execute and verify exception
        with self.assertRaises(DocumentProcessingError):
            await AnalyzeService.process_document(mock_file, "test@example.com")
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open')
    @patch('app.services.analyze_service.HeaderParser')
    @patch('app.services.analyze_service.QuestionParser')
    async def test_process_document_mock_success(self, mock_question_parser, mock_header_parser, mock_open, mock_exists):
        """Test successful mock document processing"""
        # Mock JSON file content
        mock_json_content = """{
            "content": "Sample content",
            "figures": []
        }"""
        mock_file = Mock()
        mock_file.read.return_value = mock_json_content
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock parsers
        mock_header_parser.parse.return_value = self.test_data.get_expected_parsed_header()
        mock_question_parser.extract.return_value = {
            "questions": self.test_data.get_expected_question_data(),
            "context_blocks": []
        }
        
        # Execute
        result = await AnalyzeService.process_document_mock("test@example.com")
        
        # Verify
        self.assertIsInstance(result, dict)
        self.assertTrue(self.validators.is_valid_pdf_response(result))
        self.assertEqual(result["email"], "test@example.com")
    
    @patch('pathlib.Path.exists', return_value=False)
    async def test_process_document_mock_file_not_found(self, mock_exists):
        """Test mock document processing with file not found"""
        with self.assertRaises(DocumentProcessingError):
            await AnalyzeService.process_document_mock("test@example.com")
    
    @patch('app.services.analyze_service.DocumentExtractionFactory')
    @patch('app.services.analyze_service.HeaderParser')
    @patch('app.services.analyze_service.QuestionParser')
    async def test_process_document_with_images(self, mock_question_parser, mock_header_parser, mock_factory):
        """Test document processing with images"""
        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"PDF content")
        mock_file.seek = AsyncMock()
        
        # Mock extractor with images
        mock_extractor = Mock()
        mock_extractor.extract_document_data = AsyncMock(return_value={
            "text": "Sample text",
            "image_data": {"figure_1": "base64_image_data"},
            "metadata": {}
        })
        mock_factory.get_provider.return_value = mock_extractor
        
        # Mock parsers
        mock_header_parser.parse.return_value = self.test_data.get_expected_parsed_header()
        mock_question_parser.extract.return_value = {
            "questions": self.test_data.get_expected_question_data(),
            "context_blocks": []
        }
        
        # Execute
        result = await AnalyzeService.process_document(mock_file, "test@example.com")
        
        # Verify
        self.assertIsInstance(result, dict)
        self.assertTrue(self.validators.is_valid_pdf_response(result))
    
    def test_image_categorization_logic(self):
        """Test image categorization logic"""
        # Test header image (top of page)
        header_figure = {
            "boundingRegions": [{
                "pageNumber": 1,
                "polygon": [0.1, 0.1, 0.9, 0.1, 0.9, 0.2, 0.1, 0.2]
            }]
        }
        
        # Test content image (middle of page)
        content_figure = {
            "boundingRegions": [{
                "pageNumber": 1,
                "polygon": [0.1, 0.5, 0.9, 0.5, 0.9, 0.8, 0.1, 0.8]
            }]
        }
        
        mock_azure_result = {"paragraphs": []}
        
        self.assertTrue(AnalyzeService._is_header_image(header_figure, mock_azure_result))
        self.assertFalse(AnalyzeService._is_header_image(content_figure, mock_azure_result))


if __name__ == '__main__':
    unittest.main()
