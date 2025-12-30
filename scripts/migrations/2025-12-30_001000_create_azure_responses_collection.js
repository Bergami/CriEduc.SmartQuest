// =============================================================================
// 🗄️ MIGRATION: Criação da Collection azure_responses
// =============================================================================
// Versão: 2025-12-30_001000
// Descrição: Criação da coleção azure_responses para armazenar responses completos do Azure
// Autor: Sistema MongoDB Persistence
// Data: 2025-12-30

print("🚀 [MIGRATION] Iniciando: create_azure_responses_collection");

// Conectar à base de dados
db = db.getSiblingDB("smartquest");

// =============================================================================
// ✅ VERIFICAR SE MIGRAÇÃO JÁ FOI APLICADA
// =============================================================================
const migrationVersion = "2025-12-30_001000";
const existingMigration = db.migrations.findOne({ version: migrationVersion });

if (existingMigration) {
  print(
    `⚠️ [SKIP] Migração ${migrationVersion} já foi aplicada em ${existingMigration.applied_at}`
  );
  quit();
}

// =============================================================================
// 📊 CRIAÇÃO DA COLEÇÃO
// =============================================================================

print("📄 Criando coleção 'azure_responses'...");
if (!db.getCollectionNames().includes("azure_responses")) {
  db.createCollection("azure_responses");
  print("✅ Coleção 'azure_responses' criada");
} else {
  print("ℹ️ Coleção 'azure_responses' já existe");
}

// =============================================================================
// 🎯 CRIAÇÃO DE ÍNDICES
// =============================================================================

print("🔍 Criando índices para azure_responses...");
try {
  // Índice para buscar por document_id (referência cruzada)
  db.azure_responses.createIndex(
    { document_id: 1 },
    { name: "idx_document_id" }
  );

  // Índice para buscar por user_email
  db.azure_responses.createIndex({ user_email: 1 }, { name: "idx_user_email" });

  // Índice para ordenar por data de criação
  db.azure_responses.createIndex(
    { created_at: -1 },
    { name: "idx_created_at_desc" }
  );

  // Índice para buscar por status
  db.azure_responses.createIndex({ status: 1 }, { name: "idx_status" });

  // Índice composto para buscar responses de um usuário por data
  db.azure_responses.createIndex(
    { user_email: 1, created_at: -1 },
    { name: "idx_user_email_created_at" }
  );

  // Índice para buscar por arquivo específico
  db.azure_responses.createIndex(
    { file_name: 1, file_size: 1 },
    { name: "idx_file_name_size" }
  );

  // Índice para buscar por operation_id do Azure
  db.azure_responses.createIndex(
    { azure_operation_id: 1 },
    { name: "idx_azure_operation_id", sparse: true }
  );

  print("✅ Índices para azure_responses criados");
} catch (error) {
  print(`⚠️ Erro ao criar índices para azure_responses: ${error.message}`);
}

// =============================================================================
// 📝 DOCUMENTO DE EXEMPLO (apenas se coleção está vazia)
// =============================================================================

if (db.azure_responses.countDocuments() === 0) {
  print("📝 Inserindo documento de exemplo em azure_responses...");
  const sampleAzureResponse = {
    _id: "550e8400-e29b-41d4-a716-446655440000",
    document_id: "123e4567-e89b-12d3-a456-426614174000",
    user_email: "admin@smartquest.com.br",
    file_name: "exemplo_documento.pdf",
    file_size: 1024000,
    azure_response: {
      content:
        "Este é um documento de exemplo processado pelo Azure Document Intelligence.",
      pages: [
        {
          page_number: 1,
          width: 8.5,
          height: 11.0,
          unit: "inch",
        },
      ],
      paragraphs: [
        {
          content:
            "Este é um parágrafo de exemplo extraído do documento pela API do Azure.",
          role: "paragraph",
          confidence: 0.98,
        },
      ],
      tables: [],
      key_value_pairs: [],
    },
    azure_operation_id: "azure_op_example_001",
    azure_model_id: "prebuilt-layout",
    azure_api_version: "2023-07-31",
    processing_duration_seconds: 45.2,
    confidence_score: 0.95,
    page_count: 1,
    paragraph_count: 1,
    status: "success",
    error_message: null,
    created_at: new Date(),
  };

  db.azure_responses.insertOne(sampleAzureResponse);
  print("✅ Documento de exemplo inserido em azure_responses");
}

// =============================================================================
// 📋 REGISTRAR MIGRAÇÃO APLICADA
// =============================================================================

print("📋 Registrando migração aplicada...");
if (!db.getCollectionNames().includes("migrations")) {
  db.createCollection("migrations");
  print("✅ Coleção 'migrations' criada");
}

db.migrations.insertOne({
  version: migrationVersion,
  name: "create_azure_responses_collection",
  description:
    "Criação da coleção azure_responses para armazenar responses completos do Azure Document Intelligence",
  applied_at: new Date(),
  script_file: "2025-12-30_001000_create_azure_responses_collection.js",
});

// =============================================================================
// 🎉 RESUMO FINAL
// =============================================================================

print("📊 Resumo da migração:");
print(`- Base de dados: ${db.getName()}`);
print(`- Coleções totais: ${db.getCollectionNames().length}`);
print(`- azure_responses: ${db.azure_responses.countDocuments()} documentos`);
print(`- Índices criados: 7`);
print(`- migrations: ${db.migrations.countDocuments()} migrações registradas`);

print(
  "🎉 [SUCCESS] Migração create_azure_responses_collection aplicada com sucesso!"
);
