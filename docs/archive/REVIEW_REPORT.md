🔁 1. Duplicação de Código
1.1 Lógica de Hash Duplicada
Localização: app/models/persistence/question.py e app/services/persistence/question_service.py

Problema:
A lógica de geração de hash aparece em dois lugares:

# Em question.py (método de modelo)

def generate_content_hash(self) -> str:
content = {
"text": self.text,
"alternatives": sorted([
{"text": alt.text, "is_correct": alt.is_correct}
for alt in self.alternatives
], key=lambda x: x["text"])
}
content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

# Em question_service.py (método estático)

@staticmethod
def \_generate_content_hash(question_data: dict) -> str:
content = {
"text": question_data.get("text", ""),
"alternatives": sorted([
{"text": alt.get("text", ""), "is_correct": alt.get("is_correct", False)}
for alt in question_data.get("alternatives", [])
], key=lambda x: x["text"])
}
content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

Impacto: Duplicação de lógica dificulta manutenção e pode levar a inconsistências.

Sugestão:
Centralizar em um único local, preferencialmente no modelo:

# Em question.py

@staticmethod
def calculate_content_hash(text: str, alternatives: List[dict]) -> str:
"""Calculate content hash for deduplication."""
content = {
"text": text,
"alternatives": sorted([
{"text": alt["text"], "is_correct": alt["is_correct"]}
for alt in alternatives
], key=lambda x: x["text"])
}
content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

def generate_content_hash(self) -> str:
"""Generate hash from current instance data."""
alternatives_data = [
{"text": alt.text, "is_correct": alt.is_correct}
for alt in self.alternatives
]
return self.calculate_content_hash(self.text, alternatives_data)

1.2 Tratamento de Exceções Repetido
Localização: app/services/persistence/question_service.py

Problema:
Padrão de tratamento de exceção repetido em múltiplos métodos:

except Exception as e:
self.logger.error(f"Error in method_name: {str(e)}")
raise

Sugestão:
Criar um decorator para tratamento padronizado:

from functools import wraps
from typing import Callable, Any

def handle_service_errors(operation_name: str) -> Callable:
"""Decorator for standardized error handling in service methods."""
def decorator(func: Callable) -> Callable:
@wraps(func)
async def wrapper(self, *args, \*\*kwargs) -> Any:
try:
return await func(self, *args, \*\*kwargs)
except Exception as e:
self.logger.error(f"Error in {operation_name}: {str(e)}")
raise
return wrapper
return decorator

# Uso:

@handle_service_errors("save_question")
async def save_question(self, question: Question, request_id: str) -> Question: # implementação

🧱 2. Responsabilidade Única (SRP)
2.1 QuestionService Acumula Múltiplas Responsabilidades
Localização: app/services/persistence/question_service.py

Problema:
O QuestionService está responsável por:

Persistência de questões
Detecção de duplicatas
Geração de hashes
Validação de dados
Logging detalhado
Sugestão:
Separar em classes especializadas:

# app/services/persistence/deduplication_service.py

class QuestionDeduplicationService:
"""Service specialized in question deduplication."""

    def __init__(self, repository: IQuestionRepository):
        self.repository = repository

    async def check_duplicate(
        self,
        content_hash: str,
        exam_id: str
    ) -> Optional[Question]:
        """Check if question is duplicate."""
        return await self.repository.find_by_content_hash(
            content_hash,
            exam_id
        )

    async def find_similar_questions(
        self,
        content_hash: str,
        limit: int = 5
    ) -> List[Question]:
        """Find similar questions across all exams."""
        return await self.repository.find_similar_by_hash(
            content_hash,
            limit
        )

# app/services/persistence/question_service.py

