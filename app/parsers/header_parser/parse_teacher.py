import re


def parse_teacher(header: str) -> str | None:
    """Extract teacher name from the header."""
    match = re.search(r"Professora?:\s+([^\n\r]+)", header)
    if match:
        full = match.group(1).strip()
        full = re.split(r"ANO:|Ensino|Fundamental", full)[0].strip()
        parts = full.split()
        return parts[0] if parts else full
    return None
