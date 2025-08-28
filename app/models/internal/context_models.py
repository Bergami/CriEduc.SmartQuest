"""
Internal Context Block Models

These models represent the complete context block structure used internally,
including all processing metadata and image associations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ...core.constants.content_types import ContentType


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
    def from_legacy_content(cls, legacy_content: Dict[str, Any]) -> "InternalContextContent":
        """
        Create InternalContextContent from legacy format.
        
        Args:
            legacy_content: Legacy content dictionary
            
        Returns:
            InternalContextContent instance
        """
        # Handle different legacy formats
        if isinstance(legacy_content, dict):
            if "description" in legacy_content:
                if isinstance(legacy_content["description"], list):
                    description = legacy_content["description"]
                else:
                    description = [legacy_content["description"]]
            else:
                # Fallback: try to extract from other fields
                description = []
                for key in ["texts", "content", "paragraphs"]:
                    if key in legacy_content:
                        if isinstance(legacy_content[key], list):
                            description.extend(legacy_content[key])
                        else:
                            description.append(str(legacy_content[key]))
        else:
            # Legacy content is just a string or list
            if isinstance(legacy_content, list):
                description = legacy_content
            else:
                description = [str(legacy_content)]
        
        return cls(
            description=description,
            raw_content=str(legacy_content),
            content_source="legacy_conversion"
        )
    
    def to_legacy_format(self) -> Dict[str, List[str]]:
        """
        Convert to legacy content format.
        
        Returns:
            Dictionary with description array
        """
        return {
            "description": self.description
        }
    
    class Config:
        schema_extra = {
            "example": {
                "description": [
                    "Reza a lenda que um monge budista desafiou seus discípulos.",
                    "O primeiro discípulo colocou o feijão em um sapato.",
                    "O segundo discípulo cozinhou o feijão."
                ],
                "raw_content": "Original raw text from document...",
                "content_source": "document_text",
                "extraction_confidence": 0.95
            }
        }


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
    
    @classmethod
    def from_legacy_context_block(cls, legacy_block: Dict[str, Any]) -> "InternalContextBlock":
        """
        Create InternalContextBlock from legacy format.
        
        Args:
            legacy_block: Legacy context block dictionary
            
        Returns:
            InternalContextBlock instance
        """
        from ...core.constants.content_types import ContentType
        
        # Extract content
        content_data = legacy_block.get("content", {})
        content = InternalContextContent.from_legacy_content(content_data)
        
        # Handle type field
        block_type = legacy_block.get("type", ["text"])
        if isinstance(block_type, str):
            block_type = [block_type]
        
        # Convert string types to ContentType enums
        try:
            type_enums = [ContentType(t) for t in block_type]
        except ValueError:
            # Fallback for unknown types
            type_enums = [ContentType.TEXT]
        
        return cls(
            id=legacy_block.get("id", 0),
            type=type_enums,
            content=content,
            title=legacy_block.get("title"),
            statement=legacy_block.get("statement"),
            source=legacy_block.get("source", "exam_document"),
            has_image=legacy_block.get("hasImage", False),
            extraction_method="legacy_conversion"
        )
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy context block format.
        
        Returns:
            Dictionary in legacy format
        """
        return {
            "id": self.id,
            "type": [t.value for t in self.type],
            "content": self.content.to_legacy_format(),
            "title": self.title,
            "statement": self.statement,
            "source": self.source,
            "hasImage": self.has_image
        }
    
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
