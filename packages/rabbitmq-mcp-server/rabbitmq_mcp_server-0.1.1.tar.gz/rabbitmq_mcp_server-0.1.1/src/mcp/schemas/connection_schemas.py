"""
Schemas pydantic para ferramentas de conexão RabbitMQ.

Este módulo define os schemas de entrada e saída para as ferramentas
MCP de gerenciamento de conexões RabbitMQ.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ConnectionConnectSchema(BaseModel):
    """Schema para conectar ao RabbitMQ."""
    host: str = Field(..., description="Hostname ou IP do servidor RabbitMQ")
    port: int = Field(5672, ge=1, le=65535, description="Porta do servidor RabbitMQ")
    username: str = Field(..., description="Nome de usuário para autenticação")
    password: str = Field(..., description="Senha para autenticação")
    virtual_host: str = Field("/", description="Host virtual RabbitMQ")
    ssl_enabled: bool = Field(False, description="Se SSL/TLS está habilitado")
    ssl_cert_path: Optional[str] = Field(None, description="Caminho para certificado SSL")
    ssl_key_path: Optional[str] = Field(None, description="Caminho para chave privada SSL")
    ssl_ca_path: Optional[str] = Field(None, description="Caminho para certificado CA SSL")
    connection_timeout: int = Field(30, ge=5, le=300, description="Timeout de conexão em segundos")
    heartbeat_interval: int = Field(600, ge=60, le=3600, description="Intervalo de heartbeat em segundos")


class ConnectionDisconnectSchema(BaseModel):
    """Schema para desconectar do RabbitMQ."""
    connection_id: str = Field(..., description="ID da conexão para desconectar")


class ConnectionStatusSchema(BaseModel):
    """Schema para verificar status da conexão."""
    connection_id: str = Field(..., description="ID da conexão para verificar")


class ConnectionListSchema(BaseModel):
    """Schema para listar conexões ativas."""
    include_stats: bool = Field(True, description="Se deve incluir estatísticas da conexão")


class ConnectionConnectResponse(BaseModel):
    """Resposta para conexão estabelecida."""
    connection_id: str = Field(..., description="ID da conexão estabelecida")
    status: str = Field(..., description="Status da conexão")
    host: str = Field(..., description="Host conectado")
    port: int = Field(..., description="Porta conectada")
    virtual_host: str = Field(..., description="Host virtual")
    ssl_enabled: bool = Field(..., description="Se SSL está habilitado")
    connected_at: str = Field(..., description="Timestamp da conexão")


class ConnectionStatusResponse(BaseModel):
    """Resposta para status da conexão."""
    connection_id: str = Field(..., description="ID da conexão")
    status: str = Field(..., description="Status atual da conexão")
    host: str = Field(..., description="Host da conexão")
    port: int = Field(..., description="Porta da conexão")
    virtual_host: str = Field(..., description="Host virtual")
    ssl_enabled: bool = Field(..., description="Se SSL está habilitado")
    connected_at: str = Field(..., description="Timestamp da conexão")
    last_used: str = Field(..., description="Timestamp da última utilização")
    message_count: int = Field(0, description="Número de mensagens processadas")
    error_count: int = Field(0, description="Número de erros")


class ConnectionListResponse(BaseModel):
    """Resposta para lista de conexões."""
    connections: list[ConnectionStatusResponse] = Field(..., description="Lista de conexões ativas")
    total_count: int = Field(..., description="Número total de conexões")


class ConnectionDisconnectResponse(BaseModel):
    """Resposta para desconexão."""
    connection_id: str = Field(..., description="ID da conexão desconectada")
    status: str = Field(..., description="Status após desconexão")
    disconnected_at: str = Field(..., description="Timestamp da desconexão")