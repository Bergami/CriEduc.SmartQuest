#!/usr/bin/env python3
"""
Debug do formato retornado por extract_from_paragraphs
"""
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.question_parser import QuestionParser
from app.services.azure_response_service import AzureResponseService


def debug_legacy_format():
    """
    Debug do formato legacy retornado por extract_from_paragraphs
    """
    print("🔍 DEBUG: Formato legacy retornado por extract_from_paragraphs")
    print("=" * 60)
    
    # 1. Carregar dados do Azure
    azure_result = AzureResponseService.get_latest_azure_response()
    azure_paragraphs = azure_result.get("paragraphs", []) if azure_result else []
    
    print(f"✅ Azure paragraphs carregados: {len(azure_paragraphs)}")
    
    # 2. Testar extract_from_paragraphs diretamente
    print(f"\n🔧 Testando extract_from_paragraphs...")
    paragraph_list = [{"content": p.get("content", "")} for p in azure_paragraphs if p.get("content")]
    
    result = QuestionParser.extract_from_paragraphs(paragraph_list, {})
    
    print(f"✅ Questions: {len(result.get('questions', []))}")
    
    # 3. Analisar formato da primeira questão em detalhe
    questions_dict = result.get('questions', [])
    if questions_dict:
        first_question = questions_dict[0]
        
        print(f"\n📋 ESTRUTURA COMPLETA DA PRIMEIRA QUESTÃO:")
        print(f"   📄 Tipo: {type(first_question)}")
        print(f"   🔑 Chaves disponíveis: {list(first_question.keys())}")
        
        # Salvar estrutura completa para análise
        with open("debug_legacy_question_structure.json", "w", encoding="utf-8") as f:
            json.dump(first_question, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Estrutura completa salva em: debug_legacy_question_structure.json")
        
        print(f"\n📊 VALORES POR CHAVE:")
        for key, value in first_question.items():
            if isinstance(value, str):
                print(f"   🔑 {key}: '{value[:100]}{'...' if len(value) > 100 else ''}' ({len(value)} chars)")
            elif isinstance(value, list):
                print(f"   🔑 {key}: [lista com {len(value)} itens]")
                if value and len(value) > 0:
                    print(f"      📝 Primeiro item: {type(value[0])} - {str(value[0])[:100]}")
            else:
                print(f"   🔑 {key}: {value} ({type(value)})")
        
        # 4. Comparar com o que o InternalQuestion.from_legacy_question espera
        print(f"\n📋 COMPARAÇÃO COM WHAT PYDANTIC EXPECTS:")
        print(f"   ✅ InternalQuestion.from_legacy_question procura por:")
        print(f"      📝 'question' -> encontrado: {'question' in first_question}")
        print(f"      🔤 'alternatives' -> encontrado: {'alternatives' in first_question}")
        print(f"      🔢 'number' -> encontrado: {'number' in first_question}")
        print(f"      🖼️ 'hasImage' -> encontrado: {'hasImage' in first_question}")
        print(f"      🔗 'contextId' -> encontrado: {'contextId' in first_question}")
        
        # 5. Verificar o conteúdo das alternatives
        alternatives = first_question.get('alternatives', [])
        if alternatives:
            print(f"\n🔤 ESTRUTURA DA PRIMEIRA ALTERNATIVE:")
            first_alt = alternatives[0]
            print(f"   📄 Tipo: {type(first_alt)}")
            if isinstance(first_alt, dict):
                print(f"   🔑 Chaves: {list(first_alt.keys())}")
                print(f"   📝 'letter' -> {first_alt.get('letter', 'N/A')}")
                print(f"   📝 'text' -> {first_alt.get('text', 'N/A')[:100]}...")
        
    else:
        print("❌ Nenhuma questão encontrada!")
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG CONCLUÍDO")


if __name__ == "__main__":
    debug_legacy_format()
