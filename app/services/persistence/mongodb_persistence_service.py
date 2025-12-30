"""
Implementação MongoDB do serviço de persistência

Implementa ISimplePersistenceService conforme escopo original do prompt.
Apenas operações essenciais sem complexidade desnecessária.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pymongo.errors import PyMongoError

from app.models.persistence import AnalyzeDocumentRecord, AzureProcessingDataRecord, AzureResponseRecord
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
            # get_database() já valida a conexão e lança ConnectionError se falhar
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Converte para formato MongoDB
            doc_data = analysis_record.dict_for_mongo()
            
            # Insere documento
            result = await collection.insert_one(doc_data)
            
            self._logger.info({
                "event": "analysis_result_saved",
                "status": "success",
                "document_id": str(result.inserted_id),
                "operation": "save_analysis_result"
            })
            return str(result.inserted_id)
            
        except ConnectionError as e:
            error_msg = f"MongoDB is unavailable: {str(e)}"
            self._logger.error({
                "event": "mongodb_unavailable",
                "operation": "save_analysis_result",
                "status": "error",
                "error": str(e)
            })
            raise PersistenceError(error_msg)
        except Exception as e:
            error_msg = f"Failed to save analysis result: {str(e)}"
            self._logger.error({
                "event": "save_analysis_error",
                "status": "error",
                "operation": "save_analysis_result",
                "error": str(e)
            })
            raise PersistenceError(error_msg)

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
            # get_database() já valida a conexão e lança ConnectionError se falhar
            database = await self._connection_service.get_database()
            collection = database["azure_processing_data"]
            
            # Converte para formato MongoDB
            doc_data = azure_data_record.dict_for_mongo()
            
            # Insere documento
            result = await collection.insert_one(doc_data)
            
            self._logger.info({
                "event": "azure_data_saved",
                "status": "success",
                "document_id": str(result.inserted_id),
                "operation": "save_azure_processing_data"
            })
            return str(result.inserted_id)
            
        except ConnectionError as e:
            error_msg = f"MongoDB is unavailable: {str(e)}"
            self._logger.error({
                "event": "mongodb_unavailable",
                "operation": "save_azure_processing_data",
                "status": "error",
                "error": str(e)
            })
            raise PersistenceError(error_msg)
        except Exception as e:
            error_msg = f"Failed to save Azure processing data: {str(e)}"
            self._logger.error({
                "event": "save_azure_data_error",
                "status": "error",
                "operation": "save_azure_processing_data",
                "error": str(e)
            })
            raise PersistenceError(error_msg)

    async def save_azure_response(self, azure_response_record: AzureResponseRecord) -> str:
        """
        Persiste response completo do Azure Document Intelligence.
        
        Args:
            azure_response_record: Response completo do Azure
            
        Returns:
            ID do documento salvo
            
        Raises:
            PersistenceError: Erro durante salvamento
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["azure_responses"]
            
            # Converte para formato MongoDB
            doc_data = azure_response_record.dict_for_mongo()
            
            # Insere documento
            result = await collection.insert_one(doc_data)
            
            self._logger.info({
                "event": "azure_response_saved",
                "status": "success",
                "document_id": str(result.inserted_id),
                "operation": "save_azure_response",
                "file_name": azure_response_record.file_name,
                "page_count": azure_response_record.page_count
            })
            return str(result.inserted_id)
            
        except ConnectionError as e:
            error_msg = f"MongoDB is unavailable: {str(e)}"
            self._logger.error({
                "event": "mongodb_unavailable",
                "operation": "save_azure_response",
                "status": "error",
                "error": str(e)
            })
            raise PersistenceError(error_msg)
        except Exception as e:
            error_msg = f"Failed to save Azure response: {str(e)}"
            self._logger.error({
                "event": "save_azure_response_error",
                "status": "error",
                "operation": "save_azure_response",
                "error": str(e)
            })
            raise PersistenceError(error_msg)

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

    async def get_by_user_email_with_filters(
        self,
        email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[list[AnalyzeDocumentRecord], int]:
        """
        Recupera registros por email com filtros opcionais e paginação.
        
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
            
        Raises:
            PersistenceError: Erro durante busca
        """
        try:
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Construir query base (email obrigatório)
            query = {"user_email": email}
            
            # Adicionar filtro de data se fornecido
            if start_date is not None and end_date is not None:
                query["created_at"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
            
            # Contar total de documentos que correspondem aos filtros
            total_count = await collection.count_documents(query)
            
            # Calcular skip para paginação (page 1 = skip 0, page 2 = skip page_size, etc)
            skip = (page - 1) * page_size
            
            # Buscar documentos com paginação
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
            
            documents = []
            async for doc_data in cursor:
                try:
                    document = AnalyzeDocumentRecord.from_mongo(doc_data)
                    documents.append(document)
                except Exception as e:
                    self._logger.warning(f"Error deserializing document: {e}")
                    continue
            
            self._logger.info(
                f"Found {len(documents)} documents for email {email} "
                f"(page {page}/{(total_count + page_size - 1) // page_size if total_count > 0 else 0}, "
                f"total: {total_count})"
            )
            
            return documents, total_count
            
        except Exception as e:
            self._logger.error(f"Error getting documents with filters for email {email}: {e}")
            raise PersistenceError(f"Failed to get documents with filters: {str(e)}")

    async def check_duplicate_document(
        self,
        email: str,
        filename: str,
        file_size: int
    ) -> Optional[AnalyzeDocumentRecord]:
        """
        Verifica duplicata usando índice otimizado.
        
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
        try:
            from app.models.persistence.enums import DocumentStatus
            
            database = await self._connection_service.get_database()
            collection = database["analyze_documents"]
            
            # Query otimizada com índice idx_duplicate_check
            query = {
                "user_email": email,
                "file_name": filename,
                "file_size": file_size,
                "status": DocumentStatus.COMPLETED.value  # Apenas docs bem-sucedidos
            }
            
            # Buscar documento (usa índice)
            doc = await collection.find_one(query)
            
            if doc:
                self._logger.info({
                    "event": "duplicate_document_found",
                    "email": email,
                    "filename": filename,
                    "file_size": file_size,
                    "document_id": str(doc["_id"]),
                    "processed_at": doc.get("created_at")
                })
                
                # Converter para model Pydantic
                return AnalyzeDocumentRecord.from_mongo(doc)
            
            return None
            
        except Exception as e:
            self._logger.error({
                "event": "duplicate_check_error",
                "error": str(e)
            })
            # Em caso de erro, retornar None para permitir processamento
            # (fail-safe: melhor reprocessar que bloquear)
            return None

    async def save_completed_analysis(
        self,
        email: str,
        filename: str,
        file_size: int,
        response_dict: dict
    ) -> str:
        """
        Método high-level para persistir resultado de análise completa.
        
        Encapsula toda a lógica de:
        1. Criar AnalyzeDocumentRecord com status COMPLETED
        2. Salvar no MongoDB via save_analysis_result
        3. Tratar erros de persistência
        
        Args:
            email: Email do usuário
            filename: Nome do arquivo
            file_size: Tamanho do arquivo em bytes
            response_dict: Dicionário com response completo (DocumentResponseDTO.dict())
            
        Returns:
            ID do documento salvo
            
        Raises:
            PersistenceError: Se MongoDB falhar (persistência obrigatória)
        """
        try:
            from app.models.persistence.enums import DocumentStatus
            
            self._logger.debug({
                "event": "saving_completed_analysis",
                "email": email,
                "filename": filename,
                "file_size": file_size
            })
            
            # Criar registro com status COMPLETED
            analysis_record = AnalyzeDocumentRecord.create_from_request(
                user_email=email,
                file_name=filename,
                file_size=file_size,
                response=response_dict,
                status=DocumentStatus.COMPLETED
            )
            
            # Salvar no MongoDB
            document_id = await self.save_analysis_result(analysis_record)
            
            self._logger.info({
                "event": "analysis_persisted_successfully",
                "document_id": document_id,
                "user_email": email,
                "file_name": filename
            })
            
            return document_id
            
        except Exception as e:
            self._logger.error({
                "event": "failed_to_persist_analysis",
                "error": str(e),
                "email": email,
                "filename": filename
            })
            raise PersistenceError(f"Failed to persist analysis result: {str(e)}")

    async def close(self):
        """
        Fecha recursos se necessário.
        
        Note: Database connection é gerenciada pelo DI Container,
        não fechamos aqui para não afetar outras instâncias.
        """
        self._logger.info("MongoDBPersistenceService closed (connection managed by DI Container)")