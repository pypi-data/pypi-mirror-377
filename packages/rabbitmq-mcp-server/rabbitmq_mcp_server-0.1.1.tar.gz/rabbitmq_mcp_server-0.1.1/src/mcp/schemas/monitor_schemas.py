"""
Schemas pydantic para ferramentas de monitoramento RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de monitoramento e estatísticas RabbitMQ.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MonitorStatsSchema(BaseModel):
    """Schema para obter estatísticas."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    resource_type: str = Field(..., description="Tipo de recurso (queue, exchange, connection, all)")
    resource_name: Optional[str] = Field(None, description="Nome do recurso específico (opcional)")
    include_rates: bool = Field(True, description="Se deve incluir estatísticas de taxa")
    time_range: str = Field("5m", description="Período de tempo para estatísticas")


class MonitorHealthSchema(BaseModel):
    """Schema para verificar saúde do sistema."""
    connection_id: str = Field(..., description="ID da conexão RabbitMQ")
    check_type: str = Field(..., description="Tipo de verificação (connection, server, cluster, all)")
    include_details: bool = Field(False, description="Se deve incluir informações detalhadas de saúde")


class QueueStats(BaseModel):
    """Estatísticas de uma fila."""
    queue_name: str = Field(..., description="Nome da fila")
    message_count: int = Field(..., description="Número de mensagens")
    consumer_count: int = Field(..., description="Número de consumidores")
    publish_rate: float = Field(..., description="Taxa de publicação (msg/s)")
    consume_rate: float = Field(..., description="Taxa de consumo (msg/s)")
    memory_usage: int = Field(..., description="Uso de memória em bytes")
    disk_usage: int = Field(..., description="Uso de disco em bytes")
    last_activity: str = Field(..., description="Timestamp da última atividade")


class ExchangeStats(BaseModel):
    """Estatísticas de um exchange."""
    exchange_name: str = Field(..., description="Nome do exchange")
    type: str = Field(..., description="Tipo do exchange")
    binding_count: int = Field(..., description="Número de bindings")
    publish_rate: float = Field(..., description="Taxa de publicação (msg/s)")
    memory_usage: int = Field(..., description="Uso de memória em bytes")
    last_activity: str = Field(..., description="Timestamp da última atividade")


class ConnectionStats(BaseModel):
    """Estatísticas de uma conexão."""
    connection_id: str = Field(..., description="ID da conexão")
    host: str = Field(..., description="Host da conexão")
    port: int = Field(..., description="Porta da conexão")
    status: str = Field(..., description="Status da conexão")
    message_count: int = Field(..., description="Número de mensagens processadas")
    error_count: int = Field(..., description="Número de erros")
    uptime: str = Field(..., description="Tempo de atividade")
    last_activity: str = Field(..., description="Timestamp da última atividade")


class ServerStats(BaseModel):
    """Estatísticas do servidor RabbitMQ."""
    node_name: str = Field(..., description="Nome do nó")
    version: str = Field(..., description="Versão do RabbitMQ")
    uptime: str = Field(..., description="Tempo de atividade do servidor")
    memory_usage: int = Field(..., description="Uso de memória em bytes")
    disk_usage: int = Field(..., description="Uso de disco em bytes")
    cpu_usage: float = Field(..., description="Uso de CPU em percentual")
    connection_count: int = Field(..., description="Número de conexões")
    queue_count: int = Field(..., description="Número de filas")
    exchange_count: int = Field(..., description="Número de exchanges")
    message_count: int = Field(..., description="Número total de mensagens")


class HealthCheck(BaseModel):
    """Resultado de verificação de saúde."""
    component: str = Field(..., description="Componente verificado")
    status: str = Field(..., description="Status da verificação (healthy, warning, error)")
    message: str = Field(..., description="Mensagem de status")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")
    checked_at: str = Field(..., description="Timestamp da verificação")


class MonitorStatsResponse(BaseModel):
    """Resposta para estatísticas de monitoramento."""
    resource_type: str = Field(..., description="Tipo de recurso")
    resource_name: Optional[str] = Field(None, description="Nome do recurso")
    statistics: Dict[str, Any] = Field(..., description="Estatísticas do recurso")
    time_range: str = Field(..., description="Período de tempo")
    timestamp: str = Field(..., description="Timestamp da coleta")


class MonitorHealthResponse(BaseModel):
    """Resposta para verificação de saúde."""
    check_type: str = Field(..., description="Tipo de verificação")
    overall_status: str = Field(..., description="Status geral (healthy, warning, error)")
    health_checks: List[HealthCheck] = Field(..., description="Lista de verificações de saúde")
    checked_at: str = Field(..., description="Timestamp da verificação")


class QueueStatsResponse(BaseModel):
    """Resposta para estatísticas de filas."""
    queues: List[QueueStats] = Field(..., description="Lista de estatísticas de filas")
    total_count: int = Field(..., description="Número total de filas")
    timestamp: str = Field(..., description="Timestamp da coleta")


class ExchangeStatsResponse(BaseModel):
    """Resposta para estatísticas de exchanges."""
    exchanges: List[ExchangeStats] = Field(..., description="Lista de estatísticas de exchanges")
    total_count: int = Field(..., description="Número total de exchanges")
    timestamp: str = Field(..., description="Timestamp da coleta")


class ConnectionStatsResponse(BaseModel):
    """Resposta para estatísticas de conexões."""
    connections: List[ConnectionStats] = Field(..., description="Lista de estatísticas de conexões")
    total_count: int = Field(..., description="Número total de conexões")
    timestamp: str = Field(..., description="Timestamp da coleta")


class ServerStatsResponse(BaseModel):
    """Resposta para estatísticas do servidor."""
    server: ServerStats = Field(..., description="Estatísticas do servidor")
    timestamp: str = Field(..., description="Timestamp da coleta")