"""
Utilitários de serialização para modelos de dados RabbitMQ.

Este módulo fornece funções de serialização e deserialização
para modelos de dados e mensagens RabbitMQ.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


def serialize_model(model: BaseModel, exclude_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Serializa um modelo pydantic para dicionário.
    
    Args:
        model: Instância do modelo pydantic
        exclude_fields: Campos a serem excluídos da serialização
        
    Returns:
        Dicionário com dados serializados
    """
    if exclude_fields is None:
        exclude_fields = []
    
    data = model.dict()
    
    # Excluir campos especificados
    for field in exclude_fields:
        data.pop(field, None)
    
    # Converter datetime para ISO string
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    
    return data


def deserialize_model(model_class: type, data: Dict[str, Any]) -> BaseModel:
    """
    Deserializa um dicionário para modelo pydantic.
    
    Args:
        model_class: Classe do modelo pydantic
        data: Dados para deserializar
        
    Returns:
        Instância do modelo pydantic
    """
    return model_class(**data)


def serialize_message_body(body: Union[str, Dict[str, Any]], content_type: str = "application/json") -> str:
    """
    Serializa o body de uma mensagem.
    
    Args:
        body: Conteúdo da mensagem
        content_type: Tipo de conteúdo
        
    Returns:
        String serializada
    """
    if isinstance(body, dict):
        if content_type == "application/json":
            return json.dumps(body, ensure_ascii=False)
        else:
            raise ValueError(f"Tipo de conteúdo '{content_type}' não suporta serialização de dicionário")
    
    return str(body)


def deserialize_message_body(body: str, content_type: str = "application/json") -> Union[str, Dict[str, Any]]:
    """
    Deserializa o body de uma mensagem.
    
    Args:
        body: Conteúdo serializado da mensagem
        content_type: Tipo de conteúdo
        
    Returns:
        Conteúdo deserializado
    """
    if content_type == "application/json":
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body
    
    return body


def serialize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializa cabeçalhos de mensagem.
    
    Args:
        headers: Cabeçalhos para serializar
        
    Returns:
        Cabeçalhos serializados
    """
    serialized = {}
    
    for key, value in headers.items():
        if isinstance(value, (dict, list)):
            serialized[key] = json.dumps(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = str(value)
    
    return serialized


def deserialize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deserializa cabeçalhos de mensagem.
    
    Args:
        headers: Cabeçalhos para deserializar
        
    Returns:
        Cabeçalhos deserializados
    """
    deserialized = {}
    
    for key, value in headers.items():
        if isinstance(value, str):
            # Tentar deserializar JSON
            try:
                deserialized[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Tentar deserializar datetime
                try:
                    deserialized[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    deserialized[key] = value
        else:
            deserialized[key] = value
    
    return deserialized


def serialize_connection(connection: BaseModel, include_password: bool = False) -> Dict[str, Any]:
    """
    Serializa uma conexão RabbitMQ.
    
    Args:
        connection: Instância da conexão
        include_password: Se deve incluir a senha
        
    Returns:
        Dicionário com dados da conexão
    """
    exclude_fields = [] if include_password else ["password"]
    return serialize_model(connection, exclude_fields)


def serialize_queue(queue: BaseModel) -> Dict[str, Any]:
    """
    Serializa uma fila RabbitMQ.
    
    Args:
        queue: Instância da fila
        
    Returns:
        Dicionário com dados da fila
    """
    return serialize_model(queue)


def serialize_exchange(exchange: BaseModel) -> Dict[str, Any]:
    """
    Serializa um exchange RabbitMQ.
    
    Args:
        exchange: Instância do exchange
        
    Returns:
        Dicionário com dados do exchange
    """
    return serialize_model(exchange)


def serialize_message(message: BaseModel) -> Dict[str, Any]:
    """
    Serializa uma mensagem RabbitMQ.
    
    Args:
        message: Instância da mensagem
        
    Returns:
        Dicionário com dados da mensagem
    """
    return serialize_model(message)


def to_json_string(data: Any, indent: Optional[int] = None) -> str:
    """
    Converte dados para string JSON.
    
    Args:
        data: Dados para converter
        indent: Indentação do JSON
        
    Returns:
        String JSON
    """
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def from_json_string(json_str: str) -> Any:
    """
    Converte string JSON para dados.
    
    Args:
        json_str: String JSON
        
    Returns:
        Dados deserializados
    """
    return json.loads(json_str)


def safe_json_serialize(data: Any) -> str:
    """
    Serialização JSON segura que trata tipos não serializáveis.
    
    Args:
        data: Dados para serializar
        
    Returns:
        String JSON
    """
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        else:
            return str(obj)
    
    return json.dumps(data, default=default_serializer, ensure_ascii=False)