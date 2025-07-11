import json
import os
from typing import Dict, Any
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.services.document_extraction_factory import DocumentExtractionFactory
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

        # 🆕 USAR DOCUMENT EXTRACTION FACTORY (com Azure como padrão)
        try:
            print("🔍 DEBUG: Processing with Document Extraction Factory...")
            extracted_data = await AnalyzeService._extract_text_and_metadata_with_factory(file)
            print("✅ DEBUG: Document extraction executed successfully")
        except Exception as e:
            print(f"❌ DEBUG: Error in document extraction: {str(e)}")
            print(f"🔍 DEBUG: Error type: {type(e).__name__}")
            
            # Raise custom exception for client
            error_message = f"Failed to process document: {str(e)}"
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
            "provider_metadata": extracted_data.get("metadata", {})
        }
        
        print("✅ DEBUG: Resultado final montado")
        return result

    @staticmethod
    async def _extract_text_and_metadata_with_factory(file: UploadFile) -> Dict[str, Any]:
        """
        Extract text and metadata using the Document Extraction Factory.
        Supports multiple providers with automatic fallback.
        """
        # Get the configured extraction provider
        extractor = DocumentExtractionFactory.get_provider()
        provider_name = extractor.get_provider_name()
        
        print(f"🔍 DEBUG: Using extraction provider: {provider_name}")
        
        # Extract document data
        extracted_data = await extractor.extract_document_data(file)
        
        # Parse header information from extracted text
        header_data = HeaderParser.parse(extracted_data["text"])
        
        # Return structured data compatible with current system
        return {
            "text": extracted_data["text"],
            "header": header_data,
            "metadata": {
                **extracted_data.get("metadata", {}),
                "extraction_provider": provider_name,
                "confidence": extracted_data.get("confidence", 0.0),
                "page_count": extracted_data.get("page_count", 1)
            }
        }

    @staticmethod
    async def process_document_mock(email: str, filename: str = "mock_document.pdf") -> Dict[str, Any]:
        """
        Process document using mocked data from RetornoProcessamento.json
        Does not require physical file
        """
        document_id = str(uuid4())
        print(f"🔧 DEBUG: Processing MOCK document {filename} for {email}")
        print(f"🔧 DEBUG: Generated Document ID: {document_id}")

        # Path to JSON file
        json_path = Path("tests/RetornoProcessamento.json")
        
        if not json_path.exists():
            raise DocumentProcessingError(f"Mock file not found: {json_path}")
        
        try:
            print("🔧 DEBUG: Loading mock data...")
            with open(json_path, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
            
            print("✅ DEBUG: Mock data loaded successfully")
            # Extract text content from mock structure
            text_content = mock_data["analyzeResult"]["content"]
            
            # Clean Azure selection marks using TextNormalizer
            from app.services.base.text_normalizer import TextNormalizer
            text_content = TextNormalizer.clean_extracted_text(text_content, "azure")

            # Process mock data same as normal method
            header_data = HeaderParser.parse(text_content)
            
            print(f"🔧 DEBUG: Header extracted from mock: {header_data}")
            
            print("🔧 DEBUG: Extracting questions from mock...")
            question_data = QuestionParser.extract(text_content)
            print(f"🔧 DEBUG: Questions found in mock: {len(question_data['questions'])}")
            print(f"🔧 DEBUG: Context blocks in mock: {len(question_data['context_blocks'])}")

            result = {
                "email": email,
                "document_id": document_id,
                "filename": filename,
                "header": header_data,
                "questions": question_data["questions"],
                "context_blocks": question_data["context_blocks"]                       
            }
            
            print("🔧 DEBUG: Mock processing completed")
            return result
            
        except json.JSONDecodeError as e:
            raise DocumentProcessingError(f"Error decoding mock JSON: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"Error loading mock data: {str(e)}")
