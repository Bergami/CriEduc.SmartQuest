import re
from typing import Optional


def parse_grade_value(header: str) -> Optional[str]:
    """Extract grade value from the header."""
    if not header:
        return None
    match = re.search(r"Valor:\s*([\d,\.]+)", header, re.IGNORECASE)
    return match.group(1).strip() if match else None
