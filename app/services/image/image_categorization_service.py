"""
Image Categorization Service

Responsável por categorizar imagens extraídas em header e content.
Mantém toda a lógica de extração intacta, apenas melhora a categorização.
"""
from typing import Dict, Any, List, Tuple
import logging
from app.services.azure.azure_figure_processor import AzureFigureProcessor

logger = logging.getLogger(__name__)


class ImageCategorizationService:
    """
    Serviço especializado para categorização de imagens.
    
    Responsabilidades:
    - Categorizar imagens em header vs content
    - Aplicar heurísticas de posicionamento
    - Fornecer fallbacks robustos
    """
    
    @staticmethod
    def categorize_extracted_images(
        image_data: Dict[str, str], 
        azure_result: Dict[str, Any]
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Categoriza imagens já extraídas em header e content.
        
        Args:
            image_data: Dicionário com figure_id -> base64_string (JÁ EXTRAÍDAS)
            azure_result: Resposta bruta do Azure para obter metadados de posição
            
        Returns:
            Tuple: (header_images, content_images)
        """
        logger.info(f"Starting image categorization for {len(image_data)} extracted images")
        
        header_images = []
        content_images = {}
        
        if not image_data:
            logger.warning("No image data to categorize")
            return header_images, content_images
        
        # Use Azure figure processor for categorization
        if azure_result and 'figures' in azure_result:
            processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
            categorized_figures = AzureFigureProcessor.categorize_figures_by_type(processed_figures)
            
            logger.info(f"Azure processor: {len(processed_figures)} figures processed")
            logger.info(f"Categories: header={len(categorized_figures['header'])}, content={len(categorized_figures['content'])}")
            
            # Use Azure processor categorization
            for figure in processed_figures:
                figure_id = figure['id']
                
                if figure_id in image_data:
                    base64_image = image_data[figure_id]
                    
                    if figure['type'] == 'header':
                        header_images.append({"content": base64_image})
                        logger.info(f"Figure {figure_id} categorized as header")
                    else:
                        content_images[figure_id] = base64_image
                        logger.info(f"Figure {figure_id} categorized as content ({figure['type']})")
                else:
                    logger.warning(f"Figure {figure_id} processed but no base64 image found")
        
        else:
            # Fallback to legacy categorization logic if no Azure data
            logger.warning("Using fallback categorization logic")
            
            # Get figures from Azure result for position metadata
            figures = azure_result.get("figures", [])
            logger.info(f"Found {len(figures)} figures in Azure result")
            
            for figure_id, base64_image in image_data.items():
                # Encontrar metadados correspondentes da figura
                figure_metadata = ImageCategorizationService._find_figure_metadata(figure_id, figures)
                
                # Categorizar baseado nos metadados
                is_header = ImageCategorizationService._categorize_single_image(
                    figure_id, figure_metadata, azure_result
                )
                
                if is_header:
                    header_images.append({"content": base64_image})
                    logger.info(f"✅ FALLBACK: Figure {figure_id} categorized as HEADER image")
                else:
                    content_images[figure_id] = base64_image
                    logger.info(f"✅ FALLBACK: Figure {figure_id} categorized as CONTENT image")
        
        logger.info(f"🎉 RESULT: {len(header_images)} header, {len(content_images)} content images")
        return header_images, content_images
    
    @staticmethod
    def _find_figure_metadata(figure_id: str, figures: List[Dict]) -> Dict:
        """
        Encontra metadados de uma figura pelo ID
        """
        for figure in figures:
            if figure.get("id") == figure_id:
                logger.debug(f"📍 Found metadata for figure {figure_id}")
                return figure
        
        logger.warning(f"❌ No metadata found for figure {figure_id}")
        return {}
    
    @staticmethod
    def _categorize_single_image(
        figure_id: str, 
        figure_metadata: Dict, 
        azure_result: Dict
    ) -> bool:
        """
        Categorize a single image as header or content.
        
        Returns:
            bool: True if header, False if content
        """
        logger.debug(f"Categorizing figure {figure_id}")
        
        # If no metadata, assume content
        if not figure_metadata:
            logger.debug(f"{figure_id}: No metadata -> CONTENT")
            return False
        
        # Check if on first page
        if not ImageCategorizationService._is_on_first_page(figure_metadata):
            logger.debug(f"{figure_id}: Not on first page -> CONTENT")
            return False
        
        # Check vertical position (main heuristic)
        is_top_area = ImageCategorizationService._is_in_top_area(figure_metadata)
        logger.debug(f"{figure_id}: In top area? {is_top_area}")
        
        # Check if near header elements
        near_header_elements = ImageCategorizationService._is_near_header_elements(
            figure_metadata, azure_result
        )
        logger.debug(f"{figure_id}: Near header elements? {near_header_elements}")
        
        # Final decision: top area OR near header elements
        is_header = is_top_area or near_header_elements
        
        logger.info(f"Figure {figure_id} categorized as {'HEADER' if is_header else 'CONTENT'}")
        return is_header
    
    @staticmethod
    def _is_on_first_page(figure_metadata: Dict) -> bool:
        """Check if the figure is on the first page"""
        regions = figure_metadata.get("boundingRegions", [])
        if not regions:
            return False
        
        page_number = regions[0].get("pageNumber", 0)
        return page_number == 1
    
    @staticmethod
    def _is_in_top_area(figure_metadata: Dict, threshold: float = 0.35) -> bool:
        """
        Check if the figure is in the top area of the page (first 35%)
        using boundingRegions with polygon coordinates
        """
        regions = figure_metadata.get("boundingRegions", [])
        if not regions:
            logger.debug("No boundingRegions found")
            return False
        
        # Use first region (usually only one per figure)
        region = regions[0]
        polygon = region.get("polygon", [])
        page_number = region.get("pageNumber", 1)
        
        if not polygon or len(polygon) < 8:  # Need at least 4 points (x,y) = 8 values
            logger.debug("Invalid polygon data")
            return False
        
        # Extract Y coordinates from polygon (odd values in array)
        # Polygon format: [x1, y1, x2, y2, x3, y3, x4, y4]
        y_values = [polygon[i] for i in range(1, len(polygon), 2)]
        
        # Calculate average and minimum Y position
        avg_y = sum(y_values) / len(y_values)
        min_y = min(y_values)
        
        # Check if on first page AND in top area
        is_first_page = page_number == 1
        is_top = min_y < threshold  # Use minimum position (top) of figure
        
        logger.debug(f"Page: {page_number}, Y avg: {avg_y:.3f}, Y min: {min_y:.3f}, threshold: {threshold}")
        logger.debug(f"First page: {is_first_page}, Is top: {is_top}")
        
        # Be header if on first page AND in top area
        return is_first_page and is_top
    
    @staticmethod
    def _is_near_header_elements(figure_metadata: Dict, azure_result: Dict) -> bool:
        """
        Check if the figure is near elements identified as header
        """
        # Look for paragraphs with role="pageHeader"
        header_paragraphs = [
            para for para in azure_result.get("paragraphs", [])
            if para.get("role") == "pageHeader"
        ]
        
        if not header_paragraphs:
            logger.debug("No pageHeader paragraphs found")
            return False
        
        # Check span overlap
        figure_spans = figure_metadata.get("spans", [])
        if not figure_spans:
            logger.debug("Figure has no spans")
            return False
        
        for f_span in figure_spans:
            f_offset = f_span.get("offset", 0)
            f_length = f_span.get("length", 0)
            f_end = f_offset + f_length
            
            for header_para in header_paragraphs:
                for h_span in header_para.get("spans", []):
                    h_offset = h_span.get("offset", 0)
                    h_length = h_span.get("length", 0)
                    h_end = h_offset + h_length
                    
                    # Check for overlap
                    if f_offset <= h_end and f_end >= h_offset:
                        logger.debug("Found span overlap with header element")
                        return True
        
        logger.debug("No span overlap with header elements")
        return False
    
    @staticmethod
    def force_categorize_as_header(image_data: Dict[str, str]) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Force all images to be categorized as header (for testing).
        """
        logger.warning("FORCE MODE: Categorizing all images as header")
        
        header_images = []
        content_images = {}
        
        for figure_id, base64_image in image_data.items():
            header_images.append({"content": base64_image})
            logger.info(f"FORCED: Figure {figure_id} -> HEADER")
        
        return header_images, content_images
    
    @staticmethod
    def debug_categorization_data(image_data: Dict[str, str], azure_result: Dict[str, Any]):
        """
        Complete debug method for categorization data
        """
        logger.info("DEBUG CATEGORIZATION DATA:")
        logger.info(f"Images to categorize: {len(image_data)}")
        
        figures = azure_result.get("figures", [])
        logger.info(f"Azure figures: {len(figures)}")
        
        paragraphs = azure_result.get("paragraphs", [])
        header_paras = [p for p in paragraphs if p.get("role") == "pageHeader"]
        logger.info(f"Header paragraphs: {len(header_paras)}")
        
        for figure_id in image_data.keys():
            figure_meta = ImageCategorizationService._find_figure_metadata(figure_id, figures)
            if figure_meta:
                regions = figure_meta.get("boundingRegions", [])
                if regions:
                    polygon = regions[0].get("polygon", [])
                    if polygon:
                        y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
                        avg_y = sum(y_values) / len(y_values) if y_values else 0
                        logger.info(f"{figure_id}: page={regions[0].get('pageNumber')}, y_avg={avg_y:.3f}")
                    else:
                        logger.info(f"{figure_id}: no polygon data")
                else:
                    logger.info(f"{figure_id}: no bounding regions")
            else:
                logger.info(f"{figure_id}: no metadata found")
