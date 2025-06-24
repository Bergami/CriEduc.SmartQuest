import re

def extract_alternatives_from_lines(lines: list[str], start_index: int = 0) -> tuple[str, list[str], int]:
    """
    Extrai enunciado da questão e alternativas de múltipla escolha a partir das linhas.
    Retorna:
    - Texto da questão
    - Lista de alternativas completas
    - Índice da última linha lida (para o parser avançar corretamente)
    """
    alternatives = []
    current_alternative = ""
    pattern = re.compile(r"^\(?[A-E][\)\.\-]?", re.IGNORECASE)

    question_lines = []
    i = start_index
    found_alternatives = False
    empty_line_count = 0

    while i < len(lines):
        line = lines[i].strip()

        if pattern.match(line):
            found_alternatives = True
            if current_alternative:
                alternatives.append(current_alternative.strip())
            current_alternative = line
            empty_line_count = 0
        elif found_alternatives:
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            elif pattern.match(line):
                # nova alternativa detectada — já tratada no bloco acima
                pass
            else:
                current_alternative += " " + line
                empty_line_count = 0
        else:
            question_lines.append(line)

        i += 1

    if current_alternative:
        alternatives.append(current_alternative.strip())

    question_text = " ".join(question_lines).strip()

    return question_text, alternatives, i
