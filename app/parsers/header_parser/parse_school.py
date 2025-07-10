import re
from typing import List, Optional, Union
from app.data.institution_prefixes import ALL_INSTITUTION_PREFIXES


def parse_school(header: str) -> Optional[str]:
    """Extract school name from the header."""
    pattern = r"\b(" + "|".join(ALL_INSTITUTION_PREFIXES) + r")[^\n\r]+"
    match = re.search(pattern, header)
    return match.group(0).strip() if match else None
