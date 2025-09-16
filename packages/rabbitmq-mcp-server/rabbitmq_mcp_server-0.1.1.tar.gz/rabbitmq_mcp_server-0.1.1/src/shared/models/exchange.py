"""
Modelo de dados para exchanges RabbitMQ.

Este módulo define o modelo pydantic para representar exchanges RabbitMQ
com validação de dados e serialização JSON.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ExchangeType(str, Enum):
    """Tipos de exchange RabbitMQ."""
    DIRECT = "direct"
    TOPIC = "topic"
    FANOUT = "fanout"
    HEADERS = "headers"


class Exchange(BaseModel):
    """
    Modelo para representar um exchange RabbitMQ.
    
    Atributos:
        name: Nome do exchange
        type: Tipo do exchange (direct, topic, fanout, headers)
        durable: Se o exchange sobrevive ao reinício do broker
        auto_delete: Se o exchange é deletado quando não usado
        internal: Se o exchange é interno (não para uso de clientes)
        arguments: Argumentos adicionais do exchange
        vhost: Host virtual onde o exchange existe
        created_at: Timestamp de criação do exchange
        last_updated: Timestamp da última modificação
    """
    
    name: str = Field(..., min_length=1, max_length=255, description="Nome do exchange")
    type: ExchangeType = Field(..., description="Tipo do exchange")
    durable: bool = Field(True, description="Se o exchange sobrevive ao reinício do broker")
    auto_delete: bool = Field(False, description="Se o exchange é deletado quando não usado")
    internal: bool = Field(False, description="Se o exchange é interno")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais do exchange")
    vhost: str = Field("/", min_length=1, description="Host virtual onde o exchange existe")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da última modificação")
    
    class Config:
        """Configuração do modelo pydantic."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @field_validator('name')
    @classmethod
    def validate_exchange_name(cls, v):
        """
        Valida o nome do exchange.
        
        Nomes de exchange válidos:
        - Não podem começar com 'amq.'
        - Podem conter letras, números, hífens, underscores e pontos
        - Máximo 255 caracteres
        """
        if v.startswith('amq.'):
            raise ValueError('Nome do exchange não pode começar com "amq."')
        
        # Verificar caracteres válidos
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Nome do exchange contém caracteres inválidos')
        
        return v
    
    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        """Valida os argumentos do exchange."""
        if not isinstance(v, dict):
            raise ValueError('Arguments deve ser um dicionário')
        return v
    
    def is_direct(self) -> bool:
        """
        Verifica se o exchange é do tipo direct.
        
        Returns:
            True se o exchange é direct
        """
        return self.type == ExchangeType.DIRECT
    
    def is_topic(self) -> bool:
        """
        Verifica se o exchange é do tipo topic.
        
        Returns:
            True se o exchange é topic
        """
        return self.type == ExchangeType.TOPIC
    
    def is_fanout(self) -> bool:
        """
        Verifica se o exchange é do tipo fanout.
        
        Returns:
            True se o exchange é fanout
        """
        return self.type == ExchangeType.FANOUT
    
    def is_headers(self) -> bool:
        """
        Verifica se o exchange é do tipo headers.
        
        Returns:
            True se o exchange é headers
        """
        return self.type == ExchangeType.HEADERS
    
    def is_durable(self) -> bool:
        """
        Verifica se o exchange é durável.
        
        Returns:
            True se o exchange é durável
        """
        return self.durable
    
    def is_internal(self) -> bool:
        """
        Verifica se o exchange é interno.
        
        Returns:
            True se o exchange é interno
        """
        return self.internal
    
    def is_auto_delete(self) -> bool:
        """
        Verifica se o exchange é auto-delete.
        
        Returns:
            True se o exchange é auto-delete
        """
        return self.auto_delete
    
    def get_argument(self, key: str, default: Any = None) -> Any:
        """
        Obtém um argumento do exchange.
        
        Args:
            key: Chave do argumento
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor do argumento ou valor padrão
        """
        return self.arguments.get(key, default)
    
    def set_argument(self, key: str, value: Any) -> None:
        """
        Define um argumento do exchange.
        
        Args:
            key: Chave do argumento
            value: Valor do argumento
        """
        self.arguments[key] = value
        self.last_updated = datetime.utcnow()
    
    def supports_routing_key(self) -> bool:
        """
        Verifica se o exchange suporta routing key.
        
        Returns:
            True se o exchange suporta routing key
        """
        return self.type in [ExchangeType.DIRECT, ExchangeType.TOPIC]
    
    def supports_headers(self) -> bool:
        """
        Verifica se o exchange suporta headers.
        
        Returns:
            True se o exchange suporta headers
        """
        return self.type == ExchangeType.HEADERS
    
    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário.
        
        Returns:
            Dicionário com os dados do exchange
        """
        return self.dict()
    
    @classmethod
    def create_test_exchange(cls, name: str = "test_exchange", exchange_type: ExchangeType = ExchangeType.DIRECT) -> "Exchange":
        """
        Cria um exchange de teste para desenvolvimento.
        
        Args:
            name: Nome do exchange de teste
            exchange_type: Tipo do exchange
            
        Returns:
            Instância de Exchange para testes
        """
        return cls(
            name=name,
            type=exchange_type,
            durable=True,
            auto_delete=False,
            internal=False,
            arguments={},
            vhost="/"
        )
    
    @classmethod
    def create_direct_exchange(cls, name: str) -> "Exchange":
        """
        Cria um exchange direct.
        
        Args:
            name: Nome do exchange
            
        Returns:
            Instância de Exchange direct
        """
        return cls(
            name=name,
            type=ExchangeType.DIRECT,
            durable=True,
            auto_delete=False,
            internal=False,
            arguments={}
        )
    
    @classmethod
    def create_topic_exchange(cls, name: str) -> "Exchange":
        """
        Cria um exchange topic.
        
        Args:
            name: Nome do exchange
            
        Returns:
            Instância de Exchange topic
        """
        return cls(
            name=name,
            type=ExchangeType.TOPIC,
            durable=True,
            auto_delete=False,
            internal=False,
            arguments={}
        )
    
    @classmethod
    def create_fanout_exchange(cls, name: str) -> "Exchange":
        """
        Cria um exchange fanout.
        
        Args:
            name: Nome do exchange
            
        Returns:
            Instância de Exchange fanout
        """
        return cls(
            name=name,
            type=ExchangeType.FANOUT,
            durable=True,
            auto_delete=False,
            internal=False,
            arguments={}
        )
    
    @classmethod
    def create_headers_exchange(cls, name: str) -> "Exchange":
        """
        Cria um exchange headers.
        
        Args:
            name: Nome do exchange
            
        Returns:
            Instância de Exchange headers
        """
        return cls(
            name=name,
            type=ExchangeType.HEADERS,
            durable=True,
            auto_delete=False,
            internal=False,
            arguments={}
        )