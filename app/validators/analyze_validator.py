from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from app.core.utils import is_pdf
from app.core.exceptions import (
    InvalidDocumentFormatException,
    MissingFileException,
    InvalidEmailException,
    MultipleValidationException
)

class EmailValidationModel(BaseModel):
    email: EmailStr

class AnalyzeValidator:

    @staticmethod
    def validate_all(file: UploadFile, email: str) -> List[Dict[str, Any]]:
        errors = []

        # Validação de e-mail
        try:
            EmailValidationModel(email=email)
        except ValidationError:
            errors.append(AnalyzeValidator.format_exception(InvalidEmailException()))

        # Validação de arquivo
        if not file:
            errors.append(AnalyzeValidator.format_exception(MissingFileException()))        
        elif not is_pdf(file):
                errors.append(AnalyzeValidator.format_exception(InvalidDocumentFormatException()))
        elif not file.filename.lower().endswith(".pdf"):
            errors.append(AnalyzeValidator.format_exception(InvalidDocumentFormatException()))

        # Se houver erros, lança a exceção agrupada
        if errors:
            raise MultipleValidationException(errors)
    
    @staticmethod
    def format_exception(exc: HTTPException) -> Dict[str, Any]:
        return {
            "code": exc.status_code,
            "message": exc.detail
        }

