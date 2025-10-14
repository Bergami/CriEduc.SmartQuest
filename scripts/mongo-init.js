// SmartQuest MongoDB Initialization Script
// Executed when MongoDB container starts for the first time

// Switch to smartquest database
db = db.getSiblingDB("smartquest");

// Create collection analyzeDocuments with proper naming
db.createCollection("analyzeDocuments");

// Create optimized indexes for common queries
print("Creating indexes for analyzeDocuments collection...");

// Index for user queries (most common: find by user + sort by date)
db.analyzeDocuments.createIndex({ userEmail: 1, createdAt: -1 });
print("✅ Index created: userEmail + createdAt (compound)");

// Index for date-based queries (admin dashboards)
db.analyzeDocuments.createIndex({ createdAt: -1 });
print("✅ Index created: createdAt (descending)");

// Index for filename searches
db.analyzeDocuments.createIndex({ fileName: 1 });
print("✅ Index created: fileName");

// Unique index for document ID (business key)
db.analyzeDocuments.createIndex({ documentId: 1 }, { unique: true });
print("✅ Index created: documentId (unique)");

// Create a sample document to validate structure
var sampleDoc = {
  documentId: "sample_doc_" + new Date().getTime(),
  createdAt: new Date(),
  userEmail: "admin@smartquest.com.br",
  fileName: "sample_initialization.pdf",
  response: {
    document_id: "sample_doc_" + new Date().getTime(),
    metadata: {
      pages: 1,
      language: "pt-BR",
    },
    api_version: "2.0",
    processed_at: new Date().toISOString(),
  },
};

// Insert sample document
db.analyzeDocuments.insertOne(sampleDoc);
print("✅ Sample document inserted for validation");

// Display collection stats
var stats = db.analyzeDocuments.stats();
print("📊 Collection Stats:");
print("   - Documents: " + stats.count);
print("   - Indexes: " + stats.nindexes);
print("   - Size: " + stats.size + " bytes");

print("🎉 SmartQuest MongoDB initialized successfully!");
print("📋 Collection: analyzeDocuments");
print("📋 Database: smartquest");
print("📋 Indexes: 4 (userEmail+createdAt, createdAt, fileName, documentId)");
