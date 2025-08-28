"""
Test for the new analyze_document_with_figures endpoint.
This test validates the image extraction comparison functionality.
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAnalyzeDocumentWithFigures:
    """Test suite for the analyze_document_with_figures endpoint."""
    
    def create_dummy_pdf(self) -> tempfile.NamedTemporaryFile:
        """Create a simple dummy PDF for testing."""
        # Create a minimal PDF content (this is a very basic PDF)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
186
%%EOF"""
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(pdf_content)
        temp_file.seek(0)
        return temp_file
    
    @pytest.mark.asyncio
    async def test_analyze_document_with_figures_manual_method(self):
        """Test the endpoint with manual PDF extraction method."""
        temp_file = self.create_dummy_pdf()
        
        try:
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/analyze/analyze_document_with_figures",
                    params={
                        "email": "test@example.com",
                        "extraction_method": "manual_pdf",
                        "compare_methods": False,
                        "use_refactored": True
                    },
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            # Should return 200 even if no figures are found
            assert response.status_code == 200
            
            result = response.json()
            
            # Check basic structure
            assert "image_data" in result
            assert "image_extraction_metrics" in result
            assert result["image_extraction_metrics"]["method_used"] == "manual_pdf"
            
        finally:
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_analyze_document_with_figures_comparison_mode(self):
        """Test the endpoint with comparison mode enabled."""
        temp_file = self.create_dummy_pdf()
        
        try:
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/analyze/analyze_document_with_figures",
                    params={
                        "email": "test@example.com",
                        "extraction_method": "manual_pdf",
                        "compare_methods": True,
                        "use_refactored": True
                    },
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            # Should return 200 even if no figures are found
            assert response.status_code == 200
            
            result = response.json()
            
            # Check comparison structure
            assert "image_extraction_comparison" in result
            comparison = result["image_extraction_comparison"]
            
            assert "extraction_results" in comparison
            assert "performance_metrics" in comparison
            assert "comparison_summary" in comparison
            
            # Should have results from both methods
            assert "manual_pdf" in comparison["extraction_results"]
            assert "azure_figures" in comparison["extraction_results"]
            
        finally:
            os.unlink(temp_file.name)
    
    def test_analyze_document_with_figures_invalid_method(self):
        """Test the endpoint with invalid extraction method."""
        temp_file = self.create_dummy_pdf()
        
        try:
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/analyze/analyze_document_with_figures",
                    params={
                        "email": "test@example.com",
                        "extraction_method": "invalid_method",
                        "compare_methods": False
                    },
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            # Should return validation error
            assert response.status_code == 422
            
            result = response.json()
            assert "detail" in result
            
        finally:
            os.unlink(temp_file.name)
    
    def test_analyze_document_with_figures_missing_file(self):
        """Test the endpoint without providing a file."""
        response = client.post(
            "/analyze/analyze_document_with_figures",
            params={
                "email": "test@example.com",
                "extraction_method": "manual_pdf"
            }
        )
        
        # Should return validation error for missing file
        assert response.status_code == 422
    
    def test_analyze_document_with_figures_invalid_email(self):
        """Test the endpoint with invalid email."""
        temp_file = self.create_dummy_pdf()
        
        try:
            with open(temp_file.name, "rb") as f:
                response = client.post(
                    "/analyze/analyze_document_with_figures",
                    params={
                        "email": "invalid-email",
                        "extraction_method": "manual_pdf"
                    },
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            # Should return validation error
            assert response.status_code == 422
            
        finally:
            os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
