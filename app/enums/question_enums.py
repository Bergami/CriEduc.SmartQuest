"""
Question Enums
=============

Enums related to answer types.
Migrated from app.models.internal.question_models
"""

from enum import Enum


class AnswerType(str, Enum):
    """Answer format types."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    UNKNOWN = "unknown"
