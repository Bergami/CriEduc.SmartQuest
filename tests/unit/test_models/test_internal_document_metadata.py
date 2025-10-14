"""
Testes unitários para InternalDocumentMetadata
"""

import pytest
from pydantic import ValidationError
from app.models.internal.document_models import InternalDocumentMetadata
from app.models.internal.image_models import InternalImageData


class TestInternalDocumentMetadata:
    """Testes para o modelo InternalDocumentMetadata"""
    
    def test_create_with_valid_data(self):
        """Testa criação com dados válidos"""
        # Act
        metadata = InternalDocumentMetadata(
            student="João Silva",
            network="SESI",
            school="UMEF Escola Exemplo", 
            city="Belo Horizonte",
            teacher="Prof. Maria",
            subject="Matemática",
            exam_title="Prova do 3º Trimestre",
            trimester="3º Trimestre",
            grade="9º Ano",
            date="2024-01-15"
        )
        
        # Assert
        assert metadata.student == "João Silva"
        assert metadata.network == "SESI"
        assert metadata.school == "UMEF Escola Exemplo"
        assert metadata.subject == "Matemática"
        assert metadata.city == "Belo Horizonte"
        assert metadata.teacher == "Prof. Maria"
    
    def test_create_with_unicode_characters(self):
        """Testa criação com caracteres unicode/acentos"""
        # Act
        metadata = InternalDocumentMetadata(
            student="José da Silva Araújo",
            network="PREFEITURA DE VILA VELHA",
            school="UMEF Saturnino Rangel Mauro",
            city="São Paulo",
            teacher="Profª. Cláudia",
            subject="Educação Física",
            exam_title="Avaliação Diagnóstica",
            date="15/01/2024"
        )
        
        # Assert
        assert metadata.student == "José da Silva Araújo"
        assert metadata.subject == "Educação Física"
        assert metadata.school == "UMEF Saturnino Rangel Mauro"
        assert metadata.city == "São Paulo"
    
    def test_create_with_optional_fields_none(self):
        """Testa criação com campos opcionais None"""
        # Act
        metadata = InternalDocumentMetadata()
        
        # Assert - todos os campos são opcionais
        assert metadata.student is None
        assert metadata.network is None
        assert metadata.school is None
        assert metadata.subject is None
        assert metadata.city is None
        assert metadata.teacher is None
        assert metadata.header_images == []
        assert metadata.content_images == []
        
    def test_create_with_different_date_formats(self):
        """Testa criação com diferentes formatos de data"""
        # Test case 1: Formato ISO
        metadata1 = InternalDocumentMetadata(
            date="2024-01-19",
            subject="História"
        )
        assert metadata1.date == "2024-01-19"
        
        # Test case 2: Formato brasileiro
        metadata2 = InternalDocumentMetadata(
            date="19/01/2024",
            subject="Geografia"
        )
        assert metadata2.date == "19/01/2024"
        
        # Test case 3: Formato com texto
        metadata3 = InternalDocumentMetadata(
            date="19 de Janeiro de 2024",
            subject="Literatura"
        )
        assert metadata3.date == "19 de Janeiro de 2024"
    
    def test_create_with_images(self):
        """Testa criação com listas de imagens"""
        # Arrange
        sample_image = InternalImageData(
            id="img_001",
            file_path="/path/test.pdf",
            base64_data="iVBORw0KGgoAAAANSUhEUgAA...",
            page=1,
            category="header"
        )
        
        # Act
        metadata = InternalDocumentMetadata(
            school="Escola Teste",
            subject="Teste",
            header_images=[sample_image],
            content_images=[]
        )
        
        # Assert
        assert len(metadata.header_images) == 1
        assert len(metadata.content_images) == 0
        assert metadata.header_images[0].id == "img_001"
    
    def test_validation_accepts_empty_strings(self):
        """Testa que strings vazias são aceitas (campos opcionais)"""
        # Act - não deve dar erro pois todos os campos são Optional
        metadata = InternalDocumentMetadata(
            student="",
            school="",
            subject="",
            teacher=""
        )
        
        # Assert
        assert metadata.student == ""
        assert metadata.school == ""
        assert metadata.subject == ""
        assert metadata.teacher == ""
    
    def test_class_field_alias(self):
        """Testa o campo class_ com alias 'class'"""
        # Act
        metadata = InternalDocumentMetadata(
            **{"class": "9º A", "subject": "Matemática"}
        )
        
        # Assert
        assert metadata.class_ == "9º A"
        assert metadata.subject == "Matemática"
    
    def test_model_serialization(self):
        """Testa serialização do modelo"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student="Teste Serialização",
            network="REDE TESTE",
            school="Escola Teste",
            subject="Serialização",
            city="Cidade Teste",
            extraction_confidence=0.95
        )
        
        # Act
        json_str = metadata.json()  # Pydantic v1 method
        dict_data = metadata.dict()  # Pydantic v1 method
        
        # Assert
        assert isinstance(json_str, str)
        assert isinstance(dict_data, dict)
        assert "student" in json_str
        assert ("Teste Serialização" in json_str or "Teste Serializa" in json_str)  # Unicode pode ser escapado
        assert dict_data["student"] == "Teste Serialização"
        assert dict_data["subject"] == "Serialização"
        assert dict_data["extraction_confidence"] == 0.95
    
    def test_model_deserialization(self):
        """Testa deserialização do modelo"""
        # Arrange
        data = {
            "student": "Teste Deserialização",
            "network": "REDE DESERIALIZATION",
            "school": "Escola Deserialização",
            "subject": "Deserialização",
            "city": "Cidade Deserialização",
            "teacher": "Prof. Deserialização"
        }
        
        # Act
        metadata = InternalDocumentMetadata(**data)
        
        # Assert
        assert metadata.student == "Teste Deserialização"
        assert metadata.network == "REDE DESERIALIZATION"
        assert metadata.school == "Escola Deserialização"
        assert metadata.subject == "Deserialização"
        assert metadata.city == "Cidade Deserialização"
        assert metadata.teacher == "Prof. Deserialização"
    
    def test_equality_comparison(self):
        """Testa comparação de igualdade entre instâncias"""
        # Arrange
        metadata1 = InternalDocumentMetadata(
            student="João Silva",
            school="UMEF Exemplo",
            subject="Matemática",
            teacher="Prof. Maria"
        )
        
        metadata2 = InternalDocumentMetadata(
            student="João Silva", 
            school="UMEF Exemplo",
            subject="Matemática",
            teacher="Prof. Maria"
        )
        
        metadata3 = InternalDocumentMetadata(
            student="Ana Costa",
            school="UMEF Diferente",
            subject="Física",
            teacher="Prof. João"
        )
        
        # Act & Assert
        assert metadata1 == metadata2  # Mesmos dados
        assert metadata1 != metadata3  # Dados diferentes
        assert metadata2 != metadata3  # Dados diferentes
    
    def test_to_dict_method(self):
        """Testa método dict() do Pydantic"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student="Test Dict",
            school="Dict School",
            subject="Dictionary Test",
            city="Dict City"
        )
        
        # Act
        result_dict = metadata.dict()
        
        # Assert
        assert isinstance(result_dict, dict)
        assert result_dict["student"] == "Test Dict"
        assert result_dict["school"] == "Dict School"
        assert result_dict["subject"] == "Dictionary Test"
        assert result_dict["city"] == "Dict City"
        
    def test_processing_metadata_fields(self):
        """Testa campos específicos de metadados de processamento"""
        # Arrange & Act
        metadata = InternalDocumentMetadata(
            subject="Teste Processamento",
            extraction_confidence=0.87,
            processing_notes="Teste de extração com Azure"
        )
        
        # Assert
        assert metadata.extraction_confidence == 0.87
        assert metadata.processing_notes == "Teste de extração com Azure"
        assert metadata.subject == "Teste Processamento"