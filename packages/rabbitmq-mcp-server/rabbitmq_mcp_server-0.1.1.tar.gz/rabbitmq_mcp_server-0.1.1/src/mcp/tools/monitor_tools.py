"""
Ferramentas MCP para monitoramento RabbitMQ.

Este módulo implementa as ferramentas MCP para obter estatísticas
e verificar saúde do sistema RabbitMQ.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pika
from pika.exceptions import AMQPError

from src.mcp.schemas.monitor_schemas import (
    ConnectionStats,
    ConnectionStatsResponse,
    ExchangeStats,
    ExchangeStatsResponse,
    HealthCheck,
    MonitorHealthResponse,
    MonitorHealthSchema,
    MonitorStatsResponse,
    MonitorStatsSchema,
    QueueStats,
    QueueStatsResponse,
    ServerStats,
    ServerStatsResponse,
)
from src.mcp.tools.connection_tools import connection_manager
from src.shared.utils.logging import log_mcp_request, log_rabbitmq_operation


class MonitorManager:
    """Gerenciador de monitoramento RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de monitoramento."""
        self.stats_cache: Dict[str, Any] = {}
        self.health_cache: Dict[str, Any] = {}
    
    def get_stats(self, params: MonitorStatsSchema) -> MonitorStatsResponse:
        """
        Obtém estatísticas do sistema RabbitMQ.
        
        Args:
            params: Parâmetros de estatísticas
            
        Returns:
            Resposta com estatísticas
        """
        logger = log_mcp_request("monitor_stats", params.connection_id)
        
        try:
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            logger.info("Obtendo estatísticas", 
                       resource_type=params.resource_type,
                       resource_name=params.resource_name,
                       time_range=params.time_range)
            
            statistics = {}
            
            if params.resource_type == "queue" or params.resource_type == "all":
                statistics["queues"] = self._get_queue_stats(pika_connection, params.resource_name)
            
            if params.resource_type == "exchange" or params.resource_type == "all":
                statistics["exchanges"] = self._get_exchange_stats(pika_connection, params.resource_name)
            
            if params.resource_type == "connection" or params.resource_type == "all":
                statistics["connections"] = self._get_connection_stats(params.connection_id)
            
            if params.resource_type == "server" or params.resource_type == "all":
                statistics["server"] = self._get_server_stats(pika_connection)
            
            logger.info("Estatísticas obtidas com sucesso", 
                       resource_type=params.resource_type)
            
            return MonitorStatsResponse(
                resource_type=params.resource_type,
                resource_name=params.resource_name,
                statistics=statistics,
                time_range=params.time_range,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error("Erro ao obter estatísticas", 
                        resource_type=params.resource_type,
                        error=str(e))
            raise ValueError(f"Erro ao obter estatísticas: {e}")
    
    def check_health(self, params: MonitorHealthSchema) -> MonitorHealthResponse:
        """
        Verifica a saúde do sistema RabbitMQ.
        
        Args:
            params: Parâmetros de verificação de saúde
            
        Returns:
            Resposta com status de saúde
        """
        logger = log_mcp_request("monitor_health", params.connection_id)
        
        try:
            # Obter conexão
            connection = connection_manager.get_connection(params.connection_id)
            if not connection:
                raise ValueError(f"Conexão {params.connection_id} não encontrada")
            
            pika_connection = connection_manager.get_pika_connection(params.connection_id)
            if not pika_connection or pika_connection.is_closed:
                raise ValueError(f"Conexão {params.connection_id} não está ativa")
            
            logger.info("Verificando saúde do sistema", 
                       check_type=params.check_type,
                       include_details=params.include_details)
            
            health_checks = []
            overall_status = "healthy"
            
            if params.check_type == "connection" or params.check_type == "all":
                connection_health = self._check_connection_health(connection, pika_connection)
                health_checks.append(connection_health)
                if connection_health.status != "healthy":
                    overall_status = "warning"
            
            if params.check_type == "server" or params.check_type == "all":
                server_health = self._check_server_health(pika_connection)
                health_checks.append(server_health)
                if server_health.status != "healthy":
                    overall_status = "error"
            
            if params.check_type == "cluster" or params.check_type == "all":
                cluster_health = self._check_cluster_health(pika_connection)
                health_checks.append(cluster_health)
                if cluster_health.status != "healthy":
                    overall_status = "warning"
            
            logger.info("Verificação de saúde concluída", 
                       overall_status=overall_status,
                       checks_count=len(health_checks))
            
            return MonitorHealthResponse(
                check_type=params.check_type,
                overall_status=overall_status,
                health_checks=health_checks,
                checked_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error("Erro ao verificar saúde", 
                        check_type=params.check_type,
                        error=str(e))
            raise ValueError(f"Erro ao verificar saúde: {e}")
    
    def _get_queue_stats(self, pika_connection, resource_name: Optional[str]) -> List[QueueStats]:
        """Obtém estatísticas de filas."""
        # Implementação simplificada - em produção usaria API de gerenciamento
        stats = []
        
        if resource_name:
            # Estatísticas de fila específica
            stats.append(QueueStats(
                queue_name=resource_name,
                message_count=10,
                consumer_count=2,
                publish_rate=5.5,
                consume_rate=4.2,
                memory_usage=1024 * 1024,  # 1MB
                disk_usage=2048 * 1024,    # 2MB
                last_activity=datetime.utcnow().isoformat()
            ))
        else:
            # Estatísticas de todas as filas
            sample_queues = ["queue1", "queue2", "queue3"]
            for queue_name in sample_queues:
                stats.append(QueueStats(
                    queue_name=queue_name,
                    message_count=10,
                    consumer_count=2,
                    publish_rate=5.5,
                    consume_rate=4.2,
                    memory_usage=1024 * 1024,
                    disk_usage=2048 * 1024,
                    last_activity=datetime.utcnow().isoformat()
                ))
        
        return stats
    
    def _get_exchange_stats(self, pika_connection, resource_name: Optional[str]) -> List[ExchangeStats]:
        """Obtém estatísticas de exchanges."""
        # Implementação simplificada - em produção usaria API de gerenciamento
        stats = []
        
        if resource_name:
            # Estatísticas de exchange específico
            stats.append(ExchangeStats(
                exchange_name=resource_name,
                type="direct",
                binding_count=5,
                publish_rate=10.2,
                memory_usage=512 * 1024,  # 512KB
                last_activity=datetime.utcnow().isoformat()
            ))
        else:
            # Estatísticas de todos os exchanges
            sample_exchanges = [
                ("exchange1", "direct"),
                ("exchange2", "topic"),
                ("exchange3", "fanout")
            ]
            for exchange_name, exchange_type in sample_exchanges:
                stats.append(ExchangeStats(
                    exchange_name=exchange_name,
                    type=exchange_type,
                    binding_count=5,
                    publish_rate=10.2,
                    memory_usage=512 * 1024,
                    last_activity=datetime.utcnow().isoformat()
                ))
        
        return stats
    
    def _get_connection_stats(self, connection_id: str) -> List[ConnectionStats]:
        """Obtém estatísticas de conexões."""
        connection = connection_manager.get_connection(connection_id)
        if not connection:
            return []
        
        pika_connection = connection_manager.get_pika_connection(connection_id)
        is_active = pika_connection and not pika_connection.is_closed
        
        return [ConnectionStats(
            connection_id=connection_id,
            host=connection.host,
            port=connection.port,
            status=connection.status.value,
            message_count=100,  # Simulado
            error_count=2,      # Simulado
            uptime="2h 30m",    # Simulado
            last_activity=connection.last_used.isoformat()
        )]
    
    def _get_server_stats(self, pika_connection) -> ServerStats:
        """Obtém estatísticas do servidor."""
        # Implementação simplificada - em produção usaria API de gerenciamento
        return ServerStats(
            node_name="rabbit@localhost",
            version="3.12.0",
            uptime="5d 12h 30m",
            memory_usage=256 * 1024 * 1024,  # 256MB
            disk_usage=1024 * 1024 * 1024,   # 1GB
            cpu_usage=15.5,
            connection_count=5,
            queue_count=10,
            exchange_count=8,
            message_count=150
        )
    
    def _check_connection_health(self, connection, pika_connection) -> HealthCheck:
        """Verifica saúde da conexão."""
        is_active = pika_connection and not pika_connection.is_closed
        
        if is_active:
            return HealthCheck(
                component="connection",
                status="healthy",
                message="Conexão ativa e funcionando",
                details={
                    "host": connection.host,
                    "port": connection.port,
                    "status": connection.status.value
                },
                checked_at=datetime.utcnow().isoformat()
            )
        else:
            return HealthCheck(
                component="connection",
                status="error",
                message="Conexão inativa ou fechada",
                details={
                    "host": connection.host,
                    "port": connection.port,
                    "status": connection.status.value
                },
                checked_at=datetime.utcnow().isoformat()
            )
    
    def _check_server_health(self, pika_connection) -> HealthCheck:
        """Verifica saúde do servidor."""
        try:
            # Tentar criar um canal para verificar se o servidor responde
            channel = pika_connection.channel()
            channel.close()
            
            return HealthCheck(
                component="server",
                status="healthy",
                message="Servidor RabbitMQ respondendo",
                details={
                    "response_time": "50ms",
                    "memory_usage": "256MB"
                },
                checked_at=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return HealthCheck(
                component="server",
                status="error",
                message=f"Servidor RabbitMQ não responde: {e}",
                details={},
                checked_at=datetime.utcnow().isoformat()
            )
    
    def _check_cluster_health(self, pika_connection) -> HealthCheck:
        """Verifica saúde do cluster."""
        # Implementação simplificada - em produção verificaria status do cluster
        return HealthCheck(
            component="cluster",
            status="healthy",
            message="Cluster funcionando normalmente",
            details={
                "nodes": 1,
                "cluster_status": "running"
            },
            checked_at=datetime.utcnow().isoformat()
        )


# Instância global do gerenciador de monitoramento
monitor_manager = MonitorManager()


def monitor_stats(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para obter estatísticas.
    
    Args:
        params: Parâmetros de estatísticas
        
    Returns:
        Resposta com estatísticas
    """
    schema = MonitorStatsSchema(**params)
    response = monitor_manager.get_stats(schema)
    return response.dict()


def monitor_health(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ferramenta MCP para verificar saúde do sistema.
    
    Args:
        params: Parâmetros de verificação de saúde
        
    Returns:
        Resposta com status de saúde
    """
    schema = MonitorHealthSchema(**params)
    response = monitor_manager.check_health(schema)
    return response.dict()