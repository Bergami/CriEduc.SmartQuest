"""
Content Type Enums
==================

Enums related to document content types.
Migrated from app.core.constants.content_types
"""

from enum import Enum


class ContentType(str, Enum):
    """Enum for different types of content in documents"""
    
    # Text content types
    HEADER = "header"
    FOOTER = "footer"
    PARAGRAPH = "paragraph"
    TITLE = "title"
    SUBTITLE = "subtitle"
    DIALOGUE = "dialogue"
    TEXT = "text"  # Generic text content
    
    # Visual content types
    IMAGE = "image"
    FIGURE = "figure"
    CHARGE = "charge"  # Comic strip/cartoon
    PROPAGANDA = "propaganda"  # Advertisement
    TABLE = "table"
    
    # Technical content
    FORMULA = "formula"
    
    # Educational content types
    INSTRUCTION = "instruction"
        
    # Special content
    LOGO = "logo"
    
    # Unknown/unclassified
    UNKNOWN = "unknown"
    
    @classmethod
    def from_legacy_type(cls, legacy_type: str) -> "ContentType":
        """
        Convert legacy type strings to ContentType enum.
        
        Args:
            legacy_type: Legacy type string
            
        Returns:
            ContentType enum value
        """
        # Normalize the input
        normalized = legacy_type.lower().strip()
        
        # Direct mappings
        type_mappings = {
            "text": cls.TEXT,
            "image": cls.IMAGE,
            "table": cls.TABLE,
            "figure": cls.FIGURE,
            "formula": cls.FORMULA,
            "charge": cls.CHARGE,
            "propaganda": cls.PROPAGANDA,
            "header": cls.HEADER,
            "footer": cls.FOOTER,
            "title": cls.TITLE,
            "subtitle": cls.SUBTITLE,
            "dialogue": cls.DIALOGUE,
            "paragraph": cls.PARAGRAPH,
            
            # Common variations
            "texto": cls.TEXT,
            "imagem": cls.IMAGE,
            "tabela": cls.TABLE,
            "figura": cls.FIGURE,
            "fórmula": cls.FORMULA,
            "tirinha": cls.CHARGE,
            "anúncio": cls.PROPAGANDA,
            "publicidade": cls.PROPAGANDA,
            "diálogo": cls.DIALOGUE,
            
            # English variations
            "picture": cls.IMAGE,
            "illustration": cls.FIGURE,
            "drawing": cls.FIGURE,
        }
        
        return type_mappings.get(normalized, cls.UNKNOWN)
    
    def is_visual_content(self) -> bool:
        """
        Check if this content type represents visual content.
        
        Returns:
            True if visual content, False otherwise
        """
        visual_types = {
            self.IMAGE,
            self.FIGURE,
            self.TABLE,
            self.CHARGE,
            self.PROPAGANDA
        }
        return self in visual_types
    
    def is_textual_content(self) -> bool:
        """
        Check if this content type represents textual content.
        
        Returns:
            True if textual content, False otherwise
        """
        textual_types = {
            self.TEXT,
            self.FORMULA,
            self.PARAGRAPH,
            self.TITLE,
            self.SUBTITLE,
            self.DIALOGUE,
            self.HEADER,
            self.FOOTER
        }
        return self in textual_types


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