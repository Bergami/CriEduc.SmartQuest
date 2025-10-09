"""
Image extraction factory and orchestrator.
Manages different image extraction strategies.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile

# Import enums from centralized location
from app.enums import ImageExtractionMethod

from app.services.image.extraction.base_image_extractor import BaseImageExtractor
from app.services.image.extraction.azure_figures_extractor import AzureFiguresImageExtractor
from app.services.image.extraction.manual_pdf_extractor import ManualPDFImageExtractor
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class ImageExtractionOrchestrator:
    """
    Orchestrates different image extraction strategies.

    Uses centralized file management for all extractions.
    All files are saved to: tests/documents/images/azure/
    """
    
    def __init__(self):
        """Initialize the orchestrator with centralized file management."""
        self._extractors = {
            ImageExtractionMethod.AZURE_FIGURES: AzureFiguresImageExtractor(),
            ImageExtractionMethod.MANUAL_PDF: ManualPDFImageExtractor()
        }
        logger.info("🔧 ImageExtractionOrchestrator initialized with centralized file structure")
    
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
    
    async def extract_with_fallback(
        self,
        file: UploadFile,
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract images using automatic fallback strategy.
        
        Tries MANUAL_PDF first, then falls back to AZURE_FIGURES if needed.
        This method centralizes the fallback logic previously in AnalyzeService.
        
        Args:
            file: The uploaded PDF file
            document_analysis_result: The result from document analysis  
            document_id: Optional document identifier
            
        Returns:
            Dictionary mapping figure IDs to base64 encoded images
        """
        logger.info("🔄 Starting image extraction with automatic fallback")
        await file.seek(0)
        
        # Try primary method: MANUAL_PDF
        try:
            logger.info("STEP 1: Attempting Manual PDF extraction (primary method)")
            manual_images = await self.extract_images_single_method(
                method=ImageExtractionMethod.MANUAL_PDF,
                file=file,
                document_analysis_result=document_analysis_result,
                document_id=document_id
            )
            if manual_images:
                logger.info(f"✅ Manual PDF extraction successful: {len(manual_images)} images extracted.")
                await file.seek(0)
                return manual_images
            logger.warning("⚠️ Manual PDF extraction returned no images, attempting fallback")
        except Exception as e:
            logger.warning(f"⚠️ Manual PDF extraction failed: {str(e)}, attempting fallback")
        
        await file.seek(0)
        
        # Try fallback method: AZURE_FIGURES
        try:
            logger.info("STEP 2: Using Azure Figures fallback (secondary method)")
            azure_images = await self.extract_images_single_method(
                method=ImageExtractionMethod.AZURE_FIGURES,
                file=file,
                document_analysis_result=document_analysis_result,
                document_id=document_id
            )
            if azure_images:
                logger.info(f"✅ Azure Figures fallback successful: {len(azure_images)} images extracted.")
                await file.seek(0)
                return azure_images
            logger.warning("⚠️ Azure Figures fallback also returned no images")
        except Exception as e:
            logger.error(f"❌ Azure Figures fallback failed: {str(e)}")
        
        logger.warning("❌ All image extraction methods failed, returning empty result")
        await file.seek(0)
        return {}