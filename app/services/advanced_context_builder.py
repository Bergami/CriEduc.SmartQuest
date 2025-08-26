"""
Advanced Context Block Builder with Text-Figure Association
Handles associating descriptive texts with their corresponding figures based on spatial proximity
"""
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from dataclasses import dataclass

from app.core.constants.instruction_patterns import InstructionPatterns, InstructionPattern
from app.core.constants.content_types import (
    ContentType, FigureType, TextRole, ContextBlockType, InstructionType,
    get_content_type_from_string, get_figure_type_from_content
)

logger = logging.getLogger(__name__)

@dataclass
class TextSpan:
    """Represents a text span with position information"""
    content: str
    offset: int
    length: int
    page_number: int
    bounding_regions: List[Dict] = None

@dataclass
class FigureInfo:
    """Enhanced figure information with spatial data"""
    id: str
    page_number: int
    bounding_regions: List[Dict]
    base64_image: Optional[str] = None
    associated_texts: List[TextSpan] = None
    figure_type: FigureType = FigureType.UNKNOWN
    content_type: ContentType = ContentType.UNKNOWN
    
    def __post_init__(self):
        if self.associated_texts is None:
            self.associated_texts = []

class AdvancedContextBlockBuilder:
    """
    Advanced context block builder that associates texts with figures
    and creates comprehensive context blocks with images
    """
    
    def __init__(self):
        self.instruction_patterns = InstructionPatterns()
        self.content_type_keywords = {
            ContentType.CHARGE: ['charge', 'tirinha', 'quadrinho', 'cartoon', 'comic'],
            ContentType.PROPAGANDA: ['propaganda', 'anúncio', 'advertisement', 'ad', 'publicidade'],
            ContentType.DIALOGUE: ['disse', 'falou', 'respondeu', 'perguntou', '!', '?'],
            ContentType.TITLE: ['texto', 'título', 'title'],
            ContentType.INSTRUCTION: ['analise', 'observe', 'leia', 'responda']
        }
    
    def build_enhanced_context_blocks(
        self, 
        azure_response: Dict,
        images_base64: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Build context blocks with associated texts and images
        
        Args:
            azure_response: Azure Document Intelligence response
            images_base64: Dictionary mapping figure IDs to base64 strings
            
        Returns:
            List of enhanced context blocks with associated texts and images
        """
        try:
            logger.info("🔧 BUILDING ENHANCED CONTEXT BLOCKS")
            
            # Extract figures and text spans
            figures = self._extract_figures_with_spatial_info(azure_response)
            text_spans = self._extract_text_spans_with_position(azure_response)
            
            # Associate texts with figures
            self._associate_texts_with_figures(figures, text_spans)
            
            # Add base64 images to figures
            self._add_base64_images_to_figures(figures, images_base64)
            
            # Build context blocks
            context_blocks = self._build_context_blocks_from_figures(figures)
            
            logger.info(f"✅ Built {len(context_blocks)} enhanced context blocks")
            return context_blocks
            
        except Exception as e:
            logger.error(f"❌ Error building enhanced context blocks: {str(e)}")
            return []
    
    def _extract_figures_with_spatial_info(self, azure_response: Dict) -> List[FigureInfo]:
        """Extract figures with their spatial information"""
        figures = []
        
        azure_figures = azure_response.get('figures', [])
        logger.info(f"📊 Extracting {len(azure_figures)} figures with spatial info")
        
        for figure in azure_figures:
            figure_id = figure.get('id', '')
            bounding_regions = figure.get('boundingRegions', [])
            
            if not bounding_regions:
                continue
                
            # Get page number from first bounding region
            page_number = bounding_regions[0].get('pageNumber', 1)
            
            figures.append(FigureInfo(
                id=figure_id,
                page_number=page_number,
                bounding_regions=bounding_regions
            ))
        
        logger.info(f"✅ Extracted {len(figures)} figures with spatial data")
        return figures
    
    def _extract_text_spans_with_position(self, azure_response: Dict) -> List[TextSpan]:
        """Extract text spans with their position information"""
        text_spans = []
        
        # Extract from paragraphs (more accurate positioning)
        paragraphs = azure_response.get('paragraphs', [])
        logger.info(f"📝 Extracting text spans from {len(paragraphs)} paragraphs")
        
        for paragraph in paragraphs:
            content = paragraph.get('content', '').strip()
            if not content:
                continue
            
            # Get span information
            spans = paragraph.get('spans', [])
            if not spans:
                continue
                
            span = spans[0]  # Use first span
            offset = span.get('offset', 0)
            length = span.get('length', len(content))
            
            # Get bounding regions for positioning
            bounding_regions = paragraph.get('boundingRegions', [])
            page_number = 1
            if bounding_regions:
                page_number = bounding_regions[0].get('pageNumber', 1)
            
            # Filter relevant texts
            if self._is_relevant_text_for_figures(content):
                text_spans.append(TextSpan(
                    content=content,
                    offset=offset,
                    length=length,
                    page_number=page_number,
                    bounding_regions=bounding_regions
                ))
        
        logger.info(f"✅ Extracted {len(text_spans)} relevant text spans")
        return text_spans
    
    def _is_relevant_text_for_figures(self, content: str) -> bool:
        """Check if text content is relevant for figure association"""
        content_clean = content.strip().upper()
        
        # Check for instruction patterns
        for pattern in self.instruction_patterns.get_all_patterns():
            if pattern.compiled.search(content_clean):
                return True
        
        # Check for content type keywords
        for content_type, keywords in self.content_type_keywords.items():
            if any(keyword.upper() in content_clean for keyword in keywords):
                return True
        
        # Check for dialogue patterns (uppercase sentences with punctuation)
        if re.match(r'^[A-ZÁÀÃÊÔÇ\s,!?.-]+[!?.]$', content_clean) and len(content_clean) > 10:
            return True
            
        # Check for brand names (all caps, short)
        if re.match(r'^[A-Z]{2,}\s*[A-Z]*$', content_clean) and len(content_clean) <= 15:
            return True
            
        # Check for captions/metadata
        if re.match(r'^\d+\.\d+$|^FOTO\s+[A-Z]$|^CIERRE$', content_clean):
            return True
            
        return False
    
    def _associate_texts_with_figures(self, figures: List[FigureInfo], text_spans: List[TextSpan]):
        """Associate text spans with figures based on spatial proximity"""
        logger.info(f"🔗 Associating {len(text_spans)} text spans with {len(figures)} figures")
        
        for text_span in text_spans:
            best_figure = self._find_closest_figure(text_span, figures)
            if best_figure:
                best_figure.associated_texts.append(text_span)
                logger.debug(f"   📎 Associated '{text_span.content[:30]}...' with figure {best_figure.id}")
    
    def _find_closest_figure(self, text_span: TextSpan, figures: List[FigureInfo]) -> Optional[FigureInfo]:
        """Find the closest figure to a text span based on spatial proximity"""
        if not text_span.bounding_regions:
            return None
            
        text_regions = text_span.bounding_regions
        text_page = text_span.page_number
        
        best_figure = None
        min_distance = float('inf')
        
        # Only consider figures on the same page
        page_figures = [f for f in figures if f.page_number == text_page]
        
        for figure in page_figures:
            if not figure.bounding_regions:
                continue
                
            distance = self._calculate_spatial_distance(text_regions, figure.bounding_regions)
            if distance < min_distance:
                min_distance = distance
                best_figure = figure
        
        # Only associate if distance is reasonable (within same page area)
        if min_distance < 2.0:  # Threshold for reasonable proximity
            return best_figure
            
        return None
    
    def _calculate_spatial_distance(
        self, 
        text_regions: List[Dict], 
        figure_regions: List[Dict]
    ) -> float:
        """Calculate spatial distance between text and figure regions"""
        if not text_regions or not figure_regions:
            return float('inf')
        
        # Use first regions for simplicity
        text_region = text_regions[0]
        figure_region = figure_regions[0]
        
        # Get polygon points
        text_polygon = text_region.get('polygon', [])
        figure_polygon = figure_region.get('polygon', [])
        
        if len(text_polygon) < 8 or len(figure_polygon) < 8:
            return float('inf')
        
        # Calculate center points
        text_center_x = sum(text_polygon[i] for i in range(0, len(text_polygon), 2)) / 4
        text_center_y = sum(text_polygon[i] for i in range(1, len(text_polygon), 2)) / 4
        
        figure_center_x = sum(figure_polygon[i] for i in range(0, len(figure_polygon), 2)) / 4
        figure_center_y = sum(figure_polygon[i] for i in range(1, len(figure_polygon), 2)) / 4
        
        # Calculate Euclidean distance
        distance = ((text_center_x - figure_center_x) ** 2 + (text_center_y - figure_center_y) ** 2) ** 0.5
        
        return distance
    
    def _add_base64_images_to_figures(self, figures: List[FigureInfo], images_base64: Dict[str, str]):
        """Add base64 images to figures"""
        logger.info(f"🖼️  Adding base64 images to figures")
        
        for figure in figures:
            if figure.id in images_base64:
                figure.base64_image = images_base64[figure.id]
                logger.debug(f"   ✅ Added base64 image to figure {figure.id}")
            else:
                logger.debug(f"   ❌ No base64 image found for figure {figure.id}")
    
    def _build_context_blocks_from_figures(self, figures: List[FigureInfo]) -> List[Dict[str, Any]]:
        """Build context blocks from figures with associated texts"""
        context_blocks = []
        
        # Group figures by type and content
        figure_groups = self._group_figures_by_context(figures)
        
        for group_name, group_figures in figure_groups.items():
            if not group_figures:
                continue
                
            context_block = self._create_context_block_from_group(group_name, group_figures)
            if context_block:
                context_blocks.append(context_block)
        
        return context_blocks
    
    def _group_figures_by_context(self, figures: List[FigureInfo]) -> Dict[str, List[FigureInfo]]:
        """Group figures by their context (TEXTO I, II, III, IV, etc.)"""
        groups = {
            'TEXTO I': [],
            'TEXTO II': [],
            'TEXTO III': [],
            'TEXTO IV': [],
            'OTHER': []
        }
        
        for figure in figures:
            # Check associated texts for TEXTO patterns
            grupo_encontrado = False
            
            for text_span in figure.associated_texts:
                match = self.text_patterns['subtitle'].match(text_span.content)
                if match:
                    # Extract group from TEXTO I, II, III, IV
                    texto_match = re.search(r'TEXTO\s+([IVX]+)', text_span.content, re.IGNORECASE)
                    if texto_match:
                        roman_num = texto_match.group(1)
                        group_key = f'TEXTO {roman_num}'
                        if group_key in groups:
                            groups[group_key].append(figure)
                            grupo_encontrado = True
                            break
            
            if not grupo_encontrado:
                groups['OTHER'].append(figure)
        
        return groups
    
    def _create_context_block_from_group(
        self, 
        group_name: str, 
        group_figures: List[FigureInfo]
    ) -> Optional[Dict[str, Any]]:
        """Create a context block from a group of figures"""
        if not group_figures:
            return None
        
        # Collect all texts from the group
        all_texts = []
        images = {}
        
        for figure in group_figures:
            # Add base64 image if available
            if figure.base64_image:
                images[figure.id] = figure.base64_image
            
            # Collect associated texts
            for text_span in figure.associated_texts:
                all_texts.append(text_span.content)
        
        # Build context text
        context_text = '\n'.join(all_texts) if all_texts else f"Context for {group_name}"
        
        # Determine context type
        context_type = self._determine_context_type(context_text, group_figures)
        
        context_block = {
            'id': group_name.lower().replace(' ', '_'),
            'type': context_type,
            'title': group_name,
            'content': context_text,
            'images': images,
            'figure_ids': [f.id for f in group_figures]
        }
        
        logger.info(f"📋 Created context block '{group_name}' with {len(images)} images and {len(all_texts)} texts")
        
        return context_block
    
    def _determine_context_type(self, content: str, figures: List[FigureInfo]) -> str:
        """Determine the type of context based on content"""
        content_lower = content.lower()
        
        if 'charge' in content_lower:
            return 'comic_strip'
        elif 'propaganda' in content_lower:
            return 'advertisement'
        elif any('dialog' in text.lower() for text in content.split('\n')):
            return 'dialogue'
        else:
            return 'mixed_content'

    def remove_associated_figures_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove the associated_figures field from API result"""
        if 'associated_figures' in result:
            del result['associated_figures']
            logger.info("🗑️  Removed 'associated_figures' from API result")
        
        return result
