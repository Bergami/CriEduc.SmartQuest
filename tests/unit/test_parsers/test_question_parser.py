"""
Unit tests for QuestionParser
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.parsers.question_parser import QuestionParser
from tests.fixtures.test_data import TestDataProvider, TestValidators


class TestQuestionParser(unittest.TestCase):
    """Test cases for QuestionParser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = TestDataProvider()
        self.validators = TestValidators()
        self.sample_question_text = self.test_data.get_sample_question_text()
        self.sample_context_text = self.test_data.get_sample_context_text()
    
    def test_extract_returns_dict(self):
        """Test that extract method returns a dictionary"""
        result = QuestionParser.extract(self.sample_question_text)
        self.assertIsInstance(result, dict)
    
    def test_extract_has_required_keys(self):
        """Test that extract result has required keys"""
        result = QuestionParser.extract(self.sample_question_text)
        required_keys = ["questions", "context_blocks"]
        for key in required_keys:
            self.assertIn(key, result)
    
    def test_extract_questions_is_list(self):
        """Test that questions is a list"""
        result = QuestionParser.extract(self.sample_question_text)
        self.assertIsInstance(result["questions"], list)
    
    def test_extract_context_blocks_is_list(self):
        """Test that context_blocks is a list"""
        result = QuestionParser.extract(self.sample_question_text)
        self.assertIsInstance(result["context_blocks"], list)
    
    def test_parse_single_question(self):
        """Test parsing a single question"""
        result = QuestionParser.extract(self.sample_question_text)
        questions = result["questions"]
        
        self.assertEqual(len(questions), 1)
        question = questions[0]
        
        # Validate question structure
        self.assertTrue(self.validators.is_valid_question(question))
        self.assertEqual(question["number"], 1)
        self.assertIn("discípulo", question["question"])
        self.assertEqual(len(question["alternatives"]), 5)
    
    def test_parse_question_alternatives(self):
        """Test parsing question alternatives"""
        result = QuestionParser.extract(self.sample_question_text)
        questions = result["questions"]
        
        if questions:
            question = questions[0]
            alternatives = question["alternatives"]
            
            # Check alternatives structure
            for i, alt in enumerate(alternatives):
                expected_letter = chr(ord('A') + i)
                self.assertEqual(alt["letter"], expected_letter)
                self.assertIn("text", alt)
                self.assertTrue(len(alt["text"]) > 0)
    
    def test_parse_with_context_blocks(self):
        """Test parsing with context blocks"""
        combined_text = self.sample_context_text + "\n\n" + self.sample_question_text
        result = QuestionParser.extract(combined_text)
        
        self.assertIsInstance(result["context_blocks"], list)
        # Should detect context blocks when present
    
    def test_parse_with_images(self):
        """Test parsing with image data"""
        image_data = {
            "figure_1": "base64_image_data"
        }
        result = QuestionParser.extract(self.sample_question_text, image_data)
        
        self.assertIsInstance(result, dict)
        # Should handle image data without errors
    
    def test_parse_empty_text(self):
        """Test parsing empty text"""
        result = QuestionParser.extract("")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["questions"]), 0)
        self.assertEqual(len(result["context_blocks"]), 0)
    
    def test_parse_malformed_text(self):
        """Test parsing malformed text"""
        malformed_text = "This is not a valid question format"
        result = QuestionParser.extract(malformed_text)
        
        self.assertIsInstance(result, dict)
        # Should not raise an exception
    
    def test_question_has_image_detection(self):
        """Test detection of questions with images"""
        text_with_image = """
        QUESTÃO 01
        Com base na imagem apresentada, qual é a resposta correta?
        (A) Opção A
        (B) Opção B
        (C) Opção C
        (D) Opção D
        (E) Opção E
        """
        
        result = QuestionParser.extract(text_with_image)
        questions = result["questions"]
        
        if questions:
            question = questions[0]
            self.assertIn("hasImage", question)
            self.assertTrue(question["hasImage"])
    
    def test_question_without_image_detection(self):
        """Test detection of questions without images"""
        result = QuestionParser.extract(self.sample_question_text)
        questions = result["questions"]
        
        if questions:
            question = questions[0]
            self.assertIn("hasImage", question)
            self.assertFalse(question["hasImage"])
    
    def test_context_id_assignment(self):
        """Test context ID assignment to questions"""
        combined_text = self.sample_context_text + "\n\n" + self.sample_question_text
        result = QuestionParser.extract(combined_text)
        
        questions = result["questions"]
        if questions:
            question = questions[0]
            self.assertIn("context_id", question)
            # Context ID should be assigned or None
    
    def test_multiple_questions_parsing(self):
        """Test parsing multiple questions"""
        multiple_questions_text = """
        QUESTÃO 01
        Primeira questão
        (A) Opção A
        (B) Opção B
        
        QUESTÃO 02
        Segunda questão
        (A) Opção A
        (B) Opção B
        """
        
        result = QuestionParser.extract(multiple_questions_text)
        questions = result["questions"]
        
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["number"], 1)
        self.assertEqual(questions[1]["number"], 2)


if __name__ == '__main__':
    unittest.main()
