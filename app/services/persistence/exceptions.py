"""
Exceções personalizadas para serviços de persistência

Define hierarquia de exceções específicas para operações de persistência.
"""


class PersistenceError(Exception):
    """Exceção base para erros de persistência."""
    
    def __init__(self, message: str, operation: str = None, collection: str = None, document_id: str = None):
        self.message = message
        self.operation = operation
        self.collection = collection
        self.document_id = document_id
        super().__init__(self.message)

    def __str__(self):
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.collection:
            parts.append(f"Collection: {self.collection}")
        if self.document_id:
            parts.append(f"Document ID: {self.document_id}")
        return " | ".join(parts)


class ConnectionError(PersistenceError):
    """Erro de conexão com o banco de dados."""
    pass


class DocumentNotFoundError(PersistenceError):
    """Documento não encontrado."""
    pass


class ValidationError(PersistenceError):
    """Erro de validação de dados."""
    pass


class DuplicateDocumentError(PersistenceError):
    """Documento duplicado."""
    pass