from typing import List, Tuple
import re

def extract_alternatives_from_text(text: str) -> Tuple[str, List[str]]:
    """
    Extrai o enunciado e as alternativas de uma questão.
    
    Suporta múltiplos formatos:
    - (A) (B) (C) (D) (E)
    - a) b) c) d) e)
    - A) B) C) D) E)

    Retorna:
    - Enunciado limpo
    - Lista de alternativas como strings
    """
    # Padrões para identificar alternativas
    patterns = [
        r'\([A-E]\)',           # (A) (B) (C) (D) (E)
        r'[a-e]\)',             # a) b) c) d) e)
        r'[A-E]\)',             # A) B) C) D) E)
    ]
    
    best_match = None
    best_pattern = None
    
    # Procura o padrão com mais ocorrências
    for pattern in patterns:
        matches = list(re.finditer(pattern, text))
        if len(matches) >= 3:  # Pelo menos 3 alternativas para ser válido
            if best_match is None or len(matches) > len(best_match):
                best_match = matches
                best_pattern = pattern
    
    if not best_match:
        return text.strip(), []

    # Extrai o enunciado (tudo antes da primeira alternativa)
    question_start = text[:best_match[0].start()].strip()
    
    # Remove possíveis fragmentos de alternativas do final do enunciado
    question_start = re.sub(r'\s+[a-eA-E]\)?\s*$', '', question_start)
    
    alternatives = []
    for i in range(len(best_match)):
        start = best_match[i].end()  # Depois do marcador (A), a), etc.
        end = best_match[i + 1].start() if i + 1 < len(best_match) else len(text)
        
        alt_text = text[start:end].strip()
        
        # Remove possível próximo marcador do final
        alt_text = re.sub(r'\s+\([A-E]\)\s*$', '', alt_text)
        alt_text = re.sub(r'\s+[a-eA-E]\)\s*$', '', alt_text)
        
        if alt_text:
            alternatives.append(alt_text)

    return question_start, alternatives

def extract_alternatives_from_question_text(question_text: str) -> Tuple[str, List[str]]:
    """
    Wrapper para manter compatibilidade e adicionar lógica específica para questões
    """
    # Primeiro tenta a extração padrão
    clean_question, alternatives = extract_alternatives_from_text(question_text)
    
    # Se não encontrou alternativas, tenta padrões mais específicos
    if not alternatives:
        # Tenta padrão com quebras de linha
        lines = question_text.split('\n')
        alt_lines = []
        question_lines = []
        found_alternatives = False
        
        for line in lines:
            line = line.strip()
            if re.match(r'^[a-eA-E]\)|\([A-E]\)', line):
                found_alternatives = True
                alt_lines.append(line)
            elif not found_alternatives:
                question_lines.append(line)
            else:
                # Continua adicionando às alternativas se já começou
                if alt_lines:
                    alt_lines[-1] += ' ' + line
        
        if alt_lines:
            clean_question = '\n'.join(question_lines).strip()
            # Limpa os marcadores das alternativas
            alternatives = []
            for alt in alt_lines:
                cleaned_alt = re.sub(r'^[a-eA-E]\)|\([A-E]\)', '', alt).strip()
                if cleaned_alt:
                    alternatives.append(cleaned_alt)
    
    return clean_question, alternatives
