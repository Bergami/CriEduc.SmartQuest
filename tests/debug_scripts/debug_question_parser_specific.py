#!/usr/bin/env python3
"""
Debug específico do QuestionParser.extract_typed
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.question_parser import QuestionParser
from app.services.azure_response_service import AzureResponseService


def debug_question_parser_extract_typed():
    """
    Debug específico do método extract_typed do QuestionParser
    """
    print("🔍 DEBUG: QuestionParser.extract_typed")
    print("=" * 50)
    
    # 1. Carregar dados do Azure
    print("📂 ETAPA 1: Carregando dados do Azure...")
    azure_result = AzureResponseService.get_latest_azure_response()
    azure_paragraphs = azure_result.get("paragraphs", []) if azure_result else []
    
    print(f"✅ Azure paragraphs carregados: {len(azure_paragraphs)}")
    
    # 2. Converter parágrafos para texto (como faz o AnalyzeService)
    print("\n📂 ETAPA 2: Convertendo parágrafos para texto...")
    combined_text = "\n".join([p.get("content", "") for p in azure_paragraphs if p.get("content")])
    
    print(f"✅ Texto combinado: {len(combined_text)} chars")
    print(f"✅ Primeiros 200 chars: {combined_text[:200]}...")
    print(f"✅ Últimos 200 chars: ...{combined_text[-200:]}")
    
    # 3. Testar extract_typed
    print(f"\n🔧 ETAPA 3: Testando QuestionParser.extract_typed...")
    try:
        questions, context_blocks = QuestionParser.extract_typed(combined_text, {})
        
        print(f"✅ extract_typed executado com sucesso!")
        print(f"✅ Questions retornadas: {len(questions)}")
        print(f"✅ Context blocks retornados: {len(context_blocks)}")
        
        # Analisar primeira questão
        if questions:
            q = questions[0]
            print(f"\n📋 PRIMEIRA QUESTÃO:")
            print(f"   📄 Tipo: {type(q)}")
            print(f"   🔢 Number: {getattr(q, 'number', 'N/A')}")
            
            # Debug do content
            content = getattr(q, 'content', None)
            if content:
                print(f"   📝 Content type: {type(content)}")
                if hasattr(content, 'text'):
                    print(f"   📝 Content text: {len(content.text)} chars")
                    if content.text:
                        print(f"   📝 Content preview: {content.text[:100]}...")
                elif hasattr(content, 'question'):
                    print(f"   📝 Content question: {len(content.question)} chars")
                    if content.question:
                        print(f"   📝 Question preview: {content.question[:100]}...")
            
            # Verificar propriedade question diretamente
            question_text = getattr(q, 'question', None)
            if question_text:
                print(f"   📝 Direct question: {len(question_text)} chars")
                print(f"   📝 Question preview: {question_text[:100]}...")
            else:
                print(f"   ❌ Direct question: None/Empty")
            
            # Verificar alternatives
            alternatives = getattr(q, 'alternatives', [])
            print(f"   🔤 Alternatives: {len(alternatives)}")
            
        else:
            print("❌ Nenhuma questão foi extraída!")
    
    except Exception as e:
        print(f"❌ ERRO no extract_typed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Testar extract_from_paragraphs diretamente
    print(f"\n🔧 ETAPA 4: Testando QuestionParser.extract_from_paragraphs (direto)...")
    try:
        # Converter parágrafos para formato esperado
        paragraph_list = [{"content": p.get("content", "")} for p in azure_paragraphs if p.get("content")]
        
        result = QuestionParser.extract_from_paragraphs(paragraph_list, {})
        
        print(f"✅ extract_from_paragraphs executado!")
        print(f"✅ Questions: {len(result.get('questions', []))}")
        print(f"✅ Context blocks: {len(result.get('context_blocks', []))}")
        
        # Analisar primeira questão do resultado
        questions_dict = result.get('questions', [])
        if questions_dict:
            q_dict = questions_dict[0]
            print(f"\n📋 PRIMEIRA QUESTÃO (Dict format):")
            print(f"   🔢 Number: {q_dict.get('number')}")
            print(f"   📝 Question length: {len(q_dict.get('question', ''))}")
            print(f"   🔤 Alternatives: {len(q_dict.get('alternatives', []))}")
            
            if q_dict.get('question'):
                print(f"   📝 Question preview: {q_dict.get('question')[:100]}...")
                
        else:
            print("❌ Nenhuma questão no formato dict!")
            
    except Exception as e:
        print(f"❌ ERRO no extract_from_paragraphs: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🔍 DEBUG CONCLUÍDO")


if __name__ == "__main__":
    debug_question_parser_extract_typed()
