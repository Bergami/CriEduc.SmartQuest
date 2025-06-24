from fastapi import APIRouter, UploadFile, File, Query
from app.parsers.header_parser.base import HeaderParser
from app.parsers.question_parser.base import QuestionParser
from app.services.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator
from app.utils.ocr_utils import OCRUtils

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

@router.post("/analyze_document_ocr")
async def analyze_document_ocr(file: UploadFile):
    file_bytes = await file.read()

    # ✅ Usa LayoutParser para extrair texto por blocos organizados
    pages_text = OCRUtils.extract_layoutparser_blocks_from_pdf_bytes(file_bytes)
    full_text = "\n".join(pages_text)

    # ✅ Processa os dados com os parsers já existentes
    header = HeaderParser.parse(full_text)
    question_data = QuestionParser.extract(full_text)

    return {
        "filename": file.filename,
        "pages": pages_text,
        "header": header,
        "questions": question_data["questions"],
        "context_blocks": question_data["context_blocks"]
    }