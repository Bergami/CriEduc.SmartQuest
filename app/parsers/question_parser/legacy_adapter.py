#!/usr/bin/env python3
"""
Adaptador para compatibilidade com sistema antigo de extração
=============================================================

Este módulo fornece funções compatíveis com o sistema antigo,
mas utilizando a nova implementação baseada nos princípios SOLID.

Permite migração gradual sem quebrar o código existente.
"""

from typing import List, Tuple, Dict, Any
import logging
from .azure_paragraph_question_extractor import (
    extract_questions_from_azure_paragraphs,
    QuestionExtractionFactory,
    convert_to_dict_format
)

logger = logging.getLogger(__name__)

def extract_alternatives_from_question_text(question_text: str) -> Tuple[str, List[str]]:
    """
    Função de compatibilidade com o sistema antigo.
    
    Esta função mantém a mesma assinatura da função original,
    mas usa a nova implementação baseada em princípios SOLID internamente.
    
    Args:
        question_text: Texto da questão incluindo alternativas
        
    Returns:
        Tupla com (enunciado_limpo, lista_de_alternativas)
    """
    
    # Se receber texto simples, simula estrutura de parágrafos
    # para compatibilidade com a nova implementação
    mock_paragraphs = [
        {"content": question_text}
    ]
    
    try:
        # Usa novo extractor
        extractor = QuestionExtractionFactory.create_azure_paragraph_extractor()
        result = extractor.extract_questions(mock_paragraphs)
        
        if result.questions:
            question = result.questions[0]
            alternatives_text = [alt.text for alt in question.alternatives]
            return question.statement, alternatives_text
        else:
            # Fallback: retorna texto original sem alternativas
            logger.warning("Nenhuma questão detectada, retornando texto original")
            return question_text.strip(), []
            
    except Exception as e:
        logger.error(f"Erro na nova extração, usando fallback: {str(e)}")
        # Em caso de erro, retorna texto original
        return question_text.strip(), []

def extract_alternatives_from_text(text: str) -> Tuple[str, List[str]]:
    """
    Função de compatibilidade com sistema antigo.
    
    Wrapper para extract_alternatives_from_question_text para manter
    compatibilidade total com código existente.
    """
    return extract_alternatives_from_question_text(text)

def extract_questions_from_paragraphs(
    paragraphs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extrai questões dos parágrafos retornando dicionário com estrutura padrão.
    
    Args:
        paragraphs: Lista de parágrafos do Azure Document Intelligence
        
    Returns:
        Dicionário com questões e context_blocks no formato padrão do sistema
    """
    try:
        # Usa nova implementação
        result = extract_questions_from_azure_paragraphs(paragraphs)
        
        # Converte para formato dict
        questions_dict = convert_to_dict_format(result)
        
        logger.info(f"Extração SOLID: {result.total_questions} questões extraídas com sucesso")
        
        # Retorna no formato esperado pelo sistema
        return {
            "questions": questions_dict,
            "context_blocks": []  # Context blocks serão processados separadamente
        }
        
    except Exception as e:
        logger.error(f"Erro na extração SOLID: {str(e)}")
        # Em caso de erro, retorna estrutura vazia
        return {
            "questions": [],
            "context_blocks": []
        }

# Alias para compatibilidade
extract_alternatives_from_question_text_legacy = extract_alternatives_from_question_text
