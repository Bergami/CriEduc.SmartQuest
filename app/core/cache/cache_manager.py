"""
Document cache manager for Azure Document Intelligence responses.

Main interface for caching document processing results to avoid 
redundant Azure API calls.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import UploadFile

from .cache_storage import CacheStorage
from .cache_key_builder import CacheKeyBuilder

logger = logging.getLogger(__name__)


class DocumentCacheManager:
    """
    Manages caching for document processing results.
    
    Provides high-level interface for caching Azure Document Intelligence
    responses to avoid redundant API calls for the same documents.
    """
    
    def __init__(self, cache_dir: str = "cache", cache_duration_days: int = 7):
        """
        Initialize document cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration_days: Cache duration in days (default 7)
        """
        self.storage = CacheStorage(cache_dir, cache_duration_days)
        self.key_builder = CacheKeyBuilder()
        logger.info("Document cache manager initialized")
    
    async def get_cached_document(self, email: str, file: UploadFile) -> Optional[Dict[str, Any]]:
        """
        Get cached document processing result.
        
        Args:
            email: User email
            file: Upload file object
            
        Returns:
            Cached document data if found, None otherwise
        """
        try:
            cache_key = await self.key_builder.build_cache_key_from_file(email, file)
            logger.debug(f"Looking for cached document with key: {cache_key}")
            
            cached_data = self.storage.get(cache_key)
            
            if cached_data:
                logger.info(f"Found cached document for {email} - {file.filename}")
                return cached_data
            else:
                logger.debug(f"No cached document found for {email} - {file.filename}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached document: {e}")
            return None
    
    async def cache_document_result(
        self, 
        email: str, 
        file: UploadFile, 
        extracted_data: Dict[str, Any]
    ) -> bool:
        """
        Cache document processing result.
        
        Args:
            email: User email
            file: Upload file object
            extracted_data: Extracted data from Azure Document Intelligence
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            cache_key = await self.key_builder.build_cache_key_from_file(email, file)
            logger.debug(f"Caching document with key: {cache_key}")
            
            # Prepare data for caching
            cache_data = {
                "email": email,
                "filename": file.filename,
                "content_type": file.content_type,
                "extracted_data": extracted_data,
                "cache_metadata": {
                    "cache_key": cache_key,
                    "original_filename": file.filename,
                    "user_email": email
                }
            }
            
            success = self.storage.set(cache_key, cache_data)
            
            if success:
                logger.info(f"Successfully cached document for {email} - {file.filename}")
            else:
                logger.warning(f"Failed to cache document for {email} - {file.filename}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error caching document result: {e}")
            return False
    
    def invalidate_document_cache(self, email: str, filename: str, file_size: Optional[int] = None) -> bool:
        """
        Invalidate cached document.
        
        Args:
            email: User email
            filename: Filename
            file_size: File size (optional)
            
        Returns:
            True if invalidated, False otherwise
        """
        try:
            cache_key = self.key_builder.build_cache_key(email, filename, file_size)
            success = self.storage.delete(cache_key)
            
            if success:
                logger.info(f"Invalidated cache for {email} - {filename}")
            else:
                logger.debug(f"No cache found to invalidate for {email} - {filename}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error invalidating document cache: {e}")
            return False
    
    def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries cleaned up
        """
        try:
            cleaned_count = self.storage.cleanup_expired()
            logger.info(f"Cache cleanup completed: {cleaned_count} entries removed")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = self.storage.get_cache_stats()
            logger.debug(f"Cache stats retrieved: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    async def is_document_cached(self, email: str, file: UploadFile) -> bool:
        """
        Check if document is cached without retrieving the data.
        
        Args:
            email: User email
            file: Upload file object
            
        Returns:
            True if document is cached, False otherwise
        """
        try:
            cache_key = await self.key_builder.build_cache_key_from_file(email, file)
            cached_data = self.storage.get(cache_key)
            return cached_data is not None
            
        except Exception as e:
            logger.error(f"Error checking if document is cached: {e}")
            return False
