// =============================================================================
// 🔄 MIGRATION: Adicionar campo file_size e índice de duplicatas
// =============================================================================
// Versão: 2025-12-06_001000
// Descrição: Adiciona campo file_size e cria índice composto para verificação de duplicatas
// Autor: Sistema - Cache Removal Project
// Data: 2025-12-06
// Referência: Issue #remove-cache-add-duplicate-check

print("🚀 [MIGRATION] Iniciando: add_file_size_and_duplicate_index");

// Conectar à base de dados
db = db.getSiblingDB("smartquest");

// =============================================================================
// ✅ VERIFICAR SE MIGRAÇÃO JÁ FOI APLICADA
// =============================================================================
const migrationVersion = "2025-12-06_001000";
const existingMigration = db.migrations.findOne({ version: migrationVersion });

if (existingMigration) {
  print(
    `⚠️ [SKIP] Migração ${migrationVersion} já foi aplicada em ${existingMigration.applied_at}`
  );
  quit();
}

// =============================================================================
// 🔄 ATUALIZAÇÃO DE DOCUMENTOS EXISTENTES
// =============================================================================

print("📦 [BACKUP] Criando backup de documentos existentes...");
const backupCollection = "analyze_documents_backup_" + new Date().getTime();
db.analyze_documents.aggregate([{ $match: {} }, { $out: backupCollection }]);
const backupCount = db[backupCollection].countDocuments();
print(
  `✅ [BACKUP] ${backupCount} documentos copiados para '${backupCollection}'`
);

print("🔄 [UPDATE] Adicionando file_size aos documentos existentes...");
const updateResult = db.analyze_documents.updateMany(
  { file_size: { $exists: false } },
  { $set: { file_size: 0 } }
);
print(
  `✅ [UPDATE] ${updateResult.modifiedCount} documentos atualizados com file_size=0`
);
print(
  "ℹ️ [INFO] Documentos antigos preservados. file_size=0 indica documento anterior à migration."
);

// =============================================================================
// 🎯 CRIAÇÃO DE ÍNDICES
// =============================================================================

print("📊 [INDEX] Criando índice composto para verificação de duplicatas...");

// Verificar se índice já existe
const existingIndexes = db.analyze_documents.getIndexes();
const duplicateIndexExists = existingIndexes.some(
  (idx) => idx.name === "idx_duplicate_check"
);

if (!duplicateIndexExists) {
  db.analyze_documents.createIndex(
    {
      user_email: 1,
      file_name: 1,
      file_size: 1,
    },
    {
      name: "idx_duplicate_check",
      background: false, // Seguro para desenvolvimento (collection vazia)
    }
  );
  print("✅ [INDEX] Índice composto 'idx_duplicate_check' criado com sucesso");
  print("   Campos: user_email (1), file_name (1), file_size (1)");
} else {
  print("ℹ️ [INDEX] Índice 'idx_duplicate_check' já existe");
}

// =============================================================================
// 📝 REGISTRAR MIGRAÇÃO
// =============================================================================

print("📝 [REGISTRO] Registrando migração aplicada...");
db.migrations.insertOne({
  version: migrationVersion,
  description: "Adicionar campo file_size e índice de duplicatas",
  applied_at: new Date(),
  backup_collection: backupCollection,
  documents_updated: updateResult.modifiedCount,
  notes:
    "Documentos antigos foram preservados com file_size=0. Backup criado em " +
    backupCollection +
    ". Novos documentos incluirão file_size calculado.",
});

// =============================================================================
// ✅ VALIDAÇÃO FINAL
// =============================================================================

print("\n🔍 [VALIDAÇÃO] Verificando estado final:");
print(
  `   - Documentos na coleção principal: ${db.analyze_documents.countDocuments()}`
);
print(`   - Documentos no backup: ${backupCount}`);
print(
  `   - Índices criados: ${db.analyze_documents.getIndexes().length} total`
);

// Listar todos os índices
print("\n📋 [ÍNDICES] Lista completa de índices:");
db.analyze_documents.getIndexes().forEach((idx) => {
  print(`   - ${idx.name}: ${JSON.stringify(idx.key)}`);
});

print("\n✅ [SUCCESS] Migração 2025-12-06_001000 aplicada com sucesso!");
print(`💾 [BACKUP] Documentos antigos salvos em: ${backupCollection}`);
print("🎯 [READY] Sistema pronto para verificação de duplicatas");
