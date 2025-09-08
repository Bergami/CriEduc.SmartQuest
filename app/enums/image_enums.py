"""
Image Enums
==========

Enums related to image categories and processing status.
Migrated from app.models.internal.image_models
"""

from enum import Enum


class ImageCategory(str, Enum):
    """Categories for image classification."""
    HEADER = "header"    # Images in document header
    CONTENT = "content"  # Images in content/context blocks
    UNKNOWN = "unknown"  # Unknown or unclassified images



