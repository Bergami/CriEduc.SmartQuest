import re
from app.utils.split_into_paragraphs import split_into_paragraphs
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

    title = ""
    source = ""
    enunciado = ""
    paragraphs_text = []

    remaining = lines[:]

    # Detectar fonte no final (últimas 4 linhas)
    for i in reversed(range(min(4, len(remaining)))):
        idx = len(remaining) - 1 - i
        line = remaining[idx]
        if "http" in line or re.search(r"\(.*?\)|\b[Aa]cesso em[:\-]", line):
            source = line.strip()
            remaining.pop(idx)
            break

    # Detectar título dinamicamente com base em formatação e posição
    title_candidates = []
    while remaining and len(title_candidates) < 2:
        l = remaining[0]
        if l.isupper() or l.endswith("?") or len(l.split()) <= 6:
            title_candidates.append(remaining.pop(0))
        else:
            break
    title = " ".join(title_candidates).strip()

    # Ajuste de enunciado
    if remaining and re.search(r"responder.*quest(ões|ão)", remaining[0], re.IGNORECASE):
        enunciado = remaining.pop(0).strip()

    # Caso especial: se título parecer ser o enunciado
    if not enunciado and title and re.search(r"responder.*quest(ões|ão)", title, re.IGNORECASE):
        enunciado = title
        title = ""

    # Parágrafos extraídos do restante
    paragraphs_text = split_into_paragraphs("\n".join(remaining))

    return {
        "id": block_id,
        "type": "text",
        "source": source,
        "enunciado": enunciado,
        "paragraphs": paragraphs_text,
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

    start_patterns = [
        r"Leia o texto a seguir",
        r"Analise o texto a seguir",
        r"Leia este texto",
        r"Analise a imagem",
        r"Observe (a|o) (imagem|gr[áa]fico|tabela)",
        r"^Texto\s*\d*[:.-]?$",
        r"Baseando-se no texto",
        r"Com base no texto",
        r"Após ler atentamente o texto.*?responda.*?quest(ões|ão)"
    ]
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    question_regex = re.compile(r"(QUEST[ÃA]O\s+\d+|QUEST[ÃA]O\s+\d+\.)", re.IGNORECASE)

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

    if inside_block and current_block:
        blocks.append(
            _parse_block(
                block_id,
                "\n".join(current_block).strip(),
                any("imagem" in l.lower() for l in current_block),
            )
        )

    return blocks
