"""
API Response DTOs for Questions

These DTOs represent simplified question data optimized for API responses.
They focus on educational content without internal processing metadata.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnswerOptionDTO(BaseModel):
    """Simplified answer option for API responses."""
    label: str = Field(..., description="Option label (A, B, C, etc.)")
    text: str = Field(..., description="Option text content")
    is_correct: bool = Field(default=False, description="Whether this is the correct answer")
    
    @classmethod
    def from_internal_option(cls, internal_option) -> "AnswerOptionDTO":
        """
        Create AnswerOptionDTO from InternalAnswerOption.
        
        Args:
            internal_option: InternalAnswerOption instance
            
        Returns:
            Simplified AnswerOptionDTO
        """
        return cls(
            label=internal_option.label,
            text=internal_option.text,
            is_correct=internal_option.is_correct
        )
    
    class Config:
        schema_extra = {
            "example": {
                "label": "A",
                "text": "O primeiro discípulo aplicou a criatividade.",
                "is_correct": True
            }
        }


class QuestionContentDTO(BaseModel):
    """Simplified question content for API responses."""
    statement: str = Field(..., description="Question statement")
    instruction: Optional[str] = Field(
        default=None,
        description="Additional instruction text"
    )
    
    @classmethod
    def from_internal_content(cls, internal_content) -> "QuestionContentDTO":
        """
        Create QuestionContentDTO from InternalQuestionContent.
        
        Args:
            internal_content: InternalQuestionContent instance
            
        Returns:
            Simplified QuestionContentDTO
        """
        return cls(
            statement=internal_content.statement,
            instruction=internal_content.instruction
        )
    
    class Config:
        schema_extra = {
            "example": {
                "statement": "Assinale a alternativa que indica o que fizeram o primeiro e o segundo discípulos.",
                "instruction": "Leia com atenção e responda:"
            }
        }


class QuestionDTO(BaseModel):
    """
    Simplified question for API responses.
    
    Contains essential question information for API consumers,
    without internal processing metadata or debugging information.
    """
    # Core question data
    number: int = Field(..., description="Question number")
    content: QuestionContentDTO = Field(..., description="Question content")
    options: List[AnswerOptionDTO] = Field(
        default_factory=list,
        description="Answer options"
    )
    
    # Educational metadata
    context_id: Optional[int] = Field(
        default=None,
        description="ID of associated context block"
    )
    answer_type: str = Field(
        default="unknown",
        description="Type of answer expected"
    )
    difficulty: str = Field(
        default="unknown",
        description="Question difficulty level"
    )
    subject: Optional[str] = Field(default=None, description="Subject area")
    topic: Optional[str] = Field(default=None, description="Specific topic")
    
    # Image associations (simplified)
    has_image: bool = Field(default=False, description="Whether question contains images")
    image_ids: List[str] = Field(
        default_factory=list,
        description="IDs of associated images"
    )
    
    # Quality indicators
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Overall extraction confidence (0-1)"
    )
    
    @classmethod
    def from_internal_question(cls, internal_question) -> "QuestionDTO":
        """
        Create QuestionDTO from InternalQuestion.
        
        Args:
            internal_question: InternalQuestion instance
            
        Returns:
            Simplified QuestionDTO for API response
        """
        # Convert content
        content_dto = QuestionContentDTO.from_internal_content(internal_question.content)
        
        # Convert options
        option_dtos = [
            AnswerOptionDTO.from_internal_option(opt)
            for opt in internal_question.options
        ]
        
        return cls(
            number=internal_question.number,
            content=content_dto,
            options=option_dtos,
            context_id=internal_question.context_id,
            answer_type=internal_question.answer_type.value,
            difficulty="unknown",  # Default value since difficulty was removed
            subject=internal_question.subject,
            topic=internal_question.topic,
            has_image=internal_question.has_image,
            image_ids=internal_question.associated_images,
            confidence=internal_question.confidence_score
        )
    
    def get_correct_answer(self) -> Optional[AnswerOptionDTO]:
        """Get the correct answer option."""
        for option in self.options:
            if option.is_correct:
                return option
        return None
    
    def get_correct_answers(self) -> List[AnswerOptionDTO]:
        """Get all correct answer options (for multiple correct answers)."""
        return [opt for opt in self.options if opt.is_correct]
    
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
                "subject": "Língua Portuguesa",
                "topic": "Interpretação de texto",
                "has_image": False,
                "image_ids": [],
                "confidence": 0.89
            }
        }


class QuestionListDTO(BaseModel):
    """
    Container for multiple questions in API responses.
    """
    questions: List[QuestionDTO] = Field(
        default_factory=list,
        description="List of questions"
    )
    total_count: int = Field(
        default=0,
        description="Total number of questions"
    )
    
    # Summary statistics
    with_images: int = Field(
        default=0,
        description="Number of questions with images"
    )
    answer_types: dict = Field(
        default_factory=dict,
        description="Count of each answer type"
    )
    difficulty_levels: dict = Field(
        default_factory=dict,
        description="Count of each difficulty level"
    )
    subjects: dict = Field(
        default_factory=dict,
        description="Count of questions per subject"
    )
    
    @classmethod
    def from_internal_questions(cls, internal_questions: List) -> "QuestionListDTO":
        """
        Create QuestionListDTO from list of InternalQuestion.
        
        Args:
            internal_questions: List of InternalQuestion instances
            
        Returns:
            QuestionListDTO for API response
        """
        # Convert questions
        question_dtos = [
            QuestionDTO.from_internal_question(q)
            for q in internal_questions
        ]
        
        # Calculate statistics
        with_images = sum(1 for q in question_dtos if q.has_image)
        
        # Count answer types
        answer_types = {}
        for q in question_dtos:
            answer_types[q.answer_type] = answer_types.get(q.answer_type, 0) + 1
        
        # Count difficulty levels
        difficulty_levels = {}
        for q in question_dtos:
            difficulty_levels[q.difficulty] = difficulty_levels.get(q.difficulty, 0) + 1
        
        # Count subjects
        subjects = {}
        for q in question_dtos:
            if q.subject:
                subjects[q.subject] = subjects.get(q.subject, 0) + 1
        
        return cls(
            questions=question_dtos,
            total_count=len(question_dtos),
            with_images=with_images,
            answer_types=answer_types,
            difficulty_levels=difficulty_levels,
            subjects=subjects
        )
    
    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    {
                        "number": 1,
                        "content": {
                            "statement": "Question text..."
                        },
                        "options": [
                            {
                                "label": "A",
                                "text": "Option A",
                                "is_correct": True
                            }
                        ],
                        "answer_type": "multiple_choice",
                        "difficulty": "medium",
                        "has_image": False
                    }
                ],
                "total_count": 1,
                "with_images": 0,
                "answer_types": {
                    "multiple_choice": 1
                },
                "difficulty_levels": {
                    "medium": 1
                },
                "subjects": {
                    "Língua Portuguesa": 1
                }
            }
        }
