"""
Cache management utilities for monitoring and maintaining the document cache.

Provides CLI tools for cache inspection, cleanup, and statistics.
"""
import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime

from app.core.cache import DocumentCacheManager


class CacheManager:
    """
    Utility class for cache management operations.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Cache directory path
        """
        self.cache_manager = DocumentCacheManager(cache_dir=cache_dir)
    
    def show_stats(self):
        """
        Display cache statistics.
        """
        print("📊 Cache Statistics")
        print("=" * 40)
        
        stats = self.cache_manager.get_cache_stats()
        
        if "error" in stats:
            print(f"❌ Error: {stats['error']}")
            return
        
        print(f"📁 Cache Directory: {stats['cache_dir']}")
        print(f"📄 Total Files: {stats['total_files']}")
        print(f"✅ Valid Files: {stats['valid_files']}")
        print(f"❌ Expired Files: {stats['expired_files']}")
        print(f"💾 Total Size: {stats['total_size_mb']} MB")
        
        if stats['total_files'] > 0:
            hit_rate = (stats['valid_files'] / stats['total_files']) * 100
            print(f"🎯 Cache Hit Rate: {hit_rate:.1f}%")
    
    def cleanup_expired(self):
        """
        Clean up expired cache entries.
        """
        print("🧹 Cleaning up expired cache entries...")
        
        cleaned_count = self.cache_manager.cleanup_expired_cache()
        
        if cleaned_count > 0:
            print(f"✅ Cleaned up {cleaned_count} expired entries")
        else:
            print("✅ No expired entries found")
        
        # Show updated stats
        self.show_stats()
    
    def clear_all_cache(self):
        """
        Clear all cache entries (use with caution).
        """
        print("⚠️  WARNING: This will delete ALL cache entries!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        try:
            cache_dir = Path(self.cache_manager.storage.cache_dir)
            documents_dir = cache_dir / "documents"
            
            if documents_dir.exists():
                for cache_file in documents_dir.glob("*.json"):
                    cache_file.unlink()
                    print(f"🗑️  Deleted: {cache_file.name}")
                
                print("✅ All cache entries cleared")
            else:
                print("ℹ️  Cache directory not found or empty")
                
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
    
    def inspect_cache_entry(self, cache_key: str):
        """
        Inspect a specific cache entry.
        
        Args:
            cache_key: Cache key to inspect
        """
        print(f"🔍 Inspecting cache entry: {cache_key}")
        print("=" * 50)
        
        cached_data = self.cache_manager.storage.get(cache_key)
        
        if cached_data is None:
            print("❌ Cache entry not found")
            return
        
        print("✅ Cache entry found")
        print(f"📧 Email: {cached_data.get('email', 'N/A')}")
        print(f"📄 Filename: {cached_data.get('filename', 'N/A')}")
        print(f"📝 Content Type: {cached_data.get('content_type', 'N/A')}")
        
        extracted_data = cached_data.get('extracted_data', {})
        if extracted_data:
            text_length = len(extracted_data.get('text', ''))
            print(f"📊 Text Length: {text_length} characters")
            
            header = extracted_data.get('header', {})
            if header:
                print(f"🏛️  Institution: {header.get('institution', 'N/A')}")
                print(f"📚 Subject: {header.get('subject', 'N/A')}")
        
        cache_metadata = cached_data.get('cache_metadata', {})
        if cache_metadata:
            print(f"🔑 Cache Key: {cache_metadata.get('cache_key', 'N/A')}")
    
    def list_cache_entries(self, limit: int = 10):
        """
        List cache entries.
        
        Args:
            limit: Maximum number of entries to show
        """
        print(f"📋 Cache Entries (showing up to {limit})")
        print("=" * 50)
        
        try:
            cache_dir = Path(self.cache_manager.storage.cache_dir)
            documents_dir = cache_dir / "documents"
            
            if not documents_dir.exists():
                print("ℹ️  No cache directory found")
                return
            
            cache_files = list(documents_dir.glob("*.json"))
            
            if not cache_files:
                print("ℹ️  No cache entries found")
                return
            
            for i, cache_file in enumerate(cache_files[:limit]):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    data = cache_data.get('data', {})
                    created_at = cache_data.get('created_at', 'Unknown')
                    expires_at = cache_data.get('expires_at', 'Unknown')
                    
                    print(f"\n{i+1}. {cache_file.stem}")
                    print(f"   📧 Email: {data.get('email', 'N/A')}")
                    print(f"   📄 File: {data.get('filename', 'N/A')}")
                    print(f"   📅 Created: {created_at}")
                    print(f"   ⏰ Expires: {expires_at}")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {cache_file.name}: {e}")
            
            if len(cache_files) > limit:
                print(f"\n... and {len(cache_files) - limit} more entries")
                
        except Exception as e:
            print(f"❌ Error listing cache entries: {e}")


def main():
    """
    Main CLI interface for cache management.
    """
    parser = argparse.ArgumentParser(description="Document Cache Management Utility")
    parser.add_argument("--cache-dir", default="cache", help="Cache directory path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Stats command
    subparsers.add_parser("stats", help="Show cache statistics")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up expired cache entries")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear all cache entries")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List cache entries")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum entries to show")
    
    # Inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect specific cache entry")
    inspect_parser.add_argument("cache_key", help="Cache key to inspect")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize cache manager
    cache_mgr = CacheManager(cache_dir=args.cache_dir)
    
    # Execute command
    if args.command == "stats":
        cache_mgr.show_stats()
    elif args.command == "cleanup":
        cache_mgr.cleanup_expired()
    elif args.command == "clear":
        cache_mgr.clear_all_cache()
    elif args.command == "list":
        cache_mgr.list_cache_entries(limit=args.limit)
    elif args.command == "inspect":
        cache_mgr.inspect_cache_entry(args.cache_key)


if __name__ == "__main__":
    main()
