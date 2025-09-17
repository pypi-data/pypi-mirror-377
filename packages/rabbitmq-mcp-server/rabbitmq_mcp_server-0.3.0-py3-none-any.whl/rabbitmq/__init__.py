"""
Módulo de integração RabbitMQ.

Este módulo fornece uma interface unificada para todas as operações
RabbitMQ através dos gerenciadores especializados.
"""

from .connection_manager import ConnectionManager, connection_manager
from .exchange_manager import ExchangeManager, exchange_manager
from .message_manager import MessageManager, message_manager
from .queue_manager import QueueManager, queue_manager

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
