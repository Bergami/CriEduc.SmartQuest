"""
Extraction Enums
===============

Enums related to image extraction methods.
Migrated from app.services.image_extraction.image_extraction_orchestrator
"""

from enum import Enum


class ImageExtractionMethod(Enum):
    """Available image extraction methods."""
    AZURE_FIGURES = "azure_figures"
    MANUAL_PDF = "manual_pdf"
