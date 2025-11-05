"""Image analysis stage for document processing pipeline.

This stage handles Phase 2 of the document processing: extracting and 
categorizing images from the document.
"""

import logging
from fastapi import UploadFile
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.core.interfaces import IImageExtractor, IImageCategorizer
from app.utils.processing_constants import get_pipeline_phase_name


class ImageAnalysisInput:
    """Input data for image analysis stage."""
    
    def __init__(self, file: UploadFile, document_id: str):
        self.file = file
        self.document_id = document_id


class ImageAnalysisOutput:
    """Output from image analysis stage."""
    
    def __init__(self, 
                 image_data: list,
                 header_images: list,
                 content_images: list,
                 categorized_images: list):
        self.image_data = image_data
        self.header_images = header_images
        self.content_images = content_images
        self.categorized_images = categorized_images


class ImageAnalysisStage(IPipelineStage[ImageAnalysisInput, ImageAnalysisOutput]):
    """Stage 2: Executes image extraction and categorization.
    
    This stage extracts images from the document using Azure Document Intelligence
    and categorizes them into header and content images.
    """
    
    def __init__(self, 
                 image_extractor: IImageExtractor,
                 image_categorizer: IImageCategorizer):
        self._image_extractor = image_extractor
        self._image_categorizer = image_categorizer
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Image Analysis"
    
    @property
    def stage_description(self) -> str:
        return "Extracts and categorizes images from document using Azure Document Intelligence"
    
    async def validate_input(self, input_data: ImageAnalysisInput) -> bool:
        """Validate input for image analysis.
        
        Args:
            input_data: Input containing file and document ID
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, ImageAnalysisInput):
            return False
            
        if not input_data.file:
            return False
            
        if not input_data.document_id:
            return False
            
        return True
    
    async def execute(self,
                     input_data: ImageAnalysisInput, 
                     context: ProcessingContext) -> PipelineResult[ImageAnalysisOutput]:
        """Execute image analysis stage.
        
        Args:
            input_data: Input containing file and document ID
            context: Processing context with Azure result
            
        Returns:
            PipelineResult containing image analysis output
        """
        try:
            self._logger.info(get_pipeline_phase_name(2))
            
            # 2.1: Image extraction with fallback
            image_data = await self._image_extractor.extract_with_fallback(
                file=input_data.file,
                document_analysis_result=context.azure_result,
                document_id=context.full_document_identifier
            )
            
            if image_data:
                self._logger.info(f"Phase 2.1: {len(image_data)} images extracted successfully")
            else:
                self._logger.warning("Phase 2.1: No images extracted")
                image_data = []
            
            # 2.2: Image categorization
            header_images = []
            content_images = []
            categorized_images = []
            
            if image_data:
                categorization_result = await self._image_categorizer.categorize_images(
                    image_data, context.azure_result
                )
                
                header_images = categorization_result.get("header_images", [])
                content_images = categorization_result.get("content_images", [])
                categorized_images = categorization_result.get("categorized_images", [])
                
                self._logger.info(
                    f"Phase 2.2: Images categorized - Header: {len(header_images)}, "
                    f"Content: {len(content_images)}"
                )
            
            output = ImageAnalysisOutput(
                image_data=image_data,
                header_images=header_images,
                content_images=content_images,
                categorized_images=categorized_images
            )
            
            self._logger.info("Phase 2 complete: Image analysis finished")
            
            return PipelineResult.success_result(
                data=output,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Image analysis failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )