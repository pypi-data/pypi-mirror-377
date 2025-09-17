"""Utilitários de validação para modelos de dados RabbitMQ."""

import re
from typing import Any

from pydantic import BaseModel, ValidationError


def validate_connection_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida parâmetros de conexão RabbitMQ."""
    required_fields = ["host", "username", "password"]

    for field in required_fields:
        if field not in params:
            raise ValueError(f"Campo obrigatório '{field}' não fornecido")
        if not isinstance(params[field], str) or not params[field].strip():
            raise ValueError(f"Campo '{field}' deve ser uma string não vazia")

    # Validar host
    host = params["host"].strip()
    if not _is_valid_hostname(host) and not _is_valid_ip(host):
        raise ValueError(f"Host inválido: {host}")

    # Validar port se fornecido
    if "port" in params:
        port = params["port"]
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("Porta deve ser um inteiro entre 1 e 65535")

    return params


def validate_queue_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida parâmetros de fila RabbitMQ."""
    required_fields = ["connection_id", "queue_name"]

    for field in required_fields:
        if field not in params:
            raise ValueError(f"Campo obrigatório '{field}' não fornecido")
        if not isinstance(params[field], str) or not params[field].strip():
            raise ValueError(f"Campo '{field}' deve ser uma string não vazia")

    # Validar nome da fila
    queue_name = params["queue_name"].strip()
    if not _is_valid_queue_name(queue_name):
        raise ValueError(f"Nome de fila inválido: {queue_name}")

    return params


def validate_exchange_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida parâmetros de exchange RabbitMQ."""
    required_fields = ["connection_id", "exchange_name", "exchange_type"]

    for field in required_fields:
        if field not in params:
            raise ValueError(f"Campo obrigatório '{field}' não fornecido")
        if not isinstance(params[field], str) or not params[field].strip():
            raise ValueError(f"Campo '{field}' deve ser uma string não vazia")

    # Validar tipo do exchange
    exchange_type = params["exchange_type"].strip().lower()
    valid_types = ["direct", "topic", "fanout", "headers"]
    if exchange_type not in valid_types:
        raise ValueError(f"Tipo de exchange inválido: {exchange_type}")

    return params


def validate_message_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida parâmetros de mensagem RabbitMQ."""
    required_fields = ["connection_id", "exchange_name", "routing_key", "message_body"]

    for field in required_fields:
        if field not in params:
            raise ValueError(f"Campo obrigatório '{field}' não fornecido")
        if not isinstance(params[field], str) or not params[field].strip():
            raise ValueError(f"Campo '{field}' deve ser uma string não vazia")

    return params


def validate_delivery_tags(tags: int | list[int]) -> list[int]:
    """Valida tags de entrega para confirmação/rejeição."""
    if isinstance(tags, int):
        tags = [tags]

    if not isinstance(tags, list) or not tags:
        raise ValueError("delivery_tags deve ser um inteiro ou lista de inteiros")

    for tag in tags:
        if not isinstance(tag, int) or tag <= 0:
            raise ValueError("delivery_tags deve conter apenas inteiros positivos")

    return tags


def validate_pydantic_model(model_class: type, data: dict[str, Any]) -> BaseModel:
    """Valida dados usando um modelo pydantic."""
    try:
        return model_class(**data)
    except ValidationError as e:
        raise ValueError(f"Erro de validação: {e}") from e


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> None:
    """Valida se todos os campos obrigatórios estão presentes."""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")


def validate_field_types(data: dict[str, Any], field_types: dict[str, type]) -> None:
    """Valida se os campos têm os tipos corretos."""
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            raise ValueError(f"Campo '{field}' deve ser do tipo {expected_type.__name__}")


def _is_valid_hostname(hostname: str) -> bool:
    """Verifica se um hostname é válido."""
    if len(hostname) > 253:
        return False
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        return False
    if hostname.startswith('-') or hostname.endswith('-'):
        return False
    if '..' in hostname:
        return False
    # Hostname deve começar e terminar com letra ou número
    if not re.match(r'^[a-zA-Z0-9]', hostname):
        return False
    if not re.search(r'[a-zA-Z0-9]$', hostname):
        return False
    return True


def _is_valid_ip(ip: str) -> bool:
    """Verifica se um IP é válido."""
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return False


def _is_valid_queue_name(name: str) -> bool:
    """Verifica se um nome de fila é válido."""
    if not name or len(name) > 255:
        return False
    if name.startswith('amq.'):
        return False
    return bool(re.match(r'^[a-zA-Z0-9._-]+$', name))


def _is_valid_exchange_name(name: str) -> bool:
    """Verifica se um nome de exchange é válido."""
    if not name or len(name) > 255:
        return False
    if name.startswith('amq.'):
        return False
    return bool(re.match(r'^[a-zA-Z0-9._-]+$', name))
