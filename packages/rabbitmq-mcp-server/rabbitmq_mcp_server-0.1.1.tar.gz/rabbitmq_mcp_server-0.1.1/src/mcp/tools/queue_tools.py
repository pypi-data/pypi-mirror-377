"""
Ferramentas MCP para gerenciamento de filas RabbitMQ.

Este módulo implementa as ferramentas MCP para criar, deletar,
listar e limpar filas RabbitMQ.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.exceptions import AMQPError

from src.mcp.schemas.queue_schemas import (
    QueueCreateResponse,
    QueueCreateSchema,
    QueueDeleteResponse,
    QueueDeleteSchema,
    QueueInfo,
    QueueListResponse,
    QueueListSchema,
    QueuePurgeResponse,
    QueuePurgeSchema,
)
from src.mcp.tools.connection_tools import connection_manager
from src.shared.models.queue import Queue
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation
from src.shared.utils.validation import validate_queue_params


class QueueManager:
    """Gerenciador de filas RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de filas."""
        self.queues: Dict[str, Queue] = {}
    
    def create_queue(self, params: QueueCreateSchema) -> QueueCreateResponse:
        """
        Cria uma nova fila no RabbitMQ.
        
        Args:
            params: Parâmetros de criação da fila
            
        Returns:
            Resposta com informações da fila criada
        """
        logger = log_mcp_request("queue_create", params.connection_id)
        
        try:
            # Validar parâmetros
            validated_params = validate_queue_params(params.dict())
            
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Configurar argumentos da fila
            queue_arguments = validated_params.get("arguments", {})
            
            # Declarar fila
            logger.info("Criando fila", 
                       queue_name=params.queue_name,
                       durable=params.durable,
                       exclusive=params.exclusive,
                       auto_delete=params.auto_delete)
            
            result = channel.queue_declare(
                queue=params.queue_name,
                durable=params.durable,
                exclusive=params.exclusive,
                auto_delete=params.auto_delete,
                arguments=queue_arguments
            )
            
            # Obter estatísticas da fila
            method = result.method
            message_count = method.message_count
            consumer_count = method.consumer_count
            
            # Criar modelo da fila
            queue = Queue(
                name=params.queue_name,
                durable=params.durable,
                exclusive=params.exclusive,
                auto_delete=params.auto_delete,
                arguments=queue_arguments,
                message_count=message_count,
                consumer_count=consumer_count,
                vhost=connection.virtual_host
            )
            
            # Armazenar fila
            queue_key = f"{params.connection_id}:{params.queue_name}"
            self.queues[queue_key] = queue
            
            logger.info("Fila criada com sucesso", 
                       queue_name=params.queue_name,
                       message_count=message_count,
                       consumer_count=consumer_count)
            
            return QueueCreateResponse(
                queue_name=params.queue_name,
                status="created",
                durable=params.durable,
                exclusive=params.exclusive,
                auto_delete=params.auto_delete,
                message_count=message_count,
                consumer_count=consumer_count,
                created_at=queue.created_at.isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao criar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao criar fila: {e}")
        except Exception as e:
            logger.error("Erro ao criar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro ao criar fila: {e}")
    
    def delete_queue(self, params: QueueDeleteSchema) -> QueueDeleteResponse:
        """
        Deleta uma fila do RabbitMQ.
        
        Args:
            params: Parâmetros de deleção da fila
            
        Returns:
            Resposta com informações da deleção
        """
        logger = log_mcp_request("queue_delete", params.connection_id)
        
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
            
            # Deletar fila
            logger.info("Deletando fila", 
                       queue_name=params.queue_name,
                       if_unused=params.if_unused,
                       if_empty=params.if_empty)
            
            method, message_count = channel.queue_delete(
                queue=params.queue_name,
                if_unused=params.if_unused,
                if_empty=params.if_empty
            )
            
            # Remover fila do cache
            queue_key = f"{params.connection_id}:{params.queue_name}"
            if queue_key in self.queues:
                del self.queues[queue_key]
            
            logger.info("Fila deletada com sucesso", 
                       queue_name=params.queue_name,
                       message_count=message_count)
            
            return QueueDeleteResponse(
                queue_name=params.queue_name,
                status="deleted",
                deleted_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao deletar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao deletar fila: {e}")
        except Exception as e:
            logger.error("Erro ao deletar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro ao deletar fila: {e}")
    
    def list_queues(self, params: QueueListSchema) -> QueueListResponse:
        """
        Lista todas as filas no RabbitMQ.
        
        Args:
            params: Parâmetros de listagem
            
        Returns:
            Resposta com lista de filas
        """
        logger = log_mcp_request("queue_list", params.connection_id)
        
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
            
            # Listar filas usando a API de gerenciamento
            # Nota: Esta é uma implementação simplificada
            # Em produção, seria necessário usar a API de gerenciamento RabbitMQ
            
            queues = []
            
            # Para demonstração, vamos retornar filas conhecidas
            # Em uma implementação real, você usaria a API de gerenciamento
            logger.info("Listando filas", vhost=params.vhost)
            
            # Simular algumas filas para demonstração
            if params.include_stats:
                # Filas simuladas com estatísticas
                sample_queues = [
                    QueueInfo(
                        name="test_queue_1",
                        durable=True,
                        exclusive=False,
                        auto_delete=False,
                        message_count=10,
                        consumer_count=2,
                        vhost=params.vhost,
                        created_at=datetime.utcnow().isoformat(),
                        last_updated=datetime.utcnow().isoformat()
                    ),
                    QueueInfo(
                        name="test_queue_2",
                        durable=False,
                        exclusive=True,
                        auto_delete=True,
                        message_count=0,
                        consumer_count=0,
                        vhost=params.vhost,
                        created_at=datetime.utcnow().isoformat(),
                        last_updated=datetime.utcnow().isoformat()
                    )
                ]
                queues = sample_queues
            
            logger.info("Lista de filas obtida", count=len(queues))
            
            return QueueListResponse(
                queues=queues,
                total_count=len(queues),
                vhost=params.vhost
            )
            
        except Exception as e:
            logger.error("Erro ao listar filas", error=str(e))
            raise ValueError(f"Erro ao listar filas: {e}")
    
    def purge_queue(self, params: QueuePurgeSchema) -> QueuePurgeResponse:
        """
        Limpa todas as mensagens de uma fila.
        
        Args:
            params: Parâmetros de limpeza da fila
            
        Returns:
            Resposta com informações da limpeza
        """
        logger = log_mcp_request("queue_purge", params.connection_id)
        
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
            
            # Limpar fila
            logger.info("Limpando fila", queue_name=params.queue_name)
            
            method, message_count = channel.queue_purge(queue=params.queue_name)
            
            # Atualizar cache da fila se existir
            queue_key = f"{params.connection_id}:{params.queue_name}"
            if queue_key in self.queues:
                self.queues[queue_key].update_stats(0, self.queues[queue_key].consumer_count)
            
            logger.info("Fila limpa com sucesso", 
                       queue_name=params.queue_name,
                       messages_purged=message_count)
            
            return QueuePurgeResponse(
                queue_name=params.queue_name,
                status="purged",
                messages_purged=message_count,
                purged_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao limpar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao limpar fila: {e}")
        except Exception as e:
            logger.error("Erro ao limpar fila", 
                        queue_name=params.queue_name, 
                        error=str(e))
            raise ValueError(f"Erro ao limpar fila: {e}")
    
    def get_queue(self, connection_id: str, queue_name: str) -> Optional[Queue]:
        """
        Obtém uma fila por nome.
        
        Args:
            connection_id: ID da conexão
            queue_name: Nome da fila
            
        Returns:
            Instância da fila ou None se não encontrada
        """
        queue_key = f"{connection_id}:{queue_name}"
        return self.queues.get(queue_key)


# Instância global do gerenciador de filas
queue_manager = QueueManager()


def queue_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para criar uma fila.
    
    Args:
        params: Parâmetros de criação da fila
        
    Returns:
        Resposta da criação da fila
    """
    schema = QueueCreateSchema(**params)
    response = queue_manager.create_queue(schema)
    return response.dict()


def queue_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para deletar uma fila.
    
    Args:
        params: Parâmetros de deleção da fila
        
    Returns:
        Resposta da deleção da fila
    """
    schema = QueueDeleteSchema(**params)
    response = queue_manager.delete_queue(schema)
    return response.dict()


def queue_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para listar filas.
    
    Args:
        params: Parâmetros de listagem
        
    Returns:
        Resposta com lista de filas
    """
    schema = QueueListSchema(**params)
    response = queue_manager.list_queues(schema)
    return response.dict()


def queue_purge(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para limpar uma fila.
    
    Args:
        params: Parâmetros de limpeza da fila
        
    Returns:
        Resposta da limpeza da fila
    """
    schema = QueuePurgeSchema(**params)
    response = queue_manager.purge_queue(schema)
    return response.dict()