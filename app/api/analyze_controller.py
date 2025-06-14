from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.schemas.analyze_document.upload import (
    UploadAnalyzeDocumentRequest,
    UploadAnalyzeDocumentResponse
)
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post(
    "/analyze",
    summary="Upload and analyze a document",
    response_model=UploadAnalyzeDocumentResponse,
    tags=["Analyze"]
)
async def analyze_document(
    file: UploadFile = File(...),
    metadata: UploadAnalyzeDocumentRequest = Depends()
):
    """
    Handles the upload of a PDF and simulates its analysis.
    Accepts metadata fields like subject, category, difficulty, and tags.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Simula geração de ID, análise e resposta mock
    document_id = str(uuid4())
    total_questions = 10  # ← simulação
    status = "simulated"

    return UploadAnalyzeDocumentResponse(
        document_id=document_id,
        filename=file.filename,
        total_questions=total_questions,
        status=status
    )