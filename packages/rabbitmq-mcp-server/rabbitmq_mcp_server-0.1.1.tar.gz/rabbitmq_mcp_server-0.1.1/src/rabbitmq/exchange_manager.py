"""
Gerenciador de exchanges RabbitMQ.

Este módulo implementa operações de gerenciamento de exchanges RabbitMQ,
incluindo criação, exclusão, binding e unbinding.
"""

import asyncio
from typing import Dict, List, Optional

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError

from src.shared.models.exchange import Exchange, ExchangeType
from src.shared.utils.logging import get_logger
from src.rabbitmq.connection_manager import connection_manager


class ExchangeManager:
    """Gerenciador de exchanges RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de exchanges."""
        self.logger = get_logger(__name__)
    
    async def create_exchange(
        self,
        connection_id: str,
        exchange_name: str,
        exchange_type: ExchangeType,
        durable: bool = True,
        auto_delete: bool = False,
        internal: bool = False,
        arguments: Optional[Dict] = None,
    ) -> Exchange:
        """
        Cria um novo exchange RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            exchange_type: Tipo do exchange
            durable: Se o exchange deve sobreviver ao reinício do broker
            auto_delete: Se o exchange deve ser deletado quando não usada
            internal: Se o exchange é interno (não para uso de clientes)
            arguments: Argumentos adicionais do exchange
            
        Returns:
            Modelo do exchange criado
            
        Raises:
            AMQPChannelError: Erro ao criar exchange
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Declarar exchange
                channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=exchange_type.value,
                    durable=durable,
                    auto_delete=auto_delete,
                    internal=internal,
                    arguments=arguments or {}
                )
                
                # Criar modelo do exchange
                exchange = Exchange(
                    name=exchange_name,
                    type=exchange_type,
                    durable=durable,
                    auto_delete=auto_delete,
                    internal=internal,
                    arguments=arguments or {},
                )
                
                self.logger.info("Exchange criado com sucesso",
                               connection_id=connection_id,
                               exchange_name=exchange_name,
                               exchange_type=exchange_type.value,
                               durable=durable)
                
                return exchange
                
            except Exception as e:
                self.logger.error("Erro ao criar exchange",
                                connection_id=connection_id,
                                exchange_name=exchange_name,
                                exchange_type=exchange_type.value,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao criar exchange: {str(e)}")
    
    async def delete_exchange(
        self,
        connection_id: str,
        exchange_name: str,
        if_unused: bool = False,
    ) -> bool:
        """
        Deleta um exchange RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            if_unused: Deletar apenas se não tiver bindings
            
        Returns:
            True se deletado com sucesso
            
        Raises:
            AMQPChannelError: Erro ao deletar exchange
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Deletar exchange
                channel.exchange_delete(
                    exchange=exchange_name,
                    if_unused=if_unused
                )
                
                self.logger.info("Exchange deletado com sucesso",
                               connection_id=connection_id,
                               exchange_name=exchange_name,
                               if_unused=if_unused)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao deletar exchange",
                                connection_id=connection_id,
                                exchange_name=exchange_name,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao deletar exchange: {str(e)}")
    
    async def bind_queue(
        self,
        connection_id: str,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        arguments: Optional[Dict] = None,
    ) -> bool:
        """
        Faz bind de uma fila a um exchange.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            queue_name: Nome da fila
            routing_key: Chave de roteamento
            arguments: Argumentos adicionais do binding
            
        Returns:
            True se bind bem-sucedido
            
        Raises:
            AMQPChannelError: Erro ao fazer bind
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Fazer bind
                channel.queue_bind(
                    exchange=exchange_name,
                    queue=queue_name,
                    routing_key=routing_key,
                    arguments=arguments or {}
                )
                
                self.logger.info("Bind realizado com sucesso",
                               connection_id=connection_id,
                               exchange_name=exchange_name,
                               queue_name=queue_name,
                               routing_key=routing_key)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao fazer bind",
                                connection_id=connection_id,
                                exchange_name=exchange_name,
                                queue_name=queue_name,
                                routing_key=routing_key,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao fazer bind: {str(e)}")
    
    async def unbind_queue(
        self,
        connection_id: str,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        arguments: Optional[Dict] = None,
    ) -> bool:
        """
        Remove bind de uma fila de um exchange.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            queue_name: Nome da fila
            routing_key: Chave de roteamento
            arguments: Argumentos adicionais do binding
            
        Returns:
            True se unbind bem-sucedido
            
        Raises:
            AMQPChannelError: Erro ao fazer unbind
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Fazer unbind
                channel.queue_unbind(
                    exchange=exchange_name,
                    queue=queue_name,
                    routing_key=routing_key,
                    arguments=arguments or {}
                )
                
                self.logger.info("Unbind realizado com sucesso",
                               connection_id=connection_id,
                               exchange_name=exchange_name,
                               queue_name=queue_name,
                               routing_key=routing_key)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao fazer unbind",
                                connection_id=connection_id,
                                exchange_name=exchange_name,
                                queue_name=queue_name,
                                routing_key=routing_key,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao fazer unbind: {str(e)}")
    
    async def bind_exchange(
        self,
        connection_id: str,
        source_exchange: str,
        destination_exchange: str,
        routing_key: str,
        arguments: Optional[Dict] = None,
    ) -> bool:
        """
        Faz bind de um exchange a outro exchange.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            source_exchange: Nome do exchange de origem
            destination_exchange: Nome do exchange de destino
            routing_key: Chave de roteamento
            arguments: Argumentos adicionais do binding
            
        Returns:
            True se bind bem-sucedido
            
        Raises:
            AMQPChannelError: Erro ao fazer bind
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Fazer bind de exchange para exchange
                channel.exchange_bind(
                    destination=destination_exchange,
                    source=source_exchange,
                    routing_key=routing_key,
                    arguments=arguments or {}
                )
                
                self.logger.info("Bind de exchange realizado com sucesso",
                               connection_id=connection_id,
                               source_exchange=source_exchange,
                               destination_exchange=destination_exchange,
                               routing_key=routing_key)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao fazer bind de exchange",
                                connection_id=connection_id,
                                source_exchange=source_exchange,
                                destination_exchange=destination_exchange,
                                routing_key=routing_key,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao fazer bind de exchange: {str(e)}")
    
    async def unbind_exchange(
        self,
        connection_id: str,
        source_exchange: str,
        destination_exchange: str,
        routing_key: str,
        arguments: Optional[Dict] = None,
    ) -> bool:
        """
        Remove bind de um exchange de outro exchange.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            source_exchange: Nome do exchange de origem
            destination_exchange: Nome do exchange de destino
            routing_key: Chave de roteamento
            arguments: Argumentos adicionais do binding
            
        Returns:
            True se unbind bem-sucedido
            
        Raises:
            AMQPChannelError: Erro ao fazer unbind
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Fazer unbind de exchange para exchange
                channel.exchange_unbind(
                    destination=destination_exchange,
                    source=source_exchange,
                    routing_key=routing_key,
                    arguments=arguments or {}
                )
                
                self.logger.info("Unbind de exchange realizado com sucesso",
                               connection_id=connection_id,
                               source_exchange=source_exchange,
                               destination_exchange=destination_exchange,
                               routing_key=routing_key)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao fazer unbind de exchange",
                                connection_id=connection_id,
                                source_exchange=source_exchange,
                                destination_exchange=destination_exchange,
                                routing_key=routing_key,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao fazer unbind de exchange: {str(e)}")
    
    async def get_exchange_info(
        self,
        connection_id: str,
        exchange_name: str,
    ) -> Optional[Exchange]:
        """
        Obtém informações de um exchange específico.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            
        Returns:
            Informações do exchange ou None se não encontrado
            
        Raises:
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Declarar exchange passivo (não cria se não existir)
                method = channel.exchange_declare(
                    exchange=exchange_name,
                    passive=True
                )
                
                # Criar modelo do exchange
                exchange = Exchange(
                    name=exchange_name,
                    type=ExchangeType(method.method.exchange_type),
                    durable=True,  # Assumir durável por padrão
                    auto_delete=False,
                    internal=False,
                    arguments={},
                )
                
                return exchange
                
            except Exception as e:
                self.logger.warning("Exchange não encontrado",
                                  connection_id=connection_id,
                                  exchange_name=exchange_name,
                                  error=str(e))
                return None


# Instância global do gerenciador
exchange_manager = ExchangeManager()
