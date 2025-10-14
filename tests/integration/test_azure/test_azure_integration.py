"""
Integration tests for Azure Document Intelligence service
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.azure.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.core.exceptions import DocumentProcessingError
from azure.core.exceptions import HttpResponseError
from tests.fixtures.test_data import TestDataProvider


class TestAzureDocumentIntelligenceIntegration(unittest.TestCase):
    """Integration tests for Azure Document Intelligence service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Don't initialize service here as it may fail without proper config
        # Initialize service in individual tests with proper mocking
        self.test_data = TestDataProvider()
        
        # Mock service for most tests
        with patch('app.services.azure_document_intelligence_service.settings') as mock_settings:
            mock_settings.azure_document_intelligence_endpoint = "https://test.cognitiveservices.azure.com/"
            mock_settings.azure_document_intelligence_key = "test-key"
            mock_settings.azure_document_intelligence_model = "prebuilt-layout"
            self.service = AzureDocumentIntelligenceService()
    
    def test_client_initialization(self):
        """Test Azure client initialization"""
        self.assertIsNotNone(self.service.client)
        self.assertIsNotNone(self.service.endpoint)
        self.assertIsNotNone(self.service.key)
    
    def test_extract_text_from_pdf_success(self):
        """Test successful text extraction from PDF"""
        mock_result = Mock()
        mock_result.content = "Sample extracted text\nLine 2\nLine 3"
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf(pdf_bytes)
            
            self.assertEqual(result, "Sample extracted text\nLine 2\nLine 3")
            mock_analyze.assert_called_once_with(
                model_id="prebuilt-read", 
                analyze_request=pdf_bytes,
                content_type="application/pdf"
            )
    
    def test_extract_text_from_pdf_empty_result(self):
        """Test text extraction with empty result"""
        mock_result = Mock()
        mock_result.content = ""
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf(pdf_bytes)
            
            self.assertEqual(result, "")
    
    def test_extract_text_from_pdf_none_result(self):
        """Test text extraction with None result"""
        mock_result = Mock()
        mock_result.content = None
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf(pdf_bytes)
            
            self.assertEqual(result, "")
    
    def test_extract_text_from_pdf_http_error(self):
        """Test text extraction with HTTP error"""
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.side_effect = HttpResponseError("HTTP error occurred")
            
            pdf_bytes = b"mock pdf content"
            
            with self.assertRaises(DocumentProcessingError) as context:
                self.service.extract_text_from_pdf(pdf_bytes)
            
            self.assertIn("Error extracting text from PDF", str(context.exception))
    
    def test_extract_text_from_pdf_generic_error(self):
        """Test text extraction with generic error"""
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.side_effect = Exception("Generic error")
            
            pdf_bytes = b"mock pdf content"
            
            with self.assertRaises(DocumentProcessingError) as context:
                self.service.extract_text_from_pdf(pdf_bytes)
            
            self.assertIn("Error extracting text from PDF", str(context.exception))
    
    def test_extract_text_from_pdf_with_coordinates_success(self):
        """Test successful text extraction with coordinates"""
        mock_result = Mock()
        mock_result.content = "Sample text with coordinates"
        
        # Mock pages and lines structure
        mock_page = Mock()
        mock_line1 = Mock()
        mock_line1.content = "Line 1"
        mock_line1.polygon = [
            Mock(x=100, y=100),
            Mock(x=200, y=100),
            Mock(x=200, y=120),
            Mock(x=100, y=120)
        ]
        
        mock_line2 = Mock()
        mock_line2.content = "Line 2"
        mock_line2.polygon = [
            Mock(x=100, y=150),
            Mock(x=200, y=150),
            Mock(x=200, y=170),
            Mock(x=100, y=170)
        ]
        
        mock_page.lines = [mock_line1, mock_line2]
        mock_result.pages = [mock_page]
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            self.assertIn("full_text", result)
            self.assertIn("pages", result)
            self.assertEqual(result["full_text"], "Sample text with coordinates")
            self.assertEqual(len(result["pages"]), 1)
            self.assertEqual(len(result["pages"][0]["lines"]), 2)
    
    def test_extract_text_from_pdf_with_coordinates_empty_pages(self):
        """Test text extraction with coordinates when no pages"""
        mock_result = Mock()
        mock_result.content = "Sample text"
        mock_result.pages = []
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            self.assertEqual(result["full_text"], "Sample text")
            self.assertEqual(len(result["pages"]), 0)
    
    def test_extract_text_from_pdf_with_coordinates_no_lines(self):
        """Test text extraction with coordinates when no lines"""
        mock_result = Mock()
        mock_result.content = "Sample text"
        
        mock_page = Mock()
        mock_page.lines = []
        mock_result.pages = [mock_page]
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            self.assertEqual(result["full_text"], "Sample text")
            self.assertEqual(len(result["pages"]), 1)
            self.assertEqual(len(result["pages"][0]["lines"]), 0)
    
    def test_extract_text_from_pdf_with_coordinates_error(self):
        """Test text extraction with coordinates handling errors"""
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.side_effect = HttpResponseError("HTTP error")
            
            pdf_bytes = b"mock pdf content"
            
            with self.assertRaises(DocumentProcessingError) as context:
                self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            self.assertIn("Error extracting text with coordinates from PDF", str(context.exception))
    
    def test_service_configuration_validation(self):
        """Test service configuration validation"""
        # Test with valid configuration
        with patch('app.services.azure_document_intelligence_service.settings') as mock_settings:
            mock_settings.azure_document_intelligence_endpoint = "https://test.cognitiveservices.azure.com/"
            mock_settings.azure_document_intelligence_key = "test-key"
            mock_settings.azure_document_intelligence_model = "prebuilt-layout"
            
            service = AzureDocumentIntelligenceService()
            self.assertEqual(service.endpoint, "https://test.cognitiveservices.azure.com/")
            self.assertEqual(service.key, "test-key")
    
    def test_service_with_missing_configuration(self):
        """Test service behavior with missing configuration"""
        with patch('app.services.azure_document_intelligence_service.settings') as mock_settings:
            mock_settings.azure_document_intelligence_endpoint = ""
            mock_settings.azure_document_intelligence_key = ""
            
            with self.assertRaises(ValueError) as context:
                AzureDocumentIntelligenceService()
            
            self.assertIn("Azure Document Intelligence credentials not configured", str(context.exception))
    
    def test_coordinate_extraction_accuracy(self):
        """Test coordinate extraction accuracy"""
        mock_result = Mock()
        mock_result.content = "Test content"
        
        mock_page = Mock()
        mock_line = Mock()
        mock_line.content = "Test line"
        mock_line.polygon = [
            Mock(x=10.5, y=20.3),
            Mock(x=110.7, y=20.3),
            Mock(x=110.7, y=35.8),
            Mock(x=10.5, y=35.8)
        ]
        
        mock_page.lines = [mock_line]
        mock_result.pages = [mock_page]
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock pdf content"
            result = self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            line_data = result["pages"][0]["lines"][0]
            self.assertEqual(line_data["content"], "Test line")
            self.assertEqual(len(line_data["polygon"]), 4)
            self.assertEqual(line_data["polygon"][0]["x"], 10.5)
            self.assertEqual(line_data["polygon"][0]["y"], 20.3)
    
    def test_large_document_handling(self):
        """Test handling of large documents"""
        mock_result = Mock()
        mock_result.content = "Large document content " * 1000
        
        # Create multiple pages
        mock_pages = []
        for i in range(5):
            mock_page = Mock()
            mock_page.lines = []
            for j in range(50):
                mock_line = Mock()
                mock_line.content = f"Page {i+1} Line {j+1}"
                mock_line.polygon = [
                    Mock(x=10, y=20 + j*15),
                    Mock(x=200, y=20 + j*15),
                    Mock(x=200, y=35 + j*15),
                    Mock(x=10, y=35 + j*15)
                ]
                mock_page.lines.append(mock_line)
            mock_pages.append(mock_page)
        
        mock_result.pages = mock_pages
        
        with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
            mock_analyze.return_value.result.return_value = mock_result
            
            pdf_bytes = b"mock large pdf content"
            result = self.service.extract_text_from_pdf_with_coordinates(pdf_bytes)
            
            self.assertEqual(len(result["pages"]), 5)
            self.assertEqual(len(result["pages"][0]["lines"]), 50)
            self.assertIn("Large document content", result["full_text"])
    
    def test_service_error_handling_robustness(self):
        """Test service error handling robustness"""
        error_scenarios = [
            ("Connection timeout", Exception("Connection timeout")),
            ("Authentication failed", HttpResponseError("Authentication failed")),
            ("Service unavailable", HttpResponseError("Service unavailable")),
            ("Rate limit exceeded", HttpResponseError("Rate limit exceeded")),
            ("Invalid document format", Exception("Invalid document format"))
        ]
        
        for error_name, error_exception in error_scenarios:
            with self.subTest(error=error_name):
                with patch.object(self.service.client, 'begin_analyze_document') as mock_analyze:
                    mock_analyze.side_effect = error_exception
                    
                    pdf_bytes = b"mock pdf content"
                    
                    with self.assertRaises(DocumentProcessingError):
                        self.service.extract_text_from_pdf(pdf_bytes)


if __name__ == '__main__':
    unittest.main()
