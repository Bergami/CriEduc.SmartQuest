#!/usr/bin/env python3
"""
Script para analisar como as questões e alternativas estão organizadas
em parágrafos separados no Azure Response.
"""

import json
import os

def analyze_paragraph_structure():
    """Analisa a estrutura de parágrafos do Azure Response."""
    
    azure_file = "tests/responses/azure/azure_7c36b9bd-1d8d-464e-a681-7f3e21a28fd2_Recuperacao_20250827_165443.json"
    
    if not os.path.exists(azure_file):
        print(f"❌ Arquivo não encontrado: {azure_file}")
        return
    
    print(f"🔍 Analisando estrutura de parágrafos: {azure_file}")
    print("=" * 80)
    
    with open(azure_file, 'r', encoding='utf-8') as f:
        azure_data = json.load(f)
    
    # Acessar paragraphs (na raiz do JSON)
    if 'paragraphs' in azure_data:
        paragraphs = azure_data['paragraphs']
        print(f"📄 Total de parágrafos: {len(paragraphs)}")
    else:
        print("❌ Estrutura 'paragraphs' não encontrada no arquivo!")
        return
    
    # Encontrar questões e suas alternativas
    current_question = None
    question_data = {}
    
    for i, paragraph in enumerate(paragraphs):
        content = paragraph.get('content', '').strip()
        
        # Detectar questões
        if content.startswith('QUESTÃO') and ('01' in content or '02' in content or '03' in content):
            # Extrair número da questão
            if 'QUESTÃO 01' in content or 'QUESTÃO 1' in content:
                current_question = 1
            elif 'QUESTÃO 02' in content or 'QUESTÃO 2' in content:
                current_question = 2
            elif 'QUESTÃO 03' in content or 'QUESTÃO 3' in content:
                current_question = 3
            
            if current_question:
                question_data[current_question] = {
                    'paragraph_index': i,
                    'question_content': content,
                    'alternatives': []
                }
                
                print(f"\n🎯 QUESTÃO {current_question} encontrada no parágrafo {i}:")
                print(f"   Content: {content[:150]}...")
        
        # Detectar alternativas (se estamos em uma questão)
        elif current_question and content.startswith(('a)', 'b)', 'c)', 'd)', 'e)')):
            alternative_letter = content[:2]
            alternative_content = content[2:].strip()
            
            question_data[current_question]['alternatives'].append({
                'paragraph_index': i,
                'letter': alternative_letter,
                'content': alternative_content,
                'full_content': content
            })
            
            print(f"   ✅ Alternativa {alternative_letter} no parágrafo {i}")
            print(f"      Content: {alternative_content[:100]}...")
        
        # Resetar questão atual se chegamos em uma nova questão
        elif content.startswith('QUESTÃO') and current_question:
            current_question = None
    
    # Resumo final
    print(f"\n📊 RESUMO FINAL:")
    print("=" * 80)
    
    for q_num, q_data in question_data.items():
        print(f"\n🎯 QUESTÃO {q_num}:")
        print(f"   Parágrafo: {q_data['paragraph_index']}")
        print(f"   Alternativas encontradas: {len(q_data['alternatives'])}")
        
        for alt in q_data['alternatives']:
            print(f"      {alt['letter']} - Parágrafo {alt['paragraph_index']}")
        
        # Verificar se todas as alternativas esperadas estão presentes
        letters_found = [alt['letter'] for alt in q_data['alternatives']]
        print(f"   Letras encontradas: {letters_found}")
    
    # Exemplo de como deveria ser a extração correta
    print(f"\n💡 PROPOSTA DE NOVA ABORDAGEM:")
    print("=" * 80)
    print("1. Identificar parágrafo da questão")
    print("2. Coletarparágrafos subsequentes que começam com a), b), c), d), e)")
    print("3. Cada alternativa = um parágrafo separado")
    print("4. Não tentar extrair alternativas de dentro do texto da questão")
    
    return question_data

if __name__ == "__main__":
    analyze_paragraph_structure()
