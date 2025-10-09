"""
Image Extraction Services Module

Contains services for extracting and processing images from documents.
"""

from .image_extraction_orchestrator import ImageExtractionOrchestrator
from .azure_figures_extractor import AzureFiguresImageExtractor
from .base_image_extractor import BaseImageExtractor
from .manual_pdf_extractor import ManualPDFImageExtractor

# Re-export the enum for convenience
from app.enums import ImageExtractionMethod

__all__ = [
    'ImageExtractionOrchestrator',
    'AzureFiguresImageExtractor', 
    'BaseImageExtractor',
    'ManualPDFImageExtractor',
    'ImageExtractionMethod'
]