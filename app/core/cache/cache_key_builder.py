"""
Cache key builder for document processing.

Generates consistent and unique cache keys based on user email, 
filename, and file size to prevent cache collisions.
"""
import hashlib
from typing import Optional
from fastapi import UploadFile


class CacheKeyBuilder:
    """
    Builds cache keys for document processing.
    
    Cache key format: {email}_{filename}_{file_size}_{hash_suffix}
    """
    
    @staticmethod
    def build_cache_key(email: str, filename: str, file_size: Optional[int] = None) -> str:
        """
        Build a cache key for the given parameters.
        
        Args:
            email: User email
            filename: Original filename
            file_size: File size in bytes (optional)
            
        Returns:
            Cache key string
        """
        # Sanitize components
        safe_email = CacheKeyBuilder._sanitize_component(email)
        safe_filename = CacheKeyBuilder._sanitize_component(filename)
        
        # Build base key
        if file_size:
            base_key = f"{safe_email}_{safe_filename}_{file_size}"
        else:
            base_key = f"{safe_email}_{safe_filename}"
        
        # Add hash suffix to ensure uniqueness and avoid long keys
        hash_suffix = CacheKeyBuilder._get_hash_suffix(base_key)
        
        return f"{base_key}_{hash_suffix}"
    
    @staticmethod
    async def build_cache_key_from_file(email: str, file: UploadFile) -> str:
        """
        Build a cache key from UploadFile object.
        
        Args:
            email: User email
            file: UploadFile object
            
        Returns:
            Cache key string
        """
        # Get file size
        current_position = file.file.tell()
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(current_position)  # Restore position
        
        return CacheKeyBuilder.build_cache_key(
            email=email,
            filename=file.filename,
            file_size=file_size
        )
    
    @staticmethod
    def _sanitize_component(component: str) -> str:
        """
        Sanitize a component for use in cache key.
        
        Args:
            component: Component to sanitize
            
        Returns:
            Sanitized component
        """
        # Remove special characters and limit length
        safe_component = "".join(c for c in component if c.isalnum() or c in ".-_")
        return safe_component[:50]  # Limit length
    
    @staticmethod
    def _get_hash_suffix(key: str) -> str:
        """
        Generate a short hash suffix for the key.
        
        Args:
            key: Key to hash
            
        Returns:
            Short hash suffix
        """
        return hashlib.md5(key.encode()).hexdigest()[:8]
