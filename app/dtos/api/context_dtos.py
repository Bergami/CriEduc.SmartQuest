"""
API Response DTOs for Context Blocks

These DTOs represent simplified context data optimized for API responses.
They focus on content delivery without internal processing metadata.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContextContentDTO(BaseModel):
    """Simplified context content for API responses."""
    description: List[str] = Field(
        default_factory=list,
        description="Context content paragraphs"
    )
    
    @classmethod
    def from_internal_content(cls, internal_content) -> "ContextContentDTO":
        """
        Create ContextContentDTO from InternalContextContent.
        
        Args:
            internal_content: InternalContextContent instance
            
        Returns:
            Simplified ContextContentDTO
        """
        return cls(
            description=internal_content.description
        )
    
    class Config:
        schema_extra = {
            "example": {
                "description": [
                    "Reza a lenda que um monge budista desafiou seus discípulos.",
                    "O primeiro discípulo colocou o feijão em um sapato.",
                    "O segundo discípulo cozinhou o feijão."
                ]
            }
        }


class ContextBlockDTO(BaseModel):
    """
    Simplified context block for API responses.
    
    Contains essential context information for API consumers,
    without internal processing metadata or debugging information.
    """
    # Core context data
    id: int = Field(..., description="Context block ID")
    type: List[str] = Field(..., description="Content types in this block")
    content: ContextContentDTO = Field(..., description="Block content")
    
    # Optional metadata
    title: Optional[str] = Field(default=None, description="Context block title")
    statement: Optional[str] = Field(default=None, description="Instruction statement")
    
    # Image associations (simplified)
    has_image: bool = Field(default=False, description="Whether block contains images")
    image_ids: List[str] = Field(
        default_factory=list,
        description="IDs of associated images"
    )
    
    # Question associations
    related_question_ids: List[int] = Field(
        default_factory=list,
        description="IDs of questions that reference this context"
    )
    
    @classmethod
    def from_internal_context(cls, internal_context) -> "ContextBlockDTO":
        """
        Create ContextBlockDTO from InternalContextBlock.
        
        Args:
            internal_context: InternalContextBlock instance
            
        Returns:
            Simplified ContextBlockDTO for API response
        """
        # Convert content
        content_dto = ContextContentDTO.from_internal_content(internal_context.content)
        
        # Convert types to strings
        type_strings = [t.value for t in internal_context.type]
        
        return cls(
            id=internal_context.id,
            type=type_strings,
            content=content_dto,
            title=internal_context.title,
            statement=internal_context.statement,
            has_image=internal_context.has_image,
            image_ids=internal_context.associated_images,
            related_question_ids=internal_context.related_questions
        )
    
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
                "has_image": False,
                "image_ids": [],
                "related_question_ids": [1, 2, 3]
            }
        }


class ContextListDTO(BaseModel):
    """
    Container for multiple context blocks in API responses.
    """
    contexts: List[ContextBlockDTO] = Field(
        default_factory=list,
        description="List of context blocks"
    )
    total_count: int = Field(
        default=0,
        description="Total number of context blocks"
    )
    
    # Summary statistics
    with_images: int = Field(
        default=0,
        description="Number of context blocks with images"
    )
    content_types: dict = Field(
        default_factory=dict,
        description="Count of each content type"
    )
    
    @classmethod
    def from_internal_contexts(cls, internal_contexts: List) -> "ContextListDTO":
        """
        Create ContextListDTO from list of InternalContextBlock.
        
        Args:
            internal_contexts: List of InternalContextBlock instances
            
        Returns:
            ContextListDTO for API response
        """
        # Convert context blocks
        context_dtos = [
            ContextBlockDTO.from_internal_context(ctx)
            for ctx in internal_contexts
        ]
        
        # Calculate statistics
        with_images = sum(1 for ctx in context_dtos if ctx.has_image)
        
        # Count content types
        content_types = {}
        for ctx in context_dtos:
            for content_type in ctx.type:
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return cls(
            contexts=context_dtos,
            total_count=len(context_dtos),
            with_images=with_images,
            content_types=content_types
        )
    
    class Config:
        schema_extra = {
            "example": {
                "contexts": [
                    {
                        "id": 1,
                        "type": ["text"],
                        "content": {
                            "description": ["Context content..."]
                        },
                        "title": "Context Title",
                        "has_image": False,
                        "image_ids": [],
                        "related_question_ids": [1, 2]
                    }
                ],
                "total_count": 1,
                "with_images": 0,
                "content_types": {
                    "text": 1
                }
            }
        }
