"""Figure association stage for document processing pipeline.

This stage handles Phase 6 of the document processing: associating figures
with questions to enhance question context.
"""

import logging
from typing import List
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import InternalQuestion
from app.core.interfaces import IFigureProcessor
from app.core.pipeline.stages.image_analysis import ImageAnalysisOutput


class FigureAssociationInput:
    """Input data for figure association stage."""
    
    def __init__(self, 
                 questions: List[InternalQuestion],
                 image_analysis_result: ImageAnalysisOutput):
        self.questions = questions
        self.image_analysis_result = image_analysis_result


class FigureAssociationStage(IPipelineStage[FigureAssociationInput, List[InternalQuestion]]):
    """Stage 6: Executes figure association with questions.
    
    This stage processes figures and associates them with relevant questions
    to provide enhanced context for question answering.
    """
    
    def __init__(self, figure_processor: IFigureProcessor):
        self._figure_processor = figure_processor
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Figure Association"
    
    @property
    def stage_description(self) -> str:
        return "Associates figures with questions to enhance question context"
    
    async def validate_input(self, input_data: FigureAssociationInput) -> bool:
        """Validate input for figure association.
        
        Args:
            input_data: Input containing questions and image analysis results
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, FigureAssociationInput):
            return False
            
        if not isinstance(input_data.questions, list):
            return False
            
        if not input_data.image_analysis_result:
            return False
            
        return True
    
    async def execute(self,
                     input_data: FigureAssociationInput,
                     context: ProcessingContext) -> PipelineResult[List[InternalQuestion]]:
        """Execute figure association stage.
        
        Args:
            input_data: Input containing questions and image analysis results
            context: Processing context (used for legacy compatibility)
            
        Returns:
            PipelineResult containing questions enhanced with figure associations
        """
        try:
            self._logger.info("Phase 6: Executing figure association")
            
            # TODO: This stage needs to be refactored to use the new pipeline data flow
            # For now, we'll use legacy compatibility mode
            context_dict = context.to_dict()
            
            # Add image analysis data to legacy context for compatibility
            legacy_context["categorized_images"] = input_data.image_analysis_result.categorized_images
            legacy_context["context_blocks"] = []  # This would come from previous stages
            
            images = legacy_context.get("categorized_images", [])
            context_blocks = legacy_context.get("context_blocks", [])
            
            # Process figures through the interface
            figure_results = await self._figure_processor.process_figures(images, context_blocks)
            
            # Extract enhanced questions from results
            enhanced_questions = figure_results.get("enhanced_questions", input_data.questions)
            
            self._logger.info("Phase 6: Questions enhanced with figure associations")
            
            return PipelineResult.success_result(
                data=enhanced_questions,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Figure association failed: {str(e)}"
            self._logger.warning(f"{error_msg}, proceeding without enhancement")
            
            # Return original questions if figure association fails
            return PipelineResult.success_result(
                data=input_data.questions,
                stage_name=self.stage_name
            )