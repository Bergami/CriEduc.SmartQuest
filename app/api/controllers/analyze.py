from fastapi import APIRouter, UploadFile, File, Query, Request
from typing import Dict, Any

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
    internal_response = await AnalyzeService.process_document_with_models(
        extracted_data=extracted_data,
        email=email,
        filename=file.filename,
        file=file,  # O arquivo ainda é necessário para o fallback de extração de imagens
        use_refactored=True
    )
    
    # --- ETAPA 3: Conversão para DTO da API ---
    # Converte a resposta interna (Pydantic) para o DTO da API (mantém compatibilidade)
    api_response = DocumentResponseDTO.from_internal_response(internal_response)
    
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