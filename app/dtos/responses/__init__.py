"""
API Response DTOs

These Data Transfer Objects are optimized for API responses.
They contain only essential information needed by API consumers,
without internal processing metadata or debugging information.

Key Features:
- Simplified structure for efficient serialization
- Backward compatibility with legacy formats
- Clear separation from internal data models
- Optimized for JSON API responses
- Consumer-friendly field names and structure
"""

from .image_dtos import (
    ImagePositionDTO,
    ImageDTO,
    ImageListDTO
)

from .context_dtos import (
    ContextContentDTO,
    ContextBlockDTO,
    ContextListDTO
)

from .question_dtos import (
    AnswerOptionDTO,
    QuestionContentDTO,
    QuestionDTO,
    QuestionListDTO
)

from .document_dtos import (
    DocumentMetadataDTO,
    ProcessingSummaryDTO,
    DocumentResponseDTO as LegacyDocumentResponseDTO
)

from .document_response_dto import (
    DocumentResponseDTO,
    QuestionDTO,
    ContextBlockDTO,
    AlternativeDTO,
    SubContextDTO,
    HeaderDTO
)

__all__ = [
    # Image DTOs
    "ImagePositionDTO",
    "ImageDTO",
    "ImageListDTO",
    
    # Context DTOs
    "ContextContentDTO",
    "ContextBlockDTO",
    "ContextListDTO",
    
    # Question DTOs
    "AnswerOptionDTO",
    "QuestionContentDTO",
    "QuestionDTO",
    "QuestionListDTO",
    
    # Document DTOs
    "DocumentMetadataDTO",
    "ProcessingSummaryDTO",
    "LegacyDocumentResponseDTO",
    
    # New Pydantic DTOs
    "DocumentResponseDTO",
    "AlternativeDTO",
    "SubContextDTO",
    "HeaderDTO",
]


# Version information
__version__ = "2.0.0"
__status__ = "Phase 2 - Response DTOs"


def get_all_response_dtos():
    """
    Get all available Response DTO classes.
    
    Returns:
        Dictionary mapping DTO names to classes
    """
    return {
        "ImagePositionDTO": ImagePositionDTO,
        "ImageDTO": ImageDTO,
        "ImageListDTO": ImageListDTO,
        "ContextContentDTO": ContextContentDTO,
        "ContextBlockDTO": ContextBlockDTO,
        "ContextListDTO": ContextListDTO,
        "AnswerOptionDTO": AnswerOptionDTO,
        "QuestionContentDTO": QuestionContentDTO,
        "QuestionDTO": QuestionDTO,
        "QuestionListDTO": QuestionListDTO,
        "DocumentMetadataDTO": DocumentMetadataDTO,
        "ProcessingSummaryDTO": ProcessingSummaryDTO,
        "DocumentResponseDTO": DocumentResponseDTO,
    }


def get_dto_by_name(dto_name: str):
    """
    Get a DTO class by name.
    
    Args:
        dto_name: Name of the DTO class
        
    Returns:
        DTO class or None if not found
    """
    dtos = get_all_response_dtos()
    return dtos.get(dto_name)


def validate_all_dtos():
    """
    Validate that all DTOs are properly imported and accessible.
    
    Returns:
        Dictionary with validation results
    """
    dtos = get_all_response_dtos()
    results = {}
    
    for name, dto_class in dtos.items():
        try:
            # Test basic instantiation (with minimal required fields)
            if hasattr(dto_class, 'schema'):
                schema = dto_class.schema()
                results[name] = {
                    "status": "valid",
                    "schema_available": True,
                    "required_fields": schema.get("required", [])
                }
            else:
                results[name] = {
                    "status": "valid",
                    "schema_available": False,
                    "required_fields": []
                }
        except Exception as e:
            results[name] = {
                "status": "error",
                "error": str(e),
                "schema_available": False
            }
    
    return results


def get_dto_comparison():
    """
    Compare API DTOs with their internal model counterparts.
    
    Returns:
        Dictionary with comparison information
    """
    from ...models.internal import (
        InternalImageData,
        InternalDocumentMetadata,
        InternalContextBlock,
        InternalQuestion
    )
    
    comparisons = {
        "image_comparison": {
            "internal_model": "InternalImageData",
            "api_dto": "ImageDTO",
            "simplified_fields": [
                "No azure_coordinates",
                "No extraction_metadata", 
                "No processing_notes",
                "No created_at",
                "Simplified position object"
            ]
        },
        "context_comparison": {
            "internal_model": "InternalContextBlock",
            "api_dto": "ContextBlockDTO", 
            "simplified_fields": [
                "No extraction_method",
                "No confidence_score",
                "No processing_notes",
                "Simplified content object"
            ]
        },
        "question_comparison": {
            "internal_model": "InternalQuestion",
            "api_dto": "QuestionDTO",
            "simplified_fields": [
                "No extraction_method",
                "No validation_status",
                "No processing_notes",
                "No learning_objectives",
                "Simplified options"
            ]
        },
        "document_comparison": {
            "internal_model": "InternalDocumentMetadata",
            "api_dto": "DocumentMetadataDTO",
            "simplified_fields": [
                "No header_images",
                "No content_images", 
                "No extraction_confidence",
                "No processing_notes"
            ]
        }
    }
    
    return comparisons
