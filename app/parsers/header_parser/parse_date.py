import re
from typing import Optional


def parse_date(student_line: Optional[str]) -> Optional[str]:
    """Extract exam date from the student line."""
    if not student_line:
        return None
    match = re.search(r"Data:\s*(\d{1,2}/\d{1,2}/\d{2,4})", student_line)
    return match.group(1).strip() if match else None
