"""Pipeline stages for document processing.

This package contains all the individual stages that make up the
document processing pipeline.
"""

from .context_preparation import ContextPreparationStage, ContextPreparationInput
from .image_analysis import ImageAnalysisStage, ImageAnalysisInput, ImageAnalysisOutput
from .header_parsing import HeaderParsingStage, HeaderParsingInput
from .question_extraction import QuestionExtractionStage, QuestionExtractionInput, QuestionExtractionOutput
from .context_building import ContextBuildingStage, ContextBuildingInput
from .figure_association import FigureAssociationStage, FigureAssociationInput
from .response_aggregation import ResponseAggregationStage, ResponseAggregationInput

__all__ = [
    'ContextPreparationStage',
    'ContextPreparationInput',
    'ImageAnalysisStage', 
    'ImageAnalysisInput',
    'ImageAnalysisOutput',
    'HeaderParsingStage',
    'HeaderParsingInput',
    'QuestionExtractionStage',
    'QuestionExtractionInput', 
    'QuestionExtractionOutput',
    'ContextBuildingStage',
    'ContextBuildingInput',
    'FigureAssociationStage',
    'FigureAssociationInput',
    'ResponseAggregationStage',
    'ResponseAggregationInput'
]