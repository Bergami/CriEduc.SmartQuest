from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.services.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator
from app.core.exceptions import DocumentProcessingError
import logging

# Configurar logging para debug
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze_document")
async def analyze_document(
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(None),
    use_mock: bool = Query(False, description="Use mock data from RetornoProcessamento.json")
):
    # Validar se file é obrigatório quando não usar mock
    _validate_file_requirement(use_mock, file)
    
    logger.debug(f"🔍 DEBUG: Iniciando análise do documento")
    logger.debug(f"📧 Email: {email}")
    logger.debug(f"📄 Arquivo: {file.filename if file else 'N/A (modo mock)'}")
    logger.debug(f"📊 Content-Type: {file.content_type if file else 'N/A (modo mock)'}")
    logger.debug(f"🔧 Use Mock: {use_mock}")
    
    try:
        # ✅ Validação
        logger.debug("🔍 DEBUG: Executando validação...")
        if use_mock:
            AnalyzeValidator.validate_email_only(email)
        else:
            AnalyzeValidator.validate_all(file, email)
        logger.debug("✅ DEBUG: Validação concluída com sucesso")

        # 🔍 Processing - BREAKPOINT HERE
        logger.debug("🔍 DEBUG: Starting document processing...")
        
        if use_mock:
            logger.debug("🔧 DEBUG: Using mock data...")
            extracted_data = await AnalyzeService.process_document_mock(email)
        else:
            logger.debug("🔧 DEBUG: Using normal processing (Azure)...")
            extracted_data = await AnalyzeService.process_document(file, email)
        logger.debug(f"✅ DEBUG: Processing completed")

        return extracted_data
        
    except DocumentProcessingError as e:
        logger.error(f"❌ DEBUG: Error in document processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Document Processing Error",
                "message": f"Failed to process document: {e.message}",
                "type": "azure_ai_error"
            }
        )
    except Exception as e:
        logger.error(f"❌ DEBUG: Error during analysis: {str(e)}")
        logger.error(f"🔍 DEBUG: Error type: {type(e).__name__}")
        raise

def _validate_file_requirement(use_mock: bool, file: UploadFile) -> None:
    """
    Validates if file is required based on mock usage
    """
    if not use_mock and not file:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing File",
                "message": "File is required when not using mock data",
                "type": "validation_error"
            }
        )