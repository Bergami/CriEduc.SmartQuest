"""
Interface simplificada para serviços de persistência

Define contrato conforme escopo original do prompt MongoDB.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
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

    @abstractmethod
    async def get_by_user_email_with_filters(
        self,
        email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[AnalyzeDocumentRecord], int]:
        """
        Recupera registros por email com filtros opcionais e paginação.
        
        Combina filtro obrigatório por email com filtros opcionais de data
        e suporte a paginação.
        
        Args:
            email: Email do usuário (obrigatório)
            start_date: Data início do intervalo (opcional)
            end_date: Data fim do intervalo (opcional)
            page: Número da página (1-indexed, mínimo 1)
            page_size: Itens por página (máximo 50)
            
        Returns:
            Tupla contendo:
            - Lista de registros encontrados na página
            - Total de registros que correspondem aos filtros
        """
        pass

    @abstractmethod
    async def check_duplicate_document(
        self,
        email: str,
        filename: str,
        file_size: int
    ) -> Optional[AnalyzeDocumentRecord]:
        """
        Verifica se documento já foi processado.
        
        Busca documento com:
        - Mesmo email
        - Mesmo filename
        - Mesmo file_size
        - Status COMPLETED (docs FAILED são ignorados para permitir retry)
        
        Performance: O(1) devido ao índice composto idx_duplicate_check
        
        Args:
            email: Email do usuário
            filename: Nome do arquivo
            file_size: Tamanho do arquivo em bytes
            
        Returns:
            AnalyzeDocumentRecord se encontrado, None caso contrário
        """
        pass

    @abstractmethod
    async def save_completed_analysis(
        self,
        email: str,
        filename: str,
        file_size: int,
        response_dict: dict
    ) -> str:
        """
        Método high-level para persistir resultado de análise completa.
        
        Encapsula a lógica de:
        1. Criar AnalyzeDocumentRecord com status COMPLETED
        2. Salvar no MongoDB
        3. Tratar erros de persistência
        
        Args:
            email: Email do usuário
            filename: Nome do arquivo
            file_size: Tamanho do arquivo em bytes
            response_dict: Dicionário com response completo (DocumentResponseDTO.dict())
            
        Returns:
            ID do documento salvo
            
        Raises:
            DocumentProcessingError: Se persistência falhar (MongoDB obrigatório)
        """
        pass