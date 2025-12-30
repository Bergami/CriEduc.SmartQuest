"""
Azure Response Record Model

Modelo para persistir responses completos do Azure Document Intelligence.
Essencial para debugging, auditoria e melhorias futuras do sistema.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import Field

from .base_document import BaseDocument


class AzureResponseRecord(BaseDocument):
    """
    Modelo para coleção 'azure_responses'.
    
    Armazena o response completo do Azure Document Intelligence para:
    - Debugging de problemas de extração
    - Auditoria de processamento
    - Análise de padrões e melhorias
    - Correlação com documentos processados
    """
    
    # Identificação
    document_id: str = Field(..., description="ID do documento em analyze_documents")
    user_email: str = Field(..., description="Email do usuário que processou")
    file_name: str = Field(..., description="Nome do arquivo processado")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")
    
    # Response do Azure
    azure_response: Dict[str, Any] = Field(..., description="Response completo do Azure (JSON)")
    
    # Metadados do processamento Azure
    azure_operation_id: Optional[str] = Field(None, description="ID da operação do Azure")
    azure_model_id: str = Field(..., description="Modelo usado (ex: prebuilt-layout)")
    azure_api_version: str = Field(..., description="Versão da API do Azure")
    
    # Métricas de processamento
    processing_duration_seconds: float = Field(..., description="Tempo de processamento em segundos")
    confidence_score: Optional[float] = Field(None, description="Score médio de confiança")
    page_count: int = Field(0, description="Número de páginas processadas")
    paragraph_count: int = Field(0, description="Número de parágrafos extraídos")
    
    # Status
    status: str = Field("success", description="Status do processamento (success/error)")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    
    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_email": "user@example.com",
                "file_name": "documento.pdf",
                "file_size": 1024000,
                "azure_response": {
                    "content": "Texto extraído...",
                    "pages": [],
                    "paragraphs": []
                },
                "azure_operation_id": "azure_op_123",
                "azure_model_id": "prebuilt-layout",
                "azure_api_version": "2023-07-31",
                "processing_duration_seconds": 45.2,
                "confidence_score": 0.95,
                "page_count": 5,
                "paragraph_count": 120,
                "status": "success",
                "error_message": None
            }
        }
    
    @classmethod
    def create_from_azure_processing(
        cls,
        document_id: str,
        user_email: str,
        file_name: str,
        file_size: int,
        azure_response: Dict[str, Any],
        azure_model_id: str,
        azure_api_version: str,
        processing_duration: float,
        azure_operation_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> "AzureResponseRecord":
        """
        Factory method para criar registro de response do Azure.
        
        Args:
            document_id: ID do documento processado
            user_email: Email do usuário
            file_name: Nome do arquivo
            file_size: Tamanho do arquivo em bytes
            azure_response: Response completo do Azure
            azure_model_id: ID do modelo Azure usado
            azure_api_version: Versão da API
            processing_duration: Duração do processamento em segundos
            azure_operation_id: ID da operação Azure (opcional)
            confidence_score: Score de confiança (opcional)
            status: Status do processamento
            error_message: Mensagem de erro (opcional)
            
        Returns:
            Nova instância de AzureResponseRecord
        """
        # Extrair contagens do response
        page_count = len(azure_response.get("pages", []))
        paragraph_count = len(azure_response.get("paragraphs", []))
        
        return cls(
            document_id=document_id,
            user_email=user_email,
            file_name=file_name,
            file_size=file_size,
            azure_response=azure_response,
            azure_operation_id=azure_operation_id,
            azure_model_id=azure_model_id,
            azure_api_version=azure_api_version,
            processing_duration_seconds=processing_duration,
            confidence_score=confidence_score,
            page_count=page_count,
            paragraph_count=paragraph_count,
            status=status,
            error_message=error_message
        )
