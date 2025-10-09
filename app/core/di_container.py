"""
Dependency Injection Container com Auto-wiring

Container nativo para injeção de dependência baseado em type hints.
Suporta singleton/transient lifecycle e detecção de dependências circulares.
"""
import logging
import inspect
from typing import Type, TypeVar, Dict, Any, Optional, Protocol, get_type_hints, Set
from enum import Enum


# Type variable para garantir type safety
T = TypeVar('T')

logger = logging.getLogger(__name__)


class ServiceLifetime(Enum):
    """
    🔄 ENUM: Define o ciclo de vida dos serviços
    
    SINGLETON: Uma única instância compartilhada
    - Criada uma vez na primeira resolução
    - Reutilizada em todas as resolução subsequentes
    - Ideal para serviços stateless ou caros de criar
    
    TRANSIENT: Nova instância a cada resolução
    - Criada sempre que solicitada
    - Sem compartilhamento entre usos
    - Ideal para serviços com estado ou lightweight
    """
    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceRegistration:
    """
    📋 CLASSE: Representa o registro de um serviço no container
    
    Contém todas as informações necessárias para resolver um serviço:
    - Tipo da interface (abstração)
    - Tipo da implementação (classe concreta)
    - Ciclo de vida (singleton ou transient)
    - Instância cached (se singleton)
    """
    
    def __init__(self, 
                 interface_type: Type,
                 implementation_type: Type,
                 lifetime: ServiceLifetime = ServiceLifetime.SINGLETON):
        self.interface_type = interface_type
        self.implementation_type = implementation_type
        self.lifetime = lifetime
        self.cached_instance: Optional[Any] = None
        
        logger.debug(f"📋 Service registered: {interface_type.__name__} -> {implementation_type.__name__} ({lifetime.value})")


class CircularDependencyError(Exception):
    """
    ⚠️ EXCEÇÃO: Detecta dependências circulares
    
    Exemplo de dependência circular:
    - ServiceA depende de ServiceB
    - ServiceB depende de ServiceA
    - Isso causaria loop infinito na resolução
    """
    pass


class ServiceNotRegisteredError(Exception):
    """
    ⚠️ EXCEÇÃO: Serviço não foi registrado no container
    
    Levantada quando tentamos resolver um tipo que não foi registrado
    """
    pass


