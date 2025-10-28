"""
Base class for image extraction strategies.
This provides an interface for different image extraction approaches.

Note: Images are now stored in Azure Blob Storage, not locally.
This base class focuses on extraction logic only.
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
    
    Images are returned as base64 strings and uploaded to Azure Blob Storage
    by the orchestrator, not saved locally.
    """

    def __init__(self):
        """Initialize the base extractor."""
        logger.debug("BaseImageExtractor initialized")

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
