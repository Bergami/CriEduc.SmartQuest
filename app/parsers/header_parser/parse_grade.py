import re
from typing import List, Optional, Union

def parse_grade(header: str) -> Optional[str]:
    """Extract grade/year from the header."""
    match = re.search(r"ANO:\s+([^\n\r]+)", header)
    return match.group(1).strip() if match else None
