import re


def _parse_block(block_id: int, content: str, has_image: bool) -> dict:
    """Converte o texto cru do bloco em uma estrutura mais detalhada."""
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    if has_image:
        enunciado = lines[0] if lines else ""
        return {
            "id": block_id,
            "type": "image",
            "source": "",
            "enunciado": enunciado,
            "content": "",
            "_comment": "Adicionar a imagem em base64 aqui na propriedade 'content'",
            "hasImage": True,
            "raw_content": content,
        }

    source = lines[0] if lines else ""
    enunciado = lines[1] if len(lines) > 1 else ""
    title = lines[-1] if len(lines) > 2 else ""
    paragraph_lines = lines[2:-1] if len(lines) > 3 else []

    return {
        "id": block_id,
        "type": "text",
        "source": source,
        "enunciado": enunciado,
        "paragraphs": [{"text": p} for p in paragraph_lines],
        "title": title,
        "hasImage": False,
        "raw_content": content,
    }

def detect_context_blocks(text: str) -> list[dict]:
    """
    Detecta blocos de leitura (textos base) antes das questões.
    Retorna uma lista com: id, content, hasImage.
    """
    blocks: list[dict] = []
    block_id = 1

    # Marcadores típicos de introdução de texto
    start_patterns = [
        r"Leia o texto a seguir",
        r"Analise o texto a seguir",
        r"Leia este texto",
        r"Analise a imagem",
        r"Observe (a|o) (imagem|gr[áa]fico|tabela)",
        r"^Texto\s*\d*[:.-]?$",
        r"Baseando-se no texto",
        r"Com base no texto",
    ]
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    # Ponto de corte: antes da próxima questão
    question_regex = re.compile(r"(QUESTÃO\s+\d+|QUEST[ÃA]O\s+\d+)", re.IGNORECASE)

    lines = text.splitlines()
    current_block = []
    inside_block = False

    for line in lines:
        if start_regex.search(line):
            if inside_block and current_block:
                blocks.append(
                    _parse_block(
                        block_id,
                        "\n".join(current_block).strip(),
                        any("imagem" in l.lower() for l in current_block),
                    )
                )
                block_id += 1
                current_block = []
            inside_block = True
            current_block.append(line)
            continue

        if question_regex.search(line):
            if inside_block and current_block:
                blocks.append(
                    _parse_block(
                        block_id,
                        "\n".join(current_block).strip(),
                        any("imagem" in l.lower() for l in current_block),
                    )
                )
                block_id += 1
                current_block = []
                inside_block = False
            continue

        if inside_block:
            current_block.append(line)

    # Último bloco (caso não encerrado por questão)
    if inside_block and current_block:
        blocks.append(
            _parse_block(
                block_id,
                "\n".join(current_block).strip(),
                any("imagem" in l.lower() for l in current_block),
            )
        )

    return blocks
