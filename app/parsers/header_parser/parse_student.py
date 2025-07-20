import re
from typing import Optional


def parse_student(student_line: Optional[str]) -> Optional[str]:
    """Extracts the student's name from the exam metadata line.

    Returns None if the field is blank or contains keywords like 'Data'.
    """
    if not student_line:
        return None

    match = re.search(r"Estudante:\s*([^\n\r:]+)", student_line)
    if not match:
        return None

    result = match.group(1).strip()

    # Avoid returning invalid values
    if result.lower() in ["data", "valor", "nota", "-"]:
        return None

    return result
