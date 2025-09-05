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
    # Padrões para identificar alternativas - mais flexíveis e abrangentes
    patterns = [
        r'\([A-Z]\)',           # (A) (B) (C) (D) (E) ... (Z) - suporte completo
        r'^[a-z]\)',            # a) b) c) d) e) ... z) no início de linha/texto
        r'^[A-Z]\)',            # A) B) C) D) E) ... Z) no início de linha/texto
        r'\n[a-z]\)',           # a) b) c) d) e) ... z) após quebra de linha
        r'\n[A-Z]\)',           # A) B) C) D) E) ... Z) após quebra de linha
        r'\s[a-z]\)\s',         # a) b) c) d) e) ... z) com espaços ao redor
        r'\s[A-Z]\)\s',         # A) B) C) D) E) ... Z) com espaços ao redor
    ]
    
    best_match = None
    best_pattern = None
    
    # Procura o padrão com mais ocorrências válidas (sequenciais)
    for pattern in patterns:
        matches = list(re.finditer(pattern, text))
        
        # Filtra matches que são realmente alternativas sequenciais
        valid_matches = _filter_valid_alternative_matches(matches, text, pattern)
        
        # MUDANÇA: Aceita 2+ alternativas (não força 3-5)
        # Isso permite questões com diferentes números de alternativas
        if len(valid_matches) >= 2:  # Pelo menos 2 alternativas para ser válido
            if best_match is None or len(valid_matches) > len(best_match):
                best_match = valid_matches
                best_pattern = pattern
    
    if not best_match:
        return text.strip(), []

    # Extrai o enunciado (tudo antes da primeira alternativa)
    question_start = text[:best_match[0].start()].strip()
    
    # CORREÇÃO IMPORTANTE: Remove possíveis fragmentos de alternativas do final do enunciado
    # Mas preserva indicadores de pontuação como "(2,0 pontos)"
    question_start = re.sub(r'\s+[a-zA-Z]\)?\s*$', '', question_start)
    
    # Se o enunciado termina com pontos (ex: "(2,0 pontos)"), 
    # a primeira alternativa pode estar grudada no enunciado
    if re.search(r'\(\d+[,\.]\d+\s*pontos?\)\s*$', question_start):
        # Neste caso, vamos extrair a alternativa corretamente
        # Procura por "pontos) a)" ou similar no texto original
        match_after_points = re.search(r'\(\d+[,\.]\d+\s*pontos?\)\s*([a-zA-Z]\))', text)
        if match_after_points:
            # A primeira alternativa começa após os pontos
            first_alt_start = match_after_points.start(1)
            question_start = text[:first_alt_start].strip()
            
            # Redefine best_match para começar da primeira alternativa real
            # Encontra todas as alternativas a partir da posição correta
            remaining_text = text[first_alt_start:]
            new_matches = list(re.finditer(best_pattern, remaining_text))
            if new_matches:
                # Ajusta as posições dos matches
                adjusted_matches = []
                for match in new_matches:
                    # Cria um novo match com posição ajustada
                    class AdjustedMatch:
                        def __init__(self, original_match, offset):
                            self.original = original_match
                            self.offset = offset
                        
                        def start(self):
                            return self.original.start() + self.offset
                        
                        def end(self):
                            return self.original.end() + self.offset
                        
                        def group(self):
                            return self.original.group()
                    
                    adjusted_matches.append(AdjustedMatch(match, first_alt_start))
                
                best_match = adjusted_matches
    
    alternatives = []
    for i in range(len(best_match)):
        start = best_match[i].end()  # Depois do marcador (A), a), etc.
        end = best_match[i + 1].start() if i + 1 < len(best_match) else len(text)
        
        alt_text = text[start:end].strip()
        
        # Remove possível próximo marcador do final
        alt_text = re.sub(r'\s+\([A-Z]\)\s*$', '', alt_text)
        alt_text = re.sub(r'\s+[a-zA-Z]\)\s*$', '', alt_text)
        
        if alt_text:
            alternatives.append(alt_text)

    return question_start, alternatives


