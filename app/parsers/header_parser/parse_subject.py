import re
from app.core.subjects import normalize_subject


def parse_subject(header: str) -> str | None:
    """Extract subject name from the header."""
    match = re.search(r"Professora?:\s+([^\n\r]+)", header)
    if match:
        full = match.group(1).strip()
        full = re.split(r"ANO:|Ensino|Fundamental", full)[0].strip()
        parts = full.split()
        if len(parts) > 1:
            return normalize_subject(" ".join(parts[1:]))
    return None
