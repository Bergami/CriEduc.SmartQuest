// =============================================================================
// 🗄️ MIGRATION: Criação das Coleções Iniciais
// =============================================================================
// Versão: 2025-10-14_001000
// Descrição: Criação das coleções analyze_documents e azure_processing_data
// Autor: Sistema MongoDB Persistence
// Data: 2025-10-14

print("🚀 [MIGRATION] Iniciando: create_initial_collections");

// Conectar à base de dados
db = db.getSiblingDB("smartquest");

// =============================================================================
// ✅ VERIFICAR SE MIGRAÇÃO JÁ FOI APLICADA
// =============================================================================
const migrationVersion = "2025-10-14_001000";
const existingMigration = db.migrations.findOne({ version: migrationVersion });

if (existingMigration) {
  print(
    `⚠️ [SKIP] Migração ${migrationVersion} já foi aplicada em ${existingMigration.applied_at}`
  );
  quit();
}

// =============================================================================
// 📊 CRIAÇÃO DAS COLEÇÕES
// =============================================================================

print("📄 Criando coleção 'analyze_documents'...");
if (!db.getCollectionNames().includes("analyze_documents")) {
  db.createCollection("analyze_documents");
  print("✅ Coleção 'analyze_documents' criada");
} else {
  print("ℹ️ Coleção 'analyze_documents' já existe");
}

print("🔷 Criando coleção 'azure_processing_data'...");
if (!db.getCollectionNames().includes("azure_processing_data")) {
  db.createCollection("azure_processing_data");
  print("✅ Coleção 'azure_processing_data' criada");
} else {
  print("ℹ️ Coleção 'azure_processing_data' já existe");
}

// =============================================================================
// 🎯 CRIAÇÃO DE ÍNDICES
// =============================================================================

print("🔍 Criando índices para analyze_documents...");
try {
  db.analyze_documents.createIndex(
    { user_email: 1 },
    { name: "idx_user_email" }
  );
  db.analyze_documents.createIndex(
    { created_at: -1 },
    { name: "idx_created_at_desc" }
  );
  db.analyze_documents.createIndex({ status: 1 }, { name: "idx_status" });
  db.analyze_documents.createIndex(
    { user_email: 1, created_at: -1 },
    { name: "idx_user_email_created_at" }
  );
  print("✅ Índices para analyze_documents criados");
} catch (error) {
  print(`⚠️ Erro ao criar índices para analyze_documents: ${error.message}`);
}

print("🔍 Criando índices para azure_processing_data...");
try {
  db.azure_processing_data.createIndex(
    { operation_id: 1 },
    { name: "idx_azure_operation_id" }
  );
  db.azure_processing_data.createIndex(
    { created_at: -1 },
    { name: "idx_azure_created_at_desc" }
  );
  db.azure_processing_data.createIndex(
    { model_id: 1 },
    { name: "idx_azure_model_id" }
  );
  print("✅ Índices para azure_processing_data criados");
} catch (error) {
  print(
    `⚠️ Erro ao criar índices para azure_processing_data: ${error.message}`
  );
}

// =============================================================================
// 📝 DADOS DE EXEMPLO (apenas se coleções estão vazias)
// =============================================================================

if (db.analyze_documents.countDocuments() === 0) {
  print("📝 Inserindo documento de exemplo em analyze_documents...");
  const sampleAnalyzeDocument = {
    _id: "123e4567-e89b-12d3-a456-426614174000",
    user_email: "admin@smartquest.com.br",
    file_name: "exemplo_documento.pdf",
    response: {
      document_id: "123e4567-e89b-12d3-a456-426614174000",
      status: "completed",
      context_blocks: [
        {
          type: "text",
          content: "Este é um documento de exemplo para validação do sistema.",
          page_number: 1,
        },
      ],
      questions: [
        {
          id: 1,
          text: "Qual é o objetivo principal do documento?",
          type: "objective",
          alternatives: [
            "Objetivo A",
            "Objetivo B",
            "Objetivo C",
            "Objetivo D",
          ],
        },
      ],
    },
    status: "completed",
    created_at: new Date(),
  };

  db.analyze_documents.insertOne(sampleAnalyzeDocument);
  print("✅ Documento de exemplo inserido em analyze_documents");
}

if (db.azure_processing_data.countDocuments() === 0) {
  print("📝 Inserindo documento de exemplo em azure_processing_data...");
  const sampleAzureData = {
    _id: "456f7890-a12b-34c5-d678-901234567890",
    operation_id: "azure_op_sample_123",
    model_id: "prebuilt-layout",
    api_version: "2023-07-31",
    response: {
      operation_id: "azure_op_sample_123",
      model_id: "prebuilt-layout",
      api_version: "2023-07-31",
      pages: [
        {
          page_number: 1,
          width: 8.5,
          height: 11.0,
          unit: "inch",
        },
      ],
      confidence: 0.95,
      status: "succeeded",
    },
    metrics: {
      processing_duration_seconds: 45.2,
      confidence_score: 0.95,
      pages_count: 1,
      context_blocks_count: 1,
      questions_count: 1,
      azure_operation_id: "azure_op_sample_123",
      azure_model_used: "prebuilt-layout",
      azure_api_version: "2023-07-31",
      extraction_quality_score: 0.92,
    },
    created_at: new Date(),
  };

  db.azure_processing_data.insertOne(sampleAzureData);
  print("✅ Documento de exemplo inserido em azure_processing_data");
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
  name: "create_initial_collections",
  description:
    "Criação das coleções analyze_documents e azure_processing_data com índices e dados de exemplo",
  applied_at: new Date(),
  script_file: "2025-10-14_001000_create_initial_collections.js",
});

// =============================================================================
// 🎉 RESUMO FINAL
// =============================================================================

print("📊 Resumo da migração:");
print(`- Base de dados: ${db.getName()}`);
print(`- Coleções criadas: ${db.getCollectionNames().length}`);
print(
  `- analyze_documents: ${db.analyze_documents.countDocuments()} documentos`
);
print(
  `- azure_processing_data: ${db.azure_processing_data.countDocuments()} documentos`
);
print(`- migrations: ${db.migrations.countDocuments()} migrações registradas`);

print("🎉 [SUCCESS] Migração create_initial_collections aplicada com sucesso!");
