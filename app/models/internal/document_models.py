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
    

    

    
    class Config:
        # Allow field alias for 'class' 
        allow_population_by_field_name = True


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
            "uncategorized": len([img for img in self.all_images if img.category is None])
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
