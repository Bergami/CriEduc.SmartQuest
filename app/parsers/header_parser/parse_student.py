import re
from typing import Optional


def parse_student(student_line: Optional[str]) -> Optional[str]:
    """Extrai o nome do estudante a partir da linha de metadados da prova.

    Retorna None caso o campo esteja em branco ou contenha palavras-chave como 'Data'.
    """
    if not student_line:
        return None

    match = re.search(r"Estudante:\s*([^\n\r:]+)", student_line)
    if not match:
        return None

    result = match.group(1).strip()

    # Evita retornar valores inválidos
    if result.lower() in ["data", "valor", "nota", "-"]:
        return None

    return result