class QuestionService:
"""Service for question persistence operations."""

    def __init__(
        self,
        repository: IQuestionRepository,
        deduplication_service: QuestionDeduplicationService,
        logger: Logger
    ):
        self.repository = repository
        self.deduplication = deduplication_service
        self.logger = logger

    async def save_question(
        self,
        question: Question,
        request_id: str
    ) -> Question:
        """Save question with deduplication check."""
        # Simplified logic focusing on persistence
        duplicate = await self.deduplication.check_duplicate(
            question.content_hash,
            question.exam_id
        )

        if duplicate:
            self.logger.info(f"Duplicate found: {duplicate.id}")
            return duplicate

        return await self.repository.save(question)

2.2 QuestionProcessor Mistura Orquestração e Lógica de Negócio
Localização: app/services/core/question_processor.py

Problema:
O método process_questions está muito extenso e mistura:

Orquestração de fluxo
Transformação de dados
Logging detalhado
Tratamento de erros
Sugestão:
Extrair métodos privados para responsabilidades específicas:

class QuestionProcessor:
async def process_questions(
self,
extracted_questions: List[ExtractedQuestion],
exam_id: str,
request_id: str
) -> ProcessedQuestionsResponse:
"""Process and save questions with deduplication."""
self.\_log_processing_start(len(extracted_questions), exam_id, request_id)

        results = await self._process_all_questions(
            extracted_questions,
            exam_id,
            request_id
        )

        stats = self._calculate_statistics(results)
        self._log_processing_summary(stats, request_id)

        return self._build_response(results, stats)

    async def _process_all_questions(
        self,
        extracted_questions: List[ExtractedQuestion],
        exam_id: str,
        request_id: str
    ) -> List[ProcessingResult]:
        """Process all questions and collect results."""
        results = []
        for idx, extracted in enumerate(extracted_questions, 1):
            result = await self._process_single_question(
                extracted,
                exam_id,
                request_id,
                idx
            )
            results.append(result)
        return results

    def _calculate_statistics(
        self,
        results: List[ProcessingResult]
    ) -> Dict[str, int]:
        """Calculate processing statistics."""
        return {
            "total": len(results),
            "saved": sum(1 for r in results if r.status == "saved"),
            "duplicates": sum(1 for r in results if r.status == "duplicate"),
            "failed": sum(1 for r in results if r.status == "failed")
        }

3.  Código Morto ou Desnecessário
    3.1 Imports Não Utilizados
    Localização: test_deduplication.py

Problema:

import sys
import os

# sys e os não são utilizados no código

Sugestão:
Remover imports não utilizados.

3.2 Variáveis Não Utilizadas
Localização: app/services/persistence/question_service.py

Problema:

async def save_question(self, question: Question, request_id: str) -> Question: # request_id é logado mas não usado para rastreamento real

Sugestão:
Se request_id não é usado para correlação, considerar removê-lo ou implementar uso consistente para rastreamento distribuído.

3.3 Código Comentado
Localização: Múltiplos arquivos

Problema:
Presença de código comentado que deveria estar no histórico do Git:

# Old implementation removed

# def old_method():

# pass

Sugestão:
Remover código comentado e confiar no controle de versão.

💬 4. Comentários
4.1 Comentários Redundantes
Localização: app/services/persistence/question_service.py

Problema:

# Check for duplicates

duplicate = await self.\_check_duplicate(...)

# Save question

saved = await self.repository.save(question)

Sugestão:
Remover comentários óbvios. O código deve ser autoexplicativo:

duplicate = await self.\_check_duplicate(...)
if duplicate:
return duplicate

return await self.repository.save(question)

4.2 Docstrings Incompletas
Localização: Múltiplos métodos

Problema:
Faltam docstrings em vários métodos ou estão incompletas:

def \_generate_content_hash(question_data: dict) -> str: # Sem docstring explicando formato esperado de question_data

