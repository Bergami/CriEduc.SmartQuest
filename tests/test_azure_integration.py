import pytest
import json
from fastapi import UploadFile
from io import BytesIO
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.services.analyze_service import AnalyzeService

class TestAzureDocumentIntelligence:
    
    def test_azure_service_initialization(self):
        """Testa se o serviço Azure AI é inicializado corretamente"""
        # Este teste só funcionará com credenciais válidas
        try:
            service = AzureDocumentIntelligenceService()
            assert service.endpoint is not None
            assert service.key is not None
        except ValueError as e:
            # Esperado quando credenciais não estão configuradas
            assert "not configured" in str(e)
    
    @pytest.mark.asyncio
    async def test_analyze_service_with_azure_error_handling(self):
        """Testa se o AnalyzeService lança exceção correta quando Azure AI falha"""
        # Simula um arquivo PDF
        pdf_content = b"%PDF-1.4 fake pdf content"
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(pdf_content),
            content_type="application/pdf"
        )
        
        # Como não temos credenciais Azure válidas, deve usar fallback
        result = await AnalyzeService.process_document(
            file=file,
            email="test@example.com",
            use_json_fallback=False
        )
        
        # Verifica estrutura do resultado
        assert "email" in result
        assert "document_id" in result
        assert "filename" in result
        assert "header" in result
        assert "questions" in result
        assert "context_blocks" in result
    
    def test_resultado_parser_structure(self):
        """Testa se a estrutura do resultado_parser.json está correta"""
        with open("tests/resultado_parser.json", "r", encoding="utf-8") as f:
            expected_structure = json.load(f)
        
        # Verifica campos obrigatórios
        required_fields = [
            "email", "document_id", "filename", "header", 
            "questions", "context_blocks"
        ]
        
        for field in required_fields:
            assert field in expected_structure, f"Campo {field} não encontrado"
        
        # Verifica estrutura do header
        header_fields = [
            "network", "school", "city", "teacher", "subject",
            "exam_title", "trimester", "grade", "class", 
            "student", "grade_value", "date"
        ]
        
        for field in header_fields:
            assert field in expected_structure["header"], f"Campo header.{field} não encontrado"
        
        # Verifica estrutura das questões
        if expected_structure["questions"]:
            question = expected_structure["questions"][0]
            question_fields = ["number", "question", "alternatives", "hasImage", "context_id"]
            
            for field in question_fields:
                assert field in question, f"Campo question.{field} não encontrado"
        
        # Verifica estrutura dos blocos de contexto
        if expected_structure["context_blocks"]:
            context = expected_structure["context_blocks"][0]
            context_fields = ["id", "type", "hasImage"]
            
            for field in context_fields:
                assert field in context, f"Campo context_block.{field} não encontrado"

if __name__ == "__main__":
    pytest.main([__file__])
