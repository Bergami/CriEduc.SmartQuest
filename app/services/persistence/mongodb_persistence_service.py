"""
Implementação MongoDB do serviço de persistência

Implementa ISimplePersistenceService conforme escopo original do prompt.
Apenas operações essenciais sem complexidade desnecessária.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo.errors import PyMongoError

from app.models.persistence import AnalyzeDocumentRecord, AzureProcessingDataRecord
from app.services.infrastructure import MongoDBConnectionService
from .i_simple_persistence_service import ISimplePersistenceService
from .exceptions import PersistenceError


logger = logging.getLogger(__name__)


class MongoDBPersistenceService(ISimplePersistenceService):
    """
    Implementação MongoDB do serviço de persistência.
    
    Conforme escopo original: apenas 4 operações essenciais.
    Recebe conexão pronta via DI Container.
    """

    def __init__(self, connection_service: MongoDBConnectionService):
        """
        Inicializa o serviço com serviço de conexão MongoDB.
        
        Args:
            connection_service: Serviço de conexão MongoDB via DI Container
        """
        self._connection_service = connection_service
        self._logger = logging.getLogger(__name__)
        self._logger.info("MongoDBPersistenceService initialized with connection service")

    async def save_analysis_result(self, analysis_record: AnalyzeDocumentRecord) -> str:
        """
        Persiste resultado da análise conforme prompt original.
        
        Args:
            analysis_record: Registro de análise a ser salvo
            
        Returns:
            ID do documento salvo
            
        Raises:
            PersistenceError: Erro durante salvamento
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Converte para formato MongoDB
            doc_data = analysis_record.dict_for_mongo()
            
            # Insere documento
            result = await collection.insert_one(doc_data)
            
            self._logger.info(f"Analysis result saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self._logger.error(f"Error saving analysis result: {e}")
            raise PersistenceError(f"Failed to save analysis result: {str(e)}")

    async def save_azure_processing_data(self, azure_data_record: AzureProcessingDataRecord) -> str:
        """
        Persiste dados de processamento do Azure.
        
        Args:
            azure_data_record: Dados de processamento Azure
            
        Returns:
            ID do documento salvo
            
        Raises:
            PersistenceError: Erro durante salvamento
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["azure_processing_data"]
            
            # Converte para formato MongoDB
            doc_data = azure_data_record.dict_for_mongo()
            
            # Insere documento
            result = await collection.insert_one(doc_data)
            
            self._logger.info(f"Azure processing data saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            self._logger.error(f"Error saving Azure processing data: {e}")
            raise PersistenceError(f"Failed to save Azure processing data: {str(e)}")

    async def get_by_document_id(self, document_id: str) -> Optional[AnalyzeDocumentRecord]:
        """
        Recupera registro por ID do documento.
        
        Args:
            document_id: ID do documento
            
        Returns:
            Registro encontrado ou None
            
        Raises:
            PersistenceError: Erro durante busca
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Busca por _id
            try:
                from bson import ObjectId
                from bson.errors import InvalidId
                
                object_id = ObjectId(document_id)
                doc_data = await collection.find_one({"_id": object_id})
            except (ImportError, InvalidId):
                # Se não é ObjectId válido, busca como string
                doc_data = await collection.find_one({"_id": document_id})
            
            if doc_data is None:
                return None
                
            return AnalyzeDocumentRecord.from_mongo(doc_data)
            
        except Exception as e:
            self._logger.error(f"Error getting document by ID {document_id}: {e}")
            raise PersistenceError(f"Failed to get document by ID: {str(e)}")

    async def get_by_user_email(self, email: str, limit: int = 10) -> List[AnalyzeDocumentRecord]:
        """
        Recupera registros por email do usuário.
        
        Args:
            email: Email do usuário
            limit: Limite de registros retornados
            
        Returns:
            Lista de registros encontrados
            
        Raises:
            PersistenceError: Erro durante busca
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Busca por user_email, ordenado por created_at descendente
            cursor = collection.find(
                {"user_email": email}
            ).sort("created_at", -1).limit(limit)
            
            documents = []
            async for doc_data in cursor:
                try:
                    document = AnalyzeDocumentRecord.from_mongo(doc_data)
                    documents.append(document)
                except Exception as e:
                    self._logger.warning(f"Error deserializing document: {e}")
                    continue
                    
            self._logger.info(f"Found {len(documents)} documents for email: {email}")
            return documents
            
        except Exception as e:
            self._logger.error(f"Error getting documents by email {email}: {e}")
            raise PersistenceError(f"Failed to get documents by email: {str(e)}")

    async def get_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[AnalyzeDocumentRecord]:
        """
        Recupera registros por intervalo de datas.
        
        Args:
            start_date: Data início do intervalo
            end_date: Data fim do intervalo
            limit: Limite de registros retornados
            
        Returns:
            Lista de registros encontrados
            
        Raises:
            PersistenceError: Erro durante busca
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Busca por intervalo de created_at
            query = {
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            cursor = collection.find(query).sort("created_at", -1).limit(limit)
            
            documents = []
            async for doc_data in cursor:
                try:
                    document = AnalyzeDocumentRecord.from_mongo(doc_data)
                    documents.append(document)
                except Exception as e:
                    self._logger.warning(f"Error deserializing document: {e}")
                    continue
                    
            self._logger.info(f"Found {len(documents)} documents in date range: {start_date} to {end_date}")
            return documents
            
        except Exception as e:
            self._logger.error(f"Error getting documents by date range: {e}")
            raise PersistenceError(f"Failed to get documents by date range: {str(e)}")

    async def close(self):
        """
        Fecha recursos se necessário.
        
        Note: Database connection é gerenciada pelo DI Container,
        não fechamos aqui para não afetar outras instâncias.
        """
        self._logger.info("MongoDBPersistenceService closed (connection managed by DI Container)")