Sugestão:
Adicionar docstrings completas conforme PEP 257:  
def \_generate_content_hash(question_data: dict) -> str:
"""Generate SHA-256 hash from question content.

    Args:
        question_data: Dictionary containing:
            - text (str): Question text
            - alternatives (List[dict]): List of alternatives with 'text' and 'is_correct'

    Returns:
        str: 64-character hexadecimal SHA-256 hash

    Example:
        >>> data = {
        ...     "text": "What is 2+2?",
        ...     "alternatives": [
        ...         {"text": "4", "is_correct": True},
        ...         {"text": "5", "is_correct": False}
        ...     ]
        ... }
        >>> hash_value = _generate_content_hash(data)
        >>> len(hash_value)
        64
    """

4.3 Comentários Desatualizados
Localização: app/models/persistence/question.py

Problema:
Comentários que não refletem o estado atual do código após refatorações.

Sugestão:
Revisar e atualizar ou remover comentários desatualizados durante refatorações.

🧪 5. Testabilidade
5.1 Testes Focados Apenas em Caminho Feliz
Localização: tests/unit/services/persistence/test_question_service.py

Problema:
Testes existentes cobrem principalmente cenários de sucesso:

async def test_save_question_success(self): # Apenas testa o caso de sucesso

ugestão:
Adicionar testes para casos de borda e falhas:
class TestQuestionServiceEdgeCases:
"""Test edge cases and failure scenarios."""

    async def test_save_question_with_empty_text(self):
        """Test saving question with empty text."""
        question = Question(text="", alternatives=[], exam_id="exam1")
        with pytest.raises(ValidationError):
            await service.save_question(question, "req-1")

    async def test_save_question_with_no_alternatives(self):
        """Test saving question without alternatives."""
        question = Question(text="Question?", alternatives=[], exam_id="exam1")
        with pytest.raises(ValidationError):
            await service.save_question(question, "req-1")

    async def test_save_question_with_all_incorrect_alternatives(self):
        """Test question with no correct alternative."""
        question = Question(
            text="Question?",
            alternatives=[
                Alternative(text="A", is_correct=False),
                Alternative(text="B", is_correct=False)
            ],
            exam_id="exam1"
        )
        with pytest.raises(ValidationError):
            await service.save_question(question, "req-1")

    async def test_save_question_database_connection_failure(self):
        """Test handling of database connection errors."""
        mock_repo.save.side_effect = ConnectionError("DB unavailable")
        question = create_valid_question()

        with pytest.raises(ConnectionError):
            await service.save_question(question, "req-1")

    async def test_duplicate_check_with_hash_collision(self):
        """Test behavior with hash collision (rare but possible)."""
        # Simulate hash collision scenario
        pass

    async def test_save_question_with_duplicate_alternatives(self):
        """Test question with duplicate alternative texts."""
        question = Question(
            text="Question?",
            alternatives=[
                Alternative(text="Same", is_correct=True),
                Alternative(text="Same", is_correct=False)
            ],
            exam_id="exam1"
        )
        # Should this be allowed or rejected?
        result = await service.save_question(question, "req-1")
        # Add assertions

    async def test_concurrent_duplicate_saves(self):
        """Test race condition when saving duplicates concurrently."""
        import asyncio
        question = create_valid_question()

        results = await asyncio.gather(
            service.save_question(question, "req-1"),
            service.save_question(question, "req-2"),
            service.save_question(question, "req-3")
        )

        # All should return the same question (only one saved)
        assert len(set(r.id for r in results)) == 1

5.2 Dependências Difíceis de Mockar
Localização: app/services/core/question_processor.py

Problema:
Dependências diretas dificultam testes isolados:

class QuestionProcessor:
def **init**(self, question_service: QuestionService, logger: Logger):
self.question_service = question_service
self.logger = logger

Sugestão:
Usar injeção de dependência via interfaces:

class QuestionProcessor:
def **init**(
self,
question_service: IQuestionService, # Interface em vez de implementação
logger: ILogger
):
self.question_service = question_service
self.logger = logger

5.3 Falta de Testes de Integração
Problema:
Não há testes que validem o fluxo completo de detecção de duplicatas com MongoDB real.

Sugestão:
Adicionar testes de integração:

# tests/integration/test_deduplication_flow.py

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from testcontainers.mongodb import MongoDbContainer

