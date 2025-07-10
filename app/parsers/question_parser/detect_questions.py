from typing import List, Dict, Any
import re
from .extract_alternatives_from_lines import extract_alternatives_from_lines

def detect_questions(text: str) -> List[Dict[str, Any]]:
    """
    Detecta blocos de questões no texto da prova.
    Extrai número, enunciado, alternativas e se há referência a imagem.
    """
    pattern = r"(QUEST[ÃA]O\s+\d+\.?)"
    blocks = re.split(pattern, text)

    questions = []

    for i in range(1, len(blocks), 2):
        raw_number = blocks[i]
        raw_content = blocks[i + 1] if i + 1 < len(blocks) else ""

        match_number = re.search(r"\d+", raw_number)
        if not match_number:
            continue
        number = int(match_number.group())

        # Divide o conteúdo em linhas
        lines = raw_content.strip().splitlines()

        # ✅ Usa a função atualizada que retorna question_text, alternatives e último índice
        question_text, alternatives, _ = extract_alternatives_from_lines(lines)

        # ✅ Detecta presença de imagem com base no texto da questão
        has_image = "imagem" in question_text.lower() or "figura" in question_text.lower()

        questions.append({
            "number": number,
            "question": question_text,
            "alternatives": [alt.strip() for alt in alternatives],
            "hasImage": has_image,
            "context_id": None
        })

    return questions
