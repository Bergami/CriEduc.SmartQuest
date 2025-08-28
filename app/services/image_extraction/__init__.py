"""
Image extraction module initialization.
"""

from app.services.image_extraction.image_extraction_orchestrator import (
    ImageExtractionOrchestrator,
    ImageExtractionMethod
)
from app.services.image_extraction.azure_figures_extractor import AzureFiguresImageExtractor
from app.services.image_extraction.manual_pdf_extractor import ManualPDFImageExtractor
from app.services.image_extraction.base_image_extractor import BaseImageExtractor

__all__ = [
    "ImageExtractionOrchestrator",
    "ImageExtractionMethod", 
    "AzureFiguresImageExtractor",
    "ManualPDFImageExtractor",
    "BaseImageExtractor"
]
