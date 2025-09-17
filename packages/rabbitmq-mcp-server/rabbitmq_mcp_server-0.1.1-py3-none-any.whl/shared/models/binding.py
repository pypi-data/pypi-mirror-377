"""
Modelo de dados para bindings RabbitMQ.

Este módulo define o modelo pydantic para representar bindings entre
exchanges e filas com validação de dados e serialização JSON.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Binding(BaseModel):
    """
    Modelo para representar um binding RabbitMQ.

    Atributos:
        source: Nome do exchange de origem
        destination: Nome da fila ou exchange de destino
        destination_type: Tipo do destino (queue ou exchange)
        routing_key: Chave de roteamento
        arguments: Argumentos do binding
        vhost: Host virtual onde o binding existe
        created_at: Timestamp de criação do binding
        last_updated: Timestamp da última modificação
    """

    source: str = Field(..., min_length=1, description="Nome do exchange de origem")
    destination: str = Field(..., min_length=1, description="Nome da fila ou exchange de destino")
    destination_type: str = Field("queue", description="Tipo do destino (queue ou exchange)")
    routing_key: str = Field("", description="Chave de roteamento")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Argumentos do binding")
    vhost: str = Field("/", min_length=1, description="Host virtual onde o binding existe")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da última modificação")

    class Config:
        """Configuração do modelo pydantic."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @field_validator('source', 'destination')
    @classmethod
    def validate_names(cls, v):
        """Valida os nomes de exchange e fila."""
        if v.startswith('amq.'):
            raise ValueError('Nome não pode começar com "amq."')

        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Nome contém caracteres inválidos')

        return v

    @field_validator('destination_type')
    @classmethod
    def validate_destination_type(cls, v):
        """Valida o tipo de destino."""
        if v not in ['queue', 'exchange']:
            raise ValueError('destination_type deve ser "queue" ou "exchange"')
        return v

    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        """Valida os argumentos do binding."""
        if not isinstance(v, dict):
            raise ValueError('Arguments deve ser um dicionário')
        return v

    def is_queue_binding(self) -> bool:
        """
        Verifica se é um binding para fila.

        Returns:
            True se o destino é uma fila
        """
        return self.destination_type == "queue"

    def is_exchange_binding(self) -> bool:
        """
        Verifica se é um binding para exchange.

        Returns:
            True se o destino é um exchange
        """
        return self.destination_type == "exchange"

    def has_routing_key(self) -> bool:
        """
        Verifica se tem chave de roteamento.

        Returns:
            True se tem chave de roteamento
        """
        return bool(self.routing_key)

    def get_argument(self, key: str, default: Any = None) -> Any:
        """
        Obtém um argumento do binding.

        Args:
            key: Chave do argumento
            default: Valor padrão se a chave não existir

        Returns:
            Valor do argumento ou valor padrão
        """
        return self.arguments.get(key, default)

    def set_argument(self, key: str, value: Any) -> None:
        """
        Define um argumento do binding.

        Args:
            key: Chave do argumento
            value: Valor do argumento
        """
        self.arguments[key] = value
        self.last_updated = datetime.utcnow()

    def is_headers_binding(self) -> bool:
        """
        Verifica se é um binding baseado em headers.

        Returns:
            True se é um binding de headers
        """
        return "x-match" in self.arguments

    def is_direct_binding(self) -> bool:
        """
        Verifica se é um binding direto (sem routing key).

        Returns:
            True se é um binding direto
        """
        return not self.routing_key and not self.arguments

    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário.

        Returns:
            Dicionário com os dados do binding
        """
        return self.dict()

    @classmethod
    def create_test_binding(cls, source: str = "test_exchange", destination: str = "test_queue") -> "Binding":
        """
        Cria um binding de teste para desenvolvimento.

        Args:
            source: Nome do exchange de origem
            destination: Nome da fila de destino

        Returns:
            Instância de Binding para testes
        """
        return cls(
            source=source,
            destination=destination,
            destination_type="queue",
            routing_key="test.key",
            arguments={},
            vhost="/"
        )

    @classmethod
    def create_direct_binding(cls, source: str, destination: str) -> "Binding":
        """
        Cria um binding direto.

        Args:
            source: Nome do exchange de origem
            destination: Nome da fila de destino

        Returns:
            Instância de Binding direto
        """
        return cls(
            source=source,
            destination=destination,
            destination_type="queue",
            routing_key="",
            arguments={},
            vhost="/"
        )

    @classmethod
    def create_topic_binding(cls, source: str, destination: str, routing_key: str) -> "Binding":
        """
        Cria um binding topic.

        Args:
            source: Nome do exchange de origem
            destination: Nome da fila de destino
            routing_key: Chave de roteamento

        Returns:
            Instância de Binding topic
        """
        return cls(
            source=source,
            destination=destination,
            destination_type="queue",
            routing_key=routing_key,
            arguments={},
            vhost="/"
        )

    @classmethod
    def create_headers_binding(cls, source: str, destination: str, headers: dict[str, Any]) -> "Binding":
        """
        Cria um binding baseado em headers.

        Args:
            source: Nome do exchange de origem
            destination: Nome da fila de destino
            headers: Headers para matching

        Returns:
            Instância de Binding de headers
        """
        return cls(
            source=source,
            destination=destination,
            destination_type="queue",
            routing_key="",
            arguments=headers,
            vhost="/"
        )
