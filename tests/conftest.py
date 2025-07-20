"""
Test configuration and fixtures for SmartQuest
"""
import pytest
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test data paths
FIXTURES_PATH = Path(__file__).parent / "fixtures"
PDFS_PATH = FIXTURES_PATH / "pdfs"
RESPONSES_PATH = FIXTURES_PATH / "responses"


@pytest.fixture
def test_pdf_path():
    """Path to test PDF file"""
    return PDFS_PATH / "modelo-prova.pdf"


@pytest.fixture
def test_pdf_complete_path():
    """Path to complete test PDF file"""
    return PDFS_PATH / "modelo-completo-prova.pdf"


@pytest.fixture
def mock_azure_response():
    """Mock Azure Document Intelligence response"""
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


@pytest.fixture
def mock_parsed_header():
    """Mock parsed header data"""
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


@pytest.fixture
def mock_question_data():
    """Mock question data"""
    return {
        "questions": [
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
        ],
        "context_blocks": [
            {
                "id": 0,
                "type": ["text"],
                "statement": "Após ler atentamente o texto a seguir, responda as próximas questões.",
                "title": "FEIJÕES OU PROBLEMAS?",
                "paragraphs": ["Reza a lenda que um monge..."],
                "hasImage": False
            }
        ]
    }


@pytest.fixture
def mock_upload_file():
    """Mock UploadFile for testing"""
    from unittest.mock import Mock
    
    mock_file = Mock()
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = pytest.AsyncMock(return_value=b"%PDF-1.4 mock content")
    mock_file.seek = pytest.AsyncMock()
    return mock_file


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from unittest.mock import Mock
    
    settings = Mock()
    settings.azure_document_intelligence_endpoint = "https://test.cognitiveservices.azure.com/"
    settings.azure_document_intelligence_key = "test_key"
    settings.azure_document_intelligence_model = "prebuilt-layout"
    settings.use_azure_ai = True
    return settings


# Test data for different scenarios
@pytest.fixture
def sample_text_with_questions():
    """Sample text containing questions for parsing tests"""
    return """
    PREFEITURA MUNICIPAL DE VILA VELHA
    UMEF SATURNINO RANGEL MAURO
    PROVA TRIMESTRAL - 3º TRIMESTRE
    Professora: Danielle
    Disciplina: Língua Portuguesa
    Turma: 7º ano
    Valor: 12,0
    
    Após ler atentamente o texto a seguir, responda as três próximas questões.
    
    FEIJÕES OU PROBLEMAS?
    
    Reza a lenda que um monge pediu a dois discípulos que descesse a montanha...
    
    QUESTÃO 01
    
    Nesse texto, o discípulo que venceu a prova porque
    
    (A) colocou o feijão em um sapato.
    (B) cozinhou o feijão.
    (C) desceu a montanha correndo.
    (D) sumiu da vista do oponente.
    (E) tirou seu sapato.
    """


@pytest.fixture
def sample_header_text():
    """Sample header text for parser tests"""
    return """
    PREFEITURA MUNICIPAL DE VILA VELHA
    UMEF SATURNINO RANGEL MAURO
    PROVA TRIMESTRAL - 3º TRIMESTRE
    Professora: Danielle
    Disciplina: Língua Portuguesa
    Turma: 7º ano
    Valor: 12,0
    """


# Utility functions for tests
def assert_valid_email(email: str) -> bool:
    """Helper to validate email format in tests"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def assert_valid_pdf_response(response: Dict[str, Any]) -> bool:
    """Helper to validate PDF processing response structure"""
    required_fields = ["document_id", "filename", "header", "questions", "context_blocks"]
    return all(field in response for field in required_fields)


def assert_valid_question(question: Dict[str, Any]) -> bool:
    """Helper to validate question structure"""
    required_fields = ["number", "question", "alternatives"]
    return all(field in question for field in required_fields)
