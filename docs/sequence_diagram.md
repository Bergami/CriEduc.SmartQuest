# Diagramas de Sequência - Endpoints de Análise

## 1. Endpoint `/analyze_document` - Fluxo Principal

```mermaid
sequenceDiagram
    participant Client
    participant Controller as analyze.py
    participant Validator as AnalyzeValidator
    participant Service as AnalyzeService
    participant Factory as DocumentExtractionFactory
    participant Azure as AzureDocumentIntelligenceService
    participant ImageOrch as ImageExtractionOrchestrator
    participant HeaderParser
    participant QuestionParser
    participant Adapter as DocumentResponseAdapter

    Client->>Controller: POST /analyze_document
    Note over Client,Controller: email, file (PDF)
    
    Controller->>Validator: validate_all(file, email)
    Validator-->>Controller: ✅ Validation OK
    
    Controller->>Service: process_document_with_models(file, email, use_refactored=True)
    
    Service->>Factory: get_provider()
    Factory-->>Service: AzureDocumentIntelligenceService
    
    Service->>Azure: extract_document_data(file)
    Azure->>Azure: analyze_document() [Azure API Call]
    Azure-->>Service: extracted_data (text, metadata, raw_response)
    
    Service->>ImageOrch: _extract_images_with_fallback()
    Note over Service,ImageOrch: 1. Manual PDF (rápido)<br/>2. Azure Figures (fallback)<br/>3. Legacy (último recurso)
    ImageOrch-->>Service: image_data (Dict[str, str])
    
    Service->>HeaderParser: parse(extracted_text)
    HeaderParser-->>Service: legacy_header
    
    Service->>Service: InternalDocumentMetadata.from_legacy_header()
    
    Service->>QuestionParser: extract(text, image_data)
    QuestionParser-->>Service: question_data
    
    Note over Service: Se use_refactored=True:<br/>Processar figuras Azure<br/>Criar context blocks avançados
    
    Service-->>Controller: InternalDocumentResponse (Pydantic)
    
    Controller->>Adapter: to_api_response(internal_response)
    Adapter-->>Controller: api_response (Dict)
    
    Controller-->>Client: 200 OK + api_response
```

## 2. Endpoint `/analyze_document_mock` - Fluxo Mock

```mermaid
sequenceDiagram
    participant Client
    participant Controller as analyze.py
    participant ImageOrch as ImageExtractionOrchestrator
    participant Orchestrator as DocumentProcessingOrchestrator
    participant AzureService as AzureResponseService
    participant HeaderParser
    participant QuestionParser
    participant ContextBuilder as RefactoredContextBlockBuilder

    Client->>Controller: POST /analyze_document_mock
    Note over Client,Controller: image_extraction_method (opcional)
    
    Controller->>Controller: _process_mock_with_optimized_extraction()
    
    Controller->>ImageOrch: ImageExtractionMethod(method)
    ImageOrch-->>Controller: selected_method
    
    Controller->>Orchestrator: process_document_from_saved_azure_response()
    
    Orchestrator->>AzureService: load_latest_azure_response()
    AzureService-->>Orchestrator: azure_response (JSON)
    
    Orchestrator->>AzureService: convert_azure_response_to_extracted_data()
    AzureService-->>Orchestrator: extracted_data
    
    Orchestrator->>Orchestrator: _process_extracted_data(use_refactored=True)
    
    Orchestrator->>HeaderParser: parse(text)
    HeaderParser-->>Orchestrator: header_data
    
    Orchestrator->>QuestionParser: extract(text, images)
    QuestionParser-->>Orchestrator: question_data
    
    Note over Orchestrator: REFACTORED VERSION:<br/>Processar figuras Azure<br/>Criar context blocks dinâmicos
    
    Orchestrator->>ContextBuilder: analyze_azure_figures_dynamically()
    ContextBuilder-->>Orchestrator: enhanced_context_blocks
    
    Orchestrator->>ContextBuilder: remove_associated_figures_from_result()
    ContextBuilder-->>Orchestrator: cleaned_result
    
    Orchestrator-->>Controller: result (Dict)
    
    Controller-->>Client: 200 OK + result
```

## 3. Endpoint `/analyze_document_with_figures` - Fluxo Especializado

