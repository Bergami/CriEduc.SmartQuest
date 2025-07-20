#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.parsers.question_parser.detect_questions import detect_questions
import json
import re

def debug_question_detection():
    text_with_image = """
        QUESTÃO 01
        
        Analise a imagem abaixo e responda:
        
        (A) Opção A
        (B) Opção B
        (C) Opção C
        (D) Opção D
        (E) Opção E
        """
    
    print("=== DEBUG: Question Detection ===")
    print("Input text:")
    print(repr(text_with_image))
    print()
    
    # Test the regex pattern
    pattern = r"(QUEST[ÃA]O\s+\d+\.?)"
    blocks = re.split(pattern, text_with_image)
    
    print("=== REGEX SPLIT RESULT ===")
    print(f"Number of blocks: {len(blocks)}")
    for i, block in enumerate(blocks):
        print(f"Block {i}: {repr(block)}")
    print()
    
    # Test question detection
    questions = detect_questions(text_with_image)
    
    print("=== DETECTED QUESTIONS ===")
    print(json.dumps(questions, indent=2, ensure_ascii=False))
    print()
    
    if questions:
        for i, question in enumerate(questions):
            print(f"Question {i+1}:")
            print(f"  Number: {question['number']}")
            print(f"  Question text: {repr(question['question'])}")
            print(f"  Has image: {question['hasImage']}")
            print(f"  Alternatives: {len(question['alternatives'])}")
            for j, alt in enumerate(question['alternatives']):
                print(f"    {alt['letter']}: {repr(alt['text'])}")

if __name__ == "__main__":
    debug_question_detection()
