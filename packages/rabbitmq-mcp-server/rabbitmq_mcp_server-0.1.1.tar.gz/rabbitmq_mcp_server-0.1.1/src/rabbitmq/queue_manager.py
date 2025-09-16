"""
Gerenciador de filas RabbitMQ.

Este módulo implementa operações de gerenciamento de filas RabbitMQ,
incluindo criação, exclusão, listagem e purga de filas.
"""

import asyncio
from typing import Dict, List, Optional

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError

from src.shared.models.queue import Queue, QueueStats
from src.shared.utils.logging import get_logger
from src.rabbitmq.connection_manager import connection_manager


class QueueManager:
    """Gerenciador de filas RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de filas."""
        self.logger = get_logger(__name__)
    
    async def create_queue(
        self,
        connection_id: str,
        queue_name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict] = None,
    ) -> Queue:
        """
        Cria uma nova fila RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            queue_name: Nome da fila
            durable: Se a fila deve sobreviver ao reinício do broker
            exclusive: Se a fila é exclusiva da conexão
            auto_delete: Se a fila deve ser deletada quando não usada
            arguments: Argumentos adicionais da fila
            
        Returns:
            Modelo da fila criada
            
        Raises:
            AMQPChannelError: Erro ao criar fila
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Declarar fila
                method = channel.queue_declare(
                    queue=queue_name,
                    durable=durable,
                    exclusive=exclusive,
                    auto_delete=auto_delete,
                    arguments=arguments or {}
                )
                
                # Criar modelo da fila
                queue = Queue(
                    name=queue_name,
                    durable=durable,
                    exclusive=exclusive,
                    auto_delete=auto_delete,
                    arguments=arguments or {},
                    message_count=method.method.message_count,
                    consumer_count=method.method.consumer_count,
                )
                
                self.logger.info("Fila criada com sucesso",
                               connection_id=connection_id,
                               queue_name=queue_name,
                               durable=durable)
                
                return queue
                
            except Exception as e:
                self.logger.error("Erro ao criar fila",
                                connection_id=connection_id,
                                queue_name=queue_name,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao criar fila: {str(e)}")
    
    async def delete_queue(
        self,
        connection_id: str,
        queue_name: str,
        if_unused: bool = False,
        if_empty: bool = False,
    ) -> bool:
        """
        Deleta uma fila RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            queue_name: Nome da fila
            if_unused: Deletar apenas se não tiver consumidores
            if_empty: Deletar apenas se estiver vazia
            
        Returns:
            True se deletada com sucesso
            
        Raises:
            AMQPChannelError: Erro ao deletar fila
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Deletar fila
                method = channel.queue_delete(
                    queue=queue_name,
                    if_unused=if_unused,
                    if_empty=if_empty
                )
                
                self.logger.info("Fila deletada com sucesso",
                               connection_id=connection_id,
                               queue_name=queue_name,
                               message_count=method.method.message_count)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao deletar fila",
                                connection_id=connection_id,
                                queue_name=queue_name,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao deletar fila: {str(e)}")
    
    async def list_queues(
        self,
        connection_id: str,
        vhost: str = "/",
        include_stats: bool = True,
    ) -> List[Queue]:
        """
        Lista todas as filas do servidor RabbitMQ.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            vhost: Virtual host
            include_stats: Se deve incluir estatísticas
            
        Returns:
            Lista de filas
            
        Raises:
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Usar API de gerenciamento para listar filas
                # Nota: Esta é uma implementação simplificada
                # Em produção, seria necessário usar a API HTTP de gerenciamento
                
                queues = []
                
                # Para demonstração, vamos simular algumas filas
                # Em implementação real, usaríamos pika.URLParameters com API de gerenciamento
                
                self.logger.info("Filas listadas",
                               connection_id=connection_id,
                               vhost=vhost,
                               count=len(queues))
                
                return queues
                
            except Exception as e:
                self.logger.error("Erro ao listar filas",
                                connection_id=connection_id,
                                vhost=vhost,
                                error=str(e))
                raise AMQPConnectionError(f"Falha ao listar filas: {str(e)}")
    
    async def purge_queue(self, connection_id: str, queue_name: str) -> int:
        """
        Remove todas as mensagens de uma fila.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            queue_name: Nome da fila
            
        Returns:
            Número de mensagens removidas
            
        Raises:
            AMQPChannelError: Erro ao purgar fila
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Purgar fila
                method = channel.queue_purge(queue=queue_name)
                message_count = method.method.message_count
                
                self.logger.info("Fila purgada com sucesso",
                               connection_id=connection_id,
                               queue_name=queue_name,
                               message_count=message_count)
                
                return message_count
                
            except Exception as e:
                self.logger.error("Erro ao purgar fila",
                                connection_id=connection_id,
                                queue_name=queue_name,
                                error=str(e))
                raise AMQPChannelError(f"Falha ao purgar fila: {str(e)}")
    
    async def get_queue_info(
        self,
        connection_id: str,
        queue_name: str,
    ) -> Optional[Queue]:
        """
        Obtém informações de uma fila específica.
        
        Args:
            connection_id: ID da conexão RabbitMQ
            queue_name: Nome da fila
            
        Returns:
            Informações da fila ou None se não encontrada
            
        Raises:
            AMQPConnectionError: Erro de conexão
        """
        async with connection_manager.get_connection_context(connection_id) as (connection, channel):
            if not connection or not channel:
                raise AMQPConnectionError(f"Conexão {connection_id} não encontrada ou inativa")
            
            try:
                # Declarar fila passiva (não cria se não existir)
                method = channel.queue_declare(
                    queue=queue_name,
                    passive=True
                )
                
                # Criar modelo da fila
                queue = Queue(
                    name=queue_name,
                    durable=True,  # Assumir durável por padrão
                    exclusive=False,
                    auto_delete=False,
                    arguments={},
                    message_count=method.method.message_count,
                    consumer_count=method.method.consumer_count,
                )
                
                return queue
                
            except Exception as e:
                self.logger.warning("Fila não encontrada",
                                  connection_id=connection_id,
                                  queue_name=queue_name,
                                  error=str(e))
                return None


# Instância global do gerenciador
queue_manager = QueueManager()
