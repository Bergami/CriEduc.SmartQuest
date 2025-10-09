"""
Interfaces para serviços de imagem.

Este módulo contém as interfaces abstratas que definem contratos para
os serviços relacionados ao processamento de imagens.

Aplicação do Dependency Inversion Principle (DIP) da refatoração SOLID.
"""

from .image_categorization_interface import ImageCategorizationInterface

__all__ = [
    "ImageCategorizationInterface"
]