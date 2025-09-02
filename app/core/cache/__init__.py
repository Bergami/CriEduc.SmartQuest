"""
Cache system for Azure Document Intelligence responses.

This module provides a caching layer to avoid redundant Azure API calls
for documents that have been recently processed.
"""

from .cache_manager import DocumentCacheManager
from .cache_key_builder import CacheKeyBuilder

__all__ = ["DocumentCacheManager", "CacheKeyBuilder"]
