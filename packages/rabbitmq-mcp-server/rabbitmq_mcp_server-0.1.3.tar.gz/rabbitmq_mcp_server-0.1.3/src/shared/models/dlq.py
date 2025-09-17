"""
Modelo de dados para Dead Letter Queue (DLQ) RabbitMQ.

Este módulo define o modelo pydantic para representar configurações de DLQ
com validação de dados e serialização JSON.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DeadLetterQueue(BaseModel):
    """
    Modelo para representar uma configuração de Dead Letter Queue.

    Atributos:
        queue_name: Nome da fila principal
        dlq_name: Nome da fila de dead letter
        dlq_exchange: Nome do exchange de dead letter
        routing_key: Chave de roteamento para DLQ
        ttl: Tempo de vida da mensagem em milissegundos
        max_retries: Número máximo de tentativas
        retry_delay: Delay entre tentativas em milissegundos
        arguments: Argumentos adicionais da DLQ
        vhost: Host virtual onde a DLQ existe
        created_at: Timestamp de criação da configuração
        last_updated: Timestamp da última modificação
    """

    queue_name: str = Field(..., min_length=1, description="Nome da fila principal")
    dlq_name: str = Field(..., min_length=1, description="Nome da fila de dead letter")
    dlq_exchange: str = Field(..., min_length=1, description="Nome do exchange de dead letter")
    routing_key: str = Field("failed", description="Chave de roteamento para DLQ")
    ttl: int = Field(3600000, ge=1000, description="Tempo de vida da mensagem em milissegundos")
    max_retries: int = Field(3, ge=0, le=10, description="Número máximo de tentativas")
    retry_delay: int = Field(5000, ge=1000, description="Delay entre tentativas em milissegundos")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais da DLQ")
    vhost: str = Field("/", min_length=1, description="Host virtual onde a DLQ existe")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da última modificação")

    class Config:
        """Configuração do modelo pydantic."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @field_validator('queue_name', 'dlq_name', 'dlq_exchange')
    @classmethod
    def validate_names(cls, v):
        """Valida os nomes de fila e exchange."""
        if v.startswith('amq.'):
            raise ValueError('Nome não pode começar com "amq."')

        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Nome contém caracteres inválidos')

        return v

    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        """Valida os argumentos da DLQ."""
        if not isinstance(v, dict):
            raise ValueError('Arguments deve ser um dicionário')
        return v

    def get_argument(self, key: str, default: Any = None) -> Any:
        """
        Obtém um argumento da DLQ.

        Args:
            key: Chave do argumento
            default: Valor padrão se a chave não existir

        Returns:
            Valor do argumento ou valor padrão
        """
        return self.arguments.get(key, default)

    def set_argument(self, key: str, value: Any) -> None:
        """
        Define um argumento da DLQ.

        Args:
            key: Chave do argumento
            value: Valor do argumento
        """
        self.arguments[key] = value
        self.last_updated = datetime.utcnow()

    def is_configured(self) -> bool:
        """
        Verifica se a DLQ está configurada.

        Returns:
            True se a DLQ está configurada
        """
        return bool(self.dlq_name and self.dlq_exchange)

    def get_ttl_seconds(self) -> int:
        """
        Obtém o TTL em segundos.

        Returns:
            TTL em segundos
        """
        return self.ttl // 1000

    def get_retry_delay_seconds(self) -> int:
        """
        Obtém o delay de retry em segundos.

        Returns:
            Delay em segundos
        """
        return self.retry_delay // 1000

    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário.

        Returns:
            Dicionário com os dados da DLQ
        """
        return self.dict()

    @classmethod
    def create_test_dlq(cls, queue_name: str = "test_queue") -> "DeadLetterQueue":
        """
        Cria uma DLQ de teste para desenvolvimento.

        Args:
            queue_name: Nome da fila principal

        Returns:
            Instância de DeadLetterQueue para testes
        """
        return cls(
            queue_name=queue_name,
            dlq_name=f"{queue_name}_dlq",
            dlq_exchange=f"{queue_name}_dlq_exchange",
            routing_key="failed",
            ttl=3600000,
            max_retries=3,
            retry_delay=5000,
            arguments={},
            vhost="/"
        )

    @classmethod
    def create_retry_dlq(cls, queue_name: str, max_retries: int = 5) -> "DeadLetterQueue":
        """
        Cria uma DLQ com configuração de retry.

        Args:
            queue_name: Nome da fila principal
            max_retries: Número máximo de tentativas

        Returns:
            Instância de DeadLetterQueue com retry
        """
        return cls(
            queue_name=queue_name,
            dlq_name=f"{queue_name}_retry_dlq",
            dlq_exchange=f"{queue_name}_retry_exchange",
            routing_key="retry",
            ttl=300000,  # 5 minutos
            max_retries=max_retries,
            retry_delay=10000,  # 10 segundos
            arguments={
                "x-message-ttl": 300000,
                "x-dead-letter-exchange": queue_name,
                "x-dead-letter-routing-key": queue_name
            },
            vhost="/"
        )
