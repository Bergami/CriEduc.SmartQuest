"""
Modelo de persistência para documentos analisados

Representa o modelo exato conforme prompt original MongoDB.
"""
from pydantic import Field
from datetime import datetime
from typing import Dict, Any

from .base_document import BaseDocument
from .enums import DocumentStatus


class AnalyzeDocumentRecord(BaseDocument):
    """
    Modelo de persistência para coleção 'analyze_documents'.
    
    Campos conforme especificação do prompt original:
    - id: Guid (gerado automaticamente)
    - created_at: Data hora atual (gerado automaticamente)
    - user_email: Email informado no request
    - file_name: Nome do documento enviado
    - response: Response no formato JSON
    - status: Status do processamento (enum)
    """
    
    user_email: str = Field(..., description="Email informado no request")
    file_name: str = Field(..., description="Nome do documento enviado")
    response: Dict[str, Any] = Field(..., description="Response completo em formato JSON")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="Status do processamento")
    
    class Config:
        """Configuração específica para AnalyzeDocumentRecord."""
        schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "file_name": "document.pdf",
                "response": {
                    "document_id": "123e4567-e89b-12d3-a456-426614174000",
                    "status": "completed",
                    "context_blocks": [],
                    "questions": []
                },
                "status": "completed"
            }
        }
    
    @classmethod
    def create_from_request(cls, user_email: str, file_name: str, response: Dict[str, Any], status: DocumentStatus = DocumentStatus.PENDING):
        """
        Cria novo registro a partir dos dados da requisição.
        
        Args:
            user_email: Email do usuário
            file_name: Nome do arquivo
            response: Response JSON completo
            status: Status inicial (padrão: PENDING)
            
        Returns:
            Nova instância de AnalyzeDocumentRecord
        """
        return cls(
            user_email=user_email,
            file_name=file_name,
            response=response,
            status=status
        )
    
    def mark_completed(self):
        """Marca o documento como processado com sucesso."""
        self.status = DocumentStatus.COMPLETED
        return self
    
    def mark_failed(self):
        """Marca o documento como falhado no processamento."""
        self.status = DocumentStatus.FAILED
        return self