```mermaid
sequenceDiagram
    participant Client
    participant Controller as analyze.py
    participant Validator as AnalyzeValidator
    participant Service as AnalyzeService
    participant ImageOrch as ImageExtractionOrchestrator
    participant ManualExtractor as ManualPDFImageExtractor
    participant AzureExtractor as AzureFiguresImageExtractor

    Client->>Controller: POST /analyze_document_with_figures
    Note over Client,Controller: email, file, extraction_method,<br/>compare_methods, use_refactored
    
    Controller->>Validator: validate_all(file, email)
    Validator-->>Controller: ✅ Validation OK
    
    Controller->>Controller: ImageExtractionMethod(extraction_method)
    Note over Controller: Validar método: azure_figures ou manual_pdf
    
    Controller->>Service: process_document(file, email, use_refactored)
    Service-->>Controller: extracted_data (base)
    
    alt compare_methods = True
        Controller->>ImageOrch: extract_images_with_comparison()
        
        ImageOrch->>ManualExtractor: extract_images() [Método 1]
        ManualExtractor-->>ImageOrch: manual_images + metrics
        
        ImageOrch->>AzureExtractor: extract_images() [Método 2]
        AzureExtractor->>AzureExtractor: Azure API calls para figuras
        AzureExtractor-->>ImageOrch: azure_images + metrics
        
        ImageOrch-->>Controller: comparison_results + best_images
        
        Note over Controller: Adicionar comparison_results<br/>ao extracted_data
        
    else compare_methods = False
        Controller->>ImageOrch: extract_images_single_method(selected_method)
        
        alt extraction_method = "manual_pdf"
            ImageOrch->>ManualExtractor: extract_images()
            ManualExtractor-->>ImageOrch: images + metrics
        else extraction_method = "azure_figures"
            ImageOrch->>AzureExtractor: extract_images()
            AzureExtractor-->>ImageOrch: images + metrics
        end
        
        ImageOrch-->>Controller: extracted_images + metrics
        
        Note over Controller: Adicionar images e metrics<br/>ao extracted_data
    end
    
    Controller-->>Client: 200 OK + extracted_data_with_figures
```

## 📊 Comparação Detalhada dos Fluxos

### **Complexidade de Processamento**

| Endpoint | Complexidade | Tempo Estimado | API Calls Azure |
|----------|--------------|----------------|-----------------|
| `/analyze_document` | Alta | 15-30s | 1 (análise) + 0-1 (imagens fallback) |
| `/analyze_document_mock` | Baixa | 1-3s | 0 (usa dados salvos) |
| `/analyze_document_with_figures` | Variável | 5-60s | 1-3 (dependendo do método) |

### **Estratégias de Extração de Imagens**

| Endpoint | Estratégia | Métodos Disponíveis | Fallback |
|----------|------------|---------------------|----------|
| `/analyze_document` | Automática com fallback | Manual PDF → Azure Figures → Legacy | ✅ Sim |
| `/analyze_document_mock` | Configurável | Manual PDF (recomendado) | ❌ Não |
| `/analyze_document_with_figures` | Específica ou comparativa | Azure Figures, Manual PDF | ❌ Não |

### **Casos de Uso Recomendados**

| Endpoint | Cenário Ideal | Vantagens | Limitações |
|----------|---------------|-----------|------------|
| `/analyze_document` | **Produção principal** | Tipagem forte, fallback automático, performance otimizada | Maior complexidade |
| `/analyze_document_mock` | **Desenvolvimento/testes** | Rápido, sem consumo de API, reproduzível | Dados limitados aos salvos |
| `/analyze_document_with_figures` | **Análise especializada** | Controle fino, comparação de métodos, métricas detalhadas | Sem fallback automático |

## 🔄 Fluxos de Dados Principais

### **Modelos de Resposta**

1. **`/analyze_document`**: `InternalDocumentResponse` → `DocumentResponseAdapter` → API Response
2. **`/analyze_document_mock`**: Dict direto (formato legado)
3. **`/analyze_document_with_figures`**: Dict + métricas de extração

### **Processamento de Figuras**

- **Endpoint principal**: Integrado no fluxo com `RefactoredContextBlockBuilder`
- **Mock**: Usa dados pré-processados do Azure
- **Figures**: Foco específico na extração e comparação de métodos