import re


def parse_grade(header: str) -> str | None:
    """Extract grade/year from the header."""
    match = re.search(r"ANO:\s+([^\n\r]+)", header)
    return match.group(1).strip() if match else None
