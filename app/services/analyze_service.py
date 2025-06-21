import pdfplumber
from io import BytesIO
from uuid import uuid4
from fastapi import UploadFile
from app.parsers.header_parser import HeaderParser


class AnalyzeService:
    @staticmethod
    async def process_document(file: UploadFile, email: str) -> dict:
        document_id = str(uuid4())
        extracted_data = await AnalyzeService._extract_text_and_metadata(file)

        return {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "header": extracted_data["header"],
            "extracted_text": extracted_data["text"][:500]
        }

    @staticmethod
    async def _extract_text_and_metadata(file: UploadFile) -> dict:
        file_bytes = await file.read()
        pdf_buffer = BytesIO(file_bytes)

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
