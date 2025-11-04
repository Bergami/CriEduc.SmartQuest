"""
Content Type Converter - Utility Class for Type Conversions

This utility class eliminates code duplication in content type conversions
across the application, particularly between ContentType enums and strings.

Created as part of architectural refactoring (Issue #10) to improve code
maintainability and reduce duplication.
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from app.enums.content_enums import ContentType


class ContentTypeConverter:
    """
    Utility class for converting between ContentType enums and string representations.
    
    This class centralizes conversion logic that was previously duplicated across:
    - app/services/context/context_block_builder.py
    - app/dtos/responses/document_response_dto.py
    
    Examples:
        >>> converter = ContentTypeConverter()
        >>> types = converter.strings_to_enums(['text', 'image'])
        >>> [ContentType.TEXT, ContentType.IMAGE]
        
        >>> strings = converter.enums_to_strings([ContentType.TEXT, ContentType.IMAGE])
        >>> ['text', 'image']
    """
    
    @staticmethod
    def strings_to_enums(type_strings: List[str]) -> List[ContentType]:
        """
        Convert list of type strings to ContentType enums.

        Args:
            type_strings: List of string representations of content types
            
        Returns:
            List of ContentType enum values
            
        Raises:
            ValueError: If any string cannot be converted to ContentType
            
        Example:
            >>> ContentTypeConverter.strings_to_enums(['text', 'image'])
            [ContentType.TEXT, ContentType.IMAGE]
        """
        if not type_strings:
            return []
            
        result = []
        for type_str in type_strings:
            try:
                # Handle both direct enum values and string representations
                if isinstance(type_str, str):
                    # Try direct enum value lookup first (lowercase)
                    normalized_str = type_str.lower().strip()
                    
                    # Use from_legacy_type for robust conversion
                    content_type = ContentType.from_legacy_type(normalized_str)
                    result.append(content_type)
                elif isinstance(type_str, ContentType):
                    # Already an enum, add directly
                    result.append(type_str)
                else:
                    raise ValueError(f"Cannot convert {type(type_str)} to ContentType")
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid content type string: '{type_str}'. Error: {e}")
        
        return result

    @staticmethod
    def enums_to_strings(type_enums: List[ContentType]) -> List[str]:
        """
        Convert list of ContentType enums to string representations.

        Args:
            type_enums: List of ContentType enum values
            
        Returns:
            List of string representations
            
        Example:
            >>> ContentTypeConverter.enums_to_strings([ContentType.TEXT, ContentType.IMAGE])
            ['text', 'image']
        """
        if not type_enums:
            return []
            
        return [content_type.value for content_type in type_enums]

    @staticmethod
    def normalize_content_type(content_type: Any) -> ContentType:
        """
        Normalize various input types to ContentType enum.
        
        Args:
            content_type: Input that can be string, ContentType enum, or other
            
        Returns:
            Normalized ContentType enum
            
        Raises:
            ValueError: If input cannot be normalized to ContentType
            
        Example:
            >>> ContentTypeConverter.normalize_content_type('text')
            ContentType.TEXT
            >>> ContentTypeConverter.normalize_content_type(ContentType.IMAGE)
            ContentType.IMAGE
        """
        if isinstance(content_type, ContentType):
            return content_type
        elif isinstance(content_type, str):
            return ContentTypeConverter.strings_to_enums([content_type])[0]
        else:
            raise ValueError(f"Cannot normalize {type(content_type)} to ContentType")

    @staticmethod
    def is_valid_content_type_string(type_string: str) -> bool:
        """
        Check if a string is a valid ContentType representation.
        
        Args:
            type_string: String to validate
            
        Returns:
            True if string can be converted to ContentType, False otherwise
            
        Example:
            >>> ContentTypeConverter.is_valid_content_type_string('text')
            True
            >>> ContentTypeConverter.is_valid_content_type_string('invalid')
            False
        """
        try:
            ContentTypeConverter.strings_to_enums([type_string])
            return True
        except ValueError:
            return False

    @staticmethod
    def get_default_content_types() -> List[ContentType]:
        """
        Get default content types for context blocks.
        
        Returns:
            List containing default ContentType.TEXT
            
        Example:
            >>> ContentTypeConverter.get_default_content_types()
            [ContentType.TEXT]
        """
        return [ContentType.TEXT]

    @staticmethod
    def merge_content_types(
        existing_types: List[ContentType], 
        new_types: List[ContentType]
    ) -> List[ContentType]:
        """
        Merge two lists of content types, removing duplicates.
        
        Args:
            existing_types: Current content types
            new_types: Content types to add
            
        Returns:
            Merged list without duplicates, preserving order
            
        Example:
            >>> existing = [ContentType.TEXT]
            >>> new = [ContentType.IMAGE, ContentType.TEXT]
            >>> ContentTypeConverter.merge_content_types(existing, new)
            [ContentType.TEXT, ContentType.IMAGE]
        """
        seen = set()
        result = []
        
        # Add existing types first
        for content_type in existing_types:
            if content_type not in seen:
                seen.add(content_type)
                result.append(content_type)
        
        # Add new types if not already present
        for content_type in new_types:
            if content_type not in seen:
                seen.add(content_type)
                result.append(content_type)
        
        return result