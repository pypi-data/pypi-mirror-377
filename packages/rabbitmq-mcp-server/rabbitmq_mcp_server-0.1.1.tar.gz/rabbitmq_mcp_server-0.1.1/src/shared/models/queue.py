"""
Modelo de dados para filas RabbitMQ.

Este módulo define o modelo pydantic para representar filas RabbitMQ
com validação de dados e serialização JSON.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class Queue(BaseModel):
    """
    Modelo para representar uma fila RabbitMQ.
    
    Atributos:
        name: Nome da fila
        durable: Se a fila sobrevive ao reinício do broker
        exclusive: Se a fila é exclusiva da conexão
        auto_delete: Se a fila é deletada quando não usada
        arguments: Argumentos adicionais da fila
        message_count: Número atual de mensagens na fila
        consumer_count: Número atual de consumidores
        vhost: Host virtual onde a fila existe
        created_at: Timestamp de criação da fila
        last_updated: Timestamp da última modificação
    """
    
    name: str = Field(..., min_length=1, max_length=255, description="Nome da fila")
    durable: bool = Field(True, description="Se a fila sobrevive ao reinício do broker")
    exclusive: bool = Field(False, description="Se a fila é exclusiva da conexão")
    auto_delete: bool = Field(False, description="Se a fila é deletada quando não usada")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos adicionais da fila")
    message_count: int = Field(0, ge=0, description="Número atual de mensagens na fila")
    consumer_count: int = Field(0, ge=0, description="Número atual de consumidores")
    vhost: str = Field("/", min_length=1, description="Host virtual onde a fila existe")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da última modificação")
    
    class Config:
        """Configuração do modelo pydantic."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @field_validator('name')
    @classmethod
    def validate_queue_name(cls, v):
        """
        Valida o nome da fila.
        
        Nomes de fila válidos:
        - Não podem começar com 'amq.'
        - Podem conter letras, números, hífens, underscores e pontos
        - Máximo 255 caracteres
        """
        if v.startswith('amq.'):
            raise ValueError('Nome da fila não pode começar com "amq."')
        
        # Verificar caracteres válidos
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Nome da fila contém caracteres inválidos')
        
        return v
    
    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        """Valida os argumentos da fila."""
        if not isinstance(v, dict):
            raise ValueError('Arguments deve ser um dicionário')
        return v
    
    def update_stats(self, message_count: int, consumer_count: int) -> None:
        """
        Atualiza as estatísticas da fila.
        
        Args:
            message_count: Número de mensagens
            consumer_count: Número de consumidores
        """
        self.message_count = message_count
        self.consumer_count = consumer_count
        self.last_updated = datetime.utcnow()
    
    def is_empty(self) -> bool:
        """
        Verifica se a fila está vazia.
        
        Returns:
            True se a fila não tem mensagens
        """
        return self.message_count == 0
    
    def has_consumers(self) -> bool:
        """
        Verifica se a fila tem consumidores.
        
        Returns:
            True se a fila tem consumidores
        """
        return self.consumer_count > 0
    
    def is_durable(self) -> bool:
        """
        Verifica se a fila é durável.
        
        Returns:
            True se a fila é durável
        """
        return self.durable
    
    def is_exclusive(self) -> bool:
        """
        Verifica se a fila é exclusiva.
        
        Returns:
            True se a fila é exclusiva
        """
        return self.exclusive
    
    def is_auto_delete(self) -> bool:
        """
        Verifica se a fila é auto-delete.
        
        Returns:
            True se a fila é auto-delete
        """
        return self.auto_delete
    
    def get_argument(self, key: str, default: Any = None) -> Any:
        """
        Obtém um argumento da fila.
        
        Args:
            key: Chave do argumento
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor do argumento ou valor padrão
        """
        return self.arguments.get(key, default)
    
    def set_argument(self, key: str, value: Any) -> None:
        """
        Define um argumento da fila.
        
        Args:
            key: Chave do argumento
            value: Valor do argumento
        """
        self.arguments[key] = value
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário.
        
        Returns:
            Dicionário com os dados da fila
        """
        return self.dict()
    
    @classmethod
    def create_test_queue(cls, name: str = "test_queue") -> "Queue":
        """
        Cria uma fila de teste para desenvolvimento.
        
        Args:
            name: Nome da fila de teste
            
        Returns:
            Instância de Queue para testes
        """
        return cls(
            name=name,
            durable=True,
            exclusive=False,
            auto_delete=False,
            arguments={},
            message_count=0,
            consumer_count=0,
            vhost="/"
        )
    
    @classmethod
    def create_durable_queue(cls, name: str) -> "Queue":
        """
        Cria uma fila durável.
        
        Args:
            name: Nome da fila
            
        Returns:
            Instância de Queue durável
        """
        return cls(
            name=name,
            durable=True,
            exclusive=False,
            auto_delete=False,
            arguments={}
        )
    
    @classmethod
    def create_temporary_queue(cls, name: str) -> "Queue":
        """
        Cria uma fila temporária.
        
        Args:
            name: Nome da fila
            
        Returns:
            Instância de Queue temporária
        """
        return cls(
            name=name,
            durable=False,
            exclusive=False,
            auto_delete=True,
            arguments={}
        )