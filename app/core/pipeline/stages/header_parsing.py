"""Header parsing stage for document processing pipeline.

This stage handles Phase 3 of the document processing: parsing document
header and extracting metadata.
"""

import logging
from typing import List
from app.core.pipeline.interfaces import IPipelineStage, PipelineResult
from app.models.internal.processing_context import ProcessingContext
from app.models.internal import InternalDocumentMetadata
from app.parsers.header_parser import HeaderParser
from app.core.pipeline.stages.image_analysis import ImageAnalysisOutput


class HeaderParsingInput:
    """Input data for header parsing stage."""
    
    def __init__(self, image_analysis_result: ImageAnalysisOutput):
        self.image_analysis_result = image_analysis_result


class HeaderParsingStage(IPipelineStage[HeaderParsingInput, InternalDocumentMetadata]):
    """Stage 3: Executes header parsing and metadata extraction.
    
    This stage parses the document header text and extracts structured
    metadata using header and content images for enhanced accuracy.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    @property
    def stage_name(self) -> str:
        return "Header Parsing"
    
    @property
    def stage_description(self) -> str:
        return "Parses document header and extracts structured metadata"
    
    async def validate_input(self, input_data: HeaderParsingInput) -> bool:
        """Validate input for header parsing.
        
        Args:
            input_data: Input containing image analysis results
            
        Returns:
            True if input is valid
        """
        if not isinstance(input_data, HeaderParsingInput):
            return False
            
        if not input_data.image_analysis_result:
            return False
            
        return True
    
    async def execute(self,
                     input_data: HeaderParsingInput,
                     context: ProcessingContext) -> PipelineResult[InternalDocumentMetadata]:
        """Execute header parsing stage.
        
        Args:
            input_data: Input containing image analysis results
            context: Processing context with extracted text
            
        Returns:
            PipelineResult containing parsed document metadata
        """
        try:
            self._logger.info("Phase 3: Executing header parsing")
            
            image_result = input_data.image_analysis_result
            
            header_metadata = HeaderParser.parse_to_pydantic(
                header=context.extracted_text,
                header_images=image_result.header_images,
                content_images=image_result.content_images
            )
            
            self._logger.info("Phase 3 complete: Header metadata parsed")
            
            return PipelineResult.success_result(
                data=header_metadata,
                stage_name=self.stage_name
            )
            
        except Exception as e:
            error_msg = f"Header parsing failed: {str(e)}"
            self._logger.error(error_msg, exc_info=True)
            return PipelineResult.error_result(
                error=error_msg,
                stage_name=self.stage_name
            )