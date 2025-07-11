from typing import Dict, Any
from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions
from .context_question_mapper import ContextQuestionMapper

class QuestionParser:
    @staticmethod
    def extract(text: str) -> Dict[str, Any]:
        # Use improved context block detection
        context_blocks = detect_context_blocks(text)
        questions = detect_questions(text)
        
        # Use old matching as fallback, then apply new intelligent mapping
        linked_questions = match_context_to_questions(questions, context_blocks, text)
        
        # Apply new intelligent context-question mapping
        improved_questions = ContextQuestionMapper.map_contexts_to_questions(
            text, linked_questions, context_blocks
        )

        return {
            "context_blocks": context_blocks,
            "questions": improved_questions
        }
