"""
Centralized file manager for organizing all document-related files.
Provides a unified interface for saving documents, images, and responses.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FileLocations:
    """Centralized constants for file storage locations."""
    DOCUMENTS_ORIGINAL = "tests/documents"
    DOCUMENTS_RESPONSES = "tests/documents/responses"


class CentralizedFileManager:
    """
    Centralized file manager for organizing document-related files.
    
    This manager provides:
    - Unified directory structure
    - Consistent file organization
    - Metadata management
    - Path resolution
    
    Directory structure:
    tests/documents/                    # Original documents (PDFs)
    tests/documents/responses/          # Processing responses (JSON)
    
    Note: Images are now stored in Azure Blob Storage, not locally.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the centralized file manager.
        
        Args:
            base_path: Base path for file operations. Defaults to project root.
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Default to project root (4 levels up from this file)
            self.base_path = Path(__file__).parent.parent.parent.parent
        
        # Ensure all directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create all required directories if they don't exist."""
        locations = [
            FileLocations.DOCUMENTS_ORIGINAL,
            FileLocations.DOCUMENTS_RESPONSES
        ]
        for location in locations:
            directory = self.base_path / location
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Directory ensured: {directory}")
    
    def get_path(self, location: str, filename: str = "") -> Path:
        """
        Get full path for a file or directory.
        
        Args:
            location: File location constant
            filename: Optional filename to append
            
        Returns:
            Full path to file or directory
        """
        path = self.base_path / location
        return path / filename if filename else path
    
    def save_document(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save original document (typically PDF).
        
        Args:
            filename: Name of the file
            content: File content as bytes
            metadata: Optional metadata to save alongside
            
        Returns:
            Full path to saved file
        """
        try:
            file_path = self.get_path(FileLocations.DOCUMENTS_ORIGINAL, filename)
            
            # Save document
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Save metadata if provided
            if metadata:
                self._save_metadata(file_path.parent, filename, metadata, "document")
            
            logger.info(f"📄 Document saved: {file_path} ({len(content)} bytes)")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving document {filename}: {str(e)}")
            raise
    
    def save_response(self, filename: str, response_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save processing response as JSON.
        
        Args:
            filename: Name of the response file
            response_data: Response data to save
            metadata: Optional metadata
            
        Returns:
            Full path to saved file
        """
        try:
            # Ensure filename has .json extension
            if not filename.endswith('.json'):
                filename = f"{filename}.json"
            
            file_path = self.get_path(FileLocations.DOCUMENTS_RESPONSES, filename)
            
            # Save response as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            # Save metadata if provided
            if metadata:
                self._save_metadata(file_path.parent, filename, metadata, "response")
            
            logger.info(f"📄 Response saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving response {filename}: {str(e)}")
            raise
    
    def _save_metadata(
        self, 
        directory: Path, 
        filename: str, 
        metadata: Dict[str, Any], 
        file_type: str
    ):
        """Save metadata file alongside the main file."""
        try:
            # Create metadata filename
            base_name = Path(filename).stem
            metadata_filename = f"{base_name}_metadata.json"
            metadata_path = directory / metadata_filename
            
            # Add standard metadata fields
            full_metadata = {
                "file_type": file_type,
                "original_filename": filename,
                "saved_timestamp": datetime.now().isoformat(),
                "manager_version": "1.0",
                **metadata
            }
            
            # Save metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(full_metadata, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📋 Metadata saved: {metadata_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not save metadata for {filename}: {str(e)}")
    
    def get_document_path(self, filename: str) -> Optional[Path]:
        """Get path to a document if it exists."""
        path = self.get_path(FileLocations.DOCUMENTS_ORIGINAL, filename)
        return path if path.exists() else None
    
    def get_response_path(self, filename: str) -> Optional[Path]:
        """Get path to a response file if it exists."""
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        path = self.get_path(FileLocations.DOCUMENTS_RESPONSES, filename)
        return path if path.exists() else None
    
    def list_documents(self) -> list:
        """List all documents in the documents directory."""
        docs_dir = self.get_path(FileLocations.DOCUMENTS_ORIGINAL)
        if not docs_dir.exists():
            return []
        
        return [f.name for f in docs_dir.iterdir() if f.is_file()]
    
    def list_responses(self) -> list:
        """List all response files."""
        responses_dir = self.get_path(FileLocations.DOCUMENTS_RESPONSES)
        if not responses_dir.exists():
            return []
        
        return [f.name for f in responses_dir.iterdir() if f.is_file() and f.suffix == '.json']
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the current storage structure."""
        info = {
            "base_path": str(self.base_path),
            "directories": {},
            "total_files": 0
        }
        
        locations = [
            ("DOCUMENTS_ORIGINAL", FileLocations.DOCUMENTS_ORIGINAL),
            ("DOCUMENTS_RESPONSES", FileLocations.DOCUMENTS_RESPONSES)
        ]
        
        for location_name, location_path in locations:
            dir_path = self.get_path(location_path)
            if dir_path.exists():
                files = list(dir_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                
                info["directories"][location_name] = {
                    "path": str(dir_path),
                    "exists": True,
                    "file_count": file_count
                }
                info["total_files"] += file_count
            else:
                info["directories"][location_name] = {
                    "path": str(dir_path),
                    "exists": False,
                    "file_count": 0
                }
        
        return info
