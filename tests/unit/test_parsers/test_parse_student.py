import unittest
from app.parsers.header_parser.parse_student import parse_student

class TestParseStudent(unittest.TestCase):
    def test_valid_student_name(self):
        """Testa nome válido do estudante"""
        student_line = "Estudante: João Silva"
        self.assertEqual(parse_student(student_line), "João Silva")

    def test_none_input(self):
        """Testa entrada None - cobre if not student_line"""
        self.assertIsNone(parse_student(None))

    def test_empty_string(self):
        """Testa string vazia - cobre if not student_line"""
        self.assertIsNone(parse_student(""))

    def test_whitespace_only(self):
        """Testa string apenas com espaços - cobre if not student_line"""
        self.assertIsNone(parse_student("   "))

    def test_no_estudante_keyword(self):
        """Testa linha sem 'Estudante:' - cobre if not match"""
        student_line = "Aluno: João Silva"
        self.assertIsNone(parse_student(student_line))

    def test_malformed_estudante_line(self):
        """Testa linha mal formatada - cobre if not match"""
        student_line = "Estudante João Silva"  # sem ':'
        self.assertIsNone(parse_student(student_line))

    def test_estudante_only(self):
        """Testa apenas 'Estudante:' sem nome - extrai string vazia que vira None após strip"""
        student_line = "Estudante:"
        self.assertIsNone(parse_student(student_line))

    def test_estudante_with_whitespace_only(self):
        """Testa 'Estudante:' seguido apenas de espaços"""
        student_line = "Estudante:   "
        self.assertEqual(parse_student(student_line), "")

    def test_invalid_value_data_lowercase(self):
        """Testa valor inválido 'data' - cobre if result.lower() in [...]"""
        student_line = "Estudante: data"
        self.assertIsNone(parse_student(student_line))

    def test_invalid_value_data_uppercase(self):
        """Testa valor inválido 'DATA' - cobre if result.lower() in [...]"""
        student_line = "Estudante: DATA"
        self.assertIsNone(parse_student(student_line))

    def test_invalid_value_valor(self):
        """Testa valor inválido 'valor' - cobre if result.lower() in [...]"""
        student_line = "Estudante: Valor"
        self.assertIsNone(parse_student(student_line))

    def test_invalid_value_nota(self):
        """Testa valor inválido 'nota' - cobre if result.lower() in [...]"""
        student_line = "Estudante: NOTA"
        self.assertIsNone(parse_student(student_line))

    def test_invalid_value_dash(self):
        """Testa valor inválido '-' - cobre if result.lower() in [...]"""
        student_line = "Estudante: -"
        self.assertIsNone(parse_student(student_line))

    def test_valid_name_with_spaces(self):
        """Testa nome válido com espaços extras - cobre result.strip() e return result"""
        student_line = "Estudante:   Maria Clara Santos   "
        self.assertEqual(parse_student(student_line), "Maria Clara Santos")

    def test_valid_name_simple(self):
        """Testa nome válido simples - cobre return result"""
        student_line = "Estudante: Ana"
        self.assertEqual(parse_student(student_line), "Ana")

    def test_valid_name_with_special_characters(self):
        """Testa nome válido com caracteres especiais - cobre return result"""
        student_line = "Estudante: José da Silva"
        self.assertEqual(parse_student(student_line), "José da Silva")

    def test_valid_name_with_numbers(self):
        """Testa nome válido com números - cobre return result"""
        student_line = "Estudante: João Silva 123"
        self.assertEqual(parse_student(student_line), "João Silva 123")

    def test_valid_name_with_unicode(self):
        """Testa nome válido com caracteres Unicode - cobre return result"""
        student_line = "Estudante: José é ótimo"
        self.assertEqual(parse_student(student_line), "José é ótimo")

    def test_regex_stops_at_colon(self):
        """Testa que regex para no próximo ':' - valida comportamento do regex"""
        student_line = "Estudante: João Silva: Data: 20/07/2025"
        self.assertEqual(parse_student(student_line), "João Silva")

    def test_regex_stops_at_newline(self):
        """Testa que regex para na quebra de linha - valida comportamento do regex"""
        student_line = "Estudante: João Silva\nOutra linha"
        self.assertEqual(parse_student(student_line), "João Silva")

if __name__ == "__main__":
    unittest.main()