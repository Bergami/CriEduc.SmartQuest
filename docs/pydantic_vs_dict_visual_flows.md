# 🎯 Diagramas Visuais: Pydantic vs Dict nos Fluxos

## 🔄 Diagrama 1: Fluxo REAL do Sistema (CORRIGIDO)

```mermaid
graph TD
    subgraph "📁 INPUT"
        A[📄 PDF File + Email]
    end
    
    subgraph "🔀 ENDPOINTS"
        B1[⚠️ /analyze_document<br/>HÍBRIDO]
        B2[📚 /analyze_document_mock<br/>DICT]
        B3[📊 /analyze_document_with_figures<br/>DICT]
    end
    
    subgraph "⚙️ SERVICES LAYER"
        C1[AnalyzeService<br/>.process_document_with_models<br/>→ Híbrido Pydantic/Dict]
        C2[DocumentProcessingOrchestrator<br/>.process_from_saved_azure<br/>→ Dict]
        C3[AnalyzeService<br/>.process_document<br/>→ Dict]
    end
    
    subgraph "🧱 MODELS/DATA"
        D1[⚠️ InternalDocumentResponse<br/>BaseModel + Dict fields<br/>HÍBRIDO ⚠️]
        D2[📊 Dict[str, Any]<br/>LEGACY ❌]
        D3[📊 Dict[str, Any]<br/>LEGACY ❌]
    end
    
    subgraph "🔄 ADAPTERS"
        E1[DocumentResponseAdapter<br/>Híbrido → Dict<br/>❌ REGRESSIVO]
        E2[No Adapter<br/>Dict Pass-through]
        E3[No Adapter<br/>Dict Pass-through]
    end
    
    subgraph "📤 OUTPUT"
        F1[❌ API Response<br/>Dict[str, Any]]
        F2[❌ API Response<br/>Dict[str, Any]]
        F3[❌ API Response<br/>Dict[str, Any]]
    end
    
    A --> B1
    A --> B2
    A --> B3
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    D1 --> E1
    D2 --> E2
    D3 --> E3
    
    E1 --> F1
    E2 --> F2
    E3 --> F3
    
    classDef hybrid fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef dict fill:#FFB6C1,stroke:#333,stroke-width:2px
    classDef regressive fill:#FF6347,stroke:#333,stroke-width:2px
    
    class B1,C1,D1,E1,F1 hybrid
    class B2,C2,D2,E2,F2,B3,C3,D3,E3,F3 dict
    class E1 regressive
```

## 🔄 Diagrama 2: Conversões PROBLEMÁTICAS no Endpoint "Migrado"

```mermaid
sequenceDiagram
    participant Client
    participant Controller as /analyze_document
    participant Service as AnalyzeService
    participant HeaderParser as HeaderParser
    participant QuestionParser as QuestionParser
    participant Model as InternalDocumentMetadata
    participant Response as InternalDocumentResponse
    participant Adapter as DocumentResponseAdapter
    
    Note over Client,Adapter: ⚠️ FLUXO HÍBRIDO PROBLEMÁTICO
    
    Client->>Controller: POST PDF + email
    
    Controller->>Service: process_document_with_models()
    
    Service->>HeaderParser: parse(text)
    HeaderParser-->>Service: Dict[str, Any] ❌
    Note over HeaderParser: ❌ PROBLEMA 1: Parser retorna Dict
    
    Service->>Model: from_legacy_header(dict_data)
    Note over Model: 🔄 CONVERSÃO FORÇADA: Dict → Pydantic
    Model-->>Service: InternalDocumentMetadata (Pydantic)
    
    Service->>QuestionParser: extract(text, images)
    QuestionParser-->>Service: Dict[str, Any] ❌
    Note over QuestionParser: ❌ PROBLEMA 2: Parser retorna Dict
    
    Service->>Response: InternalDocumentResponse(metadata=pydantic, questions=dict, contexts=dict)
    Note over Response: ⚠️ PROBLEMA 3: Modelo híbrido<br/>Metadados=Pydantic, Conteúdo=Dict
    Response-->>Service: InternalDocumentResponse (Híbrido)
    
    Service-->>Controller: InternalDocumentResponse (Híbrido)
    
    Controller->>Adapter: to_api_response(internal_response)
    Note over Adapter: ❌ PROBLEMA 4: Conversão regressiva<br/>Pydantic → Dict
    Adapter-->>Controller: Dict[str, Any]
    
    Controller-->>Client: API Response (Dict)
    
    Note over Client,Adapter: RESULTADO: str → Dict → Pydantic → Híbrido → Dict → JSON<br/>❌ 4 CONVERSÕES DESNECESSÁRIAS
```

## 🔄 Diagrama 3: Comparação de Complexidade

```mermaid
graph LR
    subgraph "❌ ENDPOINT DICT LEGACY"
        A1[PDF] --> A2[Service Dict] --> A3[Dict Processing] --> A4[Dict Response]
        A4 --> A5[JSON Output]
    end
    
    subgraph "✅ ENDPOINT PYDANTIC MODERNO"
        B1[PDF] --> B2[Service Pydantic] --> B3[Pydantic Processing] --> B4[Pydantic Response]
        B4 --> B5[Adapter] --> B6[Dict Response] --> B7[JSON Output]
    end
    
    subgraph "🎯 ENDPOINT PYDANTIC IDEAL"
        C1[PDF] --> C2[Service Pydantic] --> C3[Pydantic Processing] --> C4[Pydantic Response]
        C4 --> C5[JSON Output]
    end
    
    classDef legacy fill:#FFB6C1,stroke:#333,stroke-width:2px
    classDef current fill:#90EE90,stroke:#333,stroke-width:2px
    classDef ideal fill:#87CEEB,stroke:#333,stroke-width:2px
    
    class A1,A2,A3,A4,A5 legacy
    class B1,B2,B3,B4,B5,B6,B7 current
    class C1,C2,C3,C4,C5 ideal
```

