from fastapi import APIRouter, UploadFile, File, Query
from app.services.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator

router = APIRouter()

@router.post("/analyze_document")
async def analyze_document(
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(...)
):
    # ✅ Validação
    AnalyzeValidator.validate_all(file, email)

    # 🔍 Processamento
    extracted_data = await AnalyzeService.process_document(file, email)

    return extracted_data
