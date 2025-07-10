from typing import List, Dict, Any
import re

def detect_context_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Detecta blocos de leitura (textos base) antes das questões.
    Retorna uma lista com: id, content, hasImage.
    """
    blocks = []
    block_id = 1

    # Marcadores típicos de introdução de texto
    start_patterns = [
        r"Leia o texto a seguir",
        r"Analise o texto a seguir",
        r"Observe (a|o) (imagem|gráfico|tabela)",
        r"Texto \d?:?",
        r"Baseando-se no texto",
        r"Com base no texto"
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
                blocks.append({
                    "id": block_id,
                    "content": "\n".join(current_block).strip(),
                    "hasImage": any("imagem" in l.lower() for l in current_block)
                })
                block_id += 1
                current_block = []
            inside_block = True
            current_block.append(line)
            continue

        if question_regex.search(line):
            if inside_block and current_block:
                blocks.append({
                    "id": block_id,
                    "content": "\n".join(current_block).strip(),
                    "hasImage": any("imagem" in l.lower() for l in current_block)
                })
                block_id += 1
                current_block = []
                inside_block = False
            continue

        if inside_block:
            current_block.append(line)

    # Último bloco (caso não encerrado por questão)
    if inside_block and current_block:
        blocks.append({
            "id": block_id,
            "content": "\n".join(current_block).strip(),
            "hasImage": any("imagem" in l.lower() for l in current_block)
        })

    return blocks
