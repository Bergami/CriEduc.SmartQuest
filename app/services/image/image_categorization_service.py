"""
🆕 ImageCategorizationService - Versão 100% Pydantic

Serviço simplificado para categorização de imagens extraídas usando apenas Pydantic.
Substitui a versão legacy sem compatibilidade retroativa.

Implementa ImageCategorizationInterface para aplicar DIP (Dependency Inversion Principle).
"""
import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime

from app.models.internal.image_models import InternalImageData, ImageCategory, ImagePosition, ExtractionMetadata
from app.services.image.interfaces.image_categorization_interface import ImageCategorizationInterface

logger = logging.getLogger(__name__)


class ImageCategorizationService(ImageCategorizationInterface):
    """
    🆕 Serviço 100% Pydantic para categorização de imagens.
    
    Remove toda compatibilidade legacy, focando em type safety e estruturas Pydantic.
    Substitui o serviço antigo que retornava Dict.
    """
    
    @staticmethod
    def categorize_extracted_images(
        image_data: Dict[str, str], 
        azure_result: Dict[str, Any], 
        document_id: str = "unknown"
    ) -> Tuple[List[InternalImageData], List[InternalImageData]]:
        """
        🆕 Categoriza imagens extraídas em header e content (100% Pydantic).
        
        Args:
            image_data: Dicionário {figure_id: base64_data}
            azure_result: Response completo do Azure Document Intelligence
            document_id: ID do documento para tracking
            
        Returns:
            Tuple[List[InternalImageData], List[InternalImageData]]: (header_images, content_images)
        """
        logger.info(f"🆕 Starting PURE PYDANTIC image categorization for {len(image_data)} extracted images")
        
        header_images: List[InternalImageData] = []
        content_images: List[InternalImageData] = []
        
        # Processar Azure figures
        figures = azure_result.get("figures", [])
        logger.info(f"Processando {len(figures)} figuras do Azure")
        
        # Usar processamento Azure para categorização
        azure_processor = ImageCategorizationService._get_azure_processor()
        processed_figures_list = azure_processor.process_figures_from_azure_response(azure_result)
        logger.info(f"Figuras processadas: {len(processed_figures_list)}")
        
        # Converter lista em dict para facilitar acesso
        processed_figures = {}
        for fig in processed_figures_list:
            figure_id = fig.get("id")
            figure_type = fig.get("type", "content")
            if figure_id:
                processed_figures[figure_id] = figure_type
        
        header_count = sum(1 for cat in processed_figures.values() if cat == "header")
        content_count = len(processed_figures) - header_count
        logger.info(f"Azure processor: {len(processed_figures)} figures processed")
        logger.info(f"Categories: header={header_count}, content={content_count}")
        
        # Categorizar cada imagem baseado no processamento Azure
        for figure_id, base64_data in image_data.items():
            try:
                # Verificar categoria do Azure processor
                category_str = processed_figures.get(figure_id, "content")
                category = ImageCategory.HEADER if category_str == "header" else ImageCategory.CONTENT
                
                # Encontrar metadata da figura no Azure
                azure_figure_metadata = ImageCategorizationService._find_figure_metadata(figure_id, figures)
                
                # Criar objeto InternalImageData
                image_obj = ImageCategorizationService._create_internal_image_data(
                    figure_id=figure_id,
                    base64_data=base64_data,
                    category=category,
                    azure_figure_metadata=azure_figure_metadata,
                    document_id=document_id
                )
                
                # Adicionar à lista apropriada
                if category == ImageCategory.HEADER:
                    header_images.append(image_obj)
                    logger.info(f"✅ Figure {figure_id} categorized as HEADER (Pydantic)")
                else:
                    content_images.append(image_obj)
                    logger.info(f"✅ Figure {figure_id} categorized as CONTENT (Pydantic)")
                    
            except Exception as e:
                logger.error(f"❌ Error processing figure {figure_id}: {e}")
                # Em caso de erro, tratar como content
                image_obj = ImageCategorizationService._create_fallback_image_data(
                    figure_id, base64_data, document_id
                )
                content_images.append(image_obj)
        
        logger.info(f"🎉 PURE PYDANTIC RESULT: {len(header_images)} header, {len(content_images)} content images")
        return header_images, content_images
    
    @staticmethod
    def _create_internal_image_data(
        figure_id: str, 
        base64_data: str, 
        category: ImageCategory,
        azure_figure_metadata: Dict[str, Any],
        document_id: str
    ) -> InternalImageData:
        """Cria objeto InternalImageData com metadata completa."""
        
        # Extrair posição do metadata Azure
        position = ImageCategorizationService._extract_position_from_metadata(azure_figure_metadata)
        
        # Extrair página
        page = ImageCategorizationService._extract_page_from_metadata(azure_figure_metadata)
        
        return InternalImageData(
            id=figure_id,
            file_path=f"{document_id}_{figure_id}.png",  # Campo obrigatório
            base64_data=base64_data,
            category=category,
            page=page,
            position=position,
            created_at=datetime.now(),
            processing_notes=f"Categorized as {category.value} via Pure Pydantic Service"
        )
    
    @staticmethod
    def _create_fallback_image_data(figure_id: str, base64_data: str, document_id: str) -> InternalImageData:
        """Cria objeto InternalImageData básico para casos de erro."""
        return InternalImageData(
            id=figure_id,
            file_path=f"{document_id}_{figure_id}_fallback.png",  # Campo obrigatório
            base64_data=base64_data,
            category=ImageCategory.CONTENT,  # Default para content em caso de erro
            page=1,
            position=None,
            created_at=datetime.now(),
            processing_notes=f"Fallback processing due to categorization error"
        )
    
    @staticmethod
    def _extract_position_from_metadata(azure_figure_metadata: Dict[str, Any]) -> ImagePosition:
        """Extrai posição do metadata Azure."""
        if not azure_figure_metadata:
            return None
            
        bounding_regions = azure_figure_metadata.get("boundingRegions", [])
        if not bounding_regions:
            return None
            
        region = bounding_regions[0]
        polygon = region.get("polygon", [])
        
        if len(polygon) >= 8:  # Mínimo para um retângulo
            x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
            y_coords = [polygon[i] for i in range(1, len(polygon), 2)]
            
            return ImagePosition(
                x=min(x_coords),
                y=min(y_coords),
                width=max(x_coords) - min(x_coords),
                height=max(y_coords) - min(y_coords)
            )
        
        return None
    
    @staticmethod
    def _extract_page_from_metadata(azure_figure_metadata: Dict[str, Any]) -> int:
        """Extrai número da página do metadata Azure."""
        if not azure_figure_metadata:
            return 1
            
        bounding_regions = azure_figure_metadata.get("boundingRegions", [])
        if bounding_regions:
            return bounding_regions[0].get("pageNumber", 1)
            
        return 1
    
    @staticmethod
    def _find_figure_metadata(figure_id: str, figures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Encontra metadata de uma figura específica."""
        for figure in figures:
            if figure.get("id") == figure_id:
                return figure
        return {}
    
    @staticmethod
    def _get_azure_processor():
        """Retorna instância do processador Azure."""
        from app.services.azure.azure_figure_processor import AzureFigureProcessor
        return AzureFigureProcessor()
