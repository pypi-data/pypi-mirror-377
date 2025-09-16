"""
RabbitMQ MCP Server - Connection Model
Copyright (C) 2025 RabbitMQ MCP Server

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

Modelo de dados para conexões RabbitMQ.

Este módulo define o modelo pydantic para representar conexões RabbitMQ
com validação de dados e serialização JSON.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ConnectionStatus(str, Enum):
    """Status possíveis de uma conexão RabbitMQ."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class Connection(BaseModel):
    """
    Modelo para representar uma conexão RabbitMQ.
    
    Atributos:
        connection_id: Identificador único da conexão
        host: Hostname ou IP do servidor RabbitMQ
        port: Porta do servidor RabbitMQ
        username: Nome de usuário para autenticação
        password: Senha para autenticação (não serializada)
        virtual_host: Host virtual RabbitMQ
        ssl_enabled: Se SSL/TLS está habilitado
        ssl_cert_path: Caminho para certificado SSL
        ssl_key_path: Caminho para chave privada SSL
        ssl_ca_path: Caminho para certificado CA SSL
        connection_timeout: Timeout de conexão em segundos
        heartbeat_interval: Intervalo de heartbeat em segundos
        status: Status atual da conexão
        created_at: Timestamp de criação da conexão
        last_used: Timestamp da última utilização
    """
    
    connection_id: str = Field(..., description="Identificador único da conexão")
    host: str = Field(..., min_length=1, description="Hostname ou IP do servidor RabbitMQ")
    port: int = Field(5672, ge=1, le=65535, description="Porta do servidor RabbitMQ")
    username: str = Field(..., min_length=1, description="Nome de usuário para autenticação")
    password: str = Field(..., min_length=1, description="Senha para autenticação")
    virtual_host: str = Field("/", min_length=1, description="Host virtual RabbitMQ")
    ssl_enabled: bool = Field(False, description="Se SSL/TLS está habilitado")
    ssl_cert_path: Optional[str] = Field(None, description="Caminho para certificado SSL")
    ssl_key_path: Optional[str] = Field(None, description="Caminho para chave privada SSL")
    ssl_ca_path: Optional[str] = Field(None, description="Caminho para certificado CA SSL")
    connection_timeout: int = Field(30, ge=5, le=300, description="Timeout de conexão em segundos")
    heartbeat_interval: int = Field(600, ge=60, le=3600, description="Intervalo de heartbeat em segundos")
    status: ConnectionStatus = Field(ConnectionStatus.DISCONNECTED, description="Status atual da conexão")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    last_used: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da última utilização")
    
    class Config:
        """Configuração do modelo pydantic."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Excluir senha da serialização
        fields = {
            'password': {'exclude': True}
        }
    
    @field_validator('virtual_host')
    @classmethod
    def validate_virtual_host(cls, v):
        """Valida se o virtual_host começa com '/'."""
        if not v.startswith('/'):
            raise ValueError('virtual_host deve começar com "/"')
        return v
    
    @field_validator('ssl_cert_path', 'ssl_key_path', 'ssl_ca_path')
    @classmethod
    def validate_ssl_paths(cls, v, info):
        """Valida se os caminhos SSL são fornecidos quando SSL está habilitado."""
        if info.data.get('ssl_enabled', False) and v is None:
            raise ValueError('Caminhos SSL são obrigatórios quando SSL está habilitado')
        return v
    
    def update_status(self, new_status: ConnectionStatus) -> None:
        """
        Atualiza o status da conexão.
        
        Args:
            new_status: Novo status da conexão
        """
        self.status = new_status
        self.last_used = datetime.utcnow()
    
    def is_connected(self) -> bool:
        """
        Verifica se a conexão está ativa.
        
        Returns:
            True se a conexão está conectada
        """
        return self.status == ConnectionStatus.CONNECTED
    
    def is_ssl_enabled(self) -> bool:
        """
        Verifica se SSL está habilitado.
        
        Returns:
            True se SSL está habilitado
        """
        return self.ssl_enabled
    
    def get_connection_url(self) -> str:
        """
        Gera a URL de conexão RabbitMQ.
        
        Returns:
            URL de conexão formatada
        """
        protocol = "amqps" if self.ssl_enabled else "amqp"
        return f"{protocol}://{self.username}:{self.password}@{self.host}:{self.port}{self.virtual_host}"
    
    def to_dict(self, include_password: bool = False) -> dict:
        """
        Converte o modelo para dicionário.
        
        Args:
            include_password: Se deve incluir a senha no dicionário
            
        Returns:
            Dicionário com os dados da conexão
        """
        data = self.dict()
        if not include_password:
            data.pop('password', None)
        return data
    
    @classmethod
    def create_test_connection(cls, connection_id: str = "test_conn") -> "Connection":
        """
        Cria uma conexão de teste para desenvolvimento.
        
        Args:
            connection_id: ID da conexão de teste
            
        Returns:
            Instância de Connection para testes
        """
        return cls(
            connection_id=connection_id,
            host="localhost",
            port=5672,
            username="guest",
            password="guest",
            virtual_host="/",
            ssl_enabled=False,
            connection_timeout=30,
            heartbeat_interval=600,
            status=ConnectionStatus.DISCONNECTED
        )