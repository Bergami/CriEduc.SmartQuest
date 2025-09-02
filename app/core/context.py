"""
Request context management for tracking user information across services.

Provides context variables to track user email and other request-specific
data throughout the request lifecycle.
"""
from contextvars import ContextVar
from typing import Optional

# Context variables for request tracking
_current_email: ContextVar[Optional[str]] = ContextVar('current_email', default=None)
_current_request_id: ContextVar[Optional[str]] = ContextVar('current_request_id', default=None)


def set_current_email(email: str) -> None:
    """
    Set the current user email in context.
    
    Args:
        email: User email
    """
    _current_email.set(email)


def get_current_email() -> Optional[str]:
    """
    Get the current user email from context.
    
    Returns:
        Current user email or None if not set
    """
    return _current_email.get()


def set_current_request_id(request_id: str) -> None:
    """
    Set the current request ID in context.
    
    Args:
        request_id: Request ID
    """
    _current_request_id.set(request_id)


def get_current_request_id() -> Optional[str]:
    """
    Get the current request ID from context.
    
    Returns:
        Current request ID or None if not set
    """
    return _current_request_id.get()


def clear_context() -> None:
    """
    Clear all context variables.
    """
    _current_email.set(None)
    _current_request_id.set(None)
