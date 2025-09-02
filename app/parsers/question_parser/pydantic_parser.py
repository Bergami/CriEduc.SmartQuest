"""
PydanticQuestionParser - Parser Pydantic para questões

Parser Pydantic nativo que elimina conversões Dict→Pydantic,
retornando diretamente modelos Pydantic internos.

FASE 1, ETAPA 1.2 da migração Pydantic completa.
"""

from typing import Dict, Any, Optional, List, Tuple
from app.models.internal.question_models import InternalQuestion, InternalQuestionContent, InternalAnswerOption
from app.models.internal.context_models import InternalContextBlock

# Importar funções de parsing existentes (reutilizar lógica)
from .detect_context_blocks import detect_context_blocks
from .detect_questions import detect_questions
from .match_context_to_questions import match_context_to_questions
from .context_question_mapper import ContextQuestionMapper
from .context_block_image_processor import ContextBlockImageProcessor


class PydanticQuestionParser:
    """
    Parser Pydantic nativo para questões e contextos.
    
    Retorna diretamente modelos Pydantic internos, eliminando
    a necessidade de conversões Dict→Pydantic posteriores.
    """
    
    @staticmethod
    def parse(
        text: str, 
        image_data: Optional[Dict[str, str]] = None
    ) -> Tuple[List[InternalContextBlock], List[InternalQuestion]]:
        """
        Extrai questões e blocos de contexto diretamente como modelos Pydantic.
        
        Args:
            text: Texto a ser analisado
            image_data: Dicionário opcional de imagens (id -> base64_data)
            
        Returns:
            Tuple com (context_blocks, questions) como modelos Pydantic
        """
        # 1. Usar funções existentes para detecção (retornam Dict)
        context_blocks_dict = detect_context_blocks(text)
        questions_dict = detect_questions(text)
        
        # 2. Aplicar mapeamento inteligente
        linked_questions_dict = match_context_to_questions(questions_dict, context_blocks_dict, text)
        improved_questions_dict = ContextQuestionMapper.map_contexts_to_questions(
            text, linked_questions_dict, context_blocks_dict
        )
        
        # 3. CONVERSÃO PARA MODELOS PYDANTIC (antes do enriquecimento com imagens)
        context_blocks_pydantic = PydanticQuestionParser._convert_context_blocks_to_pydantic(
            context_blocks_dict
        )
        
        questions_pydantic = PydanticQuestionParser._convert_questions_to_pydantic(
            improved_questions_dict
        )
        
        # 4. Enriquecer com imagens se disponíveis (depois da conversão Pydantic)
        if image_data:
            context_blocks_pydantic = PydanticQuestionParser._associate_images_to_context_blocks(
                context_blocks_pydantic, image_data
            )
            
            # Salvar imagens para depuração
            ContextBlockImageProcessor.save_images_to_file(image_data, "tests/extracted_images")
        
        return context_blocks_pydantic, questions_pydantic
    
    @staticmethod
    def _convert_context_blocks_to_pydantic(
        context_blocks_dict: List[Dict[str, Any]]
    ) -> List[InternalContextBlock]:
        """
        Converte blocos de contexto Dict para modelos Pydantic.
        
        Args:
            context_blocks_dict: Lista de dicionários de contexto
            
        Returns:
            Lista de InternalContextBlock
        """
        context_blocks = []
        
        for block_dict in context_blocks_dict:
            try:
                # 🔧 CORREÇÃO: Usar método correto from_legacy_context_block
                context_block = InternalContextBlock.from_legacy_context_block(block_dict)
                context_blocks.append(context_block)
                
            except Exception as e:
                # Log do erro e criar contexto básico
                from app.core.logging import structured_logger
                from app.core.constants.content_types import ContentType
                
                structured_logger.warning(
                    f"Erro ao converter context block para Pydantic: {str(e)}",
                    context={"block_dict": block_dict}
                )
                
                # 🔧 CORREÇÃO: Criar contexto básico com tipos corretos
                # Processar field type corretamente
                block_type = block_dict.get("type", ["text"])
                if isinstance(block_type, str):
                    block_type = [block_type]
                
                # Converter para ContentType enum com fallback
                try:
                    type_enums = []
                    for t in block_type:
                        try:
                            type_enums.append(ContentType(t))
                        except ValueError:
                            type_enums.append(ContentType.TEXT)  # Fallback para tipos desconhecidos
                except:
                    type_enums = [ContentType.TEXT]
                
                # Criar conteúdo estruturado
                from app.models.internal.context_models import InternalContextContent
                fallback_content = InternalContextContent(
                    description=[str(block_dict.get("paragraphs", []))],
                    processing_notes=f"Fallback conversion due to error: {str(e)}"
                )
                
                fallback_context = InternalContextBlock(
                    id=block_dict.get("id", 0),
                    type=type_enums,
                    title=block_dict.get("title", ""),
                    statement=block_dict.get("statement", ""),
                    content=fallback_content,
                    has_image=block_dict.get("hasImage", False),
                    extraction_method="pydantic_parser_fallback",
                    processing_notes=f"Fallback conversion due to error: {str(e)}"
                )
                context_blocks.append(fallback_context)
        
        return context_blocks
    
    @staticmethod
    def _convert_questions_to_pydantic(
        questions_dict: List[Dict[str, Any]]
    ) -> List[InternalQuestion]:
        """
        Converte questões Dict para modelos Pydantic.
        
        Args:
            questions_dict: Lista de dicionários de questões
            
        Returns:
            Lista de InternalQuestion
        """
        questions = []
        
        for question_dict in questions_dict:
            try:
                # Usar método de conversão do modelo Pydantic
                question = InternalQuestion.from_legacy_question(question_dict)
                
                # Adicionar informações de extração
                question.extraction_method = "pydantic_parser"
                question.processing_notes = "Extracted with PydanticQuestionParser"
                
                questions.append(question)
                
            except Exception as e:
                # Log do erro e criar questão básica
                from app.core.logging import structured_logger
                structured_logger.warning(
                    f"Erro ao converter question para Pydantic: {str(e)}",
                    context={"question_dict": question_dict}
                )
                
                # Criar questão básica como fallback
                fallback_content = InternalQuestionContent(
                    statement=str(question_dict.get("content", "Questão não processada")),
                    processing_notes=f"Fallback conversion due to error: {str(e)}"
                )
                
                fallback_question = InternalQuestion(
                    number=question_dict.get("number", 0),
                    content=fallback_content,
                    extraction_method="pydantic_parser_fallback",
                    processing_notes=f"Fallback conversion due to error: {str(e)}"
                )
                questions.append(fallback_question)
        
        return questions
    
    @staticmethod
    def parse_legacy_format(
        text: str, 
        image_data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Parse retornando formato legacy para compatibilidade.
        
        Args:
            text: Texto a ser analisado
            image_data: Dicionário opcional de imagens
            
        Returns:
            Dicionário no formato legacy
        """
        context_blocks, questions = PydanticQuestionParser.parse(text, image_data)
        
        # Converter de volta para formato legacy
        return {
            "context_blocks": [block.to_legacy_format() for block in context_blocks],
            "questions": [question.to_legacy_format() for question in questions]
        }
    
    @staticmethod
    def _associate_images_to_context_blocks(
        context_blocks: List[InternalContextBlock], 
        image_data: Any
    ) -> List[InternalContextBlock]:
        """
        Associa imagens aos blocos de contexto após conversão Pydantic.
        
        Args:
            context_blocks: Lista de InternalContextBlock
            image_data: Lista de InternalImageData ou dicionário de imagens
            
        Returns:
            Lista de InternalContextBlock com imagens associadas
        """
        if not image_data:
            return context_blocks
        
        from app.core.logging import structured_logger
        
        # Converter image_data para dict se necessário
        if isinstance(image_data, list):
            # Se é lista de InternalImageData
            if image_data and hasattr(image_data[0], 'figure_id'):
                image_dict = {img.figure_id: img.image_base64 for img in image_data}
            else:
                # Se é lista de strings base64
                image_dict = {str(i): img for i, img in enumerate(image_data)}
        elif isinstance(image_data, dict):
            image_dict = image_data
        else:
            structured_logger.error(f"Unsupported image_data type: {type(image_data)}")
            return context_blocks
        
        structured_logger.info(f"Associating {len(image_dict)} images to {len(context_blocks)} context blocks")
        
        # Associar imagens aos blocos que têm has_image=True
        for block in context_blocks:
            if block.has_image and image_dict:
                # Pegar a primeira imagem disponível
                image_id = next(iter(image_dict.keys()))
                
                # Usar o método add_image_association do modelo
                block.add_image_association(image_id)
                
                # Remover da lista para não usar novamente
                image_dict.pop(image_id)
                
                structured_logger.info(f"Associated image {image_id} to context block {block.id}")
        
        return context_blocks
