from importlib.metadata import metadata
import pdfplumber
import re
from io import BytesIO
from uuid import uuid4
from fastapi import UploadFile

class AnalyzeService:
    @staticmethod
    async def process_document(file: UploadFile, email):
        """Processa o documento PDF e retorna os metadados identificados."""

        document_id = str(uuid4())  # Gera um ID único
        extracted_data = await AnalyzeService._extract_text_and_metadata(file)  # 🚀 Agora chamamos o método de forma assíncrona

        return {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "metadata": extracted_data["metadata"],
            "extracted_text": extracted_data["extracted_text"][:500]  # Retorna um trecho do texto extraído
        }
    
    @staticmethod
    async def _extract_text_and_metadata(file: UploadFile):
        """Processa o texto e extrai metadados automaticamente de forma assíncrona."""

        file_bytes = await file.read()  # 🚀 Agora estamos lendo os bytes de forma assíncrona
        pdf_buffer = BytesIO(file_bytes)

        with pdfplumber.open(pdf_buffer) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        metadata = AnalyzeService._extract_metadata(text)

        return {"metadata": metadata, "extracted_text": text}

    @staticmethod
    def _extract_metadata(text):
        """Extrai informações-chave do documento analisando padrões."""

        metadata = {
            "exam_title": re.search(r"Prova Trimestral\s+(.+)", text),
            "school": re.search(r"Prefeitura Municipal de\s+(.+)", text),
            "teacher": re.search(r"Professora:\s+(.+)", text),
            "grade": re.search(r"ANO:\s+(.+)", text),
            "trimester": re.search(r"Trimestre\s+(\d+)", text),
            "subject": re.search(r"Disciplina:\s+(.+)", text),
            "total_questions": len(re.findall(r"QUESTÃO\s+\d+", text)),
            "contains_images": "Analise a imagem" in text
        }

        return {key: match.group(1) if match and hasattr(match, "group") else None for key, match in metadata.items()}    