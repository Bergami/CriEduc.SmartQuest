"""
Advanced Context Block Builder - Refactored Version
Uses separated constants and enums for better maintainability
"""
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from dataclasses import dataclass

from app.core.constants.instruction_patterns import InstructionPatterns
from app.core.constants.content_types import (
    ContentType, FigureType, TextRole, ContextBlockType,
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
    text_role: TextRole = TextRole.UNKNOWN

@dataclass
class FigureInfo:
    """Enhanced figure information with spatial data"""
    id: str
    page_number: int
    bounding_regions: List[Dict]
    base64_image: Optional[str] = None
    associated_texts: List[TextSpan] = None
    azure_figure: Optional[Dict] = None  # Referência para a figura original do Azure
    figure_type: FigureType = FigureType.UNKNOWN
    content_type: ContentType = ContentType.UNKNOWN
    
    def __post_init__(self):
        if self.associated_texts is None:
            self.associated_texts = []

class RefactoredContextBlockBuilder:
    """
    Refactored context block builder using separated constants and enums
    """
    
    def __init__(self):
        self.instruction_patterns = InstructionPatterns()
        
        # Content type detection keywords
        self.content_keywords = {
            ContentType.CHARGE: ['charge', 'tirinha', 'quadrinho', 'cartoon', 'comic'],
            ContentType.PROPAGANDA: ['propaganda', 'anúncio', 'advertisement', 'publicidade'],
            ContentType.DIALOGUE: ['disse', 'falou', 'respondeu', 'perguntou'],
            ContentType.TITLE: ['texto', 'título', 'title'],
            ContentType.INSTRUCTION: ['analise', 'observe', 'leia', 'responda']
        }
    
    def analyze_azure_figures_dynamically(
        self, 
        azure_response: Dict[str, Any],
        images_base64: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Analisa figuras do Azure dinamicamente sem hardcoding
        
        Args:
            azure_response: Resposta do Azure Document Intelligence
            images_base64: Dicionário com imagens em base64
            
        Returns:
            Lista de context blocks estruturados
        """
        try:
            logger.info("🔧 DYNAMIC FIGURE ANALYSIS - Starting")
            
            # 1. Extrair figuras com informações espaciais
            figures = self._extract_figures_with_enhanced_info(azure_response)
            logger.info(f"📊 Extracted {len(figures)} figures with spatial data")
            
            # 2. Extrair spans de texto relevantes
            text_spans = self._extract_relevant_text_spans(azure_response)
            logger.info(f"📝 Extracted {len(text_spans)} relevant text spans")
            
            # 3. Encontrar instruções gerais (como "ANALISE OS TEXTO A SEGUIR")
            general_instructions = self._find_general_instructions(azure_response)
            logger.info(f"📋 Found {len(general_instructions)} general instructions")
            
            # 4. Associar textos às figuras baseado em proximidade espacial
            self._associate_texts_with_figures_enhanced(figures, text_spans)
            
            # 5. Adicionar imagens base64
            self._add_base64_images_to_figures(figures, images_base64)
            
            # 6. Criar context blocks baseado em análise dinâmica
            context_blocks = self._create_dynamic_context_blocks(
                figures, general_instructions, azure_response
            )
            
            logger.info(f"✅ Created {len(context_blocks)} dynamic context blocks")
            return context_blocks
            
        except Exception as e:
            logger.error(f"❌ Error in dynamic figure analysis: {str(e)}")
            return []
    
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
    
    def _add_base64_images_to_figures(self, figures: List[FigureInfo], images_base64: Dict[str, str]):
        """Adiciona imagens base64 às figuras"""
        for figure in figures:
            if figure.id in images_base64:
                figure.base64_image = images_base64[figure.id]
                logger.debug(f"   ✅ Added base64 image to {figure.id}")
    
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
                        'type': 'text',
                        'statement': statement,
                        'title': title if title else "Texto para análise",
                        'paragraphs': text_paragraphs,
                        'has_images': False,
                        'images': {}
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
        """Extrai TODOS os identificadores de sequência de uma figura"""
        sequences_found = []
        
        for text_span in figure.associated_texts:
            content_upper = text_span.content.upper()
            # Procurar por padrões como "TEXTO I:", "TEXTO II:", etc.
            matches = re.findall(r'TEXTO\s+([IVX]+)', content_upper)
            sequences_found.extend(matches)
        
        # Remover duplicatas e converter para lowercase
        unique_sequences = list(set(seq.lower() for seq in sequences_found))
        
        if len(unique_sequences) > 1:
            logger.debug(f"Figure {figure.id} has multiple sequences: {unique_sequences}")
        
        return unique_sequences
    
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
        
        # Context block principal
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': 'image_collection',
            'title': 'Análise de Textos',
            'statement': general_instruction or 'ANALISE OS TEXTO A SEGUIR:',
            'sub_contexts': sub_contexts,
            'has_images': True
        }
        
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
            'images': [figure.base64_image] if figure.base64_image else []
        }
        
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
        if not figure.base64_image:
            return None
        
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
        
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': context_type,
            'title': title,
            'statement': instruction,
            'content': {
                'description': image_texts  # Array direto com os textos
            },
            'images': [figure.base64_image],
            'has_images': True
        }
        
        logger.debug(f"Created individual context block: {title}")
        
        return context_block
    
    def _extract_complete_image_texts(self, figure: FigureInfo) -> List[str]:
        """Extrai todos os textos que estão dentro da área da imagem usando boundingRegions"""
        if not figure.azure_figure:
            return []
        
        # Obter boundingRegions da figura
        figure_regions = figure.azure_figure.get('boundingRegions', [])
        if not figure_regions:
            return []
        
        # Obter informações de página e coordenadas da figura
        figure_page = figure_regions[0].get('pageNumber', 1)
        figure_polygon = figure_regions[0].get('polygon', [])
        
        if len(figure_polygon) < 8:  # Precisa de pelo menos 4 pontos (x,y cada)
            return []
        
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
                    margin = 0.1  # Margem de tolerância
                    if (para_x_min >= fig_x_min - margin and para_x_max <= fig_x_max + margin and
                        para_y_min >= fig_y_min - margin and para_y_max <= fig_y_max + margin):
                        
                        content = paragraph.get('content', '').strip()
                        if content and len(content) > 1:
                            image_texts.append(content)
        
        # Se não conseguiu pelo método acima, usar os textos associados existentes
        if not image_texts:
            for text_span in figure.associated_texts:
                content = text_span.content.strip()
                if content and len(content) > 1 and not content.upper().startswith('QUESTÃO'):
                    image_texts.append(content)
        
        return image_texts
    
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
        all_texts = []
        content_types = set()
        
        for figure in group_figures:
            if figure.base64_image:
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
        
        context_text = '\n'.join(relevant_texts) if relevant_texts else f"Contexto para {group_name}"
        
        context_block = {
            'id': 0,  # Será renumerado depois
            'type': 'image',
            'title': group_name.replace('_', ' ').title(),
            'content': context_text,
            'images': images,
            'has_images': len(images) > 0
        }
        
        logger.debug(f"Created simple context block: {group_name} with {len(images)} images")
        
        return context_block
    
        logger.debug(f"Created simple context block: {group_name} with {len(images)} images")
        
        return context_block
    
    def _determine_context_block_type(
        self, 
        content_types: set, 
        texts: List[str]
    ) -> ContextBlockType:
        """Determina tipo do context block baseado nos tipos de conteúdo"""
        if ContentType.CHARGE in content_types:
            return ContextBlockType.CHARGE_CONTEXT
        elif ContentType.PROPAGANDA in content_types:
            return ContextBlockType.PROPAGANDA_CONTEXT
        elif any(content_type in [ContentType.DIALOGUE, ContentType.PARAGRAPH] for content_type in content_types):
            return ContextBlockType.TEXT_CONTEXT
        elif len(content_types) > 1:
            return ContextBlockType.MIXED_CONTEXT
        else:
            return ContextBlockType.UNKNOWN
    
    def remove_associated_figures_from_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove campos desnecessários 'associated_figures' e 'figure_ids' do resultado da API"""
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