@pytest.mark.integration
class TestDeduplicationIntegration:
"""Integration tests for deduplication with real MongoDB."""

    @pytest.fixture(scope="class")
    async def mongodb_container(self):
        """Start MongoDB container for testing."""
        with MongoDbContainer("mongo:7.0") as mongo:
            yield mongo

    @pytest.fixture
    async def db_client(self, mongodb_container):
        """Create MongoDB client."""
        client = AsyncIOMotorClient(mongodb_container.get_connection_url())
        yield client
        await client.drop_database("test_db")
        client.close()

    async def test_duplicate_detection_with_real_db(self, db_client):
        """Test duplicate detection with real MongoDB instance."""
        repository = MongoQuestionRepository(db_client, "test_db")
        service = QuestionService(repository, logger)

        question1 = create_question("What is 2+2?")
        question2 = create_question("What is 2+2?")  # Duplicate

        saved1 = await service.save_question(question1, "req-1")
        saved2 = await service.save_question(question2, "req-2")

        assert saved1.id == saved2.id

        # Verify only one document in database
        count = await repository.count_by_exam(question1.exam_id)
        assert count == 1

5.4 Cobertura de Testes Insuficiente
Áreas Críticas Sem Testes:

question_extraction_service.py - Sem testes unitários
Cenários de erro na camada de controller
Validação de hash em casos extremos
Performance com grandes volumes de dados
Sugestão:
Estabelecer meta de cobertura mínima de 80% e adicionar testes para áreas críticas.

🧠 6. Clareza e Legibilidade
6.1 Nomes de Variáveis Pouco Descritivos
Localização: app/services/persistence/question_service.py

Problema:
async def save_question(self, question: Question, request_id: str) -> Question:
h = question.content_hash # 'h' não é descritivo
dup = await self.\_check_duplicate(h, question.exam_id) # 'dup' abreviado

Sugestão:
async def save_question(self, question: Question, request_id: str) -> Question:
content_hash = question.content_hash
existing_question = await self.\_check_duplicate(content_hash, question.exam_id)

    if existing_question:
        self.logger.info(
            f"Duplicate question found. "
            f"Original ID: {existing_question.id}, "
            f"Request: {request_id}"
        )
        return existing_question

6.2 Métodos Longos com Múltiplas Responsabilidades
Localização: app/services/core/question_processor.py

Problema:
Método process_questions com mais de 50 linhas, difícil de entender de relance.

Sugestão:
Já abordado na seção SRP - quebrar em métodos menores e mais focados.

6.3 Magic Numbers
Localização: app/services/persistence/question_service.py

Problema:

similar = await self.repository.find_similar_by_hash(content_hash, 5)

Sugestão:

DEFAULT_SIMILAR_QUESTIONS_LIMIT = 5

similar = await self.repository.find_similar_by_hash(
content_hash,
limit=DEFAULT_SIMILAR_QUESTIONS_LIMIT
)

📐 7. Arquitetura e Design
7.1 Violação do Princípio de Inversão de Dependência
Localização: app/services/core/question_processor.py

Problema:
Dependência direta de implementação concreta:

from app.services.persistence.question_service import QuestionService

class QuestionProcessor:
def **init**(self, question_service: QuestionService, ...):

Sugestão:
Depender de abstrações:

7.2 Acoplamento Entre Camadas
Problema:
A camada de serviço está fortemente acoplada ao modelo de persistência.

Sugestão:
Introduzir DTOs para transferência entre camadas:

# app/dtos/persistence/question_dto.py

from dataclasses import dataclass
from typing import List

@dataclass
class QuestionDTO:
"""Data transfer object for question data."""
text: str
alternatives: List[AlternativeDTO]
exam_id: str
content_hash: Optional[str] = None

    def to_domain_model(self) -> Question:
        """Convert DTO to domain model."""
        return Question(
            text=self.text,
            alternatives=[alt.to_domain_model() for alt in self.alternatives],
            exam_id=self.exam_id,
            content_hash=self.content_hash
        )

