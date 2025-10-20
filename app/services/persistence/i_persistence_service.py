"""
Interface para serviços de persistência

Define contrato comum para operações de persistência seguindo o padrão Repository.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Type
from datetime import datetime

from app.models.persistence.base_document import BaseDocument


class IPersistenceService(ABC):
    """
    Interface abstrata para serviços de persistência.
    
    Define o contrato para operações CRUD seguindo o padrão Repository,
    permitindo diferentes implementações (MongoDB, SQL, etc.).
    """

    @abstractmethod
    async def save(self, document: BaseDocument, collection_name: str) -> str:
        """
        Salva um documento na coleção especificada.
        
        Args:
            document: Documento a ser salvo
            collection_name: Nome da coleção
            
        Returns:
            ID do documento salvo
            
        Raises:
            PersistenceError: Erro durante a operação de salvamento
        """
        pass

    @abstractmethod
    async def get_by_id(self, document_id: str, collection_name: str, model_class: Type[BaseDocument]) -> Optional[BaseDocument]:
        """
        Recupera um documento pelo ID.
        
        Args:
            document_id: ID do documento
            collection_name: Nome da coleção
            model_class: Classe do modelo para deserialização
            
        Returns:
            Documento encontrado ou None
            
        Raises:
            PersistenceError: Erro durante a operação de busca
        """
        pass

    @abstractmethod
    async def update(self, document_id: str, document: BaseDocument, collection_name: str) -> bool:
        """
        Atualiza um documento existente.
        
        Args:
            document_id: ID do documento a atualizar
            document: Documento com dados atualizados
            collection_name: Nome da coleção
            
        Returns:
            True se atualizado com sucesso
            
        Raises:
            PersistenceError: Erro durante a operação de atualização
        """
        pass

    @abstractmethod
    async def delete(self, document_id: str, collection_name: str) -> bool:
        """
        Remove um documento da coleção.
        
        Args:
            document_id: ID do documento a remover
            collection_name: Nome da coleção
            
        Returns:
            True se removido com sucesso
            
        Raises:
            PersistenceError: Erro durante a operação de remoção
        """
        pass

    @abstractmethod
    async def list(self, collection_name: str, model_class: Type[BaseDocument], filters: Optional[Dict[str, Any]] = None, limit: int = 100, skip: int = 0) -> List[BaseDocument]:
        """
        Lista documentos da coleção com filtros opcionais.
        
        Args:
            collection_name: Nome da coleção
            model_class: Classe do modelo para deserialização
            filters: Filtros opcionais para consulta
            limit: Limite de documentos retornados
            skip: Número de documentos a pular
            
        Returns:
            Lista de documentos encontrados
            
        Raises:
            PersistenceError: Erro durante a operação de listagem
        """
        pass

    @abstractmethod
    async def count(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta documentos na coleção com filtros opcionais.
        
        Args:
            collection_name: Nome da coleção
            filters: Filtros opcionais para consulta
            
        Returns:
            Número de documentos encontrados
            
        Raises:
            PersistenceError: Erro durante a operação de contagem
        """
        pass

    @abstractmethod
    async def exists(self, document_id: str, collection_name: str) -> bool:
        """
        Verifica se um documento existe.
        
        Args:
            document_id: ID do documento
            collection_name: Nome da coleção
            
        Returns:
            True se o documento existe
            
        Raises:
            PersistenceError: Erro durante a verificação
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do serviço de persistência.
        
        Returns:
            Dicionário com informações de status e métricas
            
        Raises:
            PersistenceError: Erro durante a verificação de saúde
        """
        pass