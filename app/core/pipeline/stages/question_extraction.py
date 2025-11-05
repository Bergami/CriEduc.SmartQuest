"""Question extraction stage for document processing pipeline.

This stage handles Phase 4 of the document processing: extracting questions
from Azure Document Intelligence paragraphs.
"""

import logging
from typing import List
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import InternalQuestion, InternalContextBlock
from app.parsers.question_parser import QuestionParser
from app.core.pipeline.stages.image_analysis import ImageAnalysisOutput


class QuestionExtractionInput:
    """Input data for question extraction stage."""
    
    def __init__(self, image_analysis_result: ImageAnalysisOutput):
        self.image_analysis_result = image_analysis_result


class QuestionExtractionOutput:
    """Output from question extraction stage."""
    
    def __init__(self, 
                 questions: List[InternalQuestion],
                 context_blocks: List[InternalContextBlock]):
        self.questions = questions
        self.context_blocks = context_blocks


class QuestionExtractionStage(IPipelineStage[QuestionExtractionInput, QuestionExtractionOutput]):
    """Stage 4: Executes question extraction from Azure paragraphs.
    
    This stage processes Azure Document Intelligence paragraphs to extract
    questions and their associated context blocks.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Question Extraction"
    
    @property
    def stage_description(self) -> str:
        return "Extracts questions and context blocks from Azure Document Intelligence paragraphs"
    
    async def validate_input(self, input_data: QuestionExtractionInput) -> bool:
        """Validate input for question extraction.
        
        Args:
            input_data: Input containing image analysis results
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, QuestionExtractionInput):
            return False
            
        if not input_data.image_analysis_result:
            return False
            
        return True
    
    async def execute(self,
                     input_data: QuestionExtractionInput,
                     context: ProcessingContext) -> PipelineResult[QuestionExtractionOutput]:
        """Execute question extraction stage.
        
        Args:
            input_data: Input containing image analysis results
            context: Processing context with Azure result
            
        Returns:
            PipelineResult containing extracted questions and context blocks
        """
        try:
            self._logger.info("Phase 4: Executing question extraction")
            
            azure_result = context.azure_result
            image_data = input_data.image_analysis_result.image_data
            
            # Extract Azure paragraphs
            azure_paragraphs = azure_result.get("paragraphs", []) if azure_result else []
            
            questions = []
            context_blocks = []
            
            if azure_paragraphs:
                self._logger.info(f"Phase 4.1: Processing {len(azure_paragraphs)} Azure paragraphs")
                
                # Prepare paragraphs in expected format
                paragraph_list = [
                    {"content": p.get("content", "")} 
                    for p in azure_paragraphs 
                    if p.get("content")
                ]
                
                # Extract using efficient method
                if paragraph_list:
                    extracted_data = QuestionParser.extract_questions_from_paragraphs(
                        paragraph_list, image_data
                    )
                    
                    questions = extracted_data.get("questions", [])
                    context_blocks = extracted_data.get("context_blocks", [])
                    
                    self._logger.info(f"Phase 4.2: Extracted {len(questions)} questions")
                    self._logger.info(f"Phase 4.3: Generated {len(context_blocks)} context blocks")
                else:
                    self._logger.warning("Phase 4.1: No valid paragraphs found")
            else:
                self._logger.warning("Phase 4: No Azure paragraphs available")
            
            output = QuestionExtractionOutput(
                questions=questions,
                context_blocks=context_blocks
            )
            
            self._logger.info("Phase 4 complete: Question extraction finished")
            
            return PipelineResult.success_result(
                data=output,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Question extraction failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )