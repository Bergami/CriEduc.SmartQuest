"""
Internal Question Models

These models represent the complete question structure used internally,
including all processing metadata and answer validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class QuestionDifficulty(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"


class AnswerType(str, Enum):
    """Answer format types."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    OPEN_ENDED = "open_ended"
    NUMERICAL = "numerical"
    FILL_IN_BLANK = "fill_in_blank"
    UNKNOWN = "unknown"


class InternalAnswerOption(BaseModel):
    """
    Internal representation of an answer option.
    
    Contains all metadata for debugging and validation.
    """
    # Core option data
    label: str = Field(..., description="Option label (A, B, C, etc.)")
    text: str = Field(..., description="Option text content")
    is_correct: bool = Field(default=False, description="Whether this is the correct answer")
    
    # Processing metadata
    extraction_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of option extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about processing this option"
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Original raw text before processing"
    )
    
    @classmethod
    def from_legacy_option(cls, legacy_option: Dict[str, Any]) -> "InternalAnswerOption":
        """
        Create InternalAnswerOption from legacy format.
        
        Args:
            legacy_option: Legacy option dictionary
            
        Returns:
            InternalAnswerOption instance
        """
        return cls(
            label=legacy_option.get("label", ""),
            text=legacy_option.get("text", ""),
            is_correct=legacy_option.get("isCorrect", False),
            raw_text=str(legacy_option),
            extraction_confidence=legacy_option.get("confidence"),
            processing_notes="legacy_conversion"
        )
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy option format.
        
        Returns:
            Dictionary in legacy format
        """
        return {
            "label": self.label,
            "text": self.text,
            "isCorrect": self.is_correct
        }
    
    class Config:
        schema_extra = {
            "example": {
                "label": "A",
                "text": "O primeiro discípulo aplicou a criatividade.",
                "is_correct": True,
                "extraction_confidence": 0.95,
                "processing_notes": "Extracted from document text",
                "raw_text": "A) O primeiro discípulo aplicou a criatividade."
            }
        }


class InternalQuestionContent(BaseModel):
    """
    Internal representation of question content.
    
    Contains all content variations and processing metadata.
    """
    # Core content
    statement: str = Field(..., description="Main question statement")
    instruction: Optional[str] = Field(
        default=None,
        description="Additional instruction text"
    )
    
    # Processing metadata
    raw_statement: Optional[str] = Field(
        default=None,
        description="Original raw statement before processing"
    )
    extraction_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score of statement extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about processing this content"
    )
    
    @classmethod
    def from_legacy_content(cls, legacy_content: Any) -> "InternalQuestionContent":
        """
        Create InternalQuestionContent from legacy format.
        
        Args:
            legacy_content: Legacy content (string or dict)
            
        Returns:
            InternalQuestionContent instance
        """
        if isinstance(legacy_content, dict):
            statement = legacy_content.get("statement", "")
            instruction = legacy_content.get("instruction")
        else:
            statement = str(legacy_content)
            instruction = None
        
        return cls(
            statement=statement,
            instruction=instruction,
            raw_statement=str(legacy_content),
            processing_notes="legacy_conversion"
        )
    
    def to_legacy_format(self) -> str:
        """
        Convert to legacy content format.
        
        Returns:
            Question statement string
        """
        return self.statement
    
    class Config:
        schema_extra = {
            "example": {
                "statement": "Assinale a alternativa que indica o que fizeram o primeiro e o segundo discípulos.",
                "instruction": "Leia com atenção e responda:",
                "raw_statement": "1. Assinale a alternativa que indica o que fizeram o primeiro e o segundo discípulos.",
                "extraction_confidence": 0.92,
                "processing_notes": "Extracted from question block"
            }
        }


class InternalQuestion(BaseModel):
    """
    Complete internal representation of a question.
    
    Contains all question data, metadata, and processing information.
    """
    # Core question data
    number: int = Field(..., description="Question number")
    content: InternalQuestionContent = Field(..., description="Question content")
    options: List[InternalAnswerOption] = Field(
        default_factory=list,
        description="Answer options"
    )
    
    # Question metadata
    context_id: Optional[int] = Field(
        default=None,
        description="ID of associated context block"
    )
    answer_type: AnswerType = Field(
        default=AnswerType.UNKNOWN,
        description="Type of answer expected"
    )
    difficulty: QuestionDifficulty = Field(
        default=QuestionDifficulty.UNKNOWN,
        description="Question difficulty level"
    )
    
    # Image associations
    associated_images: List[str] = Field(
        default_factory=list,
        description="IDs of images associated with this question"
    )
    has_image: bool = Field(default=False, description="Whether question contains images")
    
    # Educational metadata
    subject: Optional[str] = Field(default=None, description="Subject area")
    topic: Optional[str] = Field(default=None, description="Specific topic")
    learning_objectives: List[str] = Field(
        default_factory=list,
        description="Learning objectives assessed"
    )
    
    # Processing metadata
    extraction_method: Optional[str] = Field(
        default=None,
        description="Method used to extract this question"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Overall confidence score of extraction"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Notes about processing this question"
    )
    validation_status: Optional[str] = Field(
        default=None,
        description="Status of question validation"
    )
    
    @classmethod
    def from_legacy_question(cls, legacy_question: Dict[str, Any]) -> "InternalQuestion":
        """
        Create InternalQuestion from legacy format.
        
        Args:
            legacy_question: Legacy question dictionary
            
        Returns:
            InternalQuestion instance
        """
        # Extract content
        content = InternalQuestionContent.from_legacy_content(
            legacy_question.get("content", "")
        )
        
        # Extract options
        options = []
        legacy_options = legacy_question.get("options", [])
        for opt in legacy_options:
            options.append(InternalAnswerOption.from_legacy_option(opt))
        
        # Determine answer type based on options
        answer_type = AnswerType.UNKNOWN
        if len(options) > 0:
            if len(options) == 2 and all(opt.text.lower() in ["verdadeiro", "falso", "true", "false"] for opt in options):
                answer_type = AnswerType.TRUE_FALSE
            else:
                answer_type = AnswerType.MULTIPLE_CHOICE
        
        return cls(
            number=legacy_question.get("number", 0),
            content=content,
            options=options,
            context_id=legacy_question.get("contextId"),
            answer_type=answer_type,
            has_image=legacy_question.get("hasImage", False),
            subject=legacy_question.get("subject"),
            extraction_method="legacy_conversion"
        )
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy question format.
        
        Returns:
            Dictionary in legacy format
        """
        return {
            "number": self.number,
            "content": self.content.to_legacy_format(),
            "options": [opt.to_legacy_format() for opt in self.options],
            "contextId": self.context_id,
            "hasImage": self.has_image,
            "subject": self.subject
        }
    
    def get_correct_answer(self) -> Optional[InternalAnswerOption]:
        """Get the correct answer option."""
        for option in self.options:
            if option.is_correct:
                return option
        return None
    
    def get_correct_answers(self) -> List[InternalAnswerOption]:
        """Get all correct answer options (for multiple correct answers)."""
        return [opt for opt in self.options if opt.is_correct]
    
    def add_image_association(self, image_id: str) -> None:
        """Add an image association to this question."""
        if image_id not in self.associated_images:
            self.associated_images.append(image_id)
            self.has_image = True
    
    def remove_image_association(self, image_id: str) -> None:
        """Remove an image association from this question."""
        if image_id in self.associated_images:
            self.associated_images.remove(image_id)
            self.has_image = len(self.associated_images) > 0
    
    def validate_structure(self) -> List[str]:
        """
        Validate question structure and return any issues.
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not self.content.statement.strip():
            issues.append("Question statement is empty")
        
        if self.answer_type == AnswerType.MULTIPLE_CHOICE and len(self.options) < 2:
            issues.append("Multiple choice question must have at least 2 options")
        
        if self.answer_type == AnswerType.TRUE_FALSE and len(self.options) != 2:
            issues.append("True/false question must have exactly 2 options")
        
        correct_answers = self.get_correct_answers()
        if len(correct_answers) == 0:
            issues.append("No correct answer specified")
        
        # Check for duplicate option labels
        labels = [opt.label for opt in self.options]
        if len(labels) != len(set(labels)):
            issues.append("Duplicate option labels found")
        
        return issues
    
    class Config:
        schema_extra = {
            "example": {
                "number": 1,
                "content": {
                    "statement": "Assinale a alternativa que indica o que fizeram o primeiro e o segundo discípulos.",
                    "instruction": "Leia com atenção e responda:"
                },
                "options": [
                    {
                        "label": "A",
                        "text": "O primeiro discípulo aplicou a criatividade.",
                        "is_correct": True
                    },
                    {
                        "label": "B",
                        "text": "O segundo discípulo pensou fora da caixa.",
                        "is_correct": False
                    }
                ],
                "context_id": 1,
                "answer_type": "multiple_choice",
                "difficulty": "medium",
                "has_image": False,
                "subject": "Língua Portuguesa",
                "topic": "Interpretação de texto",
                "extraction_method": "pattern_matching",
                "confidence_score": 0.89
            }
        }