7.3 Falta de Padrão Repository Completo
Problema:
O repository não implementa todos os métodos esperados de um padrão Repository completo.

Sugestão:
Definir interface completa:

# app/core/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Optional

class IQuestionRepository(ABC):
"""Repository interface for question persistence."""

    @abstractmethod
    async def save(self, question: Question) -> Question:
        """Save or update a question."""
        pass

    @abstractmethod
    async def find_by_id(self, question_id: str) -> Optional[Question]:
        """Find question by ID."""
        pass

    @abstractmethod
    async def find_by_exam(self, exam_id: str) -> List[Question]:
        """Find all questions for an exam."""
        pass

    @abstractmethod
    async def find_by_content_hash(
        self,
        content_hash: str,
        exam_id: str
    ) -> Optional[Question]:
        """Find question by content hash within an exam."""
        pass

    @abstractmethod
    async def delete(self, question_id: str) -> bool:
        """Delete a question."""
        pass

    @abstractmethod
    async def exists(self, question_id: str) -> bool:
        """Check if question exists."""
        pass

    @abstractmethod
    async def count_by_exam(self, exam_id: str) -> int:
        """Count questions in an exam."""
        pass

7.4 Ausência de Padrão Unit of Work
Problema:
Não há controle transacional quando múltiplas operações precisam ser atômicas.

Sugestão:
Considerar implementar Unit of Work para operações que envolvem múltiplas entidades:

# app/core/unit_of_work.py

from abc import ABC, abstractmethod
from typing import AsyncContextManager

