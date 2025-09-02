"""
Cache decorator for Azure Document Intelligence calls.

Provides a decorator to automatically cache Azure extraction results
and avoid redundant API calls.
"""
import logging
from functools import wraps
from typing import Callable, Dict, Any
from fastapi import UploadFile

from .cache_manager import DocumentCacheManager

logger = logging.getLogger(__name__)


def cache_azure_extraction(cache_duration_days: int = 7):
    """
    Decorator to cache Azure Document Intelligence extraction results.
    
    Args:
        cache_duration_days: Cache duration in days (default 7)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract email and file from arguments
            email = None
            file = None
            
            # Try to extract from kwargs first
            if 'email' in kwargs:
                email = kwargs['email']
            if 'file' in kwargs:
                file = kwargs['file']
            
            # If not found in kwargs, look in args
            if not email or not file:
                # Try to match common patterns in function signatures
                if len(args) >= 2:
                    # Common pattern: func(file, email, ...)
                    if isinstance(args[0], UploadFile):
                        file = args[0]
                        if isinstance(args[1], str):
                            email = args[1]
                    # Alternative pattern: func(email, file, ...)
                    elif isinstance(args[1], UploadFile):
                        file = args[1]
                        if isinstance(args[0], str):
                            email = args[0]
            
            # If we couldn't extract email and file, proceed without caching
            if not email or not file:
                logger.debug("Could not extract email and file for caching, proceeding without cache")
                return await func(*args, **kwargs)
            
            # Initialize cache manager
            cache_manager = DocumentCacheManager(cache_duration_days=cache_duration_days)
            
            # Try to get from cache
            cached_result = await cache_manager.get_cached_document(email, file)
            if cached_result:
                logger.info(f"Returning cached result for {email} - {file.filename}")
                return cached_result.get("extracted_data")
            
            # If not cached, call the original function
            logger.debug(f"No cache found, calling Azure for {email} - {file.filename}")
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result:
                await cache_manager.cache_document_result(email, file, result)
            
            return result
            
        return wrapper
    return decorator


def cache_document_processing(cache_duration_days: int = 7):
    """
    Decorator specifically for document processing functions.
    
    This decorator is designed for functions that take (file, email, ...) parameters
    and return document processing results.
    
    Args:
        cache_duration_days: Cache duration in days (default 7)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(file: UploadFile, email: str, *args, **kwargs):
            # Initialize cache manager
            cache_manager = DocumentCacheManager(cache_duration_days=cache_duration_days)
            
            # Try to get from cache
            cached_result = await cache_manager.get_cached_document(email, file)
            if cached_result:
                logger.info(f"🎯 Cache HIT: Returning cached result for {email} - {file.filename}")
                return cached_result.get("extracted_data")
            
            # If not cached, call the original function
            logger.debug(f"⚡ Cache MISS: Calling Azure for {email} - {file.filename}")
            result = await func(file, email, *args, **kwargs)
            
            # Cache the result
            if result:
                await cache_manager.cache_document_result(email, file, result)
                logger.info(f"💾 Cached result for {email} - {file.filename}")
            
            return result
            
        return wrapper
    return decorator