def _filter_valid_alternative_matches(matches, text: str, pattern: str):
    """
    Filtra matches que são realmente alternativas válidas.
    Remove falsos positivos como (a) em 'o(a) interlocutor(a)'.
    
    IMPORTANTE: Detecta dinamicamente quantas alternativas existem (não assume sempre 5).
    CORREÇÃO CRÍTICA: Alternativas só são válidas se estão no INÍCIO de linhas/parágrafos.
    """
    if not matches:
        return []
    
    valid_matches = []
    
    for match in matches:
        # Extrai a letra do match
        letter = re.search(r'[a-zA-Z]', match.group())  # Suporte completo a-z, A-Z
        if not letter:
            continue
            
        letter = letter.group().lower()
        
        # REGRA CRÍTICA: Alternativas reais só aparecem no INÍCIO de parágrafos
        # Verifica se o match está no início de uma linha ou logo após pontuação final
        start_pos = match.start()
        
        # Verifica o que vem antes da alternativa
        if start_pos > 0:
            char_before = text[start_pos - 1]
            chars_before_5 = text[max(0, start_pos - 5):start_pos]
            
            # Aceita apenas se:
            # 1. Está no início do texto
            # 2. Vem logo após quebra de linha
            # 3. Vem após "(X,Y pontos)" (padrão comum)
            # 4. Tem espaços significativos antes (não está grudado em palavra)
            
            is_valid_position = (
                start_pos == 0 or  # Início do texto
                char_before in ['\n', '\r'] or  # Após quebra de linha
                chars_before_5.endswith('pontos)') or  # Após indicação de pontos
                (char_before == ' ' and text[max(0, start_pos - 10):start_pos].count(' ') >= 2)  # Espaços suficientes
            )
            
            if not is_valid_position:
                # Ignora falsos positivos como "o(a) interlocutor(a)"
                continue
        
        # Verifica se há conteúdo substantivo após a alternativa
        start_content = match.end()
        end_content = len(text)
        
        # Procura o fim desta alternativa (próxima alternativa ou fim do texto)
        for other_match in matches:
            if other_match.start() > match.end():
                end_content = other_match.start()
                break
        
        alt_content = text[start_content:end_content].strip()
        
        # Filtra alternativas muito curtas ou vazias
        if len(alt_content) < 5:  # Reduzido de 15 para 5 para aceitar alternativas mais curtas
            continue
            
        # Verifica se o conteúdo parece uma alternativa real
        words = alt_content.split()
        if len(words) < 1:  # Reduzido de 3 para 1
            continue
            
        # Não deve ser apenas pontuação ou números
        if re.match(r'^[\d\s\.,\-\(\)]+$', alt_content):
            continue
            
        valid_matches.append(match)
    
    # MUDANÇA IMPORTANTE: Aceita qualquer quantidade >= 2 que esteja em ordem sequencial
    if len(valid_matches) >= 2:
        letters_found = []
        for match in valid_matches:
            letter = re.search(r'[a-zA-Z]', match.group())  # Suporte completo
            if letter:
                letters_found.append(letter.group().lower())
        
        # Verifica se estão em ordem (a, b, c... ou pelo menos sequenciais)
        if _are_letters_sequential(letters_found):
            return valid_matches
    
    # NOVA LÓGICA: Aceita também casos com apenas 1 alternativa se for muito clara
    elif len(valid_matches) == 1:
        # Verifica se é uma alternativa muito clara (longa e bem formada)
        match = valid_matches[0]
        start_content = match.end()
        alt_content = text[start_content:].strip()
        
        # Se a alternativa é longa e bem formada, aceita
        if len(alt_content) >= 20 and len(alt_content.split()) >= 5:
            return valid_matches
    
    return []


def _are_letters_sequential(letters: List[str]) -> bool:
    """
    Verifica se as letras estão em ordem sequencial (a, b, c, d...).
    """
    if len(letters) < 2:
        return True
        
    for i in range(1, len(letters)):
        if ord(letters[i]) != ord(letters[i-1]) + 1:
            return False
    
    return True

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
            if re.match(r'^[a-zA-Z]\)|\([A-Z]\)', line):  # Suporte completo
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
                cleaned_alt = re.sub(r'^[a-zA-Z]\)|\([A-Z]\)', '', alt).strip()  # Suporte completo
                if cleaned_alt:
                    alternatives.append(cleaned_alt)
    
    return clean_question, alternatives
