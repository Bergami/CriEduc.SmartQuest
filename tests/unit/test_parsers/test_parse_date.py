import unittest
from app.parsers.header_parser.parse_date import parse_date

class TestParseDate(unittest.TestCase):
    def test_valid_date(self):
        student_line = "Estudante: João Silva Data: 19/07/2025"
        self.assertEqual(parse_date(student_line), "19/07/2025")

    def test_no_date(self):
        student_line = "Estudante: João Silva"
        self.assertIsNone(parse_date(student_line))

    def test_invalid_date_format(self):
        student_line = "Estudante: João Silva Data: Julho 19, 2025"
        self.assertIsNone(parse_date(student_line))

    def test_empty_line(self):
        student_line = ""
        self.assertIsNone(parse_date(student_line))

    def test_date_with_extra_spaces(self):
        student_line = "Estudante: João Silva Data:   19/07/2025   "
        self.assertEqual(parse_date(student_line), "19/07/2025")

if __name__ == "__main__":
    unittest.main()