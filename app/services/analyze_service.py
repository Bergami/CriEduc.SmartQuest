import re
import pdfplumber
from io import BytesIO
from uuid import uuid4
from fastapi import UploadFile
from app.core.institution_prefixes import ALL_INSTITUTION_PREFIXES
from app.core.subjects import normalize_subject
from app.core.cities import CITIES_ES


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
        lines = header.splitlines()
        normalized = re.sub(r"\s+", " ", header).strip()

        def extract_field_line(label: str) -> str | None:
            for line in lines:
                if label.lower() in line.lower():
                    return line.strip()
            return None

        def extract_network_line() -> str | None:
            for line in lines:
                if any(word in line.lower() for word in ["prefeitura", "secretaria", "governo", "instituto", "universidade"]):
                    return line.strip()
            return None

        # 🏛 Rede / Órgão
        network = extract_network_line()

        # 🏫 Escola
        school_pattern = r"\b(" + "|".join(ALL_INSTITUTION_PREFIXES) + r")[^\n\r]+"
        school_match = re.search(school_pattern, header)
        school = school_match.group(0).strip() if school_match else None

        # 🏙 Município
        city = next((c for c in CITIES_ES if c.upper() in header.upper()), None)

        # 👩‍🏫 Professora e disciplina
        teacher_match = re.search(r"Professora?:\s+([^\n\r]+)", header)
        teacher, subject = None, None
        if teacher_match:
            full = teacher_match.group(1).strip()
            full = re.split(r"ANO:|Ensino|Fundamental", full)[0].strip()
            parts = full.split()
            if len(parts) > 1:
                teacher = parts[0]
                subject = normalize_subject(" ".join(parts[1:]))
            else:
                teacher = full

        # 🎓 Ano/Série
        grade_match = re.search(r"ANO:\s+([^\n\r]+)", header)
        grade = grade_match.group(1).strip() if grade_match else None

        # 📝 Título
        title_match = re.search(r"(Prova Trimestral)", header, re.IGNORECASE)
        exam_title = title_match.group(0).strip() if title_match else None

        # 📆 Trimestre
        trimester_match = re.search(r"(\dº|\d[o°])\s+TRIMESTRE", header, re.IGNORECASE)
        trimester = trimester_match.group(1).strip() if trimester_match else None

        # 👤 Estudante, turma, nota e data da mesma linha
        student_line = extract_field_line("Estudante:")
        student, turma, grade_value, date = None, None, None, None

        if student_line:
            student_match = re.search(r"Estudante:\s*([^\n\r:]+)", student_line)
            student = student_match.group(1).strip() if student_match else None

            turma_match = re.search(r"TURMA:\s*([^\n\r:]+)", student_line)
            turma = turma_match.group(1).strip() if turma_match else None

            grade_match = re.search(r"Valor:\s*([\d,\.]+)", student_line)
            grade_value = grade_match.group(1).strip() if grade_match else None

            date_match = re.search(r"Data:\s*(\d{1,2}/\d{1,2}/\d{2,4})", student_line)
            date = date_match.group(1).strip() if date_match else None

        return {
            "network": network,
            "school": school,
            "city": city,
            "teacher": teacher,
            "subject": subject,
            "exam_title": exam_title,
            "trimester": trimester,
            "grade": grade,
            "class": turma,
            "student": student,
            "grade_value": grade_value,
            "date": date
        }
