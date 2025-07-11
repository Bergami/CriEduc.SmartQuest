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
        r"Leia a crônica",
        r"Leia este texto"
    ]
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    # Regex para detectar questões (NÃO devem ser blocos de contexto)
    question_regex = re.compile(r"^QUEST[ÃA]O\s+\d+", re.IGNORECASE)

    lines = text.splitlines()
    
    # Primeiro detectar todos os marcadores de início na ordem que aparecem
    all_blocks = []
    
    # Detectar blocos normais
    current_block = []
    inside_block = False

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Se encontrou uma questão, pare de capturar o bloco atual
        if question_regex.match(line_stripped):
            if inside_block and current_block:
                # Finalizar bloco atual antes da questão
                content = "\n".join(current_block).strip()
                has_image = any("imagem" in l.lower() for l in current_block)
                
                # Para blocos de imagem, tentar encontrar texto distante
                if has_image and "analise a imagem" in content.lower():
                    image_text = _find_image_text_nearby(lines, i - len(current_block), max_distance=20)
                    if image_text:
                        # Criar bloco especial de imagem com texto encontrado
                        parsed_block = {
                            "id": block_id,
                            "type": ["text", "image"],
                            "source": "exam_document",
                            "statement": current_block[0].strip(),
                            "paragraphs": [image_text["text"]],
                            "title": image_text["text"],
                            "hasImage": True,
                            "_line_position": i - len(current_block)  # Para ordenação
                        }
                    else:
                        parsed_block = _parse_context_block_content(content, block_id, has_image)
                        parsed_block["_line_position"] = i - len(current_block)
                else:
                    parsed_block = _parse_context_block_content(content, block_id, has_image)
                    parsed_block["_line_position"] = i - len(current_block)
                
                if _is_valid_context_block(parsed_block):
                    all_blocks.append(parsed_block)
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
                
                # Para blocos de imagem, tentar encontrar texto distante
                if has_image and "analise a imagem" in content.lower():
                    image_text = _find_image_text_nearby(lines, i - len(current_block), max_distance=20)
                    if image_text:
                        parsed_block = {
                            "id": block_id,
                            "type": ["text", "image"],
                            "source": "exam_document",
                            "statement": current_block[0].strip(),
                            "paragraphs": [image_text["text"]],
                            "title": image_text["text"],
                            "hasImage": True,
                            "_line_position": i - len(current_block)
                        }
                    else:
                        parsed_block = _parse_context_block_content(content, block_id, has_image)
                        parsed_block["_line_position"] = i - len(current_block)
                else:
                    parsed_block = _parse_context_block_content(content, block_id, has_image)
                    parsed_block["_line_position"] = i - len(current_block)
                
                if _is_valid_context_block(parsed_block):
                    all_blocks.append(parsed_block)
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
        
        # Para blocos de imagem, tentar encontrar texto distante
        if has_image and "analise a imagem" in content.lower():
            image_text = _find_image_text_nearby(lines, len(lines) - len(current_block), max_distance=20)
            if image_text:
                parsed_block = {
                    "id": block_id,
                    "type": ["text", "image"],
                    "source": "exam_document",
                    "statement": current_block[0].strip(),
                    "paragraphs": [image_text["text"]],
                    "title": image_text["text"],
                    "hasImage": True,
                    "_line_position": len(lines) - len(current_block)
                }
            else:
                parsed_block = _parse_context_block_content(content, block_id, has_image)
                parsed_block["_line_position"] = len(lines) - len(current_block)
        else:
            parsed_block = _parse_context_block_content(content, block_id, has_image)
            parsed_block["_line_position"] = len(lines) - len(current_block)
        
        if _is_valid_context_block(parsed_block):
            all_blocks.append(parsed_block)

    # Ordenar blocos pela posição no texto e reajustar IDs
    all_blocks.sort(key=lambda x: x.get("_line_position", 0))
    
    # Reajustar IDs e remover campo temporário
    for i, block in enumerate(all_blocks, 1):
        block["id"] = i
        if "_line_position" in block:
            del block["_line_position"]

    return all_blocks


def _is_valid_context_block(block: Dict[str, Any]) -> bool:
    """
    Valida se um bloco é realmente um contexto de leitura, não uma questão.
    """
    title = block.get("title", "").lower()
    statement = block.get("statement", "").lower()
    
    # Filtrar blocos que são questões
    if "questão" in title or "questão" in statement:
        return False
    
    # Filtrar blocos que são alternativas (começam com (A), (B), etc.)
    if title.startswith("(") and len(title) > 1 and title[1] in "abcde":
        return False
    if statement.startswith("(") and len(statement) > 1 and statement[1] in "abcde":
        return False
        
    # Deve ter conteúdo significativo no título
    if len(title) < 3:
        return False
        
    return True


