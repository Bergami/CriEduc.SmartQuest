# 📋 **Plano de Ação Detalhado - Upload de Imagens para Azure Blob Storage**

## 🔍 **Reanálise Completa da Situação Atual**

### **📍 Pontos Chave Identificados:**

#### **1. Salvamento Local de Imagens (🎯 Para Remover):**

- **`ImageSavingService`** - Salva base64 → JPG local em `tests/images/by_provider/`
- **`CentralizedFileManager`** - Centraliza salvamento em diretórios estruturados
- **`DocumentStorageService.save_document_images()`** - Persiste images base64 → arquivos locais
- **Base Image Extractors** - Convertem base64 → bytes → arquivos via `_save_image()`

#### **2. Inclusão de Images no Header (🎯 Para Remover):**

- **`HeaderParser.parse()`** - Linha 58: `result["images"] = header_images`
- **`HeaderDTO`** - Campo `images: List[str]`
- **`DocumentResponseDTO.from_internal_response()`** - Inclui `header_images` no response

#### **3. Inclusão de Images nos Context Blocks (🎯 Para Modificar):**

- **`RefactoredContextBlockBuilder`** - Adiciona base64 via `_add_base64_images_to_figures()`
- **`_create_individual_context_block()`** - Linha 1086: `context_block['images'] = [figure.base64_image]`
- **`_create_simple_context_block_from_group()`** - Linha 1228: `context_block['images'] = images`
- **`ContextBlockImageProcessor.enrich_context_blocks_with_images()`** - Enriquece com base64

#### **4. Estrutura dos DTOs:**

- **`ContextBlockDTO`** - Campo `images: List[str]` (base64) → deve virar URLs
- **`SubContextDTO`** - Campo `images: List[str]` (base64) → deve virar URLs
- **`InternalContextBlock`** - Campo `images: List[str]` → representa base64 atualmente

## 🎯 **Plano Detalhado de Implementação**

### **📋 Etapa 1: Configuração e Infraestrutura**

**Objetivo:** Preparar ambiente para Azure Blob Storage

**1.1 Adicionar Configurações Azure Blob Storage**

**⚠️ IMPORTANTE:** Seguir o padrão existente de configuração:

- Configurações sensíveis ficam no `.env-local` (já adicionadas)
- Configurações públicas/defaults ficam no `settings.py`

```python
# Em app/config/settings.py - Adicionar apenas as configurações públicas
azure_blob_storage_url: str = os.getenv("AZURE_BLOB_STORAGE_URL", "")
azure_blob_container_name: str = os.getenv("AZURE_BLOB_CONTAINER_NAME", "")
azure_blob_sas_token: str = os.getenv("AZURE_BLOB_SAS_TOKEN", "")
enable_azure_blob_upload: bool = os.getenv("ENABLE_AZURE_BLOB_UPLOAD", "true").lower() == "true"

# Propriedade computed para SAS URL completa
@property
def azure_blob_sas_url(self) -> str:
    """Constrói URL completa com SAS token"""
    if not self.azure_blob_storage_url or not self.azure_blob_container_name or not self.azure_blob_sas_token:
        return ""
    return f"{self.azure_blob_storage_url}/{self.azure_blob_container_name}?{self.azure_blob_sas_token}"
```

```bash
# .env-local - Configurações sensíveis (JÁ EXISTEM)
AZURE_BLOB_STORAGE_URL=https://crieducstorage.blob.core.windows.net
AZURE_BLOB_CONTAINER_NAME=crieduc-documents
AZURE_BLOB_SAS_TOKEN=sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D
ENABLE_AZURE_BLOB_UPLOAD=true
```

**1.2 Criar Serviço de Upload para Azure**

```python
# Novo arquivo: app/services/storage/azure_image_upload_service.py
class AzureImageUploadService:
    async def upload_images_and_get_urls(
        self,
        images_base64: Dict[str, str],
        document_id: str
    ) -> Dict[str, str]:
        """Converte {image_id: base64} → {image_id: url_publica}"""
```

### **📋 Etapa 2: Remover Images do Header**

**Objetivo:** Eliminar completamente images do header conforme requisito

**2.1 HeaderParser**

- **Arquivo:** `app/parsers/header_parser/base.py`
- **Ação:** Remover linhas 58-61 que adicionam `result["images"]`

**2.2 HeaderDTO**

- **Arquivo:** `app/dtos/responses/document_response_dto.py`
- **Ação:** Remover campo `images: List[str]` da classe `HeaderDTO`

**2.3 DocumentResponseDTO**

- **Arquivo:** `app/dtos/responses/document_response_dto.py`
- **Ação:** Remover linha que inclui header_images no `from_internal_response()`

### **📋 Etapa 3: Modificar Context Blocks para URLs**

**Objetivo:** Substituir base64 por URLs do Azure Blob Storage

