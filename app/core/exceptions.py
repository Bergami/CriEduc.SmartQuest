from fastapi import HTTPException

class InvalidDocumentFormatException(HTTPException):
    """Erro para quando um documento não é um PDF válido."""
    def __init__(self):
        super().__init__(status_code=400, detail="Only PDF files are supported.")

class MissingMetadataException(HTTPException):
    """Erro para quando metadata obrigatória está ausente."""
    def __init__(self, detail: str = "Metadata fields are required."):
        super().__init__(status_code=400, detail=detail)
