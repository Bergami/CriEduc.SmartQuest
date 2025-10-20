"""
Serviços de persistência

Este módulo contém interfaces e implementações para operações de persistência.
"""

from .i_simple_persistence_service import ISimplePersistenceService
from .mongodb_persistence_service import MongoDBPersistenceService
from .exceptions import (
    PersistenceError,
    ConnectionError,
    DocumentNotFoundError,
    ValidationError,
    DuplicateDocumentError
)

__all__ = [
    "ISimplePersistenceService",
    "MongoDBPersistenceService",
    "PersistenceError",
    "ConnectionError", 
    "DocumentNotFoundError",
    "ValidationError",
    "DuplicateDocumentError"
]