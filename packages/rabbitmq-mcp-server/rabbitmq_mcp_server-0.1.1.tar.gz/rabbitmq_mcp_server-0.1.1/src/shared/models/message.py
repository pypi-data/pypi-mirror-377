"""
Modelo de dados para mensagens RabbitMQ.

Este módulo define o modelo pydantic para representar mensagens RabbitMQ
com validação de dados e serialização JSON.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class MessageStatus(str, Enum):
    """Status possíveis de uma mensagem."""
    PUBLISHED = "published"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DEAD_LETTERED = "dead_lettered"


class Message(BaseModel):
    """
    Modelo para representar uma mensagem RabbitMQ.
    
    Atributos:
        message_id: Identificador único da mensagem
        body: Conteúdo da mensagem
        headers: Cabeçalhos da mensagem
        routing_key: Chave de roteamento
        exchange: Nome do exchange de origem
        queue: Nome da fila de destino
        delivery_tag: Tag de entrega para confirmação
        redelivered: Se a mensagem foi reentregue
        priority: Prioridade da mensagem (0-255)
        timestamp: Timestamp de criação da mensagem
        expiration: Tempo de expiração da mensagem
        content_type: Tipo de conteúdo da mensagem
        content_encoding: Codificação de conteúdo da mensagem
        status: Status atual da mensagem
    """
    
    message_id: str = Field(..., min_length=1, description="Identificador único da mensagem")
    body: str = Field(..., min_length=1, description="Conteúdo da mensagem")
    headers: Dict[str, Any] = Field(default_factory=dict, description="Cabeçalhos da mensagem")
    routing_key: str = Field(..., min_length=1, description="Chave de roteamento")
    exchange: str = Field(..., min_length=1, description="Nome do exchange de origem")
    queue: str = Field(..., min_length=1, description="Nome da fila de destino")
    delivery_tag: Optional[int] = Field(None, description="Tag de entrega para confirmação")
    redelivered: bool = Field(False, description="Se a mensagem foi reentregue")
    priority: int = Field(0, ge=0, le=255, description="Prioridade da mensagem")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    expiration: Optional[str] = Field(None, description="Tempo de expiração da mensagem")
    content_type: str = Field("application/json", description="Tipo de conteúdo da mensagem")
    content_encoding: str = Field("utf-8", description="Codificação de conteúdo da mensagem")
    status: MessageStatus = Field(MessageStatus.PUBLISHED, description="Status atual da mensagem")
    
    class Config:
        """Configuração do modelo pydantic."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @field_validator('headers')
    @classmethod
    def validate_headers(cls, v):
        """Valida os cabeçalhos da mensagem."""
        if not isinstance(v, dict):
            raise ValueError('Headers deve ser um dicionário')
        return v
    
    @field_validator('expiration')
    @classmethod
    def validate_expiration(cls, v):
        """Valida o tempo de expiração."""
        if v is not None:
            # Verificar se é um número válido (em milissegundos)
            try:
                int(v)
            except ValueError:
                raise ValueError('Expiration deve ser um número válido em milissegundos')
        return v
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        """Valida o tipo de conteúdo."""
        valid_types = [
            "application/json",
            "text/plain",
            "text/html",
            "application/xml",
            "application/octet-stream"
        ]
        if v not in valid_types:
            # Permitir outros tipos, mas avisar
            pass
        return v
    
    def update_status(self, new_status: MessageStatus) -> None:
        """
        Atualiza o status da mensagem.
        
        Args:
            new_status: Novo status da mensagem
        """
        self.status = new_status
    
    def is_published(self) -> bool:
        """
        Verifica se a mensagem foi publicada.
        
        Returns:
            True se a mensagem foi publicada
        """
        return self.status == MessageStatus.PUBLISHED
    
    def is_delivered(self) -> bool:
        """
        Verifica se a mensagem foi entregue.
        
        Returns:
            True se a mensagem foi entregue
        """
        return self.status == MessageStatus.DELIVERED
    
    def is_acknowledged(self) -> bool:
        """
        Verifica se a mensagem foi confirmada.
        
        Returns:
            True se a mensagem foi confirmada
        """
        return self.status == MessageStatus.ACKNOWLEDGED
    
    def is_rejected(self) -> bool:
        """
        Verifica se a mensagem foi rejeitada.
        
        Returns:
            True se a mensagem foi rejeitada
        """
        return self.status == MessageStatus.REJECTED
    
    def is_expired(self) -> bool:
        """
        Verifica se a mensagem expirou.
        
        Returns:
            True se a mensagem expirou
        """
        return self.status == MessageStatus.EXPIRED
    
    def is_dead_lettered(self) -> bool:
        """
        Verifica se a mensagem foi enviada para dead letter queue.
        
        Returns:
            True se a mensagem foi enviada para DLQ
        """
        return self.status == MessageStatus.DEAD_LETTERED
    
    def get_header(self, key: str, default: Any = None) -> Any:
        """
        Obtém um cabeçalho da mensagem.
        
        Args:
            key: Chave do cabeçalho
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor do cabeçalho ou valor padrão
        """
        return self.headers.get(key, default)
    
    def set_header(self, key: str, value: Any) -> None:
        """
        Define um cabeçalho da mensagem.
        
        Args:
            key: Chave do cabeçalho
            value: Valor do cabeçalho
        """
        self.headers[key] = value
    
    def remove_header(self, key: str) -> None:
        """
        Remove um cabeçalho da mensagem.
        
        Args:
            key: Chave do cabeçalho a ser removido
        """
        self.headers.pop(key, None)
    
    def is_json(self) -> bool:
        """
        Verifica se a mensagem é JSON.
        
        Returns:
            True se o content_type é application/json
        """
        return self.content_type == "application/json"
    
    def is_text(self) -> bool:
        """
        Verifica se a mensagem é texto.
        
        Returns:
            True se o content_type é text/*
        """
        return self.content_type.startswith("text/")
    
    def get_body_as_json(self) -> Dict[str, Any]:
        """
        Converte o body da mensagem para JSON.
        
        Returns:
            Dicionário JSON do body
            
        Raises:
            ValueError: Se o body não for JSON válido
        """
        if not self.is_json():
            raise ValueError("Mensagem não é do tipo JSON")
        
        import json
        try:
            return json.loads(self.body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Body não é JSON válido: {e}")
    
    def set_body_from_json(self, data: Dict[str, Any]) -> None:
        """
        Define o body da mensagem a partir de dados JSON.
        
        Args:
            data: Dados para serializar como JSON
        """
        import json
        self.body = json.dumps(data)
        self.content_type = "application/json"
    
    def to_dict(self) -> dict:
        """
        Converte o modelo para dicionário.
        
        Returns:
            Dicionário com os dados da mensagem
        """
        return self.dict()
    
    @classmethod
    def create_test_message(cls, message_id: str = "test_msg", body: str = "test message") -> "Message":
        """
        Cria uma mensagem de teste para desenvolvimento.
        
        Args:
            message_id: ID da mensagem de teste
            body: Conteúdo da mensagem de teste
            
        Returns:
            Instância de Message para testes
        """
        return cls(
            message_id=message_id,
            body=body,
            headers={},
            routing_key="test.routing.key",
            exchange="test_exchange",
            queue="test_queue",
            delivery_tag=None,
            redelivered=False,
            priority=0,
            content_type="application/json",
            content_encoding="utf-8",
            status=MessageStatus.PUBLISHED
        )
    
    @classmethod
    def create_json_message(cls, message_id: str, data: Dict[str, Any], routing_key: str, exchange: str) -> "Message":
        """
        Cria uma mensagem JSON.
        
        Args:
            message_id: ID da mensagem
            data: Dados para serializar como JSON
            routing_key: Chave de roteamento
            exchange: Nome do exchange
            
        Returns:
            Instância de Message com body JSON
        """
        import json
        return cls(
            message_id=message_id,
            body=json.dumps(data),
            headers={},
            routing_key=routing_key,
            exchange=exchange,
            queue="",  # Será definido pelo roteamento
            content_type="application/json",
            content_encoding="utf-8",
            status=MessageStatus.PUBLISHED
        )
    
    @classmethod
    def create_text_message(cls, message_id: str, text: str, routing_key: str, exchange: str) -> "Message":
        """
        Cria uma mensagem de texto.
        
        Args:
            message_id: ID da mensagem
            text: Texto da mensagem
            routing_key: Chave de roteamento
            exchange: Nome do exchange
            
        Returns:
            Instância de Message com body de texto
        """
        return cls(
            message_id=message_id,
            body=text,
            headers={},
            routing_key=routing_key,
            exchange=exchange,
            queue="",  # Será definido pelo roteamento
            content_type="text/plain",
            content_encoding="utf-8",
            status=MessageStatus.PUBLISHED
        )