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
            print("🔍 DEBUG: Processando com Azure AI Document Intelligence...")
            extracted_data = await AnalyzeService._extract_text_and_metadata_azure(file)
            print("✅ DEBUG: Azure AI executado com sucesso")
        except Exception as e:
            print(f"❌ DEBUG: Erro no Azure AI: {str(e)}")
            print(f"🔍 DEBUG: Tipo do erro: {type(e).__name__}")
            
            # Lança uma exceção customizada para o cliente
            error_message = f"Falha ao processar documento com Azure AI: {str(e)}"
            print(f"� DEBUG: Lançando DocumentProcessingError: {error_message}")
            raise DocumentProcessingError(error_message)
        
        print(f"🔍 DEBUG: Texto extraído: {len(extracted_data['text'])} caracteres")
        print(f"🔍 DEBUG: Header: {extracted_data['header']}")
        
        print("🔍 DEBUG: Extraindo questões...")
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
        🆕 Nova implementação usando Azure AI Document Intelligence
        Mantém compatibilidade com a estrutura atual
        """
        azure_service = AzureDocumentIntelligenceService()
        
        # Extrai dados usando Azure AI
        azure_result = await azure_service.analyze_document(file)
        
        # Mantém compatibilidade com parsers existentes
        header_text = AnalyzeService._extract_header_block(azure_result["text"])
        header_data = AnalyzeService._parse_header(header_text)

        return {
            "header": header_data,
            "text": azure_result["text"],
            "azure_metadata": {
                "confidence": azure_result.get("confidence", 0.0),
                "page_count": azure_result.get("page_count", 1),
                "tables": azure_result.get("tables", []),
                "key_value_pairs": azure_result.get("key_value_pairs", {})
            }
        }

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

        # Caminho para o arquivo JSON
        json_path = Path("tests/RetornoProcessamento.json")
        
        if not json_path.exists():
            raise DocumentProcessingError(f"Arquivo de mock não encontrado: {json_path}")
        
        try:
            print("🔧 DEBUG: Carregando dados mockados...")
            with open(json_path, 'r', encoding='utf-8') as f:
                mock_data = json.load(f)
            
            print("✅ DEBUG: Dados mockados carregados com sucesso")
             # Extrai o conteúdo de texto da estrutura correta do mock
            text_content = mock_data["analyzeResult"]["content"]

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
            raise DocumentProcessingError(f"Erro ao decodificar JSON mockado: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"Erro ao carregar dados mockados: {str(e)}")
