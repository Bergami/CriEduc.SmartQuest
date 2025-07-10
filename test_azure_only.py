#!/usr/bin/env python3
"""
Script para testar a integração apenas com Azure AI Document Intelligence
Sem dependência do pdfplumber
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.core.exceptions import DocumentProcessingError

# Carregar variáveis de ambiente
load_dotenv()

async def test_azure_only():
    """Testa a integração apenas com Azure AI"""
    
    print("🔍 TESTE: Azure AI Document Intelligence (sem pdfplumber)")
    print("=" * 60)
    
    # Verificar se as variáveis de ambiente estão configuradas
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not key:
        print("❌ ERRO: Variáveis de ambiente Azure não configuradas")
        print("   Configure AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT e AZURE_DOCUMENT_INTELLIGENCE_KEY")
        return False
    
    print(f"✅ Endpoint: {endpoint}")
    print(f"✅ Key: {key[:10]}...")
    
    # Testar arquivo de exemplo
    test_file = Path("tests/modelo-prova-completa.pdf")
    
    if not test_file.exists():
        print(f"❌ ERRO: Arquivo de teste não encontrado: {test_file}")
        return False
    
    print(f"✅ Arquivo de teste: {test_file}")
    
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
        
        # Testar Azure AI
        print("\n🔍 TESTE: Processando modelo-prova-completa.pdf com Azure AI...")
        azure_service = AzureDocumentIntelligenceService()
        
        result = await azure_service.analyze_document(mock_file)
        
        print("✅ SUCESSO: Azure AI processou o documento!")
        print(f"   - Texto extraído: {len(result['text'])} caracteres")
        print(f"   - Confiança: {result.get('confidence', 0)}")
        print(f"   - Páginas: {result.get('page_count', 0)}")
        print(f"   - Tabelas: {len(result.get('tables', []))}")
        
        # Mostrar um trecho do texto
        if result['text']:
            print(f"\n📄 Primeiros 200 caracteres do texto:")
            print(result['text'][:200])
            print("...")
        
        return True
        
    except DocumentProcessingError as e:
        print(f"❌ ERRO: DocumentProcessingError: {e.message}")
        return False
    except Exception as e:
        print(f"❌ ERRO: Exceção não tratada: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        return False

async def main():
    success = await test_azure_only()
    
    if success:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("   O projeto está configurado para usar apenas Azure AI")
    else:
        print("\n❌ TESTE FALHOU!")
        print("   Verifique as configurações do Azure AI")

if __name__ == "__main__":
    asyncio.run(main())
