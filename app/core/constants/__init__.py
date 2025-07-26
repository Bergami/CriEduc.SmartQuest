# Core Constants Package
# Centralizes all application constants for better maintainability

from .paths import ProjectPaths
from .mock_data import MockDataConstants
from .general import GeneralConstants

__all__ = [
    'ProjectPaths',
    'MockDataConstants', 
    'GeneralConstants'
]
