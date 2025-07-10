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
    file: UploadFile = File(...)
):
    logger.debug(f"🔍 DEBUG: Iniciando análise do documento")
    logger.debug(f"📧 Email: {email}")
    logger.debug(f"📄 Arquivo: {file.filename}")
    logger.debug(f"📊 Content-Type: {file.content_type}")
    
    try:
        # ✅ Validação
        logger.debug("🔍 DEBUG: Executando validação...")
        AnalyzeValidator.validate_all(file, email)
        logger.debug("✅ DEBUG: Validação concluída com sucesso")

        # 🔍 Processamento - BREAKPOINT AQUI
        logger.debug("🔍 DEBUG: Iniciando processamento do documento...")
        extracted_data = await AnalyzeService.process_document(file, email)
        logger.debug(f"✅ DEBUG: Processamento concluído")

        return extracted_data
        
    except DocumentProcessingError as e:
        logger.error(f"❌ DEBUG: Erro no processamento do documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Document Processing Error",
                "message": f"Falha ao processar o documento: {e.message}",
                "type": "azure_ai_error"
            }
        )
    except Exception as e:
        logger.error(f"❌ DEBUG: Erro durante análise: {str(e)}")
        logger.error(f"🔍 DEBUG: Tipo do erro: {type(e).__name__}")
        raise
