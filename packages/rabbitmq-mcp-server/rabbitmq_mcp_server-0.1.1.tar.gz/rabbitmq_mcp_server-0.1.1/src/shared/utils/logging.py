"""
Configuração de logging estruturado para o RabbitMQ MCP Server.

Este módulo configura o structlog para logging estruturado com suporte a:
- Formatação JSON para produção
- Formatação colorida para desenvolvimento
- Contexto de correlação para rastreamento
- Integração com MCP tools
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    include_correlation_id: bool = True,
) -> None:
    """
    Configura o logging estruturado para a aplicação.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Tipo de formatação ('json' ou 'console')
        include_correlation_id: Se deve incluir ID de correlação
    """
    # Configurar processadores base
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO"),
    ]
    
    # Adicionar ID de correlação se solicitado
    if include_correlation_id:
        processors.append(add_correlation_id)
    
    # Configurar formatação baseada no tipo
    if format_type == "json":
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])
    else:  # console
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    
    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.WriteLoggerFactory(
            file=sys.stdout
        ),
        cache_logger_on_first_use=True,
    )
    
    # Configurar logging padrão do Python
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )


def add_correlation_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adiciona ID de correlação ao contexto de logging.
    
    Args:
        logger: Logger instance
        method_name: Nome do método de logging
        event_dict: Dicionário de contexto do evento
        
    Returns:
        Dicionário de contexto atualizado
    """
    import uuid
    
    # Gerar ID de correlação se não existir
    if "correlation_id" not in event_dict:
        event_dict["correlation_id"] = str(uuid.uuid4())[:8]
    
    return event_dict


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Obtém um logger estruturado para o módulo especificado.
    
    Args:
        name: Nome do módulo (geralmente __name__)
        
    Returns:
        Logger estruturado configurado
    """
    return structlog.get_logger(name)


def log_mcp_request(
    tool_name: str,
    connection_id: Optional[str] = None,
    **kwargs: Any
) -> structlog.BoundLogger:
    """
    Cria um logger com contexto MCP para requisições.
    
    Args:
        tool_name: Nome da ferramenta MCP
        connection_id: ID da conexão RabbitMQ
        **kwargs: Contexto adicional
        
    Returns:
        Logger com contexto MCP
    """
    logger = get_logger("mcp.request")
    return logger.bind(
        tool_name=tool_name,
        connection_id=connection_id,
        **kwargs
    )


def log_rabbitmq_operation(
    operation: str,
    connection_id: str,
    **kwargs: Any
) -> structlog.BoundLogger:
    """
    Cria um logger com contexto RabbitMQ para operações.
    
    Args:
        operation: Nome da operação RabbitMQ
        connection_id: ID da conexão RabbitMQ
        **kwargs: Contexto adicional
        
    Returns:
        Logger com contexto RabbitMQ
    """
    logger = get_logger("rabbitmq.operation")
    return logger.bind(
        operation=operation,
        connection_id=connection_id,
        **kwargs
    )


def log_console_command(
    command: str,
    **kwargs: Any
) -> structlog.BoundLogger:
    """
    Cria um logger com contexto para comandos do console.
    
    Args:
        command: Nome do comando
        **kwargs: Contexto adicional
        
    Returns:
        Logger com contexto de comando
    """
    logger = get_logger("console.command")
    return logger.bind(
        command=command,
        **kwargs
    )


# Configuração padrão para desenvolvimento
if __name__ == "__main__":
    configure_logging(level="DEBUG", format_type="console")
    
    # Teste do logging
    logger = get_logger(__name__)
    logger.info("Logging configurado com sucesso", test=True)
    
    # Teste com contexto MCP
    mcp_logger = log_mcp_request("test_tool", "conn_123", test_param="value")
    mcp_logger.info("Teste de logging MCP")
    
    # Teste com contexto RabbitMQ
    rmq_logger = log_rabbitmq_operation("queue_create", "conn_123", queue_name="test")
    rmq_logger.info("Teste de logging RabbitMQ")
