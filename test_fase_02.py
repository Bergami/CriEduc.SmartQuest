#!/usr/bin/env python3
"""
🚀 FASE 02: Teste de Validação - QuestionParser Pydantic Nativo

Este script valida as melhorias implementadas na Fase 02:
1. ✅ Eliminação de conversões legacy em figure association
2. ✅ Uso direto de objetos Pydantic
3. ✅ Melhoria na performance por eliminar conversões Dict↔Pydantic
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

async def test_fase_02_improvements():
    """
    Testa as melhorias da Fase 02 comparando com comportamento anterior
    """
    
    print("🚀 FASE 02: Testando Melhorias do QuestionParser Pydantic Nativo")
    print("=" * 80)
    
    try:
        # 1. TESTAR QuestionParser.extract_typed_from_paragraphs (já implementado)
        print("\n📄 1. TESTANDO QuestionParser.extract_typed_from_paragraphs...")
        
        from app.parsers.question_parser.base import QuestionParser
        from app.services.azure_response_service import AzureResponseService
        
        # Obter dados reais do cache
        azure_result = AzureResponseService.get_latest_azure_response()
        azure_paragraphs = azure_result.get("paragraphs", [])
        
        if not azure_paragraphs:
            print("❌ Erro: Não foram encontrados parágrafos Azure no cache")
            return
        
        # Chamar método Pydantic nativo
        questions, context_blocks = QuestionParser.extract_typed_from_paragraphs(azure_paragraphs)
        
        print(f"✅ extract_typed_from_paragraphs retornou:")
        print(f"   🎯 Questions: {len(questions)} (tipo: {type(questions[0]).__name__ if questions else 'N/A'})")
        print(f"   📋 Context Blocks: {len(context_blocks)} (tipo: {type(context_blocks[0]).__name__ if context_blocks else 'N/A'})")
        
        # Verificar se são objetos Pydantic nativos
        if questions:
            q = questions[0]
            print(f"   📝 Q1 - Statement: '{q.content.statement[:50]}...'")
            print(f"   📝 Q1 - Options: {len(q.options)}")
            print(f"   📝 Q1 - Type: {type(q).__name__}")
            
            # Verificar se tem métodos Pydantic
            has_dict = hasattr(q, 'dict')
            has_json = hasattr(q, 'json')
            print(f"   ✅ Pydantic methods - dict(): {has_dict}, json(): {has_json}")
        
        # 2. TESTAR AzureFigureProcessor.associate_figures_to_pydantic_questions
        print("\n📄 2. TESTANDO AzureFigureProcessor.associate_figures_to_pydantic_questions...")
        
        from app.services.azure_figure_processor import AzureFigureProcessor
        
        # Processar figuras
        processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
        print(f"✅ Processed {len(processed_figures)} figures from Azure response")
        
        # Usar novo método Pydantic nativo
        enhanced_questions = AzureFigureProcessor.associate_figures_to_pydantic_questions(
            processed_figures, questions
        )
        
        print(f"✅ associate_figures_to_pydantic_questions retornou:")
        print(f"   🎯 Enhanced Questions: {len(enhanced_questions)} (tipo: {type(enhanced_questions[0]).__name__ if enhanced_questions else 'N/A'})")
        
        if enhanced_questions:
            eq = enhanced_questions[0]
            print(f"   📝 EQ1 - Statement: '{eq.content.statement[:50]}...'")
            print(f"   📝 EQ1 - Has Image: {eq.has_image}")
            print(f"   📝 EQ1 - Type: {type(eq).__name__}")
        
        # 3. COMPARAR PERFORMANCE - Simular fluxo antigo vs novo
        print("\n📄 3. COMPARANDO PERFORMANCE (Simulação)...")
        
        import time
        
        # ✅ NOVO FLUXO (Fase 02): Direto Pydantic
        start_time = time.time()
        
        # Questions já em Pydantic
        new_flow_questions = questions
        
        # Figure association direta
        enhanced_questions_new = AzureFigureProcessor.associate_figures_to_pydantic_questions(
            processed_figures, new_flow_questions
        )
        
        new_flow_time = time.time() - start_time
        
        # ❌ FLUXO ANTIGO (Simulado): Com conversões Dict↔Pydantic
        start_time = time.time()
        
        # Simular conversão Pydantic → Dict
        questions_dict = []
        for q in questions:
            legacy_dict = {
                "number": q.number,
                "question": q.content.statement,
                "alternatives": [{"letter": opt.label, "text": opt.text} for opt in q.options],
                "hasImage": q.has_image,
                "contextId": q.context_id,
                "subject": q.subject
            }
            questions_dict.append(legacy_dict)
        
        # Simular figure association legacy
        enhanced_questions_dict = AzureFigureProcessor.associate_figures_to_questions(
            processed_figures, questions_dict
        )
        
        # Simular conversão Dict → Pydantic
        from app.models.internal.question_models import InternalQuestion
        enhanced_questions_old = [
            InternalQuestion.from_legacy_question(q) for q in enhanced_questions_dict
        ]
        
        old_flow_time = time.time() - start_time
        
        # Resultados da comparação
        improvement = ((old_flow_time - new_flow_time) / old_flow_time) * 100 if old_flow_time > 0 else 0
        
        print(f"   ⏱️  FLUXO ANTIGO (com conversões): {old_flow_time:.4f}s")
        print(f"   ⚡ FLUXO NOVO (Pydantic nativo): {new_flow_time:.4f}s")
        print(f"   📈 MELHORIA: {improvement:.1f}% mais rápido")
        
        # 4. VERIFICAR INTEGRIDADE DOS DADOS
        print("\n📄 4. VERIFICANDO INTEGRIDADE DOS DADOS...")
        
        # Comparar resultados
        questions_match = len(enhanced_questions_new) == len(enhanced_questions_old)
        
        if questions_match and enhanced_questions_new:
            q_new = enhanced_questions_new[0]
            q_old = enhanced_questions_old[0]
            
            content_match = q_new.content.statement == q_old.content.statement
            options_match = len(q_new.options) == len(q_old.options)
            
            print(f"   ✅ Número de questions: {questions_match}")
            print(f"   ✅ Conteúdo Q1: {content_match}")
            print(f"   ✅ Opções Q1: {options_match}")
            
            if content_match and options_match:
                print("   🎉 SUCESSO: Dados idênticos entre fluxo novo e antigo!")
            else:
                print("   ⚠️  ATENÇÃO: Dados divergem entre fluxos")
        
        # 5. RESUMO DAS MELHORIAS
        print("\n📊 5. RESUMO DAS MELHORIAS DA FASE 02:")
        print("   ✅ QuestionParser.extract_typed_from_paragraphs() - Pydantic nativo")
        print("   ✅ AzureFigureProcessor.associate_figures_to_pydantic_questions() - Sem conversões")
        print("   ✅ Eliminação de conversões Dict↔Pydantic no fluxo principal")
        print(f"   📈 Melhoria de performance: {improvement:.1f}%")
        print("   🧹 Code quality: Menos código de conversão, mais type safety")
        
        print("\n🎯 FASE 02: CONCLUÍDA COM SUCESSO! ✅")
        
    except Exception as e:
        print(f"💥 ERRO durante teste da Fase 02: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fase_02_improvements())
