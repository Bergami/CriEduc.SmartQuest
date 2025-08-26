import logging
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import Request

class StructuredLogger:
    """Logger estruturado para o SmartQuest"""
    
    def __init__(self, name: str = "smartquest"):
        self.logger = logging.getLogger(name)
        self._configure_logger()
    
    def _configure_logger(self):
        """Configura o logger com formato estruturado"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _create_log_entry(self, level: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria entrada de log estruturada"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "smartquest"
        }
        
        if context:
            # Converte valores não serializáveis para string
            safe_context = {}
            for key, value in context.items():
                try:
                    json.dumps(value)
                    safe_context[key] = value
                except (TypeError, ValueError):
                    safe_context[key] = str(value)
            entry["context"] = safe_context
            
        return entry
    
    def info(self, message: str, context: Dict[str, Any] = None, **kwargs):
        """Log de informação estruturado"""
        if kwargs:
            context = {**(context or {}), **kwargs}
        
        log_entry = self._create_log_entry("INFO", message, context)
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))
    
    def warning(self, message: str, context: Dict[str, Any] = None, **kwargs):
        """Log de warning estruturado"""
        if kwargs:
            context = {**(context or {}), **kwargs}
        
        log_entry = self._create_log_entry("WARNING", message, context)
        self.logger.warning(json.dumps(log_entry, ensure_ascii=False))
    
    def error(self, message: str, context: Dict[str, Any] = None, exception: Exception = None, **kwargs):
        """Log de erro estruturado"""
        if kwargs:
            context = {**(context or {}), **kwargs}
        
        if exception:
            context = context or {}
            context.update({
                "exception_type": type(exception).__name__,
                "exception_message": str(exception)
            })
            
            # Se for nossa exceção customizada, adiciona contexto extra
            if hasattr(exception, 'to_dict'):
                context["exception_details"] = exception.to_dict()
        
        log_entry = self._create_log_entry("ERROR", message, context)
        self.logger.error(json.dumps(log_entry, ensure_ascii=False))
    
    def debug(self, message: str, context: Dict[str, Any] = None, **kwargs):
        """Log de debug estruturado"""
        if kwargs:
            context = {**(context or {}), **kwargs}
        
        log_entry = self._create_log_entry("DEBUG", message, context)
        self.logger.debug(json.dumps(log_entry, ensure_ascii=False))

    def log_request_start(self, request: Request, context: Dict[str, Any] = None):
        """Log início de requisição"""
        req_context = {
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type")
        }
        
        if context:
            req_context.update(context)
        
        self.info("Request started", req_context)
    
    def log_request_end(self, request: Request, status_code: int, duration_ms: float, context: Dict[str, Any] = None):
        """Log fim de requisição"""
        req_context = {
            "method": request.method,
            "url": str(request.url),
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2)
        }
        
        if context:
            req_context.update(context)
        
        if status_code >= 400:
            self.error("Request completed with error", req_context)
        else:
            self.info("Request completed successfully", req_context)

# Instância global do logger
structured_logger = StructuredLogger()

# Export for compatibility
logger = structured_logger
