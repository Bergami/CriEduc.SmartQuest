import re
from typing import List, Optional, Union

def parse_grade(header: str) -> Optional[str]:
    """Extract grade/year from the header."""
    # Procurar por padrões como "Turma: 7º ano" ou "ANO: 7º ano"
    match = re.search(r"(?:ANO|TURMA):\s+([^\n\r]+)", header, re.IGNORECASE)
    return match.group(1).strip() if match else None
