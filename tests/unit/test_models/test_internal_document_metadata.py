"""
Testes unitários para InternalDocumentMetadata
"""

import pytest
from pydantic import ValidationError
from app.models.internal.document_metadata import InternalDocumentMetadata


class TestInternalDocumentMetadata:
    """Testes para o modelo InternalDocumentMetadata"""
    
    def test_create_with_valid_data(self):
        """Testa criação com dados válidos"""
        # Act
        metadata = InternalDocumentMetadata(
            student_name="João Silva",
            student_code="12345",
            evaluation_date="2024-01-15",
            subject="Matemática",
            institution="UFMG",
            city="Belo Horizonte"
        )
        
        # Assert
        assert metadata.student_name == "João Silva"
        assert metadata.student_code == "12345"
        assert metadata.evaluation_date == "2024-01-15"
        assert metadata.subject == "Matemática"
        assert metadata.institution == "UFMG"
        assert metadata.city == "Belo Horizonte"
    
    def test_create_with_unicode_characters(self):
        """Testa criação com caracteres unicode/acentos"""
        # Act
        metadata = InternalDocumentMetadata(
            student_name="José da Silva Araújo",
            student_code="ALUNO-2024-001",
            evaluation_date="15/01/2024",
            subject="Educação Física",
            institution="Universidade de São Paulo",
            city="São Paulo"
        )
        
        # Assert
        assert metadata.student_name == "José da Silva Araújo"
        assert metadata.subject == "Educação Física"
        assert metadata.institution == "Universidade de São Paulo"
        assert metadata.city == "São Paulo"
    
    def test_create_with_special_student_codes(self):
        """Testa criação com diferentes formatos de código de estudante"""
        # Test case 1: Código numérico
        metadata1 = InternalDocumentMetadata(
            student_name="Ana Costa",
            student_code="2024001",
            evaluation_date="2024-01-16",
            subject="Física",
            institution="USP",
            city="São Paulo"
        )
        assert metadata1.student_code == "2024001"
        
        # Test case 2: Código alfanumérico
        metadata2 = InternalDocumentMetadata(
            student_name="Carlos Silva",
            student_code="EST-2024-042",
            evaluation_date="2024-01-17",
            subject="Química",
            institution="UNICAMP",
            city="Campinas"
        )
        assert metadata2.student_code == "EST-2024-042"
        
        # Test case 3: Código com underscores
        metadata3 = InternalDocumentMetadata(
            student_name="Maria Oliveira",
            student_code="ALUNO_001_2024",
            evaluation_date="2024-01-18",
            subject="Biologia",
            institution="UFRJ",
            city="Rio de Janeiro"
        )
        assert metadata3.student_code == "ALUNO_001_2024"
    
    def test_create_with_different_date_formats(self):
        """Testa criação com diferentes formatos de data"""
        # Test case 1: Formato ISO
        metadata1 = InternalDocumentMetadata(
            student_name="Pedro Lima",
            student_code="33333",
            evaluation_date="2024-01-19",
            subject="História",
            institution="UFPE",
            city="Recife"
        )
        assert metadata1.evaluation_date == "2024-01-19"
        
        # Test case 2: Formato brasileiro
        metadata2 = InternalDocumentMetadata(
            student_name="Lucia Santos",
            student_code="44444",
            evaluation_date="19/01/2024",
            subject="Geografia",
            institution="UFBA",
            city="Salvador"
        )
        assert metadata2.evaluation_date == "19/01/2024"
        
        # Test case 3: Formato com texto
        metadata3 = InternalDocumentMetadata(
            student_name="Roberto Costa",
            student_code="55555",
            evaluation_date="19 de Janeiro de 2024",
            subject="Literatura",
            institution="UFRGS",
            city="Porto Alegre"
        )
        assert metadata3.evaluation_date == "19 de Janeiro de 2024"
    
    def test_validation_requires_all_fields(self):
        """Testa que todos os campos são obrigatórios"""
        # Test missing student_name
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_code="12345",
                evaluation_date="2024-01-15",
                subject="Matemática",
                institution="UFMG",
                city="Belo Horizonte"
            )
        assert "student_name" in str(exc_info.value)
        
        # Test missing student_code
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_name="João Silva",
                evaluation_date="2024-01-15",
                subject="Matemática",
                institution="UFMG",
                city="Belo Horizonte"
            )
        assert "student_code" in str(exc_info.value)
        
        # Test missing evaluation_date
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_name="João Silva",
                student_code="12345",
                subject="Matemática",
                institution="UFMG",
                city="Belo Horizonte"
            )
        assert "evaluation_date" in str(exc_info.value)
        
        # Test missing subject
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_name="João Silva",
                student_code="12345",
                evaluation_date="2024-01-15",
                institution="UFMG",
                city="Belo Horizonte"
            )
        assert "subject" in str(exc_info.value)
        
        # Test missing institution
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_name="João Silva",
                student_code="12345",
                evaluation_date="2024-01-15",
                subject="Matemática",
                city="Belo Horizonte"
            )
        assert "institution" in str(exc_info.value)
        
        # Test missing city
        with pytest.raises(ValidationError) as exc_info:
            InternalDocumentMetadata(
                student_name="João Silva",
                student_code="12345",
                evaluation_date="2024-01-15",
                subject="Matemática",
                institution="UFMG"
            )
        assert "city" in str(exc_info.value)
    
    def test_validation_rejects_empty_strings(self):
        """Testa que strings vazias são rejeitadas"""
        # Test empty student_name
        with pytest.raises(ValidationError):
            InternalDocumentMetadata(
                student_name="",
                student_code="12345",
                evaluation_date="2024-01-15",
                subject="Matemática",
                institution="UFMG",
                city="Belo Horizonte"
            )
        
        # Test empty student_code
        with pytest.raises(ValidationError):
            InternalDocumentMetadata(
                student_name="João Silva",
                student_code="",
                evaluation_date="2024-01-15",
                subject="Matemática",
                institution="UFMG",
                city="Belo Horizonte"
            )
    
    def test_validation_handles_whitespace(self):
        """Testa tratamento de espaços em branco"""
        # Arrange & Act
        metadata = InternalDocumentMetadata(
            student_name="  João Silva  ",
            student_code="  12345  ",
            evaluation_date="  2024-01-15  ",
            subject="  Matemática  ",
            institution="  UFMG  ",
            city="  Belo Horizonte  "
        )
        
        # Assert - verifica se strips espaços (se o modelo faz isso)
        # ou mantém os espaços (comportamento padrão)
        assert metadata.student_name is not None
        assert metadata.student_code is not None
        assert len(metadata.student_name) >= len("João Silva")
        assert len(metadata.student_code) >= len("12345")
    
    def test_model_serialization(self):
        """Testa serialização do modelo"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Teste Serialização",
            student_code="SER-001",
            evaluation_date="2024-01-20",
            subject="Serialização",
            institution="Universidade Teste",
            city="Cidade Teste"
        )
        
        # Act
        json_str = metadata.model_dump_json()
        dict_data = metadata.model_dump()
        
        # Assert
        assert isinstance(json_str, str)
        assert isinstance(dict_data, dict)
        assert "student_name" in json_str
        assert "Teste Serialização" in json_str
        assert dict_data["student_name"] == "Teste Serialização"
        assert dict_data["student_code"] == "SER-001"
        assert dict_data["subject"] == "Serialização"
    
    def test_model_deserialization(self):
        """Testa deserialização do modelo"""
        # Arrange
        data = {
            "student_name": "Teste Deserialização",
            "student_code": "DES-001",
            "evaluation_date": "2024-01-21",
            "subject": "Deserialização",
            "institution": "Universidade Deserialização",
            "city": "Cidade Deserialização"
        }
        
        # Act
        metadata = InternalDocumentMetadata(**data)
        
        # Assert
        assert metadata.student_name == "Teste Deserialização"
        assert metadata.student_code == "DES-001"
        assert metadata.evaluation_date == "2024-01-21"
        assert metadata.subject == "Deserialização"
        assert metadata.institution == "Universidade Deserialização"
        assert metadata.city == "Cidade Deserialização"
    
    def test_equality_comparison(self):
        """Testa comparação de igualdade entre instâncias"""
        # Arrange
        metadata1 = InternalDocumentMetadata(
            student_name="João Silva",
            student_code="12345",
            evaluation_date="2024-01-15",
            subject="Matemática",
            institution="UFMG",
            city="Belo Horizonte"
        )
        
        metadata2 = InternalDocumentMetadata(
            student_name="João Silva",
            student_code="12345",
            evaluation_date="2024-01-15",
            subject="Matemática",
            institution="UFMG",
            city="Belo Horizonte"
        )
        
        metadata3 = InternalDocumentMetadata(
            student_name="Ana Costa",
            student_code="67890",
            evaluation_date="2024-01-16",
            subject="Física",
            institution="USP",
            city="São Paulo"
        )
        
        # Act & Assert
        assert metadata1 == metadata2  # Mesmos dados
        assert metadata1 != metadata3  # Dados diferentes
        assert metadata2 != metadata3  # Dados diferentes
    
    def test_to_dict_method(self):
        """Testa método to_dict se existir"""
        # Arrange
        metadata = InternalDocumentMetadata(
            student_name="Test Dict",
            student_code="DICT-001",
            evaluation_date="2024-01-22",
            subject="Dictionary Test",
            institution="Dict University",
            city="Dict City"
        )
        
        # Act & Assert
        if hasattr(metadata, 'to_dict'):
            result_dict = metadata.to_dict()
            assert isinstance(result_dict, dict)
            assert result_dict["student_name"] == "Test Dict"
        else:
            # Se não tem to_dict, usar model_dump do Pydantic
            result_dict = metadata.model_dump()
            assert isinstance(result_dict, dict)
            assert result_dict["student_name"] == "Test Dict"
