import re


def parse_student(student_line: str | None) -> str | None:
    """Extract student name from the student line."""
    if not student_line:
        return None
    match = re.search(r"Estudante:\s*([^\n\r:]+)", student_line)
    return match.group(1).strip() if match else None
