#!/usr/bin/env python3
"""
Script para comparar fluxo do endpoint principal vs mock
"""

import sys
from pathlib import Path
import logging
import asyncio

# Configurar ambiente
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def compare_flows():
    """Compara o fluxo do endpoint principal vs mock"""
    
    print("🔍 COMPARAÇÃO: ENDPOINT PRINCIPAL vs MOCK")
    print("=" * 60)
    
    try:
        # 1. TESTAR FLUXO MOCK (que sabemos que funciona)
        print("\n📄 1. TESTANDO FLUXO MOCK...")
        
        from app.services.analyze_service import AnalyzeService
        
        mock_response = await AnalyzeService.process_document_with_models_mock()
        
        print(f"✅ Mock - Questions: {len(mock_response.questions)}")
        
        if mock_response.questions:
            q = mock_response.questions[0]
            print(f"✅ Mock Q1 - Statement: '{q.content.statement[:100]}...'")
            print(f"✅ Mock Q1 - Options: {len(q.options)}")
        
        # 2. SIMULAR FLUXO DO ENDPOINT PRINCIPAL
        print("\n📄 2. SIMULANDO FLUXO DO ENDPOINT PRINCIPAL...")
        
        # Vamos simular o mesmo que o endpoint principal faz:
        # 1. DocumentExtractionService.get_extraction_data() -> cache
        # 2. AnalyzeService.process_document_with_models()
        
        from app.services.azure_response_service import AzureResponseService
        
        # Simular extracted_data como seria no endpoint principal
        azure_result = AzureResponseService.get_latest_azure_response()
        file_info = AzureResponseService.get_latest_file_info()
        extracted_data = AzureResponseService.convert_azure_response_to_extracted_data(azure_result)
        
        print(f"✅ Extracted data - Text: {len(extracted_data.get('text', ''))} chars")
        print(f"✅ Extracted data - Images: {len(extracted_data.get('image_data', {}))}")
        print(f"✅ Extracted data - Metadata: {bool(extracted_data.get('metadata'))}")
        
        # Criar um mock file object
        class MockFile:
            def __init__(self, filename):
                self.filename = filename
            
            async def seek(self, pos):
                pass
        
        mock_file = MockFile(file_info['filename'])
        
        # Simular o fluxo do endpoint principal
        print("\n🔧 3. EXECUTANDO process_document_with_models (fluxo principal)...")
        
        principal_response = await AnalyzeService.process_document_with_models(
            extracted_data=extracted_data,
            email="test@principal.com",
            filename=file_info['filename'],
            file=mock_file,
            use_refactored=True
        )
        
        print(f"✅ Principal - Questions: {len(principal_response.questions)}")
        
        if principal_response.questions:
            q = principal_response.questions[0]
            print(f"✅ Principal Q1 - Statement: '{q.content.statement[:100]}...'")
            print(f"✅ Principal Q1 - Options: {len(q.options)}")
        else:
            print("❌ PROBLEMA: Endpoint principal retornou 0 questões!")
        
        # 4. COMPARAR CONVERSÃO DTO
        print("\n📄 4. TESTANDO CONVERSÃO DTO...")
        
        from app.dtos.responses.document_response_dto import DocumentResponseDTO
        
        # Mock DTO
        mock_dto = DocumentResponseDTO.from_internal_response(mock_response)
        print(f"✅ Mock DTO - Questions: {len(mock_dto.questions)}")
        
        if mock_dto.questions:
            q = mock_dto.questions[0]
            print(f"✅ Mock DTO Q1 - Question: '{q.question[:100]}...'")
            print(f"✅ Mock DTO Q1 - Alternatives: {len(q.alternatives)}")
        
        # Principal DTO
        principal_dto = DocumentResponseDTO.from_internal_response(principal_response)
        print(f"✅ Principal DTO - Questions: {len(principal_dto.questions)}")
        
        if principal_dto.questions:
            q = principal_dto.questions[0]
            print(f"✅ Principal DTO Q1 - Question: '{q.question[:100]}...'")
            print(f"✅ Principal DTO Q1 - Alternatives: {len(q.alternatives)}")
        else:
            print("❌ PROBLEMA: Principal DTO tem 0 questões!")
        
        # 5. IDENTIFICAR DIFERENÇAS
        print("\n📊 5. ANÁLISE DAS DIFERENÇAS:")
        
        print(f"  Mock questions: {len(mock_response.questions)}")
        print(f"  Principal questions: {len(principal_response.questions)}")
        
        if len(mock_response.questions) != len(principal_response.questions):
            print("🚨 DIFERENÇA ENCONTRADA: Número de questões diferente!")
            
            print("\n🔍 DEBUG: Verificando extracted_data do principal...")
            
            # Verificar se o problema está nos parágrafos Azure
            metadata = extracted_data.get('metadata', {})
            raw_response = metadata.get('raw_response', {})
            paragraphs = raw_response.get('paragraphs', [])
            
            print(f"  📋 Parágrafos Azure: {len(paragraphs)}")
            
            # Verificar se há questões nos parágrafos
            question_paragraphs = []
            for i, p in enumerate(paragraphs):
                if 'QUESTÃO' in p.get('content', '').upper():
                    question_paragraphs.append(i)
            
            print(f"  🎯 Parágrafos com QUESTÃO: {len(question_paragraphs)}")
            
            if len(question_paragraphs) == 0:
                print("🚨 PROBLEMA IDENTIFICADO: Nenhum parágrafo contém 'QUESTÃO'!")
                print("   Isso indica que o extracted_data do principal está diferente do mock.")
        
        
    except Exception as e:
        print(f"💥 ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(compare_flows())
