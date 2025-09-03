"""
Internal Document Data Models

These models represent the complete document structure used internally,
including all metadata and processing information.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .image_models import InternalImageData
from .question_models import InternalQuestion  # 🆕 ADICIONADO - tipo Pydantic
from .context_models import InternalContextBlock  # 🆕 ADICIONADO - tipo Pydantic


class InternalDocumentMetadata(BaseModel):
    """
    Complete document metadata for internal processing.
    
    This model contains all parsed header information plus
    internal processing metadata and categorized images.
    """
    # Parsed header fields
    network: Optional[str] = Field(default=None, description="Education network")
    school: Optional[str] = Field(default=None, description="School name")
    city: Optional[str] = Field(default=None, description="City name")
    teacher: Optional[str] = Field(default=None, description="Teacher name")
    subject: Optional[str] = Field(default=None, description="Subject")
    exam_title: Optional[str] = Field(default=None, description="Exam title")
    trimester: Optional[str] = Field(default=None, description="Trimester")
    grade: Optional[str] = Field(default=None, description="Grade/year")
    class_: Optional[str] = Field(default=None, alias="class", description="Class identifier")
    student: Optional[str] = Field(default=None, description="Student name")
    grade_value: Optional[str] = Field(default=None, description="Grade value")
    date: Optional[str] = Field(default=None, description="Exam date")
    
    # Internal processing data
    header_images: List[InternalImageData] = Field(
        default_factory=list,
        description="Images categorized as header images"
    )
    content_images: List[InternalImageData] = Field(
        default_factory=list, 
        description="Images categorized as content images"
    )
    
    # Processing metadata
    extraction_confidence: Optional[float] = Field(
        default=None,
        description="Overall confidence of header extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about header processing"
    )
    
    @classmethod
    def from_legacy_header(
        cls, 
        legacy_header: Dict[str, Any], 
        header_images: List[InternalImageData] = None,
        content_images: List[InternalImageData] = None
    ) -> "InternalDocumentMetadata":
        """
        Create InternalDocumentMetadata from legacy header dictionary.
        
        Args:
            legacy_header: Dictionary from HeaderParser.parse()
            header_images: List of header images
            content_images: List of content images
            
        Returns:
            InternalDocumentMetadata instance
        """
        return cls(
            network=legacy_header.get("network"),
            school=legacy_header.get("school"),
            city=legacy_header.get("city"),
            teacher=legacy_header.get("teacher"),
            subject=legacy_header.get("subject"),
            exam_title=legacy_header.get("exam_title"),
            trimester=legacy_header.get("trimester"),
            grade=legacy_header.get("grade"),
            class_=legacy_header.get("class"),
            student=legacy_header.get("student"),
            grade_value=legacy_header.get("grade_value"),
            date=legacy_header.get("date"),
            header_images=header_images or [],
            content_images=content_images or []
        )
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert back to legacy header format for backwards compatibility.
        
        Returns:
            Dictionary in the format expected by current code
        """
        result = {
            "network": self.network,
            "school": self.school,
            "city": self.city,
            "teacher": self.teacher,
            "subject": self.subject,
            "exam_title": self.exam_title,
            "trimester": self.trimester,
            "grade": self.grade,
            "class": self.class_,
            "student": self.student,
            "grade_value": self.grade_value,
            "date": self.date,
            "images": [img.base64_data for img in self.header_images] if self.header_images else []
        }
        return result
    
    class Config:
        # Allow field alias for 'class' 
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "network": "PREFEITURA DE VILA VELHA SEMED",
                "school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
                "city": "Vila Velha",
                "teacher": "Danielle",
                "subject": "Língua Portuguesa",
                "exam_title": "Prova de recuperação",
                "trimester": "2º TRIMESTRE",
                "grade": "7º ano do Ensino Fundamental TURMA:",
                "class": None,
                "student": None,
                "grade_value": "30,0",
                "date": None,
                "header_images": [],
                "content_images": [],
                "extraction_confidence": 0.95
            }
        }


