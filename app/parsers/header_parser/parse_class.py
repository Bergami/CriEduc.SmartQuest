import re


def parse_class(student_line: str | None) -> str | None:
    """Extract class identifier from the student line."""
    if not student_line:
        return None
    match = re.search(r"TURMA:\s*([^\n\r:]+)", student_line)
    return match.group(1).strip() if match else None
