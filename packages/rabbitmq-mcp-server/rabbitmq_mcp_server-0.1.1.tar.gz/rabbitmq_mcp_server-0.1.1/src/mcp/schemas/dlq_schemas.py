"""
Schemas pydantic para ferramentas de dead letter queue RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de gerenciamento de dead letter queues RabbitMQ.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DLQConfigureSchema(BaseModel):
    """Schema para configurar dead letter queue."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    source_queue: str = Field(..., description="Nome da fila de origem para configurar DLQ")
    dlq_name: str = Field(..., description="Nome da dead letter queue")
    dlq_exchange: str = Field(..., description="Nome do dead letter exchange")
    routing_key: str = Field(..., description="Chave de roteamento para dead letter routing")
    ttl: Optional[int] = Field(None, description="Time-to-live para mensagens na DLQ (milissegundos)")
    max_length: Optional[int] = Field(None, description="Número máximo de mensagens na DLQ")
    max_bytes: Optional[int] = Field(None, description="Tamanho máximo em bytes para DLQ")


class DLQManageSchema(BaseModel):
    """Schema para gerenciar operações de dead letter queue."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    dlq_name: str = Field(..., description="Nome da dead letter queue")
    action: str = Field(..., description="Ação a realizar (list, purge, reprocess, delete)")
    reprocess_queue: Optional[str] = Field(None, description="Fila para reprocessar mensagens (para ação reprocess)")
    count: int = Field(10, ge=1, le=1000, description="Número de mensagens para processar (para ação reprocess)")


class DLQInfo(BaseModel):
    """Informações de uma dead letter queue."""
    dlq_name: str = Field(..., description="Nome da DLQ")
    source_queue: str = Field(..., description="Nome da fila de origem")
    dlq_exchange: str = Field(..., description="Nome do dead letter exchange")
    routing_key: str = Field(..., description="Chave de roteamento")
    message_count: int = Field(..., description="Número de mensagens na DLQ")
    ttl: Optional[int] = Field(None, description="Time-to-live configurado")
    max_length: Optional[int] = Field(None, description="Comprimento máximo configurado")
    max_bytes: Optional[int] = Field(None, description="Tamanho máximo configurado")
    created_at: str = Field(..., description="Timestamp de criação")
    last_updated: str = Field(..., description="Timestamp da última atualização")


class DLQMessageInfo(BaseModel):
    """Informações de uma mensagem na DLQ."""
    message_id: str = Field(..., description="ID da mensagem")
    original_queue: str = Field(..., description="Fila original da mensagem")
    dlq_name: str = Field(..., description="Nome da DLQ")
    body: str = Field(..., description="Conteúdo da mensagem")
    headers: Dict[str, Any] = Field(..., description="Cabeçalhos da mensagem")
    routing_key: str = Field(..., description="Chave de roteamento original")
    reason: str = Field(..., description="Motivo da mensagem estar na DLQ")
    timestamp: str = Field(..., description="Timestamp da mensagem")
    retry_count: int = Field(0, description="Número de tentativas")


class DLQConfigureResponse(BaseModel):
    """Resposta para configuração de DLQ."""
    dlq_name: str = Field(..., description="Nome da DLQ configurada")
    source_queue: str = Field(..., description="Nome da fila de origem")
    status: str = Field(..., description="Status da operação")
    dlq_exchange: str = Field(..., description="Nome do dead letter exchange")
    routing_key: str = Field(..., description="Chave de roteamento")
    ttl: Optional[int] = Field(None, description="Time-to-live configurado")
    max_length: Optional[int] = Field(None, description="Comprimento máximo configurado")
    max_bytes: Optional[int] = Field(None, description="Tamanho máximo configurado")
    configured_at: str = Field(..., description="Timestamp da configuração")


class DLQManageResponse(BaseModel):
    """Resposta para operações de gerenciamento de DLQ."""
    dlq_name: str = Field(..., description="Nome da DLQ")
    action: str = Field(..., description="Ação realizada")
    status: str = Field(..., description="Status da operação")
    result: Dict[str, Any] = Field(..., description="Resultado da operação")
    executed_at: str = Field(..., description="Timestamp da execução")


class DLQListResponse(BaseModel):
    """Resposta para lista de DLQs."""
    dlqs: List[DLQInfo] = Field(..., description="Lista de dead letter queues")
    total_count: int = Field(..., description="Número total de DLQs")


class DLQMessagesResponse(BaseModel):
    """Resposta para mensagens em uma DLQ."""
    dlq_name: str = Field(..., description="Nome da DLQ")
    messages: List[DLQMessageInfo] = Field(..., description="Lista de mensagens na DLQ")
    total_count: int = Field(..., description="Número total de mensagens")
    retrieved_at: str = Field(..., description="Timestamp da recuperação")


class DLQPurgeResponse(BaseModel):
    """Resposta para limpeza de DLQ."""
    dlq_name: str = Field(..., description="Nome da DLQ")
    status: str = Field(..., description="Status da operação")
    messages_purged: int = Field(..., description="Número de mensagens removidas")
    purged_at: str = Field(..., description="Timestamp da limpeza")


class DLQReprocessResponse(BaseModel):
    """Resposta para reprocessamento de mensagens da DLQ."""
    dlq_name: str = Field(..., description="Nome da DLQ")
    reprocess_queue: str = Field(..., description="Fila de destino para reprocessamento")
    status: str = Field(..., description="Status da operação")
    messages_reprocessed: int = Field(..., description="Número de mensagens reprocessadas")
    reprocessed_at: str = Field(..., description="Timestamp do reprocessamento")