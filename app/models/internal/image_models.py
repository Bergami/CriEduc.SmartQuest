"""
Internal Image Data Models

These models represent the complete image data structure used internally
for processing, including all Azure metadata, coordinates, and extraction details.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ImageCategory(str, Enum):
    """Categories for image classification."""
    HEADER = "header"
    FOOTER = "footer"
    CONTENT = "content"
    SIDEBAR = "sidebar"
    LOGO = "logo"
    WATERMARK = "watermark"
    FIGURE = "figure"
    CHART = "chart"
    DIAGRAM = "diagram"
    PHOTO = "photo"
    UNKNOWN = "unknown"


class ImageProcessingStatus(str, Enum):
    """Status of image processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ImagePosition(BaseModel):
    """
    Calculated position of an image after coordinate transformation.
    
    All coordinates are in the target coordinate system (usually pixels)
    after applying scaling factors and transformations.
    """
    x: float = Field(..., description="X coordinate (top-left corner)")
    y: float = Field(..., description="Y coordinate (top-left corner)")
    width: float = Field(..., description="Width of the image")
    height: float = Field(..., description="Height of the image")
    
    class Config:
        schema_extra = {
            "example": {
                "x": 344.304,
                "y": 53.662,
                "width": 198.67,
                "height": 154.267
            }
        }


class PageDimensions(BaseModel):
    """Dimensions of a PDF page in the target coordinate system."""
    width: float = Field(..., description="Page width")
    height: float = Field(..., description="Page height")
    
    class Config:
        schema_extra = {
            "example": {
                "width": 595.276,
                "height": 841.890
            }
        }


class ExtractionMetadata(BaseModel):
    """
    Metadata about the image extraction process.
    
    Contains information about how the image was processed,
    including scaling factors, source coordinates, and extraction settings.
    """
    scale_factor: float = Field(default=72.0, description="Scale factor applied to coordinates")
    source: str = Field(default="azure", description="Source of the image data")
    bounding_regions: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Original Azure bounding regions data"
    )
    extraction_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the image was extracted"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of the extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Any special notes about the processing"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "scale_factor": 72.0,
                "source": "azure",
                "bounding_regions": [
                    {
                        "pageNumber": 1,
                        "polygon": [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
                    }
                ],
                "confidence": 0.95,
                "processing_notes": "Standard extraction with 72pt scaling"
            }
        }


