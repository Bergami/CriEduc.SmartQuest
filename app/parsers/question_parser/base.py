from typing import Dict, Any, Optional, List, Tuple
from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions
from .context_question_mapper import ContextQuestionMapper
from .context_block_image_processor import ContextBlockImageProcessor

class QuestionParser:
    @staticmethod
    def extract(text: str, image_data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extrai questões e blocos de contexto do texto
        
        Args:
            text: Texto a ser analisado
            image_data: Dicionário opcional de imagens (id -> base64_data)
            
        Returns:
            Dicionário com questões e blocos de contexto
        """
        # Use improved context block detection
        context_blocks = detect_context_blocks(text)
        questions = detect_questions(text)
        
        # Use old matching as fallback, then apply new intelligent mapping
        linked_questions = match_context_to_questions(questions, context_blocks, text)
        
        # Apply new intelligent context-question mapping
        improved_questions = ContextQuestionMapper.map_contexts_to_questions(
            text, linked_questions, context_blocks
        )            # Enriquecer blocos de contexto com imagens se disponíveis
        if image_data:
            context_blocks = ContextBlockImageProcessor.enrich_context_blocks_with_images(
                context_blocks, image_data
            )
            
            # Salvar imagens em arquivo para depuração
            ContextBlockImageProcessor.save_images_to_file(image_data, "tests/extracted_images")

        return {
            "context_blocks": context_blocks,
            "questions": improved_questions
        }

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
        
        # Use the existing extract method to get raw data
        raw_data = QuestionParser.extract(text, image_data)
        
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
