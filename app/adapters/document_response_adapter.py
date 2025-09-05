"""
Document Response Adapter

🚨 DEPRECATED: Esta classe está depreciada desde a Fase 03 da migração Pydantic.

Use DocumentResponseDTO.from_internal_response() em vez de DocumentResponseAdapter.to_api_response().
O DocumentResponseDTO já é um modelo Pydantic nativo que FastAPI serializa automaticamente.

Esta camada adapta os modelos internos tipados para o formato de response
esperado pelos endpoints, mantendo compatibilidade com o código existente.
"""

import logging
from typing import Dict, Any
from app.models.internal import InternalDocumentResponse

logger = logging.getLogger(__name__)


class DocumentResponseAdapter:
    """
    🚨 DEPRECATED: Use DocumentResponseDTO.from_internal_response() instead
    
    Adapta InternalDocumentResponse para formato de response da API.
    
    Esta classe mantém a separação entre modelos internos (completos e tipados)
    e responses da API (formato específico para cada endpoint).
    
    FASE 03: Esta classe está sendo eliminada em favor do DocumentResponseDTO
    que já é um modelo Pydantic nativo e oferece melhor type safety.
    """
    
    @staticmethod
    def to_api_response(internal_response: InternalDocumentResponse) -> Dict[str, Any]:
        """
        🚨 DEPRECATED: Use DocumentResponseDTO.from_internal_response() instead
        
        Converte InternalDocumentResponse para formato EXATO esperado pela API.
        
        ESTRUTURA FIXA - NÃO PODE SER ALTERADA:
        - header (não document_metadata)
        - questions com "question" e "alternatives" 
        - context_blocks com "paragraphs" (opcional)
        
        Args:
            internal_response: Response interno com modelos tipados
            
        Returns:
            Dicionário no formato EXATO especificado em copilot_instructions.md
        """
        logger.warning("🚨 DEPRECATED: DocumentResponseAdapter.to_api_response() is deprecated. Use DocumentResponseDTO.from_internal_response() instead.")
        
        # ✅ Converter header usando método existente
        header_dict = internal_response.document_metadata.to_legacy_format()
        
        # ✅ Converter questions para formato API (question + alternatives)
        api_questions = []
        for q in internal_response.questions:
            api_question = {
                "number": q.number,
                "question": q.content.statement,  # content.statement → question
                "alternatives": [  # options → alternatives
                    {
                        "letter": opt.label,
                        "text": opt.text
                    }
                    for opt in q.options
                ],
                "hasImage": q.has_image,
                "context_id": q.context_id
            }
            api_questions.append(api_question)
        
        # ✅ Converter context_blocks para formato API (com paragraphs quando aplicável)
        api_context_blocks = []
        for cb in internal_response.context_blocks:
            api_context = {
                "id": cb.id,
                "type": [t.value for t in cb.type],
                "source": cb.source,
                "statement": cb.statement,
                "title": cb.title,
                "hasImage": cb.has_image
            }
            
            # ✅ Adicionar images apenas para context blocks simples (sem sub_contexts)
            if cb.sub_contexts:
                # Context blocks com sub_contexts: imagens ficam nos sub_contexts, não no pai
                api_context["images"] = []
            else:
                # Context blocks simples: usar o campo images do próprio block
                api_context["images"] = cb.images if cb.images else []
                
            # ✅ Adicionar contentType se houver imagens (apenas para context blocks simples)
            if cb.has_image and not cb.sub_contexts and cb.images:
                api_context["contentType"] = "image/jpeg;base64"
            
            # ✅ Adicionar paragraphs quando há conteúdo de texto
            if cb.content and cb.content.description:
                api_context["paragraphs"] = cb.content.description
            
            # ✅ Adicionar sub_contexts se existirem (para contextos com múltiplas sequências)
            if cb.sub_contexts:
                api_context["sub_contexts"] = [
                    {
                        "sequence": sub.sequence,
                        "type": sub.type,
                        "title": sub.title,
                        "content": sub.content,
                        "images": sub.images
                    }
                    for sub in cb.sub_contexts
                ]
            
            api_context_blocks.append(api_context)
        
        # ✅ Montar response no formato EXATO esperado
        api_response = {
            "email": internal_response.email,
            "document_id": internal_response.document_id,
            "filename": internal_response.filename,
            "header": header_dict,  # ✅ "header" não "document_metadata"
            "questions": api_questions,  # ✅ com "question" e "alternatives"
            "context_blocks": api_context_blocks  # ✅ com "paragraphs" opcional
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
