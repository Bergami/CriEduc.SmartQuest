"""
Refactored Document Analysis Orchestrator using Pipeline Architecture

This is the new implementation that uses the stage-based pipeline
to replace the monolithic approach, following Issue #10 recommendations.
"""
import logging
from typing import Dict, Any
from uuid import uuid4
from fastapi import UploadFile

from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.core.interfaces import (
    IImageCategorizer,
    IImageExtractor,
    IContextBuilder,
    IFigureProcessor
)
from app.models.internal import InternalDocumentResponse
from app.core.exceptions import DocumentProcessingError
from app.core.pipeline import PipelineConfiguration
from app.core.pipeline.document_processing_pipeline import (
    DocumentProcessingPipeline,
    DocumentProcessingPipelineInput
)

logger = logging.getLogger(__name__)


class DocumentAnalysisOrchestrator:
    """
    Refactored document analysis orchestrator using pipeline architecture.
    
    This new implementation replaces the 400+ line monolithic orchestrator
    with a clean, stage-based pipeline approach that improves:
    
    - Testability: Each stage can be tested in isolation
    - Maintainability: Clear separation of concerns
    - Extensibility: Easy to add/remove/modify stages
    - Error handling: Circuit breaker pattern with error boundaries
    - Monitoring: Individual stage performance tracking
    
    The orchestrator now serves as a facade that coordinates the pipeline
    execution while delegating actual processing to specialized stages.
    """

    def __init__(self,
                 image_extractor: IImageExtractor,
                 image_categorizer: IImageCategorizer,
                 context_builder: IContextBuilder,
                 figure_processor: IFigureProcessor):
        """Initialize orchestrator with injected dependencies.
        
        Args:
            image_extractor: Service for extracting images from documents
            image_categorizer: Service for categorizing extracted images  
            context_builder: Service for building context blocks
            figure_processor: Service for processing figures and associations
        """
        self._logger = logger
        
        # Configure pipeline with circuit breaker enabled
        pipeline_config = PipelineConfiguration(
            enable_circuit_breaker=True,
            max_stage_failures=3,
            enable_parallel_execution=False,
            timeout_seconds=300.0,
            retry_failed_stages=False,
            max_retries=1
        )
        
        # Initialize the document processing pipeline
        self._pipeline = DocumentProcessingPipeline(
            image_extractor=image_extractor,
            image_categorizer=image_categorizer,
            context_builder=context_builder,
            figure_processor=figure_processor,
            config=pipeline_config
        )
        
        self._logger.info("DocumentAnalysisOrchestrator initialized with pipeline architecture")

    async def analyze_document(self,
                             file: UploadFile,
                             extracted_data: Dict[str, Any],
                             email: str,
                             filename: str,
                             use_refactored: bool = True) -> InternalDocumentResponse:
        """
        Analyzes a document using the 7-stage pipeline architecture.
        
        This method replaces the previous monolithic implementation with
        a clean pipeline-based approach that processes documents through
        specialized stages.
        
        Args:
            file: The uploaded file to analyze
            extracted_data: Raw extracted data from document processing
            email: User email for document identification
            filename: Original filename of the document
            use_refactored: Whether to use refactored context building (default: True)
            
        Returns:
            InternalDocumentResponse: Complete analysis results
            
        Raises:
            DocumentProcessingError: If pipeline execution fails
        """
        document_id = str(uuid4())
        
        try:
            self._logger.info(f"Starting document analysis for {filename} (ID: {document_id})")
            
            # Create pipeline input
            pipeline_input = DocumentProcessingPipelineInput(
                file=file,
                extracted_data=extracted_data,
                email=email,
                filename=filename,
                document_id=document_id,
                use_refactored_context_building=use_refactored
            )
            
            # Execute the pipeline
            pipeline_result = await self._pipeline.execute(pipeline_input, None)
            
            if not pipeline_result.success:
                raise DocumentProcessingError(
                    f"Pipeline execution failed: {pipeline_result.error}"
                )
            
            document_response = pipeline_result.data
            
            self._logger.info(f"Document analysis completed successfully for {filename}")
            return document_response
            
        except Exception as e:
            self._logger.error(f"Document analysis failed for {filename}: {str(e)}", exc_info=True)
            raise DocumentProcessingError(f"Analysis pipeline failed: {str(e)}") from e