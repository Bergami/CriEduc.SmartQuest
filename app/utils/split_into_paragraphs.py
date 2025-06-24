import re

def split_into_paragraphs(text: str) -> list[dict]:
    """
    Separa texto em parágrafos usando heurísticas de OCR.
    Prioriza quebras duplas (\n\n) e, na ausência, usa fim de frase (.!?).
    """
    # Primeiro, tenta quebrar por \n\n
    raw_paragraphs = re.split(r"\n{2,}", text.strip())

    cleaned = []

    for raw in raw_paragraphs:
        merged = ""
        for line in raw.splitlines():
            if line.strip():
                if merged:
                    merged += " " + line.strip()
                else:
                    merged = line.strip()
        if merged:
            cleaned.append({"text": merged})

    return cleaned
