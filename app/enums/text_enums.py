"""
Text Enums
==========

Enums related to text roles and document structure.
"""

from enum import Enum


class TextRole(Enum):
    """Enum for text roles in document structure"""
    
    # Content roles
    BODY_TEXT = "body_text"
    DIALOGUE = "dialogue"
    INSTRUCTION = "instruction"
    SUBTITLE = "subtitle"
    CAPTION = "caption"
    
    # Unknown
    UNKNOWN = "unknown"
