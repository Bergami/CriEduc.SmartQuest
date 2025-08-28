"""
Document Response Adapter

Esta camada adapta os modelos internos tipados para o formato de response
esperado pelos endpoints, mantendo compatibilidade com o código existente.
"""

from typing import Dict, Any
from app.models.internal import InternalDocumentResponse


class DocumentResponseAdapter:
    """
    Adapta InternalDocumentResponse para formato de response da API.
    
    Esta classe mantém a separação entre modelos internos (completos e tipados)
    e responses da API (formato específico para cada endpoint).
    """
    
    @staticmethod
    def to_api_response(internal_response: InternalDocumentResponse) -> Dict[str, Any]:
        """
        Converte InternalDocumentResponse para formato de response da API.
        
        Args:
            internal_response: Response interno com modelos tipados
            
        Returns:
            Dicionário no formato esperado pelos endpoints atuais
        """
        # Converter header para formato legacy
        header_dict = internal_response.document_metadata.to_legacy_format()
        
        # Montar response no formato atual
        api_response = {
            "email": internal_response.email,
            "document_id": internal_response.document_id,
            "filename": internal_response.filename,
            "header": header_dict,
            "questions": internal_response.questions,
            "context_blocks": internal_response.context_blocks
        }
        
        return api_response
    
    @staticmethod 
    def to_full_response(internal_response: InternalDocumentResponse) -> Dict[str, Any]:
        """
        Converte para response completo com todos os dados (para debug/admin).
        
        Args:
            internal_response: Response interno com modelos tipados
            
        Returns:
            Dicionário com todos os dados disponíveis
        """
        api_response = DocumentResponseAdapter.to_api_response(internal_response)
        
        # Adicionar dados extras para debug
        api_response.update({
            "extracted_text": internal_response.extracted_text,
            "provider_metadata": internal_response.provider_metadata,
            "all_images": [img.dict() for img in internal_response.all_images],
            "categorization_summary": internal_response.get_categorization_summary(),
            "document_metadata_full": internal_response.document_metadata.dict()
        })
        
        return api_response
    
    @staticmethod
    def to_minimal_response(internal_response: InternalDocumentResponse) -> Dict[str, Any]:
        """
        Converte para response mínimo (apenas dados essenciais).
        
        Args:
            internal_response: Response interno com modelos tipados
            
        Returns:
            Dicionário com dados mínimos necessários
        """
        return {
            "document_id": internal_response.document_id,
            "questions": internal_response.questions,
            "context_blocks": internal_response.context_blocks
        }
