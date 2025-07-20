"""
Test data and utilities for SmartQuest tests
"""
from pathlib import Path
from typing import Dict, Any, List

# Test data paths
FIXTURES_PATH = Path(__file__).parent / "fixtures"
PDFS_PATH = FIXTURES_PATH / "pdfs"
RESPONSES_PATH = FIXTURES_PATH / "responses"


class TestDataProvider:
    """Provides test data for different scenarios"""
    
    @staticmethod
    def get_sample_header_text() -> str:
        """Returns sample header text for parser tests"""
        return """
        PREFEITURA MUNICIPAL DE VILA VELHA
        UMEF SATURNINO RANGEL MAURO
        PROVA TRIMESTRAL - 3º TRIMESTRE
        Professora: Danielle
        Disciplina: Língua Portuguesa
        Turma: 7º ano
        Valor: 12,0
        """
    
    @staticmethod
    def get_sample_question_text() -> str:
        """Returns sample question text for parser tests"""
        return """
        QUESTÃO 01
        
        Nesse texto, o discípulo que venceu a prova porque
        
        (A) colocou o feijão em um sapato.
        (B) cozinhou o feijão.
        (C) desceu a montanha correndo.
        (D) sumiu da vista do oponente.
        (E) tirou seu sapato.
        """
    
    @staticmethod
    def get_sample_context_text() -> str:
        """Returns sample context text for parser tests"""
        return """
        Após ler atentamente o texto a seguir, responda as três próximas questões.
        
        FEIJÕES OU PROBLEMAS?
        
        Reza a lenda que um monge pediu a dois discípulos que descesse a montanha...
        """
    
    @staticmethod
    def get_mock_azure_response() -> Dict[str, Any]:
        """Returns mock Azure Document Intelligence response"""
        return {
            "content": "PREFEITURA MUNICIPAL DE VILA VELHA\\n\\nUMEF SATURNINO RANGEL MAURO\\n\\nPROVA TRIMESTRAL - 3º TRIMESTRE\\n\\nProfessora: Danielle\\n\\nDisciplina: Língua Portuguesa\\n\\nTurma: 7º ano\\n\\nValor: 12,0\\n\\nQUESTÃO 01\\n\\nNesse texto, o discípulo que venceu a prova porque\\n\\n(A) colocou o feijão em um sapato.\\n(B) cozinhou o feijão.\\n(C) desceu a montanha correndo.\\n(D) sumiu da vista do oponente.\\n(E) tirou seu sapato.",
            "pages": [{"pageNumber": 1}],
            "paragraphs": [
                {
                    "content": "PREFEITURA MUNICIPAL DE VILA VELHA",
                    "role": "pageHeader"
                },
                {
                    "content": "UMEF SATURNINO RANGEL MAURO",
                    "role": "pageHeader"
                }
            ],
            "figures": []
        }
    
    @staticmethod
    def get_expected_parsed_header() -> Dict[str, Any]:
        """Returns expected parsed header data"""
        return {
            "network": "Prefeitura Municipal de Vila Velha",
            "school": "UMEF Saturnino Rangel Mauro",
            "city": "Vila Velha",
            "teacher": "Danielle",
            "subject": "Língua Portuguesa",
            "exam_title": "Prova Trimestral",
            "trimester": "3º TRIMESTRE",
            "grade": "7º ano",
            "class": None,
            "student": None,
            "grade_value": "12,0",
            "date": None,
            "images": []
        }
    
    @staticmethod
    def get_expected_question_data() -> List[Dict[str, Any]]:
        """Returns expected question data"""
        return [
            {
                "number": 1,
                "question": "Nesse texto, o discípulo que venceu a prova porque",
                "alternatives": [
                    {"letter": "A", "text": "colocou o feijão em um sapato."},
                    {"letter": "B", "text": "cozinhou o feijão."},
                    {"letter": "C", "text": "desceu a montanha correndo."},
                    {"letter": "D", "text": "sumiu da vista do oponente."},
                    {"letter": "E", "text": "tirou seu sapato."}
                ],
                "hasImage": False,
                "context_id": 0
            }
        ]


class TestValidators:
    """Validation utilities for tests"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validates email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_pdf_response(response: Dict[str, Any]) -> bool:
        """Validates PDF processing response structure"""
        required_fields = ["document_id", "filename", "header", "questions", "context_blocks"]
        return all(field in response for field in required_fields)
    
    @staticmethod
    def is_valid_question(question: Dict[str, Any]) -> bool:
        """Validates question structure"""
        required_fields = ["number", "question", "alternatives"]
        return all(field in question for field in required_fields)
    
    @staticmethod
    def is_valid_header(header: Dict[str, Any]) -> bool:
        """Validates header structure"""
        required_fields = ["network", "school", "teacher", "subject"]
        return all(field in header for field in required_fields)
