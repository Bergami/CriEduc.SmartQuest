import re
from typing import Optional


def parse_grade_value(student_line: Optional[str]) -> Optional[str]:
    """Extract grade value from the student line."""
    if not student_line:
        return None
    match = re.search(r"Valor:\s*([\d,\.]+)", student_line)
    return match.group(1).strip() if match else None
