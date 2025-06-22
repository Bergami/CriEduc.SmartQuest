from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions

class QuestionParser:
    @staticmethod
    def extract(text: str) -> dict:
        context_blocks = detect_context_blocks(text)
        questions = detect_questions(text)
        linked_questions = match_context_to_questions(questions, context_blocks, text)

        return {
            "context_blocks": context_blocks,
            "questions": linked_questions
        }