**3.1 Integrar Upload no RefactoredContextBlockBuilder**

- **Arquivo:** `app/services/context/refactored_context_builder.py`
- **Método:** `_add_base64_images_to_figures()`
- **Ação:** Antes de adicionar às figuras, fazer upload para Azure e obter URLs

**3.2 Atualizar \_create_individual_context_block**

- **Arquivo:** `app/services/context/refactored_context_builder.py`
- **Linha:** 1086 `context_block['images'] = [figure.base64_image]`
- **Ação:** Substituir por URLs obtidas do Azure

**3.3 Atualizar \_create_simple_context_block_from_group**

- **Arquivo:** `app/services/context/refactored_context_builder.py`
- **Linha:** 1228 `context_block['images'] = images`
- **Ação:** Substituir por URLs

**3.4 Modificar ContextBlockImageProcessor**

- **Arquivo:** `app/parsers/question_parser/context_block_image_processor.py`
- **Método:** `enrich_context_blocks_with_images()`
- **Ação:** Processar URLs ao invés de base64

### **📋 Etapa 4: Remover Salvamento Local**

**Objetivo:** Eliminar persistência local de imagens, reutilizar lógica para Azure

**4.1 Investigar e Remover Calls de Salvamento**

- **`ManualPDFImageExtractor`** - Linha 127: Remove chamada `self._save_image()`
- **`AzureFiguresImageExtractor`** - Linha 156: Remove chamada `self._save_image()`
- **`DocumentStorageService.save_document_images()`** - Tornar opcional via feature flag

**4.2 Reutilizar Lógica de Conversão**

- **`_save_single_image()`** em `ImageSavingService` - Aproveitar `base64.b64decode()`
- **`PDFImageExtractor.get_base64_image()`** - Manter lógica de conversão bytes→base64

### **📋 Etapa 5: Atualizar DTOs**

**Objetivo:** Ajustar documentação e exemplos para URLs

**5.1 ContextBlockDTO**

- **Arquivo:** `app/dtos/responses/document_response_dto.py`
- **Campo:** `images: List[str]` → Atualizar descrição de "base64" para "URLs públicas"

**5.2 SubContextDTO**

- **Arquivo:** `app/dtos/responses/document_response_dto.py`
- **Campo:** `images: List[str]` → Atualizar descrição

**5.3 Exemplos nos Schemas**

- Atualizar todos os `schema_extra` para usar URLs de exemplo ao invés de base64

### **📋 Etapa 6: Validação e Testes**

**Objetivo:** Garantir funcionamento correto

**6.1 Usar test_blob_integration.py Existente**

- Testar se URLs aparecem nos context_blocks
- Verificar se header não tem mais propriedade images
- Validar formato das URLs geradas

**6.2 Teste Manual**

- Executar endpoint com documento real
- Verificar response conforme exemplo desejado do prompt

## 🔧 **Detalhamento Técnico da Integração**

### **Fluxo de Processamento Proposto:**

```
1. Imagens extraídas → base64 (mantém atual)
2. RefactoredContextBlockBuilder recebe base64
3. 🆕 NOVO: Upload para Azure → URLs obtidas
4. URLs substituem base64 nos context_blocks
5. Response final: header sem images, context_blocks com URLs
```

### **Ponto de Integração Principal:**

```python
# Em RefactoredContextBlockBuilder._add_base64_images_to_figures()
async def _add_base64_images_to_figures(self, figures, images_base64):
    if not images_base64:
        return

    # 🆕 NOVO: Upload para Azure e obter URLs
    azure_service = AzureImageUploadService()
    images_urls = await azure_service.upload_images_and_get_urls(
        images_base64, document_id
    )

    # Usar URLs ao invés de base64
    for figure in figures:
        if figure.id in images_urls:
            figure.azure_url = images_urls[figure.id]  # URL ao invés de base64
```

## ⚡ **Implementação em Pequenos Passos**

1. ✅ **Configurar Azure Settings** - **CONCLUÍDO** ✅
2. ✅ **Criar Serviço de Upload** - **CONCLUÍDO** ✅ 
3. ⭕ **Remover Images do Header**
4. ⭕ **Integrar Upload no Context Builder**
5. ⭕ **Modificar Logic Context Blocks**
6. ⭕ **Remover Salvamento Local**
7. ⭕ **Testar Integração Completa**

## 🎯 **Status: Etapa 1 Concluída com Sucesso**

### ✅ **Etapa 1: Configuração e Infraestrutura - FINALIZADA**

**🔧 Configurações Implementadas:**
- ✅ Configurações Azure Blob Storage adicionadas em `app/config/settings.py`
- ✅ Padrão Pydantic BaseSettings mantido para compatibilidade
- ✅ Propriedades computed (`azure_blob_sas_url`, `azure_blob_enabled`) implementadas
- ✅ MockSettings atualizado com configurações Azure

