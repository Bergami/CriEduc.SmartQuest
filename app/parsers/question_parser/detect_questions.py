from typing import List, Dict, Any
import re

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

        # Novo parser para alternativas que podem estar em uma linha única
        question_text, alternatives = _parse_question_and_alternatives(lines)

        # ✅ Detecta presença de imagem com base no texto da questão
        has_image = "imagem" in question_text.lower() or "figura" in question_text.lower()

        questions.append({
            "number": number,
            "question": question_text,
            "alternatives": alternatives,
            "hasImage": has_image,
            "context_id": None
        })

    return questions


def _parse_question_and_alternatives(lines: List[str]) -> tuple[str, List[Dict[str, Any]]]:
    """
    Parse question text and alternatives from lines.
    Handles both single-line and multi-line alternatives.
    """
    question_parts = []
    alternatives = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line contains alternatives (has pattern like "(A) ... (B) ... (C) ...")
        if _line_contains_multiple_alternatives(line):
            alternatives.extend(_extract_alternatives_from_single_line(line))
        elif line.startswith('(') and len(line) > 3 and line[2] == ')':
            # Single alternative per line
            alternatives.append(_format_single_alternative(line))
        else:
            # Part of question text
            question_parts.append(line)
    
    question_text = ' '.join(question_parts).strip()
    return question_text, alternatives


def _line_contains_multiple_alternatives(line: str) -> bool:
    """Check if a line contains multiple alternatives."""
    pattern = r'\([A-E]\)'
    matches = re.findall(pattern, line)
    return len(matches) > 1


def _extract_alternatives_from_single_line(line: str) -> List[Dict[str, Any]]:
    """Extract multiple alternatives from a single line."""
    alternatives = []
    
    # Split by alternative pattern but keep the pattern
    pattern = r'(\([A-E]\))'
    parts = re.split(pattern, line)
    
    current_letter = None
    current_text = ""
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Check if this part is an alternative letter
        if re.match(r'\([A-E]\)', part):
            # Save previous alternative if exists
            if current_letter and current_text:
                alternatives.append({
                    "letter": current_letter,
                    "text": current_text.strip()
                })
            
            # Start new alternative
            current_letter = part[1]  # Extract letter from (A)
            current_text = ""
        else:
            # Add to current alternative text
            current_text += " " + part
    
    # Don't forget the last alternative
    if current_letter and current_text:
        alternatives.append({
            "letter": current_letter,
            "text": current_text.strip()
        })
    
    return alternatives


def _format_single_alternative(line: str) -> Dict[str, Any]:
    """Format a single alternative line."""
    match = re.match(r'\(([A-E])\)\s*(.*)', line)
    if match:
        letter = match.group(1)
        text = match.group(2).strip()
        return {
            "letter": letter,
            "text": text
        }
    else:
        return {
            "letter": "?",
            "text": line
        }
