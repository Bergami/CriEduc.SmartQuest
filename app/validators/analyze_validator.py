   
from fastapi import UploadFile
from app.core.exceptions import InvalidDocumentFormatException, MissingMetadataException

class AnalyzeValidator:
    @staticmethod
    def validate_file(file: UploadFile):
        """Valida se o arquivo é um PDF."""
        if not file.filename.lower().endswith(".pdf"):
            raise InvalidDocumentFormatException()

    @staticmethod
    def validate_metadata(metadata: dict):
        """Valida se os campos obrigatórios estão presentes."""
      
        # 🛠️ Cria uma lista de campos obrigatórios que devem estar no metadata
        required_fields = ["subject", "category", "difficulty", "tags"]

        # 🔍 Verifica quais campos obrigatórios estão ausentes no metadata
        missing_fields = [field for field in required_fields if field not in metadata]

        # 📢 Se houver campos faltando, retornamos a lista com eles
        if missing_fields:
            raise MissingMetadataException(f"Missing metadata fields: {', '.join(missing_fields)}")
        
        