class InternalImageData(BaseModel):
    """
    Complete internal representation of an image with all metadata.
    
    This model contains all information needed for internal processing,
    debugging, categorization, and analysis. It preserves the original
    Azure coordinates alongside calculated positions.
    """
    # Core image data
    id: str = Field(..., description="Unique image identifier")
    file_path: str = Field(..., description="Path to the image file")
    base64_data: str = Field(..., description="Base64 encoded image content")
    
    # Position and page information
    page: int = Field(default=1, description="Page number (1-indexed)")
    position: Optional[ImagePosition] = Field(
        default=None,
        description="Calculated position after coordinate transformation"
    )
    
    # Azure-specific metadata
    azure_coordinates: Optional[List[float]] = Field(
        default=None,
        description="Original coordinates from Azure [x1,y1,x2,y2,x3,y3,x4,y4]"
    )
    extraction_metadata: Optional[ExtractionMetadata] = Field(
        default=None,
        description="Metadata about the extraction process"
    )
    
    # Classification and processing
    category: ImageCategory = Field(
        default=ImageCategory.UNKNOWN,
        description="Image category classification"
    )
    processing_status: ImageProcessingStatus = Field(
        default=ImageProcessingStatus.PENDING,
        description="Current processing status"
    )
    
    # Content analysis
    extracted_text: Optional[str] = Field(
        default=None,
        description="Text extracted from the image via OCR"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Overall confidence score of the extraction"
    )
    
    # Debug and processing information
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about processing this image"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this image data was created"
    )
    
    @classmethod
    def from_azure_figure(
        cls, 
        figure: Dict[str, Any], 
        source_path: str,
        page_dimensions: Optional[PageDimensions] = None
    ) -> "InternalImageData":
        """
        Create InternalImageData from Azure Document Intelligence figure data.
        
        Args:
            figure: Azure figure dictionary
            source_path: Path to the source document
            page_dimensions: Optional page dimensions for coordinate transformation
            
        Returns:
            InternalImageData instance with complete metadata
        """
        import base64
        
        # Generate unique ID
        figure_id = figure.get("id", f"azure_figure_{hash(str(figure))}")
        
        # Extract bounding region data
        bounding_regions = figure.get("boundingRegions", [])
        coordinates = []
        page_number = 1
        
        if bounding_regions:
            region = bounding_regions[0]
            coordinates = region.get("polygon", [])
            page_number = region.get("pageNumber", 1)
        
        # Calculate position if coordinates are available
        position = None
        if len(coordinates) == 8:
            scale_factor = 72.0  # Azure uses 72 points per inch
            x_values = [coordinates[i] * scale_factor for i in range(0, len(coordinates), 2)]
            y_values = [coordinates[i+1] * scale_factor for i in range(0, len(coordinates), 2)]
            
            position = ImagePosition(
                x=max(0, min(x_values)),
                y=max(0, min(y_values)), 
                width=max(x_values) - min(x_values),
                height=max(y_values) - min(y_values)
            )
        
        # Create extraction metadata
        extraction_metadata = ExtractionMetadata(
            scale_factor=72.0,
            source="azure_document_intelligence",
            bounding_regions=bounding_regions,
            confidence=figure.get("confidence"),
            processing_notes="Created from Azure Document Intelligence figure"
        )
        
        # Extract content or use placeholder
        content = figure.get("content", "")
        base64_content = base64.b64encode(content.encode() if isinstance(content, str) else b"").decode()
        
        return cls(
            id=figure_id,
            file_path=f"{source_path}#figure_{figure_id}",
            base64_data=base64_content,
            page=page_number,
            position=position,
            azure_coordinates=coordinates,
            extraction_metadata=extraction_metadata,
            category=ImageCategory.FIGURE,
            processing_status=ImageProcessingStatus.COMPLETED,
            processing_notes="Extracted from Azure Document Intelligence"
        )
    
    def is_header_image(self, threshold: float = 0.15) -> bool:
        """
        Determine if this image is likely a header image based on position.
        
        Args:
            threshold: Y-position threshold (0-1) for header classification
            
        Returns:
            True if likely a header image, False otherwise
        """
        if not self.position:
            return False
            
        # Normalize y-position (assume standard page height of ~841 points)
        normalized_y = self.position.y / 841.0
        return normalized_y <= threshold
    
    def categorize_image(self, page_height: float = 841.0) -> ImageCategory:
        """
        Automatically categorize the image based on position and content.
        
        Args:
            page_height: Height of the page for position calculation
            
        Returns:
            Appropriate ImageCategory
        """
        if not self.position:
            return ImageCategory.UNKNOWN
            
        # Calculate relative position
        rel_y = self.position.y / page_height
        
        # Header classification
        if rel_y <= 0.15:
            return ImageCategory.HEADER
        
        # Footer classification  
        if rel_y >= 0.85:
            return ImageCategory.FOOTER
        
        # Content classification based on size and position
        if self.position.width > 200 and self.position.height > 150:
            return ImageCategory.FIGURE
        
        return ImageCategory.CONTENT
    
    class Config:
        schema_extra = {
            "example": {
                "id": "azure_figure_123",
                "file_path": "/path/to/document.pdf#figure_123",
                "base64_data": "iVBORw0KGgoAAAANSUhEUg...",
                "page": 1,
                "position": {
                    "x": 344.304,
                    "y": 53.662,
                    "width": 198.67,
                    "height": 154.267
                },
                "azure_coordinates": [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874],
                "category": "figure",
                "processing_status": "completed",
                "confidence_score": 0.95
            }
        }
