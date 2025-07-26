# Sistema de Constantes - SmartQuest

## Visão Geral

O sistema de constantes do SmartQuest foi implementado para centralizar todas as configurações, paths e valores constantes utilizados na aplicação. Isso melhora a manutenibilidade, reduz duplicação de código e facilita alterações futuras.

## Estrutura

O sistema está organizado em três módulos principais dentro de `app/core/constants/`:

### 1. ProjectPaths (`paths.py`)
Centraliza todos os paths e estruturas de diretórios do projeto.

```python
from app.core.constants import ProjectPaths

# Acessar diretórios principais
tests_root = ProjectPaths.TESTS_ROOT
app_root = ProjectPaths.APP_ROOT

# Acessar subdiretórios específicos
fixtures_dir = ProjectPaths.TESTS_FIXTURES
parsers_dir = ProjectPaths.APP_PARSERS

# Métodos utilitários
absolute_path = ProjectPaths.get_absolute_path(ProjectPaths.TESTS_ROOT)
ProjectPaths.ensure_directory_exists(ProjectPaths.TESTS_DEBUG_SCRIPTS)
```

### 2. MockDataConstants (`mock_data.py`)
Contém todas as constantes específicas para dados de mock e testes.

```python
from app.core.constants import MockDataConstants

# Obter o arquivo de resposta mock primário (com fallback automático)
primary_response = MockDataConstants.get_primary_mock_response_path()

# Obter o PDF mock principal
pdf_path = MockDataConstants.get_primary_mock_pdf_path()

# Validar existência dos arquivos mock
status = MockDataConstants.validate_mock_files_exist()

# Configurações de detecção de header
threshold = MockDataConstants.HEADER_DETECTION["vertical_threshold"]
```

### 3. GeneralConstants (`general.py`)
Constantes gerais da aplicação, configurações e mensagens.

```python
from app.core.constants import GeneralConstants

# Configurações de debug
if GeneralConstants.is_debug_enabled():
    prefix = GeneralConstants.get_debug_prefix("success")
    print(f"{prefix} Operação concluída")

# Configurações de texto
encoding = GeneralConstants.TEXT_PROCESSING["default_encoding"]
preview_length = GeneralConstants.TEXT_PROCESSING["text_preview_length"]

# Limites de documento
max_size = GeneralConstants.DOCUMENT_LIMITS["max_file_size_mb"]
supported_formats = GeneralConstants.get_supported_formats_string()
```

## Benefícios

### 1. Centralização
- Todos os paths e configurações em um local único
- Fácil localização e alteração de valores
- Redução de código duplicado

### 2. Organização por Propósito
- **Paths**: Estrutura de diretórios e arquivos
- **Mock Data**: Configurações específicas para testes e mocks
- **General**: Configurações gerais da aplicação

### 3. Funcionalidades Avançadas
- Fallback automático para arquivos mock
- Validação de existência de arquivos
- Métodos utilitários para manipulação de paths
- Configurações contextuais (debug, limits, etc.)

### 4. Facilidade de Manutenção
- Alterações em um local se propagam por toda a aplicação
- Menor chance de erros de path/configuração
- Facilita refatorações futuras

## Uso no Código

### Antes (hardcoded)
```python
json_path = Path("tests/fixtures/responses/azure_response_3Tri_20250716_215103.json")
if not json_path.exists():
    json_path = Path("tests/fixtures/responses/RetornoProcessamento.json")
    
pdf_path = "tests/fixtures/pdfs/modelo-prova.pdf"
print("🔧 DEBUG: Processing...")
```

### Depois (com constantes)
```python
from app.core.constants import MockDataConstants, GeneralConstants

json_path = MockDataConstants.get_primary_mock_response_path()
pdf_path = MockDataConstants.get_primary_mock_pdf_path()
debug_prefix = GeneralConstants.get_debug_prefix("info")
print(f"{debug_prefix} Processing...")
```

## Extensibilidade

O sistema pode ser facilmente estendido adicionando:

1. **Novos módulos de constantes**: Para funcionalidades específicas
2. **Novas configurações**: Nos módulos existentes
3. **Métodos utilitários**: Para operações comuns

### Exemplo de Extensão
```python
# app/core/constants/api_config.py
class APIConstants:
    ENDPOINTS = {
        "analyze": "/analyze/analyze_document",
        "health": "/health",
        "docs": "/docs"
    }
    
    TIMEOUT_CONFIG = {
        "request_timeout": 30,
        "connection_timeout": 5
    }
```

## Migração

Para migrar código existente:

1. Identifique valores hardcoded
2. Determine a categoria apropriada (paths, mock, general)
3. Adicione à classe de constantes correspondente
4. Substitua o valor hardcoded pela referência à constante
5. Importe a classe de constantes no arquivo

## Diretrizes

1. **Nomenclatura**: Use nomes descritivos e consistentes
2. **Organização**: Agrupe configurações relacionadas
3. **Documentação**: Inclua docstrings para métodos complexos
4. **Validação**: Implemente validações quando necessário
5. **Compatibilidade**: Mantenha retrocompatibilidade quando possível

Este sistema de constantes torna o código mais limpo, organizados e fácil de manter, especialmente em um projeto que lida com múltiplos paths de arquivos e configurações complexas como o SmartQuest.
