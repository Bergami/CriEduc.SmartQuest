# Lista de disciplinas normalizadas para análise de provas

SUBJECTS = [
    "Língua Portuguesa",
    "Matemática",
    "Ciências",
    "História",
    "Geografia",
    "Inglês",
    "Espanhol",
    "Arte",
    "Educação Física",
    "Ensino Religioso",
    "Filosofia",
    "Sociologia",
    "Redação",
    "Biologia",
    "Física",
    "Química"
]

# Sinônimos ou variações para facilitar matching
SUBJECT_ALIASES = {
    "Português": "Língua Portuguesa",
    "LP": "Língua Portuguesa",
    "Mat": "Matemática",
    "Bio": "Biologia",
    "Quim": "Química",
    "Hist": "História",
    "Geo": "Geografia",
    "EF": "Educação Física",
    "Ed. Física": "Educação Física",
    "Ed. Religiosa": "Ensino Religioso",
    "Socio": "Sociologia"
}

def normalize_subject(raw_subject: str) -> str | None:
    """Normaliza a disciplina para um nome padronizado, se possível."""
    cleaned = raw_subject.strip()
    return SUBJECT_ALIASES.get(cleaned, cleaned if cleaned in SUBJECTS else None)