# ==============================================================================
# 🧪 Script de Teste da Migration - file_size
# ==============================================================================
# Descrição: Testa migration em banco local ANTES de aplicar em produção
# Uso: .\scripts\test_migration.ps1
# Pré-requisitos: MongoDB rodando localmente, mongosh instalado

Write-Host "`n🧪 [TEST] Iniciando teste de migration..." -ForegroundColor Cyan

# ==============================================================================
# 1. VERIFICAR PRÉ-REQUISITOS
# ==============================================================================

Write-Host "`n📋 [CHECK] Verificando pré-requisitos..." -ForegroundColor Yellow

# Verificar se MongoDB está rodando
try {
    $mongoCheck = mongosh --quiet --eval "db.version()" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "MongoDB não está respondendo"
    }
    Write-Host "✅ MongoDB: $mongoCheck" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: MongoDB não está rodando!" -ForegroundColor Red
    Write-Host "   Execute: docker-compose up -d mongodb" -ForegroundColor Yellow
    exit 1
}

# ==============================================================================
# 2. CRIAR BANCO DE TESTE
# ==============================================================================

Write-Host "`n🗄️ [SETUP] Criando banco de teste..." -ForegroundColor Yellow

$testDb = "smartquest_test_migration"

# Limpar banco de teste anterior (se existir)
mongosh --quiet --eval "use $testDb; db.dropDatabase();" | Out-Null

# Criar documentos de teste
$testData = @"
use $testDb;

// Inserir documentos de teste (sem file_size)
db.analyze_documents.insertMany([
  {
    user_email: 'test1@example.com',
    file_name: 'documento1.pdf',
    status: 'COMPLETED',
    response: { questions: [] },
    created_at: new Date('2025-01-01')
  },
  {
    user_email: 'test2@example.com',
    file_name: 'documento2.pdf',
    status: 'FAILED',
    response: { error: 'Erro de teste' },
    created_at: new Date('2025-02-01')
  },
  {
    user_email: 'test3@example.com',
    file_name: 'documento3.pdf',
    status: 'COMPLETED',
    response: { questions: [] },
    created_at: new Date('2025-03-01')
  }
]);

print('✅ Documentos de teste criados: ' + db.analyze_documents.countDocuments());
"@

$testData | mongosh --quiet

Write-Host "✅ 3 documentos de teste criados" -ForegroundColor Green

# ==============================================================================
# 3. EXECUTAR MIGRATION
# ==============================================================================

Write-Host "`n🔄 [MIGRATION] Executando migration no banco de teste..." -ForegroundColor Yellow

# Copiar migration e ajustar para banco de teste
$migrationScript = Get-Content -Path ".\scripts\migrations\2025-12-06_001000_add_file_size_and_duplicate_index.js" -Raw
$testMigrationScript = $migrationScript -replace 'db.getSiblingDB\("smartquest"\)', "db.getSiblingDB(`"$testDb`")"

# Salvar script temporário
$tempScript = ".\scripts\temp_test_migration.js"
$testMigrationScript | Out-File -FilePath $tempScript -Encoding UTF8

# Executar migration
mongosh --quiet $tempScript

# Remover script temporário
Remove-Item $tempScript

# ==============================================================================
# 4. VALIDAR RESULTADOS
# ==============================================================================

Write-Host "`n🔍 [VALIDATION] Validando resultados..." -ForegroundColor Yellow

$validation = @"
use $testDb;

print('\n📊 Resultados da Validação:');
print('================================');

// 1. Verificar que documentos NÃO foram deletados
const totalDocs = db.analyze_documents.countDocuments();
print('✅ Total de documentos: ' + totalDocs + ' (esperado: 3)');

if (totalDocs !== 3) {
  print('❌ ERRO: Documentos foram deletados!');
} else {
  print('✅ PASSOU: Todos os documentos preservados');
}

// 2. Verificar que file_size foi adicionado
const docsWithFileSize = db.analyze_documents.countDocuments({ file_size: { \$exists: true } });
print('✅ Documentos com file_size: ' + docsWithFileSize + ' (esperado: 3)');

if (docsWithFileSize !== 3) {
  print('❌ ERRO: Nem todos os documentos têm file_size!');
} else {
  print('✅ PASSOU: Todos os documentos têm file_size');
}

// 3. Verificar que file_size = 0 para docs antigos
const docsWithZeroSize = db.analyze_documents.countDocuments({ file_size: 0 });
print('✅ Documentos com file_size=0: ' + docsWithZeroSize + ' (esperado: 3)');

if (docsWithZeroSize !== 3) {
  print('❌ ERRO: file_size deveria ser 0 para todos!');
} else {
  print('✅ PASSOU: file_size=0 para documentos antigos');
}

// 4. Verificar que índice foi criado
const indexes = db.analyze_documents.getIndexes();
const duplicateIndex = indexes.find(idx => idx.name === 'idx_duplicate_check');

if (!duplicateIndex) {
  print('❌ ERRO: Índice idx_duplicate_check não foi criado!');
} else {
  print('✅ PASSOU: Índice idx_duplicate_check criado');
  print('   Campos: ' + JSON.stringify(duplicateIndex.key));
}

// 5. Verificar que backup foi criado
const collections = db.getCollectionNames();
const backupExists = collections.some(col => col.startsWith('analyze_documents_backup_'));

if (!backupExists) {
  print('❌ ERRO: Backup não foi criado!');
} else {
  const backupCol = collections.find(col => col.startsWith('analyze_documents_backup_'));
  const backupCount = db[backupCol].countDocuments();
  print('✅ PASSOU: Backup criado com ' + backupCount + ' documentos');
}

// 6. Verificar registro da migration
const migrationRecord = db.migrations.findOne({ version: '2025-12-06_001000' });

if (!migrationRecord) {
  print('❌ ERRO: Migration não foi registrada!');
} else {
  print('✅ PASSOU: Migration registrada');
  print('   Documentos atualizados: ' + migrationRecord.documents_updated);
}

print('\n================================');
"@

$validation | mongosh --quiet

# ==============================================================================
# 5. LIMPEZA
# ==============================================================================

Write-Host "`n🧹 [CLEANUP] Deseja remover banco de teste? (S/N)" -ForegroundColor Yellow
$cleanup = Read-Host "Resposta"

if ($cleanup -eq 'S' -or $cleanup -eq 's') {
    mongosh --quiet --eval "use $testDb; db.dropDatabase();" | Out-Null
    Write-Host "✅ Banco de teste removido" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Banco de teste mantido: $testDb" -ForegroundColor Cyan
    Write-Host "   Para remover: mongosh --eval 'use $testDb; db.dropDatabase();'" -ForegroundColor Gray
}

# ==============================================================================
# 6. RESULTADO FINAL
# ==============================================================================

Write-Host "`n✅ [SUCCESS] Teste de migration concluído!" -ForegroundColor Green
Write-Host @"

📝 Próximos Passos:
==================
1. ✅ Se todos os testes passaram, a migration está segura
2. ⏳ Fazer backup de produção ANTES de aplicar: mongodump --db smartquest
3. ⏳ Aplicar migration em produção: mongosh scripts/migrations/2025-12-06_001000_add_file_size_and_duplicate_index.js
4. ⏳ Validar em produção com os mesmos testes
5. ✅ Commit: git commit -m "fix: Preservar documentos antigos na migration de file_size"

"@ -ForegroundColor Cyan
