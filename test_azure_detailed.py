#!/usr/bin/env python3
"""
Teste detalhado para Azure AI Document Intelligence
Para diagnosticar problemas de processamento de páginas
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.core.exceptions import DocumentProcessingError

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('azure_test.log')
    ]
)

# Carregar variáveis de ambiente
load_dotenv()

async def test_azure_detailed():
    """Testa Azure AI com logging detalhado"""
    
    print("=" * 80)
    print("🔍 TESTE DETALHADO: Azure AI Document Intelligence")
    print("=" * 80)
    
    # Verificar se as variáveis de ambiente estão configuradas
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    model = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL")
    
    print(f"📍 Endpoint: {endpoint}")
    print(f"🔑 Key: {key[:20]}..." if key else "❌ Key não encontrada")
    print(f"🤖 Model: {model}")
    
    # Testar arquivo de exemplo
    test_file = Path("tests/modelo-prova-completa.pdf")
    
    if not test_file.exists():
        print(f"❌ ERRO: Arquivo de teste não encontrado: {test_file}")
        return False
    
    file_size = test_file.stat().st_size
    print(f"📄 Arquivo: {test_file}")
    print(f"📏 Tamanho: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    try:
        # Simular um UploadFile
        class MockUploadFile:
            def __init__(self, file_path):
                self.filename = file_path.name
                self.content_type = "application/pdf"
                self._file_path = file_path
            
            async def read(self):
                with open(self._file_path, 'rb') as f:
                    return f.read()
            
            async def seek(self, position):
                pass
        
        mock_file = MockUploadFile(test_file)
        
        print("\n" + "=" * 80)
        print("🚀 INICIANDO PROCESSAMENTO AZURE AI")
        print("=" * 80)
        
        # Testar Azure AI
        azure_service = AzureDocumentIntelligenceService()
        
        result = await azure_service.analyze_document(mock_file)
        
        print("\n" + "=" * 80)
        print("✅ RESULTADO DO PROCESSAMENTO")
        print("=" * 80)
        
        print(f"📄 Texto extraído: {len(result['text'])} caracteres")
        print(f"📊 Confiança: {result.get('confidence', 0):.2f}")
        print(f"📃 Páginas processadas: {result.get('page_count', 0)}")
        print(f"🔢 Total de linhas: {result.get('total_lines', 0)}")
        print(f"🗂️ Tabelas: {len(result.get('tables', []))}")
        print(f"📝 Parágrafos: {len(result.get('paragraphs', []))}")
        print(f"🆔 Operation ID: {result.get('operation_id', 'N/A')}")
        
        # Estatísticas de processamento
        if 'processing_stats' in result:
            stats = result['processing_stats']
            print(f"\n📈 ESTATÍSTICAS DE PROCESSAMENTO:")
            print(f"   ⏱️ Tempo: {stats.get('processing_time_seconds', 0):.2f} segundos")
            print(f"   📄 Páginas/segundo: {stats.get('pages_per_second', 0):.2f}")
            print(f"   📝 Linhas/segundo: {stats.get('lines_per_second', 0):.2f}")
            print(f"   📊 Palavras totais: {stats.get('total_words', 0)}")
            print(f"   📝 Caracteres totais: {stats.get('total_characters', 0)}")
        
        # Informações por página
        if 'pages_info' in result:
            print(f"\n📋 INFORMAÇÕES POR PÁGINA:")
            for page_info in result['pages_info']:
                print(f"   📄 Página {page_info['page_number']}: {page_info['lines_count']} linhas, {page_info['words_count']} palavras")
                if page_info.get('text_sample'):
                    print(f"      🔍 Amostra: {page_info['text_sample'][:100]}...")
        
        # Mostrar um trecho do texto
        if result['text']:
            print(f"\n📖 PRIMEIROS 300 CARACTERES DO TEXTO:")
            print("-" * 60)
            print(result['text'][:300])
            print("-" * 60)
        
        # Mostrar estrutura das tabelas
        if result.get('tables'):
            print(f"\n🗂️ ESTRUTURA DAS TABELAS:")
            for i, table in enumerate(result['tables']):
                print(f"   Tabela {i+1}: {table['row_count']} linhas x {table['column_count']} colunas")
                if table.get('cells'):
                    print(f"      📊 Células: {len(table['cells'])}")
                    # Mostrar algumas células
                    for j, cell in enumerate(table['cells'][:5]):  # Primeiras 5 células
                        content = cell.get('content', '')[:30]
                        print(f"         Célula {j+1}: [{cell.get('row_index', 0)},{cell.get('column_index', 0)}] = {content}")
        
        return True
        
    except DocumentProcessingError as e:
        print(f"❌ ERRO DocumentProcessingError: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO Exceção: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        return False

async def main():
    success = await test_azure_detailed()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("   Verifique os logs em 'azure_test.log' para detalhes completos")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique os logs em 'azure_test.log' para diagnóstico")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
