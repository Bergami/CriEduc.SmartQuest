"""
Testes unitários para InternalDocumentResponse
"""

import pytest
from pydantic import ValidationError
from app.models.internal.document_models import InternalDocumentResponse, InternalDocumentMetadata
from app.models.internal.question_models import InternalQuestion, InternalAnswerOption, InternalQuestionContent
from app.models.internal.context_models import InternalContextBlock, InternalContextContent
from app.models.internal.image_models import InternalImageData


class TestInternalDocumentResponse:
    """Testes para o modelo InternalDocumentResponse"""
    
    def test_create_with_valid_data(self):
        """Testa criação com dados válidos"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student="João Silva",
            school="UMEF Exemplo",
            subject="Matemática",
            teacher="Prof. Maria"
        )
        
        question_content = InternalQuestionContent(statement="Qual é a soma de 2 + 2?")
        answer_option = InternalAnswerOption(label="B", text="4", is_correct=True)
        question = InternalQuestion(
            number=1,
            content=question_content,
            options=[answer_option]
        )
        
        context_content = InternalContextContent(description=["Resolva as questões a seguir"])
        context_block = InternalContextBlock(
            id=1,
            content=context_content,
            type=["instruction"]
        )
        
        # Act
        response = InternalDocumentResponse(
            email="test@example.com",
            document_id="doc_123",
            filename="test.pdf",
            document_metadata=metadata,
            questions=[question],
            context_blocks=[context_block]
        )
        
        # Assert
        assert response.email == "test@example.com"
        assert response.document_id == "doc_123"
        assert response.filename == "test.pdf"
        assert response.document_metadata.student == "João Silva"
        assert len(response.questions) == 1
        assert len(response.context_blocks) == 1
        assert response.questions[0].number == 1
        assert response.context_blocks[0].id == 1
    
    def test_create_with_empty_lists(self):
        """Testa criação com listas vazias"""
        # Arrange
        metadata = InternalDocumentMetadata(
            subject="Teste",
            school="Escola Teste"
        )
        
        # Act
        response = InternalDocumentResponse(
            email="empty@example.com",
            document_id="doc_empty",
            filename="empty.pdf",
            document_metadata=metadata,
            questions=[],
            context_blocks=[],
            all_images=[]
        )
        
        # Assert
        assert response.email == "empty@example.com"
        assert len(response.questions) == 0
        assert len(response.context_blocks) == 0
        assert len(response.all_images) == 0
    
    def test_create_with_multiple_questions(self):
        """Testa criação com múltiplas questões"""
        # Arrange
        metadata = InternalDocumentMetadata(subject="Matemática")
        
        questions = []
        for i in range(1, 4):
            content = InternalQuestionContent(statement=f"Questão {i}")
            option = InternalAnswerOption(label="A", text=f"Resposta {i}", is_correct=True)
            question = InternalQuestion(
                number=i,
                content=content,
                options=[option]
            )
            questions.append(question)
        
        # Act
        response = InternalDocumentResponse(
            email="multi@example.com",
            document_id="doc_multi",
            filename="multi.pdf",
            document_metadata=metadata,
            questions=questions
        )
        
        # Assert
        assert len(response.questions) == 3
        assert response.questions[0].number == 1
        assert response.questions[1].number == 2
        assert response.questions[2].number == 3
    
    def test_create_with_multiple_context_blocks(self):
        """Testa criação com múltiplos blocos de contexto"""
        # Arrange
        metadata = InternalDocumentMetadata(subject="Português")
        
        contexts = []
        for i in range(1, 5):
            content = InternalContextContent(description=[f"Contexto {i}"])
            context = InternalContextBlock(
                id=i,
                content=content,
                type=["text"]
            )
            contexts.append(context)
        
        # Act
        response = InternalDocumentResponse(
            email="context@example.com",
            document_id="doc_context",
            filename="context.pdf",
            document_metadata=metadata,
            context_blocks=contexts
        )
        
        # Assert
        assert len(response.context_blocks) == 4
        assert response.context_blocks[0].id == 1
        assert response.context_blocks[3].id == 4
    
    def test_create_with_multiple_images(self):
        """Testa criação com múltiplas imagens"""
        # Arrange
        metadata = InternalDocumentMetadata(subject="Biologia")
        
        images = []
        for i in range(1, 4):
            image = InternalImageData(
                id=f"img_{i}",
                file_path=f"/path/image_{i}.png",
                base64_data=f"base64_data_{i}",
                page=1,
                category="content"
            )
            images.append(image)
        
        # Act
        response = InternalDocumentResponse(
            email="images@example.com",
            document_id="doc_images",
            filename="images.pdf",
            document_metadata=metadata,
            all_images=images
        )
        
        # Assert
        assert len(response.all_images) == 3
        assert response.all_images[0].id == "img_1"
        assert response.all_images[2].id == "img_3"
    
    def test_validation_requires_metadata(self):
        """Testa que document_metadata é obrigatório"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                email="test@example.com",
                document_id="doc_test",
                filename="test.pdf"
                # Sem document_metadata
            )
        assert "document_metadata" in str(exc_info.value)
    
    def test_validation_requires_core_fields(self):
        """Testa que campos principais são obrigatórios"""
        metadata = InternalDocumentMetadata()
        
        # Test missing email
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                document_id="doc_test",
                filename="test.pdf",
                document_metadata=metadata
            )
        assert "email" in str(exc_info.value)
        
        # Test missing document_id
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                email="test@example.com",
                filename="test.pdf",
                document_metadata=metadata
            )
        assert "document_id" in str(exc_info.value)
        
        # Test missing filename
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentResponse(
                email="test@example.com",
                document_id="doc_test",
                document_metadata=metadata
            )
        assert "filename" in str(exc_info.value)
    
    def test_to_dict_method(self):
        """Testa método dict()"""
        # Arrange
        metadata = InternalDocumentMetadata(subject="Teste")
        
        content = InternalQuestionContent(statement="Teste question")
        option = InternalAnswerOption(label="A", text="Teste", is_correct=True)
        question = InternalQuestion(number=1, content=content, options=[option])
        
        response = InternalDocumentResponse(
            email="dict@example.com",
            document_id="doc_dict",
            filename="dict.pdf",
            document_metadata=metadata,
            questions=[question]
        )
        
        # Act
        result_dict = response.dict()
        
        # Assert
        assert isinstance(result_dict, dict)
        assert result_dict["email"] == "dict@example.com"
        assert result_dict["document_id"] == "doc_dict"
        assert result_dict["filename"] == "dict.pdf"
        assert "document_metadata" in result_dict
        assert "questions" in result_dict
        assert len(result_dict["questions"]) == 1
    
    def test_model_serialization(self):
        """Testa serialização do modelo"""
        # Arrange
        metadata = InternalDocumentMetadata(
            subject="Serialization Test",
            school="Test School"
        )
        
        response = InternalDocumentResponse(
            email="serialize@example.com",
            document_id="doc_serialize",
            filename="serialize.pdf",
            document_metadata=metadata,
            extracted_text="Sample extracted text",
            provider_metadata={"source": "azure", "confidence": 0.95}
        )
        
        # Act
        json_str = response.json()
        dict_data = response.dict()
        
        # Assert
        assert isinstance(json_str, str)
        assert isinstance(dict_data, dict)
        assert "serialize@example.com" in json_str
        assert "doc_serialize" in json_str
        assert dict_data["email"] == "serialize@example.com"
        assert dict_data["extracted_text"] == "Sample extracted text"
        assert dict_data["provider_metadata"]["source"] == "azure"
    
    def test_helper_methods(self):
        """Testa métodos auxiliares do modelo"""
        # Arrange
        metadata = InternalDocumentMetadata()
        
        header_image = InternalImageData(
            id="header_1",
            file_path="/header.png",
            base64_data="header_data",
            page=1,
            category="header"
        )
        
        content_image = InternalImageData(
            id="content_1",
            file_path="/content.png",
            base64_data="content_data",
            page=1,
            category="content"
        )
        
        metadata.header_images = [header_image]
        metadata.content_images = [content_image]
        
        response = InternalDocumentResponse(
            email="helper@example.com",
            document_id="doc_helper",
            filename="helper.pdf",
            document_metadata=metadata,
            all_images=[header_image, content_image]
        )
        
        # Act & Assert
        header_imgs = response.get_header_images()
        content_imgs = response.get_content_images()
        page_imgs = response.get_images_by_page(1)
        summary = response.get_categorization_summary()
        
        assert len(header_imgs) == 1
        assert len(content_imgs) == 1
        assert len(page_imgs) == 2
        assert header_imgs[0].id == "header_1"
        assert content_imgs[0].id == "content_1"
        assert summary["total_images"] == 2
        assert summary["header_images"] == 1
        assert summary["content_images"] == 1