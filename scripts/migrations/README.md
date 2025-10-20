# 📁 Database Migrations - MongoDB SmartQuest

## 🎯 Objetivo

Scripts de migração para evolução controlada do banco de dados MongoDB.

## 📋 Convenção de Nomenclatura

```
YYYY-MM-DD_HHMMSS_nome_descritivo.js
```

**Exemplos:**

- `2025-10-14_001000_create_initial_collections.js`
- `2025-10-14_002000_add_azure_processing_data.js`
- `2025-10-14_003000_update_analyze_documents_structure.js`

## 🔧 Como Executar

### Script Automatizado (Recomendado)

```bash
# Único comando necessário
cd scripts
python run_migrations.py
```

### Via mongosh (Manual)

```bash
mongosh mongodb://localhost:27017/smartquest scripts/migrations/2025-10-14_001000_create_initial_collections.js
```

### Via Docker (Manual)

```bash
docker exec -i mongodb-container mongosh smartquest < scripts/migrations/2025-10-14_001000_create_initial_collections.js
```

## 📊 Estrutura dos Scripts

Cada script deve conter:

1. **Cabeçalho** com descrição da migração
2. **Verificação** se a migração já foi aplicada
3. **Execução** das alterações
4. **Log** da migração aplicada
5. **Rollback** (quando possível)

## 🗃️ Controle de Versão

Mantenha um registro das migrações aplicadas na coleção `migrations`:

```javascript
db.migrations.insertOne({
  version: "2025-10-14_001000",
  name: "create_initial_collections",
  applied_at: new Date(),
  description: "Criação das coleções iniciais do sistema",
});
```
