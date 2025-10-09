# Dependency Injection Container

## 🔌 Visão Geral

O SmartQuest utiliza um **Dependency Injection Container** nativo desenvolvido especificamente para o projeto, baseado em **type hints** e **reflection** do Python.

## 🎯 Características

### **Auto-wiring Automático**

- Resolve dependências automaticamente via type hints
- Analisa construtores usando `inspect.signature()`
- Cria toda a árvore de dependências recursivamente

### **Interface-based Registration**

- Registro via interfaces abstratas (`Protocol`)
- Mapeamento Interface → Implementação
- Zero acoplamento entre classes

### **Lifecycle Management**

- **Singleton:** Uma instância reutilizada
- **Transient:** Nova instância a cada resolução
- Cache automático para singletons

### **Safety Features**

- Detecção de dependências circulares
- Validação de registros na inicialização
- Error handling detalhado

## 🛠️ Como Usar

### **1. Definir Interface**

```python
from typing import Protocol
from app.models.internal import InternalDocumentResponse

class IAnalyzeService(Protocol):
    async def process_document_with_models(
        self,
        extracted_data: Dict[str, Any],
        email: str,
        filename: str,
        file: UploadFile
    ) -> InternalDocumentResponse:
        ...
```

### **2. Implementar Service**

```python
class AnalyzeService:
    def __init__(self, orchestrator: IDocumentAnalysisOrchestrator):
        self._orchestrator = orchestrator  # ← Auto-injetado pelo container

    async def process_document_with_models(self, ...):
        return await self._orchestrator.orchestrate_analysis(...)
```

### **3. Registrar no Container**

```python
from app.core.di_container import container, ServiceLifetime

# Registro
container.register(
    IAnalyzeService,           # Interface
    AnalyzeService,           # Implementação
    ServiceLifetime.SINGLETON  # Lifecycle
)
```

### **4. Resolver Dependência**

```python
# Resolução automática - todas as dependências são criadas
service = container.resolve(IAnalyzeService)

# O container automaticamente:
# 1. Analisa AnalyzeService.__init__
# 2. Vê que precisa de IDocumentAnalysisOrchestrator
# 3. Resolve IDocumentAnalysisOrchestrator recursivamente
# 4. Cria AnalyzeService com dependência injetada
```

## ⚙️ Configuração Atual

### **Interfaces Registradas**

```python
# Core Services
IAnalyzeService → AnalyzeService
IDocumentAnalysisOrchestrator → DocumentAnalysisOrchestrator

# Specialized Services
IImageCategorizer → ImageCategorizationService
IImageExtractor → ImageExtractionOrchestrator
IContextBuilder → RefactoredContextBlockBuilder
IFigureProcessor → AzureFigureProcessor
```

### **Árvore de Dependências**

```
AnalyzeService
└── DocumentAnalysisOrchestrator
    ├── ImageCategorizationService
    ├── ImageExtractionOrchestrator
    ├── RefactoredContextBlockBuilder
    └── AzureFigureProcessor
```

## 🏗️ Implementação Técnica

### **Container Core**

```python
class SmartQuestDIContainer:
    def __init__(self):
        self._services: Dict[Type, ServiceRegistration] = {}
        self._instances: Dict[Type, Any] = {}
        self._resolution_stack: Set[Type] = set()

    def register(self, interface: Type, implementation: Type, lifetime: ServiceLifetime):
        """Registra mapeamento Interface → Implementação"""

    def resolve(self, service_type: Type) -> Any:
        """Resolve serviço e todas suas dependências"""
```

### **Auto-wiring Process**

```python
def _create_instance(self, implementation_type: Type) -> Any:
    # 1. Obter signature do construtor
    signature = inspect.signature(implementation_type.__init__)

    # 2. Resolver cada parâmetro
    resolved_dependencies = {}
    for param_name, param in signature.parameters.items():
        if param_name != 'self' and param.annotation != inspect.Parameter.empty:
            # 3. Resolver dependência recursivamente
            dependency = self.resolve(param.annotation)
            resolved_dependencies[param_name] = dependency

    # 4. Criar instância com dependências
    return implementation_type(**resolved_dependencies)
```

## 🔍 Debugging e Troubleshooting

### **Logs de Resolução**

```python
# Ativar logs detalhados
logging.getLogger("app.core.di_container").setLevel(logging.DEBUG)

# Output:
# DEBUG: Resolving: IAnalyzeService
# DEBUG: Creating: AnalyzeService with 1 dependencies
# DEBUG: Resolved: IAnalyzeService → AnalyzeService instance
```

### **Validação de Configuração**

```python
from app.config.di_config import validate_configuration

# Valida se todas as interfaces estão registradas
try:
    validate_configuration()
    print("✅ Configuration OK")
except Exception as e:
    print(f"❌ Configuration Error: {e}")
```

### **Problemas Comuns**

**1. ServiceNotRegisteredError**

```python
# Erro: Interface não registrada
service = container.resolve(IUnregisteredService)

# Solução: Registrar no di_config.py
container.register(IUnregisteredService, UnregisteredService, ServiceLifetime.SINGLETON)
```

**2. CircularDependencyError**

```python
# Erro: A → B → A
class ServiceA:
    def __init__(self, service_b: IServiceB): ...

class ServiceB:
    def __init__(self, service_a: IServiceA): ...

# Solução: Refatorar arquitetura ou usar patterns como Mediator
```

**3. Missing Type Hints**

```python
# Erro: Container não consegue resolver
class BadService:
    def __init__(self, dependency):  # ← Sem type hint
        ...

# Solução: Adicionar type hints
class GoodService:
    def __init__(self, dependency: IDependency):  # ← Com type hint
        ...
```

## 🚀 Benefícios Alcançados

### **Redução de Acoplamento**

- **Antes:** Classes conheciam implementações concretas
- **Depois:** Classes dependem apenas de interfaces
- **Resultado:** 100% de redução no acoplamento direto

### **Melhoria na Testabilidade**

- **Antes:** Mocking manual de cada dependência
- **Depois:** Container resolve mocks automaticamente
- **Resultado:** Testes mais simples e rápidos

### **Flexibilidade de Configuração**

- **Antes:** Mudanças espalhadas por múltiplos arquivos
- **Depois:** Configuração centralizada em `di_config.py`
- **Resultado:** Mudanças em um único local

### **Facilidade de Manutenção**

- **Antes:** Dependências manuais em construtores
- **Depois:** Auto-wiring transparente
- **Resultado:** Menos código boilerplate

## 📈 Performance

### **Singleton Caching**

- Instâncias singleton criadas apenas uma vez
- Reutilização automática em todas as resoluções
- Redução de overhead de criação

### **Lazy Resolution**

- Dependências resolvidas apenas quando necessário
- Não há pré-carregamento de serviços não utilizados
- Startup time otimizado

---

**O DI Container é o coração da arquitetura moderna do SmartQuest, permitindo:**

- ✅ **Zero coupling** entre componentes
- ✅ **Testabilidade** máxima via interfaces
- ✅ **Flexibilidade** de configuração
- ✅ **Manutenibilidade** simplificada
