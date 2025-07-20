import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)

class AzureResponseSerializer:
    """
    Utility class for saving Azure Document Intelligence raw responses.
    """
    
    @staticmethod
    def save_response_to_json(result: Any, original_filename: str) -> str:
        """
        Saves the raw Azure Document Intelligence response to a JSON file for testing/debugging
        
        Args:
            result: The raw result object from Azure Document Intelligence
            original_filename: The original filename of the processed document
            
        Returns:
            The path to the saved JSON file
        """
        # Create tests directory if it doesn't exist
        tests_dir = Path(__file__).parent.parent.parent.parent / "tests"
        os.makedirs(tests_dir, exist_ok=True)
        
        # Clean filename for use in the JSON filename
        clean_name = "".join(c if c.isalnum() else "_" for c in os.path.splitext(original_filename)[0])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"azure_response_{clean_name}_{timestamp}.json"
        output_path = tests_dir / output_filename
        
        # Save raw response to JSON file
        try:
            # Serialize raw result to JSON using its .as_dict() method if available
            if hasattr(result, "as_dict"):
                raw_data = result.as_dict()
            else:
                # Fallback to string representation if .as_dict() not available
                raw_data = {"raw_content": str(result)}
                
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Azure response saved to {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving Azure response to JSON: {str(e)}")
            return ""
    
    @staticmethod
    def serialize_to_dict(result: Any) -> Dict[str, Any]:
        """
        Serializa resultado do Azure para dicionário
        
        Args:
            result: Resultado do Azure Document Intelligence
            
        Returns:
            Dicionário com os dados serializados
        """
        try:
            # Usar .as_dict() se disponível
            if hasattr(result, "as_dict"):
                return result.as_dict()
            else:
                # Fallback para representação string
                return {"raw_content": str(result)}
        except Exception as e:
            logger.error(f"Erro ao serializar resultado Azure: {str(e)}")
            return {"error": f"Serialization failed: {str(e)}"}

