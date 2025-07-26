"""
Mock Data Constants
Centralizes all paths and configurations specific to mock data and testing
"""

from pathlib import Path
from .paths import ProjectPaths


class MockDataConstants:
    """
    Constants specific to mock data files and testing scenarios
    """
    
    # Mock data directories
    MOCK_RESPONSES_DIR = ProjectPaths.TESTS_FIXTURES / "responses"
    MOCK_PDFS_DIR = ProjectPaths.TESTS_FIXTURES / "pdfs"
    
    # Mock response files (ordered by preference)
    MOCK_RESPONSE_FILES = {
        "azure_new_format": MOCK_RESPONSES_DIR / "azure_response_3Tri_20250716_215103.json",
        "azure_legacy_format": MOCK_RESPONSES_DIR / "RetornoProcessamento.json",
        "parser_result": ProjectPaths.PROJECT_ROOT / "resultado_parser.json"
    }
    
    # Mock PDF files
    MOCK_PDF_FILES = {
        "modelo_prova": MOCK_PDFS_DIR / "modelo-prova.pdf",
        "modelo_prova_completa": MOCK_PDFS_DIR / "modelo-prova-completa.pdf",
        "modelo_completo_prova": MOCK_PDFS_DIR / "modelo-completo-prova.pdf"
    }
    
    # Default mock settings
    DEFAULT_MOCK_FILENAME = "mock_document.pdf"
    DEFAULT_MOCK_EMAIL = "test@example.com"
    
    # Mock image settings
    MOCK_IMAGE_CONFIG = {
        "width": 400,
        "height": 300,
        "background_color": (240, 240, 240),
        "border_color": (0, 0, 0),
        "text_color": (0, 0, 0),
        "format": "JPEG"
    }
    
    # Header detection thresholds
    HEADER_DETECTION = {
        "max_page_for_header": 1,  # Header images usually on first page
        "vertical_threshold": 0.3,  # Top 30% of page considered header area
        "fallback_threshold": 0.2   # Stricter threshold for fallback detection
    }
    
    @classmethod
    def get_primary_mock_response_path(cls) -> Path:
        """
        Get the primary mock response file path with fallback logic
        
        Returns:
            Path: Path to the preferred mock response file that exists
        """
        for file_key, file_path in cls.MOCK_RESPONSE_FILES.items():
            if file_path.exists():
                return file_path
        
        # If no files exist, return the preferred one (will be handled by calling code)
        return cls.MOCK_RESPONSE_FILES["azure_new_format"]
    
    @classmethod
    def get_primary_mock_pdf_path(cls) -> Path:
        """
        Get the primary mock PDF file path
        
        Returns:
            Path: Path to the preferred mock PDF file
        """
        primary_pdf = cls.MOCK_PDF_FILES["modelo_prova"]
        return primary_pdf
    
    @classmethod
    def get_mock_response_fallback_chain(cls) -> list[Path]:
        """
        Get ordered list of mock response files for fallback logic
        
        Returns:
            list[Path]: Ordered list of paths to try
        """
        return [
            cls.MOCK_RESPONSE_FILES["azure_new_format"],
            cls.MOCK_RESPONSE_FILES["azure_legacy_format"]
        ]
    
    @classmethod
    def validate_mock_files_exist(cls) -> dict[str, bool]:
        """
        Check which mock files exist
        
        Returns:
            dict: Status of each mock file category
        """
        status = {
            "responses": False,
            "pdfs": False,
            "missing_files": []
        }
        
        # Check response files
        for file_key, file_path in cls.MOCK_RESPONSE_FILES.items():
            if file_path.exists():
                status["responses"] = True
                break
            else:
                status["missing_files"].append(str(file_path))
        
        # Check PDF files  
        for file_key, file_path in cls.MOCK_PDF_FILES.items():
            if file_path.exists():
                status["pdfs"] = True
                break
            else:
                status["missing_files"].append(str(file_path))
        
        return status
