"""
Modelo base para documentos MongoDB

Implementa campos básicos para documentos conforme prompt original.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class BaseDocument(BaseModel):
    """
    Modelo base para documentos MongoDB.
    
    Segue especificação do prompt original com campos básicos.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Configuração Pydantic para integração MongoDB."""
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def dict_for_mongo(self, **kwargs) -> Dict[str, Any]:
        """
        Serializa o modelo para formato compatível com MongoDB.
        
        Returns:
            Dict com campos apropriados para inserção MongoDB
        """
        # Usar alias e excluir campos None
        data = self.dict(by_alias=True, exclude_none=True, **kwargs)
        
        # MongoDB irá gerar _id se não fornecido
        if not data.get("_id"):
            data.pop("_id", None)
            
        return data
    
    @classmethod
    def from_mongo(cls, data: dict):
        """
        Cria instância do modelo a partir de documento MongoDB.
        
        Args:
            data: Documento do MongoDB
            
        Returns:
            Instância do modelo Pydantic
        """
        # Converte ObjectId para string se necessário
        if "_id" in data:
            from bson import ObjectId
            if isinstance(data["_id"], ObjectId):
                data["_id"] = str(data["_id"])
        
        return cls(**data)