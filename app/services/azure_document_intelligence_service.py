import logging
import os
import tempfile
import json
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.core.exceptions import DocumentProcessingError
from app.config import settings
from app.services.utils.azure_response_serializer import AzureResponseSerializer
from app.services.utils.pdf_image_extractor import PDFImageExtractor
from app.services.providers.base_document_provider import BaseDocumentProvider
from app.services.storage.document_storage_service import DocumentStorageService

logger = logging.getLogger(__name__)

class AzureDocumentIntelligenceService(BaseDocumentProvider):
    def __init__(self, storage_service: DocumentStorageService = None):
        # Inicializar storage service
        if storage_service is None:
            storage_service = DocumentStorageService()
        
        super().__init__(storage_service)
        
        self.endpoint = settings.azure_document_intelligence_endpoint
        self.key = settings.azure_document_intelligence_key
        self.model_id = settings.azure_document_intelligence_model

        if not self.endpoint or not self.key:
            raise ValueError("Azure Document Intelligence credentials not configured")

        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )
    
    def get_provider_name(self) -> str:
        return "azure"

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract plain text from PDF bytes (for backward compatibility with tests)
        """
        try:
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-read",
                analyze_request=pdf_bytes,
                **{"content_type": "application/pdf"}
            )
            
            result = poller.result()
            return result.content if hasattr(result, "content") and result.content else ""
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise DocumentProcessingError(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_pdf_with_coordinates(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text with coordinate information from PDF bytes (for backward compatibility with tests)
        """
        try:
            poller = self.client.begin_analyze_document(
                model_id=self.model_id,
                analyze_request=pdf_bytes,
                **{"content_type": "application/pdf"}
            )
            
            result = poller.result()
            
            # Structure data similar to analyze_document but simpler
            structured_data = {
                "full_text": result.content if hasattr(result, "content") else "",
                "pages": []
            }
            
            if hasattr(result, "pages") and result.pages:
                for page in result.pages:
                    page_data = {"lines": []}
                    if hasattr(page, "lines") and page.lines:
                        for line in page.lines:
                            line_data = {
                                "content": line.content if hasattr(line, "content") else "",
                                "polygon": []
                            }
                            if hasattr(line, "polygon") and line.polygon:
                                for point in line.polygon:
                                    line_data["polygon"].append({
                                        "x": point.x if hasattr(point, "x") else 0,
                                        "y": point.y if hasattr(point, "y") else 0
                                    })
                            page_data["lines"].append(line_data)
                    structured_data["pages"].append(page_data)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting text with coordinates from PDF: {str(e)}")
            raise DocumentProcessingError(f"Error extracting text with coordinates from PDF: {str(e)}")

    async def analyze_document(self, file: UploadFile, document_id: str = None) -> Dict[str, Any]:
        """
        Analyzes document using Azure AI Document Intelligence
        Returns structured data compatible with current format
        """
        if document_id is None:
            document_id = self._generate_document_id()
            
        try:
            file_bytes = await file.read()
            await file.seek(0)

            # Process document
            poller = self.client.begin_analyze_document(
                model_id=self.model_id,
                analyze_request=file_bytes,
                **{"content_type": "application/pdf"}
            )
            
            result = poller.result()
            
            # Converter resultado para dict para armazenamento
            raw_response = self._serialize_azure_response(result)
            
            # Estruturar dados do resultado
            structured_data = self._structure_document_data(result)
            
            # Extrair imagens se houver figuras detectadas
            image_base64_dict = await self.extract_document_images(file, result)
            if image_base64_dict:
                structured_data["image_data"] = image_base64_dict
            
            # Salvar artefatos do documento
            await self._save_document_artifacts(file, document_id, raw_response, structured_data)
            
            return structured_data

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise DocumentProcessingError(f"Error processing document with Azure AI: {str(e)}")
    
    def _serialize_azure_response(self, result) -> Dict[str, Any]:
        """
        Serializa resposta do Azure para dicionário
        """
        try:
            serializer = AzureResponseSerializer()
            return serializer.serialize_to_dict(result)
        except Exception as e:
            logger.error(f"Erro ao serializar resposta Azure: {str(e)}")
            return {"error": f"Serialization failed: {str(e)}"}

    def _structure_document_data(self, result) -> Dict[str, Any]:
        """Structures data from Azure AI result"""
        full_text = result.content if hasattr(result, "content") else ""
        tables = self._extract_tables(result)
        key_value_pairs = self._extract_key_value_pairs(result)
        paragraphs = self._extract_paragraphs(result)
        images = self._extract_images(result)
        page_count = len(result.pages) if hasattr(result, "pages") and result.pages else 1
        confidence = self._calculate_average_confidence(result)
        
        return {
            "text": full_text,
            "tables": tables,
            "key_value_pairs": key_value_pairs,
            "paragraphs": paragraphs,
            "images": images,
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

    def _extract_images(self, result) -> List[Dict[str, Any]]:
        """Extract images information from the document result using figures information"""
        images = []
        
        # Verificar se o resultado tem a propriedade "figures"
        if hasattr(result, "figures") and result.figures:
            for i, figure in enumerate(result.figures):
                figure_id = getattr(figure, "id", f"{i+1}")
                
                # Inicializar dados da imagem
                image_data = {
                    "id": figure_id,
                    "confidence": getattr(figure, "confidence", 0.0),
                }
                
                # Extrair informação de regiões da figura
                if hasattr(figure, "boundingRegions") and figure.boundingRegions:
                    region = figure.boundingRegions[0]  # Usar a primeira região
                    
                    # Adicionar informação de página
                    image_data["page"] = getattr(region, "pageNumber", 1)
                    
                    # Adicionar bounding box
                    if hasattr(region, "polygon") and region.polygon:
                        # Extrair extremos do polígono para formar retângulo
                        polygon = region.polygon
                        x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
                        y_coords = [polygon[i] for i in range(1, len(polygon), 2)]
                        
                        image_data["bounding_box"] = {
                            "x": min(x_coords),
                            "y": min(y_coords),
                            "width": max(x_coords) - min(x_coords),
                            "height": max(y_coords) - min(y_coords)
                        }
                
                # Extrair referências de conteúdo
                if hasattr(figure, "spans") and figure.spans:
                    span = figure.spans[0]
                    image_data["text_offset"] = getattr(span, "offset", 0)
                    image_data["text_length"] = getattr(span, "length", 0)
                
                images.append(image_data)
        
        # Fallback para o método antigo se não houver figures
        elif hasattr(result, "images") and result.images:
            for i, image in enumerate(result.images):
                image_data = {
                    "id": i + 1,
                    "page": getattr(image, "page_number", 1),
                    "confidence": getattr(image, "confidence", 0.0),
                }
                
                # Extract bounding box information if available
                if hasattr(image, "bounding_box"):
                    image_data["bounding_box"] = {
                        "x": image.bounding_box.x,
                        "y": image.bounding_box.y,
                        "width": image.bounding_box.width,
                        "height": image.bounding_box.height
                    }
                
                # Add image type/format if available
                if hasattr(image, "format"):
                    image_data["format"] = image.format
                
                images.append(image_data)
        
        return images

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

    def _save_response_to_json(self, result, original_filename: str) -> None:
        """
        DEPRECATED: Usar storage service em vez desta função
        Mantido para compatibilidade temporária
        """
        logger.warning("_save_response_to_json está deprecated. Use storage service.")
        try:
            raw_response = self._serialize_azure_response(result)
            self.storage.save_raw_response(raw_response, original_filename, self.provider_name)
        except Exception as e:
            logger.error(f"Erro ao salvar resposta JSON: {str(e)}")

    async def extract_document_images(self, file: UploadFile, result: Any) -> Dict[str, str]:
        """
        Extrai imagens do documento PDF usando as coordenadas das figuras identificadas pelo Azure
        
        Args:
            file: Arquivo PDF original
            result: Resultado da análise do Azure Document Intelligence
            
        Returns:
            Dicionário com IDs das figuras e strings base64 das imagens
        """
        # Salvar o PDF em um arquivo temporário
        temp_file = None
        try:
            # Reposicionar o ponteiro do arquivo
            await file.seek(0)
            
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                temp_file = tmp.name
                tmp.write(await file.read())
            
            # Extrair imagens do PDF
            extracted_images = {}
            
            # Converter o resultado para um dicionário para processamento
            if hasattr(result, "as_dict"):
                result_dict = result.as_dict()
            else:
                # Se não tiver as_dict, usar a serialização que já temos
                serializer = AzureResponseSerializer()
                saved_path = serializer.save_response_to_json(result, file.filename)
                
                # Ler o arquivo JSON salvo
                if saved_path:
                    with open(saved_path, "r", encoding="utf-8") as f:
                        result_dict = json.load(f)
                else:
                    logger.error("Não foi possível serializar o resultado para extração de imagens")
                    return {}
            
            # Extrair imagens usando o PDFImageExtractor
            image_bytes_dict = PDFImageExtractor.extract_figures_from_azure_result(
                pdf_path=temp_file,
                azure_result=result_dict
            )
            
            # Converter para base64
            for figure_id, img_bytes in image_bytes_dict.items():
                base64_img = PDFImageExtractor.get_base64_image(img_bytes)
                extracted_images[figure_id] = base64_img
            
            return extracted_images
            
        except Exception as e:
            logger.error(f"Erro ao extrair imagens do documento: {str(e)}")
            return {}
            
        finally:
            # Limpar arquivo temporário
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo temporário: {str(e)}")