## 🔄 Diagrama 4: Mapa de Modelos no Sistema

```mermaid
graph TB
    subgraph "📁 app/models/internal/ (PYDANTIC ✅)"
        I1[InternalDocumentResponse<br/>BaseModel]
        I2[InternalDocumentMetadata<br/>BaseModel]
        I3[InternalImageData<br/>BaseModel]
        I4[InternalQuestion<br/>BaseModel]
        I5[InternalContextBlock<br/>BaseModel]
    end
    
    subgraph "📁 app/dtos/ (PYDANTIC ✅)"
        D1[DocumentResponseDTO<br/>BaseModel]
        D2[QuestionListDTO<br/>BaseModel]
        D3[ContextListDTO<br/>BaseModel]
        D4[ImageListDTO<br/>BaseModel]
    end
    
    subgraph "📁 app/services/ (MIXED ⚠️)"
        S1[AnalyzeService<br/>Pydantic + Dict]
        S2[HeaderParser<br/>Dict Only]
        S3[QuestionParser<br/>Dict Only]
        S4[ContextBuilder<br/>Dict Only]
    end
    
    subgraph "📁 app/adapters/ (CONVERTERS 🔄)"
        A1[DocumentResponseAdapter<br/>Pydantic → Dict]
    end
    
    I1 --> I2
    I1 --> I3
    I1 --> I4
    I1 --> I5
    
    D1 --> D2
    D1 --> D3
    D1 --> D4
    
    S1 --> I1
    S2 --> I2
    S3 --> I4
    S4 --> I5
    
    I1 --> A1
    A1 --> D1
    
    classDef pydantic fill:#90EE90,stroke:#333,stroke-width:2px
    classDef mixed fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef converter fill:#DDA0DD,stroke:#333,stroke-width:2px
    
    class I1,I2,I3,I4,I5,D1,D2,D3,D4 pydantic
    class S1,S2,S3,S4 mixed
    class A1 converter
```

## 🔄 Diagrama 5: Problemas de Performance nas Conversões

```mermaid
sequenceDiagram
    participant PDF
    participant Azure as Azure DI
    participant Parser as HeaderParser
    participant Pydantic as InternalDocumentMetadata
    participant Response as InternalDocumentResponse
    participant Adapter as DocumentResponseAdapter
    participant API as API Response
    
    Note over PDF,API: 🐌 PROBLEMA: Muitas Conversões
    
    PDF->>Azure: Análise do documento
    Azure-->>Parser: Dados raw (Dict)
    
    Note over Azure,Parser: ❌ FORMAT: Dict[str, Any]
    
    Parser->>Parser: Processar header
    Parser-->>Pydantic: Dict legado
    
    Note over Parser,Pydantic: 🔄 CONVERSÃO 1: Dict → Pydantic
    
    Pydantic->>Pydantic: Validação e tipagem
    Pydantic-->>Response: InternalDocumentMetadata
    
    Response->>Response: Montar response completo
    Response-->>Adapter: InternalDocumentResponse
    
    Note over Response,Adapter: ✅ FORMAT: Pydantic (tipado)
    
    Adapter->>Adapter: to_api_response()
    
    Note over Adapter: 🔄 CONVERSÃO 2: Pydantic → Dict
    
    Adapter-->>API: Dict[str, Any]
    
    Note over Adapter,API: ❌ FORMAT: Dict[str, Any]
    
    Note over PDF,API: SOLUÇÃO: Eliminar conversão 2<br/>Usar Pydantic direto na API
```

## 🔄 Diagrama 6: Roadmap de Migração CORRIGIDO

```mermaid
gantt
    title Migração Pydantic - Plano de Recuperação
    dateFormat YYYY-MM-DD
    section Fase 1: Correção Crítica
    Corrigir InternalDocumentResponse fields   :crit, a1, 2025-09-02, 2025-09-09
    Criar HeaderParser.parse_direct()         :crit, a2, 2025-09-05, 2025-09-12
    Criar QuestionParser.extract_typed()      :crit, a3, 2025-09-08, 2025-09-16
    section Fase 2: Otimização
    Eliminar DocumentResponseAdapter          :active, b1, 2025-09-15, 2025-09-22
    APIs response_model direto                :b2, 2025-09-18, 2025-09-25
    Migrar endpoint with_figures              :b3, 2025-09-20, 2025-09-30
    section Fase 3: Validação
    Testes end-to-end                        :c1, 2025-09-25, 2025-10-02
    Performance benchmarks                   :c2, 2025-09-28, 2025-10-05
    Documentação final                       :c3, 2025-10-01, 2025-10-08
    section Milestone
    ROI Break-even Point                     :milestone, m1, 2025-10-08, 0d
```

## 📊 Estatísticas de Migração

### Distribuição REAL de Formatos
```mermaid
pie title Estado REAL da Migração
    "Dict Legacy" : 55
    "Híbrido (Problemático)" : 25
    "Pydantic (Completo)" : 20
```

### Prioridades CORRIGIDAS de Migração
```mermaid
pie title Prioridade de Correção
    "Crítica (Corrigir Híbridos)" : 50
    "Alta (Migrar Endpoints)" : 30
    "Média (Otimizações)" : 20
```

### Complexidade REAL de Migração
```mermaid
pie title Complexidade por Problema
    "Crítica (Modelos Híbridos)" : 40
    "Alta (Parsers Dict)" : 35
    "Média (Adapters)" : 25
```