class SmartQuestDIContainer:
    """
    🏭 DEPENDENCY INJECTION CONTAINER - Coração da Fase 4
    
    RESPONSABILIDADES:
    1. Registrar serviços (mapeamento Interface -> Implementação)
    2. Resolver dependências automaticamente (auto-wiring)
    3. Gerenciar ciclo de vida (singleton/transient)
    4. Detectar dependências circulares
    5. Criar instâncias com todas as dependências injetadas
    
    COMO FUNCIONA:
    1. Registro: container.register(Interface, Implementation)
    2. Resolução: container.resolve(Interface)
    3. Auto-wiring: inspeciona construtor e resolve cada parâmetro
    4. Instanciação: cria objeto com dependências já resolvidas
    
    EXEMPLO DE USO:
    ```python
    # Registro
    container.register(IEmailService, SMTPEmailService)
    container.register(ILogger, FileLogger)
    
    # Resolução automática
    service = container.resolve(IEmailService)
    # O container automaticamente:
    # 1. Vê que SMTPEmailService precisa de ILogger
    # 2. Resolve ILogger -> FileLogger
    # 3. Cria FileLogger()
    # 4. Cria SMTPEmailService(logger=FileLogger())
    # 5. Retorna SMTPEmailService totalmente configurado
    ```
    """
    
    def __init__(self):
        """
        Inicializa o container vazio.
        
        _services: Dicionário que mapeia Interface -> ServiceRegistration
        _resolution_stack: Stack para detectar dependências circulares
        """
        self._services: Dict[Type, ServiceRegistration] = {}
        self._resolution_stack: Set[Type] = set()  # Para detectar ciclos
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("🏭 SmartQuestDIContainer initialized")

    def register(self, 
                interface_type: Type[T], 
                implementation_type: Type[T],
                lifetime: ServiceLifetime = ServiceLifetime.SINGLETON) -> 'SmartQuestDIContainer':
        """
        📝 REGISTRA um serviço no container
        
        CONCEITO:
        - Cria um mapeamento entre Interface (abstração) e Implementation (concreto)
        - Define o ciclo de vida do serviço
        - Permite method chaining para múltiplos registros
        
        Args:
            interface_type: Tipo da interface/abstração (o que queremos)
            implementation_type: Tipo da implementação (o que vamos criar)
            lifetime: Ciclo de vida (singleton ou transient)
            
        Returns:
            Self para permitir method chaining
            
        Exemplo:
        ```python
        container.register(IEmailService, SMTPEmailService, ServiceLifetime.SINGLETON)
                 .register(ILogger, FileLogger, ServiceLifetime.TRANSIENT)
        ```
        """
        
        # Validação básica
        if not interface_type or not implementation_type:
            raise ValueError("Both interface_type and implementation_type must be provided")
        
        # Cria o registro do serviço
        registration = ServiceRegistration(
            interface_type=interface_type,
            implementation_type=implementation_type,
            lifetime=lifetime
        )
        
        # Armazena no dicionário de serviços
        self._services[interface_type] = registration
        
        self._logger.info(f"✅ Registered: {interface_type.__name__} -> {implementation_type.__name__} ({lifetime.value})")
        
        # Retorna self para method chaining
        return self

    def resolve(self, service_type: Type[T]) -> T:
        """
        🔧 RESOLVE um serviço e todas suas dependências automaticamente
        
        ALGORITMO DE AUTO-WIRING:
        1. Verifica se o serviço está registrado
        2. Detecta dependências circulares
        3. Se é singleton e já existe, retorna instância cached
        4. Inspeciona o construtor da implementação
        5. Para cada parâmetro do construtor:
           a. Identifica o tipo via type hint
           b. Resolve recursivamente esse tipo
        6. Instancia a classe com todas as dependências
        7. Se singleton, armazena para reuso
        8. Retorna instância completamente configurada
        
        Args:
            service_type: Tipo do serviço a ser resolvido
            
        Returns:
            Instância do serviço com todas as dependências injetadas
            
        Raises:
            ServiceNotRegisteredError: Se serviço não foi registrado
            CircularDependencyError: Se detectar dependência circular
        """
        
        self._logger.debug(f"🔧 Resolving: {service_type.__name__}")
        
        # 1. VERIFICAÇÃO: Serviço está registrado?
        if service_type not in self._services:
            # Se não está registrado, tenta usar o próprio tipo como implementação
            self._logger.warning(f"⚠️ Service {service_type.__name__} not registered, trying to use as implementation")
            return self._create_instance(service_type)
        
        registration = self._services[service_type]
        
        # 2. DETECÇÃO DE DEPENDÊNCIA CIRCULAR
        if service_type in self._resolution_stack:
            circular_path = " -> ".join([t.__name__ for t in self._resolution_stack]) + f" -> {service_type.__name__}"
            raise CircularDependencyError(f"Circular dependency detected: {circular_path}")
        
        # 3. SINGLETON: Se já existe instância, retorna
        if (registration.lifetime == ServiceLifetime.SINGLETON and 
            registration.cached_instance is not None):
            self._logger.debug(f"♻️ Returning cached singleton: {service_type.__name__}")
            return registration.cached_instance
        
        # 4. CRIAR NOVA INSTÂNCIA
        # Adiciona ao stack de resolução para detectar ciclos
        self._resolution_stack.add(service_type)
        
        try:
            # Cria instância com auto-wiring
            instance = self._create_instance(registration.implementation_type)
            
            # Se singleton, armazena para reuso
            if registration.lifetime == ServiceLifetime.SINGLETON:
                registration.cached_instance = instance
                self._logger.debug(f"💾 Cached singleton: {service_type.__name__}")
            
            self._logger.info(f"✅ Resolved: {service_type.__name__}")
            return instance
            
        finally:
            # Remove do stack de resolução
            self._resolution_stack.discard(service_type)

    def _create_instance(self, implementation_type: Type[T]) -> T:
        """
        🏗️ CRIA uma instância com AUTO-WIRING de dependências
        
        PROCESSO DE AUTO-WIRING:
        1. Inspeciona o construtor (__init__) da classe
        2. Para cada parâmetro (exceto 'self'):
           a. Obtém o type hint do parâmetro
           b. Resolve recursivamente esse tipo
           c. Armazena para injeção
        3. Instancia a classe passando todas as dependências
        
        REFLECTION EM PYTHON:
        - inspect.signature(): Obtém assinatura do método
        - parameter.annotation: Type hint do parâmetro
        - Recursão: resolve() chama _create_instance() que chama resolve()
        
        Args:
            implementation_type: Classe a ser instanciada
            
        Returns:
            Instância com todas as dependências injetadas
        """
        
        self._logger.debug(f"🏗️ Creating instance: {implementation_type.__name__}")
        
        # INSPEÇÃO DO CONSTRUTOR
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)
        
        # RESOLUÇÃO DAS DEPENDÊNCIAS
        # Dicionário para armazenar parâmetros resolvidos
        resolved_dependencies = {}
        
        for param_name, parameter in signature.parameters.items():
            # Pula 'self' pois não é uma dependência
            if param_name == 'self':
                continue
            
            # OBTÉM O TYPE HINT
            dependency_type = parameter.annotation
            
            # Verifica se tem type hint válido
            if dependency_type == inspect.Parameter.empty:
                self._logger.warning(f"⚠️ Parameter '{param_name}' has no type hint, skipping auto-wiring")
                continue
            
            self._logger.debug(f"  🔗 Resolving dependency: {param_name} -> {dependency_type.__name__}")
            
            # RECURSÃO: Resolve a dependência
            resolved_dependency = self.resolve(dependency_type)
            resolved_dependencies[param_name] = resolved_dependency
        
        # INSTANCIAÇÃO COM DEPENDÊNCIAS
        self._logger.debug(f"  🎯 Instantiating {implementation_type.__name__} with {len(resolved_dependencies)} dependencies")
        
        try:
            # Cria instância passando todas as dependências resolvidas
            instance = implementation_type(**resolved_dependencies)
            self._logger.debug(f"✅ Created: {implementation_type.__name__}")
            return instance
            
        except Exception as e:
            self._logger.error(f"❌ Failed to create {implementation_type.__name__}: {str(e)}")
            raise

    def is_registered(self, service_type: Type) -> bool:
        """
        ❓ VERIFICA se um serviço está registrado
        
        Args:
            service_type: Tipo a verificar
            
        Returns:
            True se registrado, False caso contrário
        """
        return service_type in self._services

    def get_registrations(self) -> Dict[Type, ServiceRegistration]:
        """
        📋 OBTÉM todos os registros do container
        
        Útil para debugging e inspeção
        
        Returns:
            Dicionário com todos os registros
        """
        return self._services.copy()

    def clear(self) -> None:
        """
        🧹 LIMPA o container
        
        Remove todos os registros e instâncias cached
        Útil para testes ou reinicialização
        """
        self._services.clear()
        self._resolution_stack.clear()
        self._logger.info("🧹 Container cleared")


