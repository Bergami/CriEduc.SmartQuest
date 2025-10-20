// =============================================================================
// 🗄️ MIGRATION: Adicionar Campo Status Melhorado
// =============================================================================
// Versão: 2025-10-14_002000
// Descrição: Exemplo de como adicionar um novo campo às coleções existentes
// Autor: Sistema MongoDB Persistence
// Data: 2025-10-14

print("🚀 [MIGRATION] Iniciando: add_enhanced_status_field");

// Conectar à base de dados
db = db.getSiblingDB("smartquest");

// =============================================================================
// ✅ VERIFICAR SE MIGRAÇÃO JÁ FOI APLICADA
// =============================================================================
const migrationVersion = "2025-10-14_002000";
const existingMigration = db.migrations.findOne({ version: migrationVersion });

if (existingMigration) {
  print(
    `⚠️ [SKIP] Migração ${migrationVersion} já foi aplicada em ${existingMigration.applied_at}`
  );
  quit();
}

// =============================================================================
// 🔄 APLICAR MODIFICAÇÕES
// =============================================================================

print("🔄 Adicionando campo 'enhanced_status' aos documentos existentes...");

// Atualizar analyze_documents que não tem o campo enhanced_status
const analyzeUpdateResult = db.analyze_documents.updateMany(
  { enhanced_status: { $exists: false } },
  {
    $set: {
      enhanced_status: {
        current: "$status",
        updated_at: new Date(),
        history: [],
      },
    },
  }
);

print(
  `✅ analyze_documents: ${analyzeUpdateResult.modifiedCount} documentos atualizados`
);

// =============================================================================
// 🏃‍♂️ ROLLBACK (OPCIONAL - para demonstração)
// =============================================================================

// UNCOMMMENT para criar função de rollback
/*
print("📝 Para fazer rollback desta migração, execute:");
print("db.analyze_documents.updateMany({}, { $unset: { enhanced_status: 1 } });");
*/

// =============================================================================
// 📋 REGISTRAR MIGRAÇÃO APLICADA
// =============================================================================

print("📋 Registrando migração aplicada...");
db.migrations.insertOne({
  version: migrationVersion,
  name: "add_enhanced_status_field",
  description:
    "Adiciona campo enhanced_status com histórico aos documentos de análise",
  applied_at: new Date(),
  script_file: "2025-10-14_002000_add_enhanced_status_field.js",
  rollback_instructions:
    "db.analyze_documents.updateMany({}, { $unset: { enhanced_status: 1 } });",
});

print("🎉 [SUCCESS] Migração add_enhanced_status_field aplicada com sucesso!");
