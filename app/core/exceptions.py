from fastapi import HTTPException

class InvalidDocumentFormatException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Only PDF files are supported.")

class MissingFileException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No file was provided.")

class InvalidEmailException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid email format.")

class MultipleValidationException(HTTPException):
    def __init__(self, errors: list[str]):
        super().__init__(status_code=422, detail={"errors": errors})