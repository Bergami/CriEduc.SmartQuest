import re
from app.data.subjects import normalize_subject
from typing import List, Optional, Union

def parse_subject(header: str) -> Optional[str]:
    """Extract subject name from the header with contextual validation."""
    
    # Pattern 1: Explicit subject patterns
    subject_patterns = [
        r"Língua Portuguesa",
        r"Matemática", 
        r"Ciências",
        r"História",
        r"Geografia",
        r"Inglês",
        r"Espanhol",
        r"Arte",
        r"Educação Física",
        r"Ensino Religioso",
        r"Filosofia",
        r"Sociologia",
        r"Redação",
        r"Biologia",
        r"Física",
        r"Química"
    ]
    
    # Check for exact subject matches (case-insensitive)
    for subject in subject_patterns:
        pattern = rf"\b{re.escape(subject)}\b"
        if re.search(pattern, header, re.IGNORECASE):
            return subject
    
    # Pattern 2: Common aliases
    aliases = {
        r"\bPortuguês\b": "Língua Portuguesa",
        r"\bLP\b": "Língua Portuguesa", 
        r"\bMat\b": "Matemática",
        r"\bBio\b": "Biologia",
        r"\bQuim\b": "Química",
        r"\bHist\b": "História",
        r"\bGeo\b": "Geografia",
        r"\bEF\b": "Educação Física",
        r"\bEd\.?\s*Física\b": "Educação Física",
        r"\bEd\.?\s*Religiosa\b": "Ensino Religioso",
        r"\bSocio\b": "Sociologia"
    }
    
    for pattern, subject in aliases.items():
        if re.search(pattern, header, re.IGNORECASE):
            return subject
    
    # Pattern 3: Subject after specific keywords
    context_patterns = [
        r"(?:Disciplina|Matéria|Prova)\s*:?\s*([^:\n\r]+)",
        r"(?:de|do)\s+(Língua Portuguesa|Matemática|Ciências|História|Geografia|Inglês|Arte|Educação Física)",
    ]
    
    for pattern in context_patterns:
        match = re.search(pattern, header, re.IGNORECASE)
        if match:
            found = match.group(1).strip()
            # Validate against known subjects
            for subject in subject_patterns:
                if subject.lower() in found.lower():
                    return subject
    
    return None
