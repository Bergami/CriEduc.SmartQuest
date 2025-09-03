from fastapi import APIRouter, UploadFile, File, Query, Request
from typing import Dict, Any

# Importações dos novos serviços e dos existentes
from app.services.document_extraction_service import DocumentExtractionService
from app.services.analyze_service import AnalyzeService
from app.services.image_extraction import ImageExtractionMethod
from app.validators.analyze_validator import AnalyzeValidator
from app.adapters import DocumentResponseAdapter
from app.dtos.responses.document_response_dto import DocumentResponseDTO
from app.core.exceptions import (
    DocumentProcessingError,
    ValidationException
)
from app.core.utils import handle_exceptions
from app.core.logging import structured_logger

# Mocks e Orquestradores legados ainda podem ser necessários para outros endpoints
from app.services.document_processing_orchestrator import DocumentProcessingOrchestrator
from app.services.image_extraction import ImageExtractionOrchestrator


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
# ENDPOINTS LEGADOS/MOCK (Mantidos para não quebrar testes existentes)
# ==================================================================================

@router.post("/analyze_document_mock")
@handle_exceptions("azure_mock_document_analysis")
async def analyze_document_mock(
    request: Request,
    image_extraction_method: str = Query("manual_pdf", description="Image extraction method: manual_pdf (recommended for mock)")
):
    """
    Analisa documento usando a resposta mais recente salva do Azure Document Intelligence.
    """
    structured_logger.info(
        "Starting Azure mock document analysis",
        context={"image_extraction_method": image_extraction_method}
    )
    
    try:
        selected_method = ImageExtractionMethod(image_extraction_method)
    except ValueError:
        available_methods = [method.value for method in ImageExtractionMethod]
        raise ValidationException(f"Invalid extraction method '{image_extraction_method}'. Available methods: {available_methods}")
    
    internal_response = await AnalyzeService.process_document_with_models_mock(
        email="test@mock.com",
        image_extraction_method=selected_method
    )
    
    api_response = DocumentResponseAdapter.to_api_response(internal_response)
    
    structured_logger.info(
        "Azure mock document analysis completed successfully",
        context={"header_images_count": len(api_response.get("header", {}).get("images", []))}
    )

    return api_response

@router.post("/analyze_document_with_figures")
@handle_exceptions("document_analysis_with_figures")
async def analyze_document_with_figures(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(..., description="PDF file for analysis"),
    extraction_method: str = Query("azure_figures", description="Image extraction method: azure_figures or manual_pdf"),
    compare_methods: bool = Query(False, description="Compare both extraction methods for validation"),
    use_refactored: bool = Query(True, description="Use refactored version with enhanced processing")
):
    """
    Analisa documento PDF e extrai informações estruturadas com foco na extração de figuras.
    (Este endpoint mantém sua lógica legada por enquanto)
    """
    structured_logger.info(
        "Starting document analysis with figures extraction",
        context={
            "email": email,
            "filename": file.filename,
            "extraction_method": extraction_method,
            "compare_methods": compare_methods,
        }
    )
    
    AnalyzeValidator.validate_all(file, email)
    
    try:
        selected_method = ImageExtractionMethod(extraction_method)
    except ValueError:
        available_methods = [method.value for method in ImageExtractionMethod]
        raise ValidationException(f"Invalid extraction method '{extraction_method}'. Available methods: {available_methods}")
    
    # A lógica deste endpoint permanece a mesma por enquanto, pois tem um fluxo diferente.
    # Uma futura refatoração poderia unificar os serviços.
    orchestrator = DocumentProcessingOrchestrator(
        email=email,
        file=file,
        use_refactored=use_refactored,
        image_extraction_method=selected_method,
        compare_methods=compare_methods
    )
    result = await orchestrator.process_document_with_figures()

    structured_logger.info(
        "Document analysis with figures completed successfully",
        context={"email": email, "total_images": len(result.get("image_data", {}))}
    )

    return result