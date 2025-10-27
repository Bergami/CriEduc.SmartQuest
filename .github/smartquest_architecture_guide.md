# 🏗️ SmartQuest - Guia de Arquitetura e Padrões

## 📋 Visão Geral do Projeto

O **SmartQuest** é uma API FastAPI que processa documentos de prova usando Azure Document Intelligence para extrair:

- **Header**: Metadados da prova (escola, série, matéria, etc.)
- **Context Blocks**: Textos com sub-contextos organizados por sequência
- **Questions**: Questões com alternativas e associações a contextos

## 🎯 Arquitetura Principal

### 📁 Estrutura de Diretórios

```
app/
├── api/                    # Controllers e rotas
│   └── controllers/        # Controladores específicos
├── adapters/              # Response adapters (Pydantic → Dict)
├── config/                 # Configurações e settings
├── core/                   # Utilitários centrais, logging, exceptions
│   └── constants/          # Constantes do sistema
├── data/                   # Dados estáticos (cidades, matérias, etc.)
├── dtos/                   # Data Transfer Objects
│   ├── api/               # DTOs para API
│   └── responses/          # DTOs para respostas da API
├── models/                 # Modelos Pydantic
│   └── internal/          # Modelos internos do sistema
├── parsers/                # Processadores de dados do Azure
│   ├── header_parser/      # Parser de cabeçalho
│   └── question_parser/    # Parser de questões
├── services/               # Lógica de negócio
├── utils/                  # Utilitários específicos
├── validators/             # Validação de dados
└── main.py                # Entry point da aplicação
```

### 🔄 Fluxo Principal de Processamento

1. **Entrada**: `/analyze_document` recebe PDF file + email
2. **Azure Integration**: `azure_document_intelligence_service.py` extrai dados
3. **Context Building**: `advanced_context_builder.py` e `refactored_context_builder.py` processam contextos
4. **Response Formatting**: Adaptadores convertem Pydantic models para formato da API
5. **Saída**: JSON estruturado conforme especificação

**⚠️ Estado Atual (Setembro 2025)**: O sistema está em migração Pydantic vs Dict, com endpoint principal (`/analyze_document`) em estado híbrido.

## 📦 Padrões de DTOs e Modelos

### 🔧 Estrutura de Modelos Pydantic (Internal)

```python
# Localização: app/models/internal/
- document_models.py  # InternalDocumentResponse, InternalDocumentMetadata
- context_models.py   # InternalContextBlock, InternalContextContent
- question_models.py  # InternalQuestion, InternalAnswerOption
- image_models.py     # InternalImageData, ImagePosition
```

### 🔧 Estrutura de DTOs (API)

```python
# Localização: app/dtos/
- api/document_dtos.py    # DocumentResponseDTO (principal)
- api/context_dtos.py     # ContextDTO, SubContextDTO
- api/question_dtos.py    # QuestionDTO
- responses/document_dtos.py # DTOs de resposta legacy
```

### 🔄 Adaptadores (Pydantic → Dict)

```python
# Localização: app/adapters/
- document_response_adapter.py # DocumentResponseAdapter
```

**⚠️ Nota de Migração**: O sistema está migrando de Dict para Pydantic. Alguns componentes ainda usam Dict internamente e requerem conversões.

### 🎨 Padrão de Conversão

```python
# Para Modelos Pydantic Internos
class InternalModel(BaseModel):
    @classmethod
    def from_legacy_data(cls, legacy_data: Dict[str, Any]):
        """Converte dados Dict legados para modelo Pydantic"""
        return cls(...)

# Para DTOs de API
class ApiDTO(BaseModel):
    @classmethod
    def from_internal_model(cls, internal_model):
        """Converte modelo interno Pydantic para DTO da API"""
        return cls(...)

    def to_legacy_format(self) -> Dict[str, Any]:
        """Converte para formato legacy da API (compatibilidade)"""
        return {...}

# Para Adaptadores
class ResponseAdapter:
    @staticmethod
    def to_api_response(internal_response) -> Dict[str, Any]:
        """Converte Pydantic para Dict (temporário durante migração)"""
        return {...}
```

## 🏗️ Context Blocks e Sub-Contexts

### 📝 Estrutura de Context Block

```json
{
  "id": 1,
  "type": ["image_collection"],
  "title": "Análise de Textos",
  "statement": "ANALISE OS TEXTO A SEGUIR:",
  "sub_contexts": [
    {
      "sequence": "A",
      "type": "charge",
      "title": "TEXTO A: charge",
      "content": "Texto da charge...",
      "images": [
        // URL da imagem
      ]
    }
  ],
  "hasImage": true
}
```

