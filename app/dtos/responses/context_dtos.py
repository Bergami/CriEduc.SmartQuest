"""
API Response DTOs for Context Blocks

These DTOs represent simplified context data optimized for API responses.
They focus on content delivery without internal processing metadata.
"""

from typing import List, Optional, Any, Dict
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


class SubContextDTO(BaseModel):
    """DTO for sub-context data within context blocks."""
    sequence: str = Field(..., description="Sub-context sequence identifier")
    type: str = Field(..., description="Type of sub-context (charge, propaganda, etc.)")
    title: str = Field(..., description="Sub-context title")
    content: str = Field(..., description="Sub-context text content")
    images: List[str] = Field(
        default_factory=list,
        description="Base64 encoded images"
    )

    @classmethod
    def from_dict(cls, sub_context_dict: Dict[str, Any]) -> "SubContextDTO":
        """Create SubContextDTO from dictionary."""
        return cls(
            sequence=sub_context_dict.get("sequence", ""),
            type=sub_context_dict.get("type", ""),
            title=sub_context_dict.get("title", ""),
            content=sub_context_dict.get("content", ""),
            images=sub_context_dict.get("images", [])
        )


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
    
    # Sub-contexts support
    sub_contexts: List[SubContextDTO] = Field(
        default_factory=list,
        description="Sub-contexts within this block"
    )
    
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
        Create ContextBlockDTO from InternalContextBlock OR Dict.
        
        Args:
            internal_context: InternalContextBlock instance OR Dict
            
        Returns:
            Simplified ContextBlockDTO for API response
        """
        # 🔧 DEBUG: Log what we're receiving
        from app.core.logging import structured_logger
        structured_logger.debug(
            f"Creating ContextBlockDTO from: {type(internal_context)}, "
            f"type field: {getattr(internal_context, 'type', internal_context.get('type', 'NO_TYPE') if isinstance(internal_context, dict) else 'NO_TYPE')}"
        )
        
        # Handle both Dict and Pydantic formats
        if isinstance(internal_context, dict):
            # Dict format (current pipeline)
            
            # Extract content properly - handle both old and new structures
            content_data = internal_context.get("content", "")
            if isinstance(content_data, dict):
                # New structure: content = {'description': [texts...]}
                description_texts = content_data.get("description", [])
                if isinstance(description_texts, list):
                    content_description = description_texts
                else:
                    content_description = [str(description_texts)] if description_texts else [""]
            elif isinstance(content_data, list):
                # Direct list of texts
                content_description = content_data
            else:
                # Old structure: content is a single string
                content_description = [str(content_data)] if content_data else [""]
            
            content_dto = ContextContentDTO(
                description=content_description
            )
            
            # Process sub_contexts if present
            sub_contexts_dtos = []
            sub_contexts_data = internal_context.get("sub_contexts", [])
            if sub_contexts_data:
                for sub_context in sub_contexts_data:
                    sub_contexts_dtos.append(SubContextDTO.from_dict(sub_context))
            
            return cls(
                id=internal_context.get("id", 0),
                type=[internal_context.get("type", "text")],
                content=content_dto,
                title=internal_context.get("title", ""),
                statement=internal_context.get("statement", ""),
                sub_contexts=sub_contexts_dtos,
                has_image=internal_context.get("has_images", False),
                image_ids=[],
                related_question_ids=[]
            )
        else:
            # Pydantic format (future pipeline)
            content_dto = ContextContentDTO.from_internal_content(internal_context.content)
            
            # Convert types to strings
            type_strings = [t.value for t in internal_context.type]
            
            # Process sub_contexts (future implementation)
            sub_contexts_dtos = []
            
            return cls(
                id=internal_context.id,
                type=type_strings,
                content=content_dto,
                title=internal_context.title,
                statement=internal_context.statement,
                sub_contexts=sub_contexts_dtos,
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
                "sub_contexts": [
                    {
                        "sequence": "A",
                        "type": "charge",
                        "title": "TEXTO A: charge",
                        "content": "Texto da charge encontrada na sequência A",
                        "images": ["base64_image_data..."]
                    }
                ],
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
