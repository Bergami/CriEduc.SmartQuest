import re


def parse_grade_value(student_line: str | None) -> str | None:
    """Extract grade value from the student line."""
    if not student_line:
        return None
    match = re.search(r"Valor:\s*([\d,\.]+)", student_line)
    return match.group(1).strip() if match else None
