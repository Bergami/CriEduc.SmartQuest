import re
from typing import List, Optional, Union

def parse_exam_title(header: str) -> Optional[str]:
    """Extract the exam title from the header."""
    match = re.search(r"(Prova Trimestral)", header, re.IGNORECASE)
    return match.group(0).strip() if match else None
