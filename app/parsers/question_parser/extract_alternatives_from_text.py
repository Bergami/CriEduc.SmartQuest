from ast import List, Tuple
import re

def extract_alternatives_from_text(text: str) -> Tuple[str, List[str]]:
    """
    Extrai o enunciado e as alternativas de uma questão.

    Retorna:
    - Enunciado limpo
    - Lista de alternativas como strings
    """
    alt_regex = r"\([A-E]\)"

    # Procura todas as ocorrências de marcadores (A)...(E)
    alt_matches = List(re.finditer(alt_regex, text))

    if not alt_matches:
        return text.strip(), []

    question_start = text[:alt_matches[0].start()].strip()
    alternatives = []

    for i in range(len(alt_matches)):
        start = alt_matches[i].start()
        end = alt_matches[i + 1].start() if i + 1 < len(alt_matches) else len(text)
        alt_text = text[start:end].strip()
        alternatives.append(alt_text)

    return question_start, alternatives
