from typing import Dict, Type
from app.services.providers.base_document_provider import BaseDocumentProvider
from app.services.azure.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.services.storage.document_storage_service import DocumentStorageService

class DocumentProviderFactory:
    """
    Factory para criar instâncias de provedores de análise de documentos
    """
    
    _providers: Dict[str, Type[BaseDocumentProvider]] = {
        "azure": AzureDocumentIntelligenceService,
        # Futuros provedores podem ser adicionados aqui
        # "aws": AWSDocumentIntelligenceService,
        # "google": GoogleDocumentIntelligenceService,
    }
    
    @classmethod
    def get_provider(self, provider_name: str = "azure", 
                    storage_service: DocumentStorageService = None) -> BaseDocumentProvider:
        """
        Cria instância do provedor especificado
        
        Args:
            provider_name: Nome do provedor (azure, aws, etc.)
            storage_service: Serviço de storage (opcional)
            
        Returns:
            Instância do provedor
            
        Raises:
            ValueError: Se o provedor não for suportado
        """
        if provider_name not in self._providers:
            available = ", ".join(self._providers.keys())
            raise ValueError(f"Provedor '{provider_name}' não suportado. Disponíveis: {available}")
        
        if storage_service is None:
            storage_service = DocumentStorageService()
        
        provider_class = self._providers[provider_name]
        return provider_class(storage_service)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseDocumentProvider]) -> None:
        """
        Registra novo provedor
        
        Args:
            name: Nome do provedor
            provider_class: Classe do provedor
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Retorna lista de provedores disponíveis
        
        Returns:
            Lista com nomes dos provedores
        """
        return list(cls._providers.keys())
