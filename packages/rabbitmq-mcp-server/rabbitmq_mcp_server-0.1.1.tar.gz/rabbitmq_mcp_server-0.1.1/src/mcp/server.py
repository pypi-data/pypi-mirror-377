"""
RabbitMQ MCP Server - Main Server Module
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

Servidor MCP para RabbitMQ.

Este módulo implementa o servidor MCP principal que expõe todas as
ferramentas de gerenciamento RabbitMQ através do protocolo MCP.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from src.mcp.tools.connection_tools import (
    connection_connect,
    connection_disconnect,
    connection_list,
    connection_status,
)
from src.mcp.tools.dlq_tools import dlq_configure, dlq_manage
from src.mcp.tools.exchange_tools import (
    exchange_bind,
    exchange_create,
    exchange_delete,
    exchange_unbind,
)
from src.mcp.tools.message_tools import (
    message_acknowledge,
    message_consume,
    message_publish,
    message_reject,
)
from src.mcp.tools.monitor_tools import monitor_health, monitor_stats
from src.mcp.tools.queue_tools import (
    queue_create,
    queue_delete,
    queue_list,
    queue_purge,
)
from src.shared.utils.logging import configure_logging, get_logger


class RabbitMQMCPServer:
    """Servidor MCP para RabbitMQ."""
    
    def __init__(self):
        """Inicializa o servidor MCP."""
        self.server = Server("rabbitmq-mcp-server")
        self.logger = get_logger(__name__)
        self._register_tools()
        self._register_handlers()
    
    def _register_tools(self):
        """Registra todas as ferramentas MCP."""
        # Ferramentas de conexão
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool
    
    def _register_handlers(self):
        """Registra handlers do servidor."""
        pass
    
    async def _list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """
        Lista todas as ferramentas disponíveis.
        
        Args:
            request: Requisição de listagem de ferramentas
            
        Returns:
            Lista de ferramentas disponíveis
        """
        self.logger.info("Listando ferramentas MCP")
        
        tools = [
            # Ferramentas de conexão
            Tool(
                name="connection_connect",
                description="Establish a connection to a RabbitMQ server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "description": "Hostname or IP of the RabbitMQ server"},
                        "port": {"type": "integer", "description": "Port of the RabbitMQ server", "default": 5672},
                        "username": {"type": "string", "description": "Username for authentication"},
                        "password": {"type": "string", "description": "Password for authentication"},
                        "virtual_host": {"type": "string", "description": "RabbitMQ virtual host", "default": "/"},
                        "ssl_enabled": {"type": "boolean", "description": "Whether SSL/TLS is enabled", "default": False},
                        "connection_timeout": {"type": "integer", "description": "Connection timeout in seconds", "default": 30},
                        "heartbeat_interval": {"type": "integer", "description": "Heartbeat interval in seconds", "default": 600},
                    },
                    "required": ["host", "username", "password"]
                }
            ),
            Tool(
                name="connection_disconnect",
                description="Disconnect from a RabbitMQ server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the connection to disconnect"}
                    },
                    "required": ["connection_id"]
                }
            ),
            Tool(
                name="connection_status",
                description="Get the status of a RabbitMQ connection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the connection to check"}
                    },
                    "required": ["connection_id"]
                }
            ),
            Tool(
                name="connection_list",
                description="List all active RabbitMQ connections",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_stats": {"type": "boolean", "description": "Whether to include connection statistics", "default": True}
                    }
                }
            ),
            
            # Ferramentas de fila
            Tool(
                name="queue_create",
                description="Create a new queue in RabbitMQ with specified properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "queue_name": {"type": "string", "description": "Name of the queue to create"},
                        "durable": {"type": "boolean", "description": "Whether the queue should survive broker restart", "default": True},
                        "exclusive": {"type": "boolean", "description": "Whether the queue is exclusive to the connection", "default": False},
                        "auto_delete": {"type": "boolean", "description": "Whether the queue should be deleted when unused", "default": False},
                        "arguments": {"type": "object", "description": "Additional queue arguments", "default": {}},
                    },
                    "required": ["connection_id", "queue_name"]
                }
            ),
            Tool(
                name="queue_delete",
                description="Delete an existing queue from RabbitMQ",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "queue_name": {"type": "string", "description": "Name of the queue to delete"},
                        "if_unused": {"type": "boolean", "description": "Only delete if queue has no consumers", "default": False},
                        "if_empty": {"type": "boolean", "description": "Only delete if queue has no messages", "default": False},
                    },
                    "required": ["connection_id", "queue_name"]
                }
            ),
            Tool(
                name="queue_list",
                description="List all queues in the RabbitMQ server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "vhost": {"type": "string", "description": "Virtual host to list queues from", "default": "/"},
                        "include_stats": {"type": "boolean", "description": "Whether to include queue statistics", "default": True},
                    },
                    "required": ["connection_id"]
                }
            ),
            Tool(
                name="queue_purge",
                description="Remove all messages from a queue without deleting the queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "queue_name": {"type": "string", "description": "Name of the queue to purge"},
                    },
                    "required": ["connection_id", "queue_name"]
                }
            ),
            
            # Ferramentas de mensagem
            Tool(
                name="message_publish",
                description="Publish a message to a RabbitMQ exchange",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "exchange_name": {"type": "string", "description": "Name of the exchange to publish to"},
                        "routing_key": {"type": "string", "description": "Routing key for message delivery"},
                        "message_body": {"type": "string", "description": "Content of the message"},
                        "headers": {"type": "object", "description": "Message headers", "default": {}},
                        "priority": {"type": "integer", "description": "Message priority (0-255)", "default": 0},
                        "content_type": {"type": "string", "description": "Content type of the message", "default": "application/json"},
                        "persistent": {"type": "boolean", "description": "Whether the message should be persisted to disk", "default": True},
                    },
                    "required": ["connection_id", "exchange_name", "routing_key", "message_body"]
                }
            ),
            Tool(
                name="message_consume",
                description="Consume messages from a RabbitMQ queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "queue_name": {"type": "string", "description": "Name of the queue to consume from"},
                        "count": {"type": "integer", "description": "Number of messages to consume", "default": 1, "minimum": 1, "maximum": 100},
                        "auto_ack": {"type": "boolean", "description": "Whether to automatically acknowledge messages", "default": False},
                        "timeout": {"type": "integer", "description": "Timeout in seconds for consuming messages", "default": 30},
                    },
                    "required": ["connection_id", "queue_name"]
                }
            ),
            Tool(
                name="message_acknowledge",
                description="Acknowledge one or more messages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "delivery_tags": {"type": "array", "items": {"type": "integer"}, "description": "List of delivery tags to acknowledge"},
                        "multiple": {"type": "boolean", "description": "Whether to acknowledge all messages up to the specified tag", "default": False},
                    },
                    "required": ["connection_id", "delivery_tags"]
                }
            ),
            Tool(
                name="message_reject",
                description="Reject one or more messages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "delivery_tags": {"type": "array", "items": {"type": "integer"}, "description": "List of delivery tags to reject"},
                        "requeue": {"type": "boolean", "description": "Whether to requeue rejected messages", "default": True},
                        "multiple": {"type": "boolean", "description": "Whether to reject all messages up to the specified tag", "default": False},
                    },
                    "required": ["connection_id", "delivery_tags"]
                }
            ),
            
            # Ferramentas de exchange
            Tool(
                name="exchange_create",
                description="Create a new exchange in RabbitMQ",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "exchange_name": {"type": "string", "description": "Name of the exchange to create"},
                        "exchange_type": {"type": "string", "enum": ["direct", "topic", "fanout", "headers"], "description": "Type of exchange to create"},
                        "durable": {"type": "boolean", "description": "Whether the exchange should survive broker restart", "default": True},
                        "auto_delete": {"type": "boolean", "description": "Whether the exchange should be deleted when unused", "default": False},
                        "internal": {"type": "boolean", "description": "Whether the exchange is internal (not for client use)", "default": False},
                        "arguments": {"type": "object", "description": "Additional exchange arguments", "default": {}},
                    },
                    "required": ["connection_id", "exchange_name", "exchange_type"]
                }
            ),
            Tool(
                name="exchange_delete",
                description="Delete an existing exchange from RabbitMQ",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "exchange_name": {"type": "string", "description": "Name of the exchange to delete"},
                        "if_unused": {"type": "boolean", "description": "Only delete if exchange has no bindings", "default": False},
                    },
                    "required": ["connection_id", "exchange_name"]
                }
            ),
            Tool(
                name="exchange_bind",
                description="Bind a queue to an exchange with routing criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "exchange_name": {"type": "string", "description": "Name of the exchange to bind to"},
                        "queue_name": {"type": "string", "description": "Name of the queue to bind"},
                        "routing_key": {"type": "string", "description": "Routing key for the binding"},
                        "arguments": {"type": "object", "description": "Additional binding arguments", "default": {}},
                    },
                    "required": ["connection_id", "exchange_name", "queue_name", "routing_key"]
                }
            ),
            Tool(
                name="exchange_unbind",
                description="Unbind a queue from an exchange",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "exchange_name": {"type": "string", "description": "Name of the exchange to unbind from"},
                        "queue_name": {"type": "string", "description": "Name of the queue to unbind"},
                        "routing_key": {"type": "string", "description": "Routing key for the binding to remove"},
                        "arguments": {"type": "object", "description": "Additional binding arguments", "default": {}},
                    },
                    "required": ["connection_id", "exchange_name", "queue_name", "routing_key"]
                }
            ),
            
            # Ferramentas de DLQ
            Tool(
                name="dlq_configure",
                description="Configure dead letter queue settings for a queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "source_queue": {"type": "string", "description": "Name of the source queue to configure DLQ for"},
                        "dlq_name": {"type": "string", "description": "Name of the dead letter queue"},
                        "dlq_exchange": {"type": "string", "description": "Name of the dead letter exchange"},
                        "routing_key": {"type": "string", "description": "Routing key for dead letter routing"},
                        "ttl": {"type": "integer", "description": "Time-to-live for messages in DLQ (milliseconds)"},
                        "max_length": {"type": "integer", "description": "Maximum number of messages in DLQ"},
                        "max_bytes": {"type": "integer", "description": "Maximum size in bytes for DLQ"},
                    },
                    "required": ["connection_id", "source_queue", "dlq_name", "dlq_exchange", "routing_key"]
                }
            ),
            Tool(
                name="dlq_manage",
                description="Manage dead letter queue operations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "dlq_name": {"type": "string", "description": "Name of the dead letter queue"},
                        "action": {"type": "string", "enum": ["list", "purge", "reprocess", "delete"], "description": "Action to perform on the DLQ"},
                        "reprocess_queue": {"type": "string", "description": "Queue to reprocess messages to (for reprocess action)"},
                        "count": {"type": "integer", "description": "Number of messages to process (for reprocess action)", "default": 10},
                    },
                    "required": ["connection_id", "dlq_name", "action"]
                }
            ),
            
            # Ferramentas de monitoramento
            Tool(
                name="monitor_stats",
                description="Get statistics for queues, exchanges, and connections",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "resource_type": {"type": "string", "enum": ["queue", "exchange", "connection", "all"], "description": "Type of resource to get statistics for"},
                        "resource_name": {"type": "string", "description": "Name of specific resource (optional, for specific resource stats)"},
                        "include_rates": {"type": "boolean", "description": "Whether to include rate statistics", "default": True},
                        "time_range": {"type": "string", "enum": ["1m", "5m", "15m", "1h", "24h"], "description": "Time range for statistics", "default": "5m"},
                    },
                    "required": ["connection_id", "resource_type"]
                }
            ),
            Tool(
                name="monitor_health",
                description="Check the health status of RabbitMQ server and connections",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {"type": "string", "description": "ID of the RabbitMQ connection"},
                        "check_type": {"type": "string", "enum": ["connection", "server", "cluster", "all"], "description": "Type of health check to perform"},
                        "include_details": {"type": "boolean", "description": "Whether to include detailed health information", "default": False},
                    },
                    "required": ["connection_id", "check_type"]
                }
            ),
        ]
        
        return ListToolsResult(tools=tools)
    
    async def _call_tool(self, request: CallToolRequest) -> CallToolResult:
        """
        Executa uma ferramenta MCP.
        
        Args:
            request: Requisição de execução de ferramenta
            
        Returns:
            Resultado da execução da ferramenta
        """
        self.logger.info("Executando ferramenta MCP", 
                        tool_name=request.name,
                        arguments=request.arguments)
        
        try:
            # Mapear nome da ferramenta para função
            tool_functions = {
                # Ferramentas de conexão
                "connection_connect": connection_connect,
                "connection_disconnect": connection_disconnect,
                "connection_status": connection_status,
                "connection_list": connection_list,
                
                # Ferramentas de fila
                "queue_create": queue_create,
                "queue_delete": queue_delete,
                "queue_list": queue_list,
                "queue_purge": queue_purge,
                
                # Ferramentas de mensagem
                "message_publish": message_publish,
                "message_consume": message_consume,
                "message_acknowledge": message_acknowledge,
                "message_reject": message_reject,
                
                # Ferramentas de exchange
                "exchange_create": exchange_create,
                "exchange_delete": exchange_delete,
                "exchange_bind": exchange_bind,
                "exchange_unbind": exchange_unbind,
                
                # Ferramentas de DLQ
                "dlq_configure": dlq_configure,
                "dlq_manage": dlq_manage,
                
                # Ferramentas de monitoramento
                "monitor_stats": monitor_stats,
                "monitor_health": monitor_health,
            }
            
            if request.name not in tool_functions:
                raise ValueError(f"Ferramenta não encontrada: {request.name}")
            
            # Executar ferramenta
            result = tool_functions[request.name](request.arguments)
            
            # Converter resultado para string JSON
            result_text = json.dumps(result, indent=2, ensure_ascii=False)
            
            self.logger.info("Ferramenta executada com sucesso", 
                           tool_name=request.name)
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            self.logger.error("Erro ao executar ferramenta", 
                            tool_name=request.name,
                            error=str(e))
            
            error_result = {
                "error": str(e),
                "tool": request.name,
                "arguments": request.arguments
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
            )
    
    async def run(self):
        """Executa o servidor MCP."""
        self.logger.info("Iniciando servidor MCP RabbitMQ")
        
        # Configurar logging
        configure_logging(level="INFO", format_type="json")
        
        # Executar servidor
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="rabbitmq-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """Função principal do servidor MCP."""
    server = RabbitMQMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())