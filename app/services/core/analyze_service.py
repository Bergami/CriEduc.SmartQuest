"""
Analyze Service

Serviço principal para análise de documentos usando Dependency Injection.
Responsável por validar entrada, delegar processamento e retornar resposta estruturada.
"""
import logging
from typing import Dict, Any
from fastapi import UploadFile

from app.core.interfaces import IDocumentAnalysisOrchestrator
from app.core.di_container import container
from app.models.internal import InternalDocumentResponse
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class AnalyzeService:
    """
    Serviço principal para análise de documentos com Dependency Injection.
    
    Utiliza DI Container para resolver dependências automaticamente,
    mantendo zero acoplamento com implementações concretas.
    """
    
    def __init__(self):
        """Inicializa o serviço. Dependências são resolvidas via DI Container quando necessário."""
        self._logger = logging.getLogger(__name__)

    async def process_document_with_models(
        self,
        extracted_data: Dict[str, Any],
        email: str,
        filename: str,
        file: UploadFile
    ) -> InternalDocumentResponse:
        """
        Processa documento completo usando DI Container.
        
        Args:
            extracted_data: Dados brutos extraídos
            email: Email do usuário
            filename: Nome do arquivo
            file: UploadFile para fallback
            
        Returns:
            InternalDocumentResponse: Resposta estruturada completa
            
        Raises:
            DocumentProcessingError: Em caso de erro de validação ou processamento
        """
        
        # Validação de entrada
        self._validate_input_data(extracted_data, email, filename, file)
        
        # Resolução via DI Container
        self._logger.info(f"Processing document analysis for {filename}")
        
        try:
            # Resolve orchestrator via DI Container
            orchestrator = container.resolve(IDocumentAnalysisOrchestrator)
            
            self._logger.debug(f"Orchestrator resolved: {type(orchestrator).__name__}")
            
            # Delegação para orquestrador
            response = await orchestrator.orchestrate_analysis(
                extracted_data=extracted_data,
                email=email,
                filename=filename,
                file=file
            )
            
            # Log de sucesso
            self._logger.info(f"Analysis completed successfully for {filename}")
            return response
            
        except Exception as e:
            self._logger.error(f"Analysis failed for {filename}: {str(e)}")
            raise DocumentProcessingError(f"Document analysis failed: {str(e)}") from e

    def _validate_input_data(self,
                           extracted_data: Dict[str, Any],
                           email: str,
                           filename: str,
                           file: UploadFile) -> None:
        """Valida dados de entrada do processamento."""
        if not extracted_data:
            raise DocumentProcessingError("extracted_data is required and cannot be empty")
        
        if not email or not email.strip():
            raise DocumentProcessingError("email is required and cannot be empty")
        
        if not filename or not filename.strip():
            raise DocumentProcessingError("filename is required and cannot be empty")
        
        if not file:
            raise DocumentProcessingError("file is required for image extraction fallback")
        
        # Validar estrutura básica de extracted_data
        if not isinstance(extracted_data, dict):
            raise DocumentProcessingError("extracted_data must be a dictionary")
        
        self._logger.debug(f"Input validation passed for {filename}")