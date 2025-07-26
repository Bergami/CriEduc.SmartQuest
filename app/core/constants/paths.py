"""
Project Paths Constants
Centralizes all file and directory paths used throughout the application
"""

from pathlib import Path


class ProjectPaths:
    """
    Core project paths and directory structures
    """
    # Root directories
    PROJECT_ROOT = Path(".")
    APP_ROOT = PROJECT_ROOT / "app"
    TESTS_ROOT = PROJECT_ROOT / "tests"
    
    # Test subdirectories
    TESTS_FIXTURES = TESTS_ROOT / "fixtures"
    TESTS_DEBUG_SCRIPTS = TESTS_ROOT / "debug_scripts"
    TESTS_PARSER_ANALYSIS = TESTS_DEBUG_SCRIPTS / "parser_analysis"
    
    # Configuration files
    CONFIG_FILES = {
        "requirements": PROJECT_ROOT / "requirements.txt",
        "readme": PROJECT_ROOT / "README.md",
        "config": PROJECT_ROOT / "CONFIG.md"
    }
    
    # Application directories
    APP_PARSERS = APP_ROOT / "parsers"
    APP_SERVICES = APP_ROOT / "services"
    APP_CORE = APP_ROOT / "core"
    APP_UTILS = APP_ROOT / "utils"
    APP_VALIDATORS = APP_ROOT / "validators"
    APP_SCHEMAS = APP_ROOT / "schemas"
    
    # Parser subdirectories
    HEADER_PARSER = APP_PARSERS / "header_parser"
    QUESTION_PARSER = APP_PARSERS / "question_parser"
    
    @classmethod
    def get_absolute_path(cls, relative_path: Path) -> str:
        """
        Convert relative path to absolute string path
        
        Args:
            relative_path: Path object or string representing relative path
            
        Returns:
            str: Absolute path as string
        """
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        return str(relative_path.resolve())
    
    @classmethod
    def ensure_directory_exists(cls, path: Path) -> Path:
        """
        Ensure directory exists, create if it doesn't
        
        Args:
            path: Path to directory
            
        Returns:
            Path: The path object (for chaining)
        """
        path.mkdir(parents=True, exist_ok=True)
        return path
