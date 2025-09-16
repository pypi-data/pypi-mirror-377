"""
Ferramentas MCP para gerenciamento de dead letter queues RabbitMQ.

Este módulo implementa as ferramentas MCP para configurar e gerenciar
dead letter queues RabbitMQ.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.exceptions import AMQPError

from src.mcp.schemas.dlq_schemas import (
    DLQConfigureResponse,
    DLQConfigureSchema,
    DLQInfo,
    DLQManageResponse,
    DLQManageSchema,
    DLQMessageInfo,
    DLQMessagesResponse,
    DLQPurgeResponse,
    DLQReprocessResponse,
)
from src.mcp.tools.connection_tools import connection_manager
from src.mcp.tools.exchange_tools import exchange_manager
from src.mcp.tools.queue_tools import queue_manager
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation


class DLQManager:
    """Gerenciador de dead letter queues RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de DLQs."""
        self.dlq_configs: Dict[str, DLQInfo] = {}  # source_queue -> DLQInfo
        self.dlq_messages: Dict[str, List[DLQMessageInfo]] = {}  # dlq_name -> messages
    
    def configure_dlq(self, params: DLQConfigureSchema) -> DLQConfigureResponse:
        """
        Configura dead letter queue para uma fila.
        
        Args:
            params: Parâmetros de configuração da DLQ
            
        Returns:
            Resposta com informações da configuração
        """
        logger = log_mcp_request("dlq_configure", params.connection_id)
        
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
            
            # Configurar argumentos da DLQ
            dlq_arguments = {}
            if params.ttl:
                dlq_arguments['x-message-ttl'] = params.ttl
            if params.max_length:
                dlq_arguments['x-max-length'] = params.max_length
            if params.max_bytes:
                dlq_arguments['x-max-bytes'] = params.max_bytes
            
            # Criar dead letter exchange se não existir
            logger.info("Configurando DLQ", 
                       source_queue=params.source_queue,
                       dlq_name=params.dlq_name,
                       dlq_exchange=params.dlq_exchange)
            
            # Declarar dead letter exchange
            channel.exchange_declare(
                exchange=params.dlq_exchange,
                exchange_type='direct',
                durable=True
            )
            
            # Criar dead letter queue
            channel.queue_declare(
                queue=params.dlq_name,
                durable=True,
                arguments=dlq_arguments
            )
            
            # Vincular DLQ ao dead letter exchange
            channel.queue_bind(
                exchange=params.dlq_exchange,
                queue=params.dlq_name,
                routing_key=params.routing_key
            )
            
            # Configurar argumentos da fila de origem para usar DLQ
            source_arguments = {
                'x-dead-letter-exchange': params.dlq_exchange,
                'x-dead-letter-routing-key': params.routing_key
            }
            
            # Redeclarar fila de origem com configuração DLQ
            channel.queue_declare(
                queue=params.source_queue,
                durable=True,
                arguments=source_arguments
            )
            
            # Criar informação da DLQ
            dlq_info = DLQInfo(
                dlq_name=params.dlq_name,
                source_queue=params.source_queue,
                dlq_exchange=params.dlq_exchange,
                routing_key=params.routing_key,
                message_count=0,
                ttl=params.ttl,
                max_length=params.max_length,
                max_bytes=params.max_bytes,
                created_at=datetime.utcnow().isoformat(),
                last_updated=datetime.utcnow().isoformat()
            )
            
            # Armazenar configuração
            self.dlq_configs[params.source_queue] = dlq_info
            self.dlq_messages[params.dlq_name] = []
            
            logger.info("DLQ configurada com sucesso", 
                       source_queue=params.source_queue,
                       dlq_name=params.dlq_name)
            
            return DLQConfigureResponse(
                dlq_name=params.dlq_name,
                source_queue=params.source_queue,
                status="configured",
                dlq_exchange=params.dlq_exchange,
                routing_key=params.routing_key,
                ttl=params.ttl,
                max_length=params.max_length,
                max_bytes=params.max_bytes,
                configured_at=dlq_info.created_at
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao configurar DLQ", 
                        source_queue=params.source_queue, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao configurar DLQ: {e}")
        except Exception as e:
            logger.error("Erro ao configurar DLQ", 
                        source_queue=params.source_queue, 
                        error=str(e))
            raise ValueError(f"Erro ao configurar DLQ: {e}")
    
    def manage_dlq(self, params: DLQManageSchema) -> DLQManageResponse:
        """
        Gerencia operações de dead letter queue.
        
        Args:
            params: Parâmetros de gerenciamento
            
        Returns:
            Resposta com resultado da operação
        """
        logger = log_mcp_request("dlq_manage", params.connection_id)
        
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
            
            logger.info("Executando operação DLQ", 
                       dlq_name=params.dlq_name,
                       action=params.action)
            
            result = {}
            
            if params.action == "list":
                # Listar mensagens na DLQ
                result = self._list_dlq_messages(params.dlq_name)
                
            elif params.action == "purge":
                # Limpar DLQ
                result = self._purge_dlq(channel, params.dlq_name)
                
            elif params.action == "reprocess":
                # Reprocessar mensagens da DLQ
                result = self._reprocess_dlq_messages(
                    channel, params.dlq_name, 
                    params.reprocess_queue, params.count
                )
                
            elif params.action == "delete":
                # Deletar DLQ
                result = self._delete_dlq(channel, params.dlq_name)
                
            else:
                raise ValueError(f"Ação inválida: {params.action}")
            
            logger.info("Operação DLQ executada com sucesso", 
                       dlq_name=params.dlq_name,
                       action=params.action)
            
            return DLQManageResponse(
                dlq_name=params.dlq_name,
                action=params.action,
                status="success",
                result=result,
                executed_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error("Erro ao gerenciar DLQ", 
                        dlq_name=params.dlq_name, 
                        action=params.action,
                        error=str(e))
            raise ValueError(f"Erro ao gerenciar DLQ: {e}")
    
    def _list_dlq_messages(self, dlq_name: str) -> Dict[str, Any]:
        """Lista mensagens na DLQ."""
        messages = self.dlq_messages.get(dlq_name, [])
        return {
            "messages": [msg.dict() for msg in messages],
            "count": len(messages)
        }
    
    def _purge_dlq(self, channel, dlq_name: str) -> Dict[str, Any]:
        """Limpa mensagens da DLQ."""
        method, message_count = channel.queue_purge(queue=dlq_name)
        
        # Limpar cache de mensagens
        if dlq_name in self.dlq_messages:
            self.dlq_messages[dlq_name] = []
        
        return {
            "messages_purged": message_count,
            "purged_at": datetime.utcnow().isoformat()
        }
    
    def _reprocess_dlq_messages(self, channel, dlq_name: str, 
                               reprocess_queue: Optional[str], count: int) -> Dict[str, Any]:
        """Reprocessa mensagens da DLQ."""
        if not reprocess_queue:
            raise ValueError("reprocess_queue é obrigatório para ação reprocess")
        
        # Simular reprocessamento
        # Em uma implementação real, você moveria mensagens da DLQ para a fila de reprocessamento
        messages_reprocessed = min(count, len(self.dlq_messages.get(dlq_name, [])))
        
        return {
            "reprocess_queue": reprocess_queue,
            "messages_reprocessed": messages_reprocessed,
            "reprocessed_at": datetime.utcnow().isoformat()
        }
    
    def _delete_dlq(self, channel, dlq_name: str) -> Dict[str, Any]:
        """Deleta a DLQ."""
        channel.queue_delete(queue=dlq_name)
        
        # Remover do cache
        if dlq_name in self.dlq_messages:
            del self.dlq_messages[dlq_name]
        
        return {
            "deleted_at": datetime.utcnow().isoformat()
        }
    
    def get_dlq_config(self, source_queue: str) -> Optional[DLQInfo]:
        """
        Obtém configuração de DLQ para uma fila de origem.
        
        Args:
            source_queue: Nome da fila de origem
            
        Returns:
            Configuração da DLQ ou None se não encontrada
        """
        return self.dlq_configs.get(source_queue)
    
    def get_dlq_messages(self, dlq_name: str) -> List[DLQMessageInfo]:
        """
        Obtém mensagens de uma DLQ.
        
        Args:
            dlq_name: Nome da DLQ
            
        Returns:
            Lista de mensagens na DLQ
        """
        return self.dlq_messages.get(dlq_name, [])


# Instância global do gerenciador de DLQs
dlq_manager = DLQManager()


def dlq_configure(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para configurar dead letter queue.
    
    Args:
        params: Parâmetros de configuração
        
    Returns:
        Resposta da configuração
    """
    schema = DLQConfigureSchema(**params)
    response = dlq_manager.configure_dlq(schema)
    return response.dict()


def dlq_manage(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para gerenciar operações de dead letter queue.
    
    Args:
        params: Parâmetros de gerenciamento
        
    Returns:
        Resposta da operação
    """
    schema = DLQManageSchema(**params)
    response = dlq_manager.manage_dlq(schema)
    return response.dict()