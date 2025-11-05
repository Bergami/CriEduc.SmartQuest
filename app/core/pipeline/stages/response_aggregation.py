"""Response aggregation stage for document processing pipeline.

This stage handles Phase 7 of the document processing: aggregating all
pipeline results into the final document response.
"""

import logging
from typing import List, Optional
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import (
    InternalDocumentResponse,
    InternalDocumentMetadata,
    InternalQuestion,
    InternalContextBlock,
    InternalImageData
)
from app.core.pipeline.stages.image_analysis import ImageAnalysisOutput


class ResponseAggregationInput:
    """Input data for response aggregation stage."""
    
    def __init__(self,
                 image_analysis_result: ImageAnalysisOutput,
                 header_metadata: InternalDocumentMetadata,
                 questions: List[InternalQuestion],
                 context_blocks: Optional[List[InternalContextBlock]] = None):
        self.image_analysis_result = image_analysis_result
        self.header_metadata = header_metadata
        self.questions = questions
        self.context_blocks = context_blocks or []


class ResponseAggregationStage(IPipelineStage[ResponseAggregationInput, InternalDocumentResponse]):
    """Stage 7: Aggregates all pipeline results into final response.
    
    This stage combines all the processed data from previous stages into
    the final InternalDocumentResponse that will be returned to the client.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Response Aggregation"
    
    @property
    def stage_description(self) -> str:
        return "Aggregates all pipeline results into final document response"
    
    async def validate_input(self, input_data: ResponseAggregationInput) -> bool:
        """Validate input for response aggregation.
        
        Args:
            input_data: Input containing all pipeline results
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, ResponseAggregationInput):
            return False
            
        if not input_data.image_analysis_result:
            return False
            
        if not input_data.header_metadata:
            return False
            
        if not isinstance(input_data.questions, list):
            return False
            
        return True
    
    async def execute(self,
                     input_data: ResponseAggregationInput,
                     context: ProcessingContext) -> PipelineResult[InternalDocumentResponse]:
        """Execute response aggregation stage.
        
        Args:
            input_data: Input containing all pipeline results
            context: Processing context with document metadata
            
        Returns:
            PipelineResult containing the final document response
        """
        try:
            self._logger.info("Phase 7: Aggregating final response")
            
            # Convert image data to internal format
            internal_images = []
            if input_data.image_analysis_result.image_data:
                for img_data in input_data.image_analysis_result.image_data:
                    try:
                        internal_image = InternalImageData(
                            image_id=img_data.get("image_id", ""),
                            base64_content=img_data.get("base64_content", ""),
                            content_type=img_data.get("content_type", ""),
                            width=img_data.get("width", 0),
                            height=img_data.get("height", 0),
                            page_number=img_data.get("page_number", 1),
                            category=img_data.get("category", "unknown")
                        )
                        internal_images.append(internal_image)
                    except Exception as e:
                        self._logger.warning(f"Failed to convert image data: {e}")
            
            # Build the final response
            response = InternalDocumentResponse(
                email=context.email,
                document_id=context.document_id,
                metadata=input_data.header_metadata,
                questions=input_data.questions,
                context_blocks=input_data.context_blocks,
                images=internal_images
            )
            
            self._logger.info(
                f"Phase 7 complete: Response aggregated with {len(input_data.questions)} questions, "
                f"{len(input_data.context_blocks)} context blocks, and {len(internal_images)} images"
            )
            
            return PipelineResult.success_result(
                data=response,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Response aggregation failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )