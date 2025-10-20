// =============================================================================
// 🗄️ MIGRATION: Remover Coleção Duplicada analyzeDocuments
// =============================================================================
// Versão: 2025-10-18_001000
// Descrição: Remove coleção analyzeDocuments (camelCase) duplicada
// Autor: Sistema MongoDB Persistence
// Data: 2025-10-18

print("🚀 [MIGRATION] Iniciando: remove_duplicate_analyze_documents_collection");

// Conectar à base de dados
db = db.getSiblingDB("smartquest");

// =============================================================================
// ✅ VERIFICAR SE MIGRAÇÃO JÁ FOI APLICADA
// =============================================================================
const migrationVersion = "2025-10-18_001000";
const existingMigration = db.migrations.findOne({ version: migrationVersion });

if (existingMigration) {
  print(
    `⚠️ [SKIP] Migração ${migrationVersion} já foi aplicada em ${existingMigration.applied_at}`
  );
  quit();
}

// =============================================================================
// 🔄 VERIFICAR ESTADO ATUAL
// =============================================================================

print("📊 Verificando estado atual das coleções...");

const collections = db.getCollectionNames();
const hasAnalyzeDocumentsCamel = collections.includes("analyzeDocuments");
const hasAnalyzeDocumentsSnake = collections.includes("analyze_documents");

print(`- analyzeDocuments (camelCase): ${hasAnalyzeDocumentsCamel ? "EXISTE" : "NÃO EXISTE"}`);
print(`- analyze_documents (snake_case): ${hasAnalyzeDocumentsSnake ? "EXISTE" : "NÃO EXISTE"}`);

if (hasAnalyzeDocumentsCamel) {
  const camelCaseCount = db.analyzeDocuments.countDocuments();
  print(`- Documentos em analyzeDocuments: ${camelCaseCount}`);
  
  if (camelCaseCount > 0) {
    print("⚠️ ATENÇÃO: analyzeDocuments contém dados!");
    print("🔄 Migrando dados para analyze_documents antes de remover...");
    
    // Migrar dados se existirem
    const docs = db.analyzeDocuments.find().toArray();
    if (docs.length > 0) {
      const insertResult = db.analyze_documents.insertMany(docs);
      print(`✅ ${insertResult.insertedIds.length} documentos migrados para analyze_documents`);
    }
  }
  
  // Remover a coleção duplicada
  print("🗑️ Removendo coleção analyzeDocuments...");
  db.analyzeDocuments.drop();
  print("✅ Coleção analyzeDocuments removida com sucesso");
} else {
  print("ℹ️ Coleção analyzeDocuments já não existe, nada a fazer");
}

if (hasAnalyzeDocumentsSnake) {
  const snakeCaseCount = db.analyze_documents.countDocuments();
  print(`✅ analyze_documents possui ${snakeCaseCount} documentos`);
} else {
  print("⚠️ Coleção analyze_documents não existe! Criando...");
  db.createCollection("analyze_documents");
  print("✅ Coleção analyze_documents criada");
}

// =============================================================================
// 📋 REGISTRAR MIGRAÇÃO APLICADA
// =============================================================================

print("📋 Registrando migração aplicada...");
db.migrations.insertOne({
  version: migrationVersion,
  name: "remove_duplicate_analyze_documents_collection",
  description: "Remove coleção analyzeDocuments (camelCase) duplicada, mantendo apenas analyze_documents (snake_case)",
  applied_at: new Date(),
  script_file: "2025-10-18_001000_remove_duplicate_analyze_documents_collection.js"
});

// =============================================================================
// 🎉 RESUMO FINAL
// =============================================================================

print("📊 Estado final das coleções:");
const finalCollections = db.getCollectionNames();
finalCollections.forEach(collection => {
  if (collection.startsWith("analyze")) {
    const count = db.getCollection(collection).countDocuments();
    print(`  ✅ ${collection}: ${count} documentos`);
  }
});

print("🎉 [SUCCESS] Migração remove_duplicate_analyze_documents_collection aplicada com sucesso!");