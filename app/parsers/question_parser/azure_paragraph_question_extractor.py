#!/usr/bin/env python3
"""
Novo sistema de extração de questões e alternativas baseado em parágrafos do Azure
====================================================================================

Este módulo implementa uma nova abordagem simplificada e performática para extrair
questões e alternativas diretamente dos parágrafos retornados pelo Azure Document Intelligence.

Segue os princípios SOLID:
- Single Responsibility: Cada classe tem uma responsabilidade específica
- Open/Closed: Extensível para novos tipos de questões sem modificar código existente
- Liskov Substitution: Interfaces bem definidas
- Interface Segregation: Interfaces específicas e focadas
- Dependency Inversion: Depende de abstrações, não de implementações concretas

Substitui a complexidade atual do extract_alternatives_from_text.py por uma
implementação mais simples baseada na estrutura de parágrafos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# ==============================================================================
# DOMAIN MODELS (Seguindo Single Responsibility Principle)
# ==============================================================================

@dataclass
class Alternative:
    """Representa uma alternativa de múltipla escolha"""
    id: str
    text: str
    
    def __post_init__(self):
        """Validação e limpeza automática"""
        self.id = self.id.lower().strip()
        self.text = self.text.strip()
        
        if not self.id or not self.text:
            raise ValueError("ID e texto da alternativa são obrigatórios")

@dataclass
class Question:
    """Representa uma questão completa"""
    number: int
    statement: str
    alternatives: List[Alternative]
    
    @property
    def is_multiple_choice(self) -> bool:
        """Indica se é uma questão de múltipla escolha"""
        return len(self.alternatives) > 0
    
    @property
    def question_type(self) -> str:
        """Retorna o tipo da questão"""
        return "multiple_choice" if self.is_multiple_choice else "discursive"

@dataclass 
class ExtractionResult:
    """Resultado da extração de questões"""
    questions: List[Question]
    total_questions: int
    multiple_choice_count: int
    discursive_count: int
    extraction_method: str
    
    @classmethod
    def from_questions(cls, questions: List[Question], extraction_method: str) -> 'ExtractionResult':
        """Factory method para criar resultado da extração"""
        multiple_choice_count = sum(1 for q in questions if q.is_multiple_choice)
        discursive_count = len(questions) - multiple_choice_count
        
        return cls(
            questions=questions,
            total_questions=len(questions),
            multiple_choice_count=multiple_choice_count,
            discursive_count=discursive_count,
            extraction_method=extraction_method
        )

# ==============================================================================
# INTERFACES (Seguindo Interface Segregation Principle)
# ==============================================================================

class QuestionDetector(ABC):
    """Interface para detectores de questões"""
    
    @abstractmethod
    def detect_question_positions(self, paragraphs: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """
        Detecta as posições das questões nos parágrafos
        
        Returns:
            Lista de tuplas (posição_parágrafo, número_questão)
        """
        pass

class AlternativeExtractor(ABC):
    """Interface para extratores de alternativas"""
    
    @abstractmethod
    def extract_alternatives(
        self, 
        paragraphs: List[Dict[str, Any]], 
        question_position: int,
        next_question_position: Optional[int] = None
    ) -> List[Alternative]:
        """
        Extrai alternativas de uma questão
        
        Args:
            paragraphs: Lista de parágrafos do Azure
            question_position: Posição do parágrafo da questão
            next_question_position: Posição da próxima questão (para delimitar busca)
            
        Returns:
            Lista de alternativas extraídas
        """
        pass

class StatementExtractor(ABC):
    """Interface para extratores de enunciados"""
    
    @abstractmethod
    def extract_statement(self, paragraph_content: str) -> str:
        """
        Extrai o enunciado limpo de um parágrafo de questão
        
        Args:
            paragraph_content: Conteúdo do parágrafo da questão
            
        Returns:
            Enunciado limpo da questão
        """
        pass

class QuestionExtractor(ABC):
    """Interface principal para extração de questões"""
    
    @abstractmethod
    def extract_questions(self, paragraphs: List[Dict[str, Any]]) -> ExtractionResult:
        """
        Extrai todas as questões dos parágrafos
        
        Args:
            paragraphs: Lista de parágrafos do Azure Document Intelligence
            
        Returns:
            Resultado da extração com todas as questões
        """
        pass

# ==============================================================================
# IMPLEMENTAÇÕES (Seguindo Single Responsibility e Open/Closed Principles)
# ==============================================================================

class RegexQuestionDetector(QuestionDetector):
    """Detector de questões baseado em regex"""
    
    def __init__(self, pattern: str = r'QUESTÃO\s+(\d+)', flags: int = re.IGNORECASE):
        self.pattern = re.compile(pattern, flags)
    
    def detect_question_positions(self, paragraphs: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """Detecta posições das questões usando regex"""
        positions = []
        
        for i, paragraph in enumerate(paragraphs):
            content = paragraph.get('content', '')
            match = self.pattern.search(content)
            
            if match:
                question_number = int(match.group(1))
                positions.append((i, question_number))
                logger.debug(f"Questão {question_number} detectada na posição {i}")
        
        return positions

class StandardStatementExtractor(StatementExtractor):
    """Extrator padrão de enunciados"""
    
    def extract_statement(self, paragraph_content: str) -> str:
        """Extrai enunciado removendo 'QUESTÃO XX.' e alternativas inline"""
        # Remove "QUESTÃO XX." do início
        statement = re.sub(r'^QUESTÃO\s+\d+\.\s*', '', paragraph_content, flags=re.IGNORECASE)
        
        # Remove alternativas inline (formato a) b) c) d))
        # Encontra a primeira alternativa e corta o texto lá
        first_alt_match = re.search(r'\s+[a-e]\)\s*', statement, re.IGNORECASE)
        if first_alt_match:
            statement = statement[:first_alt_match.start()].strip()
        
        # ✅ PRESERVAR informação de pontos - NÃO remover!
        # A informação "(2,0 pontos)" é importante e deve ser mantida no enunciado
        
        # Normaliza espaços
        statement = re.sub(r'\s+', ' ', statement).strip()
        
        return statement

class HybridAlternativeExtractor(AlternativeExtractor):
    """
    Extrator híbrido que trata alternativas inline e em parágrafos separados
    """
    
    def __init__(self):
        # CENÁRIO 1: Alternativas no início de parágrafos (primeiros 3 caracteres)
        self.paragraph_start_pattern = re.compile(r'^([a-e])\)\s*(.+)', re.MULTILINE | re.IGNORECASE)
        
        # CENÁRIO 2: Alternativas inline no mesmo parágrafo
        # IMPORTANTE: Só captura a), b), c) - NUNCA (a), (b), (c)
        # Usa lookbehind negativo (?<!\() para evitar capturar se precedido por "("
        self.inline_pattern = re.compile(r'(?<!\()([a-e])\)\s*([^)]+?)(?=[a-e]\)|$)', re.IGNORECASE)
        
        # Padrão para alternativas em parágrafos separados (compatibilidade)
        self.separate_pattern = re.compile(r'^([a-e])\)\s*(.+)', re.IGNORECASE)
    
    def extract_alternatives(
        self, 
        paragraphs: List[Dict[str, Any]], 
        question_position: int,
        next_question_position: Optional[int] = None
    ) -> List[Alternative]:
        """Extrai alternativas usando método híbrido"""
        
        question_content = paragraphs[question_position].get('content', '')
        
        # 1. Primeiro, extrai alternativas inline do parágrafo da questão
        inline_alternatives = self._extract_inline_alternatives(question_content)
        
        # 2. Depois, busca alternativas adicionais nos parágrafos seguintes
        additional_alternatives = self._extract_separate_alternatives(
            paragraphs, question_position + 1, next_question_position, len(inline_alternatives)
        )
        
        # 3. Combina todas as alternativas
        all_alternatives = inline_alternatives + additional_alternatives
        
        logger.debug(f"Extraídas {len(all_alternatives)} alternativas: {len(inline_alternatives)} inline + {len(additional_alternatives)} separadas")
        
        return all_alternatives
    
    def _extract_inline_alternatives(self, question_content: str) -> List[Alternative]:
        """
        Extrai alternativas que estão no mesmo parágrafo da questão
        
        Implementa dois cenários:
        1. Alternativas no início de linhas (primeiros 3 caracteres)
        2. Alternativas inline, mas só a), b), c) - NUNCA (a), (b), (c)
        """
        alternatives = []
        
        # CENÁRIO 1: Alternativas que começam uma nova linha (mais confiáveis)
        paragraph_matches = list(self.paragraph_start_pattern.finditer(question_content))
        
        # CENÁRIO 2: Alternativas inline (com cuidado para evitar falsos positivos)
        inline_matches = list(self.inline_pattern.finditer(question_content))
        
        # Combina e ordena todas as matches por posição
        all_matches = []
        
        # Adiciona matches do início de parágrafo (mais prioritárias)
        for match in paragraph_matches:
            all_matches.append((match.start(), match, 'paragraph'))
        
        # Adiciona matches inline, mas só se não conflitarem
        for match in inline_matches:
            # Verifica se não está dentro de palavra como "interlocutor(a)"
            start_pos = match.start()
            before_text = question_content[max(0, start_pos-10):start_pos]
            
            # Se tem letra ou "_" imediatamente antes do "(", é falso positivo
            if re.search(r'[a-zA-Z_]\($', before_text):
                logger.debug(f"Ignorando falso positivo: '{before_text}({match.group(1)})'")
                continue
                
            # Verifica se não conflita com match de parágrafo
            conflicts = any(abs(match.start() - pm[1].start()) < 5 for pm in all_matches if pm[2] == 'paragraph')
            if not conflicts:
                all_matches.append((match.start(), match, 'inline'))
        
        # Ordena por posição e processa
        all_matches.sort(key=lambda x: x[0])
        
        for _, match, match_type in all_matches:
            letter = match.group(1).lower()
            alt_text = match.group(2).strip()
            
            # Limpa o texto da alternativa
            alt_text = re.sub(r'\s+', ' ', alt_text).strip()
            alt_text = re.sub(r'\.$', '', alt_text).strip()
            
            # Verifica se é sequencial e tem texto suficiente
            expected_letter = chr(ord('a') + len(alternatives))
            if letter == expected_letter and len(alt_text) > 3:
                alternatives.append(Alternative(id=letter, text=alt_text))
                logger.debug(f"Alternativa {letter} extraída ({match_type}): '{alt_text[:30]}...'")
            else:
                logger.debug(f"Alternativa {letter} rejeitada: esperado '{expected_letter}', texto='{alt_text[:20]}'")
        
        return alternatives
    
    def _extract_separate_alternatives(
        self, 
        paragraphs: List[Dict[str, Any]], 
        start_position: int, 
        end_position: Optional[int],
        inline_count: int
    ) -> List[Alternative]:
        """Extrai alternativas de parágrafos separados"""
        alternatives = []
        expected_letter = chr(ord('a') + inline_count)
        
        end_pos = end_position if end_position is not None else len(paragraphs)
        
        for i in range(start_position, min(start_position + 10, end_pos)):
            if i >= len(paragraphs):
                break
                
            content = paragraphs[i].get('content', '').strip()
            
            # Verifica se é uma alternativa
            match = self.separate_pattern.match(content)
            if match:
                letter = match.group(1).lower()
                alt_text = match.group(2).strip()
                
                # Verifica se é a próxima alternativa esperada
                if letter == expected_letter:
                    alternatives.append(Alternative(id=letter, text=alt_text))
                    expected_letter = chr(ord(expected_letter) + 1)
                else:
                    # Não é sequencial, para de procurar
                    break
            else:
                # Se não é alternativa e já temos algumas, para
                if alternatives:
                    break
        
        return alternatives

class AzureParagraphQuestionExtractor(QuestionExtractor):
    """
    Extrator principal de questões baseado em parágrafos do Azure
    (Seguindo Dependency Inversion Principle)
    """
    
    def __init__(
        self,
        question_detector: QuestionDetector,
        statement_extractor: StatementExtractor,
        alternative_extractor: AlternativeExtractor
    ):
        self.question_detector = question_detector
        self.statement_extractor = statement_extractor
        self.alternative_extractor = alternative_extractor
    
    def extract_questions(self, paragraphs: List[Dict[str, Any]]) -> ExtractionResult:
        """Extrai todas as questões usando os componentes injetados"""
        
        # 1. Detecta posições das questões
        question_positions = self.question_detector.detect_question_positions(paragraphs)
        
        if not question_positions:
            logger.warning("Nenhuma questão detectada nos parágrafos")
            return ExtractionResult.from_questions([], "azure_paragraph_extractor")
        
        logger.info(f"Detectadas {len(question_positions)} questões")
        
        # 2. Extrai cada questão
        questions = []
        for i, (pos, num) in enumerate(question_positions):
            # Determina o limite para buscar alternativas (até a próxima questão)
            next_pos = question_positions[i + 1][0] if i + 1 < len(question_positions) else None
            
            question = self._extract_single_question(paragraphs, pos, num, next_pos)
            if question:
                questions.append(question)
        
        return ExtractionResult.from_questions(questions, "azure_paragraph_extractor")
    
    def _extract_single_question(
        self, 
        paragraphs: List[Dict[str, Any]], 
        position: int, 
        number: int,
        next_position: Optional[int]
    ) -> Optional[Question]:
        """Extrai uma única questão"""
        
        try:
            question_content = paragraphs[position].get('content', '')
            
            # Extrai enunciado
            statement = self.statement_extractor.extract_statement(question_content)
            
            if not statement:
                logger.warning(f"Enunciado vazio para questão {number}")
                return None
            
            # Extrai alternativas
            alternatives = self.alternative_extractor.extract_alternatives(
                paragraphs, position, next_position
            )
            
            logger.debug(f"Questão {number}: {len(alternatives)} alternativas extraídas")
            
            return Question(
                number=number,
                statement=statement,
                alternatives=alternatives
            )
            
        except Exception as e:
            logger.error(f"Erro ao extrair questão {number}: {str(e)}")
            return None

# ==============================================================================
# FACTORY (Seguindo Dependency Inversion e Single Responsibility)
# ==============================================================================

class QuestionExtractionFactory:
    """Factory para criar extractors configurados"""
    
    @staticmethod
    def create_azure_paragraph_extractor() -> QuestionExtractor:
        """Cria extrator padrão para parágrafos do Azure"""
        
        question_detector = RegexQuestionDetector()
        statement_extractor = StandardStatementExtractor()
        alternative_extractor = HybridAlternativeExtractor()
        
        return AzureParagraphQuestionExtractor(
            question_detector=question_detector,
            statement_extractor=statement_extractor,
            alternative_extractor=alternative_extractor
        )
    
    @staticmethod
    def create_custom_extractor(
        question_detector: QuestionDetector,
        statement_extractor: StatementExtractor,
        alternative_extractor: AlternativeExtractor
    ) -> QuestionExtractor:
        """Cria extrator personalizado (para extensibilidade)"""
        
        return AzureParagraphQuestionExtractor(
            question_detector=question_detector,
            statement_extractor=statement_extractor,
            alternative_extractor=alternative_extractor
        )

# ==============================================================================
# FUNÇÃO DE CONVENIÊNCIA (Compatibilidade com código existente)
# ==============================================================================

def extract_questions_from_azure_paragraphs(paragraphs: List[Dict[str, Any]]) -> ExtractionResult:
    """
    Função de conveniência para extrair questões dos parágrafos do Azure
    
    Esta função mantém compatibilidade com o código existente enquanto
    usa a nova implementação baseada em SOLID principles.
    
    Args:
        paragraphs: Lista de parágrafos do Azure Document Intelligence
        
    Returns:
        Resultado da extração com todas as questões
    """
    extractor = QuestionExtractionFactory.create_azure_paragraph_extractor()
    return extractor.extract_questions(paragraphs)

# ==============================================================================
# UTILIDADES DE CONVERSÃO (Para integração com sistema existente)
# ==============================================================================

def convert_to_dict_format(extraction_result: ExtractionResult) -> List[Dict[str, Any]]:
    """
    Converte o resultado da extração para o formato dict esperado pelo sistema
    
    Facilita a migração gradual sem quebrar o código existente.
    """
    questions_dict = []
    
    for question in extraction_result.questions:
        question_dict = {
            "number": question.number,
            "question": question.statement,
            "type": question.question_type,
            "alternatives": [
                {
                    "letter": alt.id,
                    "text": alt.text
                }
                for alt in question.alternatives
            ],
            "is_multiple_choice": question.is_multiple_choice
        }
        questions_dict.append(question_dict)
    
    return questions_dict
