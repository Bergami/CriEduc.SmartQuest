from pydantic import BaseModel, Field
from typing import Optional, List
from typing import Dict, Optional, List


class UploadAnalyzeDocumentRequest(BaseModel):
    """Schema for the metadata fields provided when uploading an analyze document."""
    
    metadata: Dict[str, Optional[str]] = Field(
        {}, description="Metadata including subject, category, difficulty, and tags"
    )


class UploadAnalyzeDocumentResponse(BaseModel):
    """
    Schema returned after a document is successfully uploaded and analyzed.
    """

    document_id: str
    filename: str
    total_questions: int
    status: str = Field(..., description="Current status: simulated, parsed, failed, etc.")