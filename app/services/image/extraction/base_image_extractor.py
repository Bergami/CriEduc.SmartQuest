"""
Base class for image extraction strategies.
This provides an interface for different image extraction approaches.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


class BaseImageExtractor(ABC):
    """
    Abstract base class for image extraction strategies.
    
    This class defines the interface that all image extraction implementations
    must follow, allowing for easy switching between different approaches.
    
    Uses centralized file management with unified directory structure:
    tests/documents/images/azure/azure_endpoint/
    tests/documents/images/azure/azure_manual/
    """

    def __init__(self):
        """Initialize the base extractor with centralized file manager."""
        from app.services.utils.centralized_file_manager import CentralizedFileManager
        
        self.file_manager = CentralizedFileManager()
        logger.debug("BaseImageExtractor initialized with centralized file manager")

    def _save_image(
        self, 
        method: str, 
        filename: str, 
        content: bytes, 
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save image using centralized file manager.
        
        Args:
            method: Extraction method ("azure_endpoint" or "azure_manual")
            filename: Name of the image file
            content: Image content as bytes
            document_id: Optional document identifier
            metadata: Optional metadata
            
        Returns:
            Path to saved file
        """
        logger.debug(f"💾 Saving image with method {method} to centralized structure")
        
        if method == "azure_endpoint":
            return self.file_manager.save_image_azure_endpoint(
                filename, content, document_id, metadata
            )
        elif method == "azure_manual":
            return self.file_manager.save_image_azure_manual(
                filename, content, document_id, metadata
            )
        else:
            raise ValueError(f"Unknown extraction method: {method}")

    @abstractmethod
    async def extract_images(
        self, 
        file: UploadFile, 
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract images from a document.
        
        Args:
            file: The uploaded PDF file
            document_analysis_result: The result from document analysis
            document_id: Optional document identifier
            
        Returns:
            Dictionary mapping figure IDs to base64 encoded images
        """
        pass
    
    @abstractmethod
    def get_extraction_method_name(self) -> str:
        """
        Get the name of this extraction method.
        
        Returns:
            String identifier for this extraction method
        """
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this extraction method.
        
        Returns:
            Dictionary with performance-related information
        """
        pass
