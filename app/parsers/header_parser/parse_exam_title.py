import re
from typing import List, Optional, Union

def parse_exam_title(header: str) -> Optional[str]:
    """Extract the exam title from the header."""
    
    # Array com diferentes tipos de prova
    exam_types = [
        "Prova Trimestral",
        "Prova Bimestral", 
        "Prova de Recuperação",
        "Prova Final",
        "Prova Semestral",
        "Avaliação Trimestral",
        "Avaliação Bimestral",
        "Avaliação Final",
        "Teste",
        "Simulado",
        "Exame",
        "Trabalho Avaliativo"
    ]
    
    # Buscar por cada tipo de prova (case-insensitive)
    for exam_type in exam_types:
        pattern = rf"\b{re.escape(exam_type)}\b"
        match = re.search(pattern, header, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    # Padrão genérico para capturar "Prova + qualquer coisa"
    generic_match = re.search(r"\bProva\s+\w+", header, re.IGNORECASE)
    if generic_match:
        return generic_match.group(0).strip()
    
    # Padrão genérico para capturar "Avaliação + qualquer coisa"
    generic_match = re.search(r"\bAvaliação\s+\w+", header, re.IGNORECASE)
    if generic_match:
        return generic_match.group(0).strip()
    
    return None
