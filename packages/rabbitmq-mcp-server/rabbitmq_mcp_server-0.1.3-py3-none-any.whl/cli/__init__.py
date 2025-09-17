"""
Módulo CLI para RabbitMQ MCP Server.

Este módulo fornece uma interface de linha de comando para interagir
com o servidor MCP RabbitMQ.
"""

from .__main__ import cli, main
from .client import RabbitMQCLIClient, cli_client

__all__ = [
    "RabbitMQCLIClient",
    "cli_client",
    "main",
    "cli",
]
