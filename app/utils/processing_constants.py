"""
Processing Constants - Centralized Configuration Values

This module centralizes magic numbers and configuration constants used
throughout the document processing pipeline, improving maintainability
and reducing the likelihood of errors.

Created as part of architectural refactoring (Issue #10) to eliminate
magic numbers and improve code clarity.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ProcessingConstants:
    """
    Centralized constants for document processing pipeline.
    
    Using frozen dataclass to ensure immutability and prevent
    accidental modifications of critical configuration values.
    """
    
    # Debug and logging limits
    MAX_DEBUG_BLOCKS: Final[int] = 3
    MAX_LOG_CONTENT_LENGTH: Final[int] = 100
    MAX_PIPELINE_TIMEOUT_SECONDS: Final[int] = 120
    
    # Text processing thresholds  
    MIN_RELEVANT_TEXT_LENGTH: Final[int] = 3
    MAX_TITLE_LENGTH: Final[int] = 100
    MAX_PARAGRAPH_LENGTH: Final[int] = 5000
    
    # Figure and image processing
    DEFAULT_IMAGE_QUALITY: Final[int] = 85
    MAX_IMAGES_PER_CONTEXT: Final[int] = 10
    MAX_FIGURE_EXTRACT_COUNT: Final[int] = 50
    
    # Context block processing
    DEFAULT_CONTEXT_BLOCK_ID: Final[int] = 1
    MAX_CONTEXT_BLOCKS: Final[int] = 100
    MAX_SUB_CONTEXTS_PER_BLOCK: Final[int] = 20
    
    # Question extraction
    MAX_QUESTIONS_PER_DOCUMENT: Final[int] = 50
    MAX_ALTERNATIVES_PER_QUESTION: Final[int] = 10
    
    # Error handling and retry
    MAX_RETRY_ATTEMPTS: Final[int] = 3
    RETRY_DELAY_SECONDS: Final[float] = 1.0
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: Final[int] = 5
    
    # File and content limits
    MAX_FILE_SIZE_MB: Final[int] = 50
    MAX_RESPONSE_SIZE_BYTES: Final[int] = 1048576  # 1MB
    
    # Pipeline stage identifiers
    STAGE_NAMES: Final[tuple] = (
        "context_preparation",
        "image_analysis", 
        "header_parsing",
        "question_extraction",
        "context_building", 
        "figure_association",
        "final_aggregation"
    )


class PipelinePhases:
    """
    Named constants for pipeline phases to improve code readability.
    
    This replaces numeric phase identifiers with meaningful names,
    making the code self-documenting and easier to maintain.
    """
    
    PHASE_1_PREPARATION: Final[str] = "Phase 1: Preparation"
    PHASE_2_IMAGE_ANALYSIS: Final[str] = "Phase 2: Image Analysis" 
    PHASE_3_HEADER_PARSING: Final[str] = "Phase 3: Header Parsing"
    PHASE_4_QUESTION_EXTRACTION: Final[str] = "Phase 4: Question Extraction"
    PHASE_5_CONTEXT_BUILDING: Final[str] = "Phase 5: Context Building"
    PHASE_6_FIGURE_ASSOCIATION: Final[str] = "Phase 6: Figure Association"
    PHASE_7_FINAL_AGGREGATION: Final[str] = "Phase 7: Final Aggregation"


class ErrorMessages:
    """
    Centralized error messages for consistent error handling.
    
    This ensures consistent error messaging across the application
    and makes it easier to maintain error text.
    """
    
    INVALID_AZURE_RESPONSE: Final[str] = "Azure response is malformed or missing required fields"
    MISSING_DOCUMENT_ID: Final[str] = "Document ID is required for processing"
    PIPELINE_STAGE_FAILED: Final[str] = "Pipeline stage failed: {stage_name}"
    CONTEXT_BLOCK_CREATION_FAILED: Final[str] = "Failed to create context block: {error}"
    IMAGE_PROCESSING_FAILED: Final[str] = "Image processing failed: {error}"
    QUESTION_EXTRACTION_FAILED: Final[str] = "Question extraction failed: {error}"
    
    # Critical error messages
    CRITICAL_HAS_IMAGE_ERROR: Final[str] = (
        "Critical error: InternalContextBlock missing 'has_image' attribute. "
        "This indicates regression of the has_image vs has_images bug."
    )
    
    LEGACY_FALLBACK_WARNING: Final[str] = (
        "Warning: Falling back to legacy method. "
        "This should be removed after Pydantic flow validation."
    )


class DefaultValues:
    """
    Default values used throughout the processing pipeline.
    
    Centralizes default values to ensure consistency and make
    them easily configurable.
    """
    
    DEFAULT_SOURCE: Final[str] = "exam_document"
    DEFAULT_TITLE: Final[str] = "Untitled Context"
    DEFAULT_STATEMENT: Final[str] = ""
    DEFAULT_CONTENT_TYPE: Final[str] = "text"
    DEFAULT_SEQUENCE: Final[str] = "i"
    
    # Pydantic model defaults
    DEFAULT_HAS_IMAGE: Final[bool] = False
    DEFAULT_CONTEXT_ID: Final[int] = None
    DEFAULT_QUESTION_NUMBER: Final[int] = 1


# Create singleton instances for easy import
PROCESSING_CONSTANTS = ProcessingConstants()
PIPELINE_PHASES = PipelinePhases()
ERROR_MESSAGES = ErrorMessages()
DEFAULT_VALUES = DefaultValues()


def get_max_debug_blocks() -> int:
    """
    Get the maximum number of blocks to show in debug output.
    
    Returns:
        Maximum number of debug blocks to display
        
    Example:
        >>> max_blocks = get_max_debug_blocks()
        >>> for i, block in enumerate(blocks[:max_blocks]):
        ...     logger.debug(f"Block {i+1}: {block}")
    """
    return PROCESSING_CONSTANTS.MAX_DEBUG_BLOCKS


def get_pipeline_phase_name(phase_number: int) -> str:
    """
    Get human-readable name for pipeline phase.
    
    Args:
        phase_number: Phase number (1-7)
        
    Returns:
        Human-readable phase name
        
    Raises:
        ValueError: If phase number is invalid
        
    Example:
        >>> get_pipeline_phase_name(1)
        'Phase 1: Preparation'
    """
    phase_map = {
        1: PIPELINE_PHASES.PHASE_1_PREPARATION,
        2: PIPELINE_PHASES.PHASE_2_IMAGE_ANALYSIS,
        3: PIPELINE_PHASES.PHASE_3_HEADER_PARSING,
        4: PIPELINE_PHASES.PHASE_4_QUESTION_EXTRACTION,
        5: PIPELINE_PHASES.PHASE_5_CONTEXT_BUILDING,
        6: PIPELINE_PHASES.PHASE_6_FIGURE_ASSOCIATION,
        7: PIPELINE_PHASES.PHASE_7_FINAL_AGGREGATION,
    }
    
    if phase_number not in phase_map:
        raise ValueError(f"Invalid phase number: {phase_number}. Must be 1-7.")
    
    return phase_map[phase_number]