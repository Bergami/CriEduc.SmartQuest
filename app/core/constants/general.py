"""
General Application Constants
Centralizes general configuration values used throughout the application
"""

from typing import Dict, Any


class GeneralConstants:
    """
    General application constants and configuration values
    """
    
    # Application metadata
    APP_NAME = "SmartQuest"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Document processing and question extraction API"
    
    # API Configuration
    API_CONFIG = {
        "default_host": "127.0.0.1",
        "default_port": 8000,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
    
    # Document processing limits
    DOCUMENT_LIMITS = {
        "max_file_size_mb": 50,
        "max_pages": 100,
        "max_text_length": 1000000,  # 1MB text
        "supported_formats": [".pdf", ".docx", ".txt"]
    }
    
    # Text processing configuration
    TEXT_PROCESSING = {
        "default_encoding": "utf-8",
        "text_preview_length": 500,
        "min_confidence_threshold": 0.5,
        "max_extraction_retries": 3
    }
    
    # Logging configuration
    LOGGING_CONFIG = {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "log_file": "app.log",
        "max_log_size_mb": 10,
        "backup_count": 5
    }
    
    # Debug settings
    DEBUG_CONFIG = {
        "enabled": True,
        "verbose_logging": True,
        "show_stack_traces": True,
        "debug_prefix": "🔧 DEBUG:",
        "success_prefix": "✅ DEBUG:",
        "error_prefix": "❌ DEBUG:",
        "warning_prefix": "⚠️ DEBUG:"
    }
    
    # Provider settings
    PROVIDER_CONFIG = {
        "default_provider": "azure",
        "fallback_provider": "local",
        "provider_timeout_seconds": 30,
        "retry_attempts": 2
    }
    
    # Question extraction settings
    QUESTION_EXTRACTION = {
        "min_question_length": 10,
        "max_question_length": 1000,
        "question_patterns": [
            r"\d+\s*[.)]\s*",  # Numbered questions
            r"[A-Z]\s*[.)]\s*",  # Letter-based questions
            r"Questão\s*\d+",  # Portuguese question pattern
            r"Question\s*\d+"   # English question pattern
        ],
        "alternative_patterns": [
            r"[a-e]\s*[.)\-]\s*",  # Multiple choice alternatives
            r"\([a-e]\)\s*",       # Parenthesized alternatives
            r"[A-E]\s*[.)\-]\s*"   # Capital letter alternatives
        ]
    }
    
    # Header extraction settings
    HEADER_EXTRACTION = {
        "max_header_lines": 20,
        "school_keywords": ["escola", "colégio", "instituto", "universidade", "faculdade"],
        "grade_patterns": [r"\d+º\s*ano", r"série\s*\d+", r"turma\s*[A-Z]\d*"],
        "subject_keywords": ["matemática", "português", "história", "geografia", "ciências"],
        "date_patterns": [
            r"\d{2}/\d{2}/\d{4}",
            r"\d{2}-\d{2}-\d{4}",
            r"\d{4}-\d{2}-\d{2}"
        ]
    }
    
    # Error messages
    ERROR_MESSAGES = {
        "file_not_found": "File not found: {path}",
        "invalid_format": "Invalid file format: {format}. Supported formats: {supported}",
        "processing_failed": "Document processing failed: {error}",
        "extraction_failed": "Text extraction failed: {error}",
        "parsing_failed": "Document parsing failed: {error}",
        "mock_data_missing": "Mock data files not found in expected locations",
        "provider_unavailable": "Document extraction provider '{provider}' is unavailable"
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        "document_processed": "Document processed successfully",
        "text_extracted": "Text extracted successfully",
        "questions_found": "Found {count} questions in document",
        "header_parsed": "Header information parsed successfully",
        "mock_processing": "Mock document processing completed"
    }
    
    @classmethod
    def get_supported_formats_string(cls) -> str:
        """
        Get comma-separated string of supported file formats
        
        Returns:
            str: Formatted string of supported formats
        """
        return ", ".join(cls.DOCUMENT_LIMITS["supported_formats"])
    
    @classmethod
    def is_debug_enabled(cls) -> bool:
        """
        Check if debug mode is enabled
        
        Returns:
            bool: True if debug is enabled
        """
        return cls.DEBUG_CONFIG["enabled"]
    
    @classmethod
    def get_debug_prefix(cls, level: str = "info") -> str:
        """
        Get debug prefix for given level
        
        Args:
            level: Debug level (info, success, error, warning)
            
        Returns:
            str: Appropriate debug prefix
        """
        prefix_map = {
            "info": cls.DEBUG_CONFIG["debug_prefix"],
            "success": cls.DEBUG_CONFIG["success_prefix"], 
            "error": cls.DEBUG_CONFIG["error_prefix"],
            "warning": cls.DEBUG_CONFIG["warning_prefix"]
        }
        return prefix_map.get(level, cls.DEBUG_CONFIG["debug_prefix"])
