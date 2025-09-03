"""
Image Categorization Service - Pydantic Version

Versão moderna que retorna objetos Pydantic em vez de dicionários.
Após validação completa, substituirá ImageCategorizationService.
"""
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime

from app.models.internal.image_models import (
    InternalImageData, 
    ImageCategory, 
    ImagePosition, 
    ExtractionMetadata,
    ImageProcessingStatus
)
from .azure_figure_processor import AzureFigureProcessor

logger = logging.getLogger(__name__)


class ImageCategorizationServicePydantic:
    """
    🆕 Versão Pydantic do serviço de categorização de imagens.
    
    Responsabilidades:
    - Categorizar imagens em header vs content
    - Retornar objetos InternalImageData completos
    - Manter compatibilidade com lógica existente
    - Fornecer type safety completa
    """
    
    @staticmethod
    def categorize_extracted_images_pydantic(
        image_data: Dict[str, str], 
        azure_result: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Tuple[List[InternalImageData], List[InternalImageData]]:
        """
        🆕 VERSÃO PYDANTIC - Categoriza imagens e retorna objetos tipados.
        
        Args:
            image_data: Dicionário com figure_id -> base64_string (JÁ EXTRAÍDAS)
            azure_result: Resposta bruta do Azure para obter metadados de posição
            document_id: ID do documento (opcional, para rastreamento)
            
        Returns:
            Tuple: (header_images: List[InternalImageData], content_images: List[InternalImageData])
        """
        logger.info(f"🆕 Starting PYDANTIC image categorization for {len(image_data)} extracted images")
        
        header_images = []
        content_images = []
        
        if not image_data:
            logger.warning("No image data to categorize")
            return header_images, content_images
        
        # Use Azure figure processor for categorization (igual ao método legacy)
        if azure_result and 'figures' in azure_result:
            processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
            categorized_figures = AzureFigureProcessor.categorize_figures_by_type(processed_figures)
            
            logger.info(f"Azure processor: {len(processed_figures)} figures processed")
            logger.info(f"Categories: header={len(categorized_figures['header'])}, content={len(categorized_figures['content'])}")
            
            # Use Azure processor categorization - mas criar objetos Pydantic
            for figure in processed_figures:
                figure_id = figure['id']
                
                if figure_id in image_data:
                    base64_image = image_data[figure_id]
                    
                    # 🆕 Criar objeto InternalImageData em vez de Dict
                    image_obj = ImageCategorizationServicePydantic._create_internal_image_data(
                        figure_id=figure_id,
                        base64_data=base64_image,
                        azure_figure_metadata=figure,
                        is_header=(figure['type'] == 'header'),
                        document_id=document_id
                    )
                    
                    if figure['type'] == 'header':
                        header_images.append(image_obj)
                        logger.info(f"✅ Figure {figure_id} categorized as HEADER (Pydantic)")
                    else:
                        content_images.append(image_obj)
                        logger.info(f"✅ Figure {figure_id} categorized as CONTENT (Pydantic)")
                else:
                    logger.warning(f"Figure {figure_id} processed but no base64 image found")
        
        else:
            # Fallback to legacy categorization logic - mas retornar Pydantic
            logger.warning("Using fallback categorization logic (Pydantic)")
            
            # Get figures from Azure result for position metadata
            figures = azure_result.get("figures", [])
            logger.info(f"Found {len(figures)} figures in Azure result")
            
            for figure_id, base64_image in image_data.items():
                # Encontrar metadados correspondentes da figura
                figure_metadata = ImageCategorizationServicePydantic._find_figure_metadata(figure_id, figures)
                
                # Categorizar baseado nos metadados (mesma lógica)
                is_header = ImageCategorizationServicePydantic._categorize_single_image(
                    figure_id, figure_metadata, azure_result
                )
                
                # 🆕 Criar objeto InternalImageData
                image_obj = ImageCategorizationServicePydantic._create_internal_image_data(
                    figure_id=figure_id,
                    base64_data=base64_image,
                    azure_figure_metadata=figure_metadata,
                    is_header=is_header,
                    document_id=document_id
                )
                
                if is_header:
                    header_images.append(image_obj)
                    logger.info(f"✅ FALLBACK: Figure {figure_id} categorized as HEADER (Pydantic)")
                else:
                    content_images.append(image_obj)
                    logger.info(f"✅ FALLBACK: Figure {figure_id} categorized as CONTENT (Pydantic)")
        
        logger.info(f"🎉 PYDANTIC RESULT: {len(header_images)} header, {len(content_images)} content images")
        return header_images, content_images
    
    @staticmethod
    def _create_internal_image_data(
        figure_id: str,
        base64_data: str,
        azure_figure_metadata: Dict[str, Any],
        is_header: bool,
        document_id: Optional[str] = None
    ) -> InternalImageData:
        """
        🆕 Cria objeto InternalImageData completo a partir dos metadados do Azure.
        
        Args:
            figure_id: ID da figura
            base64_data: Dados base64 da imagem
            azure_figure_metadata: Metadados da figura do Azure
            is_header: Se é imagem de header ou content
            document_id: ID do documento (opcional)
            
        Returns:
            InternalImageData completo com coordenadas e metadados
        """
        # Determinar categoria
        category = ImageCategory.HEADER if is_header else ImageCategory.CONTENT
        
        # Extrair posição das coordenadas do Azure
        position = ImageCategorizationServicePydantic._extract_position_from_metadata(azure_figure_metadata)
        
        # Extrair página
        page = ImageCategorizationServicePydantic._extract_page_from_metadata(azure_figure_metadata)
        
        # Criar metadados de extração
        extraction_metadata = ExtractionMetadata(
            source="azure_document_intelligence",
            bounding_regions=azure_figure_metadata.get("boundingRegions"),
            confidence=azure_figure_metadata.get("confidence"),
            processing_notes=f"Categorized as {category.value} via ImageCategorizationServicePydantic"
        )
        
        # Criar objeto InternalImageData completo
        return InternalImageData(
            id=figure_id,
            file_path=f"extracted_images/{document_id or 'unknown'}/{figure_id}.png",
            base64_data=base64_data,
            page=page,
            position=position,
            azure_coordinates=ImageCategorizationServicePydantic._extract_polygon_from_metadata(azure_figure_metadata),
            extraction_metadata=extraction_metadata,
            category=category,
            processing_status=ImageProcessingStatus.COMPLETED,
            confidence_score=azure_figure_metadata.get("confidence", 0.95),
            processing_notes=f"Processed by ImageCategorizationServicePydantic at {datetime.now().isoformat()}",
            created_at=datetime.now()
        )
    
    @staticmethod
    def _extract_position_from_metadata(azure_figure_metadata: Dict[str, Any]) -> Optional[ImagePosition]:
        """
        Extrai ImagePosition dos metadados do Azure.
        
        Converte boundingRegions.polygon para coordenadas retangulares.
        """
        regions = azure_figure_metadata.get("boundingRegions", [])
        if not regions:
            return None
        
        region = regions[0]
        polygon = region.get("polygon", [])
        
        if not polygon or len(polygon) < 8:  # Precisa de pelo menos 4 pontos (x,y)
            return None
        
        # Extrair coordenadas do polígono
        # Formato: [x1, y1, x2, y2, x3, y3, x4, y4]
        x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
        y_coords = [polygon[i] for i in range(1, len(polygon), 2)]
        
        # Calcular retângulo envolvente
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return ImagePosition(
            x=x_min,
            y=y_min,
            width=x_max - x_min,
            height=y_max - y_min
        )
    
    @staticmethod
    def _extract_page_from_metadata(azure_figure_metadata: Dict[str, Any]) -> int:
        """Extrai número da página dos metadados do Azure."""
        regions = azure_figure_metadata.get("boundingRegions", [])
        if regions:
            return regions[0].get("pageNumber", 1)
        return 1
    
    @staticmethod
    def _extract_polygon_from_metadata(azure_figure_metadata: Dict[str, Any]) -> Optional[List[float]]:
        """Extrai coordenadas do polígono dos metadados do Azure."""
        regions = azure_figure_metadata.get("boundingRegions", [])
        if regions:
            return regions[0].get("polygon")
        return None
    
    # ======== MÉTODOS LEGACY REUTILIZADOS ========
    # (Mesma lógica do ImageCategorizationService original)
    
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
        if not ImageCategorizationServicePydantic._is_on_first_page(figure_metadata):
            logger.debug(f"{figure_id}: Not on first page -> CONTENT")
            return False
        
        # Check vertical position (main heuristic)
        is_top_area = ImageCategorizationServicePydantic._is_in_top_area(figure_metadata)
        logger.debug(f"{figure_id}: In top area? {is_top_area}")
        
        # Check if near header elements
        near_header_elements = ImageCategorizationServicePydantic._is_near_header_elements(
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
    
    # ======== MÉTODOS DE COMPATIBILIDADE ========
    
    @staticmethod
    def to_legacy_format(
        header_images: List[InternalImageData], 
        content_images: List[InternalImageData]
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        🔄 Converte resultado Pydantic para formato legacy (para testes de comparação).
        
        Returns:
            Tuple no formato esperado pelo sistema legacy
        """
        header_legacy = [{"content": img.base64_data} for img in header_images]
        content_legacy = {img.id: img.base64_data for img in content_images}
        
        return header_legacy, content_legacy
    
    @staticmethod
    def compare_with_legacy(
        image_data: Dict[str, str], 
        azure_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🧪 Compara resultados entre versão legacy e Pydantic para validação.
        
        Returns:
            Relatório de comparação detalhado
        """
        from .image_categorization_service import ImageCategorizationService
        
        # Executar versão legacy
        legacy_header, legacy_content = ImageCategorizationService.categorize_extracted_images(
            image_data, azure_result
        )
        
        # Executar versão Pydantic
        pydantic_header, pydantic_content = ImageCategorizationServicePydantic.categorize_extracted_images_pydantic(
            image_data, azure_result
        )
        
        # Converter Pydantic para formato legacy para comparação
        pydantic_header_legacy, pydantic_content_legacy = ImageCategorizationServicePydantic.to_legacy_format(
            pydantic_header, pydantic_content
        )
        
        # Comparar resultados
        header_match = legacy_header == pydantic_header_legacy
        content_match = legacy_content == pydantic_content_legacy
        
        return {
            "test_images": len(image_data),
            "legacy_results": {
                "header_count": len(legacy_header),
                "content_count": len(legacy_content)
            },
            "pydantic_results": {
                "header_count": len(pydantic_header),
                "content_count": len(pydantic_content)
            },
            "comparison": {
                "header_match": header_match,
                "content_match": content_match,
                "results_identical": header_match and content_match
            },
            "pydantic_advantages": {
                "type_safety": True,
                "position_data": len([img for img in pydantic_header + pydantic_content if img.position is not None]),
                "metadata_richness": True,
                "validation_built_in": True
            }
        }
