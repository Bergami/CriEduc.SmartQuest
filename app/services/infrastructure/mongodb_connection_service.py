"""
Serviço de conexão MongoDB

Gerencia conexão MongoDB através do DI Container.
"""
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import get_settings


logger = logging.getLogger(__name__)


class MongoDBConnectionService:
    """
    Serviço responsável por gerenciar conexão MongoDB.
    
    Implementa padrão Singleton através do DI Container.
    """

    def __init__(self):
        """Inicializa o serviço de conexão."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._settings = get_settings()
        logger.info("MongoDBConnectionService initialized")

    async def get_database(self) -> AsyncIOMotorDatabase:
        """
        Obtém conexão com a database MongoDB.
        
        Returns:
            Database MongoDB configurada
            
        Raises:
            ConnectionError: Se não conseguir conectar
        """
        if self._database is None:
            await self._connect()
        
        return self._database

    async def _connect(self):
        """
        Estabelece conexão com MongoDB.
        
        Raises:
            ConnectionError: Se falhar na conexão
        """
        try:
            self._client = AsyncIOMotorClient(
                self._settings.mongodb_url,
                serverSelectionTimeoutMS=self._settings.mongodb_connection_timeout,
                connectTimeoutMS=self._settings.mongodb_connection_timeout,
                socketTimeoutMS=self._settings.mongodb_connection_timeout
            )
            
            # Testa conexão
            await self._client.admin.command('ping')
            
            self._database = self._client[self._settings.mongodb_database]
            
            logger.info(f"MongoDB connection established: {self._settings.mongodb_database}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"MongoDB connection failed: {str(e)}")

    async def close(self):
        """Fecha conexão MongoDB."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")

    async def health_check(self) -> bool:
        """
        Verifica se conexão está funcionando.
        
        NÃO conecta automaticamente - apenas verifica se há conexão ativa.
        Use get_database() para garantir conexão antes de chamar health_check().
        
        Returns:
            True se conexão está ativa e funcionando
        """
        try:
            if self._client is None:
                return False
                
            await self._client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.warning(f"MongoDB health check failed: {e}")
            return False