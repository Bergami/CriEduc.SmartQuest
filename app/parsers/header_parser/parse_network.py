import re


def parse_network(header: str, lines: list[str]) -> str | None:
    """Extract the education network or institution name from header lines."""
    for line in lines:
        if any(word in line.lower() for word in [
            "prefeitura",
            "secretaria",
            "governo",
            "instituto",
            "universidade",
        ]):
            return line.strip()
    return None
