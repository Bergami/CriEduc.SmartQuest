from fastapi import APIRouter, UploadFile, File, Query, Request
from app.services.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator
from app.core.exceptions import (
    DocumentProcessingError,
    InvalidEmailException,
    MissingFileException,
    InvalidDocumentFormatException,
    MultipleValidationException,
    ValidationException
)
from app.core.utils import handle_exceptions
from app.core.logging import structured_logger

router = APIRouter()

@router.post("/analyze_document")
@handle_exceptions("document_analysis")
async def analyze_document(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(None),
    use_mock: bool = Query(False, description="Use mock data from Azure Document Intelligence response")
):
    """
    Analisa documento PDF e extrai informações estruturadas
    
    Args:
        request: Objeto Request do FastAPI
        email: Email do usuário para análise
        file: Arquivo PDF para análise (opcional se use_mock=True)
        use_mock: Usar dados mock em vez de processamento real
    
    Returns:
        Dados extraídos do documento em formato estruturado
    
    Raises:
        ValidationException: Erro de validação de entrada
        DocumentProcessingError: Erro no processamento do documento
    """
    
    # Log contexto da operação
    structured_logger.info(
        "Starting document analysis",
        context={
            "email": email,
            "filename": file.filename if file else None,
            "content_type": file.content_type if file else None,
            "use_mock": use_mock,
            "has_file": file is not None
        }
    )
    
    # Validar se file é obrigatório quando não usar mock
    _validate_file_requirement(use_mock, file)
    
    # Validação de entrada
    structured_logger.debug("Executing input validation")
    if use_mock:
        AnalyzeValidator.validate_email_only(email)
    else:
        AnalyzeValidator.validate_all(file, email)
    structured_logger.debug("Input validation completed successfully")

    # Processamento do documento
    structured_logger.debug("Starting document processing")
    
    if use_mock:
        structured_logger.info("Using mock data for document processing", email=email)
        extracted_data = await AnalyzeService.process_document_mock(email)
    else:
        structured_logger.info(
            "Using Azure Document Intelligence for processing",
            context={
                "email": email,
                "filename": file.filename,
                "file_size": file.size if hasattr(file, 'size') else None
            }
        )
        extracted_data = await AnalyzeService.process_document(file, email)
    
    structured_logger.info(
        "Document analysis completed successfully",
        context={
            "email": email,
            "use_mock": use_mock,
            "result_keys": list(extracted_data.keys()) if extracted_data else []
        }
    )

    return extracted_data

def _validate_file_requirement(use_mock: bool, file: UploadFile) -> None:
    """
    Valida se arquivo é obrigatório baseado no uso de mock
    
    Args:
        use_mock: Se está usando dados mock
        file: Arquivo enviado
    
    Raises:
        MissingFileException: Quando arquivo é obrigatório mas não foi fornecido
    """
    if not use_mock and not file:
        raise MissingFileException()