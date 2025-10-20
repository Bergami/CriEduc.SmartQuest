"""
Modelo de persistência para dados de processamento do Azure

Modelo específico para armazenar informações detalhadas do processamento Azure,
incluindo response completo e métricas Pydantic.
"""
from pydantic import Field, BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_document import BaseDocument


class ProcessingMetrics(BaseModel):
    """
    Modelo Pydantic para métricas de processamento.
    
    Mantém padrão atual da aplicação usando Pydantic para validação.
    """
    
    processing_duration_seconds: Optional[float] = Field(None, description="Duração do processamento")
    confidence_score: Optional[float] = Field(None, description="Score de confiança geral")
    pages_count: Optional[int] = Field(None, description="Número de páginas processadas")
    context_blocks_count: Optional[int] = Field(None, description="Número de blocos de contexto")
    questions_count: Optional[int] = Field(None, description="Número de questões identificadas")
    azure_operation_id: Optional[str] = Field(None, description="ID da operação Azure")
    azure_model_used: Optional[str] = Field(None, description="Modelo Azure utilizado")
    azure_api_version: Optional[str] = Field(None, description="Versão da API Azure")
    extraction_quality_score: Optional[float] = Field(None, description="Score de qualidade da extração")
    
    def calculate_quality_score(self) -> float:
        """
        Calcula score de qualidade baseado nas métricas disponíveis.
        
        Returns:
            Score entre 0 e 1
        """
        score = 0.0
        factors = 0
        
        if self.confidence_score is not None:
            score += self.confidence_score
            factors += 1
            
        if self.processing_duration_seconds is not None:
            # Processamento rápido (<300s) é melhor
            time_score = 1.0 if self.processing_duration_seconds < 300 else 0.5
            score += time_score
            factors += 1
            
        if self.context_blocks_count is not None and self.context_blocks_count > 0:
            score += 1.0
            factors += 1
            
        if self.questions_count is not None and self.questions_count > 0:
            score += 1.0
            factors += 1
            
        return score / factors if factors > 0 else 0.0


class AzureProcessingDataRecord(BaseDocument):
    """
    Modelo de persistência para coleção 'azure_processing_data'.
    
    Armazena dados específicos do processamento Azure conforme solicitado:
    - created_at: Data hora atual (herdado)
    - user_email: Email informado no request
    - file_name: Nome do documento enviado
    - response: Response inteiro e íntegro do Azure no formato JSON
    - metrics: Informações de métricas em modelo Pydantic
    """
    
    user_email: str = Field(..., description="Email informado no request")
    file_name: str = Field(..., description="Nome do documento enviado")
    response: Dict[str, Any] = Field(..., description="Response completo do Azure em formato JSON")
    metrics: ProcessingMetrics = Field(..., description="Métricas de processamento Pydantic")
    
    class Config:
        """Configuração específica para AzureProcessingDataRecord."""
        schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "file_name": "document.pdf",
                "response": {
                    "operation_id": "azure_op_123",
                    "model_id": "prebuilt-layout",
                    "api_version": "2023-07-31",
                    "result": {
                        "pages": [],
                        "context_blocks": [],
                        "confidence": 0.95
                    }
                },
                "metrics": {
                    "processing_duration_seconds": 45.2,
                    "confidence_score": 0.95,
                    "pages_count": 5,
                    "context_blocks_count": 12,
                    "questions_count": 8,
                    "azure_operation_id": "azure_op_123",
                    "azure_model_used": "prebuilt-layout",
                    "azure_api_version": "2023-07-31"
                }
            }
        }
    
    @classmethod
    def create_from_azure_response(
        cls,
        user_email: str,
        file_name: str,
        azure_response: Dict[str, Any],
        processing_metrics: ProcessingMetrics
    ):
        """
        Cria novo registro a partir da resposta do Azure.
        
        Args:
            user_email: Email do usuário
            file_name: Nome do arquivo
            azure_response: Response completo do Azure
            processing_metrics: Métricas de processamento
            
        Returns:
            Nova instância de AzureProcessingDataRecord
        """
        return cls(
            user_email=user_email,
            file_name=file_name,
            response=azure_response,
            metrics=processing_metrics
        )
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo de qualidade do processamento.
        
        Returns:
            Dict com informações de qualidade
        """
        quality_score = self.metrics.calculate_quality_score()
        
        return {
            "overall_quality_score": quality_score,
            "confidence_score": self.metrics.confidence_score,
            "processing_duration": self.metrics.processing_duration_seconds,
            "content_extracted": {
                "pages": self.metrics.pages_count or 0,
                "context_blocks": self.metrics.context_blocks_count or 0,
                "questions": self.metrics.questions_count or 0
            },
            "azure_info": {
                "operation_id": self.metrics.azure_operation_id,
                "model": self.metrics.azure_model_used,
                "api_version": self.metrics.azure_api_version
            }
        }