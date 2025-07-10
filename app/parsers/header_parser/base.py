from __future__ import annotations
from typing import Optional, Dict, Any

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
    def parse(header: str) -> Dict[str, Any]:
        lines = header.splitlines()

        def extract_field_line(label: str) -> Optional[str]:
            for line in lines:
                if label.lower() in line.lower():
                    return line.strip()
            return None

        student_line = extract_field_line("Estudante:")

        return {
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
            "grade_value": parse_grade_value(student_line),
            "date": parse_date(student_line),
        }
