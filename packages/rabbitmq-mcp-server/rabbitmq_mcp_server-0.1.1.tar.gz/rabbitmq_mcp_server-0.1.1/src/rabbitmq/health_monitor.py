"""
Monitor de saúde RabbitMQ.

Este módulo implementa monitoramento de saúde das conexões
e do servidor RabbitMQ.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from src.shared.models.connection import Connection, ConnectionStatus
from src.shared.utils.logging import get_logger
from src.rabbitmq.connection_manager import connection_manager


class HealthStatus(str, Enum):
    """Status de saúde."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Resultado de verificação de saúde."""
    name: str
    status: HealthStatus
    message: str
    details: Optional[Dict] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class HealthMetrics:
    """Métricas de saúde."""
    connection_count: int
    active_connections: int
    failed_connections: int
    avg_response_time: float
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


class HealthMonitor:
    """Monitor de saúde RabbitMQ."""
    
    def __init__(self):
        """Inicializa o monitor de saúde."""
        self.logger = get_logger(__name__)
        self.health_checks: List[Callable] = []
        self.metrics_history: List[HealthMetrics] = []
        self.max_history_size = 100
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Registra verificações de saúde padrão."""
        self.health_checks.extend([
            self._check_connection_health,
            self._check_server_connectivity,
            self._check_channel_health,
            self._check_memory_usage,
        ])
    
    async def check_connection_health(self, connection_id: str) -> HealthCheck:
        """
        Verifica a saúde de uma conexão específica.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Resultado da verificação de saúde
        """
        try:
            # Verificar se conexão existe
            if connection_id not in connection_manager.connections:
                return HealthCheck(
                    name="connection_exists",
                    status=HealthStatus.CRITICAL,
                    message=f"Conexão {connection_id} não encontrada"
                )
            
            connection = connection_manager.connections[connection_id]
            
            # Verificar status da conexão
            if connection.status != ConnectionStatus.CONNECTED:
                return HealthCheck(
                    name="connection_status",
                    status=HealthStatus.CRITICAL,
                    message=f"Conexão {connection_id} não está conectada",
                    details={"status": connection.status.value}
                )
            
            # Verificar se conexão ainda está ativa
            if connection_id in connection_manager.connection_objects:
                conn_obj = connection_manager.connection_objects[connection_id]
                if conn_obj.is_closed:
                    return HealthCheck(
                        name="connection_active",
                        status=HealthStatus.CRITICAL,
                        message=f"Conexão {connection_id} está fechada"
                    )
            
            # Verificar canal
            channel = await connection_manager.get_channel(connection_id)
            if not channel:
                return HealthCheck(
                    name="channel_health",
                    status=HealthStatus.CRITICAL,
                    message=f"Canal da conexão {connection_id} não está disponível"
                )
            
            if channel.is_closed:
                return HealthCheck(
                    name="channel_health",
                    status=HealthStatus.CRITICAL,
                    message=f"Canal da conexão {connection_id} está fechado"
                )
            
            # Teste de conectividade básico
            try:
                # Tentar declarar uma fila temporária
                temp_queue = f"health_check_{int(time.time())}"
                method = channel.queue_declare(queue=temp_queue, auto_delete=True)
                channel.queue_delete(queue=temp_queue)
                
                return HealthCheck(
                    name="connection_health",
                    status=HealthStatus.HEALTHY,
                    message=f"Conexão {connection_id} está saudável",
                    details={
                        "uptime": time.time() - connection.created_at,
                        "message_count": method.method.message_count,
                        "consumer_count": method.method.consumer_count,
                    }
                )
                
            except Exception as e:
                return HealthCheck(
                    name="connection_health",
                    status=HealthStatus.CRITICAL,
                    message=f"Falha no teste de conectividade: {str(e)}"
                )
                
        except Exception as e:
            return HealthCheck(
                name="connection_health",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar saúde da conexão: {str(e)}"
            )
    
    async def check_server_health(self, connection_id: str) -> HealthCheck:
        """
        Verifica a saúde do servidor RabbitMQ.
        
        Args:
            connection_id: ID da conexão para usar no teste
            
        Returns:
            Resultado da verificação de saúde
        """
        try:
            channel = await connection_manager.get_channel(connection_id)
            if not channel:
                return HealthCheck(
                    name="server_health",
                    status=HealthStatus.CRITICAL,
                    message="Não é possível obter canal para verificação do servidor"
                )
            
            # Medir tempo de resposta
            start_time = time.time()
            
            # Teste básico de conectividade
            method = channel.queue_declare(queue="", exclusive=True)
            queue_name = method.method.queue
            channel.queue_delete(queue=queue_name)
            
            response_time = (time.time() - start_time) * 1000  # em ms
            
            # Determinar status baseado no tempo de resposta
            if response_time < 100:
                status = HealthStatus.HEALTHY
                message = "Servidor RabbitMQ está respondendo rapidamente"
            elif response_time < 500:
                status = HealthStatus.WARNING
                message = "Servidor RabbitMQ está respondendo lentamente"
            else:
                status = HealthStatus.CRITICAL
                message = "Servidor RabbitMQ está respondendo muito lentamente"
            
            return HealthCheck(
                name="server_health",
                status=status,
                message=message,
                details={
                    "response_time_ms": response_time,
                    "queue_name": queue_name,
                }
            )
            
        except AMQPConnectionError as e:
            return HealthCheck(
                name="server_health",
                status=HealthStatus.CRITICAL,
                message=f"Erro de conexão com servidor: {str(e)}"
            )
        except AMQPChannelError as e:
            return HealthCheck(
                name="server_health",
                status=HealthStatus.CRITICAL,
                message=f"Erro de canal: {str(e)}"
            )
        except Exception as e:
            return HealthCheck(
                name="server_health",
                status=HealthStatus.UNKNOWN,
                message=f"Erro inesperado: {str(e)}"
            )
    
    async def check_cluster_health(self, connection_id: str) -> HealthCheck:
        """
        Verifica a saúde do cluster RabbitMQ.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Resultado da verificação de saúde
        """
        try:
            # Esta é uma implementação simplificada
            # Em produção, seria necessário usar a API de gerenciamento HTTP
            
            channel = await connection_manager.get_channel(connection_id)
            if not channel:
                return HealthCheck(
                    name="cluster_health",
                    status=HealthStatus.CRITICAL,
                    message="Não é possível obter canal para verificação do cluster"
                )
            
            # Verificação básica - assumir cluster saudável se conexão funciona
            return HealthCheck(
                name="cluster_health",
                status=HealthStatus.HEALTHY,
                message="Cluster RabbitMQ está funcionando",
                details={
                    "note": "Verificação simplificada - use API de gerenciamento para detalhes completos"
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="cluster_health",
                status=HealthStatus.UNKNOWN,
                message=f"Erro ao verificar cluster: {str(e)}"
            )
    
    async def get_health_metrics(self) -> HealthMetrics:
        """
        Obtém métricas de saúde atuais.
        
        Returns:
            Métricas de saúde
        """
        try:
            connections = await connection_manager.list_connections(include_stats=True)
            
            total_connections = len(connections)
            active_connections = len([c for c in connections.values() if c.status == ConnectionStatus.CONNECTED])
            failed_connections = total_connections - active_connections
            
            # Calcular tempo médio de resposta (simplificado)
            response_times = []
            for connection in connections.values():
                if connection.stats and "uptime" in connection.stats:
                    # Usar uptime como proxy para tempo de resposta
                    response_times.append(connection.stats["uptime"])
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            metrics = HealthMetrics(
                connection_count=total_connections,
                active_connections=active_connections,
                failed_connections=failed_connections,
                avg_response_time=avg_response_time,
            )
            
            # Armazenar no histórico
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            self.logger.error("Erro ao obter métricas de saúde", error=str(e))
            return HealthMetrics(
                connection_count=0,
                active_connections=0,
                failed_connections=0,
                avg_response_time=0,
            )
    
    async def run_health_checks(self, connection_id: Optional[str] = None) -> List[HealthCheck]:
        """
        Executa todas as verificações de saúde.
        
        Args:
            connection_id: ID da conexão específica (opcional)
            
        Returns:
            Lista de resultados das verificações
        """
        results = []
        
        # Verificações específicas de conexão
        if connection_id:
            results.append(await self.check_connection_health(connection_id))
            results.append(await self.check_server_health(connection_id))
            results.append(await self.check_cluster_health(connection_id))
        else:
            # Verificações gerais
            connections = await connection_manager.list_connections()
            if connections:
                # Usar primeira conexão disponível
                first_connection_id = next(iter(connections.keys()))
                results.append(await self.check_server_health(first_connection_id))
                results.append(await self.check_cluster_health(first_connection_id))
            else:
                results.append(HealthCheck(
                    name="no_connections",
                    status=HealthStatus.CRITICAL,
                    message="Nenhuma conexão ativa encontrada"
                ))
        
        # Executar verificações registradas
        for check_func in self.health_checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func(connection_id)
                else:
                    result = check_func(connection_id)
                
                if isinstance(result, HealthCheck):
                    results.append(result)
            except Exception as e:
                results.append(HealthCheck(
                    name=check_func.__name__,
                    status=HealthStatus.UNKNOWN,
                    message=f"Erro na verificação: {str(e)}"
                ))
        
        return results
    
    async def _check_connection_health(self, connection_id: Optional[str] = None) -> HealthCheck:
        """Verificação de saúde das conexões."""
        connections = await connection_manager.list_connections()
        
        if not connections:
            return HealthCheck(
                name="connection_health",
                status=HealthStatus.CRITICAL,
                message="Nenhuma conexão ativa"
            )
        
        healthy_connections = len([c for c in connections.values() if c.status == ConnectionStatus.CONNECTED])
        total_connections = len(connections)
        
        if healthy_connections == total_connections:
            status = HealthStatus.HEALTHY
            message = f"Todas as {total_connections} conexões estão saudáveis"
        elif healthy_connections > 0:
            status = HealthStatus.WARNING
            message = f"{healthy_connections}/{total_connections} conexões estão saudáveis"
        else:
            status = HealthStatus.CRITICAL
            message = "Nenhuma conexão está saudável"
        
        return HealthCheck(
            name="connection_health",
            status=status,
            message=message,
            details={
                "total_connections": total_connections,
                "healthy_connections": healthy_connections,
                "unhealthy_connections": total_connections - healthy_connections,
            }
        )
    
    async def _check_server_connectivity(self, connection_id: Optional[str] = None) -> HealthCheck:
        """Verificação de conectividade do servidor."""
        if connection_id:
            return await self.check_server_health(connection_id)
        else:
            return HealthCheck(
                name="server_connectivity",
                status=HealthStatus.UNKNOWN,
                message="ID da conexão não fornecido para verificação de conectividade"
            )
    
    async def _check_channel_health(self, connection_id: Optional[str] = None) -> HealthCheck:
        """Verificação de saúde dos canais."""
        if not connection_id:
            return HealthCheck(
                name="channel_health",
                status=HealthStatus.UNKNOWN,
                message="ID da conexão não fornecido para verificação de canal"
            )
        
        channel = await connection_manager.get_channel(connection_id)
        if not channel:
            return HealthCheck(
                name="channel_health",
                status=HealthStatus.CRITICAL,
                message=f"Canal não disponível para conexão {connection_id}"
            )
        
        if channel.is_closed:
            return HealthCheck(
                name="channel_health",
                status=HealthStatus.CRITICAL,
                message=f"Canal fechado para conexão {connection_id}"
            )
        
        return HealthCheck(
            name="channel_health",
            status=HealthStatus.HEALTHY,
            message=f"Canal saudável para conexão {connection_id}"
        )
    
    async def _check_memory_usage(self, connection_id: Optional[str] = None) -> HealthCheck:
        """Verificação de uso de memória (simplificada)."""
        # Esta é uma implementação simplificada
        # Em produção, seria necessário usar a API de gerenciamento HTTP
        
        return HealthCheck(
            name="memory_usage",
            status=HealthStatus.HEALTHY,
            message="Verificação de memória não implementada",
            details={
                "note": "Use API de gerenciamento HTTP para métricas detalhadas"
            }
        )


# Instância global do monitor
health_monitor = HealthMonitor()
