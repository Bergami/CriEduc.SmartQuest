"""Context building stage for document processing pipeline.

This stage handles Phase 5 of the document processing: building enhanced
context blocks using the refactored Pydantic approach.
"""

import logging
from typing import List, Optional
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import InternalContextBlock
from app.core.interfaces import IContextBuilder
from app.core.pipeline.stages.image_analysis import ImageAnalysisOutput


class ContextBuildingInput:
    """Input data for context building stage."""
    
    def __init__(self, 
                 image_analysis_result: ImageAnalysisOutput,
                 use_refactored: bool = True):
        self.image_analysis_result = image_analysis_result
        self.use_refactored = use_refactored


class ContextBuildingStage(IPipelineStage[ContextBuildingInput, Optional[List[InternalContextBlock]]]):
    """Stage 5: Executes enhanced context block building.
    
    This stage builds context blocks using the refactored Pydantic approach,
    with fallback to legacy methods if needed.
    """
    
    def __init__(self, context_builder: IContextBuilder):
        self._context_builder = context_builder
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Context Building"
    
    @property
    def stage_description(self) -> str:
        return "Builds enhanced context blocks using refactored Pydantic approach with legacy fallback"
    
    async def validate_input(self, input_data: ContextBuildingInput) -> bool:
        """Validate input for context building.
        
        Args:
            input_data: Input containing image analysis results and configuration
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, ContextBuildingInput):
            return False
            
        if not input_data.image_analysis_result:
            return False
            
        return True
    
    async def execute(self,
                     input_data: ContextBuildingInput,
                     context: ProcessingContext) -> PipelineResult[Optional[List[InternalContextBlock]]]:
        """Execute context building stage.
        
        Args:
            input_data: Input containing image analysis results
            context: Processing context with Azure result
            
        Returns:
            PipelineResult containing enhanced context blocks or None if skipped
        """
        try:
            if not input_data.use_refactored:
                self._logger.info("Phase 5: Skipped - refactored context building disabled")
                return PipelineResult.success_result(
                    data=None,
                    stage_name=self.stage_name
                )
            
            self._logger.info("Phase 5: Executing refactored context building")
            
            azure_result = context.azure_result
            image_data = input_data.image_analysis_result.image_data
            
            if not azure_result:
                self._logger.warning("Phase 5: No Azure result - skipping enhanced context building")
                return PipelineResult.success_result(
                    data=None,
                    stage_name=self.stage_name
                )
            
            try:
                self._logger.info("Phase 5.1: Using parse_to_pydantic() - Native Pydantic Interface")
                
                enhanced_context_blocks = await self._context_builder.parse_to_pydantic(
                    azure_result, image_data, context.document_id
                )
                
                blocks_with_images = sum(1 for cb in enhanced_context_blocks if cb.has_image)
                
                self._logger.info(
                    f"Phase 5: Created {len(enhanced_context_blocks)} context blocks "
                    f"({blocks_with_images} with images)"
                )
                
                return PipelineResult.success_result(
                    data=enhanced_context_blocks,
                    stage_name=self.stage_name
                )
                
            except Exception as e:
                self._logger.warning(f"Phase 5: parse_to_pydantic failed ({e}), using legacy method")
                
                # Fallback to legacy method
                enhanced_context_blocks_dict = await self._context_builder.build_context_blocks_from_azure_figures(
                    azure_result, image_data, context.document_id
                )
                
                if enhanced_context_blocks_dict:
                    context_blocks = [
                        InternalContextBlock.from_legacy_context_block(cb)
                        for cb in enhanced_context_blocks_dict
                    ]
                    self._logger.info(f"Phase 5: Created {len(context_blocks)} context blocks (legacy method)")
                    
                    return PipelineResult.success_result(
                        data=context_blocks,
                        stage_name=self.stage_name
                    )
                else:
                    self._logger.warning("Phase 5: No enhanced context blocks created")
                    return PipelineResult.success_result(
                        data=None,
                        stage_name=self.stage_name
                    )
                    
        except Exception as e:
            error_msg = f"Context building failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )