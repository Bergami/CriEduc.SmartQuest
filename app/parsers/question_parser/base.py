from typing import Dict, Any, Optional, List, Tuple
from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions
from .context_question_mapper import ContextQuestionMapper
from .context_block_image_processor import ContextBlockImageProcessor
from .legacy_adapter import extract_questions_from_paragraphs_legacy_compatible

class QuestionParser:
    @staticmethod
    def extract(text: str, image_data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        🚨 DEPRECATED: Use extract_from_paragraphs() instead
        
        This method is deprecated and only maintained for backward compatibility.
        It now redirects to the new SOLID-based extraction system.
        
        Args:
            text: Texto a ser analisado
            image_data: Dicionário opcional de imagens (id -> base64_data)
            
        Returns:
            Dicionário com questões e blocos de contexto
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning("🚨 DEPRECATED: QuestionParser.extract() is deprecated. Use extract_from_paragraphs() instead.")
        
        # 🆕 Redirecionar para novo sistema SOLID
        synthetic_paragraphs = [{"content": text}]
        return QuestionParser.extract_from_paragraphs(synthetic_paragraphs, image_data)

    @staticmethod
    def extract_typed(
        text: str, 
        image_data: Optional[Dict[str, str]] = None
    ) -> Tuple[List, List]:
        """
        PHASE 2 COMPLETE: Native Pydantic interface for QuestionParser.
        
        Extrai questoes e blocos de contexto retornando tipos Pydantic nativos.
        
        Args:
            text: Texto a ser analisado
            image_data: Dicionario opcional de imagens (id -> base64_data)
            
        Returns:
            Tuple[List[InternalQuestion], List[InternalContextBlock]]: 
                Questions and context blocks as native Pydantic models
        """
        # Import here to avoid circular imports
        from app.models.internal.question_models import InternalQuestion
        from app.models.internal.context_models import InternalContextBlock
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 🆕 Usar sempre extração SOLID - criar parágrafos sintéticos do texto
        logger.info("🔄 extract_typed: Converting text to synthetic paragraphs for SOLID extraction")
        synthetic_paragraphs = [{"content": text}]
        
        # Use the new SOLID extraction method
        raw_data = QuestionParser.extract_from_paragraphs(synthetic_paragraphs, image_data)
        
        # Convert to Pydantic models
        pydantic_questions = [
            InternalQuestion.from_legacy_question(q) 
            for q in raw_data["questions"]
        ]
        
        pydantic_context_blocks = [
            InternalContextBlock.from_legacy_context_block(cb) 
            for cb in raw_data["context_blocks"]
        ]
        
        return pydantic_questions, pydantic_context_blocks
    
    @staticmethod
    def extract_from_paragraphs(
        paragraphs: List[Dict[str, Any]], 
        image_data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        🆕 NOVA FUNCIONALIDADE: Extrai questões diretamente dos parágrafos do Azure
        
        Esta função usa a nova implementação baseada em princípios SOLID para extrair
        questões diretamente dos parágrafos do Azure Document Intelligence, oferecendo
        melhor performance e precisão.
        
        Args:
            paragraphs: Lista de parágrafos do Azure Document Intelligence
            image_data: Dicionário opcional de imagens (id -> base64_data)
            
        Returns:
            Dicionário com questões no formato legacy para compatibilidade
        """
        # Usar nova implementação SOLID via adaptador de compatibilidade
        result = extract_questions_from_paragraphs_legacy_compatible(paragraphs)
        
        # O adaptador já retorna no formato correto
        questions = result.get("questions", [])
        context_blocks = result.get("context_blocks", [])
        
        # Enriquecer com dados de imagem se disponível
        if image_data:
            # Aplicar enriquecimento de imagens nas questões
            for question in questions:
                if question.get('hasImage', False):
                    # Lógica para associar imagens às questões pode ser implementada aqui
                    pass
        
        return {
            "context_blocks": context_blocks,
            "questions": questions
        }
