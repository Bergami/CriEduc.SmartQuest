"""
Content Type Enums for Document Analysis
Defines standardized content types and figure categories

⚠️  DEPRECATED: This module is deprecated. 
    Import from app.enums instead:
    
    from app.enums import ContentType, FigureType, TextRole
    from app.enums import ContextBlockType
    # REMOVED unused enums: InstructionType, ProcessingStatus, ExtractionMethod, ValidationLevel
"""
from enum import Enum, auto

# Import from centralized enums and re-export for backwards compatibility
from app.enums import (
    ContentType as _ContentType,
    FigureType as _FigureType, 
    TextRole as _TextRole,
    ContextBlockType as _ContextBlockType
    # REMOVED unused enums: InstructionType, ProcessingStatus, ExtractionMethod, ValidationLevel
)

# Re-export with original names for backwards compatibility
ContentType = _ContentType
FigureType = _FigureType
TextRole = _TextRole
ContextBlockType = _ContextBlockType

# REMOVED unused enums (no longer available):
# InstructionType, ProcessingStatus, ExtractionMethod, ValidationLevel

# ContentType is now imported from app.enums above

# FigureType is now imported from app.enums above

# TextRole is now imported from app.enums above

# ContextBlockType is now imported from app.enums above

# InstructionType is now imported from app.enums above

# Utility functions for enum operations
def get_content_type_from_string(content_str: str) -> ContentType:
    """
    Converts string to ContentType enum
    
    Args:
        content_str: String representation of content type
        
    Returns:
        ContentType enum value
    """
    content_lower = content_str.lower().strip()
    
    # Map common variations to enum values
    content_mapping = {
        'charge': ContentType.CHARGE,
        'propaganda': ContentType.PROPAGANDA,
        'advertisement': ContentType.PROPAGANDA,
        'ad': ContentType.PROPAGANDA,
        'comic': ContentType.CHARGE,
        'cartoon': ContentType.CHARGE,
        'tirinha': ContentType.CHARGE,
        'text': ContentType.PARAGRAPH,
        'texto': ContentType.PARAGRAPH,
        'image': ContentType.IMAGE,
        'imagem': ContentType.IMAGE,
        'figure': ContentType.FIGURE,
        'figura': ContentType.FIGURE,
        'header': ContentType.HEADER,
        'footer': ContentType.FOOTER,
        'title': ContentType.TITLE,
        'subtitle': ContentType.SUBTITLE,
        'dialogue': ContentType.DIALOGUE,
        'diálogo': ContentType.DIALOGUE,
        'anúncio': ContentType.PROPAGANDA,
        'publicidade': ContentType.PROPAGANDA
    }
    
    return content_mapping.get(content_lower, ContentType.UNKNOWN)

def get_figure_type_from_content(content_type: ContentType, position_info: dict = None) -> FigureType:
    """
    Determines figure type based on content type and position
    
    Args:
        content_type: ContentType enum
        position_info: Optional position information
        
    Returns:
        FigureType enum value
    """
    # Direct mapping for some content types
    if content_type == ContentType.CHARGE:
        return FigureType.CHARGE
    elif content_type == ContentType.PROPAGANDA:
        return FigureType.PROPAGANDA
    elif content_type == ContentType.HEADER:
        return FigureType.HEADER
    elif content_type == ContentType.FOOTER:
        return FigureType.FOOTER
    elif content_type == ContentType.LOGO:
        return FigureType.LOGO
    
    # Position-based determination
    if position_info:
        y_position = position_info.get('y', 0)
        if y_position < 1.0:  # Top of page
            return FigureType.HEADER
        elif y_position > 10.0:  # Bottom of page
            return FigureType.FOOTER
    
    # Default to content figure
    return FigureType.CONTENT


# REMOVED: ProcessingStatus, ExtractionMethod, and ValidationLevel (unused enums)
