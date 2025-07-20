import unittest
from app.data.cities import extract_city

class TestExtractCity(unittest.TestCase):
    def test_city_present(self):
        header = "Prefeitura Municipal de Vila Velha"
        self.assertEqual(extract_city(header), "Vila Velha")

    def test_city_absent(self):
        header = "Prefeitura Municipal de Cidade Inexistente"
        self.assertIsNone(extract_city(header))

    def test_empty_header(self):
        header = ""
        self.assertIsNone(extract_city(header))

    def test_case_insensitivity(self):
        header = "prefeitura municipal de vitória"
        self.assertEqual(extract_city(header), "Vitória")

    def test_special_characters(self):
        header = "Prefeitura Municipal de Água Doce do Norte"
        self.assertEqual(extract_city(header), "Água Doce do Norte")

if __name__ == "__main__":
    unittest.main()