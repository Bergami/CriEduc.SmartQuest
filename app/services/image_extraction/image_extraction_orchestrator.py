"""
Image extraction factory and orchestrator.
Manages different image extraction strategies and provides comparison capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import UploadFile
from enum import Enum

from app.services.image_extraction.base_image_extractor import BaseImageExtractor
from app.services.image_extraction.azure_figures_extractor import AzureFiguresImageExtractor
from app.services.image_extraction.manual_pdf_extractor import ManualPDFImageExtractor
from app.services.utils.image_saving_service import ImageSavingService
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class ImageExtractionMethod(Enum):
    """Available image extraction methods."""
    AZURE_FIGURES = "azure_figures"
    MANUAL_PDF = "manual_pdf"


class ImageExtractionOrchestrator:
    """
    Orchestrates different image extraction strategies.
    
    This class provides:
    - Strategy selection
    - Performance comparison
    - Fallback mechanisms
    - Metrics collection
    """
    
    def __init__(self):
        self._extractors = {
            ImageExtractionMethod.AZURE_FIGURES: AzureFiguresImageExtractor(),
            ImageExtractionMethod.MANUAL_PDF: ManualPDFImageExtractor()
        }
        
        # Initialize image saving service
        self.image_saver = ImageSavingService()
        
        self._comparison_results = []
    
    async def extract_images_single_method(
        self,
        method: ImageExtractionMethod,
        file: UploadFile,
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract images using a single method.
        
        Args:
            method: The extraction method to use
            file: The uploaded PDF file
            document_analysis_result: The result from document analysis
            document_id: Optional document identifier
            
        Returns:
            Dictionary mapping figure IDs to base64 encoded images
        """
        if method not in self._extractors:
            raise DocumentProcessingError(f"Unknown extraction method: {method.value}")
        
        extractor = self._extractors[method]
        logger.info(f"🔧 Using extraction method: {extractor.get_extraction_method_name()}")
        
        return await extractor.extract_images(file, document_analysis_result, document_id)
    
    async def extract_images_with_comparison(
        self,
        file: UploadFile,
        document_analysis_result: Dict[str, Any],
        document_id: Optional[str] = None,
        methods: Optional[List[ImageExtractionMethod]] = None
    ) -> Dict[str, Any]:
        """
        Extract images using multiple methods for comparison.
        
        Args:
            file: The uploaded PDF file
            document_analysis_result: The result from document analysis
            document_id: Optional document identifier
            methods: List of methods to compare (default: all methods)
            
        Returns:
            Dictionary with results from each method and comparison data
        """
        if methods is None:
            methods = list(ImageExtractionMethod)
        
        logger.info(f"🔄 Starting image extraction comparison with {len(methods)} methods...")
        
        results = {
            "extraction_results": {},
            "performance_metrics": {},
            "comparison_summary": {}
        }
        
        # Extract with each method
        for method in methods:
            try:
                logger.info(f"🔧 Testing method: {method.value}")
                
                # Reset file position before each extraction
                await file.seek(0)
                
                # Extract images
                images = await self.extract_images_single_method(
                    method, file, document_analysis_result, document_id
                )
                
                # Get performance metrics
                extractor = self._extractors[method]
                metrics = extractor.get_performance_metrics()
                
                # Store results
                results["extraction_results"][method.value] = images
                results["performance_metrics"][method.value] = metrics
                
                logger.info(f"✅ Method {method.value}: {len(images)} images extracted")
                
            except Exception as e:
                logger.error(f"❌ Method {method.value} failed: {str(e)}")
                results["extraction_results"][method.value] = {}
                results["performance_metrics"][method.value] = {
                    "error": str(e),
                    "success_rate": 0.0
                }
        
        # Generate comparison summary
        results["comparison_summary"] = self._generate_comparison_summary(results)
        
        # Save comparison results to disk if document_id is provided
        if document_id:
            try:
                saved_path = self.image_saver.save_comparison_results(
                    comparison_data=results,
                    document_id=document_id,
                    filename=getattr(file, 'filename', 'unknown'),
                    email="comparison_extraction"
                )
                logger.info(f"💾 Comparison results saved to: {saved_path}")
                results["comparison_saved_path"] = saved_path
            except Exception as e:
                logger.warning(f"⚠️  Could not save comparison results: {str(e)}")
        
        # Store for historical analysis
        self._comparison_results.append(results)
        
        logger.info("🎉 Image extraction comparison completed")
        return results
    
    def _generate_comparison_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary comparing the different extraction methods."""
        summary = {
            "total_methods_tested": len(results["extraction_results"]),
            "successful_methods": 0,
            "method_comparison": {},
            "recommendations": []
        }
        
        # Analyze each method
        for method, images in results["extraction_results"].items():
            metrics = results["performance_metrics"].get(method, {})
            
            method_summary = {
                "images_extracted": len(images) if images else 0,
                "success": len(images) > 0 if images else False,
                "performance": metrics
            }
            
            if method_summary["success"]:
                summary["successful_methods"] += 1
            
            summary["method_comparison"][method] = method_summary
        
        # Generate recommendations
        if summary["successful_methods"] == 0:
            summary["recommendations"].append("No extraction methods succeeded. Check document format and configuration.")
        elif summary["successful_methods"] == 1:
            successful_method = next(
                method for method, data in summary["method_comparison"].items() 
                if data["success"]
            )
            summary["recommendations"].append(f"Only {successful_method} succeeded. Consider using it as primary method.")
        else:
            # Compare methods that succeeded
            best_method = self._determine_best_method(summary["method_comparison"])
            summary["recommendations"].append(f"Multiple methods succeeded. {best_method} appears to be the best option.")
        
        return summary
    
    def _determine_best_method(self, method_comparison: Dict[str, Any]) -> str:
        """Determine the best method based on success rate and performance."""
        best_method = None
        best_score = -1
        
        for method, data in method_comparison.items():
            if not data["success"]:
                continue
            
            # Simple scoring: number of images + success rate
            score = data["images_extracted"]
            
            performance = data.get("performance", {})
            if performance.get("success_rate", 0) > 0:
                score += performance["success_rate"] * 10  # Weight success rate
            
            if score > best_score:
                best_score = score
                best_method = method
        
        return best_method or "unknown"
    
    def get_available_methods(self) -> List[str]:
        """Get list of available extraction methods."""
        return [method.value for method in ImageExtractionMethod]
    
    def get_historical_comparison_data(self) -> List[Dict[str, Any]]:
        """Get historical comparison results for analysis."""
        return self._comparison_results.copy()
    
    def clear_comparison_history(self):
        """Clear historical comparison data."""
        self._comparison_results.clear()
        logger.info("🗑️  Comparison history cleared")
