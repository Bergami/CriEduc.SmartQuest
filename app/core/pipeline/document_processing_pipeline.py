"""Document processing pipeline implementation.

This module provides the main pipeline that orchestrates all stages
to process documents using the new stage-based architecture.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import UploadFile

from app.core.pipeline.interfaces import IPipeline, PipelineResult, PipelineStageWrapper, PipelineConfiguration
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import InternalDocumentResponse
from app.core.interfaces import IImageExtractor, IImageCategorizer, IContextBuilder, IFigureProcessor

from app.core.pipeline.stages import (
    ContextPreparationStage,
    ContextPreparationInput,
    ImageAnalysisStage,
    ImageAnalysisInput,
    HeaderParsingStage,
    HeaderParsingInput,
    QuestionExtractionStage,
    QuestionExtractionInput,
    ContextBuildingStage,
    ContextBuildingInput,
    FigureAssociationStage,
    FigureAssociationInput,
    ResponseAggregationStage,
    ResponseAggregationInput
)


class DocumentProcessingPipelineInput:
    """Input for the complete document processing pipeline."""
    
    def __init__(self,
                 file: UploadFile,
                 extracted_data: Dict[str, Any],
                 email: str,
                 filename: str,
                 document_id: str,
                 use_refactored_context_building: bool = True):
        self.file = file
        self.extracted_data = extracted_data
        self.email = email
        self.filename = filename
        self.document_id = document_id
        self.use_refactored_context_building = use_refactored_context_building


class DocumentProcessingPipeline(IPipeline):
    """Main document processing pipeline using stage-based architecture.
    
    This pipeline replaces the monolithic DocumentAnalysisOrchestrator
    with a composable, testable, and maintainable stage-based approach.
    """
    
    def __init__(self,
                 image_extractor: IImageExtractor,
                 image_categorizer: IImageCategorizer,
                 context_builder: IContextBuilder,
                 figure_processor: IFigureProcessor,
                 config: Optional[PipelineConfiguration] = None):
        """Initialize the pipeline with required dependencies.
        
        Args:
            image_extractor: Service for extracting images from documents
            image_categorizer: Service for categorizing extracted images
            context_builder: Service for building context blocks
            figure_processor: Service for processing figures
            config: Pipeline configuration (uses defaults if None)
        """
        self._config = config or PipelineConfiguration()
        self._logger = logging.getLogger(__name__)
        
        # Initialize stages with descriptive names for better code readability
        self._context_preparation_stage = ContextPreparationStage()
        self._image_analysis_stage = ImageAnalysisStage(image_extractor, image_categorizer)
        self._header_parsing_stage = HeaderParsingStage()
        self._question_extraction_stage = QuestionExtractionStage()
        self._context_building_stage = ContextBuildingStage(context_builder)
        self._figure_association_stage = FigureAssociationStage(figure_processor)
        self._response_aggregation_stage = ResponseAggregationStage()
        
        # Wrap stages with error boundaries if enabled
        if self._config.enable_circuit_breaker:
            self._wrapped_stages = [
                PipelineStageWrapper(stage, self._config.max_stage_failures)
                for stage in [
                    self._context_preparation_stage,
                    self._image_analysis_stage,
                    self._header_parsing_stage,
                    self._question_extraction_stage,
                    self._context_building_stage,
                    self._figure_association_stage,
                    self._response_aggregation_stage
                ]
            ]
        else:
            self._wrapped_stages = None
    
    @property
    def pipeline_name(self) -> str:
        return "Document Processing Pipeline"
    
    def get_stage_count(self) -> int:
        return 7
    
    async def execute(self,
                     initial_input: DocumentProcessingPipelineInput,
                     context: Optional[ProcessingContext] = None) -> PipelineResult[InternalDocumentResponse]:
        """Execute the complete document processing pipeline.
        
        Args:
            initial_input: Initial pipeline input with file and metadata
            context: Not used (pipeline creates its own context)
            
        Returns:
            PipelineResult containing the final document response
        """
        try:
            self._logger.info(f"Starting {self.pipeline_name} with {self.get_stage_count()} stages")
            
            # Stage 1: Context Preparation
            stage_1_input = ContextPreparationInput(
                extracted_data=initial_input.extracted_data,
                email=initial_input.email,
                filename=initial_input.filename,
                document_id=initial_input.document_id
            )
            
            stage_1_result = await self._execute_stage(0, stage_1_input, None)
            if not stage_1_result.success:
                return stage_1_result
            
            processing_context = stage_1_result.data
            
            # Stage 2: Image Analysis
            stage_2_input = ImageAnalysisInput(
                file=initial_input.file,
                document_id=initial_input.document_id
            )
            
            stage_2_result = await self._execute_stage(1, stage_2_input, processing_context)
            if not stage_2_result.success:
                return stage_2_result
            
            image_analysis_result = stage_2_result.data
            
            # Stage 3: Header Parsing
            stage_3_input = HeaderParsingInput(image_analysis_result)
            
            stage_3_result = await self._execute_stage(2, stage_3_input, processing_context)
            if not stage_3_result.success:
                return stage_3_result
            
            header_metadata = stage_3_result.data
            
            # Stage 4: Question Extraction
            stage_4_input = QuestionExtractionInput(image_analysis_result)
            
            stage_4_result = await self._execute_stage(3, stage_4_input, processing_context)
            if not stage_4_result.success:
                return stage_4_result
            
            question_extraction_result = stage_4_result.data
            
            # Stage 5: Context Building (optional)
            stage_5_input = ContextBuildingInput(
                image_analysis_result,
                initial_input.use_refactored_context_building
            )
            
            stage_5_result = await self._execute_stage(4, stage_5_input, processing_context)
            if not stage_5_result.success:
                return stage_5_result
            
            enhanced_context_blocks = stage_5_result.data or []
            
            # Stage 6: Figure Association
            stage_6_input = FigureAssociationInput(
                questions=question_extraction_result.questions,
                image_analysis_result=image_analysis_result
            )
            
            stage_6_result = await self._execute_stage(5, stage_6_input, processing_context)
            if not stage_6_result.success:
                return stage_6_result
            
            enhanced_questions = stage_6_result.data
            
            # Stage 7: Response Aggregation
            stage_7_input = ResponseAggregationInput(
                image_analysis_result=image_analysis_result,
                header_metadata=header_metadata,
                questions=enhanced_questions,
                context_blocks=enhanced_context_blocks
            )
            
            stage_7_result = await self._execute_stage(6, stage_7_input, processing_context)
            if not stage_7_result.success:
                return stage_7_result
            
            final_response = stage_7_result.data
            
            self._logger.info(f"{self.pipeline_name} completed successfully")
            
            return PipelineResult.success_result(
                data=final_response,
                stage_name=self.pipeline_name
            )
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.pipeline_name
            )
    
    async def _execute_stage(self, stage_index: int, input_data: Any, context: ProcessingContext) -> PipelineResult:
        """Execute a specific stage with error handling.
        
        Args:
            stage_index: Index of the stage to execute (0-6)
            input_data: Input data for the stage
            context: Processing context
            
        Returns:
            PipelineResult from stage execution
        """
        # Map stage index to descriptive stage instances
        stages = [
            self._context_preparation_stage,
            self._image_analysis_stage,
            self._header_parsing_stage,
            self._question_extraction_stage,
            self._context_building_stage,
            self._figure_association_stage,
            self._response_aggregation_stage
        ]
        
        stage = stages[stage_index]
        
        if self._wrapped_stages:
            # Use wrapped stage with error boundaries
            wrapped_stage = self._wrapped_stages[stage_index]
            return await wrapped_stage.execute_with_error_boundary(input_data, context)
        else:
            # Execute stage directly
            return await stage.execute(input_data, context)