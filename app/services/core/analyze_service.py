"""
🎯 Analyze Service - FASE 3 SOLID Refactoring

NOVA RESPONSABILIDADE ÚNICA (SRP Máximo):
- Validar dados de entrada
- Delegar análise para DocumentAnalysisOrchestrator
- Formatar resposta

RESPONSABILIDADES REMOVIDAS (movidas para DocumentAnalysisOrchestrator):
- Orquestração do pipeline de análise
- Coordenação de extração e categorização de imagens
- Parsing de header e questões
- Construção de context blocks

Esta classe agora segue o princípio SRP de forma extrema,
focando apenas em validação e delegação.
"""
import logging
from typing import Dict, Any
from fastapi import UploadFile

from app.services.core.document_analysis_orchestrator import DocumentAnalysisOrchestrator
from app.services.image.image_categorization_service import ImageCategorizationService
from app.services.image.extraction.image_extraction_orchestrator import ImageExtractionOrchestrator
from app.services.azure.azure_figure_processor import AzureFigureProcessor
from app.services.context.refactored_context_builder import RefactoredContextBlockBuilder
from app.models.internal import InternalDocumentResponse
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class AnalyzeService:
    """
    🎯 FASE 3: Serviço com Responsabilidade Única Máxima (SRP)
    
    ÚNICA RESPONSABILIDADE:
    - Validar dados de entrada
    - Delegar análise completa para DocumentAnalysisOrchestrator
    - Retornar resposta formatada
    
    PRINCÍPIOS SOLID APLICADOS:
    - SRP: Uma única responsabilidade - coordenação de alto nível
    - OCP: Extensível via diferentes orquestradores
    - LSP: Pode usar qualquer implementação de DocumentAnalysisOrchestrator
    - DIP: Depende de abstrações (orquestrador injetado)
    
    BEFORE: 240+ linhas com múltiplas responsabilidades
    AFTER: ~30 linhas focadas em validação e delegação
    """
    
    def __init__(self):
        """
        Inicializa o serviço com orquestrador especializado.
        
        FASE 4 TODO: Substituir por dependency injection via container
        """
        # Dependency composition (preparação para DI Container na Fase 4)
        self._orchestrator = DocumentAnalysisOrchestrator(
            image_categorizer=ImageCategorizationService(),
            image_extractor=ImageExtractionOrchestrator(),
            context_builder=RefactoredContextBlockBuilder(),
            figure_processor=AzureFigureProcessor()
        )
        self._logger = logging.getLogger(__name__)

    async def process_document_with_models(
        self,
        extracted_data: Dict[str, Any],
        email: str,
        filename: str,
        file: UploadFile,
        use_refactored: bool = True
    ) -> InternalDocumentResponse:
        """
        🎯 FASE 3: Método ultra-simplificado focado em SRP.
        
        RESPONSABILIDADES:
        1. Validação de entrada (input validation)
        2. Delegação completa para orquestrador
        3. Log de resultado
        
        Args:
            extracted_data: Dados brutos extraídos
            email: Email do usuário
            filename: Nome do arquivo
            file: UploadFile para fallback
            use_refactored: Flag para usar lógica avançada
            
        Returns:
            InternalDocumentResponse: Resposta estruturada completa
            
        Raises:
            DocumentProcessingError: Em caso de erro de validação ou processamento
        """
        
        # 1. Input validation (única responsabilidade restante)
        self._validate_input_data(extracted_data, email, filename, file)
        
        # 2. Complete delegation to specialized orchestrator
        self._logger.info(f"🎯 FASE 3: Delegating analysis to DocumentAnalysisOrchestrator for {filename}")
        
        try:
            response = await self._orchestrator.orchestrate_analysis(
                extracted_data=extracted_data,
                email=email,
                filename=filename,
                file=file,
                use_refactored=use_refactored
            )
            
            # 3. Success logging
            self._logger.info(f"✅ FASE 3: Analysis completed successfully for {filename}")
            return response
            
        except Exception as e:
            self._logger.error(f"❌ FASE 3: Analysis failed for {filename}: {str(e)}")
            raise DocumentProcessingError(f"Document analysis failed: {str(e)}") from e

    def _validate_input_data(self,
                           extracted_data: Dict[str, Any],
                           email: str,
                           filename: str,
                           file: UploadFile) -> None:
        """
        Valida dados de entrada do processamento.
        
        Raises:
            DocumentProcessingError: Se dados inválidos
        """
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
        
        self._logger.debug(f"✅ Input validation passed for {filename}")

# ==================================================================================
# 🧹 CÓDIGO LEGADO REMOVIDO - MOVIDO PARA DocumentAnalysisOrchestrator
# ==================================================================================
# - Todo o pipeline de análise (240+ linhas)
# - Lógica de extração e categorização de imagens
# - Parsing de header e questões
# - Construção de context blocks
# - Associação de figuras
# - Agregação de resposta
#
# BENEFÍCIOS DA REFATORAÇÃO:
# - Redução de 240+ linhas para ~60 linhas (-75%)
# - Responsabilidade única bem definida (SRP)
# - Fácil testabilidade (mock apenas o orquestrador)
# - Base preparada para Dependency Injection (Fase 4)
# ==================================================================================