class IUnitOfWork(ABC, AsyncContextManager):
"""Unit of Work pattern for transactional operations."""

    questions: IQuestionRepository
    exams: IExamRepository

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes."""
        pass

# Uso:

async with unit_of_work:
question = await unit_of_work.questions.save(question_data)
await unit_of_work.exams.update_question_count(exam_id)
await unit_of_work.commit()

📏 8. Conformidade com PEP 8 e PEP 257
8.1 Linhas Muito Longas
Localização: Múltiplos arquivos

Problema:  
self.logger.info(f"Processing {len(extracted_questions)} questions for exam {exam_id} (Request: {request_id})")

Sugestão:
Quebrar linhas conforme PEP 8 (limite de 88-100 caracteres com Black):
self.logger.info(
f"Processing {len(extracted_questions)} questions "
f"for exam {exam_id} (Request: {request_id})"
)

8.2 Imports Não Ordenados
Localização: Múltiplos arquivos

Problema:
Imports não seguem a ordem padrão (stdlib, third-party, local).

Sugestão:
Usar ferramenta como isort:

# Standard library

import hashlib
import json
from typing import List, Optional

# Third-party

from motor.motor_asyncio import AsyncIOMotorCollection

# Local

from app.models.persistence.question import Question
from app.core.interfaces import IQuestionRepository

8.3 Docstrings Não Conformes com PEP 257
Problema:
Inconsistência no formato de docstrings.

Sugestão:
Padronizar usando Google ou NumPy style:

def generate_content_hash(self) -> str:
"""Generate SHA-256 hash from question content.

    The hash is calculated from the question text and alternatives,
    ensuring consistent ordering for deduplication purposes.

    Returns:
        A 64-character hexadecimal string representing the SHA-256 hash.

    Example:
        >>> question = Question(text="What is 2+2?", ...)
        >>> hash_value = question.generate_content_hash()
        >>> len(hash_value)
        64
    """

8.4 Espaçamento Inconsistente
Problema:
Espaçamento inconsistente ao redor de operadores e após vírgulas.

Sugestão:
Usar formatador automático como Black:

pip install black
black app/ tests/

🧩 9. Complexidade Ciclomática
9.1 Método com Alta Complexidade
Localização: app/services/core/question_processor.py::process_questions

Problema:
Complexidade ciclomática estimada > 15 devido a múltiplos caminhos de decisão.

Análise:

async def process_questions(...): # 1. Loop principal
for idx, extracted in enumerate(extracted_questions, 1):
try: # 2. Conversão
question = ...

            # 3. Verificação de duplicata
            if not question.content_hash:
                # 4. Geração de hash
                question.content_hash = ...

            # 5. Salvamento
            saved = await self.question_service.save_question(...)

            # 6. Verificação de duplicata após salvar
            if saved.id != question.id:
                # Lógica duplicata
            else:
                # Lógica nova questão

            # 7. Tratamento de sucesso
            results.append(...)

        except Exception as e:
            # 8. Tratamento de erro
            results.append(...)

    # 9-12. Cálculo de estatísticas com múltiplas condições
    # 13-15. Logging condicional
    # 16. Construção de resposta

    Sugestão:

Refatorar usando métodos auxiliares (já sugerido na seção SRP):

async def process_questions(
self,
extracted_questions: List[ExtractedQuestion],
exam_id: str,
request_id: str
) -> ProcessedQuestionsResponse:
"""Process questions with reduced complexity."""
self.\_log_processing_start(len(extracted_questions), exam_id, request_id)

    # Complexidade reduzida delegando para métodos especializados
    results = []
    for idx, extracted in enumerate(extracted_questions, 1):
        result = await self._process_single_question(
            extracted,
            exam_id,
            request_id,
            idx
        )
        results.append(result)

    return self._build_final_response(results, request_id)

async def \_process_single_question(
self,
extracted: ExtractedQuestion,
exam_id: str,
request_id: str,
index: int
) -> ProcessingResult:
"""Process a single question (complexity ~5)."""
try:
question = self.\_convert_to_domain_model(extracted, exam_id)
saved = await self.\_save_with_deduplication(question, request_id)
return self.\_create_success_result(saved, question, index)
except Exception as e:
return self.\_create_error_result(e, index)

9.2 Condicionais Aninhadas
Localização: app/services/persistence/question_service.py

Problema:

if duplicate:
if duplicate.id != question.id:
if duplicate.exam_id == question.exam_id: # Lógica aninhada

Sugestão:
Usar retorno antecipado (early return):  
if not duplicate:
return await self.repository.save(question)

if duplicate.id == question.id:
return question

if duplicate.exam_id != question.exam_id:
raise ValueError("Hash collision across exams")

self.logger.info(f"Duplicate found: {duplicate.id}")
return duplicate

9.3 Expressões Booleanas Complexas
Problema:

if (question.content_hash and
len(question.alternatives) > 0 and
any(alt.is_correct for alt in question.alternatives) and
question.text.strip() != ""):

Sugestão:
Extrair para método com nome descritivo:

def \_is_valid_question(self, question: Question) -> bool:
"""Check if question is valid for persistence."""
has_content_hash = bool(question.content_hash)
has_alternatives = len(question.alternatives) > 0
has_correct_answer = any(alt.is_correct for alt in question.alternatives)
has_text = question.text.strip() != ""

    return all([
        has_content_hash,
        has_alternatives,
        has_correct_answer,
        has_text
    ])

# Uso:

if not self.\_is_valid_question(question):
raise ValidationError("Invalid question data")

🎯 11. Performance e Otimização
11.1 N+1 Query Problem
Localização: app/services/core/question_processor.py

Problema:
Busca de duplicatas é feita uma por vez dentro do loop:

for extracted in extracted_questions: # Cada iteração faz uma query ao banco
saved = await self.question_service.save_question(question, request_id)

Sugestão:
Implementar busca em lote:

async def process_questions_batch(
self,
extracted_questions: List[ExtractedQuestion],
exam_id: str,
request_id: str
) -> ProcessedQuestionsResponse:
"""Process questions with batch duplicate checking."""

    # Converter todas as questões
    questions = [
        self._convert_to_domain_model(eq, exam_id)
        for eq in extracted_questions
    ]

    # Buscar todas as duplicatas de uma vez
    hashes = [q.content_hash for q in questions]
    existing_questions = await self.question_service.find_by_hashes_batch(
        hashes,
        exam_id
    )

    # Mapear duplicatas
    existing_map = {q.content_hash: q for q in existing_questions}

    # Processar com base no mapa
    results = []
    for question in questions:
        if question.content_hash in existing_map:
            results.append(self._create_duplicate_result(
                existing_map[question.content_hash]
            ))
        else:
            saved = await self.question_service.save_question(
                question,
                request_id
            )
            results.append(self._create_success_result(saved))

    return self._build_response(results)

11.2 Falta de Índices no Banco
Problema:
Busca por content_hash pode ser lenta sem índice apropriado.

Sugestão:
Garantir índices no MongoDB:

# scripts/migrations/add_content_hash_index.py

async def create_indexes():
"""Create indexes for question deduplication."""
await questions_collection.create_index(
[("content_hash", 1), ("exam_id", 1)],
unique=True,
name="idx_content_hash_exam"
)

    await questions_collection.create_index(
        [("exam_id", 1)],
        name="idx_exam_id"
    )

11.3 Geração de Hash Repetida
Problema:
Hash pode ser gerado múltiplas vezes para a mesma questão.

Sugestão:
Cachear hash após primeira geração:

class Question:
def **init**(self, ...):
self.\_content_hash: Optional[str] = None

    @property
    def content_hash(self) -> str:
        """Get content hash, generating if needed."""
        if self._content_hash is None:
            self._content_hash = self.generate_content_hash()
        return self._content_hash

    @content_hash.setter
    def content_hash(self, value: str):
        """Set content hash explicitly."""
        self._content_hash = value

📊 Métricas de Código
Estatísticas Estimadas
Métrica Valor Atual Recomendado Status
Cobertura de Testes ~40% >80% ❌
Complexidade Ciclomática Média ~12 <10 ⚠️
Duplicação de Código ~8% <5% ⚠️
Linhas por Método (média) ~25 <20 ⚠️
Conformidade PEP 8 ~75% >95% ⚠️
Docstring Coverage ~60% >90% ❌
🎯 Priorização de Refatorações
Alta Prioridade (Crítico)
Adicionar testes para casos de erro e borda - Fundamental para confiabilidade
Implementar validação de entrada robusta - Previne erros e vulnerabilidades
Corrigir duplicação de lógica de hash - Evita inconsistências
Adicionar índices no MongoDB - Performance crítica
Média Prioridade (Importante)
Separar responsabilidades em QuestionService - Melhora manutenibilidade
Reduzir complexidade de process_questions - Facilita compreensão
Implementar pattern Unit of Work - Garante consistência transacional
Melhorar docstrings conforme PEP 257 - Facilita manutenção
Baixa Prioridade (Desejável)
Padronizar formatação com Black/isort - Consistência visual
Remover código comentado - Limpeza
Extrair magic numbers para constantes - Clareza
Implementar batch processing - Otimização de performance
🚀 Recomendações Finais
Pontos Positivos
✅ Implementação funcional de detecção de duplicatas
✅ Uso de type hints consistente
✅ Separação em camadas bem definida
✅ Logging estruturado para rastreabilidade

Áreas de Melhoria Críticas
Cobertura de Testes: Aumentar para pelo menos 80%, incluindo casos de erro
Validação de Dados: Implementar validação robusta em todas as camadas
Separação de Responsabilidades: Refatorar classes com múltiplas responsabilidades
Performance: Implementar busca em lote e garantir índices apropriados
Próximos Passos Sugeridos
Criar issues no GitHub para cada categoria de problema
Priorizar refatorações de alta prioridade
Estabelecer pipeline de CI/CD com verificação de:
Cobertura mínima de testes (80%)
Linting (flake8, pylint)
Formatação (black, isort)
Type checking (mypy)
Implementar code review obrigatório antes de merge
Documentar padrões de código no projeto
