"""
Azure-based image extraction strategy using official SDK method.
Uses Azure Document Intelligence figures API following official documentation.
"""

import logging
import io
import time
from typing import Dict, Any, Optional
from fastapi import UploadFile
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption
from azure.core.credentials import AzureKeyCredential

from app.services.image_extraction.base_image_extractor import BaseImageExtractor
from app.services.utils.image_saving_service import ImageSavingService
from app.config import settings
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class AzureFiguresImageExtractor(BaseImageExtractor):
    """
    Image extraction using Azure Document Intelligence figures functionality.
    
    This implementation follows the official Azure SDK documentation and uses:
    - AnalyzeOutputOption.FIGURES for requesting figures
    - poller.details["operation_id"] for getting operation ID
    - client.get_analyze_result_figure() for downloading figures
    """
    
    def __init__(self):
        self.endpoint = settings.azure_document_intelligence_endpoint
        self.key = settings.azure_document_intelligence_key
        self.model_id = settings.azure_document_intelligence_model
        
        if not self.endpoint or not self.key:
            raise ValueError("Azure Document Intelligence credentials not configured")
        
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
        
        # Initialize image saving service
        self.image_saver = ImageSavingService()
        
        self._extraction_metrics = {
            "method": "azure_figures",
            "api_calls": 0,
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
        Extract images using Azure figures API with official SDK method.
        
        This method follows the official Azure documentation:
        1. Analyzes document with AnalyzeOutputOption.FIGURES
        2. Gets operation_id from poller.details
        3. Uses client.get_analyze_result_figure() for each figure
        4. Returns base64 encoded images
        """
        start_time = time.time()
        
        try:
            logger.info("🔄 Starting Azure figures-based image extraction using official SDK...")
            
            # Reposition file pointer and read content
            await file.seek(0)
            file_content = await file.read()
            
            if not file_content:
                logger.error("❌ Empty PDF file")
                return {}
            
            # Step 1: Analyze document with FIGURES output using official method
            logger.info("📊 Analyzing document with AnalyzeOutputOption.FIGURES...")
            
            poller = self.client.begin_analyze_document(
                model_id=self.model_id,
                analyze_request=io.BytesIO(file_content),
                content_type="application/pdf",
                output=[AnalyzeOutputOption.FIGURES]  # Official way to request figures
            )
            
            self._extraction_metrics["api_calls"] += 1
            
            # Step 2: Get result and operation_id (official method)
            result = poller.result()
            operation_id = poller.details.get("operation_id")
            
            logger.info(f"✅ Analysis completed. Operation ID: {operation_id}")
            logger.info(f"📋 Model ID: {result.model_id}")
            
            # Step 3: Check if figures were detected
            figures = getattr(result, 'figures', [])
            if not figures:
                logger.warning("⚠️  No figures detected in document")
                return {}
            
            logger.info(f"🎯 Found {len(figures)} figures to extract")
            
            # Step 4: Extract each figure using official SDK method
            extracted_images = {}
            
            for figure in figures:
                figure_id = getattr(figure, 'id', 'unknown')
                
                try:
                    if operation_id and result.model_id:
                        logger.info(f"🔗 Fetching figure {figure_id} using official SDK...")
                        
                        # Use official SDK method - no manual HTTP requests needed!
                        figure_response = self.client.get_analyze_result_figure(
                            model_id=result.model_id,
                            result_id=operation_id,
                            figure_id=figure_id
                        )
                        
                        # Convert response to bytes and then base64
                        figure_bytes = b"".join(figure_response)  # figure_response is iterable
                        
                        if figure_bytes:
                            import base64
                            base64_image = base64.b64encode(figure_bytes).decode('utf-8')
                            extracted_images[figure_id] = base64_image
                            
                            logger.info(f"✅ Figure {figure_id}: {len(figure_bytes)} bytes → {len(base64_image)} chars base64")
                            self._extraction_metrics["successful_extractions"] += 1
                        else:
                            logger.warning(f"⚠️  Figure {figure_id}: Empty response from Azure")
                            self._extraction_metrics["failed_extractions"] += 1
                    else:
                        logger.warning(f"⚠️  Missing operation_id or model_id for figure {figure_id}")
                        self._extraction_metrics["failed_extractions"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error extracting figure {figure_id}: {str(e)}")
                    self._extraction_metrics["failed_extractions"] += 1
            
            processing_time = time.time() - start_time
            self._extraction_metrics["total_processing_time"] += processing_time
            
            # Save extracted images to disk if any were found
            if extracted_images and document_id:
                try:
                    saved_path = self.image_saver.save_images_from_extraction(
                        images=extracted_images,
                        method="azure_figures",
                        document_id=document_id,
                        filename=getattr(file, 'filename', 'unknown'),
                        email="extracted_via_azure_figures"
                    )
                    logger.info(f"💾 Azure figures images saved to: {saved_path}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not save Azure figures images: {str(e)}")
            
            logger.info(f"🎉 Azure figures extraction completed: {len(extracted_images)} images in {processing_time:.2f}s")
            return extracted_images
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._extraction_metrics["total_processing_time"] += processing_time
            
            logger.error(f"❌ Error in Azure figures extraction: {str(e)}", exc_info=True)
            raise DocumentProcessingError(f"Azure figures extraction failed: {str(e)}")
    
    def get_extraction_method_name(self) -> str:
        """Get the name of this extraction method."""
        return "azure_figures"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this extraction method."""
        metrics = self._extraction_metrics.copy()
        
        # Calculate derived metrics
        total_attempts = metrics["successful_extractions"] + metrics["failed_extractions"]
        if total_attempts > 0:
            metrics["success_rate"] = metrics["successful_extractions"] / total_attempts
        else:
            metrics["success_rate"] = 0.0
        
        if metrics["api_calls"] > 0:
            metrics["avg_processing_time"] = metrics["total_processing_time"] / metrics["api_calls"]
        else:
            metrics["avg_processing_time"] = 0.0
        
        return metrics
