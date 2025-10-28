from fastapi import APIRouter, UploadFile, File, Query, Request
from typing import Dict, Any

# IMPORTANTE: Importar di_config PRIMEIRO para configurar dependências
from app.config import di_config  # Configura automaticamente todas as dependências

# Importações dos novos serviços e dos existentes
from app.services.extraction.document_extraction_service import DocumentExtractionService
from app.services.core.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator
from app.dtos.responses.document_response_dto import DocumentResponseDTO
from app.core.exceptions import (
    DocumentProcessingError,
    ValidationException
)
from app.core.utils import handle_exceptions
from app.core.logging import structured_logger


router = APIRouter()

@router.post("/analyze_document", response_model=DocumentResponseDTO)
@handle_exceptions("document_analysis")
async def analyze_document(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(..., description="PDF file for analysis")
) -> DocumentResponseDTO:
    """
    ✅ REFATORADO: Analisa um documento PDF com um fluxo de responsabilidades claras.
    1. Extrai os dados brutos (usando cache).
    2. Orquestra a análise desses dados.
    """
    structured_logger.info(
        "Starting document analysis with SOLID architecture",
        context={"email": email, "filename": file.filename}
    )
    
    # Validação de entrada
    structured_logger.debug("Executing input validation")
    AnalyzeValidator.validate_all(file, email)
    structured_logger.debug("Input validation completed successfully")

    # --- ETAPA 1: Extração de Dados (com cache transparente) ---
    structured_logger.debug("Step 1: Extracting data using DocumentExtractionService")
    extracted_data = await DocumentExtractionService.get_extraction_data(file, email)

    if not extracted_data:
        raise DocumentProcessingError("Failed to extract any data from the document. The file might be empty, corrupted, or in an unsupported format.")
    
    structured_logger.info(
        "Data extraction completed",
        context={"email": email, "filename": file.filename}
    )

    # --- ETAPA 2: Orquestração da Análise ---
    structured_logger.debug("Step 2: Orchestrating analysis using AnalyzeService")
    
    # Resolver AnalyzeService via DI Container (não instanciar manualmente)
    from app.core.di_container import container
    from app.core.interfaces import IAnalyzeService
    
    # Container resolve automaticamente TODA a árvore de dependências:
    # IAnalyzeService → AnalyzeService
    # └── IDocumentAnalysisOrchestrator → DocumentAnalysisOrchestrator
    #     ├── IImageCategorizer → ImageCategorizationService
    #     ├── IImageExtractor → ImageExtractionOrchestrator
    #     ├── IContextBuilder → RefactoredContextBlockBuilder
    #     └── IFigureProcessor → AzureFigureProcessor
    analyze_service = container.resolve(IAnalyzeService)
    
    structured_logger.debug(f"AnalyzeService resolved via DI Container: {type(analyze_service).__name__}")
    
    internal_response = await analyze_service.process_document_with_models(
        extracted_data=extracted_data,
        email=email,
        filename=file.filename,
        file=file,  # O arquivo ainda é necessário para o fallback de extração de imagens
        use_refactored=True
    )
    
    # --- ETAPA 3: Conversão para DTO da API ---
    # Converte a resposta interna (Pydantic) para o DTO da API (mantém compatibilidade)
    api_response = DocumentResponseDTO.from_internal_response(internal_response)
    
    # --- ETAPA 4: PERSISTÊNCIA OBRIGATÓRIA NO MONGODB ---
    from app.services.persistence import ISimplePersistenceService
    from app.models.persistence import AnalyzeDocumentRecord, DocumentStatus
    
    try:
        structured_logger.debug("Step 4: Persisting analysis result to MongoDB")
        
        # Resolver serviço de persistência via DI Container
        persistence_service = container.resolve(ISimplePersistenceService)
        
        # Criar registro conforme prompt original
        analysis_record = AnalyzeDocumentRecord.create_from_request(
            user_email=email,
            file_name=file.filename,
            response=api_response.dict(),  # Response JSON completo
            status=DocumentStatus.COMPLETED
        )
        
        # Salvar no MongoDB (lança erro se MongoDB estiver indisponível)
        document_id = await persistence_service.save_analysis_result(analysis_record)
        
        structured_logger.info(
            "Analysis result persisted successfully",
            context={
                "document_id": document_id,
                "user_email": email,
                "file_name": file.filename
            }
        )
        
    except Exception as e:
        # Log do erro e propaga a exceção (persistência é obrigatória)
        structured_logger.error(
            "Failed to persist analysis result - MongoDB required",
            context={"error": str(e), "email": email, "filename": file.filename}
        )
        raise DocumentProcessingError(f"Failed to persist analysis result: {str(e)}")
    
    structured_logger.info(
        "Document analysis completed successfully",
        context={
            "email": email,
            "document_id": internal_response.document_id,
            "questions_count": len(internal_response.questions),
            "context_blocks_count": len(internal_response.context_blocks),
            "header_images_count": len(internal_response.document_metadata.header_images),
            "migration_status": "100_percent_pydantic_flow"
        }
    )

    return api_response

# ==================================================================================
# 🧹 ENDPOINTS REMOVIDOS: analyze_document_mock e analyze_document_with_figures
# Removidos após confirmação de que o endpoint principal /analyze_document está funcionando
# ==================================================================================
