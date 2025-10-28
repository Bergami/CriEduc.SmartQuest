"""
Advanced Context Block Builder
Uses separated constants and enums for better maintainability.
Integrates with Azure Blob Storage for image handling and storage.
"""
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
import re
import logging
import uuid
from dataclasses import dataclass

from app.core.constants.instruction_patterns import InstructionPatterns
from app.models.internal.image_models import InternalImageData, ImageCategory
from app.core.constants.content_types import (
    ContentType, FigureType, TextRole, ContextBlockType,
    get_content_type_from_string, get_figure_type_from_content
)

if TYPE_CHECKING:
    from app.models.internal.context_models import InternalContextBlock, InternalSubContext

# Import direto para evitar problemas com DI
from app.core.interfaces import IImageUploadService

logger = logging.getLogger(__name__)

@dataclass
class TextSpan:
    """Represents a text span with position information"""
    content: str
    offset: int
    length: int
    page_number: int
    bounding_regions: List[Dict] = None
    text_role: TextRole = TextRole.UNKNOWN

@dataclass
class FigureInfo:
    """Enhanced figure information with spatial data"""
    id: str
    page_number: int
    bounding_regions: List[Dict]
    base64_image: Optional[str] = None
    azure_image_url: Optional[str] = None  # URL da imagem no Azure Blob Storage
    associated_texts: List[TextSpan] = None
    azure_figure: Optional[Dict] = None  # Referência para a figura original do Azure
    figure_type: FigureType = FigureType.UNKNOWN
    content_type: ContentType = ContentType.UNKNOWN
    
    def __post_init__(self):
        if self.associated_texts is None:
            self.associated_texts = []

