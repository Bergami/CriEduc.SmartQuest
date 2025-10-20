// =============================================================================
// 🍃 INICIALIZAÇÃO DO BANCO DE DADOS SMARTQUEST
// =============================================================================
// Script de inicialização do MongoDB para desenvolvimento local
// Executado automaticamente pelo Docker Compose durante container startup

// Selecionar a base de dados smartquest
print("🚀 Iniciando configuração da base de dados 'smartquest'...");
db = db.getSiblingDB("smartquest");

// =============================================================================
// 📊 CRIAÇÃO DAS COLEÇÕES CONFORME PROMPT ORIGINAL
// =============================================================================

// 1. COLEÇÃO: analyze_documents (conforme prompt original)
print("📄 Criando coleção 'analyze_documents'...");
db.createCollection("analyze_documents");

// 2. COLEÇÃO: azure_processing_data (dados específicos Azure + métricas)
print("🔷 Criando coleção 'azure_processing_data'...");
db.createCollection("azure_processing_data");

// =============================================================================
// 🎯 CRIAÇÃO DE ÍNDICES PARA PERFORMANCE
// =============================================================================

print("🔍 Criando índices para otimização de consultas...");

// Índices para analyze_documents
db.analyze_documents.createIndex({ user_email: 1 }, { name: "idx_user_email" });
db.analyze_documents.createIndex(
  { created_at: -1 },
  { name: "idx_created_at_desc" }
);
db.analyze_documents.createIndex({ status: 1 }, { name: "idx_status" });
db.analyze_documents.createIndex(
  { user_email: 1, created_at: -1 },
  { name: "idx_user_email_created_at" }
);

// Índices para azure_processing_data
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

print("✅ Índices criados com sucesso!");

// =============================================================================
// 📝 INSERÇÃO DE DADOS DE EXEMPLO
// =============================================================================

print("📝 Inserindo documentos de exemplo...");

// Documento de exemplo para analyze_documents (conforme AnalyzeDocumentRecord)
const sampleAnalyzeDocument = {
  _id: "123e4567-e89b-12d3-a456-426614174000", // GUID conforme BaseDocument
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
        alternatives: ["Objetivo A", "Objetivo B", "Objetivo C", "Objetivo D"],
      },
    ],
  },
  status: "completed",
  created_at: new Date(),
};

db.analyze_documents.insertOne(sampleAnalyzeDocument);

// Documento de exemplo para azure_processing_data (conforme AzureProcessingDataRecord)
const sampleAzureData = {
  _id: "456f7890-a12b-34c5-d678-901234567890", // GUID conforme BaseDocument
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

print("✅ Documentos de exemplo inseridos!");

// =============================================================================
// 🎉 CONFIRMAÇÃO FINAL
// =============================================================================

print("📊 Resumo da configuração:");
print(`- Base de dados: ${db.getName()}`);
print(`- Coleções criadas: ${db.getCollectionNames().length}`);
print(
  `- analyze_documents: ${db.analyze_documents.countDocuments()} documentos`
);
print(
  `- azure_processing_data: ${db.azure_processing_data.countDocuments()} documentos`
);

print("🎉 Configuração do MongoDB SmartQuest concluída com sucesso!");
print("🔗 Pronto para receber conexões da aplicação.");

// =============================================================================
// 📋 ESTRUTURA FINAL CONFORME MODELOS PYDANTIC:
//
// Collections (Coleções):
// ✅ analyze_documents - plural, snake_case (AnalyzeDocumentRecord)
// ✅ azure_processing_data - descritivo, snake_case (AzureProcessingDataRecord)
//
// analyze_documents campos:
// ✅ _id (GUID), created_at, user_email, file_name, response, status
//
// azure_processing_data campos:
// ✅ _id (GUID), created_at, operation_id, model_id, api_version, response, metrics
//
// Nomenclatura MongoDB:
// ✅ Sem espaços, caracteres especiais
// ✅ snake_case consistente
// ✅ Nomes descritivos e específicos
// =============================================================================
