"""
Image Processing Services Module

Contains services for image categorization and processing.
Consolidado: Uma única implementação padrão.
"""

from .image_categorization_service import ImageCategorizationService

# Import from extraction submodule
from .extraction import ImageExtractionOrchestrator, AzureFiguresImageExtractor, BaseImageExtractor, ManualPDFImageExtractor, ImageExtractionMethod

__all__ = [
    'ImageCategorizationService',
    'ImageExtractionOrchestrator',
    'AzureFiguresImageExtractor',
    'BaseImageExtractor',
    'ManualPDFImageExtractor',
    'ImageExtractionMethod'
]