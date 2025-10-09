"""
Image Processing Services Module

Contains services for image categorization and processing.
"""

from .image_categorization_service import ImageCategorizationService as ImageCategorizationServiceLegacy
from .image_categorization_service_pydantic import ImageCategorizationServicePydantic
from .image_categorization_service_pure_pydantic import ImageCategorizationService

# Import from extraction submodule
from .extraction import ImageExtractionOrchestrator, AzureFiguresImageExtractor, BaseImageExtractor, ManualPDFImageExtractor, ImageExtractionMethod

__all__ = [
    'ImageCategorizationService',
    'ImageCategorizationServiceLegacy',
    'ImageCategorizationServicePydantic', 
    'ImageExtractionOrchestrator',
    'AzureFiguresImageExtractor',
    'BaseImageExtractor',
    'ManualPDFImageExtractor',
    'ImageExtractionMethod'
]