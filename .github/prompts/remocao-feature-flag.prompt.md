# Remoção de Feature Flags: enable_mongodb_persistence e enable_local_image_saving

## Contexto
Atualmente, o sistema utiliza duas feature flags para controlar o comportamento de persistência e salvamento de imagens:

1. **`enable_mongodb_persistence`**: Define se a persistência no MongoDB está habilitada.
2. **`enable_local_image_saving`**: Define se o salvamento local de imagens está habilitado.

Com base nas melhores práticas e na evolução do sistema, o comportamento padrão deve ser:
- **Persistência no MongoDB** como o mecanismo principal de armazenamento.
- **Salvamento no Azure Blob Storage** como o único destino para imagens.
- Caso qualquer um desses serviços esteja indisponível, o sistema deve retornar um erro apropriado.

A remoção dessas feature flags simplificará o código, eliminando caminhos alternativos e garantindo maior consistência no comportamento do sistema.

---

## Objetivo
Remover as feature flags `enable_mongodb_persistence` e `enable_local_image_saving` do sistema, garantindo que:
- O MongoDB seja sempre utilizado como o mecanismo de persistência.
- O Azure Blob Storage seja o único destino para salvamento de imagens.
- Erros sejam retornados caso qualquer um dos serviços esteja indisponível.
- Logs estruturados sejam utilizados para melhorar a observabilidade e facilitar o monitoramento.

---

## Passos para Remoção

### 1. Atualizar o Arquivo de Configuração
- **Arquivo:** `app/config/settings.py`
- **Ação:** Remover as definições das feature flags `enable_mongodb_persistence` e `enable_local_image_saving`.
- **Exemplo:**
  ```python
  # Remover estas linhas:
  enable_mongodb_persistence: bool = os.getenv("ENABLE_MONGODB_PERSISTENCE", "true").lower() == "true"
  enable_local_image_saving: bool = os.getenv("ENABLE_LOCAL_IMAGE_SAVING", "false").lower() == "true"
  ```

### 2. Atualizar os Serviços
#### 2.1. DocumentStorageService
- **Arquivo:** `app/services/storage/document_storage_service.py`
- **Ação:** Remover verificações relacionadas à feature flag `enable_local_image_saving`.
- **Comportamento:** Garantir que o salvamento de imagens seja feito exclusivamente no Azure Blob Storage.
- **Exemplo:**
  ```python
  # Antes:
  if not settings.enable_local_image_saving:
      logger.info("Local image saving disabled by feature flag")
      return {}

  # Depois:
  # Sempre salvar no Azure Blob Storage
  ```

#### 2.2. BaseDocumentProvider
- **Arquivo:** `app/services/providers/base_document_provider.py`
- **Ação:** Remover verificações relacionadas à feature flag `enable_local_image_saving`.
- **Comportamento:** Garantir que o salvamento de imagens seja feito exclusivamente no Azure Blob Storage.

#### 2.3. MongoDB Persistence
- **Arquivo:** `app/services/persistence/mongodb_service.py` (ou equivalente)
- **Ação:** Remover verificações relacionadas à feature flag `enable_mongodb_persistence`.
- **Comportamento:** Garantir que o MongoDB seja sempre utilizado como o mecanismo de persistência.

### 3. Adicionar Tratamento de Erros
- **Ação:** Garantir que erros sejam retornados caso o MongoDB ou o Azure Blob Storage estejam indisponíveis.
- **Exemplo:**
  ```python
  if not mongodb_service.is_available():
      logger.error("MongoDB is unavailable")
      raise PersistenceError("MongoDB is unavailable")

  if not azure_blob_service.is_available():
      logger.error("Azure Blob Storage is unavailable")
      raise StorageError("Azure Blob Storage is unavailable")
  ```

### 4. Garantir Logging Estruturado
- **Ação:** Substituir logs simples por logs estruturados para melhorar a observabilidade.
- **Exemplo:**
  ```python
  logger.info({
      "event": "image_saved",
      "status": "success",
      "storage": "azure_blob",
      "document_id": document_id
  })
  ```

### 5. Atualizar Testes
- **Ação:** Atualizar os testes unitários e de integração para refletir a remoção das feature flags.
- **Exemplo:**
  - Remover cenários de teste que verificam o comportamento com as feature flags habilitadas/desabilitadas.
  - Garantir que os testes validem o comportamento padrão (MongoDB e Azure Blob Storage).

---

## Considerações Finais
- **Benefícios:**
  - Simplificação do código.
  - Redução de caminhos alternativos e potenciais fontes de bugs.
  - Garantia de consistência no comportamento do sistema.
  - Melhor observabilidade com logs estruturados.

- **Impacto:**
  - O sistema dependerá exclusivamente do MongoDB e do Azure Blob Storage.
  - Erros serão retornados caso qualquer um dos serviços esteja indisponível.

- **Próximos Passos:**
  - Implementar as mudanças descritas.
  - Validar o comportamento do sistema após as alterações.
  - Monitorar os logs para garantir que a observabilidade foi aprimorada.
