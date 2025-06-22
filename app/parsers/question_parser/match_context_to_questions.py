def match_context_to_questions(
    questions: list[dict],
    contexts: list[dict],
    text: str,
    max_distance: int = 1000
) -> list[dict]:
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
    context_positions = [
        (
            ctx["id"],
            text.find(ctx.get("raw_content", ctx.get("content", "")))
        )
        for ctx in contexts
    ]

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
    context_positions: list[tuple[int, int]],
    max_distance: int
) -> int | None:
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
