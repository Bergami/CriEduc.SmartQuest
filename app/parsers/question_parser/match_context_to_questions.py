from typing import List, Dict, Any, Optional, Tuple


def match_context_to_questions(
    questions: List[Dict[str, Any]],
    contexts: List[Dict[str, Any]],
    text: str,
    max_distance: int = 1000
) -> List[Dict[str, Any]]:
    """
    Associa cada questão ao contexto mais próximo (antes ou depois),
    desde que dentro de um limite de distância.
    
    Retorna a lista de questões com o campo 'context_id' adicionado.
    """
    # Localiza a posição das questões no texto
    question_positions = [
        (q["number"], text.find(q["question"]))
        for q in questions
    ]

    # Localiza a posição dos contextos no texto
    context_positions = []
    for ctx in contexts:
        # Support both old format (statement) and new format (content)
        context_text = ctx.get("statement") or ctx.get("content") or ctx.get("title", "")
        if context_text:
            # Use case-insensitive search for better matching
            import re
            pattern = re.escape(context_text[:100])  # Escape special regex chars
            match = re.search(pattern, text, re.IGNORECASE)
            position = match.start() if match else text.lower().find(context_text[:100].lower())
            context_positions.append((ctx["id"], position))
        else:
            context_positions.append((ctx["id"], -1))

    result = []

    for q_num, q_pos in question_positions:
        context_id = _find_closest_context_id(q_pos, context_positions, max_distance)

        # Atualiza a questão com o context_id
        matched = next((q for q in questions if q["number"] == q_num), None)
        if matched:
            matched["context_id"] = context_id
            result.append(matched)

    return result


def _find_closest_context_id(
    q_pos: int,
    context_positions: List[Tuple[int, int]],
    max_distance: int
) -> Optional[int]:
    """
    Retorna o id do contexto mais próximo da posição da questão,
    se estiver dentro da distância máxima permitida.
    """
    closest_id = None
    min_distance = float("inf")

    for ctx_id, ctx_pos in context_positions:
        distance = abs(q_pos - ctx_pos)
        if distance < min_distance and distance <= max_distance:
            min_distance = distance
            closest_id = ctx_id

    return closest_id