class ContextBlockBuilder:
    """
    Context block builder using separated constants and enums
    """
    
    def __init__(self, image_upload_service: IImageUploadService = None):
        self.instruction_patterns = InstructionPatterns()
        self._image_upload_service = image_upload_service
        
        # Content type detection keywords
        self.content_keywords = {
            ContentType.CHARGE: ['charge', 'tirinha', 'quadrinho', 'cartoon', 'comic'],
            ContentType.PROPAGANDA: ['propaganda', 'anúncio', 'advertisement', 'publicidade'],
            ContentType.DIALOGUE: ['disse', 'falou', 'respondeu', 'perguntou'],
            ContentType.TITLE: ['texto', 'título', 'title'],
            ContentType.INSTRUCTION: ['analise', 'observe', 'leia', 'responda']
        }
    
    async def build_context_blocks_from_azure_figures(
        self,
        azure_response: Dict[str, Any],
        images_base64: Dict[str, str] = None,
        document_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Builds context blocks from Azure figures dynamically without hardcoding.
        
        Args:
            azure_response: The full response from Azure Document Intelligence.
            images_base64: Dictionary mapping figure IDs to base64 image data.
            
        Returns:
            A list of structured context blocks.
        """
        try:
            logger.info("🔧 DYNAMIC FIGURE ANALYSIS - Starting")

            # 1. Extract figures directly from the Azure response.
            figures = self._extract_figures_with_enhanced_info(azure_response)
            logger.info(f"📊 Extracted {len(figures)} figures from Azure response")

            # 2. Extrair spans de texto relevantes
            text_spans = self._extract_relevant_text_spans(azure_response)
            logger.info(f"📝 Extracted {len(text_spans)} relevant text spans")
            
            # 3. Encontrar instruções gerais (como "ANALISE OS TEXTO A SEGUIR")
            general_instructions = self._find_general_instructions(azure_response)
            logger.info(f"📋 Found {len(general_instructions)} general instructions")
            
            # 4. Associar textos às figuras baseado em proximidade espacial
            self._associate_texts_with_figures_enhanced(figures, text_spans)
            
            # 5. Adicionar imagens base64 às figuras se disponíveis
            if images_base64:
                # Usar document_id passado como parâmetro ou fallback
                effective_document_id = document_id or azure_response.get('model_id', 'unknown_document')
                azure_urls = await self._add_base64_images_to_figures(figures, images_base64, effective_document_id)
                logger.info(f"📷 Added images to {len([f for f in figures if f.base64_image or (hasattr(f, 'azure_image_url') and f.azure_image_url)])} figures")
            
            # 6. Criar context blocks baseado em análise dinâmica
            context_blocks = self._create_dynamic_context_blocks(
                figures, general_instructions, azure_response
            )
            
            logger.info(f"✅ Created {len(context_blocks)} dynamic context blocks")
            return context_blocks
            
        except Exception as e:
            logger.error(f"❌ Error in dynamic figure analysis: {str(e)}")
            return []

    def _convert_internal_images_to_figure_info(self, images: List[InternalImageData]) -> List[FigureInfo]:
        """Converte uma lista de InternalImageData para uma lista de FigureInfo."""
        figure_infos = []
        for img in images:
            # A conversão precisa mapear os campos de InternalImageData para FigureInfo
            # O azure_figure pode ser None se não tivermos a referência direta
            figure_info = FigureInfo(
                id=img.id,
                page_number=img.page,
                bounding_regions=img.extraction_metadata.bounding_regions if img.extraction_metadata else [],
                base64_image=img.base64_data,
                azure_figure=None, # Este campo pode precisar ser preenchido de outra forma se necessário
                figure_type=FigureType.CONTENT, # Categoria precisa ser mapeada
                content_type=ContentType.FIGURE # Categoria precisa ser mapeada
            )
            figure_infos.append(figure_info)
        return figure_infos
    
    def _extract_figures_with_enhanced_info(self, azure_response: Dict) -> List[FigureInfo]:
        """Extrai figuras com informações aprimoradas usando enums"""
        figures = []
        
        azure_figures = azure_response.get('figures', [])
        
        for figure in azure_figures:
            figure_id = figure.get('id', '')
            bounding_regions = figure.get('boundingRegions', [])
            
            if not bounding_regions:
                continue
                
            page_number = bounding_regions[0].get('pageNumber', 1)
            
            # Determinar tipos usando enums
            figure_type, content_type = self._classify_figure_with_enums(figure, azure_response)
            
            figure_info = FigureInfo(
                id=figure_id,
                page_number=page_number,
                bounding_regions=bounding_regions,
                azure_figure=figure  # Adicionar referência para a figura original
            )
            
            figures.append(figure_info)
            logger.debug(f"   📷 {figure_id}: {figure_type.value} ({content_type.value})")
        
        return figures
    
    def _classify_figure_with_enums(
        self, 
        figure: Dict[str, Any], 
        azure_response: Dict
    ) -> Tuple[FigureType, ContentType]:
        """
        Classifica figura usando enums baseado em posição e conteúdo
        """
        # Análise de posição
        spans = figure.get('spans', [])
        page_number = figure.get('boundingRegions', [{}])[0].get('pageNumber', 1)
        
        # Header detection (primeira página, início do documento)
        if spans and page_number == 1:
            first_offset = spans[0].get('offset', 0)
            if first_offset < 500:
                return FigureType.HEADER, ContentType.HEADER
        
        # Caption analysis
        caption = figure.get('caption', {}).get('content', '')
        if caption:
            content_type = get_content_type_from_string(caption)
            if content_type != ContentType.UNKNOWN:
                figure_type = get_figure_type_from_content(content_type)
                return figure_type, content_type
        
        # Content analysis
        content_texts = self._extract_figure_content_texts(figure, azure_response)
        combined_content = ' '.join(content_texts).lower()
        
        # Detect content type by keywords
        for content_type, keywords in self.content_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                figure_type = get_figure_type_from_content(content_type)
                return figure_type, content_type
        
        # Position-based classification for remaining figures
        bounding_regions = figure.get('boundingRegions', [])
        if bounding_regions:
            polygon = bounding_regions[0].get('polygon', [])
            if len(polygon) >= 2:
                y_position = polygon[1]  # Y coordinate
                if y_position < 1.0:
                    return FigureType.HEADER, ContentType.HEADER
                elif y_position > 10.0:
                    return FigureType.FOOTER, ContentType.FOOTER
        
        # Default classification
        return FigureType.CONTENT, ContentType.FIGURE
    
    def _extract_relevant_text_spans(self, azure_response: Dict) -> List[TextSpan]:
        """Extrai spans de texto relevantes para associação com figuras"""
        text_spans = []
        paragraphs = azure_response.get('paragraphs', [])
        
        for paragraph in paragraphs:
            content = paragraph.get('content', '').strip()
            if not content:
                continue
            
            # Verificar se é texto relevante usando padrões
            if self._is_text_relevant_for_association(content):
                spans = paragraph.get('spans', [])
                bounding_regions = paragraph.get('boundingRegions', [])
                
                if spans and bounding_regions:
                    span = spans[0]
                    page_number = bounding_regions[0].get('pageNumber', 1)
                    text_role = self._determine_text_role(content)
                    
                    text_span = TextSpan(
                        content=content,
                        offset=span.get('offset', 0),
                        length=span.get('length', len(content)),
                        page_number=page_number,
                        bounding_regions=bounding_regions,
                        text_role=text_role
                    )
                    
                    text_spans.append(text_span)
        
        return text_spans
    
    def _is_text_relevant_for_association(self, content: str) -> bool:
        """Verifica se texto é relevante para associação com figuras"""
        content_upper = content.upper().strip()
        
        # Check instruction patterns
        instruction_info = self.instruction_patterns.extract_instruction_content(content)
        if instruction_info['instruction_type'] != 'unknown':
            return True
        
        # Check content keywords
        for content_type, keywords in self.content_keywords.items():
            if any(keyword.upper() in content_upper for keyword in keywords):
                return True
        
        # Dialogue patterns
        if re.match(r'^[A-ZÁÀÃÊÔÇ\s,!?.-]+[!?.]$', content_upper) and len(content_upper) > 10:
            return True
        
        # Brand/company names (all caps, short)
        if re.match(r'^[A-Z]{2,15}$', content_upper.replace(' ', '')):
            return True
        
        # Numbers, dates, captions
        if re.match(r'^\d+(\.\d+)?$|^FOTO\s+[A-Z]$|^CIERRE$', content_upper):
            return True
        
        return False
    
    def _determine_text_role(self, content: str) -> TextRole:
        """Determina o papel do texto usando enum"""
        content_upper = content.upper().strip()
        
        # Instruction detection
        instruction_info = self.instruction_patterns.extract_instruction_content(content)
        if instruction_info['instruction_type'] != 'unknown':
            return TextRole.INSTRUCTION
        
        # Subtitle detection (TEXTO I:, TEXTO II:, etc.)
        if re.match(r'TEXTO\s+[IVX]+:', content_upper):
            return TextRole.SUBTITLE
        
        # Dialogue detection
        if re.match(r'^[A-ZÁÀÃÊÔÇ\s,!?.-]+[!?.]$', content_upper) and len(content_upper) > 10:
            return TextRole.DIALOGUE
        
        # Caption detection
        if re.match(r'^\d+(\.\d+)?$|^FOTO\s+[A-Z]$|^CIERRE$', content_upper):
            return TextRole.CAPTION
        
        # Default
        return TextRole.BODY_TEXT
    
    def _find_general_instructions(self, azure_response: Dict) -> List[Dict[str, Any]]:
        """Encontra instruções gerais como 'ANALISE OS TEXTO A SEGUIR'"""
        instructions = []
        paragraphs = azure_response.get('paragraphs', [])
        
        for paragraph in paragraphs:
            content = paragraph.get('content', '').strip()
            
            instruction_info = self.instruction_patterns.extract_instruction_content(content)
            
            if instruction_info['instruction_type'] != 'unknown':
                instructions.append({
                    'content': content,
                    'instruction_info': instruction_info,
                    'bounding_regions': paragraph.get('boundingRegions', []),
                    'spans': paragraph.get('spans', [])
                })
        
        return instructions
    
    def _extract_figure_content_texts(self, figure: Dict, azure_response: Dict) -> List[str]:
        """Extrai textos de conteúdo da figura baseado nos elements"""
        content_texts = []
        elements = figure.get('elements', [])
        paragraphs = azure_response.get('paragraphs', [])
        
        for element in elements:
            if element.startswith('/paragraphs/'):
                try:
                    para_index = int(element.split('/')[-1])
                    if para_index < len(paragraphs):
                        content = paragraphs[para_index].get('content', '')
                        if content:
                            content_texts.append(content)
                except (ValueError, IndexError):
                    continue
        
        return content_texts
    
    def _associate_texts_with_figures_enhanced(
        self, 
        figures: List[FigureInfo], 
        text_spans: List[TextSpan]
    ):
        """Associa textos às figuras com lógica aprimorada"""
        for text_span in text_spans:
            # Encontrar figura mais próxima na mesma página
            page_figures = [f for f in figures if f.page_number == text_span.page_number]
            
            if not page_figures:
                continue
            
            best_figure = self._find_closest_figure_enhanced(text_span, page_figures)
            if best_figure:
                best_figure.associated_texts.append(text_span)
                logger.debug(f"   📎 Associated '{text_span.content[:30]}...' with {best_figure.id}")
    
    def _find_closest_figure_enhanced(
        self, 
        text_span: TextSpan, 
        figures: List[FigureInfo]
    ) -> Optional[FigureInfo]:
        """Encontra figura mais próxima com lógica aprimorada"""
        if not text_span.bounding_regions:
            return None
        
        text_regions = text_span.bounding_regions
        best_figure = None
        min_distance = float('inf')
        
        for figure in figures:
            if not figure.bounding_regions:
                continue
            
            distance = self._calculate_spatial_distance(text_regions, figure.bounding_regions)
            
            # Bonus for semantic relationship
            if self._has_semantic_relationship(text_span, figure):
                distance *= 0.5  # Reduce distance for semantic matches
            
            if distance < min_distance:
                min_distance = distance
                best_figure = figure
        
        # Only associate if distance is reasonable
        return best_figure if min_distance < 2.0 else None
    
    def _has_semantic_relationship(self, text_span: TextSpan, figure: FigureInfo) -> bool:
        """Verifica se há relacionamento semântico entre texto e figura"""
        text_content = text_span.content.upper()
        
        # Check if text mentions figure type
        if figure.content_type == ContentType.CHARGE and any(word in text_content for word in ['CHARGE', 'TIRINHA']):
            return True
        
        if figure.content_type == ContentType.PROPAGANDA and any(word in text_content for word in ['PROPAGANDA', 'ANÚNCIO']):
            return True
        
        # Check for sequence markers (TEXTO I, II, III, IV)
        if text_span.text_role == TextRole.SUBTITLE and 'TEXTO' in text_content:
            return True
        
        return False
    
    def _calculate_spatial_distance(
        self, 
        text_regions: List[Dict], 
        figure_regions: List[Dict]
    ) -> float:
        """Calcula distância espacial entre regiões"""
        if not text_regions or not figure_regions:
            return float('inf')
        
        text_region = text_regions[0]
        figure_region = figure_regions[0]
        
        text_polygon = text_region.get('polygon', [])
        figure_polygon = figure_region.get('polygon', [])
        
        if len(text_polygon) < 8 or len(figure_polygon) < 8:
            return float('inf')
        
        # Calculate center points
        text_center_x = sum(text_polygon[i] for i in range(0, len(text_polygon), 2)) / 4
        text_center_y = sum(text_polygon[i] for i in range(1, len(text_polygon), 2)) / 4
        
        figure_center_x = sum(figure_polygon[i] for i in range(0, len(figure_polygon), 2)) / 4
        figure_center_y = sum(figure_polygon[i] for i in range(1, len(figure_polygon), 2)) / 4
        
        # Euclidean distance
        distance = ((text_center_x - figure_center_x) ** 2 + (text_center_y - figure_center_y) ** 2) ** 0.5
        
        return distance
    
    async def _add_base64_images_to_figures(self, figures: List[FigureInfo], images_base64: Dict[str, str], document_id: str = None) -> Dict[str, str]:
        """
        Adiciona imagens às figuras - Versão com Azure Blob Storage
        
        Args:
            figures: Lista de figuras para processar
            images_base64: Dicionário {image_id: base64_string}
            document_id: ID do documento para identificação
            
        Returns:
            Dicionário {image_id: azure_url} com URLs das imagens no Azure
        """
        if not images_base64:
            logger.warning("No images_base64 provided to _add_base64_images_to_figures")
            return {}
            
        logger.info(f"Processing images: {len(images_base64)} images available for {len(figures)} figures")
        
        # Se o serviço de upload está disponível, fazer upload para Azure
        azure_urls = {}
        if self._image_upload_service:
            try:
                # Usar document_id como GUID se fornecido, caso contrário gerar novo
                # O document_id pode ser usado tanto para identificação interna quanto para storage
                effective_document_guid = document_id if document_id else str(uuid.uuid4())
                
                # Fazer upload das imagens para Azure Blob Storage
                azure_urls = await self._image_upload_service.upload_images_and_get_urls(
                    images_base64=images_base64,
                    document_id=effective_document_guid,
                    document_guid=effective_document_guid
                )
                
                logger.info(f"Azure upload completed: {len(azure_urls)}/{len(images_base64)} images uploaded")
                
            except Exception as e:
                logger.error(f"Failed to upload images to Azure: {str(e)}")
                # Fallback para base64 se upload falhar
                azure_urls = {}
        
        # Aplicar URLs do Azure ou base64 como fallback às figuras
        images_added = 0
        for figure in figures:
            if figure.id in azure_urls:
                # Usar URL do Azure
                figure.azure_image_url = azure_urls[figure.id]
                figure.base64_image = None  # Limpar base64 para economizar memória
                images_added += 1
                logger.debug(f"   ✅ Added Azure URL to {figure.id}")
            elif figure.id in images_base64:
                # Fallback para base64 se Azure não disponível
                figure.base64_image = images_base64[figure.id]
                images_added += 1
                logger.debug(f"   📦 Added base64 image to {figure.id} (fallback)")
            else:
                logger.debug(f"   ❌ No image found for {figure.id}")
        
        logger.info(f"Successfully processed images for {images_added}/{len(figures)} figures")
        
        # Log figuras sem imagens
        figures_without_images = [f.id for f in figures if not (hasattr(f, 'azure_image_url') and f.azure_image_url) and not f.base64_image]
        if figures_without_images:
            logger.warning(f"Figures without images: {figures_without_images}")
            
        return azure_urls
    
    def _create_dynamic_context_blocks(
        self, 
        figures: List[FigureInfo], 
        general_instructions: List[Dict],
        azure_response: Dict
    ) -> List[Dict[str, Any]]:
        """Cria context blocks dinamicamente baseado na análise"""
        context_blocks = []
        
        # Armazenar azure_response como atributo para uso em outros métodos
        self.azure_response = azure_response
        
        # 1. Primeiro, extrair context_blocks de TEXTO do documento
        text_context_blocks = self._extract_text_context_blocks(azure_response)
        context_blocks.extend(text_context_blocks)
        
        # 2. Depois, agrupar figuras por contexto baseado em instruções e proximidade
        grouped_figures = self._group_figures_dynamically(figures, general_instructions)
        
        # 3. Processar grupos de figuras
        for group_name, group_figures in grouped_figures.items():
            if not group_figures or group_name == 'header':
                continue
            
            if group_name == 'individual_figures':
                # Criar um context_block separado para cada figura individual
                for figure in group_figures:
                    context_block = self._create_individual_context_block(figure)
                    if context_block:
                        context_blocks.append(context_block)
            elif group_name == 'content_blocks':
                # Verificar se é um grupo com múltiplas sequências (TEXTO I, II, III, IV)
                if self._has_multiple_sequences(group_figures):
                    context_block = self._create_context_block_with_sub_contexts(group_name, group_figures)
                else:
                    context_block = self._create_simple_context_block_from_group(group_name, group_figures)
                
                if context_block:
                    context_blocks.append(context_block)
        
        # 4. Renumerar IDs sequencialmente
        for i, block in enumerate(context_blocks, 1):
            block['id'] = i
        
        return context_blocks
    
    def _extract_text_context_blocks(self, azure_response: Dict) -> List[Dict[str, Any]]:
        """Extrai context blocks de texto usando análise de parágrafos do Azure"""
        
        if 'paragraphs' not in azure_response:
            logger.warning("No paragraphs found in Azure response for text context blocks")
            return []
        
        paragraphs = azure_response['paragraphs']
        context_blocks = []
        i = 0
        
        logger.info(f"Analyzing {len(paragraphs)} paragraphs for text context blocks")
        
        while i < len(paragraphs):
            para = paragraphs[i]
            content = para.get('content', '').strip()
            
            # Procurar por instruções de leitura (passando contexto posicional)
            if self._is_reading_instruction(content, i, paragraphs):
                # Encontrou uma instrução, agora coletar os parágrafos seguintes
                statement = content
                title = ""
                text_paragraphs = []
                
                i += 1  # Próximo parágrafo
                
                # Coletar título (próximo parágrafo após instrução)
                if i < len(paragraphs):
                    next_content = paragraphs[i].get('content', '').strip()
                    if self._is_likely_title(next_content):
                        title = next_content
                        i += 1
                
                # Coletar parágrafos do texto até encontrar uma quebra lógica
                while i < len(paragraphs):
                    current_content = paragraphs[i].get('content', '').strip()
                    
                    # Parar se encontrar questão ou nova instrução
                    if self._is_question_start(current_content) or self._is_reading_instruction(current_content, i, paragraphs):
                        break
                        
                    # Pular informações de header, mas continuar coletando texto
                    if self._is_header_info(current_content):
                        i += 1
                        continue
                    
                    # Parar se o parágrafo for quebra de contexto (mas não header)
                    if self._is_context_break(current_content):
                        break
                    
                    text_paragraphs.append(current_content)
                    i += 1
                
                # Criar context block se tiver conteúdo válido
                if title or text_paragraphs:
                    context_block = {
                        'id': len(context_blocks) + 1,
                        'type': ['text'],
                        'source': 'exam_document',
                        'statement': statement,
                        'title': title if title else "Texto para análise",
                        'paragraphs': text_paragraphs,
                        'hasImage': False
                    }
                    context_blocks.append(context_block)
                    logger.info(f"📋 Created text context block: '{statement}' -> '{title}' ({len(text_paragraphs)} paragraphs)")
                
                continue
            
            i += 1
        
        return context_blocks
    
    def _parse_text_content(self, instruction_title: str, content: str) -> tuple:
        """Parse content to extract statement, title, and paragraphs"""
        
        # Statement é a instrução (ex: "LEIA O TEXTO A SEGUIR")
        statement = instruction_title if instruction_title else ""
        
        # Extrair título do texto (primeira linha geralmente)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        title = ""
        paragraphs = []
        
        if lines:
            # Primeira linha não vazia é geralmente o título
            potential_title = lines[0]
            
            # Verificar se primeira linha parece com título de texto literário (contém parênteses com autor)
            if '(' in potential_title and ')' in potential_title and len(potential_title) < 100:
                title = potential_title
                paragraphs = lines[1:] if len(lines) > 1 else []
            # Se primeira linha é curta e não termina com ponto, pode ser título
            elif len(potential_title) < 100 and not potential_title.endswith('.'):
                title = potential_title
                paragraphs = lines[1:] if len(lines) > 1 else []
            else:
                # Se primeira linha é muito longa, considerar todo conteúdo como parágrafos
                paragraphs = lines
                
                # Tentar extrair título de uma possível linha com formato "Título (Autor)"
                for line in lines[:3]:  # Procurar título nas primeiras 3 linhas
                    if '(' in line and ')' in line and len(line) < 80:
                        title = line
                        # Remover título dos parágrafos
                        if line in paragraphs:
                            paragraphs.remove(line)
                        break
        
        # Se ainda não encontrou título, usar uma descrição genérica
        if not title and statement:
            title = "Texto para análise"
        
        return statement, title, paragraphs
    
    def _is_reading_instruction(self, content: str, paragraph_index: int = -1, all_paragraphs: List[Dict] = None) -> bool:
        """Verifica se o conteúdo é uma instrução de leitura para context blocks de texto"""
        content_upper = content.upper()
        
        # Se temos informações de contexto, usar análise posicional
        if paragraph_index >= 0 and all_paragraphs:
            # Verificar se há questão próxima (indica instrução individual)
            context_range = 5  # Verificar 5 parágrafos antes e depois
            start = max(0, paragraph_index - context_range)
            end = min(len(all_paragraphs), paragraph_index + context_range)
            
            for i in range(start, end):
                if i == paragraph_index:
                    continue
                para_content = all_paragraphs[i].get('content', '').upper()
                # Se há questão próxima, é instrução individual
                if 'QUESTÃO' in para_content and ('PARA RESPONDER' in content_upper):
                    return False
        
        # Excluir instruções específicas de figuras individuais
        individual_instructions = [
            "LEIA O TEXTO A SEGUIR PARA RESPONDER À PRÓXIMA QUESTÃO",
            "ANALISE A TIRINHA A SEGUIR PARA RESPONDER À PRÓXIMA QUESTÃO", 
            "OBSERVE A FIGURA A SEGUIR PARA RESPONDER À PRÓXIMA QUESTÃO"
        ]
        
        # Se é uma instrução individual, não deve ser tratada como context block de texto
        for individual_instr in individual_instructions:
            if individual_instr in content_upper:
                return False
        
        # Instruções válidas para context blocks de texto
        text_instructions = [
            "LEIA O TEXTO A SEGUIR",
            "LEIA O TEXTO",
            "ANALISE O TEXTO A SEGUIR",
            "APÓS LER ATENTAMENTE O TEXTO",
            "LEIA A CRÔNICA E DEPOIS",
            "LEIA ESTE TEXTO"
        ]
        
        for instruction in text_instructions:
            if instruction in content_upper:
                return True
        
        return False

    def _is_likely_title(self, content: str) -> bool:
        """Verifica se o conteúdo parece ser um título"""
        # Título geralmente tem parênteses com autor
        if '(' in content and ')' in content and len(content) < 100:
            return True
        
        # Título curto sem pontos finais
        if len(content) < 80 and not content.endswith('.') and not content.endswith('?'):
            # Evitar confundir com outras coisas
            if not content.startswith('QUE') and not content.isdigit():
                return True
        
        return False

    def _is_question_start(self, content: str) -> bool:
        """Verifica se o conteúdo é início de uma questão"""
        content_upper = content.upper()
        return (
            content_upper.startswith('QUESTÃO') or
            content_upper.startswith('PERGUNTA') or
            content_upper.startswith('1.') or
            content_upper.startswith('2.') or
            'QUESTÃO' in content_upper[:20]
        )

    def _is_header_info(self, content: str) -> bool:
        """Verifica se o conteúdo é informação de header (mas não quebra de contexto definitiva)"""
        content_upper = content.upper()
        content_stripped = content.strip()
        
        # Informações de header que devem ser puladas mas não param a coleta
        header_fields = [
            'DATA:',
            'VALOR:',
            'NOTA:',
            'PONTOS:',
            'ESTUDANTE:',
            'PROFESSOR:',
            'TRIMESTRE:',
            'ANO:',
            'TURMA:'
        ]
        
        for field in header_fields:
            if content_upper.startswith(field) or content_upper == field.rstrip(':'):
                return True
            # Também verificar se é só o valor (ex: "30,0" após "Valor:")
            if field == 'VALOR:' and content_stripped.replace(',', '.').replace('.', '').replace(' ', '').isdigit():
                return True
        
        # Casos como apenas "Data", "Nota", valores numéricos isolados
        if content_stripped.rstrip(':').upper() in ['DATA', 'VALOR', 'NOTA', 'PONTOS']:
            return True
            
        # Valores numéricos curtos (provavelmente notas/valores)
        if len(content_stripped) < 10 and content_stripped.replace(',', '').replace('.', '').isdigit():
            return True
            
        return False

    def _is_context_break(self, content: str) -> bool:
        """Verifica se há quebra de contexto (parada definitiva)"""
        content_upper = content.upper()
        
        # Indicadores de mudança de contexto definitiva
        breaks = [
            'ANALISE',
            'OBSERVE',
            'CONSIDERE',
            'DE ACORDO COM',
            'COM BASE NO TEXTO',
            'QUESTÃO',
            'ALTERNATIVAS:'
        ]
        
        for break_indicator in breaks:
            if content_upper.startswith(break_indicator):
                return True
        
        return False
    
    def _group_figures_dynamically(
        self, 
        figures: List[FigureInfo], 
        general_instructions: List[Dict]
    ) -> Dict[str, List[FigureInfo]]:
        """Agrupa figuras dinamicamente sem hardcoding"""
        groups = {
            'header': [],
            'content_blocks': [],
            'individual_figures': []
        }
        
        # Separate by figure type and instruction context
        for figure in figures:
            if figure.figure_type == FigureType.HEADER:
                groups['header'].append(figure)
            else:
                # Verificar se a figura tem instrução individual
                if self._has_individual_instruction(figure):
                    groups['individual_figures'].append(figure)
                else:
                    groups['content_blocks'].append(figure)
        
        logger.info(f"🔗 Grouped figures: {list(groups.keys())}")
        for group_name, group_figures in groups.items():
            logger.info(f"   {group_name}: {len(group_figures)} figures")
        
        return groups
    
    def _extract_sequence_identifier(self, figure: FigureInfo) -> Optional[str]:
        """Extrai identificador de sequência (TEXTO I, II, III, IV) dos textos associados"""
        sequences = self._extract_all_sequence_identifiers(figure)
        return sequences[0] if sequences else None
    
    def _extract_all_sequence_identifiers(self, figure: FigureInfo) -> List[str]:
        """Extrai TODOS os identificadores de sequência de uma figura - Versão melhorada"""
        sequences_found = []
        
        # Verificar se figure.associated_texts existe e não está vazio
        if not hasattr(figure, 'associated_texts') or not figure.associated_texts:
            logger.debug(f"No associated_texts found for figure {getattr(figure, 'id', 'unknown')}")
            return sequences_found
        
        for text_span in figure.associated_texts:
            content_upper = text_span.content.upper()
            
            # Padrões mais robustos para detectar sequências
            patterns = [
                r'TEXTO\s+([IVX]+)\s*:',      # TEXTO I:, TEXTO II:, etc.
                r'TEXTO\s+([IVX]+)\s*[-–]',   # TEXTO I -, TEXTO II -, etc.
                r'TEXTO\s+([IVX]+)\s*\.',     # TEXTO I., TEXTO II., etc.
                r'TEXTO\s+([IVX]+)\s+',       # TEXTO I (seguido de espaço)
                r'^([IVX]+)\s*[-–:]',         # I:, II:, III: no início da linha
                r'^\s*([IVX]+)\s*\.',         # I., II., III. no início da linha
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content_upper)
                sequences_found.extend(matches)
            
            # Também procurar por numeração arábica como fallback
            arabic_patterns = [
                r'TEXTO\s+(\d+)\s*:',         # TEXTO 1:, TEXTO 2:, etc.
                r'TEXTO\s+(\d+)\s*[-–]',      # TEXTO 1 -, TEXTO 2 -, etc.
            ]
            
            for pattern in arabic_patterns:
                arabic_matches = re.findall(pattern, content_upper)
                # Converter números arábicos para romanos
                for num in arabic_matches:
                    try:
                        num_int = int(num)
                        if num_int <= 10:  # Limitar conversão para números pequenos
                            roman = self._arabic_to_roman(num_int)
                            sequences_found.append(roman)
                    except ValueError:
                        continue
        
        # Remover duplicatas e converter para lowercase, mantendo ordem
        seen = set()
        unique_sequences = []
        for seq in sequences_found:
            seq_lower = seq.lower()
            if seq_lower not in seen:
                seen.add(seq_lower)
                unique_sequences.append(seq_lower)
        
        if len(unique_sequences) > 1:
            logger.debug(f"Figure {figure.id} has multiple sequences: {unique_sequences}")
        elif len(unique_sequences) == 1:
            logger.debug(f"Figure {figure.id} has sequence: {unique_sequences[0]}")
        
        return unique_sequences
    
    def _arabic_to_roman(self, num: int) -> str:
        """Converte números arábicos para romanos (1-10)"""
        conversion = {
            1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V',
            6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X'
        }
        return conversion.get(num, str(num))
    
    def _has_individual_instruction(self, figure: FigureInfo) -> bool:
        """Verifica se a figura tem uma instrução individual (não faz parte do grupo ANALISE OS TEXTO A SEGUIR)"""
        for text_span in figure.associated_texts:
            content_upper = text_span.content.upper()
            
            # Instruções individuais específicas
            individual_instructions = [
                'ANALISE A TIRINHA A SEGUIR',
                'LEIA O TEXTO A SEGUIR PARA RESPONDER',
                'OBSERVE A FIGURA A SEGUIR',
                'CONSIDERE A IMAGEM A SEGUIR'
            ]
            
            for instruction in individual_instructions:
                if instruction in content_upper:
                    return True
        
        return False
    
    def _identify_content_type_from_figure(self, figure: FigureInfo) -> str:
        """Identifica o tipo de conteúdo baseado nos textos associados à figura"""
        # Verificar textos associados para identificar tipo
        for text_span in figure.associated_texts:
            content_upper = text_span.content.upper()
            if 'CHARGE' in content_upper:
                return 'charge'
            elif 'PROPAGANDA' in content_upper:
                return 'propaganda'
            elif 'FOTO' in content_upper:
                return 'photo'
            elif 'TIRINHA' in content_upper:
                return 'comic'
        
        # Default baseado no content_type da figura
        return figure.content_type.value.lower() if figure.content_type else 'unknown'
    
    def _has_multiple_sequences(self, figures: List[FigureInfo]) -> bool:
        """Verifica se um grupo de figuras contém múltiplas sequências (TEXTO I, II, III, IV)"""
        all_sequences = set()
        
        for figure in figures:
            sequences = self._extract_all_sequence_identifiers(figure)
            all_sequences.update(sequences)
        
        return len(all_sequences) > 1
    
    def _create_context_block_with_sub_contexts(
        self, 
        group_name: str, 
        group_figures: List[FigureInfo]
    ) -> Optional[Dict[str, Any]]:
        """Cria context block com sub_contexts para múltiplas sequências"""
        if not group_figures:
            return None
        
        # Organizar figuras por sequência
        sequence_groups = {}
        general_instruction = None
        
        for figure in group_figures:
            sequences = self._extract_all_sequence_identifiers(figure)
            
            if not sequences:
                # Figura sem sequência - pode ser instrução geral
                for text_span in figure.associated_texts:
                    if 'ANALISE' in text_span.content.upper():
                        general_instruction = text_span.content.strip()
                continue
            
            for sequence in sequences:
                if sequence not in sequence_groups:
                    sequence_groups[sequence] = []
                sequence_groups[sequence].append(figure)
        
        # Criar sub_contexts
        sub_contexts = []
        for sequence in sorted(sequence_groups.keys()):
            figures_in_sequence = sequence_groups[sequence]
            
            # Para cada sequência, criar um sub_context
            for figure in figures_in_sequence:
                sub_context = self._create_sub_context_from_figure(sequence, figure)
                if sub_context:
                    sub_contexts.append(sub_context)
        
        # Coletar todas as imagens dos sub_contexts
        all_images = []
        for sub_context in sub_contexts:
            sub_images = sub_context.get('images', [])
            logger.debug(f"Sub-context has {len(sub_images)} images")
            all_images.extend(sub_images)
        
        logger.debug(f"Total images collected for context block: {len(all_images)}")
        
        # Context block principal
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': ['text', 'image'],
            'source': 'exam_document',
            'title': 'Análise de Textos',
            'statement': general_instruction if general_instruction else '',
            'paragraphs': [],  # Context blocks com sub_contexts geralmente não têm paragraphs próprios
            'hasImage': len(all_images) > 0,
            'images': [],  # 🔧 CORREÇÃO: Context blocks com sub_contexts NÃO têm imagens no pai
            'sub_contexts': sub_contexts
        }
        
        # Adicionar campo contentType se houver imagens
        if len(all_images) > 0:
            context_block['contentType'] = 'image/jpeg;base64'
        
        logger.debug(f"Created context block with {len(sub_contexts)} sub_contexts")
        
        return context_block
    
    def _create_sub_context_from_figure(
        self, 
        sequence: str, 
        figure: FigureInfo
    ) -> Optional[Dict[str, Any]]:
        """Cria um sub_context a partir de uma figura e sequência"""
        
        # Filtrar textos relevantes para esta sequência específica
        relevant_texts = []
        sequence_title = None
        
        for text_span in figure.associated_texts:
            content_upper = text_span.content.upper()
            
            # Se é o título da sequência (TEXTO I:, TEXTO II:, etc.)
            if f'TEXTO {sequence.upper()}:' in content_upper:
                sequence_title = text_span.content.strip()
                continue
            
            # Se é conteúdo relevante (não é número isolado, não é outra sequência)
            content_clean = text_span.content.strip()
            if (len(content_clean) > 3 and 
                not content_clean.isdigit() and 
                'TEXTO' not in content_upper and
                'QUESTÃO' not in content_upper):
                relevant_texts.append(content_clean)
        
        # Se não encontrou título específico, usar padrão
        if not sequence_title:
            # Detectar tipo baseado nos textos
            content_type = 'figura'
            for text in relevant_texts:
                if 'charge' in text.lower():
                    content_type = 'charge'
                    break
                elif 'propaganda' in text.lower():
                    content_type = 'propaganda'
                    break
            
            sequence_title = f"TEXTO {sequence.upper()}: {content_type}"
        
        sub_context = {
            'sequence': sequence.upper(),
            'type': self._detect_sub_context_type(relevant_texts),
            'title': sequence_title,
            'content': '\n'.join(relevant_texts) if relevant_texts else '',
            'images': [],  # Inicializar vazio
            'azure_image_urls': []  # Novo campo para URLs do Azure
        }
        
        # Adicionar imagem se disponível
        if hasattr(figure, 'azure_image_url') and figure.azure_image_url:
            sub_context['azure_image_urls'] = [figure.azure_image_url]
            logger.debug(f"Added Azure URL to sub-context {sequence}")
        elif figure.base64_image:
            sub_context['images'] = [figure.base64_image]
            logger.debug(f"Added base64 image to sub-context {sequence} (fallback)")
        
        return sub_context
    
    def _detect_sub_context_type(self, texts: List[str]) -> str:
        """Detecta o tipo de sub_context baseado nos textos"""
        combined_text = ' '.join(texts).lower()
        
        if 'charge' in combined_text:
            return 'charge'
        elif 'propaganda' in combined_text:
            return 'propaganda'
        elif 'tirinha' in combined_text:
            return 'comic'
        elif 'foto' in combined_text:
            return 'photo'
        else:
            return 'image'
    
    def _create_individual_context_block(self, figure: FigureInfo) -> Optional[Dict[str, Any]]:
        """Cria um context_block individual para figuras com instruções próprias"""
        
        # Extrair instrução e título
        instruction = None
        title = None
        content_parts = []
        
        for text_span in figure.associated_texts:
            content = text_span.content.strip()
            content_upper = content.upper()
            
            # Detectar instrução
            if any(instr in content_upper for instr in [
                'ANALISE A TIRINHA', 'LEIA O TEXTO A SEGUIR', 
                'OBSERVE A FIGURA', 'CONSIDERE A IMAGEM'
            ]):
                instruction = content
                continue
            
            # Detectar questão (não incluir no content)
            if content_upper.startswith('QUESTÃO'):
                continue
            
            # Coletar outros conteúdos relevantes
            if len(content) > 3 and not content.isdigit():
                content_parts.append(content)
        
        # Determinar título baseado no tipo de conteúdo
        if not title:
            if any('tirinha' in part.lower() for part in content_parts):
                title = "Análise de Tirinha"
            elif any('vida pede passagem' in part.lower() for part in content_parts):
                title = "A Vida Pede Passagem"
            else:
                title = "Análise de Imagem"
        
        # Determinar tipo (apenas: text, image, image_collection)
        context_type = 'image'  # Padrão para figuras individuais
        
        # Extrair textos completos da imagem usando boundingRegions
        image_texts = self._extract_complete_image_texts(figure)
        
        # Criar context block base
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': [context_type],
            'source': 'exam_document',
            'title': title,
            'statement': instruction,
            'paragraphs': image_texts,  # Usar os textos extraídos como paragraphs
            'hasImage': True  # Sempre True para figuras individuais
        }
        
        # Adicionar imagens se disponíveis
        if hasattr(figure, 'azure_image_url') and figure.azure_image_url:
            context_block['contentType'] = 'image/url'
            context_block['azure_image_urls'] = [figure.azure_image_url]
            context_block['images'] = []  # Limpar base64 para economizar memória
            logger.debug(f"Added Azure URL to individual context block: {title}")
        elif figure.base64_image:
            context_block['contentType'] = 'image/jpeg;base64'
            context_block['images'] = [figure.base64_image]
            logger.debug(f"Added base64 image to individual context block: {title} (fallback)")
        else:
            # Mesmo sem imagem, manter estrutura
            context_block['images'] = []
            logger.warning(f"No image available for figure {figure.id} in context block: {title}")
        
        logger.debug(f"Created individual context block: {title} with {len(image_texts)} text paragraphs, hasImage={context_block.get('hasImage')}, images_count={len(context_block.get('images', []))}")
        
        return context_block
    
    def _extract_complete_image_texts(self, figure: FigureInfo) -> List[str]:
        """Extrai todos os textos que estão dentro da área da imagem usando boundingRegions - Versão melhorada"""
        if not figure.azure_figure:
            # Se não temos azure_figure, usar textos associados como fallback
            logger.debug(f"No azure_figure for {figure.id}, using associated texts as fallback")
            return [text.content.strip() for text in figure.associated_texts 
                   if text.content.strip() and len(text.content.strip()) > 1]
        
        # Obter boundingRegions da figura
        figure_regions = figure.azure_figure.get('boundingRegions', [])
        if not figure_regions:
            logger.debug(f"No boundingRegions for {figure.id}, using associated texts")
            return [text.content.strip() for text in figure.associated_texts 
                   if text.content.strip() and len(text.content.strip()) > 1]
        
        # Obter informações de página e coordenadas da figura
        figure_page = figure_regions[0].get('pageNumber', 1)
        figure_polygon = figure_regions[0].get('polygon', [])
        
        if len(figure_polygon) < 8:  # Precisa de pelo menos 4 pontos (x,y cada)
            logger.debug(f"Invalid polygon for {figure.id}, using associated texts")
            return [text.content.strip() for text in figure.associated_texts 
                   if text.content.strip() and len(text.content.strip()) > 1]
        
        # Calcular bounding box da figura
        x_coords = [figure_polygon[i] for i in range(0, len(figure_polygon), 2)]
        y_coords = [figure_polygon[i] for i in range(1, len(figure_polygon), 2)]
        
        fig_x_min, fig_x_max = min(x_coords), max(x_coords)
        fig_y_min, fig_y_max = min(y_coords), max(y_coords)
        
        # Buscar spans de texto que estejam dentro da área da figura
        image_texts = []
        
        # Verificar se temos acesso ao azure_response completo
        if hasattr(self, 'azure_response') and 'paragraphs' in self.azure_response:
            for paragraph in self.azure_response['paragraphs']:
                para_regions = paragraph.get('boundingRegions', [])
                
                for region in para_regions:
                    if region.get('pageNumber') != figure_page:
                        continue
                    
                    para_polygon = region.get('polygon', [])
                    if len(para_polygon) < 8:
                        continue
                    
                    # Calcular bounding box do parágrafo
                    para_x_coords = [para_polygon[i] for i in range(0, len(para_polygon), 2)]
                    para_y_coords = [para_polygon[i] for i in range(1, len(para_polygon), 2)]
                    
                    para_x_min, para_x_max = min(para_x_coords), max(para_x_coords)
                    para_y_min, para_y_max = min(para_y_coords), max(para_y_coords)
                    
                    # Verificar se o parágrafo está dentro da área da figura (com margem)
                    margin = 0.1  # Margem de tolerância aumentada
                    if (para_x_min >= fig_x_min - margin and para_x_max <= fig_x_max + margin and
                        para_y_min >= fig_y_min - margin and para_y_max <= fig_y_max + margin):
                        
                        content = paragraph.get('content', '').strip()
                        if content and len(content) > 1:
                            image_texts.append(content)
                            logger.debug(f"Found text within figure {figure.id}: {content[:50]}...")
        
        # Se não conseguiu pelo método acima, usar os textos associados existentes
        if not image_texts:
            logger.debug(f"No texts found within boundingRegions for {figure.id}, using associated texts")
            for text_span in figure.associated_texts:
                content = text_span.content.strip()
                if content and len(content) > 1 and not content.upper().startswith('QUESTÃO'):
                    image_texts.append(content)
        
        # Filtrar textos muito curtos ou irrelevantes
        filtered_texts = []
        for text in image_texts:
            # Pular números isolados, questões, ou textos muito curtos
            if (len(text) > 3 and 
                not text.isdigit() and 
                not text.upper().startswith('QUESTÃO') and
                not re.match(r'^\d+\s*$', text.strip())):
                filtered_texts.append(text)
        
        logger.debug(f"Extracted {len(filtered_texts)} texts for figure {figure.id}")
        return filtered_texts
    
    def _create_simple_context_block_from_group(
        self, 
        group_name: str, 
        group_figures: List[FigureInfo]
    ) -> Optional[Dict[str, Any]]:
        """Cria context block simples (sem sub_contexts) a partir de um grupo"""
        if not group_figures:
            return None
        
        # Collect images and texts
        images = []
        azure_urls = []
        all_texts = []
        content_types = set()
        
        for figure in group_figures:
            # Priorizar Azure URLs sobre base64
            if hasattr(figure, 'azure_image_url') and figure.azure_image_url:
                azure_urls.append(figure.azure_image_url)
            elif figure.base64_image:
                images.append(figure.base64_image)
            
            content_types.add(figure.content_type)
            
            for text_span in figure.associated_texts:
                all_texts.append(text_span.content)
        
        # Build context text from relevant texts only
        relevant_texts = []
        for text in all_texts:
            # Filtrar textos irrelevantes como números isolados
            if len(text.strip()) > 3 and not text.strip().isdigit():
                relevant_texts.append(text)
        
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': ['image'],
            'source': 'exam_document',
            'title': group_name.replace('_', ' ').title(),
            'paragraphs': relevant_texts,
            'hasImage': len(azure_urls) > 0 or len(images) > 0
        }
        
        # Adicionar imagens com prioridade para Azure URLs
        if len(azure_urls) > 0:
            context_block['contentType'] = 'image/url'
            context_block['azure_image_urls'] = azure_urls
            context_block['images'] = []  # Limpar base64
            logger.debug(f"Added {len(azure_urls)} Azure URLs to simple context block: {group_name}")
        elif len(images) > 0:
            context_block['contentType'] = 'image/jpeg;base64'
            context_block['images'] = images
            logger.debug(f"Added {len(images)} base64 images to simple context block: {group_name} (fallback)")
        else:
            context_block['images'] = []
        
        logger.debug(f"Created simple context block: {group_name} with {len(azure_urls)} Azure URLs and {len(images)} base64 images")
        
        return context_block
    
    def _determine_context_block_type(
        self, 
        content_types: set, 
        texts: List[str]
    ) -> ContextBlockType:
        """Determina tipo do context block baseado nos tipos de conteúdo"""
        # Check if has visual content (charge, propaganda, image, figure)
        visual_types = {ContentType.CHARGE, ContentType.PROPAGANDA, ContentType.IMAGE, ContentType.FIGURE}
        has_visual = bool(visual_types.intersection(content_types))
        
        # Check if has text content  
        text_types = {ContentType.TEXT, ContentType.DIALOGUE, ContentType.PARAGRAPH, ContentType.TITLE}
        has_text = bool(text_types.intersection(content_types)) or any(texts)
        
        # Determine context block type
        if has_visual and has_text:
            return ContextBlockType.TEXT_AND_IMAGE
        elif has_visual:
            return ContextBlockType.IMAGE_CONTEXT
        elif has_text:
            return ContextBlockType.TEXT_CONTEXT
        else:
            return ContextBlockType.UNKNOWN
    
    def remove_figure_association_fields(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Removes unnecessary 'associated_figures' and 'figure_ids' fields from the API result."""
        # Remove associated_figures do nível superior
        if 'associated_figures' in result:
            del result['associated_figures']
            logger.info("Removed 'associated_figures' from API result")
        
        # Remove figure_ids e associated_figures das questões
        if 'questions' in result:
            for question in result['questions']:
                if 'figure_ids' in question:
                    del question['figure_ids']
                    logger.info("Removed 'figure_ids' from question")
                if 'associated_figures' in question:
                    del question['associated_figures']
                    logger.info("Removed 'associated_figures' from question")
        
        # Remove figure_ids dos context blocks
        if 'context_blocks' in result:
            for context_block in result['context_blocks']:
                if 'figure_ids' in context_block:
                    del context_block['figure_ids']
                    logger.info("Removed 'figure_ids' from context block")
                if 'associated_figures' in context_block:
                    del context_block['associated_figures']
                    logger.info("Removed 'associated_figures' from context block")
        
        return result

    # ============================================
    # FASE 2: INTERFACE PYDANTIC NATIVA
    # ============================================
    
    async def parse_to_pydantic(
        self,
        azure_response: Dict[str, Any],
        images_base64: Dict[str, str] = None,
        document_id: str = None
    ) -> List['InternalContextBlock']:
        """
        FASE 2: Interface Pydantic nativa - retorna diretamente objetos Pydantic
        
        Args:
            azure_response: The full response from Azure Document Intelligence.
            images_base64: Dictionary mapping figure IDs to base64 image data.
            
        Returns:
            A list of InternalContextBlock Pydantic objects (not Dicts).
        """
        try:
            from app.models.internal.context_models import InternalContextBlock
            
            logger.info("🚀 FASE 2: Starting parse_to_pydantic - Direct Pydantic interface")

            # 1. Extract figures directly from the Azure response.
            figures = self._extract_figures_with_enhanced_info(azure_response)
            logger.info(f"📊 [Pydantic] Extracted {len(figures)} figures from Azure response")

            # 2. Extrair spans de texto relevantes
            text_spans = self._extract_relevant_text_spans(azure_response)
            logger.info(f"📝 [Pydantic] Extracted {len(text_spans)} relevant text spans")
            
            # 3. Encontrar instruções gerais (como "ANALISE OS TEXTO A SEGUIR")
            general_instructions = self._find_general_instructions(azure_response)
            logger.info(f"📋 [Pydantic] Found {len(general_instructions)} general instructions")
            
            # 4. Associar textos às figuras baseado em proximidade espacial
            self._associate_texts_with_figures_enhanced(figures, text_spans)
            
            # 5. Adicionar imagens base64 às figuras se disponíveis
            if images_base64:
                # Usar document_id passado como parâmetro ou fallback
                effective_document_id = document_id or azure_response.get('model_id', 'unknown_document')
                azure_urls = await self._add_base64_images_to_figures(figures, images_base64, effective_document_id)
                logger.info(f"📷 [Pydantic] Added images to {len([f for f in figures if f.base64_image or (hasattr(f, 'azure_image_url') and f.azure_image_url)])} figures")
            
            # 6. Criar context blocks DIRETAMENTE como Pydantic objects
            context_blocks = self._create_pydantic_context_blocks(
                figures, general_instructions, azure_response
            )
            
            logger.info(f"✅ [Pydantic] Created {len(context_blocks)} InternalContextBlock objects")
            return context_blocks
            
        except Exception as e:
            logger.error(f"❌ [Pydantic] Error in parse_to_pydantic: {str(e)}")
            return []

    def _create_pydantic_context_blocks(
        self,
        figures: List[FigureInfo],
        general_instructions: List[str],
        azure_response: Dict[str, Any]
    ) -> List['InternalContextBlock']:
        """
        Create context blocks directly as Pydantic objects (FASE 2)
        """
        from app.models.internal.context_models import InternalContextBlock, InternalSubContext
        
        logger.info("🔧 [Pydantic] Creating context blocks as Pydantic objects")
        context_blocks = []
        
        try:
            # Primeiro criar os context blocks baseados nas figuras
            for i, figure in enumerate(figures):
                logger.info(f"🔍 [Pydantic] Processing figure {i+1}/{len(figures)} - ID: {figure.id}")
                
                # Detectar sequências no texto da figura
                sequences = self._extract_all_sequence_identifiers(figure)
                logger.info(f"📝 [Pydantic] Found {len(sequences)} sequences in figure {figure.id}")
                
                # Criar sub_contexts se sequências foram encontradas
                sub_contexts = []
                if sequences:
                    logger.info(f"🎯 [Pydantic] Creating sub-contexts for sequences: {sequences}")
                    
                    for sequence in sequences:
                        # Extrair texto específico para esta sequência (implementação simples)
                        sequence_text = f"Content for sequence {sequence}"
                        
                        # Criar InternalSubContext Pydantic object
                        sub_context_data = {
                            "sequence": sequence,
                            "type": "text",  # Default type
                            "title": f"TEXTO {sequence}",
                            "content": sequence_text,
                            "images": [],  # Inicializar vazio
                            "azure_image_urls": []  # Novo campo
                        }
                        
                        # Adicionar imagem se disponível
                        if hasattr(figure, 'azure_image_url') and figure.azure_image_url:
                            sub_context_data["azure_image_urls"] = [figure.azure_image_url]
                        elif figure.base64_image:
                            sub_context_data["images"] = [figure.base64_image]
                        
                        sub_context = InternalSubContext(**sub_context_data)
                        sub_contexts.append(sub_context)
                        logger.info(f"✅ [Pydantic] Created sub-context for sequence '{sequence}'")
                
                # Extrair texto principal da figura
                main_content = self._extract_complete_image_texts(figure)
                main_text = "\n".join(main_content) if main_content else ""
                
                # Determinar tipo do context block - fix para usar content_types corretos
                content_types = set()  # Por enquanto, usar conjunto vazio
                content_type_enum = self._determine_context_block_type(content_types, main_content)
                
                # Criar content object
                from app.models.internal.context_models import InternalContextContent
                content_obj = InternalContextContent(
                    description=main_content if main_content else [main_text] if main_text else [""],
                    raw_content=main_text,
                    content_source="figure_text"
                )
                
                # Criar InternalContextBlock Pydantic object
                context_block_data = {
                    "id": i+1,  # Use figure index + 1 as ID
                    "type": [ContentType.TEXT] if not (figure.base64_image or (hasattr(figure, 'azure_image_url') and figure.azure_image_url)) else [ContentType.IMAGE],
                    "content": content_obj,
                    "title": f"Context {i+1}",  # Placeholder title
                    "images": [],  # Inicializar vazio
                    "azure_image_urls": [],  # Novo campo
                    "sub_contexts": sub_contexts
                }
                
                # Adicionar imagem se disponível e não há sub_contexts
                if not sub_contexts:
                    if hasattr(figure, 'azure_image_url') and figure.azure_image_url:
                        context_block_data["azure_image_urls"] = [figure.azure_image_url]
                    elif figure.base64_image:
                        context_block_data["images"] = [figure.base64_image]
                
                context_block = InternalContextBlock(**context_block_data)
                
                context_blocks.append(context_block)
                logger.info(f"✅ [Pydantic] Created context block {i+1} with {len(sub_contexts)} sub-contexts")
            
            # Criar context block adicional para instruções gerais (se houver)
            if general_instructions:
                # Converter instruções para strings se necessário
                instruction_texts = []
                for instruction in general_instructions:
                    if isinstance(instruction, str):
                        instruction_texts.append(instruction)
                    elif isinstance(instruction, dict):
                        instruction_texts.append(str(instruction.get('content', instruction)))
                    else:
                        instruction_texts.append(str(instruction))
                
                instruction_text = "\n".join(instruction_texts)
                
                # Criar content object para instruções
                from app.models.internal.context_models import InternalContextContent
                instruction_content = InternalContextContent(
                    description=instruction_texts,
                    raw_content=instruction_text,
                    content_source="general_instructions"
                )
                
                instruction_block = InternalContextBlock(
                    id=len(context_blocks) + 1,
                    type=[ContentType.TEXT],
                    content=instruction_content,
                    title="Instructions",
                    images=[],
                    sub_contexts=[]
                )
                
                context_blocks.append(instruction_block)
                logger.info(f"✅ [Pydantic] Created instruction block with general instructions")
            
            logger.info(f"🎉 [Pydantic] Successfully created {len(context_blocks)} Pydantic context blocks")
            return context_blocks
            
        except Exception as e:
            import traceback
            logger.error(f"❌ [Pydantic] Error creating Pydantic context blocks: {str(e)}")
            logger.error(f"❌ [Pydantic] Full traceback: {traceback.format_exc()}")
            return []
