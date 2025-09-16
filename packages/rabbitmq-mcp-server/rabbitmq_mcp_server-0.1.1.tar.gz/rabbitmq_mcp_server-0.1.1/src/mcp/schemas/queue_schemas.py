"""
Schemas pydantic para ferramentas de fila RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de gerenciamento de filas RabbitMQ.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueueCreateSchema(BaseModel):
    """Schema para criar uma fila."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    queue_name: str = Field(..., description="Nome da fila para criar")
    durable: bool = Field(True, description="Se a fila deve sobreviver ao reinício do broker")
    exclusive: bool = Field(False, description="Se a fila é exclusiva da conexão")
    auto_delete: bool = Field(False, description="Se a fila deve ser deletada quando não usada")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais da fila")


class QueueDeleteSchema(BaseModel):
    """Schema para deletar uma fila."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    queue_name: str = Field(..., description="Nome da fila para deletar")
    if_unused: bool = Field(False, description="Deletar apenas se a fila não tem consumidores")
    if_empty: bool = Field(False, description="Deletar apenas se a fila não tem mensagens")


class QueueListSchema(BaseModel):
    """Schema para listar filas."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    vhost: str = Field("/", description="Host virtual para listar filas")
    include_stats: bool = Field(True, description="Se deve incluir estatísticas das filas")


class QueuePurgeSchema(BaseModel):
    """Schema para limpar uma fila."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    queue_name: str = Field(..., description="Nome da fila para limpar")


class QueueInfo(BaseModel):
    """Informações de uma fila."""
    name: str = Field(..., description="Nome da fila")
    durable: bool = Field(..., description="Se a fila é durável")
    exclusive: bool = Field(..., description="Se a fila é exclusiva")
    auto_delete: bool = Field(..., description="Se a fila é auto-delete")
    message_count: int = Field(..., description="Número de mensagens na fila")
    consumer_count: int = Field(..., description="Número de consumidores")
    vhost: str = Field(..., description="Host virtual")
    created_at: str = Field(..., description="Timestamp de criação")
    last_updated: str = Field(..., description="Timestamp da última atualização")


class QueueCreateResponse(BaseModel):
    """Resposta para criação de fila."""
    queue_name: str = Field(..., description="Nome da fila criada")
    status: str = Field(..., description="Status da operação")
    durable: bool = Field(..., description="Se a fila é durável")
    exclusive: bool = Field(..., description="Se a fila é exclusiva")
    auto_delete: bool = Field(..., description="Se a fila é auto-delete")
    message_count: int = Field(0, description="Número de mensagens na fila")
    consumer_count: int = Field(0, description="Número de consumidores")
    created_at: str = Field(..., description="Timestamp de criação")


class QueueDeleteResponse(BaseModel):
    """Resposta para deleção de fila."""
    queue_name: str = Field(..., description="Nome da fila deletada")
    status: str = Field(..., description="Status da operação")
    deleted_at: str = Field(..., description="Timestamp da deleção")


class QueueListResponse(BaseModel):
    """Resposta para lista de filas."""
    queues: List[QueueInfo] = Field(..., description="Lista de filas")
    total_count: int = Field(..., description="Número total de filas")
    vhost: str = Field(..., description="Host virtual")


class QueuePurgeResponse(BaseModel):
    """Resposta para limpeza de fila."""
    queue_name: str = Field(..., description="Nome da fila limpa")
    status: str = Field(..., description="Status da operação")
    messages_purged: int = Field(..., description="Número de mensagens removidas")
    purged_at: str = Field(..., description="Timestamp da limpeza")