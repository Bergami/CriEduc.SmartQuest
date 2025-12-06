"""
Document Extraction Service

Este serviço tem a responsabilidade única de extrair dados de um documento
usando Azure Document Intelligence.
"""
import logging
from typing import Dict, Any
from fastapi import UploadFile
from app.services.core.document_extraction_factory import DocumentExtractionFactory

logger = logging.getLogger(__name__)

class DocumentExtractionService:
    """
    Serviço com a responsabilidade única de extrair dados de um documento
    usando Azure Document Intelligence.
    
    NOTA: Verificação de duplicatas agora é feita no controller antes
    de chamar este método.
    """
    
    @staticmethod
    async def get_extraction_data(file: UploadFile, email: str) -> Dict[str, Any]:
        """
        Extrai dados do documento usando Azure Document Intelligence.
        
        NOTA: Verificação de duplicatas agora é feita no controller
        antes de chamar este método.
        
        Args:
            file: Arquivo para extração
            email: Email do usuário (usado apenas para logging)
            
        Returns:
            Dicionário com os dados extraídos do Azure.
        """
        logger.info(f"⚡ Extracting document data for {email} - {file.filename}")
        
        # Resetar ponteiro do arquivo
        await file.seek(0)
        
        # Extrair do provedor (Azure Document Intelligence)
        extractor = DocumentExtractionFactory.get_provider()
        extracted_data = await extractor.extract_document_data(file)
        
        # Resetar ponteiro para próximo consumidor
        await file.seek(0)
        
        return extracted_data
