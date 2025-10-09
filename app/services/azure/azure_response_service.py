"""
Azure Response Service

Responsável por gerenciar arquivos de resposta do Azure Document Intelligence
salvos no diretório tests/responses/azure.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from app.core.logging import logger


class AzureResponseService:
    """
    Serviço para carregar e processar respostas salvas do Azure Document Intelligence.
    """
    
    @staticmethod
    def get_azure_responses_directory() -> Path:
        """
        Retorna o diretório onde estão salvos os responses do Azure.
        """
        base_path = Path(__file__).parent.parent.parent  # Vai para raiz do projeto
        return base_path / "tests" / "responses" / "azure"
    
    @staticmethod
    def get_latest_azure_response() -> Optional[Dict[str, Any]]:
        """
        Busca e carrega o arquivo de resposta mais recente do Azure.
        
        Returns:
            Dict com a resposta do Azure ou None se não encontrar arquivos
            
        Raises:
            FileNotFoundError: Se o diretório não existir ou estiver vazio
            json.JSONDecodeError: Se o arquivo não for um JSON válido
        """
        azure_dir = AzureResponseService.get_azure_responses_directory()
        
        if not azure_dir.exists():
            raise FileNotFoundError(f"Azure responses directory not found: {azure_dir}")
        
        # Buscar todos os arquivos JSON no diretório
        json_files = list(azure_dir.glob("*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in Azure responses directory: {azure_dir}")
        
        # Ordenar por data de modificação (mais recente primeiro)
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        logger.info(f"Loading latest Azure response: {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                azure_response = json.load(f)
            
            logger.info(f"Successfully loaded Azure response from {latest_file.name}")
            return azure_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {latest_file.name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {latest_file.name}: {str(e)}")
            raise
    
    @staticmethod
    def get_latest_file_info() -> Dict[str, Any]:
        """
        Retorna informações sobre o arquivo mais recente sem carregar seu conteúdo.
        
        Returns:
            Dict com informações do arquivo (nome, data de modificação, tamanho)
        """
        azure_dir = AzureResponseService.get_azure_responses_directory()
        
        if not azure_dir.exists():
            raise FileNotFoundError(f"Azure responses directory not found: {azure_dir}")
        
        json_files = list(azure_dir.glob("*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in Azure responses directory: {azure_dir}")
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        file_stats = latest_file.stat()
        
        return {
            "filename": latest_file.name,
            "path": str(latest_file),
            "size_bytes": file_stats.st_size,
            "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "modified_timestamp": file_stats.st_mtime
        }
    
    @staticmethod
    def convert_azure_response_to_extracted_data(azure_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte uma resposta do Azure para o formato esperado pelo AnalyzeService.
        
        Args:
            azure_response: Resposta bruta do Azure Document Intelligence
            
        Returns:
            Dict no formato expected por _extract_text_and_metadata_with_factory
        """
        logger.info("Converting Azure response to extracted_data format")
        
        # Extrair texto do Azure response
        text_content = azure_response.get("content", "")
        
        # Criar metadados simulando o que viria do extractor
        metadata = {
            "extraction_provider": "azure_mock",
            "confidence": 0.95,  # Assumir alta confiança para dados já processados
            "page_count": len(azure_response.get("pages", [])),
            "raw_response": azure_response,
            "document_id": "mock_from_saved_response",
            "processing_mode": "saved_response"
        }
        
        # Simular dados de imagem vazios (serão carregados posteriormente se necessário)
        image_data = {}
        
        # Estrutura compatível com o que AnalyzeService espera
        extracted_data = {
            "text": text_content,
            "header": {},  # Será preenchido pelo HeaderParser
            "images": image_data,
            "metadata": metadata,
            "confidence": 0.95,
            "page_count": len(azure_response.get("pages", [])),
            "image_data": image_data
        }
        
        logger.info(f"Converted Azure response: {len(text_content)} chars, {len(azure_response.get('pages', []))} pages")
        
        return extracted_data