class InternalDocumentResponse(BaseModel):
    """
    Complete internal document response with all processing data.
    
    This is the master model that contains everything needed for
    internal processing, debugging, and analysis.
    """
    # Core response data
    email: str = Field(..., description="User email")
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    
    # Document content and metadata
    document_metadata: InternalDocumentMetadata = Field(
        ..., 
        description="Complete document metadata with images"
    )
    
    # Questions and context (fully typed Pydantic models)
    questions: List[InternalQuestion] = Field(
        default_factory=list,
        description="Questions with complete Pydantic validation"  # ✅ MIGRADO
    )
    context_blocks: List[InternalContextBlock] = Field(
        default_factory=list,
        description="Context blocks with complete Pydantic validation"  # ✅ MIGRADO
    )
    
    # Raw processing data
    extracted_text: Optional[str] = Field(
        default=None,
        description="Raw extracted text"
    )
    provider_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw metadata from document provider"
    )
    
    # All images (for internal use)
    all_images: List[InternalImageData] = Field(
        default_factory=list,
        description="All images from the document with complete metadata"
    )
    
    def get_header_images(self) -> List[InternalImageData]:
        """Get all images categorized as header images."""
        return self.document_metadata.header_images
    
    def get_content_images(self) -> List[InternalImageData]:
        """Get all images categorized as content images.""" 
        return self.document_metadata.content_images
    
    def get_images_by_page(self, page: int) -> List[InternalImageData]:
        """Get all images from a specific page."""
        return [img for img in self.all_images if img.page == page]
    
    def get_categorization_summary(self) -> Dict[str, int]:
        """Get summary of image categorization."""
        return {
            "total_images": len(self.all_images),
            "header_images": len(self.get_header_images()),
            "content_images": len(self.get_content_images()),
            "uncategorized": len([img for img in self.all_images if img.categorization is None])
        }
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy format for backwards compatibility.
        
        Returns:
            Dictionary in legacy format expected by current code
        """
        return {
            "email": self.email,
            "document_id": self.document_id,
            "filename": self.filename,
            "header": self.document_metadata.to_legacy_format(),
            "questions": [q.to_legacy_format() for q in self.questions],
            "context_blocks": [cb.to_legacy_format() for cb in self.context_blocks],
            "extracted_text": self.extracted_text,
            "provider_metadata": self.provider_metadata,
            "all_images": [img.dict() for img in self.all_images]
        }
    
    @classmethod
    def from_legacy_format(
        cls,
        legacy_response: Dict[str, Any],
        document_metadata: "InternalDocumentMetadata",
        all_images: List[InternalImageData] = None
    ) -> "InternalDocumentResponse":
        """
        Create InternalDocumentResponse from legacy format with full Pydantic validation.
        
        Args:
            legacy_response: Legacy response dictionary
            document_metadata: Document metadata (already Pydantic)
            all_images: All images from document
            
        Returns:
            InternalDocumentResponse with Pydantic models
        """
        # Convert questions to Pydantic
        questions = []
        for q_dict in legacy_response.get("questions", []):
            questions.append(InternalQuestion.from_legacy_question(q_dict))
        
        # Convert context blocks to Pydantic
        context_blocks = []
        for cb_dict in legacy_response.get("context_blocks", []):
            context_blocks.append(InternalContextBlock.from_legacy_context_block(cb_dict))
        
        return cls(
            email=legacy_response.get("email", ""),
            document_id=legacy_response.get("document_id", ""),
            filename=legacy_response.get("filename", ""),
            document_metadata=document_metadata,
            questions=questions,
            context_blocks=context_blocks,
            extracted_text=legacy_response.get("extracted_text"),
            provider_metadata=legacy_response.get("provider_metadata", {}),
            all_images=all_images or []
        )
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "document_id": "12345-abcde",
                "filename": "prova_3tri.pdf",
                "document_metadata": {
                    "network": "PREFEITURA DE VILA VELHA SEMED",
                    "subject": "Língua Portuguesa",
                    "header_images": [],
                    "content_images": []
                },
                "questions": [],
                "context_blocks": [],
                "all_images": []
            }
        }
