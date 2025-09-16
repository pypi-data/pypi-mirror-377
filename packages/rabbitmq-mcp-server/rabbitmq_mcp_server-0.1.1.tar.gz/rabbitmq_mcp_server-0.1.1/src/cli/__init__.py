"""
Módulo CLI para RabbitMQ MCP Server.

Este módulo fornece uma interface de linha de comando para interagir
com o servidor MCP RabbitMQ.
"""

from .client import RabbitMQCLIClient, cli_client
from .__main__ import main, cli

__all__ = [
    "RabbitMQCLIClient",
    "cli_client", 
    "main",
    "cli",
]
