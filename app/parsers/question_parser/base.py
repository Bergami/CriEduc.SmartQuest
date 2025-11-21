from typing import Dict, Any, Optional, List, Tuple
from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions
from .context_question_mapper import ContextQuestionMapper
from .legacy_adapter import extract_questions_from_paragraphs

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
        🔧 CORRIGIDO: Native Pydantic interface for QuestionParser.
        
        Extrai questoes e blocos de contexto retornando tipos Pydantic nativos.
        Inclui validação adequada para prevenir perda de dados durante conversão.
        
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
        
        # 🔧 CORREÇÃO CRÍTICA: NÃO converter parágrafos para texto único!
        # O problema era que estava passando texto combinado em vez de parágrafos separados
        logger.info("🔄 extract_typed: Using text as single paragraph (preserving original logic)")
        
        # ⚠️ IMPORTANTE: extract_from_paragraphs espera parágrafos separados, não texto único
        # Se recebemos texto único, assumimos que é para compatibilidade e criamos parágrafo sintético
        synthetic_paragraphs = [{"content": text}]
        
        # Use the SOLID extraction method
        raw_data = QuestionParser.extract_from_paragraphs(synthetic_paragraphs, image_data)
        
        # 🔧 CORREÇÃO: Validar dados antes da conversão
        questions_list = raw_data.get("questions", [])
        context_blocks_list = raw_data.get("context_blocks", [])
        
        logger.info(f"🔍 extract_typed: Raw data has {len(questions_list)} questions, {len(context_blocks_list)} context blocks")
        
        # Convert to Pydantic models with validation
        pydantic_questions = []
        for i, q in enumerate(questions_list):
            try:
                # 🔧 CORREÇÃO: Validar estrutura antes da conversão
                if not isinstance(q, dict):
                    logger.error(f"❌ Question {i} is not a dict: {type(q)}")
                    continue
                    
                if not q.get("question"):
                    logger.error(f"❌ Question {i} has empty 'question' field: {q}")
                    continue
                
                # Debug da questão antes da conversão
                logger.debug(f"🔍 Converting question {i+1}: number={q.get('number')}, question_length={len(q.get('question', ''))}, alternatives={len(q.get('alternatives', []))}")
                
                pydantic_q = InternalQuestion.from_dict(q)
                pydantic_questions.append(pydantic_q)
                logger.info(f"✅ Question {i+1} converted successfully - content: {len(pydantic_q.content.statement)} chars, options: {len(pydantic_q.options)}")
                
            except Exception as e:
                logger.error(f"❌ Error converting question {i}: {e}")
                logger.error(f"❌ Question data: {q}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                continue
        
        # Convert context blocks with validation
        pydantic_context_blocks = []
        for i, cb in enumerate(context_blocks_list):
            try:
                if not isinstance(cb, dict):
                    logger.warning(f"⚠️ Context block {i} is not a dict: {type(cb)}")
                    continue
                    
                pydantic_cb = InternalContextBlock.from_dict(cb)
                pydantic_context_blocks.append(pydantic_cb)
                logger.debug(f"✅ Context block {i+1} converted successfully")
                
            except Exception as e:
                logger.error(f"❌ Error converting context block {i}: {e}")
                logger.error(f"❌ Context block data: {cb}")
                continue
        
        logger.info(f"🔧 extract_typed: Successfully converted {len(pydantic_questions)} questions, {len(pydantic_context_blocks)} context blocks")
        
        # 🔧 CORREÇÃO: Validação final antes de retornar
        if len(pydantic_questions) == 0 and len(questions_list) > 0:
            logger.error("❌ CRITICAL: All questions lost during Pydantic conversion!")
            logger.error(f"❌ Original questions: {questions_list}")
        
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
        result = extract_questions_from_paragraphs(paragraphs)
        
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
