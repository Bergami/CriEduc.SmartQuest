"""Context preparation stage for document processing pipeline.

This stage handles Phase 1 of the document processing: preparing the basic
analysis context from extracted document data.
"""

import logging
from typing import Dict, Any
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext, ProcessingContextBuilder
from app.utils.processing_constants import get_pipeline_phase_name


class ContextPreparationInput:
    """Input data for context preparation stage."""
    
    def __init__(self, 
                 extracted_data: Dict[str, Any],
                 email: str,
                 filename: str,
                 document_id: str):
        self.extracted_data = extracted_data
        self.email = email
        self.filename = filename
        self.document_id = document_id


class ContextPreparationStage(IPipelineStage[ContextPreparationInput, ProcessingContext]):
    """Stage 1: Prepares the basic analysis context.
    
    This stage takes raw extracted document data and creates an immutable
    ProcessingContext that will be passed through the rest of the pipeline.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Context Preparation"
    
    @property 
    def stage_description(self) -> str:
        return "Prepares immutable processing context from extracted document data"
    
    async def validate_input(self, input_data: ContextPreparationInput) -> bool:
        """Validate input for context preparation.
        
        Args:
            input_data: Input containing extracted data and metadata
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, ContextPreparationInput):
            return False
            
        if not input_data.extracted_data:
            return False
            
        if not input_data.email or not input_data.filename or not input_data.document_id:
            return False
            
        return True
    
    async def execute(self, 
                     input_data: ContextPreparationInput,
                     context: ProcessingContext) -> PipelineResult[ProcessingContext]:
        """Execute context preparation stage.
        
        Args:
            input_data: Input containing extraction data and metadata
            context: Not used in this stage (this creates the initial context)
            
        Returns:
            PipelineResult containing the prepared ProcessingContext
        """
        try:
            self._logger.info(get_pipeline_phase_name(1))
            
            # Build immutable context using builder pattern
            new_context = ProcessingContextBuilder.from_extraction_data(
                extracted_data=input_data.extracted_data,
                email=input_data.email,
                filename=input_data.filename,
                document_id=input_data.document_id
            ).build()
            
            self._logger.info(
                f"{get_pipeline_phase_name(1)} complete: Context prepared with Azure result: {new_context.has_azure_result}"
            )
            
            return PipelineResult.success_result(
                data=new_context,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Failed to prepare analysis context: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )