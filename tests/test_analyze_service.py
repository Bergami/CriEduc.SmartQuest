import json
import asyncio
import os
from fastapi import UploadFile
from io import BytesIO
from app.services.analyze_service import AnalyzeService


def load_file_bytes(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        return f.read()


def load_expected_result(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def remove_dynamic_fields(data: dict) -> dict:
    for key in ["document_id", "email", "filename", "extracted_text"]:
        data.pop(key, None)
    return data


def test_compare_parser_output_with_expected_result():
    # Caminhos
    base_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(base_dir, "modelo-prova.pdf")
    json_path = os.path.join(base_dir, "resultado_parser.json")

    # Simula UploadFile
    file_bytes = load_file_bytes(pdf_path)
    fake_upload = UploadFile(filename=pdf_path, file=BytesIO(file_bytes))

    # Executa análise
    result = asyncio.run(AnalyzeService.process_document(fake_upload, email="teste@teste.com"))

    # Carrega gabarito
    expected = load_expected_result(json_path)

    # Remove campos voláteis
    result = remove_dynamic_fields(result)
    expected = remove_dynamic_fields(expected)

    # Faz a comparação
    assert result == expected, "Resultado gerado não bate com o esperado"
