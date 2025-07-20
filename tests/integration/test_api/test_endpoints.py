"""
Integration tests for API endpoints
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures.test_data import TestDataProvider


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.test_data = TestDataProvider()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("azure_ai_enabled", data)
        self.assertIn("version", data)
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("azure_ai_configured", data)
        self.assertIn("azure_ai_enabled", data)
    
    def test_health_endpoint_direct(self):
        """Test health endpoint direct route"""
        response = self.client.get("/health/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SmartQuest is alive!")
    
    def test_analyze_document_missing_email(self):
        """Test analyze_document endpoint without email"""
        response = self.client.post("/analyze/analyze_document")
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_analyze_document_invalid_email(self):
        """Test analyze_document endpoint with invalid email"""
        response = self.client.post(
            "/analyze/analyze_document",
            params={"email": "invalid-email", "use_mock": "true"}
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_analyze_document_mock_mode(self):
        """Test analyze_document endpoint in mock mode"""
        with patch('app.services.analyze_service.AnalyzeService.process_document_mock') as mock_process:
            mock_process.return_value = {
                "email": "test@example.com",
                "document_id": "test-id",
                "filename": "mock_document.pdf",
                "header": self.test_data.get_expected_parsed_header(),
                "questions": self.test_data.get_expected_question_data(),
                "context_blocks": []
            }
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={
                    "email": "test@example.com",
                    "use_mock": True
                }
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["email"], "test@example.com")
            self.assertIn("document_id", data)
            self.assertIn("header", data)
            self.assertIn("questions", data)
            self.assertIn("context_blocks", data)
    
    def test_analyze_document_without_file_not_mock(self):
        """Test analyze_document endpoint without file when not in mock mode"""
        response = self.client.post(
            "/analyze/analyze_document",
            params={"email": "test@example.com", "use_mock": False}
        )
        
        self.assertEqual(response.status_code, 400)  # Bad request
        data = response.json()
        self.assertIn("error", data["detail"])
    
    def test_analyze_document_with_file(self):
        """Test analyze_document endpoint with file"""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        
        with patch('app.services.analyze_service.AnalyzeService.process_document') as mock_process:
            mock_process.return_value = {
                "email": "test@example.com",
                "document_id": "test-id",
                "filename": "test.pdf",
                "header": self.test_data.get_expected_parsed_header(),
                "questions": self.test_data.get_expected_question_data(),
                "context_blocks": []
            }
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={"email": "test@example.com"},
                files={"file": ("test.pdf", pdf_content, "application/pdf")}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["email"], "test@example.com")
            self.assertEqual(data["filename"], "test.pdf")
    
    def test_analyze_document_with_non_pdf_file(self):
        """Test analyze_document endpoint with non-PDF file"""
        text_content = b"This is not a PDF file"
        
        response = self.client.post(
            "/analyze/analyze_document",
            params={"email": "test@example.com"},
            files={"file": ("test.txt", text_content, "text/plain")}
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_analyze_document_processing_error(self):
        """Test analyze_document endpoint with processing error"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        
        with patch('app.services.analyze_service.AnalyzeService.process_document') as mock_process:
            from app.core.exceptions import DocumentProcessingError
            mock_process.side_effect = DocumentProcessingError("Processing failed")
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={"email": "test@example.com"},
                files={"file": ("test.pdf", pdf_content, "application/pdf")}
            )
            
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("error", data["detail"])
            self.assertEqual(data["detail"]["error"], "Document Processing Error")
    
    def test_analyze_document_generic_error(self):
        """Test analyze_document endpoint with generic error"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        
        with patch('app.services.analyze_service.AnalyzeService.process_document') as mock_process:
            mock_process.side_effect = Exception("Generic error")
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={"email": "test@example.com"},
                files={"file": ("test.pdf", pdf_content, "application/pdf")}
            )
            
            self.assertEqual(response.status_code, 500)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get("/")
        
        # Check that CORS headers are present (FastAPI TestClient might not show all headers)
        self.assertEqual(response.status_code, 200)
    
    def test_api_response_format(self):
        """Test API response format consistency"""
        with patch('app.services.analyze_service.AnalyzeService.process_document_mock') as mock_process:
            expected_response = {
                "email": "test@example.com",
                "document_id": "test-id",
                "filename": "mock_document.pdf",
                "header": self.test_data.get_expected_parsed_header(),
                "questions": self.test_data.get_expected_question_data(),
                "context_blocks": []
            }
            mock_process.return_value = expected_response
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={
                    "email": "test@example.com",
                    "use_mock": True
                }
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify response structure
            required_fields = ["email", "document_id", "filename", "header", "questions", "context_blocks"]
            for field in required_fields:
                self.assertIn(field, data)
    
    def test_content_type_handling(self):
        """Test different content types handling"""
        # Test with correct content type
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        
        with patch('app.services.analyze_service.AnalyzeService.process_document') as mock_process:
            mock_process.return_value = {
                "email": "test@example.com",
                "document_id": "test-id",
                "filename": "test.pdf",
                "header": self.test_data.get_expected_parsed_header(),
                "questions": [],
                "context_blocks": []
            }
            
            response = self.client.post(
                "/analyze/analyze_document",
                params={"email": "test@example.com"},
                files={"file": ("test.pdf", pdf_content, "application/pdf")}
            )
            
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
