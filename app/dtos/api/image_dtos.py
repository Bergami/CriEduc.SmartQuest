"""
API Response DTOs for Images

These DTOs represent simplified image data optimized for API responses.
They contain only the essential information needed by API consumers,
without internal processing metadata.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ImagePositionDTO(BaseModel):
    """Simplified image position for API responses."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate") 
    width: float = Field(..., description="Image width")
    height: float = Field(..., description="Image height")
    
    class Config:
        schema_extra = {
            "example": {
                "x": 344.304,
                "y": 53.662,
                "width": 198.67,
                "height": 154.267
            }
        }


class ImageDTO(BaseModel):
    """
    Simplified image data for API responses.
    
    Contains only essential information for API consumers,
    without internal processing metadata or debugging information.
    """
    # Essential image data
    id: str = Field(..., description="Unique image identifier")
    base64_data: str = Field(..., description="Base64 encoded image content")
    page: int = Field(..., description="Page number (1-indexed)")
    
    # Position information (optional for API consumers)
    position: Optional[ImagePositionDTO] = Field(
        default=None,
        description="Image position on page"
    )
    
    # Basic classification
    category: str = Field(
        default="unknown",
        description="Image category (header, content, figure, etc.)"
    )
    
    # Optional extracted content
    extracted_text: Optional[str] = Field(
        default=None,
        description="Text extracted from image"
    )
    
    # Quality indicator
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score (0-1)"
    )
    
    @classmethod
    def from_internal_image(cls, internal_image) -> "ImageDTO":
        """
        Create ImageDTO from InternalImageData.
        
        Args:
            internal_image: InternalImageData instance
            
        Returns:
            Simplified ImageDTO for API response
        """
        # Convert position if available
        position_dto = None
        if internal_image.position:
            position_dto = ImagePositionDTO(
                x=internal_image.position.x,
                y=internal_image.position.y,
                width=internal_image.position.width,
                height=internal_image.position.height
            )
        
        return cls(
            id=internal_image.id,
            base64_data=internal_image.base64_data,
            page=internal_image.page,
            position=position_dto,
            category=internal_image.category.value,
            extracted_text=internal_image.extracted_text,
            confidence=internal_image.confidence_score
        )
    
    class Config:
        schema_extra = {
            "example": {
                "id": "img_001",
                "base64_data": "iVBORw0KGgoAAAANSUhEUg...",
                "page": 1,
                "position": {
                    "x": 344.304,
                    "y": 53.662,
                    "width": 198.67,
                    "height": 154.267
                },
                "category": "figure",
                "extracted_text": "Gráfico de Vendas 2024",
                "confidence": 0.95
            }
        }


class ImageListDTO(BaseModel):
    """
    Container for multiple images in API responses.
    """
    images: List[ImageDTO] = Field(
        default_factory=list,
        description="List of images"
    )
    total_count: int = Field(
        default=0,
        description="Total number of images"
    )
    page_counts: Optional[dict] = Field(
        default=None,
        description="Number of images per page"
    )
    
    @classmethod
    def from_internal_images(cls, internal_images: List) -> "ImageListDTO":
        """
        Create ImageListDTO from list of InternalImageData.
        
        Args:
            internal_images: List of InternalImageData instances
            
        Returns:
            ImageListDTO for API response
        """
        # Convert images
        image_dtos = [
            ImageDTO.from_internal_image(img) 
            for img in internal_images
        ]
        
        # Calculate page counts
        page_counts = {}
        for img in internal_images:
            page = img.page
            page_counts[page] = page_counts.get(page, 0) + 1
        
        return cls(
            images=image_dtos,
            total_count=len(image_dtos),
            page_counts=page_counts
        )
    
    class Config:
        schema_extra = {
            "example": {
                "images": [
                    {
                        "id": "img_001",
                        "base64_data": "iVBORw0KGgoAAAANSUhEUg...",
                        "page": 1,
                        "category": "header",
                        "confidence": 0.98
                    }
                ],
                "total_count": 1,
                "page_counts": {
                    "1": 1
                }
            }
        }
