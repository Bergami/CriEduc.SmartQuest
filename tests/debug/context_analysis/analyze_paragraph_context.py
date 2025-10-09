#!/usr/bin/env python3
"""
Analisa o contexto ao redor dos parágrafos com instruções para entender melhor o posicionamento
"""
import json

def analyze_paragraph_context():
    print("Analisando contexto dos paragrafos com instrucoes...")
    
    azure_file = "tests/responses/azure/azure_Recuperacao_20250825_192910.json"
    with open(azure_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    paragraphs = data.get('paragraphs', [])
    
    # Encontrar parágrafos com instruções "LEIA O TEXTO A SEGUIR"
    instruction_paragraphs = []
    for i, para in enumerate(paragraphs):
        content = para.get('content', '').strip()
        if 'LEIA O TEXTO A SEGUIR' in content.upper():
            instruction_paragraphs.append(i)
    
    print(f"Encontradas instruções nos parágrafos: {instruction_paragraphs}")
    
    # Analisar contexto ao redor de cada instrução
    for para_idx in instruction_paragraphs:
        print(f"\n{'='*80}")
        print(f"CONTEXTO DO PARÁGRAFO {para_idx}")
        print(f"{'='*80}")
        
        # Mostrar 5 parágrafos antes e 10 depois
        start = max(0, para_idx - 5)
        end = min(len(paragraphs), para_idx + 11)
        
        for i in range(start, end):
            content = paragraphs[i].get('content', '').strip()
            marker = " >>> INSTRUÇÃO <<<" if i == para_idx else ""
            
            print(f"[{i:2d}] {content[:100]}...{marker}")
            if len(content) > 100:
                print(f"     Tamanho total: {len(content)} caracteres")
        
        # Analisar o que vem imediatamente após a instrução
        print(f"\nANÁLISE DETALHADA APÓS PARÁGRAFO {para_idx}:")
        next_start = para_idx + 1
        next_end = min(len(paragraphs), para_idx + 6)
        
        for i in range(next_start, next_end):
            content = paragraphs[i].get('content', '').strip()
            print(f"\n[{i}] CONTEÚDO COMPLETO:")
            print(f"    {content}")
            
            # Analisar tipo de conteúdo
            content_upper = content.upper()
            if '(' in content and ')' in content:
                print("    >>> POSSÍVEL TÍTULO (com autor)")
            elif any(word in content_upper for word in ['QUESTÃO', 'PERGUNTA']):
                print("    >>> QUESTÃO")
            elif any(word in content_upper for word in ['DATA:', 'VALOR:', 'NOTA:']):
                print("    >>> INFORMAÇÃO DE CABEÇALHO")
            elif len(content) > 100:
                print("    >>> PARÁGRAFO DE TEXTO LONGO")
            elif len(content) < 20:
                print("    >>> TEXTO CURTO")

if __name__ == "__main__":
    analyze_paragraph_context()
