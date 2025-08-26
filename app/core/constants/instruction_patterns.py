"""
Instruction Patterns for Document Analysis
Patterns used to identify instructional text that precedes figures or content blocks
"""
import re
from typing import List, Pattern
from dataclasses import dataclass

@dataclass
class InstructionPattern:
    """Represents an instruction pattern with metadata"""
    pattern: str
    description: str
    flags: int = re.IGNORECASE
    
    @property
    def compiled(self) -> Pattern[str]:
        """Returns compiled regex pattern"""
        return re.compile(self.pattern, self.flags)

class InstructionPatterns:
    """Collection of instruction patterns for document analysis"""
    
    # Analysis instructions
    ANALYZE_TEXT = InstructionPattern(
        pattern=r'analise?\s+(?:a|o|os)\s+(?:texto|textos)s?\s+(?:a\s+seguir|abaixo)',
        description="Analyze the following text(s)"
    )
    
    ANALYZE_IMAGE = InstructionPattern(
        pattern=r'analise?\s+(?:a|o|os)\s+(?:imagem|figura|charge|propaganda)s?\s+(?:a\s+seguir|abaixo)',
        description="Analyze the following image(s)/figure(s)"
    )
    
    # Reading instructions
    READ_TEXT = InstructionPattern(
        pattern=r'leia\s+(?:o|os)\s+(?:texto|textos)\s+(?:a\s+seguir|abaixo)',
        description="Read the following text(s)"
    )
    
    # Observation instructions
    OBSERVE_FIGURE = InstructionPattern(
        pattern=r'observe\s+(?:a|o|os)\s+(?:imagem|figura|propaganda)s?\s+(?:a\s+seguir|abaixo)',
        description="Observe the following figure(s)/image(s)"
    )
    
    # Text block markers
    TEXT_BLOCK_MARKER = InstructionPattern(
        pattern=r'(?:texto|charge|propaganda)\s+[IVX]+:',
        description="Text block markers (TEXTO I:, TEXTO II:, etc.)"
    )
    
    # Question analysis instructions
    ANALYZE_FOR_QUESTION = InstructionPattern(
        pattern=r'analise\s+(?:a\s+tirinha|o\s+texto|a\s+propaganda)\s+(?:a\s+seguir\s+)?para\s+responder',
        description="Analyze content to answer question"
    )
    
    # General content instructions
    GENERAL_ANALYSIS = InstructionPattern(
        pattern=r'(?:analise|observe|leia)\s+(?:.*?)(?:a\s+seguir|abaixo)',
        description="General analysis instruction"
    )
    
    @classmethod
    def get_all_patterns(cls) -> List[InstructionPattern]:
        """Returns all instruction patterns"""
        return [
            cls.ANALYZE_TEXT,
            cls.ANALYZE_IMAGE,
            cls.READ_TEXT,
            cls.OBSERVE_FIGURE,
            cls.TEXT_BLOCK_MARKER,
            cls.ANALYZE_FOR_QUESTION,
            cls.GENERAL_ANALYSIS
        ]
    
    @classmethod
    def find_instruction_type(cls, text: str) -> str:
        """
        Identifies the type of instruction in the given text
        
        Args:
            text: Text to analyze
            
        Returns:
            String identifier of the instruction type or 'unknown'
        """
        text_clean = text.strip()
        
        for pattern in cls.get_all_patterns():
            if pattern.compiled.search(text_clean):
                return pattern.__class__.__name__.split('.')[-1].lower()
        
        return 'unknown'
    
    @classmethod
    def extract_instruction_content(cls, text: str) -> dict:
        """
        Extracts structured information from instruction text
        
        Args:
            text: Instruction text to parse
            
        Returns:
            Dictionary with instruction details
        """
        text_clean = text.strip().upper()
        
        result = {
            'original_text': text,
            'instruction_type': 'unknown',
            'content_type': 'unknown',
            'sequence_number': None,
            'is_for_question': False
        }
        
        # Check for text block markers (TEXTO I, II, III, IV)
        texto_match = re.search(r'TEXTO\s+([IVX]+)', text_clean)
        if texto_match:
            result['instruction_type'] = 'text_block_marker'
            result['sequence_number'] = texto_match.group(1)
            
            # Check content type in the same line
            if 'CHARGE' in text_clean:
                result['content_type'] = 'charge'
            elif 'PROPAGANDA' in text_clean:
                result['content_type'] = 'propaganda'
            else:
                result['content_type'] = 'text'
        
        # Check for question-related instructions
        if 'PARA RESPONDER' in text_clean:
            result['is_for_question'] = True
            result['instruction_type'] = 'question_analysis'
        
        # Check for general analysis instructions
        if any(word in text_clean for word in ['ANALISE', 'OBSERVE', 'LEIA']):
            if result['instruction_type'] == 'unknown':
                result['instruction_type'] = 'general_analysis'
        
        return result
