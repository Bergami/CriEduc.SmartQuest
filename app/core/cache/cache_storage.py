"""
File-based cache storage for Azure Document Intelligence responses.

Provides persistent caching using JSON files with automatic expiration.
"""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CacheStorage:
    """
    File-based cache storage with automatic expiration.
    """
    
    def __init__(self, cache_dir: str = "cache", cache_duration_days: int = 7):
        """
        Initialize cache storage.
        
        Args:
            cache_dir: Directory to store cache files
            cache_duration_days: Cache duration in days (default 7)
        """
        self.cache_duration_days = cache_duration_days
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.documents_cache_dir = self.cache_dir / "documents"
        self.documents_cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"Cache storage initialized at {self.cache_dir}")
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data by key.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        cache_file = self._get_cache_file_path(cache_key)
        
        if not cache_file.exists():
            logger.debug(f"Cache miss: {cache_key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            if self._is_expired(cache_data):
                logger.info(f"Cache expired: {cache_key}")
                self._delete_cache_file(cache_file)
                return None
            
            logger.info(f"Cache hit: {cache_key}")
            return cache_data.get("data")
            
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Error reading cache file {cache_file}: {e}")
            self._delete_cache_file(cache_file)
            return None
    
    def set(self, cache_key: str, data: Dict[str, Any]) -> bool:
        """
        Store data in cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            cache_data = {
                "data": data,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=self.cache_duration_days)).isoformat(),
                "cache_key": cache_key
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data cached successfully: {cache_key}")
            return True
            
        except (OSError, TypeError) as e:
            logger.error(f"Error writing cache file {cache_file}: {e}")
            return False
    
    def delete(self, cache_key: str) -> bool:
        """
        Delete cached data.
        
        Args:
            cache_key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_file = self._get_cache_file_path(cache_key)
        return self._delete_cache_file(cache_file)
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache files.
        
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        
        try:
            for cache_file in self.documents_cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_expired(cache_data):
                        self._delete_cache_file(cache_file)
                        cleaned_count += 1
                        
                except (json.JSONDecodeError, KeyError, OSError):
                    # If we can't read the file, delete it
                    self._delete_cache_file(cache_file)
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired cache files")
                
        except OSError as e:
            logger.error(f"Error during cache cleanup: {e}")
        
        return cleaned_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = list(self.documents_cache_dir.glob("*.json"))
            total_files = len(cache_files)
            
            valid_files = 0
            expired_files = 0
            total_size = 0
            
            for cache_file in cache_files:
                try:
                    total_size += cache_file.stat().st_size
                    
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_expired(cache_data):
                        expired_files += 1
                    else:
                        valid_files += 1
                        
                except (json.JSONDecodeError, KeyError, OSError):
                    expired_files += 1
            
            return {
                "total_files": total_files,
                "valid_files": valid_files,
                "expired_files": expired_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": str(self.cache_dir)
            }
            
        except OSError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """
        Get cache file path for the given key.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Path to cache file
        """
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in ".-_")
        return self.documents_cache_dir / f"{safe_key}.json"
    
    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """
        Check if cache data is expired.
        
        Args:
            cache_data: Cache data with expiration info
            
        Returns:
            True if expired, False otherwise
        """
        try:
            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            return datetime.now() > expires_at
        except (KeyError, ValueError):
            return True
    
    def _delete_cache_file(self, cache_file: Path) -> bool:
        """
        Delete a cache file.
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Deleted cache file: {cache_file}")
                return True
            return False
        except OSError as e:
            logger.error(f"Error deleting cache file {cache_file}: {e}")
            return False
