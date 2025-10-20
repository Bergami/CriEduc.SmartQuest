"""
Modelos de persistência para MongoDB

Este módulo contém os modelos Pydantic específicos para persistência 
de dados no MongoDB conforme prompt original.
"""

from .base_document import BaseDocument
from .analyze_document_record import AnalyzeDocumentRecord
from .azure_processing_data_record import AzureProcessingDataRecord, ProcessingMetrics
from .enums import DocumentStatus

__all__ = [
    "BaseDocument",
    "AnalyzeDocumentRecord", 
    "AzureProcessingDataRecord",
    "ProcessingMetrics",
    "DocumentStatus"
]