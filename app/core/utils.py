import time
from datetime import datetime
from typing import Callable
from functools import wraps
from fastapi import UploadFile, Request, HTTPException
from .exceptions import SmartQuestException
from .logging import structured_logger

def is_pdf(file: UploadFile) -> bool:
    """Verifica se o arquivo é um PDF válido"""
    file.file.seek(0)
    header = file.file.read(5)
    file.file.seek(0)
    return header == b"%PDF-"

def handle_exceptions(operation_name: str = "operation"):
    """
    Decorator para tratamento padronizado de exceções em controllers
    
    Args:
        operation_name: Nome da operação para logs
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Tenta extrair request do primeiro argumento se for Request
            request = None
            if args and hasattr(args[0], 'method') and hasattr(args[0], 'url'):
                request = args[0]
            
            try:
                # Log início da operação
                context = {
                    "operation": operation_name,
                    "function": func.__name__
                }
                
                if request:
                    structured_logger.log_request_start(request, context)
                else:
                    structured_logger.info(f"Starting {operation_name}", context)
                
                # Executa a função
                result = await func(*args, **kwargs)
                
                # Log sucesso
                duration_ms = (time.time() - start_time) * 1000
                context["duration_ms"] = round(duration_ms, 2)
                
                if request:
                    structured_logger.log_request_end(request, 200, duration_ms, context)
                else:
                    structured_logger.info(f"Completed {operation_name} successfully", context)
                
                return result
                
            except SmartQuestException as e:
                # Log erro personalizado
                duration_ms = (time.time() - start_time) * 1000
                context = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2)
                }
                
                if request:
                    structured_logger.log_request_end(request, e.status_code, duration_ms, context)
                
                structured_logger.error(f"SmartQuest exception in {operation_name}", context, exception=e)
                
                # Retorna HTTPException para FastAPI
                raise e.to_http_exception()
                
            except HTTPException as e:
                # Log HTTPException do FastAPI
                duration_ms = (time.time() - start_time) * 1000
                context = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2),
                    "status_code": e.status_code
                }
                
                if request:
                    structured_logger.log_request_end(request, e.status_code, duration_ms, context)
                
                structured_logger.error(f"HTTP exception in {operation_name}", context, exception=e)
                raise
                
            except Exception as e:
                # Log erro inesperado
                duration_ms = (time.time() - start_time) * 1000
                context = {
                    "operation": operation_name,
                    "function": func.__name__,
                    "duration_ms": round(duration_ms, 2)
                }
                
                if request:
                    structured_logger.log_request_end(request, 500, duration_ms, context)
                
                structured_logger.error(f"Unexpected error in {operation_name}", context, exception=e)
                
                # Converte erro inesperado para HTTPException
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "internal_server_error",
                        "message": "An unexpected error occurred while processing your request",
                        "type": "internal_server_error",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
        
        return wrapper
    return decorator
