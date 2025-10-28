"""
Manual PDF-based image extraction strategy.
Uses coordinate-based cropping from the existing PDF processing approach.
"""

import logging
import tempfile
import os
import time
from typing import Dict, Any, Optional
from fastapi import UploadFile

from app.services.image.extraction.base_image_extractor import BaseImageExtractor
from app.services.utils.pdf_image_extractor import PDFImageExtractor
from app.services.utils.image_saving_service import ImageSavingService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class ManualPDFImageExtractor(BaseImageExtractor):
    """
    Image extraction using manual PDF coordinate-based cropping.
    
    This implementation uses the existing approach of extracting images
    by cropping the PDF based on bounding box coordinates.
    """
    
    def __init__(self):
        super().__init__()  # Initialize BaseImageExtractor
        
        self._extraction_metrics = {
            "method": "manual_pdf_cropping",
            "documents_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_processing_time": 0.0
        }
    
    async def extract_images(
        self, 
        file: UploadFile, 
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract images using manual PDF coordinate-based cropping.
        
        This method:
        1. Saves the PDF to a temporary file
        2. Uses the existing PDFImageExtractor with coordinate data
        3. Returns base64 encoded images
        """
        start_time = time.time()
        temp_file = None
        
        try:
            logger.info("🔧 Starting manual PDF-based image extraction...")
            
            # Reposition file pointer and read content
            await file.seek(0)
            file_content = await file.read()
            
            if not file_content:
                logger.error("❌ Empty PDF file")
                return {}
            
            logger.info(f"📄 PDF file loaded: {len(file_content)} bytes")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                temp_file = tmp.name
                tmp.write(file_content)
            
            logger.info(f"📁 Temporary file created: {temp_file}")
            
            # Verify temporary file
            if not os.path.exists(temp_file):
                raise DocumentProcessingError(f"Temporary file not created: {temp_file}")
            
            temp_file_size = os.path.getsize(temp_file)
            logger.info(f"📊 Temporary file size: {temp_file_size} bytes")
            
            # Check for figures in the analysis result
            figures = document_analysis_result.get("figures", [])
            if not figures:
                logger.warning("⚠️  No figures found in analysis result")
                return {}
            
            logger.info(f"🎯 Found {len(figures)} figures for extraction")
            
            # Extract images using existing PDFImageExtractor
            logger.info("🔧 Using PDFImageExtractor for coordinate-based extraction...")
            
            image_bytes_dict = PDFImageExtractor.extract_figures_from_azure_result(
                pdf_path=temp_file,
                azure_result=document_analysis_result
            )
            
            logger.info(f"📸 PDFImageExtractor returned {len(image_bytes_dict)} images")
            
            # Convert to base64
            extracted_images = {}
            for figure_id, img_bytes in image_bytes_dict.items():
                if img_bytes:
                    base64_img = PDFImageExtractor.get_base64_image(img_bytes)
                    extracted_images[figure_id] = base64_img
                    
                    logger.info(f"✅ Figure {figure_id}: {len(img_bytes)} bytes → {len(base64_img)} chars base64")
                    self._extraction_metrics["successful_extractions"] += 1
                else:
                    logger.warning(f"⚠️  Figure {figure_id}: empty or null bytes")
                    self._extraction_metrics["failed_extractions"] += 1
            
            processing_time = time.time() - start_time
            self._extraction_metrics["total_processing_time"] += processing_time
            self._extraction_metrics["documents_processed"] += 1
            
            logger.info(f"🎉 Manual PDF extraction completed: {len(extracted_images)} images in {processing_time:.2f}s")
            return extracted_images
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._extraction_metrics["total_processing_time"] += processing_time
            
            logger.error(f"❌ Error in manual PDF extraction: {str(e)}", exc_info=True)
            raise DocumentProcessingError(f"Manual PDF extraction failed: {str(e)}")
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                    logger.debug(f"🗑️  Temporary file removed: {temp_file}")
                except Exception as e:
                    logger.error(f"❌ Error removing temporary file: {str(e)}")
    
    def get_extraction_method_name(self) -> str:
        """Get the name of this extraction method."""
        return "manual_pdf_cropping"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this extraction method."""
        metrics = self._extraction_metrics.copy()
        
        # Calculate derived metrics
        total_attempts = metrics["successful_extractions"] + metrics["failed_extractions"]
        if total_attempts > 0:
            metrics["success_rate"] = metrics["successful_extractions"] / total_attempts
        else:
            metrics["success_rate"] = 0.0
        
        if metrics["documents_processed"] > 0:
            metrics["avg_processing_time"] = metrics["total_processing_time"] / metrics["documents_processed"]
        else:
            metrics["avg_processing_time"] = 0.0
        
        return metrics
