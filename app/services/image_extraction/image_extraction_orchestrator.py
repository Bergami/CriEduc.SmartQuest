"""
Image extraction factory and orchestrator.
Manages different image extraction strategies.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile

# Import enums from centralized location
from app.enums import ImageExtractionMethod

from app.services.image_extraction.base_image_extractor import BaseImageExtractor
from app.services.image_extraction.azure_figures_extractor import AzureFiguresImageExtractor
from app.services.image_extraction.manual_pdf_extractor import ManualPDFImageExtractor
from app.services.utils.image_saving_service import ImageSavingService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class ImageExtractionOrchestrator:
    """
    Orchestrates different image extraction strategies.

    This class provides:
    - Strategy selection
    - Fallback mechanisms
    """
    
    def __init__(self):
        self._extractors = {
            ImageExtractionMethod.AZURE_FIGURES: AzureFiguresImageExtractor(),
            ImageExtractionMethod.MANUAL_PDF: ManualPDFImageExtractor()
        }
        self.image_saver = ImageSavingService()
    
    async def extract_images_single_method(
        self,
        method: ImageExtractionMethod,
        file: UploadFile,
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract images using a single method.

        Args:
            method: The extraction method to use
            file: The uploaded PDF file
            document_analysis_result: The result from document analysis
            document_id: Optional document identifier

        Returns:
            Dictionary mapping figure IDs to base64 encoded images
        """
        if method not in self._extractors:
            raise DocumentProcessingError(f"Unknown extraction method: {method.value}")

        extractor = self._extractors[method]
        logger.info(f"🔧 Using extraction method: {extractor.get_extraction_method_name()}")

        return await extractor.extract_images(file, document_analysis_result, document_id)