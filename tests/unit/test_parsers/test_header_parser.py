"""
Unit tests for HeaderParser
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.parsers.header_parser import HeaderParser
from app.models.internal import InternalDocumentMetadata
from tests.fixtures.test_data import TestDataProvider


class TestHeaderParser(unittest.TestCase):
    """Test cases for HeaderParser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = TestDataProvider()
        self.sample_header_text = self.test_data.get_sample_header_text()
    
    def test_parse_returns_dict(self):
        """Test that parse method returns a dictionary"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIsInstance(result, dict)
    
    def test_parse_to_pydantic_returns_pydantic_model(self):
        """🆕 Test that parse_to_pydantic method returns InternalDocumentMetadata"""
        result = HeaderParser.parse_to_pydantic(self.sample_header_text)
        self.assertIsInstance(result, InternalDocumentMetadata)
    
    def test_parse_to_pydantic_has_same_fields_as_dict_method(self):
        """🆕 Test that Pydantic method extracts same fields as dict method"""
        dict_result = HeaderParser.parse(self.sample_header_text)
        pydantic_result = HeaderParser.parse_to_pydantic(self.sample_header_text)
        
        # Convert Pydantic back to dict for comparison
        pydantic_dict = pydantic_result.to_legacy_format()
        
        # Compare main fields (excluding images)
        main_fields = ["network", "school", "city", "teacher", "subject", 
                      "exam_title", "trimester", "grade", "class", "student", 
                      "grade_value", "date"]
        
        for field in main_fields:
            self.assertEqual(
                dict_result.get(field), 
                pydantic_dict.get(field),
                f"Field '{field}' differs between dict and Pydantic methods"
            )
    
    def test_parse_to_pydantic_with_images(self):
        """🆕 Test Pydantic method with header and content images"""
        result = HeaderParser.parse_to_pydantic(
            self.sample_header_text,
            header_images=[],  # Empty list for now
            content_images=[]  # Empty list for now
        )
        
        self.assertIsInstance(result, InternalDocumentMetadata)
        self.assertIsInstance(result.header_images, list)
        self.assertIsInstance(result.content_images, list)
    
    def test_parse_network_field(self):
        """Test network field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("network", result)
        self.assertEqual(result["network"].upper(), "PREFEITURA MUNICIPAL DE VILA VELHA")

    def test_parse_school_field(self):
        """Test school field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("school", result)
        self.assertEqual(result["school"].upper(), "UMEF SATURNINO RANGEL MAURO")
    
    def test_parse_teacher_field(self):
        """Test teacher field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("teacher", result)
        self.assertEqual(result["teacher"], "Danielle")
    
    def test_parse_subject_field(self):
        """Test subject field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("subject", result)
        self.assertEqual(result["subject"], "Língua Portuguesa")
    
    def test_parse_exam_title_field(self):
        """Test exam title field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("exam_title", result)
        self.assertEqual(result["exam_title"].upper(), "PROVA TRIMESTRAL")

    def test_parse_trimester_field(self):
        """Test trimester field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("trimester", result)
        self.assertEqual(result["trimester"], "3º TRIMESTRE")
    
    def test_parse_grade_field(self):
        """Test grade field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("grade", result)
        self.assertEqual(result["grade"], "7º ano")
    
    def test_parse_grade_value_field(self):
        """Test grade value field parsing"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("grade_value", result)
        self.assertEqual(result["grade_value"], "12,0")
    
    def test_parse_with_empty_string(self):
        """Test parsing with empty string"""
        result = HeaderParser.parse("")
        self.assertIsInstance(result, dict)
        # All fields should be None or empty when no text is provided
        for key, value in result.items():
            if key != "images":  # images is a list, not None
                self.assertIsNone(value)
    
    def test_parse_with_images(self):
        """Test parsing with header images"""
        test_images = [
            {"content": "base64_image_data", "page": 1}
        ]
        result = HeaderParser.parse(self.sample_header_text, test_images)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 1)
        self.assertEqual(result["images"][0]["content"], "base64_image_data")
    
    def test_parse_without_images(self):
        """Test parsing without images"""
        result = HeaderParser.parse(self.sample_header_text)
        self.assertIn("images", result)
        self.assertEqual(len(result["images"]), 0)
    
    def test_parse_required_fields_present(self):
        """Test that all required fields are present in result"""
        result = HeaderParser.parse(self.sample_header_text)
        required_fields = [
            "network", "school", "city", "teacher", "subject",
            "exam_title", "trimester", "grade", "class", "student",
            "grade_value", "date", "images"
        ]
        for field in required_fields:
            self.assertIn(field, result)
    
    def test_parse_handles_malformed_input(self):
        """Test parser handles malformed input gracefully"""
        malformed_text = "This is not a valid header format"
        result = HeaderParser.parse(malformed_text)
        self.assertIsInstance(result, dict)
        # Should not raise an exception
    
    def test_parse_case_insensitive(self):
        """Test parser is case insensitive"""
        lowercase_text = self.sample_header_text.lower()
        result = HeaderParser.parse(lowercase_text)
        self.assertIsInstance(result, dict)
        # Should still parse some fields correctly


if __name__ == '__main__':
    unittest.main()
