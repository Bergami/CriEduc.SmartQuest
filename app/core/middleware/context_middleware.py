"""
Request context middleware for automatic email tracking.

Middleware that extracts user email from request and sets it in context
for use by services and cache system.
"""
import json
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import set_current_email, set_current_request_id, clear_context
from uuid import uuid4

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and set request context variables.
    
    Automatically extracts user email from request and sets it in context
    for use by services throughout the request lifecycle.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and set context variables.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware in chain
            
        Returns:
            Response object
        """
        # Generate request ID
        request_id = str(uuid4())
        set_current_request_id(request_id)
        
        # Extract email from request
        email = await self._extract_email_from_request(request)
        
        if email:
            set_current_email(email)
            logger.debug(f"Set email in context: {email} (request: {request_id})")
        else:
            logger.debug(f"No email found in request (request: {request_id})")
        
        try:
            # Process request
            response = await call_next(request)
            return response
        finally:
            # Clear context after request
            clear_context()
    
    async def _extract_email_from_request(self, request: Request) -> str:
        """
        Extract email from various sources in the request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User email if found, None otherwise
        """
        try:
            # 1. Try query parameters
            if 'email' in request.query_params:
                return request.query_params['email']
            
            # 2. Try form data (for multipart/form-data)
            if request.headers.get('content-type', '').startswith('multipart/form-data'):
                # Note: We can't read form data here without consuming the stream
                # This will be handled in the endpoint
                pass
            
            # 3. Try JSON body (for application/json)
            elif request.headers.get('content-type', '').startswith('application/json'):
                # Read body carefully to avoid consuming the stream
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        if isinstance(data, dict) and 'email' in data:
                            return data['email']
                    except json.JSONDecodeError:
                        pass
            
            # 4. Try headers
            if 'x-user-email' in request.headers:
                return request.headers['x-user-email']
                
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting email from request: {e}")
            return None
