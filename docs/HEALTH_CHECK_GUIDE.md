# 🏥 Health Check Development Guide

**Guia completo para criação e manutenção de health checks no SmartQuest API**

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Regras e Padrões](#regras-e-padrões)
- [Como Adicionar um Novo Health Check](#como-adicionar-um-novo-health-check)
- [Classificação de Dependências](#classificação-de-dependências)
- [Boas Práticas](#boas-práticas)
- [Testes](#testes)
- [Exemplos](#exemplos)

---

## 🎯 Visão Geral

O sistema de health check do SmartQuest API é responsável por:

- ✅ Verificar a saúde de todas as dependências externas
- ✅ Fornecer diagnósticos detalhados para troubleshooting
- ✅ Permitir monitoramento automatizado via status HTTP
- ✅ Diferenciar entre falhas críticas e não-críticas

**Endpoint**: `GET /health/`

**Respostas**:

- `200 OK` - Sistema saudável ou degradado (operacional)
- `503 Service Unavailable` - Sistema não pode operar (dependências críticas falharam)

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────┐
│          FastAPI Endpoint (/health/)            │
│                                                 │
│  1. Cria HealthChecker(container)               │
│  2. Executa checker.check_all(settings)         │
│  3. Calcula status geral                        │
│  4. Retorna HealthResponse                      │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│             HealthChecker Class                 │
│                                                 │
│  • check_mongodb() → DependencyStatus           │
│  • check_blob_storage() → DependencyStatus      │
│  • check_azure_ai() → DependencyStatus          │
│  • check_all() → Dict[str, DependencyStatus]    │
│  • calculate_overall_status() → Status          │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│          DI Container & Services                │
│                                                 │
│  • MongoDBConnectionService                     │
│  • IImageUploadService (Blob Storage)           │
│  • Settings (Azure AI Config)                   │
└─────────────────────────────────────────────────┘
```

### Classes e Modelos

```python
class DependencyStatus(BaseModel):
    status: str      # "healthy" | "unhealthy" | "degraded"
    message: str     # Human-readable status message
    details: Dict    # Diagnostic information

class HealthResponse(BaseModel):
    status: str                              # Overall system status
    message: str                             # Overall status message
    timestamp: datetime                      # Check execution time
    service: Dict[str, str]                  # API metadata
    environment: str                         # Environment name
    dependencies: Dict[str, DependencyStatus] # Individual checks
    endpoints: Dict[str, str]                # Available endpoints

class HealthChecker:
    CRITICAL_SERVICES = {"mongodb", "azure_blob_storage"}

    def __init__(self, container, logger)
    async def check_mongodb() -> DependencyStatus
    async def check_blob_storage() -> DependencyStatus
    def check_azure_ai(settings) -> DependencyStatus
    async def check_all(settings) -> Dict[str, DependencyStatus]
    def calculate_overall_status(dependencies) -> Tuple[str, str, List[str]]
```

---

## 📐 Regras e Padrões

### ✅ REGRA 1: Todo Health Check DEVE ser um método da classe `HealthChecker`

**❌ NÃO FAZER**:

```python
# Função privada isolada
async def _check_my_service_health() -> DependencyStatus:
    ...
```

**✅ FAZER**:

```python
class HealthChecker:
    async def check_my_service(self) -> DependencyStatus:
        """
        Check MyService health and connectivity.

        Verifies:
            - Service is registered in DI Container
            - Service is accessible
            - Service passes health check

        Returns:
            DependencyStatus with service health information
        """
        ...
```

---

### ✅ REGRA 2: Health Checks Assíncronos DEVEM usar `async def`

Para serviços que fazem I/O (rede, banco de dados, APIs externas):

```python
async def check_my_service(self) -> DependencyStatus:
    """Check service that requires I/O operations."""
    try:
        # I/O operations
        result = await service.verify_connection()
        return DependencyStatus(status="healthy", ...)
    except Exception as e:
        return DependencyStatus(status="unhealthy", ...)
```

Para verificações síncronas (configuração, validação de variáveis):

```python
def check_my_config(self, settings) -> DependencyStatus:
    """Check configuration without I/O."""
    has_config = bool(settings.my_config_value)
    if has_config:
        return DependencyStatus(status="healthy", ...)
    return DependencyStatus(status="degraded", ...)
```

---

### ✅ REGRA 3: Retornar SEMPRE `DependencyStatus` - NUNCA lançar exceções

**❌ NÃO FAZER**:

```python
async def check_my_service(self) -> DependencyStatus:
    service = self.container.resolve(MyService)
    result = await service.ping()  # Pode lançar exceção
    return DependencyStatus(status="healthy", ...)
```

**✅ FAZER**:

```python
async def check_my_service(self) -> DependencyStatus:
    try:
        if not self.container.is_registered(MyService):
            return DependencyStatus(
                status="unhealthy",
                message="Service not registered",
                details={"error": "Service not configured"}
            )

        service = self.container.resolve(MyService)
        result = await service.ping()

        return DependencyStatus(
            status="healthy",
            message="Service operational",
            details={"response_time": result.time}
        )

    except Exception as e:
        self.logger.error(f"Service check failed: {e}")
        return DependencyStatus(
            status="unhealthy",
            message="Service check failed",
            details={"error": str(e)}
        )
```

---

### ✅ REGRA 4: Fornecer detalhes diagnósticos úteis

**Informações que DEVEM estar em `details`**:

```python
# ✅ Bom exemplo
DependencyStatus(
    status="healthy",
    message="MongoDB connected",
    details={
        "database": "smartquest",
        "collections_count": 5,
        "collections": ["users", "documents", ...],
        "response_time_ms": 15
    }
)

# ❌ Detalhes insuficientes
DependencyStatus(
    status="healthy",
    message="MongoDB connected",
    details={}  # Sem informações diagnósticas
)
```

---

### ✅ REGRA 5: Usar logging adequado

```python
async def check_my_service(self) -> DependencyStatus:
    try:
        # Log de início para debug
        self.logger.debug("Starting MyService health check")

        result = await service.ping()

        # Log de sucesso
        self.logger.info(f"MyService healthy: {result}")

        return DependencyStatus(status="healthy", ...)

    except ConnectionError as e:
        # Log de erro com nível apropriado
        self.logger.error(f"MyService connection failed: {e}")
        return DependencyStatus(status="unhealthy", ...)

    except Exception as e:
        # Log de exceções inesperadas
        self.logger.exception(f"Unexpected error in MyService check: {e}")
        return DependencyStatus(status="unhealthy", ...)
```

---

## 🆕 Como Adicionar um Novo Health Check

### Passo 1: Adicionar método à classe `HealthChecker`

```python
# Em: app/api/controllers/health.py

class HealthChecker:
    # ... métodos existentes ...

    async def check_redis(self) -> DependencyStatus:
        """
        Check Redis cache connectivity and health.

        Verifies:
            - Service is registered in DI Container
            - Redis connection is established
            - PING command succeeds
            - Memory usage is within limits

        Returns:
            DependencyStatus with Redis health information including:
                - Connection status
                - Memory usage
                - Number of keys
                - Redis version
        """
        try:
            from app.services.cache.redis_service import RedisService

            # 1. Check service registration
            if not self.container.is_registered(RedisService):
                return DependencyStatus(
                    status="unhealthy",
                    message="Redis service not registered in DI Container",
                    details={"error": "Service not configured"}
                )

            # 2. Resolve service
            redis_service = self.container.resolve(RedisService)

            # 3. Test connectivity
            try:
                ping_result = await redis_service.ping()
                if not ping_result:
                    return DependencyStatus(
                        status="unhealthy",
                        message="Redis PING failed",
                        details={"error": "PING returned False"}
                    )
            except Exception as conn_error:
                self.logger.error(f"Redis connection failed: {conn_error}")
                return DependencyStatus(
                    status="unhealthy",
                    message="Failed to connect to Redis",
                    details={"error": str(conn_error)}
                )

            # 4. Gather diagnostic information
            info = await redis_service.get_info()

            return DependencyStatus(
                status="healthy",
                message="Redis connected and operational",
                details={
                    "version": info.get("redis_version"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory_human": info.get("used_memory_human"),
                    "keys": await redis_service.dbsize()
                }
            )

        except Exception as e:
            self.logger.error(f"Redis health check error: {e}")
            return DependencyStatus(
                status="unhealthy",
                message="Redis health check failed",
                details={"error": str(e)}
            )
```

### Passo 2: Adicionar ao método `check_all()`

```python
async def check_all(self, settings) -> Dict[str, DependencyStatus]:
    """Execute all health checks concurrently."""

    # Execute async checks in parallel
    mongodb_task = self.check_mongodb()
    blob_task = self.check_blob_storage()
    redis_task = self.check_redis()  # ← NOVO

    # Wait for all
    mongodb_result, blob_result, redis_result = await asyncio.gather(
        mongodb_task,
        blob_task,
        redis_task,  # ← NOVO
        return_exceptions=True
    )

    # Handle exceptions
    if isinstance(redis_result, Exception):
        self.logger.error(f"Redis check raised exception: {redis_result}")
        redis_result = DependencyStatus(
            status="unhealthy",
            message="Redis check failed with exception",
            details={"error": str(redis_result)}
        )

    # Synchronous checks
    azure_ai_result = self.check_azure_ai(settings)

    return {
        "mongodb": mongodb_result,
        "azure_blob_storage": blob_result,
        "redis": redis_result,  # ← NOVO
        "azure_document_intelligence": azure_ai_result
    }
```

### Passo 3: Classificar criticidade

Se o serviço for **CRÍTICO** (sistema não pode operar sem ele):

```python
class HealthChecker:
    # Adicionar à lista de serviços críticos
    CRITICAL_SERVICES = {
        "mongodb",
        "azure_blob_storage",
        "redis"  # ← NOVO (se crítico)
    }
```

Se o serviço for **NÃO CRÍTICO** (sistema pode degradar gracefully):

- Não adicionar ao `CRITICAL_SERVICES`
- O sistema ficará como "degraded" se falhar

### Passo 4: Testar

```python
# tests/unit/api/controllers/test_health_checker.py

@pytest.mark.asyncio
async def test_check_redis_healthy():
    """Test Redis health check when service is healthy."""
    # Arrange
    mock_container = Mock()
    mock_redis = Mock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.get_info = AsyncMock(return_value={
        "redis_version": "6.2.0",
        "connected_clients": 5,
        "used_memory_human": "1.5M"
    })
    mock_redis.dbsize = AsyncMock(return_value=1000)

    mock_container.is_registered.return_value = True
    mock_container.resolve.return_value = mock_redis

    checker = HealthChecker(mock_container)

    # Act
    result = await checker.check_redis()

    # Assert
    assert result.status == "healthy"
    assert "Redis connected" in result.message
    assert result.details["version"] == "6.2.0"
    assert result.details["keys"] == 1000
```

---

## 🎯 Classificação de Dependências

### Serviços CRÍTICOS (CRITICAL_SERVICES)

**Critérios**:

- Sistema **NÃO PODE** operar sem este serviço
- Falha resulta em `503 Service Unavailable`
- Exemplo: Banco de dados principal, autenticação

**Exemplos Atuais**:

- ✅ MongoDB - Persistência de dados obrigatória
- ✅ Azure Blob Storage - Armazenamento de imagens obrigatório

**Comportamento**:

```python
if critical_service.status != "healthy":
    overall_status = "unhealthy"  # HTTP 503
```

### Serviços NÃO CRÍTICOS

**Critérios**:

- Sistema **PODE** operar com funcionalidade reduzida
- Falha resulta em `200 OK` com status "degraded"
- Sistema tem fallback ou modo degradado

**Exemplos Atuais**:

- ✅ Azure Document Intelligence - Pode usar mock se indisponível

**Comportamento**:

```python
if non_critical_service.status != "healthy":
    overall_status = "degraded"  # HTTP 200
```

---

## 🎨 Boas Práticas

### ✅ DO: Use verificação incremental

```python
async def check_my_service(self) -> DependencyStatus:
    # 1. Check registration first
    if not self.container.is_registered(MyService):
        return DependencyStatus(status="unhealthy", ...)

    # 2. Resolve service
    service = self.container.resolve(MyService)

    # 3. Test basic connectivity
    if not await service.can_connect():
        return DependencyStatus(status="unhealthy", ...)

    # 4. Test functionality
    if not await service.ping():
        return DependencyStatus(status="degraded", ...)

    # 5. Gather diagnostics
    info = await service.get_info()
    return DependencyStatus(status="healthy", details=info)
```

### ✅ DO: Timeout em operações de rede

```python
async def check_external_api(self) -> DependencyStatus:
    try:
        # Set timeout to prevent hanging
        async with asyncio.timeout(5.0):  # Python 3.11+
            result = await api_service.health()

        return DependencyStatus(status="healthy", ...)

    except asyncio.TimeoutError:
        return DependencyStatus(
            status="unhealthy",
            message="API health check timeout",
            details={"error": "Request timeout after 5s"}
        )
```

### ✅ DO: Categorize status corretamente

```python
# Serviço completamente indisponível
return DependencyStatus(status="unhealthy", ...)

# Serviço disponível mas com problemas
return DependencyStatus(status="degraded", ...)

# Serviço totalmente funcional
return DependencyStatus(status="healthy", ...)
```

### ❌ DON'T: Fazer operações pesadas

```python
# ❌ NÃO FAZER: Verificação muito lenta
async def check_database(self):
    # Scanning milhões de registros
    count = await db.count_all_documents()  # Muito lento!
    return DependencyStatus(...)

# ✅ FAZER: Verificação rápida
async def check_database(self):
    # Simple ping test
    await db.admin.command('ping')  # Rápido!
    return DependencyStatus(...)
```

### ❌ DON'T: Expor informações sensíveis

```python
# ❌ NÃO FAZER
details={
    "connection_string": "mongodb://user:password@host",  # Senha exposta!
    "api_key": settings.secret_key  # Chave exposta!
}

# ✅ FAZER
details={
    "database": "smartquest",
    "host": "localhost",
    "authenticated": True  # Sem expor credenciais
}
```

---

## 🧪 Testes

### Estrutura de Testes

```
tests/
└── unit/
    └── api/
        └── controllers/
            └── test_health_checker.py  # Testes da classe HealthChecker
```

### Template de Teste

```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.api.controllers.health import HealthChecker, DependencyStatus

class TestHealthChecker:
    """Test suite for HealthChecker class."""

    @pytest.mark.asyncio
    async def test_check_service_healthy(self):
        """Test service health check when healthy."""
        # Arrange
        mock_container = Mock()
        mock_service = Mock()
        mock_service.ping = AsyncMock(return_value=True)

        mock_container.is_registered.return_value = True
        mock_container.resolve.return_value = mock_service

        checker = HealthChecker(mock_container)

        # Act
        result = await checker.check_my_service()

        # Assert
        assert result.status == "healthy"
        assert "operational" in result.message.lower()
        mock_service.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_service_not_registered(self):
        """Test service health check when not registered."""
        # Arrange
        mock_container = Mock()
        mock_container.is_registered.return_value = False

        checker = HealthChecker(mock_container)

        # Act
        result = await checker.check_my_service()

        # Assert
        assert result.status == "unhealthy"
        assert "not registered" in result.message.lower()

    @pytest.mark.asyncio
    async def test_check_service_connection_failed(self):
        """Test service health check when connection fails."""
        # Arrange
        mock_container = Mock()
        mock_service = Mock()
        mock_service.ping = AsyncMock(
            side_effect=ConnectionError("Connection refused")
        )

        mock_container.is_registered.return_value = True
        mock_container.resolve.return_value = mock_service

        checker = HealthChecker(mock_container)

        # Act
        result = await checker.check_my_service()

        # Assert
        assert result.status == "unhealthy"
        assert "failed" in result.message.lower()
        assert "Connection refused" in result.details["error"]
```

### Executar Testes

```bash
# Todos os testes de health check
pytest tests/unit/api/controllers/test_health_checker.py -v

# Teste específico
pytest tests/unit/api/controllers/test_health_checker.py::TestHealthChecker::test_check_service_healthy -v

# Com coverage
pytest tests/unit/api/controllers/test_health_checker.py --cov=app.api.controllers.health --cov-report=html
```

---

## 📚 Exemplos Completos

### Exemplo 1: Serviço Assíncrono (Database)

```python
async def check_postgresql(self) -> DependencyStatus:
    """Check PostgreSQL database health."""
    try:
        from app.services.database.postgresql_service import PostgreSQLService

        if not self.container.is_registered(PostgreSQLService):
            return DependencyStatus(
                status="unhealthy",
                message="PostgreSQL service not registered",
                details={"error": "Service not configured"}
            )

        db_service = self.container.resolve(PostgreSQLService)

        # Test connection with timeout
        try:
            async with asyncio.timeout(3.0):
                version = await db_service.get_version()
                pool_status = await db_service.get_pool_status()
        except asyncio.TimeoutError:
            return DependencyStatus(
                status="unhealthy",
                message="PostgreSQL connection timeout",
                details={"error": "Connection timeout after 3s"}
            )
        except Exception as conn_error:
            self.logger.error(f"PostgreSQL connection failed: {conn_error}")
            return DependencyStatus(
                status="unhealthy",
                message="Failed to connect to PostgreSQL",
                details={"error": str(conn_error)}
            )

        return DependencyStatus(
            status="healthy",
            message="PostgreSQL connected and operational",
            details={
                "version": version,
                "pool_size": pool_status["size"],
                "pool_available": pool_status["available"],
                "pool_used": pool_status["used"]
            }
        )

    except Exception as e:
        self.logger.error(f"PostgreSQL health check error: {e}")
        return DependencyStatus(
            status="unhealthy",
            message="PostgreSQL health check failed",
            details={"error": str(e)}
        )
```

### Exemplo 2: Serviço Síncrono (Configuração)

```python
def check_email_config(self, settings) -> DependencyStatus:
    """Check email service configuration."""
    try:
        has_host = bool(settings.smtp_host)
        has_port = bool(settings.smtp_port)
        has_credentials = bool(settings.smtp_username and settings.smtp_password)
        is_enabled = settings.email_enabled

        if not is_enabled:
            return DependencyStatus(
                status="degraded",
                message="Email service disabled",
                details={
                    "enabled": False,
                    "note": "Email notifications will not be sent"
                }
            )

        if has_host and has_port and has_credentials:
            return DependencyStatus(
                status="healthy",
                message="Email service configured",
                details={
                    "enabled": True,
                    "smtp_host": settings.smtp_host,
                    "smtp_port": settings.smtp_port,
                    "has_credentials": True
                }
            )
        else:
            return DependencyStatus(
                status="degraded",
                message="Email service partially configured",
                details={
                    "enabled": is_enabled,
                    "smtp_configured": has_host and has_port,
                    "credentials_configured": has_credentials,
                    "note": "Missing configuration - email service unavailable"
                }
            )

    except Exception as e:
        self.logger.error(f"Email config check error: {e}")
        return DependencyStatus(
            status="degraded",
            message="Email configuration check failed",
            details={"error": str(e)}
        )
```

### Exemplo 3: API Externa

```python
async def check_external_api(self) -> DependencyStatus:
    """Check external API availability."""
    try:
        from app.services.external.api_client import ExternalAPIClient

        if not self.container.is_registered(ExternalAPIClient):
            return DependencyStatus(
                status="unhealthy",
                message="External API client not registered",
                details={"error": "Service not configured"}
            )

        api_client = self.container.resolve(ExternalAPIClient)

        # Test API with timeout
        try:
            async with asyncio.timeout(5.0):
                response = await api_client.health_check()

                if response.status_code == 200:
                    return DependencyStatus(
                        status="healthy",
                        message="External API accessible",
                        details={
                            "response_time_ms": response.elapsed_ms,
                            "api_version": response.headers.get("X-API-Version"),
                            "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining")
                        }
                    )
                else:
                    return DependencyStatus(
                        status="degraded",
                        message=f"External API returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "error": response.text
                        }
                    )

        except asyncio.TimeoutError:
            return DependencyStatus(
                status="unhealthy",
                message="External API timeout",
                details={"error": "Request timeout after 5s"}
            )
        except Exception as api_error:
            self.logger.error(f"External API request failed: {api_error}")
            return DependencyStatus(
                status="unhealthy",
                message="Failed to reach external API",
                details={"error": str(api_error)}
            )

    except Exception as e:
        self.logger.error(f"External API health check error: {e}")
        return DependencyStatus(
            status="unhealthy",
            message="External API health check failed",
            details={"error": str(e)}
        )
```

---

## 📊 Checklist para Review

Ao adicionar ou modificar health checks, verifique:

- [ ] Método adicionado à classe `HealthChecker`
- [ ] Nome do método segue padrão `check_<service_name>()`
- [ ] Usa `async def` se faz I/O, `def` se apenas config
- [ ] Retorna sempre `DependencyStatus` - nunca lança exceções
- [ ] Tem try-except tratando todas as exceções
- [ ] Logging adequado (debug, info, error)
- [ ] Docstring completa com descrição, verificações e retorno
- [ ] Detalhes diagnósticos úteis em `details`
- [ ] Timeout configurado para operações de rede
- [ ] Não expõe informações sensíveis
- [ ] Adicionado ao método `check_all()`
- [ ] Classificado como crítico ou não-crítico
- [ ] Testes unitários criados
- [ ] Documentação atualizada

---

## 🔗 Referências

- **Arquivo**: `app/api/controllers/health.py`
- **Testes**: `tests/unit/api/controllers/test_health_checker.py`
- **Documentação API**: `docs/API.md`
- **Arquitetura**: `docs/ARCHITECTURE.md`

---

**Última atualização**: 27 de outubro de 2025  
**Versão**: 2.0.0  
**Autor**: SmartQuest Team
