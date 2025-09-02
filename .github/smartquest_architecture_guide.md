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
├── config/                 # Configurações e settings
├── core/                   # Utilitários centrais, logging, exceptions
├── data/                   # Dados estáticos (cidades, matérias, etc.)
├── dtos/                   # Data Transfer Objects
│   └── responses/          # DTOs para respostas da API
├── parsers/                # Processadores de dados do Azure
├── services/               # Lógica de negócio
├── utils/                  # Utilitários específicos
└── validators/             # Validação de dados
```

### 🔄 Fluxo Principal de Processamento

1. **Entrada**: `/analyze/analyze_document` recebe imagem base64
2. **Azure Integration**: `azure_document_intelligence_service.py` extrai dados
3. **Context Building**: `refactored_context_builder.py` processa contextos
4. **Response Formatting**: DTOs convertem para formato da API
5. **Saída**: JSON estruturado conforme especificação

## 📦 Padrões de DTOs

### 🔧 Estrutura de Response DTOs
```python
# Localização: app/dtos/responses/
- context_dtos.py     # ContextBlockDTO, SubContextDTO
- document_dtos.py    # DocumentResponseDTO (principal)
- image_dtos.py       # ImageDTO
- question_dtos.py    # QuestionDTO
```

### 🎨 Padrão de Conversão
```python
class DTO(BaseModel):
    @classmethod
    def from_internal_context(cls, internal_data):
        """Converte dados internos para DTO da API"""
        # Lógica de conversão aqui
        return cls(...)

    def get_legacy_format(self) -> Dict[str, Any]:
        """Converte para formato legacy da API"""
        # Para compatibilidade com versões anteriores
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
      "images": ["base64_image_data"]
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
- `refactored_context_builder.py`: Processamento avançado de contextos

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

### 🎯 Campos Removidos (ETAPA 1)
- ❌ `isCorrect` nas alternativas
- ❌ `images` na raiz da resposta
- ❌ `summary` na raiz da resposta

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
# Rodar com mock
python start_simple.py --use-mock

# Testar endpoint específico
python test_api_direct.py

# Rodar testes
python -m pytest tests/
```

## 🚨 Pontos Críticos de Atenção

### ⚠️ Validação de Dados
```python
# CUIDADO: Hybrid Dict/Pydantic handling
if isinstance(internal_context, dict):
    # Processar como Dict
else:
    # Processar como Pydantic Model
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

### 🔧 Adicionando Novo Campo ao DTO
```python
# 1. Adicionar no DTO
class ContextBlockDTO(BaseModel):
    novo_campo: Optional[str] = Field(default=None)

# 2. Atualizar from_internal_context
@classmethod
def from_internal_context(cls, internal_context):
    return cls(
        # campos existentes...
        novo_campo=internal_context.get("novo_campo")
    )

# 3. Atualizar get_legacy_format se necessário
def get_legacy_format(self):
    return {
        # campos existentes...
        "novo_campo": self.novo_campo
    }
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

**📌 Lembre-se**: Este projeto tem uma estrutura de resposta **FIXA** que não pode ser alterada sem quebrar a compatibilidade. Sempre preserve os campos essenciais e use `get_legacy_format()` para conversões de compatibilidade.

## 📚 Lições Aprendidas - Manutenção Agosto 2025

### 🎯 Context da Manutenção
**Problema Reportado**: "As imagens não estão sendo trazidas neste endpoint"
**Endpoint Afetado**: `/analyze/analyze_document_with_last_azure_response`
**Causa Raiz**: Separação inadequada de responsabilidades

### 🔍 Investigação Realizada

#### 📊 Análise via Scripts de Debug
```python
# investigate_processed_figures.py - Revelou o problema:
# ✅ 7 figuras processadas com metadados completos
# ❌ Campos ausentes: 'file_path', 'base64_image'
# ✅ Metadados presentes: id, page_number, polygon, coordinates, etc.
```

#### 🎯 Root Cause Analysis
1. **AzureFigureProcessor** funcionando corretamente (metadados ✅)
2. **ImageExtractionOrchestrator** não estava sendo chamado (imagens ❌)
3. **Placeholders vazios** sendo criados sem dados reais

### 💡 Soluções Implementadas

#### 🔧 Fix Temporário (Placeholders)
```python
# Conversão básica de processed_figures para InternalImageData
image_data = InternalImageData(
    id=figure_id,
    file_path=f"temp/figure_{figure_id}.png",  # Placeholder
    base64_data="",  # TODO: Implementar extração real
    position=position,
    azure_coordinates=figure.get('polygon')
)
```

#### 🎯 Solução Definitiva (Pendente)
```python
# Integrar ImageExtractionOrchestrator no process_document_with_azure_response
orchestrator = ImageExtractionOrchestrator()
real_images = await orchestrator.extract_images_single_method(
    method=ImageExtractionMethod.AZURE_FIGURES,
    document_analysis_result=azure_response,
    document_id=document_id
)
```

### 🚀 Próximos Passos

#### 📋 Implementação Prioritária
1. **Integrar ImageExtractionOrchestrator** no `process_document_with_azure_response`
2. **Testar estratégia AZURE_FIGURES** sem arquivo PDF
3. **Implementar fallback** para MANUAL_PDF se necessário
4. **Validar endpoint** retorna imagens reais (não placeholders)

#### 🎯 Melhorias de Arquitetura
1. **Interface comum** para ambos métodos de processamento
2. **Factory pattern** para escolher estratégia automaticamente
3. **Métricas de performance** para comparar estratégias
4. **Documentação inline** sobre responsabilidades

### 🔒 Validações de Qualidade

#### ✅ Checklist de Conclusão
- [ ] Endpoint retorna imagens reais (base64_data preenchido)
- [ ] Mantém compatibilidade com formato de resposta
- [ ] Performance aceitável (< 30s processamento)
- [ ] Logs informativos sobre estratégia utilizada
- [ ] Testes automatizados para ambos cenários

#### 🎯 Métricas de Sucesso
- **Imagens extraídas**: > 0 para documentos com figuras
- **Taxa de sucesso**: > 95% para documentos válidos
- **Tempo de resposta**: < 30 segundos
- **Separação clara**: Metadados vs Extração de imagens

### 🔧 Comandos de Debug Úteis

```powershell
# Investigar figuras processadas
python investigate_processed_figures.py

# Testar endpoint com Azure response
python test_api_direct.py

# Executar com mock para validação
python start_simple.py --use-mock

# Verificar extração de imagens específica
python -c "from app.services.image_extraction import ImageExtractionOrchestrator; print('Available methods:', ImageExtractionOrchestrator().get_available_methods())"
```

**⚠️ IMPORTANTE**: Esta documentação reflete o estado em Agosto 2025. Para manutenções futuras, sempre verificar se a separação de responsabilidades está sendo respeitada.
