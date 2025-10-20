"""
Serviços de infraestrutura

Contém serviços de infraestrutura como conexões e recursos externos.
"""

from .mongodb_connection_service import MongoDBConnectionService

__all__ = [
    "MongoDBConnectionService"
]