def _determine_context_type(paragraphs: List[str], has_image: bool, instruction: str) -> List[str]:
    """
    Determina o tipo do context_block baseado no conteúdo e presença de imagem.
    Retorna uma lista com os tipos: ["text"], ["image"], ou ["text", "image"]
    """
    types = []
    
    # Verificar se há conteúdo textual significativo
    has_meaningful_text = False
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        # Considerar texto significativo se tiver mais de 20 caracteres e não for só uma instrução
        if (len(paragraph) > 20 and 
            not paragraph.lower().startswith(('analise a imagem', 'observe a imagem', 'veja a imagem'))):
            has_meaningful_text = True
            break
    
    # Se não há parágrafos significativos, verificar a instrução
    if not has_meaningful_text and instruction:
        instruction_lower = instruction.lower()
        # Se a instrução não é apenas sobre imagem, considerar como texto
        if not any(word in instruction_lower for word in ['imagem', 'figura', 'gráfico', 'analise a imagem']):
            has_meaningful_text = True
    
    # Adicionar tipos baseado no conteúdo
    if has_meaningful_text:
        types.append("text")
    
    if has_image:
        types.append("image")
    
    # Se não há nem texto nem imagem, considerar como texto por padrão
    if not types:
        types.append("text")
    
    return types


def _parse_context_block_content(content: str, block_id: int, has_image: bool) -> Dict[str, Any]:
    """
    Parse context block content into structured format matching expected output.
    """
    lines = content.split('\n')
    
    # Extract instruction and title correctly
    instruction = ""
    text_title = ""
    paragraphs = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # First meaningful line is usually the instruction (like "Leia o texto a seguir")
        if not instruction and any(pattern in line.lower() for pattern in ['leia', 'analise', 'observe', 'texto']):
            instruction = line
        elif not text_title and instruction and line != instruction:
            # Next meaningful line after instruction is usually the title of the text
            text_title = line
            # Collect remaining lines as paragraphs
            remaining_lines = [l.strip() for l in lines[i:] if l.strip()]
            paragraphs = remaining_lines
            break
    
    # If no clear structure found, try to extract from content
    if not text_title and not instruction:
        # Look for patterns that might be titles (ALL CAPS, short lines, etc.)
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and line.isupper():
                text_title = line
                break
        
        if not text_title:
            text_title = content.split('\n')[0].strip() if content else f"Texto {block_id}"
        
        instruction = content if not text_title else ""
        paragraphs = [content]
    
    # Determinar o tipo do context_block
    context_types = _determine_context_type(paragraphs, has_image, instruction)
    
    return {
        "id": block_id,
        "type": context_types,
        "source": "exam_document",
        "statement": instruction if instruction else f"Leia o texto {block_id}",
        "paragraphs": paragraphs,
        "title": text_title if text_title else f"Texto {block_id}",
        "hasImage": has_image
    }


def _find_image_text_nearby(lines: List[str], instruction_line: int, max_distance: int = 20) -> Dict[str, Any]:
    """
    Procura por texto que parece ser extraído de imagem nas linhas próximas.
    """
    # Padrões específicos para texto extraído de imagem
    specific_patterns = [
        r"FAVOR.*NÃO.*DEXAR",
        r"FAVOR.*NAO.*DEXAR", 
    ]
    
    # Padrões gerais para texto de imagem (mais restritivos)
    general_patterns = [
        r"^[A-Z\s]{15,}$",  # Linha só com maiúsculas, pelo menos 15 chars
        r"^[A-Z][A-Z\s]*[A-Z]$",  # Começa e termina com maiúscula, só maiúsculas/espaços no meio
    ]
    
    question_regex = re.compile(r"^QUEST[ÃA]O\s+\d+", re.IGNORECASE)
    
    # Primeiro procurar por padrões específicos conhecidos
    for i in range(instruction_line + 1, min(len(lines), instruction_line + max_distance + 1)):
        line = lines[i].strip()
        
        if not line:
            continue
            
        # Pular questões
        if question_regex.match(line):
            continue
            
        # Pular alternativas de questões (A), (B), etc.
        if re.match(r"^\([ABCDE]\)", line):
            continue
            
        # Pular comandos de leitura
        if any(cmd in line.lower() for cmd in ['leia o texto', 'analise o texto', 'observe']):
            continue
            
        # Verificar padrões específicos primeiro
        for pattern in specific_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return {
                    "text": line,
                    "line_index": i,
                    "distance": i - instruction_line
                }
    
    # Se não encontrou padrões específicos, procurar por padrões gerais
    for i in range(instruction_line + 1, min(len(lines), instruction_line + max_distance + 1)):
        line = lines[i].strip()
        
        if not line:
            continue
            
        # Pular questões
        if question_regex.match(line):
            continue
            
        # Pular alternativas de questões (A), (B), etc.
        if re.match(r"^\([ABCDE]\)", line):
            continue
            
        # Pular comandos de leitura
        if any(cmd in line.lower() for cmd in ['leia o texto', 'analise o texto', 'observe']):
            continue
            
        # Verificar padrões gerais
        for pattern in general_patterns:
            if re.match(pattern, line):
                return {
                    "text": line,
                    "line_index": i,
                    "distance": i - instruction_line
                }
    
    return None