### 🎯 Sub-Context Types

- **charge**: Charges/cartuns
- **propaganda**: Textos publicitários
- **text**: Textos simples
- **image**: Conteúdo visual específico

## 🔧 Azure Document Intelligence

### 📍 Arquivos Principais

- `azure_document_intelligence_service.py`: Client do Azure
- `document_extraction_factory.py`: Factory para diferentes provedores
- `advanced_context_builder.py`: Processamento avançado de contextos
- `refactored_context_builder.py`: Processamento refatorado de contextos
- `document_processing_orchestrator.py`: Orquestrador de processamento
- `mock_document_service.py`: Serviço mock para testes

### 🎨 Dados do Azure (Estrutura Esperada)

```python
{
    "analyzeResult": {
        "documents": [...],
        "pages": [...],
        "tables": [...],
        "figures": [
            {
                "id": "figure_A",
                "boundingRegions": [...],
                "spans": [...]
            }
        ]
    }
}
```

- Lembrar: Quando um documento é processado ele retorna um json, contendo as informações do documento e as informações das imagens estão presente dentro da propriedade "figures". O sistema salva uma cópia desses responses em "D:\Git\CriEduc.SmartQuest\tests\responses\azure". Sempre que for analisar, busque o último arquivo processado, verifique pala data de modificação deste arquivo.

## 🎯 Padrões de Nomenclatura

### 📝 Convenções de Código

- **Classes**: PascalCase (`ContextBlockDTO`)
- **Funções/Variáveis**: snake_case (`from_internal_context`)
- **Constantes**: UPPER_CASE (`MAX_IMAGE_SIZE`)
- **Arquivos**: snake_case (`context_dtos.py`)

### 🌐 Convenções de API

- **Endpoints**: `/analyze/analyze_document`
- **Campos JSON**: camelCase no output (`hasImage`, `contextId`)
- **Campos internos**: snake_case (`has_image`, `context_id`)

## 🔄 Migração e Versionamento

### 📋 Formato Legacy vs Novo

```python
# Legacy (mantido para compatibilidade)
"contexts": [...]  # Nome antigo

# Novo (padrão atual)
"context_blocks": [...]  # Nome correto
```

### 🎯 Migração Pydantic vs Dict (Status Setembro 2025)

#### ✅ Componentes Migrados para Pydantic

- **Modelos Internos**: `InternalDocumentResponse`, `InternalDocumentMetadata`
- **DTOs de API**: Todos os DTOs principais
- **Validação**: Metadados de documento e estrutura básica

#### ⚠️ Componentes Híbridos (Em Migração)

- **Endpoint Principal**: `/analyze_document` usa Pydantic + Dict interno
- **InternalDocumentResponse**: Campos `questions` e `context_blocks` ainda são Dict
- **Parsers**: `HeaderParser` e `QuestionParser` retornam Dict

#### ❌ Componentes Ainda em Dict

- **Processamento Interno**: Pipeline de parsing usa Dict
- **Endpoint Legacy**: `/analyze_document_with_figures`
- **Context Builders**: Alguns ainda processam apenas Dict

#### 🔄 Conversões Desnecessárias

- **DocumentResponseAdapter**: Converte Pydantic → Dict (temporário)
- **Header Processing**: Dict → Pydantic → uso interno

## 🧪 Testing e Debug

### 📁 Estrutura de Testes

```
tests/
├── documents/          # Documentos de teste
├── extracted_images/   # Imagens extraídas
├── extracted_text/     # Textos extraídos
├── responses/         # Respostas do Azure salvas
└── unit/              # Testes unitários
```

### 🔧 Comandos de Debug

```powershell
# Rodar com mock (endpoint principal)
python start_simple.py --use-mock

# Executar via task configurada
# Use o comando run_task se disponível

# Rodar testes completos
python run_tests.py

# Rodar apenas testes unitários
python run_tests.py --unit

# Rodar com coverage
python run_tests.py --coverage

# Verificar primeiro conjunto de questões
python check_first_questions.py
```

## 🚨 Pontos Críticos de Atenção

### ⚠️ Validação de Dados - Estado Híbrido