**🚀 Serviço Implementado:**
- ✅ `AzureImageUploadService` criado em `app/services/storage/azure_image_upload_service.py`
- ✅ Upload assíncrono de múltiplas imagens implementado
- ✅ Nomenclatura segura de blobs com timestamp e UUID
- ✅ Tratamento de erros robusto com logging detalhado
- ✅ URLs com SAS token para acesso (necessário devido à configuração do storage account)

**🧪 Validação Implementada:**
- ✅ Teste de conectividade completo em `test_azure_blob_connection.py`
- ✅ **TODOS OS TESTES PASSARAM** - Azure Blob Storage funcionando 100%
- ✅ Upload real testado com imagem de 1x1 pixel (638 bytes)
- ✅ URL pública acessível com SAS token

**📊 Resultado dos Testes:**
```
Status Geral: PASS
Resumo: {'PASS': 4, 'FAIL': 0, 'SKIP': 0}

✅ CONFIGURATION: PASS - Todas as configurações Azure estão presentes  
✅ CONNECTIVITY: PASS - Conectividade básica OK
✅ IMAGE_UPLOAD: PASS - Upload realizado com sucesso
✅ PUBLIC_URL: PASS - URL pública acessível - 638 bytes recebidos

🎉 Todos os testes passaram! Azure Blob Storage está funcionando corretamente.
```

**🔍 Descobertas Importantes:**
- Storage account não permite acesso público direto (status 409)
- URLs devem incluir SAS token para acesso
- Metadados personalizados do Azure são sensíveis a caracteres especiais
- Upload via PUT request funciona perfeitamente com status 201

---

### 🚀 **Pronto para Próximas Etapas**

A infraestrutura Azure está 100% operacional. Próximos passos:
- **Etapa 2:** Remover Images do Header
- **Etapa 3:** Integrar Upload no Context Builder  
- **Etapa 4:** Modificar Logic Context Blocks

## 📝 **Arquivos Específicos a Modificar**

### **Configuração:**

- `app/config/settings.py` - Adicionar configurações Azure Blob Storage

### **Novos Serviços:**

- `app/services/storage/azure_image_upload_service.py` - Serviço de upload

### **Header (Remover Images):**

- `app/parsers/header_parser/base.py` - Método `parse()`
- `app/dtos/responses/document_response_dto.py` - Classes `HeaderDTO` e `DocumentResponseDTO`

### **Context Blocks (Base64 → URLs):**

- `app/services/context/refactored_context_builder.py` - Múltiplos métodos
- `app/parsers/question_parser/context_block_image_processor.py` - Método `enrich_context_blocks_with_images()`

### **Salvamento Local (Remover/Opcional):**

- `app/services/image/extraction/manual_pdf_extractor.py`
- `app/services/image/extraction/azure_figures_extractor.py`
- `app/services/storage/document_storage_service.py`

### **DTOs e Documentação:**

- `app/dtos/responses/document_response_dto.py` - Atualizar descrições
- Vários arquivos com `schema_extra` - Atualizar exemplos

## 🔍 **Exemplo de Transformação Esperada**

### **🔴 ANTES (Atual):**

```json
{
  "header": {
    "school": "UMEF Saturnino Rangel Mauro",
    "teacher": "Danielle",
    "subject": "Língua Portuguesa",
    "images": ["/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQEBAQI..."]
  },
  "context_blocks": [
    {
      "id": 1,
      "type": ["text", "image"],
      "hasImage": true,
      "images": ["/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQEBAQI..."],
      "contentType": "image/jpeg;base64"
    }
  ]
}
```

### **🟢 DEPOIS (Desejado):**

```json
{
  "header": {
    "school": "UMEF Saturnino Rangel Mauro",
    "teacher": "Danielle",
    "subject": "Língua Portuguesa"
  },
  "context_blocks": [
    {
      "id": 1,
      "type": ["text", "image"],
      "hasImage": true,
      "images": [
        "https://crieducstorage.blob.core.windows.net/crieduc-documents/doc123-img1.jpg"
      ],
      "contentType": "image/url"
    }
  ]
}
```

## 🚨 **Riscos e Considerações**

### **Técnicos:**

- **Latência:** Upload para Azure adiciona tempo de processamento
- **Falhas de Upload:** Necessário fallback ou retry logic
- **Dependência Externa:** Azure Blob Storage deve estar disponível

### **Arquiteturais:**

- **Breaking Change:** Clientes devem atualizar para processar URLs ao invés de base64
- **Versionamento:** Considerar versionamento da API durante transição

### **Operacionais:**

- **Custos:** Armazenamento e transferência no Azure
- **Monitoramento:** Logs de upload, falhas, latência
- **Limpeza:** Estratégia para remoção de imagens antigas

---

**📌 Este plano contempla todos os requisitos do prompt original com implementação em pequenos passos controláveis.**
