# Exemplo de Migração para o Sistema de Constantes

## Arquivo de exemplo: debug_api_check.py

### Antes (com paths hardcoded)
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
from pathlib import Path

# Paths hardcoded
json_path = "tests/fixtures/responses/azure_response_3Tri_20250716_215103.json"
pdf_path = "tests/fixtures/pdfs/modelo-prova.pdf"

print("🔧 DEBUG: Loading mock data...")

if not os.path.exists(json_path):
    print("❌ DEBUG: JSON file not found")
    sys.exit(1)
```

### Depois (usando constantes)
```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import json
from pathlib import Path
from app.core.constants import MockDataConstants, GeneralConstants

# Usar constantes para paths
json_path = MockDataConstants.get_primary_mock_response_path()
pdf_path = MockDataConstants.get_primary_mock_pdf_path()

# Usar constantes para debug
debug_prefix = GeneralConstants.get_debug_prefix("info")
error_prefix = GeneralConstants.get_debug_prefix("error")

print(f"{debug_prefix} Loading mock data...")

if not json_path.exists():
    print(f"{error_prefix} JSON file not found: {json_path}")
    sys.exit(1)
```

## Outros exemplos de migração

### Header Parser
```python
# Antes
DEFAULT_ENCODING = "utf-8"
MAX_HEADER_LINES = 20

# Depois
from app.core.constants import GeneralConstants

encoding = GeneralConstants.TEXT_PROCESSING["default_encoding"]
max_lines = GeneralConstants.HEADER_EXTRACTION["max_header_lines"]
```

### Configuração de API
```python
# Antes
app = FastAPI(
    title="SmartQuest",
    description="Document processing API",
    version="1.0.0"
)

# Depois
from app.core.constants import GeneralConstants

app = FastAPI(
    title=GeneralConstants.APP_NAME,
    description=GeneralConstants.APP_DESCRIPTION,
    version=GeneralConstants.APP_VERSION
)
```

### Validações de arquivo
```python
# Antes
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_FORMATS = [".pdf", ".docx", ".txt"]

if file.size > MAX_FILE_SIZE:
    raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE}")

if not any(file.filename.endswith(fmt) for fmt in SUPPORTED_FORMATS):
    raise ValueError(f"Unsupported format. Supported: {', '.join(SUPPORTED_FORMATS)}")

# Depois
from app.core.constants import GeneralConstants

max_size = GeneralConstants.DOCUMENT_LIMITS["max_file_size_mb"] * 1024 * 1024
supported_formats = GeneralConstants.DOCUMENT_LIMITS["supported_formats"]

if file.size > max_size:
    error_msg = GeneralConstants.ERROR_MESSAGES["invalid_format"].format(
        format=file.filename.split('.')[-1],
        supported=GeneralConstants.get_supported_formats_string()
    )
    raise ValueError(error_msg)
```

## Benefícios Observados

1. **Centralização**: Todos os valores em um local
2. **Consistência**: Prefixos de debug padronizados
3. **Flexibilidade**: Fallback automático para arquivos mock
4. **Manutenibilidade**: Alterações se propagam automaticamente
5. **Validação**: Métodos utilitários para verificar arquivos
6. **Documentação**: Valores auto-documentados pelas constantes

## Próximos Passos

1. Migrar arquivos de debug em `tests/debug_scripts/`
2. Atualizar parsers para usar constantes de configuração
3. Migrar configurações de API
4. Atualizar validadores para usar mensagens de erro padronizadas
5. Considerar adicionar constantes específicas para Azure Document Intelligence
