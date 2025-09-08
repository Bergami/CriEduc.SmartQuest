"""
Context Enums
============

Enums related to context blocks and instruction types.
Migrated from app.core.constants.content_types
"""

from enum import Enum


class ContextBlockType(Enum):
    """Enum for different types of context blocks"""
    
    # Basic context block types
    TEXT_CONTEXT = "text_context"      # Pure text content
    IMAGE_CONTEXT = "image_context"    # Pure image/visual content  
    TEXT_AND_IMAGE = "text_and_image"  # Mixed text and image content
    
    # Unknown/fallback
    UNKNOWN = "unknown"
