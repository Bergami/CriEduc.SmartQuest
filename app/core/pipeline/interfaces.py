"""Pipeline interfaces and base classes for document processing stages.

This module defines the core interfaces for implementing a stage-based
document processing pipeline, replacing the monolithic orchestrator approach.
"""

from abc import ABC, abstractmethod  # ABC = Abstract Base Class - Python mechanism for defining interfaces
from typing import Any, Dict, Generic, TypeVar, Optional
from dataclasses import dataclass
from app.models.internal.processing_context import ProcessingContext

# Type variables for pipeline stage input/output
TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')


@dataclass
class PipelineResult(Generic[TOutput]):
    """Result wrapper for pipeline stage execution.
    
    Provides structured result with success status, data, and error handling.
    
    Attributes:
        success: Whether the stage executed successfully
        data: The actual result data (None if failed)
        error: Error information if stage failed
        stage_name: Name of the stage that produced this result
        execution_time_ms: Time taken to execute in milliseconds
    """
    success: bool
    data: Optional[TOutput]
    error: Optional[str] = None
    stage_name: str = "unknown"
    execution_time_ms: float = 0.0
    
    @classmethod
    def success_result(cls, data: TOutput, stage_name: str, execution_time_ms: float = 0.0) -> 'PipelineResult[TOutput]':
        """Create a successful result."""
        return cls(
            success=True,
            data=data,
            stage_name=stage_name,
            execution_time_ms=execution_time_ms
        )
    
    @classmethod
    def error_result(cls, error: str, stage_name: str, execution_time_ms: float = 0.0) -> 'PipelineResult[TOutput]':
        """Create an error result."""
        return cls(
            success=False,
            data=None,
            error=error,
            stage_name=stage_name,
            execution_time_ms=execution_time_ms
        )


class IPipelineStage(ABC, Generic[TInput, TOutput]):
    """Interface for pipeline stages in document processing.
    
    Each stage represents a single, focused responsibility in the document
    analysis pipeline. Stages are composable and can be tested in isolation.
    
    Note: ABC (Abstract Base Class) is Python's mechanism for defining interfaces.
    It ensures that any class inheriting from this interface must implement
    all abstract methods, providing compile-time validation of the interface contract.
    """
    
    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Human-readable name for this stage."""
        pass
    
    @property
    @abstractmethod
    def stage_description(self) -> str:
        """Description of what this stage does."""
        pass
    
    @abstractmethod
    async def execute(self, 
                     input_data: TInput, 
                     context: ProcessingContext) -> PipelineResult[TOutput]:
        """Execute this pipeline stage.
        
        Args:
            input_data: Input data for this stage
            context: Immutable processing context
            
        Returns:
            PipelineResult containing the output or error information
        """
        pass
    
    @abstractmethod
    async def validate_input(self, input_data: TInput) -> bool:
        """Validate that input data is suitable for this stage.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        pass


class IPipeline(ABC):
    """Interface for document processing pipelines.
    
    A pipeline is a composition of stages that processes documents
    through a series of transformations.
    
    Note: ABC (Abstract Base Class) enforces implementation of all abstract methods
    in derived classes, ensuring consistent pipeline behavior across implementations.
    """
    
    @property
    @abstractmethod
    def pipeline_name(self) -> str:
        """Name of this pipeline."""
        pass
    
    @abstractmethod
    async def execute(self, 
                     initial_input: Any, 
                     context: ProcessingContext) -> PipelineResult[Any]:
        """Execute the entire pipeline.
        
        Args:
            initial_input: Initial input to the pipeline
            context: Processing context
            
        Returns:
            Final result of pipeline execution
        """
        pass
    
    @abstractmethod
    def get_stage_count(self) -> int:
        """Get the number of stages in this pipeline."""
        pass


class PipelineStageWrapper:
    """Wrapper that adds common functionality to pipeline stages.
    
    Provides error boundaries, timing, logging, and circuit breaker patterns
    around stage execution as suggested in Issue #10.
    """
    
    def __init__(self, stage: IPipelineStage, max_failures: int = 3):
        """Initialize wrapper with stage and failure threshold.
        
        Args:
            stage: The pipeline stage to wrap
            max_failures: Maximum consecutive failures before circuit opens
        """
        self.stage = stage
        self.max_failures = max_failures
        self.failure_count = 0
        self.circuit_open = False
        
    async def execute_with_error_boundary(self, 
                                        input_data: Any, 
                                        context: ProcessingContext) -> PipelineResult[Any]:
        """Execute stage with error boundary and circuit breaker.
        
        Args:
            input_data: Input for the wrapped stage
            context: Processing context
            
        Returns:
            PipelineResult with error handling applied
        """
        import time
        import logging
        
        logger = logging.getLogger(f"pipeline.{self.stage.stage_name}")
        
        # Circuit breaker check
        if self.circuit_open:
            error_msg = f"Circuit breaker open for stage {self.stage.stage_name}"
            logger.error(error_msg)
            return PipelineResult.error_result(error_msg, self.stage.stage_name)
        
        start_time = time.time()
        
        try:
            # Input validation
            if not await self.stage.validate_input(input_data):
                error_msg = f"Input validation failed for stage {self.stage.stage_name}"
                logger.warning(error_msg)
                self._record_failure()
                return PipelineResult.error_result(error_msg, self.stage.stage_name)
            
            # Execute stage
            logger.info(f"Executing stage: {self.stage.stage_name}")
            result = await self.stage.execute(input_data, context)
            
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            
            if result.success:
                # Reset failure count on success
                self.failure_count = 0
                logger.info(f"Stage {self.stage.stage_name} completed successfully in {execution_time:.2f}ms")
            else:
                self._record_failure()
                logger.warning(f"Stage {self.stage.stage_name} failed: {result.error}")
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = f"Unexpected error in stage {self.stage.stage_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            self._record_failure()
            
            return PipelineResult.error_result(
                error_msg, 
                self.stage.stage_name, 
                execution_time
            )
    
    def _record_failure(self):
        """Record a failure and check if circuit should open."""
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            self.circuit_open = True
            
    def reset_circuit(self):
        """Reset the circuit breaker."""
        self.failure_count = 0
        self.circuit_open = False


@dataclass
class PipelineConfiguration:
    """Configuration for pipeline execution.
    
    Attributes:
        enable_circuit_breaker: Whether to enable circuit breaker pattern
        max_stage_failures: Maximum failures before circuit opens
        enable_parallel_execution: Whether to enable parallel stage execution where possible
        timeout_seconds: Maximum time allowed for pipeline execution
        retry_failed_stages: Whether to retry failed stages
        max_retries: Maximum number of retries per stage
    """
    enable_circuit_breaker: bool = True
    max_stage_failures: int = 3
    enable_parallel_execution: bool = False
    timeout_seconds: float = 300.0  # 5 minutes
    retry_failed_stages: bool = False
    max_retries: int = 1