```python
# ⚠️ ATENÇÃO: Sistema em migração Pydantic/Dict
# Alguns campos ainda são Dict mesmo em modelos "Pydantic"

# Verificar tipo antes de processar
if isinstance(data, BaseModel):
    # Processar como Pydantic Model
    result = data.field_name
elif isinstance(data, dict):
    # Processar como Dict
    result = data.get("field_name")
else:
    # Processo de conversão pode ser necessário
    pass

# Campos híbridos em InternalDocumentResponse:
# ✅ Pydantic: metadata, email, document_id
# ❌ Dict: questions, context_blocks
```

### 🔒 Campos Obrigatórios na Resposta

- `header`: Sempre presente com metadados
- `context_blocks`: Array de contextos (pode ser vazio)
- `questions`: Array de questões (pode ser vazio)
- `sub_contexts`: Array dentro de cada context_block

### 🎯 Response Structure (NUNCA ALTERAR)

```json
{
  "header": {...},
  "context_blocks": [...],
  "questions": [...]
}
```

## 📚 Recursos e Referências

### 🔗 Links Importantes

- Azure Document Intelligence API
- FastAPI Documentation
- Pydantic Models

### 📝 Arquivos de Configuração

- `.env`: Configurações principais
- `.env-local`: Chaves do Azure
- `pyproject.toml`: Dependências Python

### 🎯 Mock Response

- Usar `--use-mock` para testar sem Azure
- Mock simula resposta completa com dados realistas

## 🎨 Exemplo de Implementação

### 🔧 Adicionando Novo Campo ao Sistema Híbrido

```python
# 1. Se adicionando a modelo Pydantic interno
class InternalDocumentResponse(BaseModel):
    novo_campo: Optional[str] = Field(default=None)

# 2. Se adicionando a DTO de API
class DocumentResponseDTO(BaseModel):
    novo_campo: Optional[str] = Field(default=None)

    @classmethod
    def from_internal_response(cls, internal_response):
        return cls(
            # campos existentes...
            novo_campo=internal_response.novo_campo
        )

# 3. Se adicionando a adaptador (temporário)
class DocumentResponseAdapter:
    @staticmethod
    def to_api_response(internal_response):
        return {
            # campos existentes...
            "novo_campo": internal_response.novo_campo
        }

# 4. Se campo está em área Dict (questions/context_blocks)
# Adicionar via parser específico até migração completa
```

## 🎯 Regras de Negócio Específicas

### 📋 Context Builder Rules

- Sequences são identificadas como A, B, C, etc.
- Cada sequence pode ter múltiplas figures
- Sub-contexts são criados por sequence + figure
- Título formatado: "TEXTO {sequence}: {type}"

### 🎨 Image Processing

- Imagens são armazenadas como base64
- Azure extrai boundingRegions para localização
- Imagens associadas a contexts via sequence

## 🔧 Separação de Responsabilidades - Extração de Imagens

### 📋 Problema Identificado (Agosto 2025)

Durante manutenção do endpoint `/analyze/analyze_document_with_last_azure_response`, foi identificado que a **separação de responsabilidades** na extração de imagens não estava clara, causando demora em manutenções simples.

### 🎯 Responsabilidades Corretas

#### 📊 AzureFigureProcessor

**Localização**: `app/services/azure_figure_processor.py`
**Responsabilidade**: Processar APENAS metadados das figuras

```python
# ✅ FAZ (correto):
- Extrair coordenadas (polygon, boundingRegions)
- Classificar tipos (header, content, comic_strip, etc.)
- Associar contexto e legendas
- Ordenar por página e posição

# ❌ NÃO FAZ (não é responsabilidade):
- Extrair dados binários das imagens
- Converter para base64
- Salvar arquivos de imagem
```

#### 🔧 ImageExtractionOrchestrator

**Localização**: `app/services/image_extraction/image_extraction_orchestrator.py`
**Responsabilidade**: Orquestrar extração de imagens reais

```python
# ✅ FAZ (correto):
- Gerenciar estratégias de extração
- AZURE_FIGURES: Via Azure SDK
- MANUAL_PDF: Recorte manual baseado em coordenadas
- Fornecer fallback automático
- Retornar imagens em base64

# 📊 Estratégias Disponíveis:
ImageExtractionMethod.AZURE_FIGURES  # Azure SDK
ImageExtractionMethod.MANUAL_PDF     # Coordenadas manuais
```

### 🚨 Problema Específico Identificado

#### ❌ Situação Incorreta (Agosto 2025)

No método `process_document_with_azure_response()`:

```python
# ❌ PROBLEMA: Só processava metadados
processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_response)

# ❌ RESULTADO: Placeholders vazios
image_data = InternalImageData(
    base64_data="",  # TODO: Extrair imagem real
    file_path=f"temp/figure_{figure_id}.png",  # Placeholder
)
```

#### ✅ Solução Correta

```python
# ✅ SEPARAR RESPONSABILIDADES:

# 1. Processar metadados (AzureFigureProcessor)
processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_response)

# 2. Extrair imagens reais (ImageExtractionOrchestrator)
orchestrator = ImageExtractionOrchestrator()
image_data = await orchestrator.extract_images_single_method(
    method=ImageExtractionMethod.AZURE_FIGURES,
    document_analysis_result=azure_response,
    document_id=document_id
)
```

### 📋 Diferenças Entre Métodos de Processamento

#### 🔧 process_document_with_models()

**Status**: ✅ Implementação Correta

```python
# Usa AMBAS as responsabilidades corretamente:
1. Extração de texto/metadados (Document Extraction Factory)
2. Extração de imagens (ImageExtractionOrchestrator) ✅
3. Processamento Pydantic (PydanticQuestionParser)
```

#### ⚠️ process_document_with_azure_response()

**Status**: ❌ Implementação Incompleta (Identificado em Agosto 2025)

```python
# Estava usando APENAS metadados:
1. Processamento de metadados (AzureFigureProcessor) ✅
2. Extração de imagens (ImageExtractionOrchestrator) ❌ FALTANDO
3. Processamento Pydantic (PydanticQuestionParser) ✅
```

### 🎯 Regras de Arquitetura

#### ✅ Princípios Corretos

1. **Single Responsibility**: Cada classe tem UMA responsabilidade clara
2. **Separation of Concerns**: Metadados ≠ Extração de Imagens
3. **Orchestration Pattern**: ImageExtractionOrchestrator gerencia estratégias
4. **Strategy Pattern**: Múltiplas formas de extrair (Azure SDK vs Manual)

#### ❌ Anti-Patterns a Evitar

1. **God Class**: Uma classe fazendo tudo (metadados + extração + processamento)
2. **Mixed Responsibilities**: Processar metadados e extrair imagens no mesmo lugar
3. **Tight Coupling**: Hardcoded para uma única estratégia de extração

### 🔍 Checklist para Manutenções Futuras

Antes de modificar extração de imagens, verificar:

- [ ] **Metadados**: Está usando `AzureFigureProcessor`?
- [ ] **Imagens Reais**: Está usando `ImageExtractionOrchestrator`?
- [ ] **Estratégia**: Qual método (AZURE_FIGURES vs MANUAL_PDF)?
- [ ] **Fallback**: Tem fallback automático implementado?
- [ ] **Testes**: Ambos os casos (com/sem arquivo PDF) funcionam?

### 🔍 Question Processing

- Questions referenciam contexts via `context_id`
- Alternativas têm `letter` (A, B, C...) e `text`
- Campo `isCorrect` foi REMOVIDO (ETAPA 1)

---

**📌 Lembre-se**: Este projeto tem uma estrutura de resposta **FIXA** que não pode ser alterada sem quebrar a compatibilidade. Durante a migração Pydantic vs Dict, sempre preserve os campos essenciais e use adaptadores para conversões de compatibilidade.

## 🎯 Próximos Passos da Migração

### 🔴 Prioridade Alta

1. **Completar campos Pydantic em InternalDocumentResponse**

   - Migrar `questions: List[Dict]` → `questions: List[InternalQuestion]`
   - Migrar `context_blocks: List[Dict]` → `context_blocks: List[InternalContextBlock]`

2. **Refatorar Parsers para Pydantic**
   - `HeaderParser.parse()` retornar `InternalDocumentMetadata` diretamente
   - `QuestionParser.extract()` retornar objetos Pydantic tipados

### � Prioridade Média

3. **Eliminar DocumentResponseAdapter**

   - Usar `response_model` do FastAPI diretamente
   - Remover conversões Pydantic → Dict desnecessárias

4. **Unificar endpoints**
   - Migrar `/analyze_document_with_figures` para método refatorado
   - Padronizar processamento em todos os endpoints

### 📊 Métricas de Progresso

- **Atual**: 37% migrado para Pydantic
- **Meta**: 75% migrado (Outubro 2025)
- **Status**: Nenhum endpoint 100% Pydantic ainda
