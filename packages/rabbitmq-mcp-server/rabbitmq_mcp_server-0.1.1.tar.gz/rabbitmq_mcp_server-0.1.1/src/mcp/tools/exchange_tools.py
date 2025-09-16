"""
Ferramentas MCP para gerenciamento de exchanges RabbitMQ.

Este módulo implementa as ferramentas MCP para criar, deletar,
vincular e desvincular exchanges RabbitMQ.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.exceptions import AMQPError

from src.mcp.schemas.exchange_schemas import (
    BindingInfo,
    ExchangeBindResponse,
    ExchangeBindSchema,
    ExchangeCreateResponse,
    ExchangeCreateSchema,
    ExchangeDeleteResponse,
    ExchangeDeleteSchema,
    ExchangeInfo,
    ExchangeUnbindResponse,
    ExchangeUnbindSchema,
)
from src.mcp.tools.connection_tools import connection_manager
from src.shared.models.exchange import Exchange, ExchangeType
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation
from src.shared.utils.validation import validate_exchange_params


class ExchangeManager:
    """Gerenciador de exchanges RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de exchanges."""
        self.exchanges: Dict[str, Exchange] = {}
        self.bindings: Dict[str, List[BindingInfo]] = {}  # exchange_name -> list of bindings
    
    def create_exchange(self, params: ExchangeCreateSchema) -> ExchangeCreateResponse:
        """
        Cria um novo exchange no RabbitMQ.
        
        Args:
            params: Parâmetros de criação do exchange
            
        Returns:
            Resposta com informações do exchange criado
        """
        logger = log_mcp_request("exchange_create", params.connection_id)
        
        try:
            # Validar parâmetros
            validated_params = validate_exchange_params(params.dict())
            
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            # Criar canal
            channel = pika_connection.channel()
            
            # Declarar exchange
            logger.info("Criando exchange", 
                       exchange_name=params.exchange_name,
                       exchange_type=params.exchange_type,
                       durable=params.durable,
                       auto_delete=params.auto_delete,
                       internal=params.internal)
            
            channel.exchange_declare(
                exchange=params.exchange_name,
                exchange_type=params.exchange_type,
                durable=params.durable,
                auto_delete=params.auto_delete,
                internal=params.internal,
                arguments=params.arguments
            )
            
            # Criar modelo do exchange
            exchange = Exchange(
                name=params.exchange_name,
                type=ExchangeType(params.exchange_type),
                durable=params.durable,
                auto_delete=params.auto_delete,
                internal=params.internal,
                arguments=params.arguments,
                vhost=connection.virtual_host
            )
            
            # Armazenar exchange
            exchange_key = f"{params.connection_id}:{params.exchange_name}"
            self.exchanges[exchange_key] = exchange
            
            # Inicializar lista de bindings
            self.bindings[params.exchange_name] = []
            
            logger.info("Exchange criado com sucesso", 
                       exchange_name=params.exchange_name,
                       exchange_type=params.exchange_type)
            
            return ExchangeCreateResponse(
                exchange_name=params.exchange_name,
                exchange_type=params.exchange_type,
                status="created",
                durable=params.durable,
                auto_delete=params.auto_delete,
                internal=params.internal,
                created_at=exchange.created_at.isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao criar exchange", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao criar exchange: {e}")
        except Exception as e:
            logger.error("Erro ao criar exchange", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro ao criar exchange: {e}")
    
    def delete_exchange(self, params: ExchangeDeleteSchema) -> ExchangeDeleteResponse:
        """
        Deleta um exchange do RabbitMQ.
        
        Args:
            params: Parâmetros de deleção do exchange
            
        Returns:
            Resposta com informações da deleção
        """
        logger = log_mcp_request("exchange_delete", params.connection_id)
        
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
            
            # Deletar exchange
            logger.info("Deletando exchange", 
                       exchange_name=params.exchange_name,
                       if_unused=params.if_unused)
            
            channel.exchange_delete(
                exchange=params.exchange_name,
                if_unused=params.if_unused
            )
            
            # Remover exchange do cache
            exchange_key = f"{params.connection_id}:{params.exchange_name}"
            if exchange_key in self.exchanges:
                del self.exchanges[exchange_key]
            
            # Remover bindings do cache
            if params.exchange_name in self.bindings:
                del self.bindings[params.exchange_name]
            
            logger.info("Exchange deletado com sucesso", 
                       exchange_name=params.exchange_name)
            
            return ExchangeDeleteResponse(
                exchange_name=params.exchange_name,
                status="deleted",
                deleted_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao deletar exchange", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao deletar exchange: {e}")
        except Exception as e:
            logger.error("Erro ao deletar exchange", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro ao deletar exchange: {e}")
    
    def bind_queue(self, params: ExchangeBindSchema) -> ExchangeBindResponse:
        """
        Vincula uma fila a um exchange.
        
        Args:
            params: Parâmetros de binding
            
        Returns:
            Resposta com informações do binding
        """
        logger = log_mcp_request("exchange_bind", params.connection_id)
        
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
            
            # Criar binding
            logger.info("Criando binding", 
                       exchange_name=params.exchange_name,
                       queue_name=params.queue_name,
                       routing_key=params.routing_key)
            
            channel.queue_bind(
                exchange=params.exchange_name,
                queue=params.queue_name,
                routing_key=params.routing_key,
                arguments=params.arguments
            )
            
            # Criar informação do binding
            binding = BindingInfo(
                exchange_name=params.exchange_name,
                queue_name=params.queue_name,
                routing_key=params.routing_key,
                arguments=params.arguments,
                created_at=datetime.utcnow().isoformat()
            )
            
            # Armazenar binding
            if params.exchange_name not in self.bindings:
                self.bindings[params.exchange_name] = []
            self.bindings[params.exchange_name].append(binding)
            
            logger.info("Binding criado com sucesso", 
                       exchange_name=params.exchange_name,
                       queue_name=params.queue_name)
            
            return ExchangeBindResponse(
                binding_created=True,
                exchange_name=params.exchange_name,
                queue_name=params.queue_name,
                routing_key=params.routing_key,
                bound_at=binding.created_at
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao criar binding", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao criar binding: {e}")
        except Exception as e:
            logger.error("Erro ao criar binding", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro ao criar binding: {e}")
    
    def unbind_queue(self, params: ExchangeUnbindSchema) -> ExchangeUnbindResponse:
        """
        Desvincula uma fila de um exchange.
        
        Args:
            params: Parâmetros de unbinding
            
        Returns:
            Resposta com informações do unbinding
        """
        logger = log_mcp_request("exchange_unbind", params.connection_id)
        
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
            
            # Remover binding
            logger.info("Removendo binding", 
                       exchange_name=params.exchange_name,
                       queue_name=params.queue_name,
                       routing_key=params.routing_key)
            
            channel.queue_unbind(
                exchange=params.exchange_name,
                queue=params.queue_name,
                routing_key=params.routing_key,
                arguments=params.arguments
            )
            
            # Remover binding do cache
            if params.exchange_name in self.bindings:
                self.bindings[params.exchange_name] = [
                    binding for binding in self.bindings[params.exchange_name]
                    if not (binding.queue_name == params.queue_name and 
                           binding.routing_key == params.routing_key)
                ]
            
            logger.info("Binding removido com sucesso", 
                       exchange_name=params.exchange_name,
                       queue_name=params.queue_name)
            
            return ExchangeUnbindResponse(
                binding_removed=True,
                exchange_name=params.exchange_name,
                queue_name=params.queue_name,
                routing_key=params.routing_key,
                unbound_at=datetime.utcnow().isoformat()
            )
            
        except AMQPError as e:
            logger.error("Erro AMQP ao remover binding", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro AMQP ao remover binding: {e}")
        except Exception as e:
            logger.error("Erro ao remover binding", 
                        exchange_name=params.exchange_name, 
                        error=str(e))
            raise ValueError(f"Erro ao remover binding: {e}")
    
    def get_exchange(self, connection_id: str, exchange_name: str) -> Optional[Exchange]:
        """
        Obtém um exchange por nome.
        
        Args:
            connection_id: ID da conexão
            exchange_name: Nome do exchange
            
        Returns:
            Instância do exchange ou None se não encontrado
        """
        exchange_key = f"{connection_id}:{exchange_name}"
        return self.exchanges.get(exchange_key)
    
    def get_bindings(self, exchange_name: str) -> List[BindingInfo]:
        """
        Obtém os bindings de um exchange.
        
        Args:
            exchange_name: Nome do exchange
            
        Returns:
            Lista de bindings
        """
        return self.bindings.get(exchange_name, [])


# Instância global do gerenciador de exchanges
exchange_manager = ExchangeManager()


def exchange_create(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para criar um exchange.
    
    Args:
        params: Parâmetros de criação do exchange
        
    Returns:
        Resposta da criação do exchange
    """
    schema = ExchangeCreateSchema(**params)
    response = exchange_manager.create_exchange(schema)
    return response.dict()


def exchange_delete(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para deletar um exchange.
    
    Args:
        params: Parâmetros de deleção do exchange
        
    Returns:
        Resposta da deleção do exchange
    """
    schema = ExchangeDeleteSchema(**params)
    response = exchange_manager.delete_exchange(schema)
    return response.dict()


def exchange_bind(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para vincular uma fila a um exchange.
    
    Args:
        params: Parâmetros de binding
        
    Returns:
        Resposta do binding
    """
    schema = ExchangeBindSchema(**params)
    response = exchange_manager.bind_queue(schema)
    return response.dict()


def exchange_unbind(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para desvincular uma fila de um exchange.
    
    Args:
        params: Parâmetros de unbinding
        
    Returns:
        Resposta do unbinding
    """
    schema = ExchangeUnbindSchema(**params)
    response = exchange_manager.unbind_queue(schema)
    return response.dict()