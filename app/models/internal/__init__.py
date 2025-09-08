"""
Internal Data Models

These models contain complete information for internal processing.
They preserve all metadata, coordinates, and processing details needed
for debugging, analysis, and advanced processing operations.
"""

# Re-export all internal models for easy importing
from .image_models import (
    InternalImageData,
    ImagePosition,
    ExtractionMetadata,
    ImageCategory
)
from .document_models import (
    InternalDocumentResponse,
    InternalDocumentMetadata
)
from .context_models import (
    InternalContextBlock,
    InternalContextContent
)
from .question_models import (
    InternalQuestion,
    InternalAnswerOption,
    InternalQuestionContent,
    AnswerType
)

__all__ = [
    # Image models
    "InternalImageData",
    "ImagePosition", 
    "ExtractionMetadata",
    "ImageCategory",
    
    # Document models
    "InternalDocumentResponse",
    "InternalDocumentMetadata",
    
    # Context models
    "InternalContextBlock",
    "InternalContextContent",
    
    # Question models
    "InternalQuestion",
    "InternalAnswerOption",
    "InternalQuestionContent", 
    "AnswerType"
]
