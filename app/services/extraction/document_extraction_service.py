"""
Document Extraction Service

Este serviço tem a responsabilidade única de extrair dados de um documento,
gerenciando de forma transparente o cache e os provedores de extração.
"""
import logging
from typing import Dict, Any
from fastapi import UploadFile
from app.core.cache import DocumentCacheManager
from app.services.core.document_extraction_factory import DocumentExtractionFactory

logger = logging.getLogger(__name__)

class DocumentExtractionService:
    """
    Serviço com a responsabilidade única de extrair dados de um documento,
    gerenciando de forma transparente o cache e os provedores de extração.
    """
    
    @staticmethod
    async def get_extraction_data(file: UploadFile, email: str) -> Dict[str, Any]:
        """
        Obtém os dados extraídos de um documento, usando o cache primeiro.
        Se não houver cache, chama o provedor de extração (Azure) e armazena o resultado.
        
        Args:
            file: Arquivo para extração
            email: Email do usuário para a chave de cache
            
        Returns:
            Dicionário com os dados extraídos.
        """
        # A lógica de cache é centralizada aqui.
        cache_manager = DocumentCacheManager()
        
        # 1. Verificar cache
        # O ponteiro do arquivo precisa ser resetado para a leitura do cache funcionar
        await file.seek(0)
        cached_result = await cache_manager.get_cached_document(email, file)
        if cached_result:
            logger.info(f"🎯 Cache HIT: Using cached extraction for {email} - {file.filename}")
            # Resetar o ponteiro do arquivo novamente para o próximo consumidor
            await file.seek(0)
            return cached_result.get("extracted_data")

        logger.info(f"⚡ Cache MISS: Extracting from provider for {email} - {file.filename}")
        
        # 2. Se não houver cache, extrair do provedor
        # Resetar o ponteiro do arquivo para a extração
        await file.seek(0)
        extractor = DocumentExtractionFactory.get_provider()
        extracted_data = await extractor.extract_document_data(file)
        
        # 3. Armazenar no cache para futuras requisições
        if extracted_data:
            # Resetar o ponteiro do arquivo para a criação da chave de cache
            await file.seek(0)
            await cache_manager.cache_document_result(email, file, extracted_data)
            logger.info(f"💾 Cached extraction result for {email} - {file.filename}")
        
        # Resetar o ponteiro do arquivo para o próximo consumidor
        await file.seek(0)
        return extracted_data
