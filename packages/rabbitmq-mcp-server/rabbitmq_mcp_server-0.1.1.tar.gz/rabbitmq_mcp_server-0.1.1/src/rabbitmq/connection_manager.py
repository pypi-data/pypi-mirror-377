"""
Gerenciador de conexões RabbitMQ.

Este módulo implementa o gerenciamento de conexões RabbitMQ,
incluindo criação, manutenção e limpeza de conexões.
"""

import asyncio
import uuid
from typing import Dict, Optional, Set
from contextlib import asynccontextmanager

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from src.shared.models.connection import Connection, ConnectionStatus
from src.shared.utils.logging import get_logger


class ConnectionManager:
    """Gerenciador de conexões RabbitMQ."""
    
    def __init__(self):
        """Inicializa o gerenciador de conexões."""
        self.connections: Dict[str, Connection] = {}
        self.connection_objects: Dict[str, AsyncioConnection] = {}
        self.channels: Dict[str, pika.channel.Channel] = {}
        self.logger = get_logger(__name__)
        self._lock = asyncio.Lock()
    
    async def create_connection(
        self,
        host: str,
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        ssl_enabled: bool = False,
        connection_timeout: int = 30,
        heartbeat_interval: int = 600,
    ) -> str:
        """
        Cria uma nova conexão RabbitMQ.
        
        Args:
            host: Hostname ou IP do servidor RabbitMQ
            port: Porta do servidor RabbitMQ
            username: Nome de usuário para autenticação
            password: Senha para autenticação
            virtual_host: Virtual host RabbitMQ
            ssl_enabled: Se SSL/TLS está habilitado
            connection_timeout: Timeout de conexão em segundos
            heartbeat_interval: Intervalo de heartbeat em segundos
            
        Returns:
            ID da conexão criada
            
        Raises:
            AMQPConnectionError: Erro ao conectar com RabbitMQ
        """
        async with self._lock:
            connection_id = str(uuid.uuid4())
            
            try:
                # Configurar parâmetros de conexão
                credentials = pika.PlainCredentials(username, password)
                
                connection_params = pika.ConnectionParameters(
                    host=host,
                    port=port,
                    virtual_host=virtual_host,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=1.0,
                    socket_timeout=connection_timeout,
                    heartbeat=heartbeat_interval,
                    ssl_options=pika.SSLOptions() if ssl_enabled else None,
                )
                
                # Criar conexão assíncrona
                connection = AsyncioConnection(connection_params)
                
                # Aguardar conexão ser estabelecida
                await asyncio.sleep(0.1)  # Pequeno delay para estabilizar
                
                if connection.is_closed:
                    raise AMQPConnectionError("Falha ao estabelecer conexão")
                
                # Criar canal
                channel = connection.channel()
                
                # Armazenar conexão e canal
                self.connection_objects[connection_id] = connection
                self.channels[connection_id] = channel
                
                # Criar modelo de conexão
                connection_model = Connection(
                    id=connection_id,
                    host=host,
                    port=port,
                    username=username,
                    virtual_host=virtual_host,
                    ssl_enabled=ssl_enabled,
                    status=ConnectionStatus.CONNECTED,
                    created_at=asyncio.get_event_loop().time(),
                )
                
                self.connections[connection_id] = connection_model
                
                self.logger.info("Conexão RabbitMQ criada com sucesso",
                               connection_id=connection_id,
                               host=host,
                               port=port)
                
                return connection_id
                
            except Exception as e:
                self.logger.error("Erro ao criar conexão RabbitMQ",
                                connection_id=connection_id,
                                error=str(e))
                
                # Limpar recursos em caso de erro
                await self._cleanup_connection(connection_id)
                raise AMQPConnectionError(f"Falha ao conectar: {str(e)}")
    
    async def disconnect_connection(self, connection_id: str) -> bool:
        """
        Desconecta uma conexão RabbitMQ.
        
        Args:
            connection_id: ID da conexão a ser desconectada
            
        Returns:
            True se desconectada com sucesso, False caso contrário
        """
        async with self._lock:
            if connection_id not in self.connections:
                self.logger.warning("Tentativa de desconectar conexão inexistente",
                                  connection_id=connection_id)
                return False
            
            try:
                connection = self.connections[connection_id]
                connection.status = ConnectionStatus.DISCONNECTING
                
                # Fechar canal
                if connection_id in self.channels:
                    channel = self.channels[connection_id]
                    if not channel.is_closed:
                        channel.close()
                    del self.channels[connection_id]
                
                # Fechar conexão
                if connection_id in self.connection_objects:
                    conn_obj = self.connection_objects[connection_id]
                    if not conn_obj.is_closed:
                        conn_obj.close()
                    del self.connection_objects[connection_id]
                
                # Atualizar status
                connection.status = ConnectionStatus.DISCONNECTED
                connection.disconnected_at = asyncio.get_event_loop().time()
                
                self.logger.info("Conexão RabbitMQ desconectada",
                               connection_id=connection_id)
                
                return True
                
            except Exception as e:
                self.logger.error("Erro ao desconectar conexão",
                                connection_id=connection_id,
                                error=str(e))
                return False
    
    async def get_connection_status(self, connection_id: str) -> Optional[ConnectionStatus]:
        """
        Obtém o status de uma conexão.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Status da conexão ou None se não encontrada
        """
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        
        # Verificar se conexão ainda está ativa
        if connection_id in self.connection_objects:
            conn_obj = self.connection_objects[connection_id]
            if conn_obj.is_closed:
                connection.status = ConnectionStatus.DISCONNECTED
                connection.disconnected_at = asyncio.get_event_loop().time()
        
        return connection.status
    
    async def list_connections(self, include_stats: bool = True) -> Dict[str, Connection]:
        """
        Lista todas as conexões ativas.
        
        Args:
            include_stats: Se deve incluir estatísticas das conexões
            
        Returns:
            Dicionário com conexões ativas
        """
        async with self._lock:
            # Atualizar status das conexões
            for connection_id, connection in self.connections.items():
                if connection_id in self.connection_objects:
                    conn_obj = self.connection_objects[connection_id]
                    if conn_obj.is_closed and connection.status == ConnectionStatus.CONNECTED:
                        connection.status = ConnectionStatus.DISCONNECTED
                        connection.disconnected_at = asyncio.get_event_loop().time()
            
            # Filtrar apenas conexões ativas
            active_connections = {
                conn_id: conn for conn_id, conn in self.connections.items()
                if conn.status == ConnectionStatus.CONNECTED
            }
            
            if include_stats:
                # Adicionar estatísticas básicas
                for connection in active_connections.values():
                    connection.stats = {
                        "uptime": asyncio.get_event_loop().time() - connection.created_at,
                        "channels_count": 1,  # Simplificado
                        "messages_sent": 0,  # TODO: Implementar contadores
                        "messages_received": 0,
                    }
            
            return active_connections
    
    async def get_channel(self, connection_id: str) -> Optional[pika.channel.Channel]:
        """
        Obtém o canal de uma conexão.
        
        Args:
            connection_id: ID da conexão
            
        Returns:
            Canal RabbitMQ ou None se não encontrado
        """
        if connection_id not in self.channels:
            return None
        
        channel = self.channels[connection_id]
        
        # Verificar se canal ainda está ativo
        if channel.is_closed:
            # Tentar recriar canal
            if connection_id in self.connection_objects:
                conn_obj = self.connection_objects[connection_id]
                if not conn_obj.is_closed:
                    try:
                        new_channel = conn_obj.channel()
                        self.channels[connection_id] = new_channel
                        return new_channel
                    except Exception as e:
                        self.logger.error("Erro ao recriar canal",
                                        connection_id=connection_id,
                                        error=str(e))
                        return None
                else:
                    # Conexão fechada, remover canal
                    del self.channels[connection_id]
                    return None
        
        return channel
    
    async def _cleanup_connection(self, connection_id: str):
        """
        Limpa recursos de uma conexão.
        
        Args:
            connection_id: ID da conexão
        """
        try:
            # Fechar canal
            if connection_id in self.channels:
                channel = self.channels[connection_id]
                if not channel.is_closed:
                    channel.close()
                del self.channels[connection_id]
            
            # Fechar conexão
            if connection_id in self.connection_objects:
                conn_obj = self.connection_objects[connection_id]
                if not conn_obj.is_closed:
                    conn_obj.close()
                del self.connection_objects[connection_id]
            
            # Remover modelo
            if connection_id in self.connections:
                del self.connections[connection_id]
                
        except Exception as e:
            self.logger.error("Erro ao limpar recursos da conexão",
                            connection_id=connection_id,
                            error=str(e))
    
    async def cleanup_all(self):
        """Limpa todas as conexões."""
        async with self._lock:
            connection_ids = list(self.connections.keys())
            for connection_id in connection_ids:
                await self._cleanup_connection(connection_id)
            
            self.logger.info("Todas as conexões foram limpas")
    
    @asynccontextmanager
    async def get_connection_context(self, connection_id: str):
        """
        Context manager para obter uma conexão de forma segura.
        
        Args:
            connection_id: ID da conexão
            
        Yields:
            Tupla (connection, channel) ou (None, None) se erro
        """
        connection = self.connections.get(connection_id)
        channel = await self.get_channel(connection_id)
        
        try:
            yield connection, channel
        except Exception as e:
            self.logger.error("Erro no contexto da conexão",
                            connection_id=connection_id,
                            error=str(e))
            raise


# Instância global do gerenciador
connection_manager = ConnectionManager()
