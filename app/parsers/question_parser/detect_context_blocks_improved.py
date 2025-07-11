from typing import List, Dict, Any
import re

def detect_context_blocks(text: str) -> List[Dict[str, Any]]:
    """
    Detecta blocos de leitura (textos base) antes das questões.
    Improved version that properly extracts context content.
    """
    blocks = []
    
    # Define context introduction patterns with their extraction logic
    context_patterns = [
        {
            'pattern': r'Após ler atentamente o texto a seguir, responda as (\w+) próximas questões\.\s*(.*?)(?=QUESTÃO|\Z)',
            'title_template': 'Após ler atentamente o texto a seguir, responda as {} próximas questões.'
        },
        {
            'pattern': r'Leia o texto a seguir para responder as (\w+) próximas questões\.\s*(.*?)(?=QUESTÃO|\Z)',
            'title_template': 'Leia o texto a seguir para responder as {} próximas questões.'
        },
        {
            'pattern': r'LEIA O TEXTO A SEGUIR\s*(.*?)(?=QUESTÃO|\Z)',
            'title_template': 'LEIA O TEXTO A SEGUIR'
        },
        {
            'pattern': r'Leia (?:a|o) (?:crônica|texto) e depois resolva as próximas questões\.\s*(.*?)(?=\Z)',
            'title_template': 'Leia a crônica e depois resolva as próximas questões.'
        },
        {
            'pattern': r'Analise (?:a|o) (?:imagem|texto) (?:abaixo|a seguir)\s*(.*?)(?=QUESTÃO|\Z)',
            'title_template': 'Analise a imagem abaixo'
        },
        {
            'pattern': r'Leia este texto\s*(.*?)(?=QUESTÃO|\Z)',
            'title_template': 'Leia este texto'
        }
    ]
    
    block_id = 1
    
    for pattern_info in context_patterns:
        pattern = pattern_info['pattern']
        title_template = pattern_info['title_template']
        
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            groups = match.groups()
            
            # Extract content (last group is always the content)
            content = groups[-1].strip() if groups else ""
            
            # Extract question count if captured
            question_count = None
            if len(groups) > 1 and groups[0]:
                question_count = groups[0]
                title = title_template.format(question_count)
            else:
                title = title_template
            
            if content:
                # Clean content
                content = _clean_context_content(content)
                
                if _is_valid_context_content(content):
                    block = {
                        "id": block_id,
                        "type": "reading_comprehension", 
                        "source": "exam_document",
                        "content": content,
                        "title": title,
                        "hasImage": "imagem" in title.lower(),
                        "question_count": _parse_question_count(question_count) if question_count else None
                    }
                    
                    blocks.append(block)
                    block_id += 1
    
    # Fallback: extract standalone context texts that might not have explicit introduction
    if len(blocks) < 3:  # Expected to have at least 3-5 contexts
        additional_blocks = _extract_standalone_contexts(text, block_id)
        blocks.extend(additional_blocks)
    
    # Remove duplicates and clean up blocks
    cleaned_blocks = _remove_duplicate_blocks(blocks)
    
    return cleaned_blocks


def _clean_context_content(content: str) -> str:
    """Clean and normalize context content"""
    # Remove excessive whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Remove Azure selection marks
    content = re.sub(r':selected:', '', content)
    content = re.sub(r':unselected:', '', content)
    
    # Split into lines and clean
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    return '\n'.join(lines).strip()


def _is_valid_context_content(content: str) -> bool:
    """Validate if content is a valid context block"""
    if len(content) < 50:  # Too short to be meaningful context
        return False
    
    # Should not be just a list of alternatives
    lines = content.split('\n')
    alternative_lines = sum(1 for line in lines if re.match(r'^\([A-E]\)', line.strip()))
    
    if alternative_lines > len(lines) * 0.5:  # More than 50% are alternatives
        return False
    
    return True


def _parse_question_count(count_word: str) -> int:
    """Parse question count word to number"""
    count_map = {
        'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'quatro': 4, 'cinco': 5
    }
    return count_map.get(count_word.lower(), 1)


def _extract_standalone_contexts(text: str, start_id: int) -> List[Dict[str, Any]]:
    """Extract context blocks that don't have explicit introduction patterns"""
    blocks = []
    
    # Look for standalone text blocks that are likely contexts
    # These are usually titled texts followed by content
    standalone_patterns = [
        r'(FEIJÕES OU PROBLEMAS\?.*?)(?=QUESTÃO|\n\n[A-Z])',
        r'(PARQUES EM CHAMAS.*?)(?=QUESTÃO|\n\n[A-Z])', 
        r'(POR QUE TODO MUNDO USAVA PERUCA.*?)(?=QUESTÃO|\n\n[A-Z])',
        r'(DIABETES SEM FREIO.*?)(?=QUESTÃO|\n\n[A-Z])',
        r'(FAVOR NÃO DEXAR OBIGETOS.*?)(?=QUESTÃO|\n\n[A-Z])'
    ]
    
    block_id = start_id
    
    for pattern in standalone_patterns:
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            content = match.group(1).strip()
            
            if content and _is_valid_context_content(content):
                # Extract title from first line
                lines = content.split('\n')
                title = lines[0].strip() if lines else f"Texto {block_id}"
                
                block = {
                    "id": block_id,
                    "type": "reading_comprehension",
                    "source": "exam_document", 
                    "content": _clean_context_content(content),
                    "title": title,
                    "hasImage": False,
                    "question_count": None
                }
                
                blocks.append(block)
                block_id += 1
    
    return blocks


def _remove_duplicate_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate context blocks based on content similarity"""
    if not blocks:
        return blocks
    
    unique_blocks = []
    
    for block in blocks:
        content = block.get('content', '')
        title = block.get('title', '')
        
        # Check if this block is similar to any existing block
        is_duplicate = False
        
        for existing in unique_blocks:
            existing_content = existing.get('content', '')
            existing_title = existing.get('title', '')
            
            # Check content similarity (first 200 characters)
            content_similarity = _calculate_similarity(content[:200], existing_content[:200])
            title_similarity = _calculate_similarity(title, existing_title)
            
            # Consider duplicate if content is very similar (>80%) or titles are very similar (>90%)
            if content_similarity > 0.8 or title_similarity > 0.9:
                is_duplicate = True
                
                # Keep the block with more content or better title
                if len(content) > len(existing_content) or (not existing_title and title):
                    # Replace the existing block with this better one
                    existing_index = unique_blocks.index(existing)
                    unique_blocks[existing_index] = block
                break
        
        if not is_duplicate:
            unique_blocks.append(block)
    
    # Re-assign sequential IDs
    for i, block in enumerate(unique_blocks, 1):
        block['id'] = i
    
    return unique_blocks


def _calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (simple ratio)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple similarity based on common words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0
