#!/usr/bin/env python3
"""
Debug específico do InternalQuestion.from_legacy_question
"""
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.internal.question_models import InternalQuestion


def debug_pydantic_conversion():
    """
    Debug da conversão Pydantic que está falhando
    """
    print("🔍 DEBUG: InternalQuestion.from_legacy_question")
    print("=" * 60)
    
    # Usar a estrutura legacy que sabemos que está correta
    legacy_question = {
        "number": 1,
        "question": "O texto de Marina Colasanti descreve diversas situações do cotidiano da sociedade contemporânea com o objetivo central de fomentar nos(as) leitores(as) uma reflexão a respeito: (2,0 pontos)",
        "type": "multiple_choice",
        "alternatives": [
            {
                "letter": "a",
                "text": "da velocidade com que a tecnologia influencia na nossa comunicação diária e na vida dos jovens e adultos"
            },
            {
                "letter": "b", 
                "text": "do desrespeito do ser humano com a vida humilde de pessoas pertencentes a grupos sociais mais pobres na sociedade"
            },
            {
                "letter": "c",
                "text": "da rotina cotidiana que nos habitua e muitas vezes não enxergamos como isso nos aprisiona."
            },
            {
                "letter": "d",
                "text": "da vida contemporânea que se tornou muito mais prática com tantas atribuições no dia a dia."
            }
        ],
        "is_multiple_choice": True
    }
    
    print(f"📋 LEGACY QUESTION INPUT:")
    print(f"   🔢 number: {legacy_question.get('number')}")
    print(f"   📝 question: {len(legacy_question.get('question', ''))} chars")
    print(f"   🔤 alternatives: {len(legacy_question.get('alternatives', []))} items")
    
    # Testar conversão
    print(f"\n🔧 CONVERTENDO PARA PYDANTIC...")
    try:
        pydantic_question = InternalQuestion.from_legacy_question(legacy_question)
        
        print(f"✅ Conversão bem-sucedida!")
        print(f"   📄 Tipo: {type(pydantic_question)}")
        print(f"   🔢 Number: {pydantic_question.number}")
        
        # Debug do content
        print(f"\n📝 CONTENT DEBUG:")
        print(f"   📄 Content tipo: {type(pydantic_question.content)}")
        print(f"   📝 Content statement: {len(pydantic_question.content.statement)} chars")
        print(f"   📝 Statement preview: {pydantic_question.content.statement[:100]}...")
        
        # Debug das options
        print(f"\n🔤 OPTIONS DEBUG:")
        print(f"   📄 Options tipo: {type(pydantic_question.options)}")
        print(f"   🔤 Options count: {len(pydantic_question.options)}")
        
        for i, opt in enumerate(pydantic_question.options):
            print(f"   Option {i+1}: {opt.label}) {opt.text[:50]}...")
        
        # Testar propriedade "question" direta
        if hasattr(pydantic_question, 'question'):
            print(f"\n❌ PROBLEMA: Propriedade 'question' existe: {getattr(pydantic_question, 'question', 'N/A')}")
        else:
            print(f"\n✅ Propriedade 'question' não existe (correto)")
        
        # Testar propriedade "alternatives" direta  
        if hasattr(pydantic_question, 'alternatives'):
            print(f"❌ PROBLEMA: Propriedade 'alternatives' existe: {len(getattr(pydantic_question, 'alternatives', []))}")
        else:
            print(f"✅ Propriedade 'alternatives' não existe (correto, deve usar 'options')")
        
        # Simular o que está acontecendo no dict() (Pydantic v1)
        print(f"\n📊 DICT() TEST:")
        try:
            dumped = pydantic_question.dict()
            print(f"✅ dict() executado")
            print(f"   🔑 Chaves: {list(dumped.keys())}")
            
            # Verificar campos específicos no dump
            if 'content' in dumped:
                content_dump = dumped['content']
                print(f"   📝 Content dump: {type(content_dump)} - {list(content_dump.keys()) if isinstance(content_dump, dict) else content_dump}")
            
            if 'options' in dumped:
                options_dump = dumped['options']
                print(f"   🔤 Options dump: {len(options_dump)} items")
            
            # Salvar dump para análise
            with open("debug_pydantic_conversion_dump.json", "w", encoding="utf-8") as f:
                json.dump(dumped, f, indent=2, ensure_ascii=False)
            print(f"💾 Dict dump salvo em: debug_pydantic_conversion_dump.json")
            
        except Exception as e:
            print(f"❌ ERRO no dict(): {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ ERRO na conversão: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG CONCLUÍDO")


if __name__ == "__main__":
    debug_pydantic_conversion()
