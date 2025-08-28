"""
Data Transfer Objects (DTOs)

This module contains all DTOs used in the SmartQuest application.
DTOs are organized by purpose and consumer type.

Structure:
- responses/: DTOs optimized for API responses
- requests/: DTOs for API request validation (future expansion)
- internal/: DTOs for internal service communication (future expansion)
- external/: DTOs for external service integration (future expansion)
"""

from .responses import (
    # Image DTOs
    ImagePositionDTO,
    ImageDTO,
    ImageListDTO,
    
    # Context DTOs
    ContextContentDTO,
    ContextBlockDTO,
    ContextListDTO,
    
    # Question DTOs
    AnswerOptionDTO,
    QuestionContentDTO,
    QuestionDTO,
    QuestionListDTO,
    
    # Document DTOs
    DocumentMetadataDTO,
    ProcessingSummaryDTO,
    DocumentResponseDTO,
)

# Re-export API DTOs at the top level for convenience
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
    "DocumentResponseDTO",
]


# Version and metadata
__version__ = "2.0.0"
__description__ = "SmartQuest Data Transfer Objects"


def get_dto_info():
    """
    Get information about available DTOs.
    
    Returns:
        Dictionary with DTO categories and descriptions
    """
    return {
        "version": __version__,
        "description": __description__,
        "categories": {
            "responses": {
                "description": "DTOs optimized for API responses",
                "path": "app.dtos.responses",
                "count": 13,
                "main_types": ["Image", "Context", "Question", "Document"]
            }
        },
        "design_principles": [
            "Separation of concerns between internal and external data",
            "Optimized serialization for API responses",
            "Backward compatibility with legacy formats",
            "Clear, consumer-friendly structure",
            "Comprehensive validation with Pydantic"
        ]
    }
