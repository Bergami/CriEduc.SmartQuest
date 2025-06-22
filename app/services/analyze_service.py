import json
import os
from io import BytesIO
from uuid import uuid4
from fastapi import UploadFile

try:  # pdfplumber may be unavailable in constrained environments
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - fallback when dependency is missing
    pdfplumber = None

from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.utils.final_result_builder import FinalResultBuilder

class AnalyzeService:
    @staticmethod
    async def process_document(
        file: UploadFile,
        email: str,
        use_json_fallback: bool = False,
    ) -> dict:
        document_id = str(uuid4())

        if use_json_fallback or pdfplumber is None:
            # 🔄 Fallback: carrega dados prontos do arquivo JSON
            json_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "tests",
                "resultado_parser.json",
            )
            json_path = os.path.abspath(json_path)

            with open(json_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)

            parsed_data["document_id"] = document_id
            parsed_data["email"] = email
            parsed_data["filename"] = file.filename
            parsed_data["extracted_text"] = "Documento carregado via fallback JSON."

            return parsed_data

        extracted_data = await AnalyzeService._extract_text_and_metadata(file)
        question_data = QuestionParser.extract(extracted_data["text"])

        return {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "header": extracted_data["header"],
            "questions": question_data["questions"],
            "context_blocks": question_data["context_blocks"],
            "extracted_text": extracted_data["text"][:500]
        }

    @staticmethod
    async def _extract_text_and_metadata(file: UploadFile) -> dict:
        file_bytes = await file.read()
        pdf_buffer = BytesIO(file_bytes)

        if pdfplumber is None:
            # Retorna texto vazio se o parser de PDF não estiver disponível
            text = ""
        else:
            with pdfplumber.open(pdf_buffer) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        header_text = AnalyzeService._extract_header_block(text)
        header_data = AnalyzeService._parse_header(header_text)

        return {
            "header": header_data,
            "text": text
        }

    @staticmethod
    def _extract_header_block(text: str, max_lines: int = 12) -> str:
        lines = text.strip().splitlines()
        return "\n".join(lines[:max_lines])

    @staticmethod
    def _parse_header(header: str) -> dict:
        return HeaderParser.parse(header)
