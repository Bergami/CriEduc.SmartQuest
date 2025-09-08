"""
Figure Enums
============

Enums related to figure types and positioning.
"""

from enum import Enum
from .content_enums import ContentType


class FigureType(Enum):
    """Enum for figure types based on positioning and content"""
    
    # Position-based types
    HEADER = "header"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    CONTENT = "content"
    
    # Content-based types
    CHARGE = "charge"
    PROPAGANDA = "propaganda"
    
    # Administrative types
    LOGO = "logo"
    
    # Unknown
    UNKNOWN = "unknown"


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
