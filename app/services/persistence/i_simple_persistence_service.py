"""
Interface simplificada para serviços de persistência

Define contrato conforme escopo original do prompt MongoDB.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from app.models.persistence import AnalyzeDocumentRecord, AzureProcessingDataRecord


class ISimplePersistenceService(ABC):
    """
    Interface simplificada para persistência.
    
    Conforme escopo original: apenas 4 operações essenciais + save Azure data.
    """

    @abstractmethod
    async def save_analysis_result(self, analysis_record: AnalyzeDocumentRecord) -> str:
        """
        Persiste resultado da análise conforme prompt original.
        
        Args:
            analysis_record: Registro de análise
            
        Returns:
            ID do documento salvo
        """
        pass

    @abstractmethod
    async def save_azure_processing_data(self, azure_data_record: AzureProcessingDataRecord) -> str:
        """
        Persiste dados de processamento do Azure.
        
        Args:
            azure_data_record: Dados de processamento Azure
            
        Returns:
            ID do documento salvo
        """
        pass

    @abstractmethod
    async def get_by_document_id(self, document_id: str) -> Optional[AnalyzeDocumentRecord]:
        """
        Recupera registro por ID do documento.
        
        Args:
            document_id: ID do documento
            
        Returns:
            Registro encontrado ou None
        """
        pass

    @abstractmethod
    async def get_by_user_email(self, email: str, limit: int = 10) -> List[AnalyzeDocumentRecord]:
        """
        Recupera registros por email do usuário.
        
        Args:
            email: Email do usuário
            limit: Limite de registros
            
        Returns:
            Lista de registros encontrados
        """
        pass

    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[AnalyzeDocumentRecord]:
        """
        Recupera registros por intervalo de datas.
        
        Args:
            start_date: Data início
            end_date: Data fim
            limit: Limite de registros
            
        Returns:
            Lista de registros encontrados
        """
        pass