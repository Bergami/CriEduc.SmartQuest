"""
Azure-based image extraction strategy.
Uses Azure Document Intelligence figures API to extract images.
"""

import logging
import io
import tempfile
import os
import time
from typing import Dict, Any, Optional
from fastapi import UploadFile
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption
from azure.core.credentials import AzureKeyCredential

from app.services.image.extraction.base_image_extractor import BaseImageExtractor
from app.services.utils.image_saving_service import ImageSavingService
from app.config import settings
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class AzureFiguresImageExtractor(BaseImageExtractor):
    """
    Image extraction using Azure Document Intelligence figures functionality.
    
    This implementation uses Azure's native figure detection and extraction
    capabilities, which should provide better performance and accuracy.
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
        Extract images using Azure figures API.
        
        This method:
        1. Re-analyzes the document with output=figures parameter
        2. Gets the analysis result ID
        3. Fetches individual figure images via the figures endpoint
        4. Returns base64 encoded images
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("🔄 Starting Azure figures-based image extraction...")
            
            # Reposition file pointer and read content
            await file.seek(0)
            file_content = await file.read()
            
            if not file_content:
                logger.error("❌ Empty PDF file")
                return {}
            
            # Step 1: Analyze document with output parameter for figures
            logger.info("📊 Analyzing document with figures output...")
            
            # Use the correct API - analyze_document with output parameter
            poller = self.client.begin_analyze_document(
                model_id=self.model_id,
                analyze_request=io.BytesIO(file_content),
                content_type="application/pdf",
                output=["figures"]  # Request figures in output
            )
            
            self._extraction_metrics["api_calls"] += 1
            
            # Wait for analysis to complete
            result = poller.result()
            
            # Get operation/result ID for figure retrieval
            operation_location = getattr(poller, '_operation_location', None) 
            result_id = None
            
            if operation_location:
                # Extract result ID from operation location
                # Format: https://endpoint/documentintelligence/operations/{result_id}
                result_id = operation_location.split('/')[-1]
                logger.info(f"✅ Analysis completed. Result ID: {result_id}")
            else:
                logger.warning("⚠️  Could not extract result ID from operation")
            
            # Step 2: Check if figures were detected
            figures = getattr(result, 'figures', [])
            if not figures:
                logger.warning("⚠️  No figures detected in document")
                return {}
            
            logger.info(f"🎯 Found {len(figures)} figures to extract")
            
            # Step 3: Extract each figure image
            extracted_images = {}
            
            for figure in figures:
                figure_id = getattr(figure, 'id', 'unknown')
                
                try:
                    if result_id:
                        # Use the correct endpoint for getting figure
                        # According to Azure docs: GET {endpoint}/documentintelligence/operations/{resultId}/figures/{figureId}
                        figure_url = f"{self.endpoint.rstrip('/')}/documentintelligence/operations/{result_id}/figures/{figure_id}"
                        
                        logger.info(f"🔗 Fetching figure from: {figure_url}")
                        
                        # Make direct HTTP request for figure using httpx (already in dependencies)
                        import httpx
                        
                        headers = {
                            'Ocp-Apim-Subscription-Key': self.key
                        }
                        
                        async with httpx.AsyncClient() as client:
                            response = await client.get(figure_url, headers=headers)
                            
                            if response.status_code == 200:
                                figure_bytes = response.content
                                
                                # Convert to base64
                                import base64
                                base64_image = base64.b64encode(figure_bytes).decode('utf-8')
                                extracted_images[figure_id] = base64_image
                                
                                logger.info(f"✅ Figure {figure_id}: {len(figure_bytes)} bytes → {len(base64_image)} chars base64")
                                self._extraction_metrics["successful_extractions"] += 1
                            else:
                                logger.error(f"❌ HTTP {response.status_code} for figure {figure_id}: {response.text}")
                                self._extraction_metrics["failed_extractions"] += 1
                    else:
                        logger.warning(f"⚠️  No result_id available for figure {figure_id}")
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
