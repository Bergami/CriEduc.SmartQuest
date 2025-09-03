from __future__ import annotations
from typing import Optional, Dict, Any, List

from .parse_network import parse_network
from .parse_school import parse_school
from .parse_city import parse_city
from .parse_teacher import parse_teacher
from .parse_subject import parse_subject
from .parse_exam_title import parse_exam_title
from .parse_trimester import parse_trimester
from .parse_grade import parse_grade
from .parse_class import parse_class
from .parse_student import parse_student
from .parse_grade_value import parse_grade_value
from .parse_date import parse_date


class HeaderParser:
    """Parse metadata fields from an exam header block."""

    @staticmethod
    def parse(header: str, header_images: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        🚨 MÉTODO LEGADO - Mantido para compatibilidade
        
        Parse header and return dictionary format (legacy format).
        Usado por endpoints que ainda não migraram para Pydantic.
        
        Args:
            header: Header text to parse
            header_images: Optional list of header images
            
        Returns:
            Dictionary with parsed header fields
        """
        lines = header.splitlines()

        def extract_field_line(label: str) -> Optional[str]:
            for line in lines:
                if label.lower() in line.lower():
                    return line.strip()
            return None

        student_line = extract_field_line("Estudante:")

        result = {
            "network": parse_network(header, lines),
            "school": parse_school(header),
            "city": parse_city(header),
            "teacher": parse_teacher(header),
            "subject": parse_subject(header),
            "exam_title": parse_exam_title(header),
            "trimester": parse_trimester(header),
            "grade": parse_grade(header),
            "class": parse_class(student_line),
            "student": parse_student(student_line),
            "grade_value": parse_grade_value(header),
            "date": parse_date(student_line),
        }
        
        # Add images array if header_images are provided
        if header_images:
            result["images"] = header_images
        else:
            result["images"] = []

        return result

    @staticmethod
    def parse_to_pydantic(
        header: str, 
        header_images: Optional[List] = None,
        content_images: Optional[List] = None
    ):
        """
        🆕 MÉTODO PYDANTIC - Retorna diretamente InternalDocumentMetadata
        
        Parse header and return typed Pydantic model directly.
        Usado por endpoints migrados para Pydantic.
        
        Args:
            header: Header text to parse
            header_images: Optional list of header images (InternalImageData)
            content_images: Optional list of content images (InternalImageData)
            
        Returns:
            InternalDocumentMetadata with full type safety
        """
        from app.models.internal import InternalDocumentMetadata
        
        lines = header.splitlines()

        def extract_field_line(label: str) -> Optional[str]:
            for line in lines:
                if label.lower() in line.lower():
                    return line.strip()
            return None

        student_line = extract_field_line("Estudante:")

        # ✅ Criar diretamente o modelo Pydantic
        return InternalDocumentMetadata(
            network=parse_network(header, lines),
            school=parse_school(header),
            city=parse_city(header),
            teacher=parse_teacher(header),
            subject=parse_subject(header),
            exam_title=parse_exam_title(header),
            trimester=parse_trimester(header),
            grade=parse_grade(header),
            class_=parse_class(student_line),
            student=parse_student(student_line),
            grade_value=parse_grade_value(header),
            date=parse_date(student_line),
            header_images=header_images or [],
            content_images=content_images or []
        )