# ==================================================================================
# 🎯 INSTÂNCIA GLOBAL DO CONTAINER
# ==================================================================================
# Singleton pattern para o container - uma única instância global
# Isso permite que todas as partes da aplicação usem o mesmo container
container = SmartQuestDIContainer()

def get_container() -> SmartQuestDIContainer:
    """
    🌍 OBTÉM a instância global do container
    
    Pattern comum em DI containers - facilita acesso global
    
    Returns:
        Instância global do container
    """
    return container

# ==================================================================================
# 📝 EXEMPLO DE USO COMENTADO
# ==================================================================================
"""
EXEMPLO PRÁTICO DE AUTO-WIRING:

1. DEFINIÇÃO DE INTERFACES:
```python
class IEmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> bool: ...

class ILogger(Protocol):
    def log(self, message: str) -> None: ...
```

2. IMPLEMENTAÇÕES:
```python
class FileLogger:
    def log(self, message: str) -> None:
        print(f"LOG: {message}")

class EmailService:
    def __init__(self, logger: ILogger):  # ← DEPENDÊNCIA INJETADA
        self.logger = logger
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        self.logger.log(f"Sending email to {to}")
        return True
```

3. REGISTRO:
```python
container.register(ILogger, FileLogger)
container.register(IEmailService, EmailService)
```

4. RESOLUÇÃO AUTOMÁTICA:
```python
email_service = container.resolve(IEmailService)
# O container automaticamente:
# 1. Vê que EmailService precisa de ILogger
# 2. Resolve ILogger -> FileLogger
# 3. Cria FileLogger()
# 4. Cria EmailService(logger=FileLogger())
# 5. Retorna EmailService totalmente configurado
```

BENEFÍCIOS:
- Zero acoplamento entre classes
- Fácil troca de implementações
- Testes simplificados (mock dependencies)
- Configuração centralizada
- Reutilização automática (singletons)
"""
