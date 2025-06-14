from pydantic import BaseModel, Field
from typing import Optional, List


class UploadAnalyzeDocumentRequest(BaseModel):
    """
    Schema for the metadata fields provided when uploading an analyze document.
    This data is submitted via multipart/form-data using Form(...)
    """

    subject: Optional[str] = Field(None, description="Subject of the exam (e.g. Math, History)")
    category: Optional[str] = Field(None, description="Exam category (e.g. ENEM, Vestibular)")
    difficulty_level: Optional[str] = Field(None, description="Optional difficulty level")
    tags: Optional[List[str]] = Field(None, description="Optional tags for filtering (e.g. ['algebra', 'geometry'])")


class UploadAnalyzeDocumentResponse(BaseModel):
    """
    Schema returned after a document is successfully uploaded and analyzed.
    """

    document_id: str
    filename: str
    total_questions: int
    status: str = Field(..., description="Current status: simulated, parsed, failed, etc.")