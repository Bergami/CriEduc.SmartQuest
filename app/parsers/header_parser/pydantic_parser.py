"""
Pydantic-based header parser for SmartQuest.
Extracts document metadata directly to Pydantic models without Dict conversion.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.internal.document_models import InternalDocumentMetadata
from app.models.internal.image_models import InternalImageData

# Import existing parser functions for reuse
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

logger = logging.getLogger(__name__)

class PydanticHeaderParser:
    """
    Pydantic-based header parser that extracts metadata directly to InternalDocumentMetadata.
    Eliminates Dict->Pydantic conversion issues from the legacy HeaderParser.
    """
    
    def __init__(self):
        """Initialize the Pydantic header parser."""
        logger.info("🔧 PydanticHeaderParser initialized")
    
    @staticmethod
    def parse(
        header: str, 
        header_images: Optional[List[Dict[str, Any]]] = None
    ) -> InternalDocumentMetadata:
        """
        Parse header from extracted text directly to Pydantic model.
        
        Args:
            header: Extracted header text from Azure Document Intelligence
            header_images: Optional list of header images
            
        Returns:
            InternalDocumentMetadata: Pydantic model with extracted metadata
        """
        try:
            logger.info("🔍 Starting Pydantic header parsing")
            
            # Parse header using existing extraction functions
            lines = header.splitlines()
            
            def extract_field_line(label: str) -> Optional[str]:
                for line in lines:
                    if label.lower() in line.lower():
                        return line.strip()
                return None

            student_line = extract_field_line("Estudante:")
            
            # Extract all fields using proven parsing functions
            network = parse_network(header, lines)
            school = parse_school(header)
            city = parse_city(header)
            teacher = parse_teacher(header)
            subject = parse_subject(header)
            exam_title = parse_exam_title(header)
            trimester = parse_trimester(header)
            grade = parse_grade(header)
            class_ = parse_class(student_line)
            student = parse_student(student_line)
            grade_value = parse_grade_value(header)
            date = parse_date(student_line)
            
            # Convert header_images to InternalImageData if provided
            internal_header_images = []
            if header_images:
                for img_data in header_images:
                    try:
                        internal_img = InternalImageData(
                            id=img_data.get("id", f"header_img_{len(internal_header_images)}"),
                            base64_content=img_data.get("content", ""),
                            category="header",
                            page_number=img_data.get("page_number", 1),
                            confidence_score=img_data.get("confidence", 0.0)
                        )
                        internal_header_images.append(internal_img)
                    except Exception as e:
                        logger.warning(f"⚠️ Error converting header image: {str(e)}")
            
            # Calculate extraction confidence
            extracted_fields = [
                network, school, city, teacher, subject, exam_title,
                trimester, grade, class_, student, grade_value, date
            ]
            non_empty_fields = len([f for f in extracted_fields if f])
            total_fields = len(extracted_fields)
            confidence = non_empty_fields / total_fields if total_fields > 0 else 0.0
            
            # Create Pydantic model directly
            metadata = InternalDocumentMetadata(
                network=network,
                school=school,
                city=city,
                teacher=teacher,
                subject=subject,
                exam_title=exam_title,
                trimester=trimester,
                grade=grade,
                class_=class_,
                student=student,
                grade_value=grade_value,
                date=date,
                header_images=internal_header_images,
                content_images=[],  # Will be populated later
                extraction_confidence=confidence,
                processing_notes=f"Extracted {non_empty_fields}/{total_fields} fields"
            )
            
            logger.info("✅ Pydantic header parsing completed successfully")
            PydanticHeaderParser._log_extracted_fields(metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Error in Pydantic header parsing: {str(e)}")
            # Return minimal metadata on error
            return InternalDocumentMetadata(
                extraction_confidence=0.0,
                processing_notes=f"Parsing failed: {str(e)}"
            )
    
    @staticmethod
    def _log_extracted_fields(metadata: InternalDocumentMetadata) -> None:
        """Log extracted fields for debugging."""
        extracted_fields = []
        
        if metadata.network:
            extracted_fields.append(f"network: {metadata.network}")
        if metadata.school:
            extracted_fields.append(f"school: {metadata.school}")
        if metadata.subject:
            extracted_fields.append(f"subject: {metadata.subject}")
        if metadata.teacher:
            extracted_fields.append(f"teacher: {metadata.teacher}")
        if metadata.exam_title:
            extracted_fields.append(f"exam_title: {metadata.exam_title}")
        if metadata.grade:
            extracted_fields.append(f"grade: {metadata.grade}")
            
        logger.info(f"📋 Extracted fields: {', '.join(extracted_fields)}")
        logger.info(f"🎯 Confidence score: {metadata.extraction_confidence:.2f}")
        logger.info(f"📸 Header images: {len(metadata.header_images)}")
