"""
Schemas pydantic para ferramentas de exchange RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de gerenciamento de exchanges RabbitMQ.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExchangeCreateSchema(BaseModel):
    """Schema para criar um exchange."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    exchange_name: str = Field(..., description="Nome do exchange para criar")
    exchange_type: str = Field(..., description="Tipo do exchange (direct, topic, fanout, headers)")
    durable: bool = Field(True, description="Se o exchange deve sobreviver ao reinício do broker")
    auto_delete: bool = Field(False, description="Se o exchange deve ser deletado quando não usado")
    internal: bool = Field(False, description="Se o exchange é interno (não para uso de clientes)")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais do exchange")


class ExchangeDeleteSchema(BaseModel):
    """Schema para deletar um exchange."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    exchange_name: str = Field(..., description="Nome do exchange para deletar")
    if_unused: bool = Field(False, description="Deletar apenas se o exchange não tem bindings")


class ExchangeBindSchema(BaseModel):
    """Schema para vincular uma fila a um exchange."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    exchange_name: str = Field(..., description="Nome do exchange para vincular")
    queue_name: str = Field(..., description="Nome da fila para vincular")
    routing_key: str = Field(..., description="Chave de roteamento para o binding")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais do binding")


class ExchangeUnbindSchema(BaseModel):
    """Schema para desvincular uma fila de um exchange."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    exchange_name: str = Field(..., description="Nome do exchange para desvincular")
    queue_name: str = Field(..., description="Nome da fila para desvincular")
    routing_key: str = Field(..., description="Chave de roteamento do binding a ser removido")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais do binding")


class ExchangeInfo(BaseModel):
    """Informações de um exchange."""
    name: str = Field(..., description="Nome do exchange")
    type: str = Field(..., description="Tipo do exchange")
    durable: bool = Field(..., description="Se o exchange é durável")
    auto_delete: bool = Field(..., description="Se o exchange é auto-delete")
    internal: bool = Field(..., description="Se o exchange é interno")
    vhost: str = Field(..., description="Host virtual")
    created_at: str = Field(..., description="Timestamp de criação")
    last_updated: str = Field(..., description="Timestamp da última atualização")
    binding_count: int = Field(0, description="Número de bindings")


class BindingInfo(BaseModel):
    """Informações de um binding."""
    exchange_name: str = Field(..., description="Nome do exchange")
    queue_name: str = Field(..., description="Nome da fila")
    routing_key: str = Field(..., description="Chave de roteamento")
    arguments: Dict[str, Any] = Field(..., description="Argumentos do binding")
    created_at: str = Field(..., description="Timestamp de criação")


class ExchangeCreateResponse(BaseModel):
    """Resposta para criação de exchange."""
    exchange_name: str = Field(..., description="Nome do exchange criado")
    exchange_type: str = Field(..., description="Tipo do exchange")
    status: str = Field(..., description="Status da operação")
    durable: bool = Field(..., description="Se o exchange é durável")
    auto_delete: bool = Field(..., description="Se o exchange é auto-delete")
    internal: bool = Field(..., description="Se o exchange é interno")
    created_at: str = Field(..., description="Timestamp de criação")


class ExchangeDeleteResponse(BaseModel):
    """Resposta para deleção de exchange."""
    exchange_name: str = Field(..., description="Nome do exchange deletado")
    status: str = Field(..., description="Status da operação")
    deleted_at: str = Field(..., description="Timestamp da deleção")


class ExchangeBindResponse(BaseModel):
    """Resposta para binding de exchange."""
    binding_created: bool = Field(..., description="Se o binding foi criado com sucesso")
    exchange_name: str = Field(..., description="Nome do exchange")
    queue_name: str = Field(..., description="Nome da fila")
    routing_key: str = Field(..., description="Chave de roteamento")
    bound_at: str = Field(..., description="Timestamp do binding")


class ExchangeUnbindResponse(BaseModel):
    """Resposta para unbinding de exchange."""
    binding_removed: bool = Field(..., description="Se o binding foi removido com sucesso")
    exchange_name: str = Field(..., description="Nome do exchange")
    queue_name: str = Field(..., description="Nome da fila")
    routing_key: str = Field(..., description="Chave de roteamento")
    unbound_at: str = Field(..., description="Timestamp do unbinding")


class ExchangeListResponse(BaseModel):
    """Resposta para lista de exchanges."""
    exchanges: List[ExchangeInfo] = Field(..., description="Lista de exchanges")
    total_count: int = Field(..., description="Número total de exchanges")
    vhost: str = Field(..., description="Host virtual")


class ExchangeBindingsResponse(BaseModel):
    """Resposta para bindings de um exchange."""
    exchange_name: str = Field(..., description="Nome do exchange")
    bindings: List[BindingInfo] = Field(..., description="Lista de bindings")
    total_count: int = Field(..., description="Número total de bindings")