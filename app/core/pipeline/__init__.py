"""Pipeline architecture for document processing.

This package provides a stage-based pipeline architecture to replace
the monolithic DocumentAnalysisOrchestrator approach.
"""

from .interfaces import (
    IPipelineStage,
    IPipeline,
    PipelineResult,
    PipelineStageWrapper,
    PipelineConfiguration
)

__all__ = [
    'IPipelineStage',
    'IPipeline', 
    'PipelineResult',
    'PipelineStageWrapper',
    'PipelineConfiguration'
]