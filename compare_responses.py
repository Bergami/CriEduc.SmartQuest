#!/usr/bin/env python3
"""
Script para comparar a resposta atual com o resultado esperado
"""

import json
from pathlib import Path

def compare_responses():
    """Compara resposta atual com resultado esperado"""
    
    # Carregar arquivos
    atual_file = Path("tests/resposta_atual.json")
    esperado_file = Path("tests/resultado_parser.json")
    
    if not atual_file.exists():
        print("❌ Arquivo resposta_atual.json não encontrado")
        return
        
    if not esperado_file.exists():
        print("❌ Arquivo resultado_parser.json não encontrado")
        return
    
    with open(atual_file, 'r', encoding='utf-8') as f:
        atual = json.load(f)
    
    with open(esperado_file, 'r', encoding='utf-8') as f:
        esperado = json.load(f)
    
    print("🔍 COMPARAÇÃO ENTRE ATUAL E ESPERADO")
    print("="*60)
    
    # Comparar campos principais
    print(f"📧 Email:")
    print(f"   Atual:    {atual.get('email')}")
    print(f"   Esperado: {esperado.get('email')}")
    print()
    
    print(f"📄 Filename:")
    print(f"   Atual:    {atual.get('filename')}")
    print(f"   Esperado: {esperado.get('filename')}")
    print()
    
    # Comparar header
    print(f"📋 HEADER:")
    header_fields = ['network', 'school', 'city', 'teacher', 'subject', 'exam_title', 'trimester', 'grade']
    
    for field in header_fields:
        atual_val = atual.get('header', {}).get(field)
        esperado_val = esperado.get('header', {}).get(field)
        
        status = "✅" if atual_val == esperado_val else "❌"
        print(f"   {status} {field}:")
        print(f"      Atual:    {atual_val}")
        print(f"      Esperado: {esperado_val}")
    
    print()
    
    # Comparar questões
    atual_questions = atual.get('questions', [])
    esperado_questions = esperado.get('questions', [])
    
    print(f"📝 QUESTÕES:")
    print(f"   Atual:    {len(atual_questions)} questões")
    print(f"   Esperado: {len(esperado_questions)} questões")
    
    # Comparar primeira questão em detalhes
    if atual_questions and esperado_questions:
        print(f"\n📋 PRIMEIRA QUESTÃO (detalhes):")
        q1_atual = atual_questions[0]
        q1_esperado = esperado_questions[0]
        
        print(f"   ✅ Número: {q1_atual.get('number')} vs {q1_esperado.get('number')}")
        print(f"   📝 Pergunta atual:    {q1_atual.get('question')}")
        print(f"   📝 Pergunta esperada: {q1_esperado.get('question')}")
        
        atual_alts = q1_atual.get('alternatives', [])
        esperado_alts = q1_esperado.get('alternatives', [])
        
        print(f"   📚 Alternativas: {len(atual_alts)} vs {len(esperado_alts)}")
        
        for i, (atual_alt, esperado_alt) in enumerate(zip(atual_alts, esperado_alts)):
            print(f"      {atual_alt.get('letter')}: {atual_alt.get('text')}")
            print(f"      {esperado_alt.get('letter')}: {esperado_alt.get('text')}")
            if atual_alt.get('text') != esperado_alt.get('text'):
                print("      ❌ DIFERENÇA!")
            print()
    
    # Comparar blocos de contexto
    atual_contexts = atual.get('context_blocks', [])
    esperado_contexts = esperado.get('context_blocks', [])
    
    print(f"📚 BLOCOS DE CONTEXTO:")
    print(f"   Atual:    {len(atual_contexts)} blocos")
    print(f"   Esperado: {len(esperado_contexts)} blocos")

if __name__ == "__main__":
    compare_responses()
