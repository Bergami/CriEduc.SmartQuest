"""
Azure Figure Processor

Responsável por processar e categorizar figuras do Azure Document Intelligence
com base na análise das coordenadas e contexto.
"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class AzureFigureProcessor:
    """
    Processador especializado para figuras do Azure Document Intelligence.
    
    Responsabilidades:
    - Processar figures com boundingRegions e polygon
    - Categorizar por tipo (header, content, etc.)
    - Associar figures a contextos e questões
    - Ordenar por posição no documento
    """
    
    @staticmethod
    def process_figures_from_azure_response(azure_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processa todas as figuras do response do Azure
        
        Args:
            azure_response: Response completo do Azure Document Intelligence
            
        Returns:
            Lista de figuras processadas e categorizadas
        """
        figures = azure_response.get('figures', [])
        paragraphs = azure_response.get('paragraphs', [])
        
        if not figures:
            logger.info("Nenhuma figura encontrada no response do Azure")
            return []
        
        logger.info(f"Processando {len(figures)} figuras do Azure")
        
        processed_figures = []
        for figure in figures:
            processed_figure = AzureFigureProcessor._process_single_figure(figure, paragraphs)
            if processed_figure:
                processed_figures.append(processed_figure)
        
        # Ordenar por página e posição
        processed_figures.sort(key=lambda f: (f['page_number'], f['y_position']))
        
        logger.info(f"Figuras processadas: {len(processed_figures)}")
        return processed_figures
    
    @staticmethod
    def _process_single_figure(figure: Dict[str, Any], paragraphs: List[Dict]) -> Dict[str, Any]:
        """
        Processa uma única figura
        """
        figure_id = figure.get('id', 'unknown')
        
        if not figure.get('boundingRegions'):
            logger.warning(f"Figura {figure_id} sem boundingRegions")
            return None
        
        bounding_region = figure['boundingRegions'][0]
        page_number = bounding_region.get('pageNumber', 1)
        polygon = bounding_region.get('polygon', [])
        
        if len(polygon) < 8:  # Precisa de pelo menos 4 pontos (x,y)
            logger.warning(f"Figura {figure_id} com polygon inválido")
            return None
        
        # Extrair informações de posição
        position_info = AzureFigureProcessor._extract_position_info(polygon)
        
        # Classificar tipo da figura
        figure_type = AzureFigureProcessor._classify_figure_type(figure, paragraphs, position_info)
        
        # Extrair contexto se disponível
        context_info = AzureFigureProcessor._extract_figure_context(figure, paragraphs)
        
        return {
            'id': figure_id,
            'page_number': page_number,
            'polygon': polygon,
            'x_position': position_info['x_center'],
            'y_position': position_info['y_center'],
            'width': position_info['width'],
            'height': position_info['height'],
            'type': figure_type,
            'context': context_info,
            'caption': figure.get('caption', {}).get('content', ''),
            'spans': figure.get('spans', []),
            'elements': figure.get('elements', [])
        }
    
    @staticmethod
    def _extract_position_info(polygon: List[float]) -> Dict[str, float]:
        """
        Extrai informações de posição do polygon
        Polygon format: [x1, y1, x2, y2, x3, y3, x4, y4]
        """
        x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
        y_coords = [polygon[i] for i in range(1, len(polygon), 2)]
        
        return {
            'x_min': min(x_coords),
            'x_max': max(x_coords),
            'y_min': min(y_coords),
            'y_max': max(y_coords),
            'x_center': sum(x_coords) / len(x_coords),
            'y_center': sum(y_coords) / len(y_coords),
            'width': max(x_coords) - min(x_coords),
            'height': max(y_coords) - min(y_coords)
        }
    
    @staticmethod
    def _classify_figure_type(figure: Dict[str, Any], paragraphs: List[Dict], position_info: Dict[str, float]) -> str:
        """
        Classifica o tipo da figura baseado em contexto e posição
        """
        page_number = figure['boundingRegions'][0]['pageNumber']
        y_position = position_info['y_center']
        
        # Verificar se tem caption
        caption = figure.get('caption', {}).get('content', '').lower()
        
        if caption:
            if 'charge' in caption or 'tirinha' in caption:
                return 'comic_strip'
            elif 'propaganda' in caption:
                return 'advertisement'
            elif 'texto' in caption:
                return 'text_block'
            elif 'foto' in caption or 'imagem' in caption:
                return 'image'
        
        # Classificar por posição
        if page_number == 1 and y_position < 0.4:  # Primeira página, terço superior
            return 'header'
        elif y_position > 0.8:  # Parte inferior da página
            return 'footer'
        else:
            return 'content'
    
    @staticmethod
    def _extract_figure_context(figure: Dict[str, Any], paragraphs: List[Dict]) -> Dict[str, Any]:
        """
        Extrai contexto relacionado à figura
        """
        context = {
            'related_paragraphs': [],
            'text_content': '',
            'preceding_text': '',
            'following_text': ''
        }
        
        # Verificar elementos relacionados
        elements = figure.get('elements', [])
        for element in elements:
            if element.startswith('/paragraphs/'):
                try:
                    para_index = int(element.split('/')[-1])
                    if para_index < len(paragraphs):
                        para = paragraphs[para_index]
                        context['related_paragraphs'].append({
                            'index': para_index,
                            'content': para.get('content', ''),
                            'role': para.get('role', '')
                        })
                        context['text_content'] += para.get('content', '') + ' '
                except (ValueError, IndexError):
                    continue
        
        # Buscar texto próximo baseado em spans
        spans = figure.get('spans', [])
        if spans and paragraphs:
            span = spans[0]
            offset = span.get('offset', 0)
            length = span.get('length', 0)
            
            # Encontrar parágrafos antes e depois
            for para in paragraphs:
                para_spans = para.get('spans', [])
                for para_span in para_spans:
                    para_offset = para_span.get('offset', 0)
                    para_length = para_span.get('length', 0)
                    
                    # Parágrafo antes da figura
                    if para_offset + para_length <= offset:
                        context['preceding_text'] = para.get('content', '')
                    
                    # Parágrafo depois da figura
                    elif para_offset >= offset + length:
                        if not context['following_text']:  # Pegar apenas o primeiro
                            context['following_text'] = para.get('content', '')
        
        return context
    
    @staticmethod
    def categorize_figures_by_type(processed_figures: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Categoriza figuras por tipo
        """
        categories = {
            'header': [],
            'content': [],
            'advertisements': [],
            'comic_strips': [],
            'text_blocks': [],
            'images': [],
            'footer': []
        }
        
        for figure in processed_figures:
            figure_type = figure.get('type', 'content')
            
            if figure_type == 'header':
                categories['header'].append(figure)
            elif figure_type == 'advertisement':
                categories['advertisements'].append(figure)
            elif figure_type == 'comic_strip':
                categories['comic_strips'].append(figure)
            elif figure_type == 'text_block':
                categories['text_blocks'].append(figure)
            elif figure_type == 'image':
                categories['images'].append(figure)
            elif figure_type == 'footer':
                categories['footer'].append(figure)
            else:
                categories['content'].append(figure)
        
        return categories
    
    @staticmethod
    def associate_figures_to_questions(figures: List[Dict[str, Any]], questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Associa figuras às questões baseado em proximidade e contexto
        """
        updated_questions = []
        
        for question in questions:
            question_copy = question.copy()
            associated_figures = []
            
            # Buscar figuras próximas ou mencionadas
            for figure in figures:
                if AzureFigureProcessor._is_figure_related_to_question(figure, question):
                    associated_figures.append(figure['id'])
            
            question_copy['associated_figures'] = associated_figures
            updated_questions.append(question_copy)
        
        return updated_questions
    
    @staticmethod
    def _is_figure_related_to_question(figure: Dict[str, Any], question: Dict[str, Any]) -> bool:
        """
        Verifica se uma figura está relacionada a uma questão
        """
        # Verificar menções no texto da questão
        question_text = question.get('question', '').lower()
        
        # Menções diretas
        if ('imagem' in question_text or 'figura' in question_text or 
            'charge' in question_text or 'tirinha' in question_text or
            'propaganda' in question_text or 'texto' in question_text):
            return True
        
        # Verificar proximidade por posição
        # Se a questão menciona "acima", "abaixo", "seguir", etc.
        proximity_keywords = ['acima', 'abaixo', 'seguir', 'anterior', 'analise']
        if any(keyword in question_text for keyword in proximity_keywords):
            return True
        
        return False
