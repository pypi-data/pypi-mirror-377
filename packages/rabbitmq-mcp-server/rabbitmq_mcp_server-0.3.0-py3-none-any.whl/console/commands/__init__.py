"""
Console Commands Module

Comandos CLI para o cliente console.
"""

from .connection_commands import connection_group
from .dlq_commands import dlq_group
from .exchange_commands import exchange_group
from .message_commands import message_group
from .monitor_commands import monitor_group
from .queue_commands import queue_group

__all__ = [
    "connection_group",
    "queue_group",
    "message_group",
    "exchange_group",
    "dlq_group",
    "monitor_group"
]
