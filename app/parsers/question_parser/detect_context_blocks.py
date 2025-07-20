from typing import List, Dict, Any
import re

def detect_context_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Detects reading blocks (base texts) before questions.
    Returns a list with: id, type, source, statement, paragraphs, title, hasImage.
    """
    blocks = []
    block_id = 1

    # Typical text introduction markers
    start_patterns = [
        r"Leia o texto a seguir",  # Read the following text
        r"Analise o texto a seguir",  # Analyze the following text
        r"Analise a imagem abaixo",  # Analyze the image below
        r"Observe (a|o) (imagem|gráfico|tabela)",  # Observe the image/graph/table
        r"Texto \d?:?",  # Text #:
        r"Baseando-se no texto",  # Based on the text
        r"Com base no texto",  # Based on the text
        r"Leia a crônica",  # Read the chronicle
        r"Leia este texto"  # Read this text
    ]
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    # Regex to detect questions (should NOT be context blocks)
    question_regex = re.compile(r"^QUEST[ÃA]O\s+\d+", re.IGNORECASE)

    lines = text.splitlines()
    
    # First detect all start markers in the order they appear
    all_blocks = []
    
    # Detect normal blocks
    current_block = []
    inside_block = False

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # If a question is found, stop capturing the current block
        if question_regex.match(line_stripped):
            if inside_block and current_block:
                # Finalize current block before the question
                content = "\n".join(current_block).strip()
                has_image = any("imagem" in l.lower() for l in current_block)
                
                # Para blocos de imagem, tentar encontrar texto distante
                if has_image and "analise a imagem" in content.lower():
                    image_text = _find_image_text_nearby(lines, i - len(current_block), max_distance=20)
                    if image_text:
                        # Create special image block with found text
                        parsed_block = {
                            "id": block_id,
                            "type": ["text", "image"],
                            "source": "exam_document",
                            "statement": current_block[0].strip(),
                            "paragraphs": [image_text["text"]],
                            "title": image_text["text"],
                            "hasImage": True,
                            "_line_position": i - len(current_block)  # For sorting
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

        # If a text start marker is found
        if start_regex.search(line_stripped):
            if inside_block and current_block:
                # Finalize previous block
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

        # If we're inside a block, add the line
        if inside_block:
            current_block.append(line)

    # Last block (in case not ended by a question)
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

    # Sort blocks by position in text and readjust IDs
    all_blocks.sort(key=lambda x: x.get("_line_position", 0))
    
    # Readjust IDs and remove temporary field
    for i, block in enumerate(all_blocks, 1):
        block["id"] = i
        if "_line_position" in block:
            del block["_line_position"]

    return all_blocks


def _is_valid_context_block(block: Dict[str, Any]) -> bool:
    """
    Validates if a block is really a reading context, not a question.
    """
    title = block.get("title", "").lower()
    statement = block.get("statement", "").lower()
    
    # Filter blocks that are questions
    if "questão" in title or "questão" in statement:
        return False
    
    # Filter blocks that are alternatives (starting with (A), (B), etc.)
    if title.startswith("(") and len(title) > 1 and title[1] in "abcde":
        return False
    if statement.startswith("(") and len(statement) > 1 and statement[1] in "abcde":
        return False
        
    # Must have significant content in the title
    if len(title) < 3:
        return False
        
    return True


def _determine_context_type(paragraphs: List[str], has_image: bool, instruction: str) -> List[str]:
    """
    Determines the type of context_block based on content and presence of image.
    Returns a list with types: ["text"], ["image"], or ["text", "image"]
    """
    types = []
    
    # Check if there is significant textual content
    has_meaningful_text = False
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        # Consider text significant if it has more than 20 characters and is not just an instruction
        if (len(paragraph) > 20 and 
            not paragraph.lower().startswith(('analise a imagem', 'observe a imagem', 'veja a imagem'))):
            has_meaningful_text = True
            break
    
    # If there are no significant paragraphs, check the instruction
    if not has_meaningful_text and instruction:
        instruction_lower = instruction.lower()
        # If the instruction is not just about an image, consider it as text
        if not any(word in instruction_lower for word in ['imagem', 'figura', 'gráfico', 'analise a imagem']):
            has_meaningful_text = True
    
    # Add types based on content
    if has_meaningful_text:
        types.append("text")
    
    if has_image:
        types.append("image")
    
    # If there's neither text nor image, consider it as text by default
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
    Looks for text that appears to be extracted from an image in nearby lines.
    """
    # Specific patterns for text extracted from images
    specific_patterns = [
        r"FAVOR.*NÃO.*DEXAR",
        r"FAVOR.*NAO.*DEXAR", 
    ]
    
    # General patterns for image text (more restrictive)
    general_patterns = [
        r"^[A-Z\s]{15,}$",  # Line with only uppercase, at least 15 chars
        r"^[A-Z][A-Z\s]*[A-Z]$",  # Starts and ends with uppercase, only uppercase/spaces in between
    ]
    
    question_regex = re.compile(r"^QUEST[ÃA]O\s+\d+", re.IGNORECASE)
    
    # First look for known specific patterns
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
    
    # If no specific patterns were found, look for general patterns
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
