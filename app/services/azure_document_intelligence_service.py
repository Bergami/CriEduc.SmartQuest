import logging
from typing import Dict, Any, List
from fastapi import UploadFile
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.core.exceptions import DocumentProcessingError
from app.config import settings

logger = logging.getLogger(__name__)

class AzureDocumentIntelligenceService:
    def __init__(self):
        self.endpoint = settings.azure_document_intelligence_endpoint
        self.key = settings.azure_document_intelligence_key
        self.model_id = settings.azure_document_intelligence_model

        if not self.endpoint or not self.key:
            raise ValueError("Azure Document Intelligence credentials not configured")

        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    async def analyze_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Analisa documento usando Azure AI Document Intelligence
        Retorna dados estruturados compatíveis com o formato atual
        """
        try:
            file_bytes = await file.read()
            await file.seek(0)

            # Processar documento
            poller = self.client.begin_analyze_document(
                model_id=self.model_id,
                body=file_bytes,
                content_type="application/pdf"
            )
            
            result = poller.result()
            structured_data = self._structure_document_data(result)
            
            return structured_data

        except Exception as e:
            logger.error(f"Erro ao processar documento: {str(e)}")
            raise DocumentProcessingError(f"Erro ao processar documento com Azure AI: {str(e)}")

    def _structure_document_data(self, result) -> Dict[str, Any]:
        """Estrutura dados do resultado do Azure AI"""
        full_text = result.content if hasattr(result, "content") else ""
        tables = self._extract_tables(result)
        key_value_pairs = self._extract_key_value_pairs(result)
        paragraphs = self._extract_paragraphs(result)
        page_count = len(result.pages) if hasattr(result, "pages") and result.pages else 1
        confidence = self._calculate_average_confidence(result)
        
        return {
            "text": full_text,
            "tables": tables,
            "key_value_pairs": key_value_pairs,
            "paragraphs": paragraphs,
            "page_count": page_count,
            "confidence": confidence
        }

    def _extract_tables(self, result) -> List[Dict[str, Any]]:
        tables = []
        if hasattr(result, "tables") and result.tables:
            for table in result.tables:
                table_data = {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": []
                }
                for cell in table.cells:
                    table_data["cells"].append({
                        "content": cell.content if cell.content else "",
                        "row_index": cell.row_index,
                        "column_index": cell.column_index,
                        "confidence": getattr(cell, 'confidence', 0.0)
                    })
                tables.append(table_data)
        return tables

    def _extract_key_value_pairs(self, result) -> Dict[str, str]:
        kv_pairs = {}
        if hasattr(result, "key_value_pairs") and result.key_value_pairs:
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    key = kv_pair.key.content.strip() if kv_pair.key.content else ""
                    value = kv_pair.value.content.strip() if kv_pair.value.content else ""
                    if key and value:
                        kv_pairs[key] = value
        return kv_pairs

    def _extract_paragraphs(self, result) -> List[Dict[str, Any]]:
        paragraphs = []
        if hasattr(result, "paragraphs") and result.paragraphs:
            for para in result.paragraphs:
                paragraphs.append({
                    "content": para.content if para.content else "",
                    "role": getattr(para, 'role', None),
                    "confidence": getattr(para, 'confidence', 0.0)
                })
        return paragraphs

    def _calculate_average_confidence(self, result) -> float:
        confidences = []
        if hasattr(result, "paragraphs") and result.paragraphs:
            for para in result.paragraphs:
                if hasattr(para, 'confidence') and para.confidence:
                    confidences.append(para.confidence)
        if hasattr(result, "key_value_pairs") and result.key_value_pairs:
            for kv in result.key_value_pairs:
                if hasattr(kv, 'confidence') and kv.confidence:
                    confidences.append(kv.confidence)
        return sum(confidences) / len(confidences) if confidences else 0.8
