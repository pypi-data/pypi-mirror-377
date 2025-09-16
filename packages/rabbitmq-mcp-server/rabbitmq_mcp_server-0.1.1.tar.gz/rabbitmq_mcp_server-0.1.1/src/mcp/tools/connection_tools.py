"""
RabbitMQ MCP Server - Connection Tools
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

Ferramentas MCP para gerenciamento de conexões RabbitMQ.

Este módulo implementa as ferramentas MCP para conectar, desconectar,
verificar status e listar conexões RabbitMQ.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.adapters.blocking_connection import BlockingConnection
from pika.connection import ConnectionParameters

from src.mcp.schemas.connection_schemas import (
    ConnectionConnectResponse,
    ConnectionDisconnectResponse,
    ConnectionDisconnectSchema,
    ConnectionListResponse,
    ConnectionListSchema,
    ConnectionStatusResponse,
    ConnectionStatusSchema,
    ConnectionConnectSchema,
)
from src.shared.models.connection import Connection, ConnectionStatus
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation
from src.shared.utils.serialization import serialize_model
from src.shared.utils.validation import validate_connection_params


class ConnectionManager:
    """Gerenciador de conexões RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de conexões."""
        self.connections: Dict[str, Connection] = {}
        self.pika_connections: Dict[str, BlockingConnection] = {}
    
    def connect(self, params: ConnectionConnectSchema) -> ConnectionConnectResponse:
        """
        Estabelece uma conexão com o RabbitMQ.
        
        Args:
            params: Parâmetros de conexão
            
        Returns:
            Resposta com informações da conexão estabelecida
        """
        logger = log_mcp_request("connection_connect")
        
        try:
            # Validar parâmetros
            validated_params = validate_connection_params(params.dict())
            
            # Criar ID único para a conexão
            connection_id = str(uuid.uuid4())
            
            # Configurar parâmetros de conexão
            connection_params = ConnectionParameters(
                host=validated_params["host"],
                port=validated_params.get("port", 5672),
                virtual_host=validated_params.get("virtual_host", "/"),
                credentials=pika.PlainCredentials(
                    validated_params["username"],
                    validated_params["password"]
                ),
                connection_attempts=3,
                retry_delay=2,
                socket_timeout=validated_params.get("connection_timeout", 30),
                heartbeat=validated_params.get("heartbeat_interval", 600)
            )
            
            # Configurar SSL se habilitado
            if validated_params.get("ssl_enabled", False):
                ssl_options = pika.SSLOptions(
                    context=None,  # Será configurado pelo pika
                    server_hostname=validated_params["host"]
                )
                connection_params.ssl_options = ssl_options
            
            # Estabelecer conexão
            logger.info("Estabelecendo conexão RabbitMQ", 
                       host=validated_params["host"], 
                       port=validated_params.get("port", 5672))
            
            pika_connection = BlockingConnection(connection_params)
            
            # Criar modelo de conexão
            connection = Connection(
                connection_id=connection_id,
                host=validated_params["host"],
                port=validated_params.get("port", 5672),
                username=validated_params["username"],
                password=validated_params["password"],
                virtual_host=validated_params.get("virtual_host", "/"),
                ssl_enabled=validated_params.get("ssl_enabled", False),
                ssl_cert_path=validated_params.get("ssl_cert_path"),
                ssl_key_path=validated_params.get("ssl_key_path"),
                ssl_ca_path=validated_params.get("ssl_ca_path"),
                connection_timeout=validated_params.get("connection_timeout", 30),
                heartbeat_interval=validated_params.get("heartbeat_interval", 600),
                status=ConnectionStatus.CONNECTED
            )
            
            # Armazenar conexões
            self.connections[connection_id] = connection
            self.pika_connections[connection_id] = pika_connection
            
            logger.info("Conexão estabelecida com sucesso", connection_id=connection_id)
            
            return ConnectionConnectResponse(
                connection_id=connection_id,
                status=connection.status.value,
                host=connection.host,
                port=connection.port,
                virtual_host=connection.virtual_host,
                ssl_enabled=connection.ssl_enabled,
                connected_at=connection.created_at.isoformat()
            )
            
        except Exception as e:
            logger.error("Erro ao estabelecer conexão", error=str(e))
            raise ValueError(f"Erro ao conectar ao RabbitMQ: {e}")
    
    def disconnect(self, params: ConnectionDisconnectSchema) -> ConnectionDisconnectResponse:
        """
        Desconecta de uma conexão RabbitMQ.
        
        Args:
            params: Parâmetros de desconexão
            
        Returns:
            Resposta com informações da desconexão
        """
        logger = log_mcp_request("connection_disconnect", params.connection_id)
        
        try:
            connection_id = params.connection_id
            
            if connection_id not in self.connections:
                raise ValueError(f"Conexão {connection_id} não encontrada")
            
            # Fechar conexão pika
            if connection_id in self.pika_connections:
                pika_connection = self.pika_connections[connection_id]
                if not pika_connection.is_closed:
                    pika_connection.close()
                del self.pika_connections[connection_id]
            
            # Atualizar status da conexão
            connection = self.connections[connection_id]
            connection.update_status(ConnectionStatus.DISCONNECTED)
            
            logger.info("Conexão desconectada com sucesso", connection_id=connection_id)
            
            return ConnectionDisconnectResponse(
                connection_id=connection_id,
                status=connection.status.value,
                disconnected_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error("Erro ao desconectar", connection_id=params.connection_id, error=str(e))
            raise ValueError(f"Erro ao desconectar: {e}")
    
    def get_status(self, params: ConnectionStatusSchema) -> ConnectionStatusResponse:
        """
        Obtém o status de uma conexão RabbitMQ.
        
        Args:
            params: Parâmetros de verificação de status
            
        Returns:
            Resposta com status da conexão
        """
        logger = log_mcp_request("connection_status", params.connection_id)
        
        try:
            connection_id = params.connection_id
            
            if connection_id not in self.connections:
                raise ValueError(f"Conexão {connection_id} não encontrada")
            
            connection = self.connections[connection_id]
            
            # Verificar se a conexão pika ainda está ativa
            is_active = False
            if connection_id in self.pika_connections:
                pika_connection = self.pika_connections[connection_id]
                is_active = not pika_connection.is_closed
            
            # Atualizar status se necessário
            if not is_active and connection.status == ConnectionStatus.CONNECTED:
                connection.update_status(ConnectionStatus.DISCONNECTED)
            
            logger.info("Status da conexão obtido", 
                       connection_id=connection_id, 
                       status=connection.status.value)
            
            return ConnectionStatusResponse(
                connection_id=connection_id,
                status=connection.status.value,
                host=connection.host,
                port=connection.port,
                virtual_host=connection.virtual_host,
                ssl_enabled=connection.ssl_enabled,
                connected_at=connection.created_at.isoformat(),
                last_used=connection.last_used.isoformat(),
                message_count=0,  # TODO: Implementar contador de mensagens
                error_count=0     # TODO: Implementar contador de erros
            )
            
        except Exception as e:
            logger.error("Erro ao obter status", connection_id=params.connection_id, error=str(e))
            raise ValueError(f"Erro ao obter status: {e}")
    
    def list_connections(self, params: ConnectionListSchema) -> ConnectionListResponse:
        """
        Lista todas as conexões ativas.
        
        Args:
            params: Parâmetros de listagem
            
        Returns:
            Resposta com lista de conexões
        """
        logger = log_mcp_request("connection_list")
        
        try:
            connections = []
            
            for connection_id, connection in self.connections.items():
                # Verificar se a conexão pika ainda está ativa
                is_active = False
                if connection_id in self.pika_connections:
                    pika_connection = self.pika_connections[connection_id]
                    is_active = not pika_connection.is_closed
                
                # Atualizar status se necessário
                if not is_active and connection.status == ConnectionStatus.CONNECTED:
                    connection.update_status(ConnectionStatus.DISCONNECTED)
                
                # Incluir estatísticas se solicitado
                if params.include_stats:
                    connections.append(ConnectionStatusResponse(
                        connection_id=connection_id,
                        status=connection.status.value,
                        host=connection.host,
                        port=connection.port,
                        virtual_host=connection.virtual_host,
                        ssl_enabled=connection.ssl_enabled,
                        connected_at=connection.created_at.isoformat(),
                        last_used=connection.last_used.isoformat(),
                        message_count=0,  # TODO: Implementar contador de mensagens
                        error_count=0     # TODO: Implementar contador de erros
                    ))
            
            logger.info("Lista de conexões obtida", count=len(connections))
            
            return ConnectionListResponse(
                connections=connections,
                total_count=len(connections)
            )
            
        except Exception as e:
            logger.error("Erro ao listar conexões", error=str(e))
            raise ValueError(f"Erro ao listar conexões: {e}")
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """
        Obtém uma conexão por ID.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Instância da conexão ou None se não encontrada
        """
        return self.connections.get(connection_id)
    
    def get_pika_connection(self, connection_id: str) -> Optional[BlockingConnection]:
        """
        Obtém uma conexão pika por ID.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Instância da conexão pika ou None se não encontrada
        """
        return self.pika_connections.get(connection_id)


# Instância global do gerenciador de conexões
connection_manager = ConnectionManager()


def connection_connect(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para conectar ao RabbitMQ.
    
    Args:
        params: Parâmetros de conexão
        
    Returns:
        Resposta da conexão
    """
    schema = ConnectionConnectSchema(**params)
    response = connection_manager.connect(schema)
    return response.dict()


def connection_disconnect(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para desconectar do RabbitMQ.
    
    Args:
        params: Parâmetros de desconexão
        
    Returns:
        Resposta da desconexão
    """
    schema = ConnectionDisconnectSchema(**params)
    response = connection_manager.disconnect(schema)
    return response.dict()


def connection_status(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para verificar status da conexão.
    
    Args:
        params: Parâmetros de verificação de status
        
    Returns:
        Resposta com status da conexão
    """
    schema = ConnectionStatusSchema(**params)
    response = connection_manager.get_status(schema)
    return response.dict()


def connection_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para listar conexões ativas.
    
    Args:
        params: Parâmetros de listagem
        
    Returns:
        Resposta com lista de conexões
    """
    schema = ConnectionListSchema(**params)
    response = connection_manager.list_connections(schema)
    return response.dict()