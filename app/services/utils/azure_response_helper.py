"""
Helper para extrair métricas e metadados de responses do Azure Document Intelligence
"""
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AzureResponseHelper:
    """
    Helper class para extrair informações de responses do Azure.
    """
    
    @staticmethod
    def extract_metrics(azure_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai métricas do response do Azure.
        
        Args:
            azure_response: Response completo do Azure
            
        Returns:
            Dicionário com métricas extraídas
        """
        try:
            page_count = len(azure_response.get("pages", []))
            paragraph_count = len(azure_response.get("paragraphs", []))
            
            # Calcular confidence score médio
            confidence_score = AzureResponseHelper._calculate_average_confidence(azure_response)
            
            # Extrair operation_id se disponível
            operation_id = azure_response.get("operation_id") or azure_response.get("model_id")
            
            return {
                "page_count": page_count,
                "paragraph_count": paragraph_count,
                "confidence_score": confidence_score,
                "operation_id": operation_id
            }
        except Exception as e:
            logger.warning(f"Error extracting metrics from Azure response: {e}")
            return {
                "page_count": 0,
                "paragraph_count": 0,
                "confidence_score": None,
                "operation_id": None
            }
    
    @staticmethod
    def _calculate_average_confidence(azure_response: Dict[str, Any]) -> Optional[float]:
        """
        Calcula confidence score médio do response.
        
        Args:
            azure_response: Response do Azure
            
        Returns:
            Confidence score médio ou None
        """
        try:
            confidences = []
            
            # Paragraphs confidence
            for para in azure_response.get("paragraphs", []):
                if "confidence" in para and para["confidence"] is not None:
                    confidences.append(para["confidence"])
            
            # Pages confidence (se disponível)
            for page in azure_response.get("pages", []):
                if "confidence" in page and page["confidence"] is not None:
                    confidences.append(page["confidence"])
            
            if confidences:
                return sum(confidences) / len(confidences)
            return None
        except Exception as e:
            logger.debug(f"Could not calculate confidence: {e}")
            return None
    
    @staticmethod
    def extract_azure_metadata(extracted_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extrai metadados do Azure de extracted_data.
        
        Args:
            extracted_data: Dados extraídos contendo metadados
            
        Returns:
            Tupla (azure_model_id, azure_api_version)
        """
        metadata = extracted_data.get("metadata", {})
        
        # Modelo Azure usado
        azure_model_id = (
            metadata.get("azure_model_used") or
            metadata.get("azure_model_id") or
            metadata.get("model_id") or
            "prebuilt-layout"
        )
        
        # Versão da API
        azure_api_version = (
            metadata.get("azure_api_version") or
            metadata.get("api_version") or
            "2023-07-31"
        )
        
        return azure_model_id, azure_api_version
    
    @staticmethod
    def get_azure_response_from_extracted_data(extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recupera o response bruto do Azure de extracted_data.
        
        Args:
            extracted_data: Dados extraídos que podem conter raw_response
            
        Returns:
            Response bruto do Azure ou None
        """
        try:
            metadata = extracted_data.get("metadata", {})
            
            # Tentar obter raw_response
            azure_response = metadata.get("raw_response")
            
            if not azure_response:
                logger.warning("No raw_response found in extracted_data metadata")
                return None
            
            return azure_response
        except Exception as e:
            logger.error(f"Error getting Azure response from extracted_data: {e}")
            return None
