from fastapi import APIRouter, UploadFile, File, Query
from pydantic import EmailStr
from app.services.analyze_service import AnalyzeService

router = APIRouter()

@router.post("/analyze_document")
async def analyze_document(
    email: EmailStr = Query(..., description="E-mail do usuário para identificação"),
    file: UploadFile = File(...)
):
    """Recebe um PDF, valida o e-mail e retorna os metadados extraídos."""



    # 🛠 **Processamento do Documento**
    extracted_data = await AnalyzeService.process_document(file, email)

    return extracted_data