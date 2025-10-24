from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi import UploadFile
from app.services.storage.document_storage_service import DocumentStorageService
from app.config.settings import get_settings

class BaseDocumentProvider(ABC):
    """
    Interface base para provedores de análise de documentos
    """
    
    def __init__(self, storage_service: DocumentStorageService):
        self.storage = storage_service
        self.provider_name = self.get_provider_name()
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna o nome do provedor (azure, aws, etc.)"""
        pass
    
    @abstractmethod
    async def analyze_document(self, file: UploadFile, document_id: str) -> Dict[str, Any]:
        """
        Analisa documento e retorna dados estruturados
        
        Args:
            file: Arquivo para análise
            document_id: ID único do documento
            
        Returns:
            Dados estruturados do documento
        """
        pass
    
    async def _save_document_artifacts(self, file: UploadFile, document_id: str, 
                                     raw_response: Dict[str, Any], 
                                     structured_data: Dict[str, Any]) -> None:
        """
        Salva artefatos do documento processado
        
        Args:
            file: Arquivo original
            document_id: ID único do documento
            raw_response: Resposta bruta do provedor
            structured_data: Dados estruturados
        """
        try:
            # Salvar documento original
            await file.seek(0)
            file_content = await file.read()
            self.storage.save_original_document(file_content, file.filename, document_id)
            
            # Salvar resposta bruta
            self.storage.save_raw_response(raw_response, file.filename, self.provider_name)
            
            # REMOVIDO: save_extracted_text() - texto extraído não precisa ser persistido
            # O texto já fica disponível na memória através do structured_data
            
            # Salvar imagens se existirem (condicional por feature flag)
            settings = get_settings()
            if "image_data" in structured_data and settings.enable_local_image_saving:
                self.storage.save_document_images(structured_data["image_data"], document_id, self.provider_name)
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao salvar artefatos do documento {document_id}: {str(e)}")
    
    def _generate_document_id(self) -> str:
        """Gera ID único para o documento"""
        from uuid import uuid4
        return str(uuid4())
