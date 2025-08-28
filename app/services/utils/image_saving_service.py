"""
Service for saving extracted images with proper naming conventions.
Handles saving images from different extraction methods to organized directories.
"""

import os
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ImageSavingService:
    """
    Service for saving extracted images with proper organization and naming.
    
    Directory structure:
    tests/images/by_provider/
    ├── azure_manual/          # Manual PDF cropping method (existing)
    ├── azure_figures/         # Azure figures API method (new)
    └── comparison/            # Comparison results
    """
    
    def __init__(self, base_path: Optional[str] = None):
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Default to project root
            self.base_path = Path(__file__).parent.parent.parent.parent
        
        self.images_dir = self.base_path / "tests" / "images" / "by_provider"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.images_dir / "azure_manual",      # Existing manual method (rename from 'azure')
            self.images_dir / "azure_figures",     # New Azure figures method
            self.images_dir / "comparison"         # Comparison results
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Directory ensured: {directory}")
    
    def save_images_from_extraction(
        self,
        images: Dict[str, str],
        method: str,
        document_id: str,
        filename: str = "unknown",
        email: str = "unknown"
    ) -> str:
        """
        Save images from extraction with proper naming convention.
        
        Args:
            images: Dictionary of figure_id -> base64_image
            method: Extraction method ('azure_figures', 'manual_pdf', etc.)
            document_id: Unique document identifier
            filename: Original filename
            email: User email
            
        Returns:
            Path to the saved directory
        """
        try:
            # Determine target directory based on method
            if method == "azure_figures":
                target_dir = self.images_dir / "azure_figures"
            elif method == "manual_pdf":
                target_dir = self.images_dir / "azure_manual"
            else:
                target_dir = self.images_dir / method
            
            # Create document-specific subdirectory
            document_dir = target_dir / document_id
            document_dir.mkdir(parents=True, exist_ok=True)
            
            # Save metadata file
            self._save_metadata(document_dir, {
                "method": method,
                "document_id": document_id,
                "filename": filename,
                "email": email,
                "extraction_timestamp": datetime.now().isoformat(),
                "total_images": len(images)
            })
            
            # Save each image
            saved_count = 0
            for figure_id, base64_image in images.items():
                if base64_image:
                    image_path = self._save_single_image(
                        document_dir, figure_id, base64_image, method
                    )
                    if image_path:
                        saved_count += 1
                        logger.debug(f"✅ Saved {figure_id} → {image_path}")
            
            logger.info(f"📸 Saved {saved_count}/{len(images)} images for method '{method}' in {document_dir}")
            return str(document_dir)
            
        except Exception as e:
            logger.error(f"❌ Error saving images for method '{method}': {str(e)}")
            return ""
    
    def _save_single_image(
        self,
        document_dir: Path,
        figure_id: str,
        base64_image: str,
        method: str
    ) -> Optional[str]:
        """Save a single image with proper naming."""
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(base64_image)
            
            # Create filename with method prefix for clarity
            if method == "azure_figures":
                filename = f"fig_{figure_id}.jpg"
            elif method == "manual_pdf":
                filename = f"manual_{figure_id}.jpg"
            else:
                filename = f"{method}_{figure_id}.jpg"
            
            # Save image file
            image_path = document_dir / filename
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            return str(image_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving image {figure_id}: {str(e)}")
            return None
    
    def _save_metadata(self, document_dir: Path, metadata: Dict[str, Any]):
        """Save metadata file for the extraction."""
        try:
            import json
            
            metadata_file = document_dir / "extraction_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📋 Metadata saved: {metadata_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving metadata: {str(e)}")
    
    def save_comparison_results(
        self,
        comparison_data: Dict[str, Any],
        document_id: str,
        filename: str = "unknown",
        email: str = "unknown"
    ) -> str:
        """
        Save comparison results with images from all methods.
        
        Args:
            comparison_data: Full comparison data including extraction_results
            document_id: Unique document identifier
            filename: Original filename
            email: User email
            
        Returns:
            Path to the saved comparison directory
        """
        try:
            # Create comparison directory
            comparison_dir = self.images_dir / "comparison" / document_id
            comparison_dir.mkdir(parents=True, exist_ok=True)
            
            # Save comparison metadata
            comparison_metadata = {
                "document_id": document_id,
                "filename": filename,
                "email": email,
                "comparison_timestamp": datetime.now().isoformat(),
                "methods_tested": list(comparison_data.get("extraction_results", {}).keys()),
                "comparison_summary": comparison_data.get("comparison_summary", {})
            }
            
            self._save_metadata(comparison_dir, comparison_metadata)
            
            # Save images from each method
            extraction_results = comparison_data.get("extraction_results", {})
            saved_methods = []
            
            for method, images in extraction_results.items():
                if images:
                    method_dir = comparison_dir / method
                    method_dir.mkdir(exist_ok=True)
                    
                    for figure_id, base64_image in images.items():
                        if base64_image:
                            image_path = self._save_single_image(
                                method_dir, figure_id, base64_image, method
                            )
                            if image_path:
                                logger.debug(f"✅ Comparison: {method}/{figure_id} → {image_path}")
                    
                    saved_methods.append(method)
            
            logger.info(f"📊 Saved comparison results for {len(saved_methods)} methods in {comparison_dir}")
            return str(comparison_dir)
            
        except Exception as e:
            logger.error(f"❌ Error saving comparison results: {str(e)}")
            return ""
    
    def get_saved_images_path(self, method: str, document_id: str) -> Optional[Path]:
        """Get the path where images for a specific method and document are saved."""
        if method == "azure_figures":
            target_dir = self.images_dir / "azure_figures"
        elif method == "manual_pdf":
            target_dir = self.images_dir / "azure_manual"
        else:
            target_dir = self.images_dir / method
        
        document_dir = target_dir / document_id
        return document_dir if document_dir.exists() else None
    
    def list_saved_extractions(self) -> Dict[str, list]:
        """List all saved extractions by method."""
        extractions = {}
        
        for method_dir in self.images_dir.iterdir():
            if method_dir.is_dir():
                method_name = method_dir.name
                extractions[method_name] = []
                
                for doc_dir in method_dir.iterdir():
                    if doc_dir.is_dir():
                        # Count images in directory
                        image_count = len(list(doc_dir.glob("*.jpg")))
                        
                        # Load metadata if available
                        metadata_file = doc_dir / "extraction_metadata.json"
                        metadata = {}
                        if metadata_file.exists():
                            try:
                                import json
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                            except:
                                pass
                        
                        extractions[method_name].append({
                            "document_id": doc_dir.name,
                            "image_count": image_count,
                            "metadata": metadata
                        })
        
        return extractions
