# Arquitetura do Sistema SmartQuest

## 🏗️ Visão Geral

SmartQuest é um sistema de análise de documentos PDF com arquitetura moderna baseada em **Clean Architecture** e **SOLID Principles**.

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Controllers  │  REST Endpoints  │  Auto Docs      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  AnalyzeService  │  DI Container  │  Error Handling        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  DocumentAnalysisOrchestrator  │  Interfaces  │  Models    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Azure Services  │  File I/O  │  External APIs            │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 Dependency Injection Container

### **Conceito**

Sistema nativo de injeção de dependência baseado em type hints que resolve automaticamente toda a árvore de dependências.

### **Características**

- **Auto-wiring** via Python reflection
- **Interface-based** registration
- **Singleton/Transient** lifecycle management
- **Circular dependency** detection
- **Zero external libraries**

### **Exemplo de Uso**

```python
# Registro
container.register(IAnalyzeService, AnalyzeService, ServiceLifetime.SINGLETON)

# Resolução automática
service = container.resolve(IAnalyzeService)  # Todas as dependências resolvidas
```

## 🎯 Componentes Principais

### **1. AnalyzeService**

- **Responsabilidade:** Validação de entrada e delegação
- **Padrão:** Service Layer
- **Dependências:** IDocumentAnalysisOrchestrator (via DI)

### **2. DocumentAnalysisOrchestrator**

- **Responsabilidade:** Orquestração do pipeline de análise
- **Padrão:** Orchestrator Pattern
- **Pipeline:** 7 fases especializadas

### **3. Specialized Services**

- **ImageCategorizationService:** Categorização header/content
- **ImageExtractionOrchestrator:** Extração de imagens
- **RefactoredContextBlockBuilder:** Construção de contextos
- **AzureFigureProcessor:** Processamento de figuras

## 🔄 Pipeline de Processamento

```
[PDF Upload]
    │
    ▼
[1. Context Preparation] ─── Azure Document Intelligence
    │
    ▼
[2. Image Analysis] ─────── Image Extraction + Categorization
    │
    ▼
[3. Header Parsing] ────── Metadata Extraction
    │
    ▼
[4. Question Extraction] ── Paragraph Processing
    │
    ▼
[5. Context Building] ──── Enhanced Context Blocks
    │
    ▼
[6. Figure Processing] ─── Question-Figure Association
    │
    ▼
[7. Response Assembly] ─── Final Document Response
```

## 🏛️ SOLID Principles Aplicados

### **Single Responsibility Principle (SRP)**

- **AnalyzeService:** Apenas validação e delegação
- **DocumentAnalysisOrchestrator:** Apenas orquestração
- **Cada service:** Uma responsabilidade específica

### **Open/Closed Principle (OCP)**

- Pipeline extensível via novos orquestradores
- Implementações substituíveis via interfaces
- Novos parsers plugáveis

### **Liskov Substitution Principle (LSP)**

- Interfaces garantem substituibilidade
- Implementações intercambiáveis
- Contratos bem definidos

### **Interface Segregation Principle (ISP)**

- Interfaces específicas por responsabilidade
- IImageCategorizer, IImageExtractor, etc.
- Clientes dependem apenas do que usam

### **Dependency Inversion Principle (DIP)**

- Dependências via abstrações (interfaces)
- Alto nível não depende de baixo nível
- DI Container gerencia inversão

## 📦 Estrutura de Modelos

### **Internal Models (Domain)**

```python
InternalDocumentResponse    # Resposta completa
InternalQuestion           # Questão com alternativas
InternalContextBlock       # Bloco de contexto
InternalImageData         # Dados de imagem
InternalDocumentMetadata  # Metadados do documento
```

### **API Models (Presentation)**

```python
DocumentResponse          # Response para API
QuestionModel            # Questão para frontend
ContextBlockModel        # Context block para API
```

## 🔧 Configuração e Ambientes

### **Variáveis de Ambiente**

- **Azure Configuration:** Endpoints, keys, models
- **Application Settings:** Debug, timeouts, features
- **Development Tools:** Mock services, logging levels

### **Ambientes Suportados**

- **Development:** Mock services ativados
- **Staging:** Azure real + debug logs
- **Production:** Full Azure + optimized logging

## 🚦 Error Handling

### **Exception Hierarchy**

```python
DocumentProcessingError          # Base exception
├── ValidationError             # Input validation
├── AzureServiceError          # Azure failures
├── ParsingError               # Text parsing issues
└── ConfigurationError         # Setup problems
```

### **Error Recovery**

- Graceful degradation para serviços externos
- Fallback mechanisms em parsers
- Retry logic para calls Azure
- Detailed logging para debugging

## 📈 Performance e Escalabilidade

### **Otimizações**

- **Singleton services** via DI Container
- **Lazy loading** de dependências pesadas
- **Caching** de responses Azure (futuro)
- **Async processing** em I/O operations

### **Escalabilidade**

- **Stateless services** para horizontal scaling
- **Resource pooling** para conexões externas
- **Circuit breaker** para serviços instáveis (futuro)

## 🔍 Observabilidade

### **Logging**

- **Structured logging** com contexto
- **Level-based** (DEBUG, INFO, WARNING, ERROR)
- **Performance metrics** em operações críticas

### **Monitoring**

- Health checks em `/health/`
- Dependency status validation
- Service availability tracking

---

**Esta arquitetura garante:**

- ✅ **Manutenibilidade** via separação clara
- ✅ **Testabilidade** via DI e interfaces
- ✅ **Escalabilidade** via design stateless
- ✅ **Flexibilidade** via plugin architecture
