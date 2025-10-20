"""
Enumerações para status de documentos e processamento

Define status possíveis para documentos analisados.
"""
from enum import Enum


class DocumentStatus(str, Enum):
    """
    Status possíveis para análise de documentos.
    
    Valores são strings para facilitar serialização JSON e MongoDB.
    """
    
    PENDING = "pending"      # Análise iniciada, aguardando processamento
    COMPLETED = "completed"  # Análise concluída com sucesso
    FAILED = "failed"        # Análise falhou por algum motivo
    
    def __str__(self) -> str:
        """Retorna valor string do enum."""
        return self.value