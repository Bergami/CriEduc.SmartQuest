"""
API Response DTOs for Document Processing

These DTOs represent the main document processing results optimized for API responses.
They aggregate all document analysis results in a clean, consumer-friendly format.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .image_dtos import ImageListDTO
from .context_dtos import ContextListDTO
from .question_dtos import QuestionListDTO


class DocumentMetadataDTO(BaseModel):
    """Simplified document metadata for API responses."""
    # Essential document information
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
    date: Optional[str] = Field(default=None, description="Exam date")
    
    @classmethod
    def from_internal_metadata(cls, internal_metadata) -> "DocumentMetadataDTO":
        """
        Create DocumentMetadataDTO from InternalDocumentMetadata.
        
        Args:
            internal_metadata: InternalDocumentMetadata instance
            
        Returns:
            Simplified DocumentMetadataDTO
        """
        return cls(
            network=internal_metadata.network,
            school=internal_metadata.school,
            city=internal_metadata.city,
            teacher=internal_metadata.teacher,
            subject=internal_metadata.subject,
            exam_title=internal_metadata.exam_title,
            trimester=internal_metadata.trimester,
            grade=internal_metadata.grade,
            class_=internal_metadata.class_,
            student=internal_metadata.student,
            date=internal_metadata.date
        )
    
    class Config:
        schema_extra = {
            "example": {
                "network": "SESI",
                "school": "Escola SESI Campinas",
                "city": "Campinas",
                "teacher": "Maria Silva",
                "subject": "Língua Portuguesa",
                "exam_title": "Avaliação do 3º Trimestre",
                "trimester": "3º Trimestre",
                "grade": "9º Ano",
                "class": "9º A",
                "student": "João Santos",
                "date": "2024-11-15"
            }
        }


class ProcessingSummaryDTO(BaseModel):
    """Summary of document processing results."""
    # Processing statistics
    total_images: int = Field(default=0, description="Total number of images extracted")
    total_contexts: int = Field(default=0, description="Total number of context blocks")
    total_questions: int = Field(default=0, description="Total number of questions")
    
    # Quality indicators
    avg_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Average confidence score across all extractions"
    )
    
    # Content distribution
    image_categories: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of images by category"
    )
    question_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of questions by type"
    )
    content_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of context blocks by content type"
    )
    
    # Processing metadata
    processing_time: Optional[float] = Field(
        default=None,
        description="Total processing time in seconds"
    )
    extraction_method: str = Field(
        default="azure_document_intelligence",
        description="Primary extraction method used"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_images": 5,
                "total_contexts": 3,
                "total_questions": 10,
                "avg_confidence": 0.92,
                "image_categories": {
                    "header": 1,
                    "content": 4
                },
                "question_types": {
                    "multiple_choice": 8,
                    "true_false": 2
                },
                "content_types": {
                    "text": 2,
                    "mixed": 1
                },
                "processing_time": 15.3,
                "extraction_method": "azure_document_intelligence"
            }
        }


class DocumentResponseDTO(BaseModel):
    """
    Complete document processing response for API consumers.
    
    This DTO aggregates all processing results in a clean, optimized format
    suitable for API responses without internal processing metadata.
    """
    # Document identification
    document_id: Optional[str] = Field(default=None, description="Unique document identifier")
    
    # Document metadata
    metadata: DocumentMetadataDTO = Field(..., description="Document metadata")
    
    # Processing results
    images: ImageListDTO = Field(default_factory=ImageListDTO, description="Extracted images")
    contexts: ContextListDTO = Field(default_factory=ContextListDTO, description="Context blocks")
    questions: QuestionListDTO = Field(default_factory=QuestionListDTO, description="Questions")
    
    # Processing summary
    summary: ProcessingSummaryDTO = Field(
        default_factory=ProcessingSummaryDTO,
        description="Processing summary and statistics"
    )
    
    # Response metadata
    processed_at: datetime = Field(
        default_factory=datetime.now,
        description="When the document was processed"
    )
    api_version: str = Field(
        default="2.0",
        description="API version used for processing"
    )
    
    @classmethod
    def from_internal_response(cls, internal_response) -> "DocumentResponseDTO":
        """
        Create DocumentResponseDTO from InternalDocumentResponse.
        
        Args:
            internal_response: InternalDocumentResponse instance
            
        Returns:
            Optimized DocumentResponseDTO for API response
        """
        # Convert metadata
        metadata_dto = DocumentMetadataDTO.from_internal_metadata(internal_response.metadata)
        
        # Convert images
        images_dto = ImageListDTO.from_internal_images(internal_response.images)
        
        # Convert contexts
        contexts_dto = ContextListDTO.from_internal_contexts(internal_response.contexts)
        
        # Convert questions
        questions_dto = QuestionListDTO.from_internal_questions(internal_response.questions)
        
        # Calculate processing summary
        summary = cls._calculate_summary(internal_response, images_dto, contexts_dto, questions_dto)
        
        return cls(
            document_id=getattr(internal_response, 'document_id', None),
            metadata=metadata_dto,
            images=images_dto,
            contexts=contexts_dto,
            questions=questions_dto,
            summary=summary
        )
    
    @staticmethod
    def _calculate_summary(
        internal_response,
        images_dto: ImageListDTO,
        contexts_dto: ContextListDTO,
        questions_dto: QuestionListDTO
    ) -> ProcessingSummaryDTO:
        """Calculate processing summary from converted DTOs."""
        
        # Calculate average confidence
        confidences = []
        
        # Collect image confidences
        for img in images_dto.images:
            if img.confidence:
                confidences.append(img.confidence)
        
        # Collect question confidences
        for q in questions_dto.questions:
            if q.confidence:
                confidences.append(q.confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else None
        
        # Extract categories and types
        image_categories = {}
        for img in images_dto.images:
            cat = img.category
            image_categories[cat] = image_categories.get(cat, 0) + 1
        
        return ProcessingSummaryDTO(
            total_images=images_dto.total_count,
            total_contexts=contexts_dto.total_count,
            total_questions=questions_dto.total_count,
            avg_confidence=avg_confidence,
            image_categories=image_categories,
            question_types=questions_dto.answer_types,
            content_types=contexts_dto.content_types
        )
    
    def get_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy format for backward compatibility.
        
        Returns:
            Dictionary in legacy response format
        """
        return {
            "header": {
                "network": self.metadata.network,
                "school": self.metadata.school,
                "city": self.metadata.city,
                "teacher": self.metadata.teacher,
                "subject": self.metadata.subject,
                "exam_title": self.metadata.exam_title,
                "trimester": self.metadata.trimester,
                "grade": self.metadata.grade,
                "class": self.metadata.class_,
                "student": self.metadata.student,
                "date": self.metadata.date
            },
            "contexts": [
                {
                    "id": ctx.id,
                    "type": ctx.type,
                    "content": {"description": ctx.content.description},
                    "title": ctx.title,
                    "statement": ctx.statement,
                    "hasImage": ctx.has_image
                }
                for ctx in self.contexts.contexts
            ],
            "questions": [
                {
                    "number": q.number,
                    "question": q.content.statement,
                    "alternatives": [
                        {
                            "letter": opt.label,
                            "text": opt.text,
                            "isCorrect": opt.is_correct
                        }
                        for opt in q.options
                    ],
                    "contextId": q.context_id,
                    "hasImage": q.has_image,
                    "subject": q.subject
                }
                for q in self.questions.questions
            ],
            "images": [
                {
                    "id": img.id,
                    "content": img.base64_data,
                    "page": img.page,
                    "category": img.category
                }
                for img in self.images.images
            ],
            "summary": {
                "totalImages": self.summary.total_images,
                "totalContexts": self.summary.total_contexts,
                "totalQuestions": self.summary.total_questions,
                "avgConfidence": self.summary.avg_confidence
            }
        }
    
    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_12345",
                "metadata": {
                    "network": "SESI",
                    "school": "Escola SESI Campinas",
                    "subject": "Língua Portuguesa",
                    "exam_title": "Avaliação do 3º Trimestre",
                    "grade": "9º Ano"
                },
                "images": {
                    "images": [],
                    "total_count": 0
                },
                "contexts": {
                    "contexts": [],
                    "total_count": 0
                },
                "questions": {
                    "questions": [],
                    "total_count": 0
                },
                "summary": {
                    "total_images": 0,
                    "total_contexts": 0,
                    "total_questions": 0,
                    "avg_confidence": 0.95
                },
                "processed_at": "2024-08-26T10:30:00Z",
                "api_version": "2.0"
            }
        }
