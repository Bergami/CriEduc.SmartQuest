import re
from typing import List, Optional, Union

def parse_trimester(header: str) -> Optional[str]:
    """Extract trimester information from the header."""
    match = re.search(r"(\dº|\d[o°])\s+TRIMESTRE", header, re.IGNORECASE)
    return match.group(1).strip() if match else None
