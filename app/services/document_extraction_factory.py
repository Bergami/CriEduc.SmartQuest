import os
import logging
from typing import Dict, Any, Optional
from app.services.base.document_extraction_interface import DocumentExtractionInterface
from app.services.adapters.azure_extraction_adapter import AzureExtractionAdapter
from app.services.storage.document_storage_service import DocumentStorageService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

class DocumentExtractionFactory:
    """
    Factory class for managing document extraction providers.
    Handles provider selection, fallback mechanisms, and configuration.
    """
    
    _providers = {}
    _default_provider = None
    _storage_service = None
    
    @classmethod
    def initialize(cls, storage_service: DocumentStorageService = None):
        """Initialize available providers based on configuration"""
        cls._providers = {}
        
        # Inicializar storage service
        if storage_service is None:
            storage_service = DocumentStorageService()
        cls._storage_service = storage_service
        
        # Register Azure provider
        try:
            azure_adapter = AzureExtractionAdapter()
            if azure_adapter.is_available():
                cls._providers["azure"] = azure_adapter
                logger.info("Azure Document Intelligence provider registered")
                
                # Set as default if none set
                if cls._default_provider is None:
                    cls._default_provider = "azure"
                    
        except Exception as e:
            logger.warning(f"Failed to register Azure provider: {str(e)}")
        
        # Future: Add other providers here
        # cls._register_tesseract_provider()
        # cls._register_google_vision_provider()
        
        # Get preferred provider from environment
        preferred_provider = os.getenv("DOCUMENT_EXTRACTION_PROVIDER", cls._default_provider)
        if preferred_provider and preferred_provider in cls._providers:
            cls._default_provider = preferred_provider
            logger.info(f"Using configured provider: {preferred_provider}")
        
        if not cls._providers:
            raise DocumentProcessingError("No document extraction providers available")
            
        logger.info(f"Document extraction factory initialized with {len(cls._providers)} providers")
    
    @classmethod
    def get_provider(cls, provider_name: Optional[str] = None) -> DocumentExtractionInterface:
        """
        Get a document extraction provider instance.
        
        Args:
            provider_name: Specific provider name, or None for default
            
        Returns:
            Document extraction provider instance
        """
        if not cls._providers:
            cls.initialize()
        
        # Use specified provider or default
        target_provider = provider_name or cls._default_provider
        
        if target_provider not in cls._providers:
            available_providers = list(cls._providers.keys())
            logger.warning(f"Provider '{target_provider}' not available. Available: {available_providers}")
            
            # Fallback to first available provider
            if available_providers:
                target_provider = available_providers[0]
                logger.info(f"Falling back to provider: {target_provider}")
            else:
                raise DocumentProcessingError("No document extraction providers available")
        
        return cls._providers[target_provider]
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """Get list of available providers and their status"""
        if not cls._providers:
            cls.initialize()
            
        return {
            name: provider.is_available() 
            for name, provider in cls._providers.items()
        }
    
    @classmethod
    def get_default_provider_name(cls) -> str:
        """Get the name of the default provider"""
        if not cls._providers:
            cls.initialize()
        return cls._default_provider
    
    # Future provider registration methods
    # @classmethod
    # def _register_tesseract_provider(cls):
    #     """Register Tesseract OCR provider"""
    #     try:
    #         from app.services.adapters.tesseract_extraction_adapter import TesseractExtractionAdapter
    #         tesseract_adapter = TesseractExtractionAdapter()
    #         if tesseract_adapter.is_available():
    #             cls._providers["tesseract"] = tesseract_adapter
    #             logger.info("Tesseract OCR provider registered")
    #     except Exception as e:
    #         logger.warning(f"Failed to register Tesseract provider: {str(e)}")
    
    # @classmethod
    # def _register_google_vision_provider(cls):
    #     """Register Google Vision API provider"""
    #     try:
    #         from app.services.adapters.google_vision_adapter import GoogleVisionAdapter
    #         google_adapter = GoogleVisionAdapter()
    #         if google_adapter.is_available():
    #             cls._providers["google_vision"] = google_adapter
    #             logger.info("Google Vision API provider registered")
    #     except Exception as e:
    #         logger.warning(f"Failed to register Google Vision provider: {str(e)}")
