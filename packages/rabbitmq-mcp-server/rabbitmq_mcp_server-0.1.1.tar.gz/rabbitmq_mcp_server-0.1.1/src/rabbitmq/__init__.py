"""
Módulo de integração RabbitMQ.

Este módulo fornece uma interface unificada para todas as operações
RabbitMQ através dos gerenciadores especializados.
"""

from .connection_manager import connection_manager, ConnectionManager
from .queue_manager import queue_manager, QueueManager
from .message_manager import message_manager, MessageManager
from .exchange_manager import exchange_manager, ExchangeManager

__all__ = [
    "connection_manager",
    "ConnectionManager",
    "queue_manager", 
    "QueueManager",
    "message_manager",
    "MessageManager",
    "exchange_manager",
    "ExchangeManager",
]
