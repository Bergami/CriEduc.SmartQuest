"""
DTO para resposta do endpoint GET /analyze/analyze_document/{id}

Representa o documento persistido no MongoDB conforme especificação.
"""

from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AnalyzeDocumentResponseDTO(BaseModel):
    """
    DTO para resposta do endpoint GET /analyze/analyze_document/{id}.
    
    Retorna os dados exatos conforme salvos no MongoDB, seguindo
    a especificação do prompt original.
    """
    
    id: str = Field(..., description="ID do documento no MongoDB", alias="_id")
    document_name: str = Field(..., description="Nome do arquivo", alias="file_name")
    status: str = Field(..., description="Status do processamento")
    analysis_results: Dict[str, Any] = Field(..., description="Resultado da análise", alias="response")
    created_at: datetime = Field(..., description="Data/hora de criação")
    user_email: str = Field(..., description="Email do usuário")

    class Config:
        """Configuração do DTO."""
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "49ad106b-787b-4c9a-80ac-4c81388355ca",
                "document_name": "example.pdf", 
                "status": "processed",
                "analysis_results": {
                    "document_id": "doc_12345",
                    "email": "user@example.com",
                    "filename": "example.pdf",
                    "questions": [],
                    "context_blocks": []
                },
                "created_at": "2024-10-28T10:30:00Z",
                "user_email": "user@example.com"
            }
        }

    @classmethod
    def from_mongo_record(cls, mongo_record: Dict[str, Any]) -> "AnalyzeDocumentResponseDTO":
        """
        Converte registro do MongoDB para DTO de resposta.
        
        Args:
            mongo_record: Documento do MongoDB
            
        Returns:
            DTO formatado para resposta da API
        """
        return cls(
            id=str(mongo_record.get("_id")),
            document_name=mongo_record.get("file_name"),
            status=mongo_record.get("status", "unknown"),
            analysis_results=mongo_record.get("response", {}),
            created_at=mongo_record.get("created_at"),
            user_email=mongo_record.get("user_email")
        )

    @classmethod  
    def from_analyze_document_record(cls, record) -> "AnalyzeDocumentResponseDTO":
        """
        Converte AnalyzeDocumentRecord para DTO de resposta.
        
        Args:
            record: Instância de AnalyzeDocumentRecord
            
        Returns:
            DTO formatado para resposta da API
        """
        return cls(
            id=str(record.id),
            document_name=record.file_name,
            status=record.status.value if hasattr(record.status, 'value') else str(record.status),
            analysis_results=record.response,
            created_at=record.created_at,
            user_email=record.user_email
        )