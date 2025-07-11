import json
import os
from typing import Dict, Any
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService
from app.core.exceptions import DocumentProcessingError
from app.utils.final_result_builder import FinalResultBuilder

class AnalyzeService:
    @staticmethod
    async def process_document(file: UploadFile, email: str, use_json_fallback: bool = False) -> Dict[str, Any]:
        document_id = str(uuid4())
        print(f"🔍 DEBUG: Processando documento {file.filename} para {email}")
        print(f"🔍 DEBUG: Document ID gerado: {document_id}")

        if use_json_fallback:
            print("🔍 DEBUG: Usando fallback JSON...")
            # Carrega resultado_parser.json
            with open("resultado_parser.json", "r", encoding="utf-8") as f:
                parsed_data = json.load(f)

            parsed_data["document_id"] = document_id
            parsed_data["email"] = email
            parsed_data["filename"] = file.filename
            parsed_data["extracted_text"] = "Documento carregado via fallback JSON."

            return parsed_data

        # 🆕 USAR APENAS AZURE AI DOCUMENT INTELLIGENCE
        try:
            print("🔍 DEBUG: Processing with Azure AI Document Intelligence...")
            extracted_data = await AnalyzeService._extract_text_and_metadata_azure(file)
            print("✅ DEBUG: Azure AI executed successfully")
        except Exception as e:
            print(f"❌ DEBUG: Error in Azure AI: {str(e)}")
            print(f"🔍 DEBUG: Error type: {type(e).__name__}")
            
            # Raise custom exception for client
            error_message = f"Failed to process document with Azure AI: {str(e)}"
            print(f"🚨 DEBUG: Raising DocumentProcessingError: {error_message}")
            raise DocumentProcessingError(error_message)
        
        print(f"🔍 DEBUG: Text extracted: {len(extracted_data['text'])} characters")
        print(f"🔍 DEBUG: Header: {extracted_data['header']}")
        
        print("🔍 DEBUG: Extracting questions...")
        question_data = QuestionParser.extract(extracted_data["text"])
        print(f"🔍 DEBUG: Questões encontradas: {len(question_data['questions'])}")
        print(f"🔍 DEBUG: Blocos de contexto: {len(question_data['context_blocks'])}")

        result = {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "header": extracted_data["header"],
            "questions": question_data["questions"],
            "context_blocks": question_data["context_blocks"],
            "extracted_text": extracted_data["text"][:500],
            "azure_metadata": extracted_data.get("azure_metadata", {})
        }
        
        print("✅ DEBUG: Resultado final montado")
        return result

    @staticmethod
    async def _extract_text_and_metadata_azure(file: UploadFile) -> Dict[str, Any]:
        """
        New implementation using Azure AI Document Intelligence
        Maintains compatibility with current structure
        """
        azure_service = AzureDocumentIntelligenceService()
        
        # Extract data using Azure AI
        azure_result = await azure_service.analyze_document(file)
        
        # Clean Azure selection marks
        clean_text = AnalyzeService._clean_azure_selection_marks(azure_result["text"])
        
        # Maintain compatibility with existing parsers
        header_text = AnalyzeService._extract_header_block(clean_text)
        header_data = AnalyzeService._parse_header(header_text)

        return {
            "header": header_data,
            "text": clean_text,
            "azure_metadata": {
                "confidence": azure_result.get("confidence", 0.0),
                "page_count": azure_result.get("page_count", 1),
                "tables": azure_result.get("tables", []),
                "key_value_pairs": azure_result.get("key_value_pairs", {})
            }
        }

    @staticmethod
    def _clean_azure_selection_marks(text: str) -> str:
        """
        Remove símbolos de seleção do Azure Document Intelligence como :selected: e :unselected:
        """
        import re
        # Remove símbolos de seleção
        text = re.sub(r':selected:', '', text)
        text = re.sub(r':unselected:', '', text)
        
        # Remove múltiplos espaços consecutivos mas preserva quebras de linha
        text = re.sub(r'[ \t]+', ' ', text)  # apenas espaços e tabs, não quebras de linha
        
        # Remove espaços no início e fim das linhas
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text

    @staticmethod
    def _extract_header_block(text: str, max_lines: int = 12) -> str:
        lines = text.strip().splitlines()
        return "\n".join(lines[:max_lines])

    @staticmethod
    def _parse_header(header: str) -> Dict[str, Any]:
        return HeaderParser.parse(header)

    @staticmethod
    async def process_document_mock(email: str, filename: str = "mock_document.pdf") -> Dict[str, Any]:
        """
        Processa documento usando dados mockados do arquivo RetornoProcessamento.json
        Não requer arquivo físico
        """
        document_id = str(uuid4())
        print(f"🔧 DEBUG: Processando documento MOCK {filename} para {email}")
        print(f"🔧 DEBUG: Document ID gerado: {document_id}")

        # Path to JSON file
        json_path = Path("tests/RetornoProcessamento.json")
        
        if not json_path.exists():
            raise DocumentProcessingError(f"Mock file not found: {json_path}")
        
        try:
            print("🔧 DEBUG: Loading mock data...")
            with open(json_path, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
            
            print("✅ DEBUG: Dados mockados carregados com sucesso")
             # Extrai o conteúdo de texto da estrutura correta do mock
            text_content = mock_data["analyzeResult"]["content"]
            
            # Remove símbolos de seleção do Azure Document Intelligence
            text_content = AnalyzeService._clean_azure_selection_marks(text_content)

            # Processa os dados do JSON da mesma forma que o método normal
            header_text = AnalyzeService._extract_header_block(text_content)
            header_data = AnalyzeService._parse_header(header_text)
            
            print(f"🔧 DEBUG: Header extraído do mock: {header_data}")
            
            print("🔧 DEBUG: Extraindo questões do mock...")
            question_data = QuestionParser.extract(text_content)
            print(f"🔧 DEBUG: Questões encontradas no mock: {len(question_data['questions'])}")
            print(f"🔧 DEBUG: Blocos de contexto no mock: {len(question_data['context_blocks'])}")

            result = {
                "email": email,
                "document_id": document_id,
                "filename": filename,
                "header": header_data,
                "questions": question_data["questions"],
                "context_blocks": question_data["context_blocks"]                       
            }
            
            print("🔧 DEBUG: Processamento mock concluído")
            return result
            
        except json.JSONDecodeError as e:
            raise DocumentProcessingError(f"Error decoding mock JSON: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"Error loading mock data: {str(e)}")
