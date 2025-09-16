"""
Pool de conexões RabbitMQ.

Este módulo implementa um pool de conexões para otimizar
o gerenciamento de múltiplas conexões RabbitMQ.
"""

import asyncio
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from contextlib import asynccontextmanager

import pika
from pika.adapters.asyncio_connection import AsyncioConnection

from src.shared.models.connection import Connection, ConnectionStatus
from src.shared.utils.logging import get_logger


@dataclass
class PoolConfig:
    """Configuração do pool de conexões."""
    max_connections: int = 10
    min_connections: int = 1
    connection_timeout: int = 30
    idle_timeout: int = 300  # 5 minutos
    heartbeat_interval: int = 600
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class PooledConnection:
    """Conexão do pool com metadados."""
    connection: AsyncioConnection
    channel: pika.channel.Channel
    created_at: float
    last_used_at: float
    use_count: int
    is_available: bool = True


class ConnectionPool:
    """Pool de conexões RabbitMQ."""
    
    def __init__(self, config: Optional[PoolConfig] = None):
        """
        Inicializa o pool de conexões.
        
        Args:
            config: Configuração do pool
        """
        self.config = config or PoolConfig()
        self.connections: Dict[str, PooledConnection] = {}
        self.available_connections: Set[str] = set()
        self.busy_connections: Set[str] = set()
        self.logger = get_logger(__name__)
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Inicia a tarefa de limpeza de conexões ociosas."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_idle_connections())
    
    async def _cleanup_idle_connections(self):
        """Limpa conexões ociosas periodicamente."""
        while True:
            try:
                await asyncio.sleep(60)  # Verificar a cada minuto
                await self._cleanup_idle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Erro na limpeza de conexões ociosas", error=str(e))
    
    async def _cleanup_idle(self):
        """Remove conexões ociosas que excedem o timeout."""
        async with self._lock:
            current_time = time.time()
            idle_connections = []
            
            for conn_id, pooled_conn in self.connections.items():
                if (pooled_conn.is_available and 
                    current_time - pooled_conn.last_used_at > self.config.idle_timeout):
                    idle_connections.append(conn_id)
            
            # Manter pelo menos min_connections
            if len(self.connections) - len(idle_connections) < self.config.min_connections:
                idle_connections = idle_connections[:len(self.connections) - self.config.min_connections]
            
            for conn_id in idle_connections:
                await self._remove_connection(conn_id)
                self.logger.info("Conexão ociosa removida do pool", connection_id=conn_id)
    
    async def create_connection(
        self,
        host: str,
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        ssl_enabled: bool = False,
    ) -> str:
        """
        Cria uma nova conexão no pool.
        
        Args:
            host: Hostname ou IP do servidor RabbitMQ
            port: Porta do servidor RabbitMQ
            username: Nome de usuário
            password: Senha
            virtual_host: Virtual host
            ssl_enabled: Se SSL está habilitado
            
        Returns:
            ID da conexão criada
            
        Raises:
            Exception: Erro ao criar conexão
        """
        async with self._lock:
            # Verificar limite máximo
            if len(self.connections) >= self.config.max_connections:
                raise Exception(f"Pool atingiu limite máximo de {self.config.max_connections} conexões")
            
            connection_id = f"{host}:{port}:{username}:{virtual_host}:{len(self.connections)}"
            
            try:
                # Configurar parâmetros de conexão
                credentials = pika.PlainCredentials(username, password)
                
                connection_params = pika.ConnectionParameters(
                    host=host,
                    port=port,
                    virtual_host=virtual_host,
                    credentials=credentials,
                    connection_attempts=self.config.retry_attempts,
                    retry_delay=self.config.retry_delay,
                    socket_timeout=self.config.connection_timeout,
                    heartbeat=self.config.heartbeat_interval,
                    ssl_options=pika.SSLOptions() if ssl_enabled else None,
                )
                
                # Criar conexão
                connection = AsyncioConnection(connection_params)
                
                # Aguardar estabilização
                await asyncio.sleep(0.1)
                
                if connection.is_closed:
                    raise Exception("Falha ao estabelecer conexão")
                
                # Criar canal
                channel = connection.channel()
                
                # Criar conexão do pool
                current_time = time.time()
                pooled_conn = PooledConnection(
                    connection=connection,
                    channel=channel,
                    created_at=current_time,
                    last_used_at=current_time,
                    use_count=0,
                    is_available=True
                )
                
                self.connections[connection_id] = pooled_conn
                self.available_connections.add(connection_id)
                
                self.logger.info("Conexão criada no pool",
                               connection_id=connection_id,
                               host=host,
                               port=port,
                               pool_size=len(self.connections))
                
                return connection_id
                
            except Exception as e:
                self.logger.error("Erro ao criar conexão no pool",
                                connection_id=connection_id,
                                error=str(e))
                raise
    
    async def get_connection(self, connection_id: Optional[str] = None) -> Optional[str]:
        """
        Obtém uma conexão disponível do pool.
        
        Args:
            connection_id: ID específico da conexão (opcional)
            
        Returns:
            ID da conexão obtida ou None se não disponível
        """
        async with self._lock:
            if connection_id:
                # Buscar conexão específica
                if (connection_id in self.connections and 
                    connection_id in self.available_connections):
                    pooled_conn = self.connections[connection_id]
                    pooled_conn.is_available = False
                    pooled_conn.last_used_at = time.time()
                    pooled_conn.use_count += 1
                    
                    self.available_connections.remove(connection_id)
                    self.busy_connections.add(connection_id)
                    
                    return connection_id
                else:
                    return None
            else:
                # Buscar primeira conexão disponível
                if self.available_connections:
                    conn_id = next(iter(self.available_connections))
                    pooled_conn = self.connections[conn_id]
                    pooled_conn.is_available = False
                    pooled_conn.last_used_at = time.time()
                    pooled_conn.use_count += 1
                    
                    self.available_connections.remove(conn_id)
                    self.busy_connections.add(conn_id)
                    
                    return conn_id
                else:
                    return None
    
    async def release_connection(self, connection_id: str) -> bool:
        """
        Libera uma conexão de volta para o pool.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            True se liberada com sucesso
        """
        async with self._lock:
            if (connection_id in self.connections and 
                connection_id in self.busy_connections):
                
                pooled_conn = self.connections[connection_id]
                
                # Verificar se conexão ainda está ativa
                if pooled_conn.connection.is_closed:
                    await self._remove_connection(connection_id)
                    return False
                
                # Liberar conexão
                pooled_conn.is_available = True
                pooled_conn.last_used_at = time.time()
                
                self.busy_connections.remove(connection_id)
                self.available_connections.add(connection_id)
                
                self.logger.debug("Conexão liberada para o pool",
                                connection_id=connection_id)
                
                return True
            else:
                return False
    
    async def get_channel(self, connection_id: str) -> Optional[pika.channel.Channel]:
        """
        Obtém o canal de uma conexão.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Canal RabbitMQ ou None se não encontrado
        """
        if connection_id not in self.connections:
            return None
        
        pooled_conn = self.connections[connection_id]
        
        # Verificar se canal ainda está ativo
        if pooled_conn.channel.is_closed:
            # Tentar recriar canal
            if not pooled_conn.connection.is_closed:
                try:
                    new_channel = pooled_conn.connection.channel()
                    pooled_conn.channel = new_channel
                    return new_channel
                except Exception as e:
                    self.logger.error("Erro ao recriar canal",
                                    connection_id=connection_id,
                                    error=str(e))
                    return None
            else:
                # Conexão fechada, remover do pool
                await self._remove_connection(connection_id)
                return None
        
        return pooled_conn.channel
    
    async def _remove_connection(self, connection_id: str):
        """
        Remove uma conexão do pool.
        
        Args:
            connection_id: ID da conexão
        """
        if connection_id in self.connections:
            pooled_conn = self.connections[connection_id]
            
            try:
                # Fechar canal
                if not pooled_conn.channel.is_closed:
                    pooled_conn.channel.close()
                
                # Fechar conexão
                if not pooled_conn.connection.is_closed:
                    pooled_conn.connection.close()
            except Exception as e:
                self.logger.warning("Erro ao fechar conexão",
                                  connection_id=connection_id,
                                  error=str(e))
            
            # Remover dos conjuntos
            self.available_connections.discard(connection_id)
            self.busy_connections.discard(connection_id)
            del self.connections[connection_id]
    
    async def close_connection(self, connection_id: str) -> bool:
        """
        Fecha uma conexão específica.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            True se fechada com sucesso
        """
        async with self._lock:
            await self._remove_connection(connection_id)
            return True
    
    async def close_all(self):
        """Fecha todas as conexões do pool."""
        async with self._lock:
            connection_ids = list(self.connections.keys())
            for connection_id in connection_ids:
                await self._remove_connection(connection_id)
            
            # Cancelar tarefa de limpeza
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Pool de conexões fechado")
    
    def get_pool_stats(self) -> Dict:
        """
        Obtém estatísticas do pool.
        
        Returns:
            Dicionário com estatísticas
        """
        total_connections = len(self.connections)
        available_connections = len(self.available_connections)
        busy_connections = len(self.busy_connections)
        
        return {
            "total_connections": total_connections,
            "available_connections": available_connections,
            "busy_connections": busy_connections,
            "max_connections": self.config.max_connections,
            "min_connections": self.config.min_connections,
            "utilization_rate": busy_connections / total_connections if total_connections > 0 else 0,
        }
    
    @asynccontextmanager
    async def get_connection_context(self, connection_id: Optional[str] = None):
        """
        Context manager para obter uma conexão do pool.
        
        Args:
            connection_id: ID específico da conexão (opcional)
            
        Yields:
            ID da conexão ou None se erro
        """
        conn_id = await self.get_connection(connection_id)
        
        try:
            yield conn_id
        finally:
            if conn_id:
                await self.release_connection(conn_id)


# Instância global do pool
connection_pool = ConnectionPool()
