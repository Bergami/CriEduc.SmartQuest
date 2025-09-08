"""
Centralized Enums for SmartQuest Application
==========================================

This package contains all enums used throughout the SmartQuest application,
organized by category for better maintainability and discoverability.

Categories:
- content_enums: Content types and utility functions
- figure_enums: Figure types and positioning  
- text_enums: Text roles and document structure
- image_enums: Image categories
- question_enums: Answer types
- context_enums: Context block types  
- extraction_enums: Image extraction methods
"""

# Content and document enums
from .content_enums import ContentType
from .figure_enums import FigureType
from .text_enums import TextRole

# Processing enums - removed unused enums
# Removed: ProcessingStatus, ExtractionMethod, ValidationLevel (not used in codebase)

# Image enums
from .image_enums import (
    ImageCategory
)

# Question enums
from .question_enums import (
    AnswerType
)

# Context enums
from .context_enums import (
    ContextBlockType
    # Removed: InstructionType (not used in codebase)
)

# Extraction enums
from .extraction_enums import (
    ImageExtractionMethod
)

__all__ = [
    # Content
    "ContentType", "FigureType", "TextRole",
    # Images
    "ImageCategory",
    # Questions
    "AnswerType",
    # Context
    "ContextBlockType",
    # Extraction
    "ImageExtractionMethod"
    
    # REMOVED (not used in codebase):
    # "ProcessingStatus", "ExtractionMethod", "ValidationLevel", "InstructionType"
]
