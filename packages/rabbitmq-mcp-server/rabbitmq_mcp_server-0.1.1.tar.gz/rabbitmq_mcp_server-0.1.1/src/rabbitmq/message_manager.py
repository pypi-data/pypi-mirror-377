"""
Gerenciador de mensagens RabbitMQ.

Este módulo implementa operações de publicação e consumo de mensagens
RabbitMQ, incluindo acknowledge, reject e reprocessamento.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError

from src.shared.models.message import Message, MessageStatus
from src.shared.utils.logging import get_logger
from src.shared.utils.serialization import serialize_message_body
from src.rabbitmq.connection_manager import connection_manager


class MessageManager:
    """Gerenciador de mensagens RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de mensagens."""
        self.logger = get_logger(__name__)
        self.consumed_messages: Dict[str, List[Message]] = {}
    
    async def publish_message(
        self,
        connection_id: str,
        exchange_name: str,
        routing_key: str,
        message_body: str,
        headers: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        content_type: str = "application/json",
        persistent: bool = True,
    ) -> str:
        """
        Publica uma mensagem em um exchange RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            exchange_name: Nome do exchange
            routing_key: Chave de roteamento
            message_body: Corpo da mensagem
            headers: Cabeçalhos da mensagem
            priority: Prioridade da mensagem (0-255)
            content_type: Tipo de conteúdo
            persistent: Se a mensagem deve ser persistida
            
        Returns:
            ID da mensagem publicada
            
        Raises:
            AMQPChannelError: Erro ao publicar mensagem
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                message_id = str(uuid.uuid4())
                
                # Configurar propriedades da mensagem
                properties = pika.BasicProperties(
                    message_id=message_id,
                    content_type=content_type,
                    delivery_mode=2 if persistent else 1,
                    priority=priority,
                    headers=headers or {},
                    timestamp=int(asyncio.get_event_loop().time()),
                )
                
                # Publicar mensagem
                channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=message_body,
                    properties=properties,
                    mandatory=True
                )
                
                self.logger.info("Mensagem publicada com sucesso",
                               connection_id=connection_id,
                               exchange_name=exchange_name,
                               routing_key=routing_key,
                               message_id=message_id)
                
                return message_id
                
            except Exception as e:
                self.logger.error("Erro ao publicar mensagem",
                                connection_id=connection_id,
                                exchange_name=exchange_name,
                                routing_key=routing_key,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao publicar mensagem: {str(e)}")
    
    async def consume_messages(
        self,
        connection_id: str,
        queue_name: str,
        count: int = 1,
        auto_ack: bool = False,
        timeout: int = 30,
    ) -> List[Message]:
        """
        Consome mensagens de uma fila RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            queue_name: Nome da fila
            count: Número de mensagens a consumir
            auto_ack: Se deve fazer acknowledge automático
            timeout: Timeout em segundos
            
        Returns:
            Lista de mensagens consumidas
            
        Raises:
            AMQPChannelError: Erro ao consumir mensagens
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                messages = []
                consumed_count = 0
                
                # Configurar callback para mensagens
                def message_callback(ch, method, properties, body):
                    nonlocal consumed_count
                    
                    if consumed_count >= count:
                        return
                    
                    # Criar modelo da mensagem
                    message = Message(
                        id=properties.message_id or str(uuid.uuid4()),
                        body=body.decode('utf-8'),
                        headers=properties.headers or {},
                        priority=properties.priority or 0,
                        content_type=properties.content_type or "application/json",
                        delivery_tag=method.delivery_tag,
                        exchange=method.exchange,
                        routing_key=method.routing_key,
                        redelivered=method.redelivered,
                        status=MessageStatus.CONSUMED,
                    )
                    
                    messages.append(message)
                    consumed_count += 1
                    
                    # Auto-ack se habilitado
                    if auto_ack:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                
                # Configurar consumer
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=message_callback,
                    auto_ack=auto_ack
                )
                
                # Consumir mensagens com timeout
                start_time = asyncio.get_event_loop().time()
                while consumed_count < count and (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        # Processar eventos do canal
                        channel.connection.process_data_events(time_limit=0.1)
                        await asyncio.sleep(0.01)
                    except Exception as e:
                        self.logger.warning("Erro ao processar eventos do canal",
                                          error=str(e))
                        break
                
                # Cancelar consumer
                channel.basic_cancel(consumer_tag=channel.consumer_tags[0] if channel.consumer_tags else None)
                
                # Armazenar mensagens consumidas
                if connection_id not in self.consumed_messages:
                    self.consumed_messages[connection_id] = []
                self.consumed_messages[connection_id].extend(messages)
                
                self.logger.info("Mensagens consumidas",
                               connection_id=connection_id,
                               queue_name=queue_name,
                               count=len(messages))
                
                return messages
                
            except Exception as e:
                self.logger.error("Erro ao consumir mensagens",
                                connection_id=connection_id,
                                queue_name=queue_name,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao consumir mensagens: {str(e)}")
    
    async def acknowledge_messages(
        self,
        connection_id: str,
        delivery_tags: List[int],
        multiple: bool = False,
    ) -> bool:
        """
        Faz acknowledge de mensagens.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            delivery_tags: Lista de delivery tags
            multiple: Se deve fazer ack de todas as mensagens até o tag especificado
            
        Returns:
            True se acknowledge bem-sucedido
            
        Raises:
            AMQPChannelError: Erro ao fazer acknowledge
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                for delivery_tag in delivery_tags:
                    channel.basic_ack(
                        delivery_tag=delivery_tag,
                        multiple=multiple
                    )
                
                self.logger.info("Mensagens reconhecidas",
                               connection_id=connection_id,
                               delivery_tags=delivery_tags,
                               multiple=multiple)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao reconhecer mensagens",
                                connection_id=connection_id,
                                delivery_tags=delivery_tags,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao reconhecer mensagens: {str(e)}")
    
    async def reject_messages(
        self,
        connection_id: str,
        delivery_tags: List[int],
        requeue: bool = True,
        multiple: bool = False,
    ) -> bool:
        """
        Rejeita mensagens.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            delivery_tags: Lista de delivery tags
            requeue: Se deve recolocar mensagens na fila
            multiple: Se deve rejeitar todas as mensagens até o tag especificado
            
        Returns:
            True se rejeição bem-sucedida
            
        Raises:
            AMQPChannelError: Erro ao rejeitar mensagens
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                for delivery_tag in delivery_tags:
                    channel.basic_nack(
                        delivery_tag=delivery_tag,
                        requeue=requeue,
                        multiple=multiple
                    )
                
                self.logger.info("Mensagens rejeitadas",
                               connection_id=connection_id,
                               delivery_tags=delivery_tags,
                               requeue=requeue,
                               multiple=multiple)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao rejeitar mensagens",
                                connection_id=connection_id,
                                delivery_tags=delivery_tags,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao rejeitar mensagens: {str(e)}")
    
    async def get_consumed_messages(self, connection_id: str) -> List[Message]:
        """
        Obtém mensagens consumidas de uma conexão.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Lista de mensagens consumidas
        """
        return self.consumed_messages.get(connection_id, [])
    
    async def clear_consumed_messages(self, connection_id: str):
        """
        Limpa mensagens consumidas de uma conexão.
        
        Args:
            connection_id: ID da conexão
        """
        if connection_id in self.consumed_messages:
            del self.consumed_messages[connection_id]
        
        self.logger.info("Mensagens consumidas limpas",
                       connection_id=connection_id)


# Instância global do gerenciador
message_manager = MessageManager()
