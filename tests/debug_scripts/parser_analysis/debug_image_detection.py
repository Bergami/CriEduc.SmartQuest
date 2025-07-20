#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.parsers.question_parser import QuestionParser
import json

def debug_image_detection():
    text_with_image = """
        QUESTÃO 01
        
        Analise a imagem abaixo e responda:
        
        (A) Opção A
        (B) Opção B
        (C) Opção C
        (D) Opção D
        (E) Opção E
        """
    
    print("=== DEBUG: Image Detection ===")
    print("Input text:")
    print(repr(text_with_image))
    print()
    
    result = QuestionParser.extract(text_with_image)
    
    print("=== RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    print("=== QUESTIONS ANALYSIS ===")
    questions = result["questions"]
    print(f"Number of questions found: {len(questions)}")
    
    if questions:
        for i, question in enumerate(questions):
            print(f"\nQuestion {i+1}:")
            print(f"  hasImage: {question.get('hasImage', 'NOT_PRESENT')}")
            print(f"  question text: {repr(question.get('question', ''))}")
            print(f"  full structure: {json.dumps(question, indent=4, ensure_ascii=False)}")
    
    print("\n=== CONTEXT BLOCKS ANALYSIS ===")
    context_blocks = result["context_blocks"]
    print(f"Number of context blocks found: {len(context_blocks)}")
    
    if context_blocks:
        for i, block in enumerate(context_blocks):
            print(f"\nContext Block {i+1}:")
            print(f"  hasImage: {block.get('hasImage', 'NOT_PRESENT')}")
            print(f"  type: {block.get('type', 'NOT_PRESENT')}")
            print(f"  statement: {repr(block.get('statement', ''))}")
            print(f"  paragraphs: {block.get('paragraphs', [])}")

if __name__ == "__main__":
    debug_image_detection()
