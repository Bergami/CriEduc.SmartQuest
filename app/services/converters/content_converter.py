"""
Content Converter Service

Serviço dedicado para conversão de diferentes formatos de conteúdo
para a estrutura interna do sistema.

Responsabilidades:
- Parsing de múltiplos formatos de entrada (dict, list, string)
- Normalização de estruturas de conteúdo
- Extração de metadados de conversão
"""
import logging
from typing import Dict, Any, List, Tuple


logger = logging.getLogger(__name__)


class ContentConverter:
    """
    Conversor de conteúdo para estruturas internas.
    
    Este serviço encapsula a lógica complexa de conversão de diferentes
    formatos de conteúdo (dict, list, string) para o formato padronizado
    usado pelos modelos internos.
    """
    
    @staticmethod
    def parse_content(content_data: Any) -> Tuple[List[str], str, str]:
        """
        Parse content data de vários formatos para estrutura padronizada.
        
        Args:
            content_data: Dados de conteúdo em qualquer formato suportado:
                - dict: {"description": [...], "texts": [...], etc}
                - list: ["text1", "text2", ...]
                - str: "single text"
                
        Returns:
            Tuple contendo:
                - description (List[str]): Textos extraídos
                - raw_content (str): Representação string do conteúdo original
                - content_source (str): Fonte da conversão
        """
        logger.debug("[ContentConverter.parse_content] Received content_data:")
        logger.debug(content_data)
        
        description: List[str] = []
        
        # Handle dict format
        if isinstance(content_data, dict):
            description = ContentConverter._parse_dict_content(content_data)
        # Handle list format
        elif isinstance(content_data, list):
            description = content_data
        # Handle string format
        else:
            description = [str(content_data)]
        
        # Generate metadata
        raw_content = str(content_data)
        content_source = ContentConverter._identify_content_source(content_data)
        
        logger.debug("[ContentConverter.parse_content] Generated description:")
        logger.debug(description)
        
        return description, raw_content, content_source
    
    @staticmethod
    def _parse_dict_content(content_dict: Dict[str, Any]) -> List[str]:
        """
        Parse conteúdo em formato dict.
        
        Trata múltiplos formatos de dict:
        - {"description": [...]} ou {"description": "text"}
        - {"texts": [...], "content": [...], "paragraphs": [...]}
        - Outros formatos de fallback
        
        Args:
            content_dict: Dict contendo dados de conteúdo
            
        Returns:
            Lista de strings extraídas
        """
        description: List[str] = []
        
        # Priority 1: Extract from 'description' field
        if "description" in content_dict:
            desc_value = content_dict["description"]
            if isinstance(desc_value, list):
                description = desc_value
            else:
                description = [desc_value]
        else:
            # Priority 2: Try to extract from alternative fields
            alternative_fields = ["texts", "content", "paragraphs"]
            for field in alternative_fields:
                if field in content_dict:
                    field_value = content_dict[field]
                    if isinstance(field_value, list):
                        description.extend(field_value)
                    else:
                        description.append(str(field_value))
        
        return description
    
    @staticmethod
    def _identify_content_source(content_data: Any) -> str:
        """
        Identifica a fonte/tipo do conteúdo baseado em sua estrutura.
        
        Args:
            content_data: Dados de conteúdo
            
        Returns:
            String identificando a fonte (ex: "dict_conversion", "list_direct", etc)
        """
        if isinstance(content_data, dict):
            if "description" in content_data:
                return "dict_with_description"
            elif any(key in content_data for key in ["texts", "content", "paragraphs"]):
                return "dict_with_alternative_fields"
            else:
                return "dict_unknown_format"
        elif isinstance(content_data, list):
            return "list_direct"
        else:
            return "string_conversion"
