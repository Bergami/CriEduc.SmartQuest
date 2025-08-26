"""
Content Type Enums for Document Analysis
Defines standardized content types and figure categories
"""
from enum import Enum, auto

class ContentType(Enum):
    """Enum for different types of content in documents"""
    
    # Text content types
    HEADER = "header"
    FOOTER = "footer"
    PARAGRAPH = "paragraph"
    TITLE = "title"
    SUBTITLE = "subtitle"
    DIALOGUE = "dialogue"
    
    # Visual content types
    IMAGE = "image"
    FIGURE = "figure"
    CHARGE = "charge"  # Comic strip/cartoon
    PROPAGANDA = "propaganda"  # Advertisement
    DIAGRAM = "diagram"
    CHART = "chart"
    PHOTO = "photo"
    
    # Educational content types
    QUESTION = "question"
    ALTERNATIVE = "alternative"
    INSTRUCTION = "instruction"
    CONTEXT_BLOCK = "context_block"
    
    # Mixed content
    TEXT_WITH_IMAGE = "text_with_image"
    MIXED_CONTENT = "mixed_content"
    
    # Special content
    WATERMARK = "watermark"
    LOGO = "logo"
    SIGNATURE = "signature"
    
    # Unknown/unclassified
    UNKNOWN = "unknown"

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
    ILLUSTRATION = "illustration"
    PHOTO = "photo"
    DIAGRAM = "diagram"
    CHART = "chart"
    TABLE_IMAGE = "table_image"
    
    # Educational types
    QUESTION_FIGURE = "question_figure"
    CONTEXT_FIGURE = "context_figure"
    EXAMPLE_FIGURE = "example_figure"
    
    # Administrative types
    LOGO = "logo"
    WATERMARK = "watermark"
    STAMP = "stamp"
    
    # Unknown
    UNKNOWN = "unknown"

class TextRole(Enum):
    """Enum for text roles in document structure"""
    
    # Structural roles
    TITLE = "title"
    SUBTITLE = "subtitle"
    HEADER = "header"
    FOOTER = "footer"
    CAPTION = "caption"
    
    # Content roles
    BODY_TEXT = "body_text"
    DIALOGUE = "dialogue"
    QUOTE = "quote"
    INSTRUCTION = "instruction"
    
    # Educational roles
    QUESTION_TEXT = "question_text"
    ALTERNATIVE_TEXT = "alternative_text"
    CONTEXT_TEXT = "context_text"
    
    # Metadata roles
    AUTHOR = "author"
    DATE = "date"
    PAGE_NUMBER = "page_number"
    
    # Unknown
    UNKNOWN = "unknown"

class ContextBlockType(Enum):
    """Enum for different types of context blocks"""
    
    # Visual context blocks
    IMAGE_CONTEXT = "image_context"
    CHARGE_CONTEXT = "charge_context"
    PROPAGANDA_CONTEXT = "propaganda_context"
    
    # Text context blocks
    TEXT_CONTEXT = "text_context"
    DIALOGUE_CONTEXT = "dialogue_context"
    NARRATIVE_CONTEXT = "narrative_context"
    
    # Mixed context blocks
    MIXED_CONTEXT = "mixed_context"
    TEXT_AND_IMAGE = "text_and_image"
    
    # Educational context blocks
    EXAMPLE_CONTEXT = "example_context"
    EXERCISE_CONTEXT = "exercise_context"
    REFERENCE_CONTEXT = "reference_context"
    
    # Unknown
    UNKNOWN = "unknown"

class InstructionType(Enum):
    """Enum for different types of instructions"""
    
    # Analysis instructions
    ANALYZE_TEXT = "analyze_text"
    ANALYZE_IMAGE = "analyze_image"
    ANALYZE_FIGURE = "analyze_figure"
    
    # Reading instructions
    READ_TEXT = "read_text"
    READ_CAREFULLY = "read_carefully"
    
    # Observation instructions
    OBSERVE_IMAGE = "observe_image"
    OBSERVE_FIGURE = "observe_figure"
    
    # Action instructions
    ANSWER_QUESTION = "answer_question"
    CHOOSE_ALTERNATIVE = "choose_alternative"
    COMPARE = "compare"
    IDENTIFY = "identify"
    
    # General instructions
    GENERAL_ANALYSIS = "general_analysis"
    GENERAL_INSTRUCTION = "general_instruction"
    
    # Unknown
    UNKNOWN = "unknown"

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
