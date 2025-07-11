import re
from typing import Dict, Any

class TextNormalizer:
    """
    Handles text cleaning and normalization for all document extraction providers.
    Centralizes text processing logic to ensure consistency across different providers.
    """
    
    @staticmethod
    def clean_extracted_text(text: str, provider_name: str = None) -> str:
        """
        Clean and normalize extracted text from any provider.
        
        Args:
            text: Raw extracted text
            provider_name: Name of the extraction provider (for provider-specific cleaning)
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Apply common cleaning rules
        cleaned_text = TextNormalizer._apply_common_cleaning(text)
        
        # Apply provider-specific cleaning
        if provider_name:
            cleaned_text = TextNormalizer._apply_provider_specific_cleaning(cleaned_text, provider_name)
        
        return cleaned_text
    
    @staticmethod
    def _apply_common_cleaning(text: str) -> str:
        """Apply universal text cleaning rules while preserving structure"""
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        # Remove excessive horizontal whitespace but preserve line breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Only spaces and tabs, not newlines
        
        # Remove empty lines but preserve structure
        lines = [line.strip() for line in text.split('\n')]
        # Keep lines that have content or serve as structural separators
        filtered_lines = []
        for line in lines:
            if line.strip():  # Keep non-empty lines
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @staticmethod
    def _apply_provider_specific_cleaning(text: str, provider_name: str) -> str:
        """Apply provider-specific cleaning rules"""
        provider_name = provider_name.lower()
        
        if provider_name == "azure":
            # Remove Azure-specific selection marks
            text = re.sub(r':selected:', '', text)
            text = re.sub(r':unselected:', '', text)
            
        elif provider_name == "tesseract":
            # Future: Add Tesseract-specific cleaning
            pass
            
        elif provider_name == "google_vision":
            # Future: Add Google Vision-specific cleaning
            pass
        
        return text
    
    @staticmethod
    def normalize_output_format(raw_data: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
        """
        Normalize output format from different providers to a standard structure.
        
        Args:
            raw_data: Raw data from the extraction provider
            provider_name: Name of the provider
            
        Returns:
            Standardized data structure
        """
        # Standard output structure
        normalized = {
            "text": "",
            "confidence": 0.0,
            "page_count": 1,
            "metadata": {
                "provider": provider_name,
                "raw_metadata": {}
            }
        }
        
        if provider_name.lower() == "azure":
            normalized.update({
                "text": TextNormalizer.clean_extracted_text(
                    raw_data.get("text", ""), 
                    provider_name
                ),
                "confidence": raw_data.get("confidence", 0.0),
                "page_count": raw_data.get("page_count", 1),
                "metadata": {
                    "provider": provider_name,
                    "raw_metadata": {
                        "tables": raw_data.get("tables", []),
                        "key_value_pairs": raw_data.get("key_value_pairs", {}),
                        "paragraphs": raw_data.get("paragraphs", [])
                    }
                }
            })
        
        return normalized
