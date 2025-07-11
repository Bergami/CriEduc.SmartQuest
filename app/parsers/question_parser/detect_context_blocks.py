from typing import List, Dict, Any
import re

def detect_context_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Detecta blocos de leitura (textos base) antes das questões.
    Retorna uma lista com: id, type, source, enunciado, paragraphs, title, hasImage.
    """
    blocks = []
    block_id = 1

    # Marcadores típicos de introdução de texto
    start_patterns = [
        r"Leia o texto a seguir",
        r"Analise o texto a seguir", 
        r"Analise a imagem abaixo",
        r"Observe (a|o) (imagem|gráfico|tabela)",
        r"Texto \d?:?",
        r"Baseando-se no texto",
        r"Com base no texto",
        r"Leia a crônica"
    ]
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    # Regex para detectar questões (NÃO devem ser blocos de contexto)
    question_regex = re.compile(r"^QUEST[ÃA]O\s+\d+", re.IGNORECASE)

    lines = text.splitlines()
    current_block = []
    inside_block = False

    for line in lines:
        line_stripped = line.strip()
        
        # Se encontrou uma questão, pare de capturar o bloco atual
        if question_regex.match(line_stripped):
            if inside_block and current_block:
                # Finalizar bloco atual antes da questão
                content = "\n".join(current_block).strip()
                has_image = any("imagem" in l.lower() for l in current_block)
                
                parsed_block = _parse_context_block_content(content, block_id, has_image)
                if _is_valid_context_block(parsed_block):
                    blocks.append(parsed_block)
                    block_id += 1
                
                current_block = []
                inside_block = False
            continue

        # Se encontrou marcador de início de texto
        if start_regex.search(line_stripped):
            if inside_block and current_block:
                # Finalizar bloco anterior
                content = "\n".join(current_block).strip()
                has_image = any("imagem" in l.lower() for l in current_block)
                
                parsed_block = _parse_context_block_content(content, block_id, has_image)
                if _is_valid_context_block(parsed_block):
                    blocks.append(parsed_block)
                    block_id += 1
                
                current_block = []
            
            inside_block = True
            current_block.append(line)
            continue

        # Se estamos dentro de um bloco, adicionar linha
        if inside_block:
            current_block.append(line)

    # Último bloco (caso não encerrado por questão)
    if inside_block and current_block:
        content = "\n".join(current_block).strip()
        has_image = any("imagem" in l.lower() for l in current_block)
        
        parsed_block = _parse_context_block_content(content, block_id, has_image)
        if _is_valid_context_block(parsed_block):
            blocks.append(parsed_block)

    return blocks


def _is_valid_context_block(block: Dict[str, Any]) -> bool:
    """
    Valida se um bloco é realmente um contexto de leitura, não uma questão.
    """
    title = block.get("title", "").lower()
    enunciado = block.get("enunciado", "").lower()
    
    # Filtrar blocos que são questões
    if "questão" in title or "questão" in enunciado:
        return False
    
    # Filtrar blocos que são alternativas (começam com (A), (B), etc.)
    if title.startswith("(") and len(title) > 1 and title[1] in "abcde":
        return False
    if enunciado.startswith("(") and len(enunciado) > 1 and enunciado[1] in "abcde":
        return False
        
    # Deve ter conteúdo significativo
    if len(enunciado) < 10:
        return False
        
    return True


def _parse_context_block_content(content: str, block_id: int, has_image: bool) -> Dict[str, Any]:
    """
    Parse context block content into structured format matching expected output.
    """
    lines = content.split('\n')
    
    # Extract title (usually the first line with instruction like "Leia o texto a seguir")
    title = ""
    enunciado = ""
    paragraphs = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # First meaningful line is usually the title/instruction
        if not title and any(pattern in line.lower() for pattern in ['leia', 'analise', 'observe', 'texto']):
            title = line
        elif not enunciado and title and line != title:
            # Next meaningful line after title is usually the beginning of the text
            enunciado = line
            # Collect remaining lines as paragraphs
            remaining_lines = [l.strip() for l in lines[i:] if l.strip()]
            paragraphs = remaining_lines
            break
    
    # If no clear structure found, use content as enunciado
    if not enunciado:
        enunciado = content
        paragraphs = [content]
    
    return {
        "id": block_id,
        "type": "reading_comprehension",
        "source": "exam_document",
        "enunciado": enunciado,
        "paragraphs": paragraphs,
        "title": title if title else f"Texto {block_id}",
        "hasImage": has_image
    }
