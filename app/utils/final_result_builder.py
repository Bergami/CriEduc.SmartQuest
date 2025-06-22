import json
from typing import Dict, Any

class FinalResultBuilder:
    @staticmethod
    def load_from_result_file(filepath: str) -> Dict[str, Any]:
        """
        Lê o resultado_parser.json e retorna um dicionário estruturado para resposta da API.
        """
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        
        response = {
            "email": data["email"],
            "document_id": data["document_id"],
            "filename": data["filename"],
            "header": data["header"],
            "questions": [],
            "context_blocks": data.get("context_blocks", [])
        }

        for q in data["questions"]:
            question_entry = {
                "number": q["number"],
                "question": q["question"].strip(),
                "alternatives": [
                    f"({alt['letter']}) {alt['text'].strip()}" for alt in q["alternatives"]
                ] if "alternatives" in q else [],
                "hasImage": q.get("hasImage", False),
                "context_id": q.get("context_id", None)
            }
            response["questions"].append(question_entry)

        return response

    @staticmethod
    def load_from_json(path="resultado_parser.json") -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)