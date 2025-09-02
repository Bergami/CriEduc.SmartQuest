# 🎯 Diagramas Visuais: Pydantic vs Dict nos Fluxos

## 🔄 Diagrama 1: Fluxo Completo do Sistema

```mermaid
graph TD
    subgraph "📁 INPUT"
        A[📄 PDF File + Email]
    end
    
    subgraph "🔀 ENDPOINTS"
        B1[🆕 /analyze_document<br/>PYDANTIC]
        B2[📚 /analyze_document_mock<br/>MIXED]
        B3[📊 /analyze_document_with_figures<br/>DICT]
    end
    
    subgraph "⚙️ SERVICES LAYER"
        C1[AnalyzeService<br/>.process_document_with_models<br/>→ Pydantic]
        C2[DocumentProcessingOrchestrator<br/>.process_from_saved_azure<br/>→ Dict]
        C3[AnalyzeService<br/>.process_document<br/>→ Dict]
    end
    
    subgraph "🧱 MODELS/DATA"
        D1[📦 InternalDocumentResponse<br/>BaseModel<br/>PYDANTIC ✅]
        D2[📊 Dict[str, Any]<br/>LEGACY ⚠️]
        D3[📊 Dict[str, Any]<br/>LEGACY ❌]
    end
    
    subgraph "🔄 ADAPTERS"
        E1[DocumentResponseAdapter<br/>Pydantic → Dict]
        E2[No Adapter<br/>Dict Pass-through]
        E3[No Adapter<br/>Dict Pass-through]
    end
    
    subgraph "📤 OUTPUT"
        F1[✅ API Response<br/>Dict[str, Any]]
        F2[⚠️ API Response<br/>Dict[str, Any]]
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
    
    classDef pydantic fill:#90EE90,stroke:#333,stroke-width:2px
    classDef mixed fill:#FFE4B5,stroke:#333,stroke-width:2px
    classDef dict fill:#FFB6C1,stroke:#333,stroke-width:2px
    
    class B1,C1,D1,E1,F1 pydantic
    class B2,C2,D2,E2,F2 mixed
    class B3,C3,D3,E3,F3 dict
```

## 🔄 Diagrama 2: Conversões de Dados no Endpoint Principal

```mermaid
sequenceDiagram
    participant Client
    participant Controller as /analyze_document
    participant Service as AnalyzeService
    participant Parser as HeaderParser
    participant Model as InternalDocumentMetadata
    participant Response as InternalDocumentResponse
    participant Adapter as DocumentResponseAdapter
    
    Note over Client,Adapter: 🆕 FLUXO PYDANTIC COMPLETO
    
    Client->>Controller: POST PDF + email
    
    Controller->>Service: process_document_with_models()
    
    Service->>Parser: parse(text) → Dict
    Note over Parser: ❌ LEGADO: Retorna Dict
    
    Service->>Model: from_legacy_header(dict_data)
    Note over Model: ✅ CONVERSÃO: Dict → Pydantic
    Model-->>Service: InternalDocumentMetadata (Pydantic)
    
    Service->>Response: InternalDocumentResponse(metadata=...)
    Note over Response: ✅ PYDANTIC: Modelo tipado completo
    Response-->>Service: InternalDocumentResponse (Pydantic)
    
    Service-->>Controller: InternalDocumentResponse (Pydantic)
    
    Controller->>Adapter: to_api_response(internal_response)
    Note over Adapter: 🔄 CONVERSÃO: Pydantic → Dict
    Adapter-->>Controller: Dict[str, Any]
    
    Controller-->>Client: API Response (Dict)
    
    Note over Client,Adapter: PROBLEMA: Conversão desnecessária<br/>Pydantic → Dict → JSON
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

## 🔄 Diagrama 6: Roadmap de Migração

```mermaid
gantt
    title Migração Pydantic - Timeline
    dateFormat YYYY-MM-DD
    section Fase 1: Endpoints
    Migrar /analyze_document_with_figures    :done, a1, 2025-09-02, 2025-09-15
    Migrar /analyze_document_mock           :active, a2, 2025-09-10, 2025-09-25
    section Fase 2: Services
    HeaderParser → Pydantic                :a3, 2025-09-20, 2025-10-05
    QuestionParser → Pydantic              :a4, 2025-09-25, 2025-10-10
    ContextBuilder → Pydantic              :a5, 2025-10-01, 2025-10-15
    section Fase 3: Optimization
    Eliminar conversões desnecessárias      :a6, 2025-10-10, 2025-10-25
    API Response → Pydantic direto          :a7, 2025-10-20, 2025-11-05
    section Fase 4: Testing
    Testes completos                       :a8, 2025-10-25, 2025-11-10
    Performance benchmarks                  :a9, 2025-11-01, 2025-11-15
```

## 📊 Estatísticas de Migração

### Distribuição Atual de Formatos
```mermaid
pie title Uso de Formatos no Sistema
    "Pydantic (Migrado)" : 45
    "Dict Legacy" : 35
    "Misto (Transição)" : 20
```

### Prioridades de Migração
```mermaid
pie title Prioridade de Migração
    "Alta (Endpoints)" : 40
    "Média (Services)" : 35
    "Baixa (Helpers)" : 25
```

### Complexidade de Migração
```mermaid
pie title Complexidade por Componente
    "Fácil (Models)" : 30
    "Média (Services)" : 45
    "Difícil (Parsers)" : 25
```
