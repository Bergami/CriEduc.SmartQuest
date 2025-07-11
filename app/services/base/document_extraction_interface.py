from abc import ABC, abstractmethod
from typing import Dict, Any, List
from fastapi import UploadFile

class DocumentExtractionInterface(ABC):
    """
    Abstract interface for document extraction services.
    Defines the contract that all document extraction providers must implement.
    """
    
    @abstractmethod
    async def extract_document_data(self, file: UploadFile) -> Dict[str, Any]:
        """
        Extract structured data from a document file.
        
        Args:
            file: The uploaded document file to process
            
        Returns:
            Dict containing:
                - text: Full extracted text content
                - confidence: Overall confidence score (0.0 to 1.0)
                - metadata: Provider-specific metadata
                - page_count: Number of pages in document
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the extraction provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available"""
        pass
