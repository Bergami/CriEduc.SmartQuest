from typing import List, Dict, Any
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, ValidationError
from app.core.utils import is_pdf
from app.core.exceptions import (
    InvalidDocumentFormatException,
    MissingFileException,
    InvalidEmailException,
    MultipleValidationException,
    SmartQuestException
)

class EmailValidationModel(BaseModel):
    email: EmailStr

class AnalyzeValidator:

    @staticmethod
    def validate_email_only(email: str) -> None:
        """Valida apenas o email (para modo mock)"""
        try:
            EmailValidationModel(email=email)
        except ValidationError:
            raise InvalidEmailException(email)

    @staticmethod
    def validate_all(file: UploadFile, email: str) -> None:
        """Valida arquivo e email, coletando erros e lançando exceção múltipla se necessário"""
        errors = []

        # Validação de e-mail
        try:
            EmailValidationModel(email=email)
        except ValidationError:
            errors.append("Invalid email format")

        # Validação de arquivo
        if not file:
            errors.append("No file was provided")        
        elif not is_pdf(file):
            # Detecta o tipo do arquivo pelo content_type se disponível
            received_format = getattr(file, 'content_type', 'unknown')
            errors.append(f"Only PDF files are supported, received: {received_format}")
        elif not file.filename.lower().endswith(".pdf"):
            errors.append("File must have .pdf extension")

        # Se houver erros, lança a exceção agrupada
        if errors:
            raise MultipleValidationException(errors)

    @staticmethod
    def format_exception(exc: SmartQuestException) -> Dict[str, Any]:
        """Formata exceção customizada para uso em logs ou respostas"""
        return {
            "code": exc.status_code,
            "message": exc.message,
            "type": exc.error_type
        }

