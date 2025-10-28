"""
Dependency Injection Container with Auto-wiring.

Native DI container based on type hints with singleton/transient lifecycle
and circular dependency detection.
"""
import logging
import inspect
from typing import Type, TypeVar, Dict, Any, Optional, Protocol, get_type_hints, Set
from enum import Enum

T = TypeVar('T')
logger = logging.getLogger(__name__)


class ServiceLifetime(Enum):
    """Service lifecycle: SINGLETON (shared instance) or TRANSIENT (new instance each time)."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceRegistration:
    """Represents a service registration with interface, implementation, lifetime, and cached instance."""
    
    def __init__(self, 
                 interface_type: Type,
                 implementation_type: Type,
                 lifetime: ServiceLifetime = ServiceLifetime.SINGLETON):
        self.interface_type = interface_type
        self.implementation_type = implementation_type
        self.lifetime = lifetime
        self.cached_instance: Optional[Any] = None
        logger.debug(f"Service registered: {interface_type.__name__} -> {implementation_type.__name__} ({lifetime.value})")


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected during resolution."""
    pass


class ServiceNotRegisteredError(Exception):
    """Raised when attempting to resolve an unregistered service."""
    pass


class SmartQuestDIContainer:
    """
    Dependency Injection Container with automatic dependency resolution.
    
    Responsibilities:
    - Register services (Interface -> Implementation mapping)
    - Resolve dependencies automatically (auto-wiring via type hints)
    - Manage lifecycle (singleton/transient)
    - Detect circular dependencies
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceRegistration] = {}
        self._resolution_stack: Set[Type] = set()
        self._logger = logging.getLogger(__name__)
        self._logger.info("SmartQuestDIContainer initialized")

    def register(self, 
                interface_type: Type[T], 
                implementation_type: Type[T],
                lifetime: ServiceLifetime = ServiceLifetime.SINGLETON) -> 'SmartQuestDIContainer':
        """Register a service mapping with specified lifecycle."""
        if not interface_type or not implementation_type:
            raise ValueError("Both interface_type and implementation_type must be provided")
        
        registration = ServiceRegistration(
            interface_type=interface_type,
            implementation_type=implementation_type,
            lifetime=lifetime
        )
        
        self._services[interface_type] = registration
        self._logger.info(f"Registered: {interface_type.__name__} -> {implementation_type.__name__} ({lifetime.value})")
        
        return self

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service and all its dependencies automatically.
        
        Auto-wiring algorithm:
        1. Check if service is registered
        2. Detect circular dependencies
        3. Return cached instance if singleton exists
        4. Inspect constructor for dependencies
        5. Recursively resolve each dependency
        6. Instantiate class with resolved dependencies
        7. Cache if singleton
        """
        self._logger.debug(f"Resolving: {service_type.__name__}")
        
        if service_type not in self._services:
            self._logger.warning(f"Service {service_type.__name__} not registered, trying to use as implementation")
            return self._create_instance(service_type)
        
        registration = self._services[service_type]
        
        if service_type in self._resolution_stack:
            circular_path = " -> ".join([t.__name__ for t in self._resolution_stack]) + f" -> {service_type.__name__}"
            raise CircularDependencyError(f"Circular dependency detected: {circular_path}")
        
        if (registration.lifetime == ServiceLifetime.SINGLETON and 
            registration.cached_instance is not None):
            self._logger.debug(f"Returning cached singleton: {service_type.__name__}")
            return registration.cached_instance
        
        self._resolution_stack.add(service_type)
        
        try:
            instance = self._create_instance(registration.implementation_type)
            
            if registration.lifetime == ServiceLifetime.SINGLETON:
                registration.cached_instance = instance
                self._logger.debug(f"Cached singleton: {service_type.__name__}")
            
            self._logger.info(f"Resolved: {service_type.__name__}")
            return instance
            
        finally:
            self._resolution_stack.discard(service_type)

    def _create_instance(self, implementation_type: Type[T]) -> T:
        """Create instance with auto-wired dependencies by inspecting constructor type hints."""
        self._logger.debug(f"Creating instance: {implementation_type.__name__}")
        
        constructor = implementation_type.__init__
        signature = inspect.signature(constructor)
        
        resolved_dependencies = {}
        
        for param_name, parameter in signature.parameters.items():
            if param_name == 'self':
                continue
            
            dependency_type = parameter.annotation
            
            if dependency_type == inspect.Parameter.empty:
                self._logger.warning(f"Parameter '{param_name}' has no type hint, skipping auto-wiring")
                continue
            
            self._logger.debug(f"Resolving dependency: {param_name} -> {dependency_type.__name__}")
            resolved_dependency = self.resolve(dependency_type)
            resolved_dependencies[param_name] = resolved_dependency
        
        self._logger.debug(f"Instantiating {implementation_type.__name__} with {len(resolved_dependencies)} dependencies")
        
        try:
            instance = implementation_type(**resolved_dependencies)
            self._logger.debug(f"Created: {implementation_type.__name__}")
            return instance
        except Exception as e:
            self._logger.error(f"Failed to create {implementation_type.__name__}: {str(e)}")
            raise

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered in the container."""
        return service_type in self._services

    def get_registrations(self) -> Dict[Type, ServiceRegistration]:
        """Get all service registrations for debugging and inspection."""
        return self._services.copy()

    def clear(self) -> None:
        """Clear all registrations and cached instances."""
        self._services.clear()
        self._resolution_stack.clear()
        self._logger.info("Container cleared")


container = SmartQuestDIContainer()


def get_container() -> SmartQuestDIContainer:
    """Get the global container instance."""
    return container
