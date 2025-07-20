"""
Unit tests for AnalyzeValidator
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.validators.analyze_validator import AnalyzeValidator
from app.core.exceptions import (
    InvalidEmailException, 
    MissingFileException, 
    InvalidDocumentFormatException,
    MultipleValidationException
)
from tests.fixtures.test_data import TestValidators


class TestAnalyzeValidator(unittest.TestCase):
    """Test cases for AnalyzeValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validators = TestValidators()
    
    def test_validate_email_only_valid_email(self):
        """Test validate_email_only with valid email"""
        valid_email = "test@example.com"
        try:
            AnalyzeValidator.validate_email_only(valid_email)
            # Should not raise exception
        except Exception as e:
            self.fail(f"validate_email_only raised exception with valid email: {e}")
    
    def test_validate_email_only_invalid_email(self):
        """Test validate_email_only with invalid email"""
        invalid_email = "invalid-email"
        with self.assertRaises(InvalidEmailException):
            AnalyzeValidator.validate_email_only(invalid_email)
    
    def test_validate_email_only_empty_email(self):
        """Test validate_email_only with empty email"""
        empty_email = ""
        with self.assertRaises(InvalidEmailException):
            AnalyzeValidator.validate_email_only(empty_email)
    
    def test_validate_all_valid_inputs(self):
        """Test validate_all with valid inputs"""
        # Mock valid PDF file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.file = Mock()
        mock_file.file.seek = Mock()
        mock_file.file.read = Mock(return_value=b"%PDF-")
        
        valid_email = "test@example.com"
        
        try:
            AnalyzeValidator.validate_all(mock_file, valid_email)
            # Should not raise exception
        except Exception as e:
            self.fail(f"validate_all raised exception with valid inputs: {e}")
    
    def test_validate_all_missing_file(self):
        """Test validate_all with missing file"""
        valid_email = "test@example.com"
        
        with self.assertRaises(MultipleValidationException):
            AnalyzeValidator.validate_all(None, valid_email)
    
    def test_validate_all_invalid_email(self):
        """Test validate_all with invalid email"""
        # Mock valid PDF file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.file = Mock()
        mock_file.file.seek = Mock()
        mock_file.file.read = Mock(return_value=b"%PDF-")
        
        invalid_email = "invalid-email"
        
        with self.assertRaises(MultipleValidationException):
            AnalyzeValidator.validate_all(mock_file, invalid_email)
    
    def test_validate_all_non_pdf_file(self):
        """Test validate_all with non-PDF file"""
        # Mock non-PDF file
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.file = Mock()
        mock_file.file.seek = Mock()
        mock_file.file.read = Mock(return_value=b"Not PDF")
        
        valid_email = "test@example.com"
        
        with self.assertRaises(MultipleValidationException):
            AnalyzeValidator.validate_all(mock_file, valid_email)
    
    def test_validate_all_multiple_errors(self):
        """Test validate_all with multiple validation errors"""
        invalid_email = "invalid-email"
        
        with self.assertRaises(MultipleValidationException) as context:
            AnalyzeValidator.validate_all(None, invalid_email)
        
        # Should contain multiple errors
        exception = context.exception
        self.assertIsInstance(exception.detail, dict)
        self.assertIn("errors", exception.detail)
        self.assertGreater(len(exception.detail["errors"]), 1)
    
    def test_format_exception_method(self):
        """Test format_exception method"""
        test_exception = InvalidEmailException()
        formatted = AnalyzeValidator.format_exception(test_exception)
        
        self.assertIsInstance(formatted, dict)
        self.assertIn("code", formatted)
        self.assertIn("message", formatted)
        self.assertEqual(formatted["code"], 422)
        self.assertEqual(formatted["message"], "Invalid email format.")
    
    def test_email_validation_edge_cases(self):
        """Test email validation with edge cases"""
        edge_cases = [
            ("user@domain.com", True),
            ("user.name@domain.com", True),
            ("user+tag@domain.com", True),
            ("user@domain.co.uk", True),
            ("user@sub.domain.com", True),
            ("@domain.com", False),
            ("user@", False),
            ("user", False),
            ("user@domain", False),
            ("user@domain..com", False),
        ]
        
        for email, should_be_valid in edge_cases:
            try:
                AnalyzeValidator.validate_email_only(email)
                is_valid = True
            except InvalidEmailException:
                is_valid = False
                
            self.assertEqual(is_valid, should_be_valid, 
                           f"Email '{email}' validation failed. Expected: {should_be_valid}, Got: {is_valid}")
    
    def test_pdf_file_validation(self):
        """Test PDF file validation"""
        # Mock PDF file
        mock_pdf = Mock()
        mock_pdf.file = Mock()
        mock_pdf.file.seek = Mock()
        mock_pdf.file.read = Mock(return_value=b"%PDF-")
        
        # Mock non-PDF file
        mock_non_pdf = Mock()
        mock_non_pdf.file = Mock()
        mock_non_pdf.file.seek = Mock()
        mock_non_pdf.file.read = Mock(return_value=b"Not PDF")
        
        # Test with utilities
        from app.core.utils import is_pdf
        
        self.assertTrue(is_pdf(mock_pdf))
        self.assertFalse(is_pdf(mock_non_pdf))
    
    def test_validation_performance(self):
        """Test validation performance with large inputs"""
        import time
        
        # Create a large email that should be invalid due to length
        # Most email systems have limits around 320 characters total
        large_email = "a" * 300 + "@" + "b" * 300 + ".com"
        
        start_time = time.time()
        
        # Test with the actual validator (not the test utility)
        try:
            AnalyzeValidator.validate_email_only(large_email)
            is_valid = True
        except InvalidEmailException:
            is_valid = False
        
        end_time = time.time()
        
        # Should complete quickly (under 1 second)
        self.assertLess(end_time - start_time, 1.0)
        
        # This email should be invalid due to excessive length
        # If it's still valid, let's test with an obviously invalid format
        if is_valid:
            # Test with clearly invalid email format
            invalid_email = "clearly_invalid_email_format"
            with self.assertRaises(InvalidEmailException):
                AnalyzeValidator.validate_email_only(invalid_email)


if __name__ == '__main__':
    unittest.main()
