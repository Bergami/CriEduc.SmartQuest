from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.services.analyze_service import AnalyzeService

router = APIRouter()

@router.post("/analyze_document")
async def analyze_document(
    email: str = Query(..., description="E-mail do usuário para identificação"),
    file: UploadFile = File(...)
):
    """Recebe um PDF, valida o e-mail e retorna os metadados extraídos."""

    # # 🔍 **Validação do E-mail**
    # if not is_valid_email(email):
    #     raise HTTPException(status_code=400, detail="E-mail inválido")

    # 🛠 **Processamento do Documento**
    extracted_data = await AnalyzeService.process_document(file, email)

    return extracted_data