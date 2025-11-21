"""
Internal Context Block Models

These models represent the complete context block structure used internally,
including all processing metadata and image associations.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from ...core.constants.content_types import ContentType

class InternalSubContext(BaseModel):
    """
    Internal representation of a sub-context (used in context blocks with multiple sequences).
    """
    sequence: str = Field(..., description="Sequence identifier (I, II, III, IV)")
    type: str = Field(..., description="Type of sub-context (charge, propaganda, photo, etc.)")
    title: str = Field(..., description="Title of the sub-context")
    content: Optional[str] = Field(default=None, description="Text content of the sub-context (optional)")
    images: List[str] = Field(default_factory=list, description="Base64 images for this sub-context")
    azure_image_urls: List[str] = Field(default_factory=list, description="Azure Blob Storage URLs for this sub-context")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InternalSubContext":
        """Create InternalSubContext from dictionary format."""
        # 🔧 CORREÇÃO: content é opcional, retornar None se não existir ou se for string vazia
        content_value = data.get("content")
        if content_value == "":
            content_value = None
        
        return cls(
            sequence=data.get("sequence", ""),
            type=data.get("type", "image"),
            title=data.get("title", ""),
            content=content_value,
            images=data.get("images", []),
            azure_image_urls=data.get("azure_image_urls", [])
        )
class InternalContextContent(BaseModel):
    """
    Internal representation of context block content.
    
    This model preserves all content variations and processing metadata
    for debugging and analysis purposes.
    """
    # Core content
    description: List[str] = Field(
        default_factory=list,
        description="Main content texts"
    )
    
    # Additional content variations (for debugging/analysis)
    raw_content: Optional[str] = Field(
        default=None,
        description="Original raw content before processing"
    )
    processed_paragraphs: Optional[List[str]] = Field(
        default=None,
        description="Content after paragraph processing"
    )
    
    # Content metadata
    content_source: Optional[str] = Field(
        default=None,
        description="Source of the content (document_text, image_text, etc.)"
    )
    extraction_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of content extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about content processing"
    )
    
    @classmethod
    def from_dict(cls, content_data: Dict[str, Any]) -> "InternalContextContent":
        """
        Create InternalContextContent from dictionary format.
        
        Uses ContentConverter service to handle complex parsing logic.
        
        Args:
            content_data: Content data in dictionary format
            
        Returns:
            InternalContextContent instance
        """
        from app.services.converters import ContentConverter
        
        # Delegate parsing to dedicated service
        description, raw_content, content_source = ContentConverter.parse_content(content_data)
        
        return cls(
            description=description,
            raw_content=raw_content,
            content_source=content_source
        )
class InternalContextBlock(BaseModel):
    """
    Complete internal representation of a context block.
    
    This model contains all information needed for internal processing,
    including image associations, processing metadata, and debug information.
    """
    # Core context block data
    id: int = Field(..., description="Context block ID")
    type: List[ContentType] = Field(..., description="Content types in this block")
    content: InternalContextContent = Field(..., description="Block content")
    
    # Extended metadata
    title: Optional[str] = Field(default=None, description="Context block title")
    statement: Optional[str] = Field(default=None, description="Instruction statement")
    source: Optional[str] = Field(default="exam_document", description="Source of the context")
    
    # Image associations
    images: List[str] = Field(
        default_factory=list,
        description="Base64 images directly in this context block"
    )
    azure_image_urls: List[str] = Field(
        default_factory=list,
        description="Azure Blob Storage URLs for images in this context block"
    )
    associated_images: List[str] = Field(
        default_factory=list,
        description="IDs of images associated with this context block"
    )
    has_image: bool = Field(default=False, description="Whether block contains images")
    
    # Processing metadata
    extraction_method: Optional[str] = Field(
        default=None,
        description="Method used to extract this context block"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Confidence score of the extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about processing this block"
    )
    
    # Question associations
    related_questions: List[int] = Field(
        default_factory=list,
        description="Question IDs that reference this context block"
    )
    
    # Sub-contexts (for context blocks with multiple sequences like TEXTO I, II, III, IV)
    sub_contexts: Optional[List[InternalSubContext]] = Field(
        default=None,
        description="Sub-contexts for context blocks with multiple sequences"
    )
    
    @classmethod
    def from_dict(cls, block_data: Dict[str, Any]) -> "InternalContextBlock":
        """
        Create InternalContextBlock from dictionary format.
        
        Args:
            block_data: Context block data in dictionary format
            
        Returns:
            InternalContextBlock instance
        """
        from ...core.constants.content_types import ContentType
        
        # Extract content
        content_data = block_data.get("content", {})
        content = InternalContextContent.from_dict(content_data)
        
        # Handle type field
        block_type = block_data.get("type", ["text"])
        if isinstance(block_type, str):
            block_type = [block_type]
        
        # Convert string types to ContentType enums
        try:
            type_enums = [ContentType(t) for t in block_type]
        except ValueError:
            # Fallback for unknown types
            type_enums = [ContentType.TEXT]
        
        # ✅ Preserve sub_contexts if they exist
        sub_contexts = None
        if "sub_contexts" in block_data and block_data["sub_contexts"]:
            sub_contexts = [
                InternalSubContext.from_dict(sub_ctx)
                for sub_ctx in block_data["sub_contexts"]
            ]
        
        return cls(
            id=block_data.get("id", 0),
            type=type_enums,
            content=content,
            title=block_data.get("title"),
            statement=block_data.get("statement"),
            source=block_data.get("source", "exam_document"),
            images=block_data.get("images", []),
            azure_image_urls=block_data.get("azure_image_urls", []),
            associated_images=block_data.get("associated_images", []),
            has_image=block_data.get("hasImage", False),
            extraction_method="dict_conversion",
            sub_contexts=sub_contexts
        )
    def add_image_association(self, image_id: str) -> None:
        """Add an image association to this context block."""
        if image_id not in self.associated_images:
            self.associated_images.append(image_id)
            self.has_image = True
    
    def remove_image_association(self, image_id: str) -> None:
        """Remove an image association from this context block."""
        if image_id in self.associated_images:
            self.associated_images.remove(image_id)
            self.has_image = len(self.associated_images) > 0
    
    def add_question_reference(self, question_id: int) -> None:
        """Add a question reference to this context block."""
        if question_id not in self.related_questions:
            self.related_questions.append(question_id)
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "type": ["text"],
                "content": {
                    "description": [
                        "Reza a lenda que um monge budista desafiou seus discípulos."
                    ]
                },
                "title": "FEIJÕES OU PROBLEMAS?",
                "statement": "Leia o texto a seguir",
                "source": "exam_document",
                "has_image": False,
                "associated_images": [],
                "related_questions": [1, 2, 3],
                "extraction_method": "pattern_matching",
                "confidence_score": 0.95
            }
        }
