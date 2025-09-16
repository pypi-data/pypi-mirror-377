"""
Ferramentas MCP para gerenciamento de mensagens RabbitMQ.

Este módulo implementa as ferramentas MCP para publicar, consumir,
confirmar e rejeitar mensagens RabbitMQ.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.exceptions import AMQPError

from src.mcp.schemas.message_schemas import (
    MessageAcknowledgeResponse,
    MessageAcknowledgeSchema,
    MessageConsumeResponse,
    MessageConsumeSchema,
    MessageInfo,
    MessagePublishResponse,
    MessagePublishSchema,
    MessageRejectResponse,
    MessageRejectSchema,
)
from src.mcp.tools.connection_tools import connection_manager
from src.shared.models.message import Message, MessageStatus
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation
from src.shared.utils.validation import validate_message_params, validate_delivery_tags


class MessageManager:
    """Gerenciador de mensagens RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de mensagens."""
        self.messages: Dict[str, Message] = {}
        self.delivery_tags: Dict[str, int] = {}  # Mapeia message_id para delivery_tag
    
    def publish_message(self, params: MessagePublishSchema) -> MessagePublishResponse:
        """
        Publica uma mensagem em um exchange RabbitMQ.
        
        Args:
            params: Parâmetros de publicação da mensagem
            
        Returns:
            Resposta com informações da mensagem publicada
        """
        logger = log_mcp_request("message_publish", params.connection_id)
        
        try:
            # Validar parâmetros
            validated_params = validate_message_params(params.dict())
            
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Gerar ID único para a mensagem
            message_id = str(uuid.uuid4())
            
            # Configurar propriedades da mensagem
            properties = pika.BasicProperties(
                message_id=message_id,
                content_type=params.content_type,
                delivery_mode=2 if params.persistent else 1,  # 2 = persistente, 1 = não persistente
                priority=params.priority,
                headers=params.headers,
                expiration=params.expiration,
                timestamp=int(datetime.utcnow().timestamp())
            )
            
            # Publicar mensagem
            logger.info("Publicando mensagem", 
                       message_id=message_id,
                       exchange_name=params.exchange_name,
                       routing_key=params.routing_key,
                       content_type=params.content_type)
            
            channel.basic_publish(
                exchange=params.exchange_name,
                routing_key=params.routing_key,
                body=params.message_body,
                properties=properties
            )
            
            # Criar modelo da mensagem
            message = Message(
                message_id=message_id,
                body=params.message_body,
                headers=params.headers,
                routing_key=params.routing_key,
                exchange=params.exchange_name,
                queue="",  # Será determinado pelo roteamento
                priority=params.priority,
                content_type=params.content_type,
                status=MessageStatus.PUBLISHED
            )
            
            # Armazenar mensagem
            self.messages[message_id] = message
            
            logger.info("Mensagem publicada com sucesso", 
                       message_id=message_id,
                       exchange_name=params.exchange_name)
            
            return MessagePublishResponse(
                message_id=message_id,
                status="published",
                exchange_name=params.exchange_name,
                routing_key=params.routing_key,
                delivery_tag=0,  # Não aplicável para publicação
                published_at=message.timestamp.isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao publicar mensagem", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao publicar mensagem: {e}")
        except Exception as e:
            logger.error("Erro ao publicar mensagem", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro ao publicar mensagem: {e}")
    
    def consume_messages(self, params: MessageConsumeSchema) -> MessageConsumeResponse:
        """
        Consome mensagens de uma fila RabbitMQ.
        
        Args:
            params: Parâmetros de consumo de mensagens
            
        Returns:
            Resposta com mensagens consumidas
        """
        logger = log_mcp_request("message_consume", params.connection_id)
        
        try:
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Configurar QoS
            channel.basic_qos(prefetch_count=params.count)
            
            messages = []
            message_count = 0
            
            # Função para processar mensagens
            def process_message(ch, method, properties, body):
                nonlocal message_count
                
                if message_count >= params.count:
                    return
                
                # Criar modelo da mensagem
                message = Message(
                    message_id=properties.message_id or str(uuid.uuid4()),
                    body=body.decode('utf-8'),
                    headers=properties.headers or {},
                    routing_key=method.routing_key,
                    exchange=method.exchange,
                    queue=params.queue_name,
                    delivery_tag=method.delivery_tag,
                    redelivered=method.redelivered,
                    priority=properties.priority or 0,
                    content_type=properties.content_type or "application/json",
                    status=MessageStatus.DELIVERED
                )
                
                # Armazenar mensagem e mapear delivery_tag
                self.messages[message.message_id] = message
                self.delivery_tags[message.message_id] = method.delivery_tag
                
                # Adicionar à lista de mensagens
                messages.append(MessageInfo(
                    message_id=message.message_id,
                    body=message.body,
                    headers=message.headers,
                    routing_key=message.routing_key,
                    exchange=message.exchange,
                    queue=message.queue,
                    delivery_tag=message.delivery_tag,
                    redelivered=message.redelivered,
                    priority=message.priority,
                    timestamp=message.timestamp.isoformat(),
                    content_type=message.content_type,
                    content_encoding="utf-8"
                ))
                
                message_count += 1
                
                # Confirmar mensagem se auto_ack estiver habilitado
                if params.auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    message.update_status(MessageStatus.ACKNOWLEDGED)
            
            # Configurar consumidor
            logger.info("Consumindo mensagens", 
                       queue_name=params.queue_name,
                       count=params.count,
                       auto_ack=params.auto_ack)
            
            consumer_tag = channel.basic_consume(
                queue=params.queue_name,
                on_message_callback=process_message,
                auto_ack=False  # Sempre False, controlamos manualmente
            )
            
            # Consumir mensagens com timeout
            start_time = datetime.utcnow()
            timeout_seconds = params.timeout
            
            while message_count < params.count:
                # Verificar timeout
                if (datetime.utcnow() - start_time).seconds >= timeout_seconds:
                    break
                
                # Processar mensagens
                pika_connection.process_data_events(time_limit=1)
            
            # Cancelar consumidor
            channel.basic_cancel(consumer_tag)
            
            logger.info("Mensagens consumidas", 
                       queue_name=params.queue_name,
                       count=len(messages))
            
            return MessageConsumeResponse(
                messages=messages,
                count=len(messages),
                queue_name=params.queue_name,
                consumed_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao consumir mensagens", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao consumir mensagens: {e}")
        except Exception as e:
            logger.error("Erro ao consumir mensagens", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro ao consumir mensagens: {e}")
    
    def acknowledge_messages(self, params: MessageAcknowledgeSchema) -> MessageAcknowledgeResponse:
        """
        Confirma uma ou mais mensagens.
        
        Args:
            params: Parâmetros de confirmação
            
        Returns:
            Resposta com informações da confirmação
        """
        logger = log_mcp_request("message_acknowledge", params.connection_id)
        
        try:
            # Validar delivery_tags
            validated_tags = validate_delivery_tags(params.delivery_tags)
            
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Confirmar mensagens
            logger.info("Confirmando mensagens", 
                       delivery_tags=validated_tags,
                       multiple=params.multiple)
            
            for tag in validated_tags:
                channel.basic_ack(
                    delivery_tag=tag,
                    multiple=params.multiple
                )
                
                # Atualizar status das mensagens
                for message_id, message in self.messages.items():
                    if message.delivery_tag == tag:
                        message.update_status(MessageStatus.ACKNOWLEDGED)
                        break
            
            logger.info("Mensagens confirmadas com sucesso", 
                       count=len(validated_tags))
            
            return MessageAcknowledgeResponse(
                acknowledged=True,
                delivery_tags=validated_tags,
                count=len(validated_tags),
                acknowledged_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao confirmar mensagens", 
                        delivery_tags=params.delivery_tags, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao confirmar mensagens: {e}")
        except Exception as e:
            logger.error("Erro ao confirmar mensagens", 
                        delivery_tags=params.delivery_tags, 
                        error=str(e))
            raise ValueError(f"Erro ao confirmar mensagens: {e}")
    
    def reject_messages(self, params: MessageRejectSchema) -> MessageRejectResponse:
        """
        Rejeita uma ou mais mensagens.
        
        Args:
            params: Parâmetros de rejeição
            
        Returns:
            Resposta com informações da rejeição
        """
        logger = log_mcp_request("message_reject", params.connection_id)
        
        try:
            # Validar delivery_tags
            validated_tags = validate_delivery_tags(params.delivery_tags)
            
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Rejeitar mensagens
            logger.info("Rejeitando mensagens", 
                       delivery_tags=validated_tags,
                       requeue=params.requeue,
                       multiple=params.multiple)
            
            for tag in validated_tags:
                channel.basic_nack(
                    delivery_tag=tag,
                    requeue=params.requeue,
                    multiple=params.multiple
                )
                
                # Atualizar status das mensagens
                for message_id, message in self.messages.items():
                    if message.delivery_tag == tag:
                        message.update_status(MessageStatus.REJECTED)
                        break
            
            logger.info("Mensagens rejeitadas com sucesso", 
                       count=len(validated_tags),
                       requeued=params.requeue)
            
            return MessageRejectResponse(
                rejected=True,
                delivery_tags=validated_tags,
                count=len(validated_tags),
                requeued=params.requeue,
                rejected_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao rejeitar mensagens", 
                        delivery_tags=params.delivery_tags, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao rejeitar mensagens: {e}")
        except Exception as e:
            logger.error("Erro ao rejeitar mensagens", 
                        delivery_tags=params.delivery_tags, 
                        error=str(e))
            raise ValueError(f"Erro ao rejeitar mensagens: {e}")
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """
        Obtém uma mensagem por ID.
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            Instância da mensagem ou None se não encontrada
        """
        return self.messages.get(message_id)


# Instância global do gerenciador de mensagens
message_manager = MessageManager()


def message_publish(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para publicar uma mensagem.
    
    Args:
        params: Parâmetros de publicação
        
    Returns:
        Resposta da publicação
    """
    schema = MessagePublishSchema(**params)
    response = message_manager.publish_message(schema)
    return response.dict()


def message_consume(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para consumir mensagens.
    
    Args:
        params: Parâmetros de consumo
        
    Returns:
        Resposta com mensagens consumidas
    """
    schema = MessageConsumeSchema(**params)
    response = message_manager.consume_messages(schema)
    return response.dict()


def message_acknowledge(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para confirmar mensagens.
    
    Args:
        params: Parâmetros de confirmação
        
    Returns:
        Resposta da confirmação
    """
    schema = MessageAcknowledgeSchema(**params)
    response = message_manager.acknowledge_messages(schema)
    return response.dict()


def message_reject(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para rejeitar mensagens.
    
    Args:
        params: Parâmetros de rejeição
        
    Returns:
        Resposta da rejeição
    """
    schema = MessageRejectSchema(**params)
    response = message_manager.reject_messages(schema)
    return response.dict()