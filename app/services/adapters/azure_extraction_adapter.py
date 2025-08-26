import logging
from typing import Dict, Any
from fastapi import UploadFile
from app.services.base.document_extraction_interface import DocumentExtractionInterface
from app.services.base.text_normalizer import TextNormalizer
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class AzureExtractionAdapter(DocumentExtractionInterface):
    """
    Adapter for Azure Document Intelligence service.
    Implements the standard document extraction interface.
    """
    
    def __init__(self):
        self._service = None
        self._available = False
        
        try:
            self._service = AzureDocumentIntelligenceService()
            self._available = True
            logger.info("Azure Document Intelligence adapter initialized successfully")
        except Exception as e:
            logger.warning(f"Azure Document Intelligence not available: {str(e)}")
            self._available = False
    
    async def extract_document_data(self, file: UploadFile) -> Dict[str, Any]:
        """
        Extract document data using Azure Document Intelligence.
        
        Args:
            file: The uploaded document file
            
        Returns:
            Normalized document data structure
        """
        if not self.is_available():
            raise DocumentProcessingError("Azure Document Intelligence is not available")
        
        try:
            # Use existing Azure service
            raw_data = await self._service.analyze_document(file)
            
            # Normalize the output using TextNormalizer
            normalized_data = TextNormalizer.normalize_output_format(raw_data, self.get_provider_name())
            
            
            # DEBUG: Check what's being returned by adapter
            logger.debug(f"normalized_data metadata keys = {list(normalized_data.get('metadata', {}).keys())}")
            if 'raw_response' in normalized_data.get('metadata', {}):
                raw_response = normalized_data['metadata']['raw_response']
                logger.debug(f"raw_response figures = {len(raw_response.get('figures', []))}")
            else:
                logger.debug("NO raw_response in metadata!")
            
            logger.info(f"Successfully extracted {len(normalized_data['text'])} characters from document")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error extracting document with Azure: {str(e)}")
            raise DocumentProcessingError(f"Azure extraction failed: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Return provider name"""
        return "azure"
    
    def is_available(self) -> bool:
        """Check if Azure service is available"""
        return self._available and self._service is not None
