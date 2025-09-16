"""
Schemas pydantic para ferramentas de mensagem RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de gerenciamento de mensagens RabbitMQ.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessagePublishSchema(BaseModel):
    """Schema para publicar uma mensagem."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    exchange_name: str = Field(..., description="Nome do exchange para publicar")
    routing_key: str = Field(..., description="Chave de roteamento para entrega da mensagem")
    message_body: str = Field(..., description="Conteúdo da mensagem")
    headers: Dict[str, Any] = Field(default_factory=dict, description="Cabeçalhos da mensagem")
    priority: int = Field(0, ge=0, le=255, description="Prioridade da mensagem")
    expiration: Optional[str] = Field(None, description="Tempo de expiração da mensagem")
    content_type: str = Field("application/json", description="Tipo de conteúdo da mensagem")
    persistent: bool = Field(True, description="Se a mensagem deve ser persistida em disco")


class MessageConsumeSchema(BaseModel):
    """Schema para consumir mensagens."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    queue_name: str = Field(..., description="Nome da fila para consumir")
    count: int = Field(1, ge=1, le=100, description="Número de mensagens para consumir")
    auto_ack: bool = Field(False, description="Se deve confirmar automaticamente as mensagens")
    timeout: int = Field(30, ge=1, le=300, description="Timeout em segundos para consumir mensagens")


class MessageAcknowledgeSchema(BaseModel):
    """Schema para confirmar mensagens."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    delivery_tags: List[int] = Field(..., description="Lista de tags de entrega para confirmar")
    multiple: bool = Field(False, description="Se deve confirmar todas as mensagens até o tag especificado")


class MessageRejectSchema(BaseModel):
    """Schema para rejeitar mensagens."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    delivery_tags: List[int] = Field(..., description="Lista de tags de entrega para rejeitar")
    requeue: bool = Field(True, description="Se deve recolocar as mensagens rejeitadas na fila")
    multiple: bool = Field(False, description="Se deve rejeitar todas as mensagens até o tag especificado")


class MessageInfo(BaseModel):
    """Informações de uma mensagem."""
    message_id: str = Field(..., description="ID da mensagem")
    body: str = Field(..., description="Conteúdo da mensagem")
    headers: Dict[str, Any] = Field(..., description="Cabeçalhos da mensagem")
    routing_key: str = Field(..., description="Chave de roteamento")
    exchange: str = Field(..., description="Nome do exchange de origem")
    queue: str = Field(..., description="Nome da fila de destino")
    delivery_tag: Optional[int] = Field(None, description="Tag de entrega")
    redelivered: bool = Field(..., description="Se a mensagem foi reentregue")
    priority: int = Field(..., description="Prioridade da mensagem")
    timestamp: str = Field(..., description="Timestamp de criação")
    content_type: str = Field(..., description="Tipo de conteúdo")
    content_encoding: str = Field(..., description="Codificação de conteúdo")


class MessagePublishResponse(BaseModel):
    """Resposta para publicação de mensagem."""
    message_id: str = Field(..., description="ID da mensagem publicada")
    status: str = Field(..., description="Status da operação")
    exchange_name: str = Field(..., description="Nome do exchange")
    routing_key: str = Field(..., description="Chave de roteamento")
    delivery_tag: int = Field(..., description="Tag de entrega")
    published_at: str = Field(..., description="Timestamp da publicação")


class MessageConsumeResponse(BaseModel):
    """Resposta para consumo de mensagens."""
    messages: List[MessageInfo] = Field(..., description="Lista de mensagens consumidas")
    count: int = Field(..., description="Número de mensagens consumidas")
    queue_name: str = Field(..., description="Nome da fila")
    consumed_at: str = Field(..., description="Timestamp do consumo")


class MessageAcknowledgeResponse(BaseModel):
    """Resposta para confirmação de mensagens."""
    acknowledged: bool = Field(..., description="Se a confirmação foi bem-sucedida")
    delivery_tags: List[int] = Field(..., description="Lista de tags confirmados")
    count: int = Field(..., description="Número de mensagens confirmadas")
    acknowledged_at: str = Field(..., description="Timestamp da confirmação")


class MessageRejectResponse(BaseModel):
    """Resposta para rejeição de mensagens."""
    rejected: bool = Field(..., description="Se a rejeição foi bem-sucedida")
    delivery_tags: List[int] = Field(..., description="Lista de tags rejeitados")
    count: int = Field(..., description="Número de mensagens rejeitadas")
    requeued: bool = Field(..., description="Se as mensagens foram recolocadas na fila")
    rejected_at: str = Field(..., description="Timestamp da rejeição")