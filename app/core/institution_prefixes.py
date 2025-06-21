# Prefixos e padrões usados para identificar instituições de ensino no Brasil
SCHOOL_PREFIXES = [
    "UMEF", "EMEF", "EMEIF", "EM", "UEF", "UE", "CMEI", "CEIM",
    "EEEFM", "EEEM", "EEEF", "EE"
]

HIGHER_EDUCATION_PREFIXES = [
    # Universidades federais e estaduais
    "UF[A-Z]{2}", "UFR[A-Z]", "IF[A-Z]{2}", "IFES", "IFSP", "UE[A-Z]{2}",

    # Universidades/Faculdades privadas
    "FAESA", "MULTIVIX", "UVV", "Estácio", "Pitágoras", "UNES", "UNIP",

    # Instituições genéricas
    "Faculdade", "Centro Universitário", "Universidade", "Instituto Federal"
]

# Unificado (para quem quiser importar todos de uma vez)
ALL_INSTITUTION_PREFIXES = SCHOOL_PREFIXES + HIGHER_EDUCATION_PREFIXES
