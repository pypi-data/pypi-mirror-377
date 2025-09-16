"""
Tratamento de erros MCP.

Este módulo implementa tratamento centralizado de erros
para o servidor MCP RabbitMQ.
"""

import asyncio
import json
import traceback
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError, AMQPError

from mcp.types import CallToolResult, TextContent

from src.shared.utils.logging import get_logger


class ErrorType(str, Enum):
    """Tipos de erro."""
    VALIDATION_ERROR = "validation_error"
    CONNECTION_ERROR = "connection_error"
    CHANNEL_ERROR = "channel_error"
    RABBITMQ_ERROR = "rabbitmq_error"
    TIMEOUT_ERROR = "timeout_error"
    PERMISSION_ERROR = "permission_error"
    NOT_FOUND_ERROR = "not_found_error"
    INTERNAL_ERROR = "internal_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorInfo:
    """Informações de erro."""
    error_type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    original_error: Optional[Exception] = None
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ErrorHandler:
    """Tratador de erros MCP."""
    
    def __init__(self):
        """Inicializa o tratador de erros."""
        self.logger = get_logger(__name__)
        self.error_mappings = self._create_error_mappings()
    
    def _create_error_mappings(self) -> Dict[type, ErrorType]:
        """Cria mapeamentos de tipos de erro."""
        return {
            # Erros de validação
            ValueError: ErrorType.VALIDATION_ERROR,
            TypeError: ErrorType.VALIDATION_ERROR,
            KeyError: ErrorType.VALIDATION_ERROR,
            
            # Erros RabbitMQ
            AMQPConnectionError: ErrorType.CONNECTION_ERROR,
            AMQPChannelError: ErrorType.CHANNEL_ERROR,
            AMQPError: ErrorType.RABBITMQ_ERROR,
            
            # Erros de timeout
            asyncio.TimeoutError: ErrorType.TIMEOUT_ERROR,
            TimeoutError: ErrorType.TIMEOUT_ERROR,
            
            # Erros de permissão
            PermissionError: ErrorType.PERMISSION_ERROR,
            
            # Erros de não encontrado
            FileNotFoundError: ErrorType.NOT_FOUND_ERROR,
            ConnectionRefusedError: ErrorType.CONNECTION_ERROR,
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        include_traceback: bool = False,
    ) -> ErrorInfo:
        """
        Trata um erro e retorna informações estruturadas.
        
        Args:
            error: Exceção a ser tratada
            context: Contexto adicional
            include_traceback: Se deve incluir traceback
            
        Returns:
            Informações do erro
        """
        error_type = self._classify_error(error)
        message = self._create_error_message(error, error_type)
        details = self._extract_error_details(error, error_type)
        
        error_info = ErrorInfo(
            error_type=error_type,
            message=message,
            details=details,
            original_error=error,
            context=context,
        )
        
        if include_traceback:
            error_info.traceback = traceback.format_exc()
        
        # Log do erro
        self._log_error(error_info)
        
        return error_info
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """
        Classifica o tipo de erro.
        
        Args:
            error: Exceção
            
        Returns:
            Tipo do erro
        """
        error_type = self.error_mappings.get(type(error))
        
        if error_type:
            return error_type
        
        # Verificar por mensagem de erro
        error_message = str(error).lower()
        
        if "connection" in error_message or "connect" in error_message:
            return ErrorType.CONNECTION_ERROR
        elif "channel" in error_message:
            return ErrorType.CHANNEL_ERROR
        elif "timeout" in error_message:
            return ErrorType.TIMEOUT_ERROR
        elif "permission" in error_message or "access" in error_message:
            return ErrorType.PERMISSION_ERROR
        elif "not found" in error_message or "does not exist" in error_message:
            return ErrorType.NOT_FOUND_ERROR
        elif "validation" in error_message or "invalid" in error_message:
            return ErrorType.VALIDATION_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _create_error_message(self, error: Exception, error_type: ErrorType) -> str:
        """
        Cria mensagem de erro amigável.
        
        Args:
            error: Exceção
            error_type: Tipo do erro
            
        Returns:
            Mensagem de erro
        """
        base_message = str(error)
        
        # Mensagens específicas por tipo
        if error_type == ErrorType.CONNECTION_ERROR:
            return f"Erro de conexão RabbitMQ: {base_message}"
        elif error_type == ErrorType.CHANNEL_ERROR:
            return f"Erro de canal RabbitMQ: {base_message}"
        elif error_type == ErrorType.RABBITMQ_ERROR:
            return f"Erro RabbitMQ: {base_message}"
        elif error_type == ErrorType.TIMEOUT_ERROR:
            return f"Timeout na operação: {base_message}"
        elif error_type == ErrorType.PERMISSION_ERROR:
            return f"Erro de permissão: {base_message}"
        elif error_type == ErrorType.NOT_FOUND_ERROR:
            return f"Recurso não encontrado: {base_message}"
        elif error_type == ErrorType.VALIDATION_ERROR:
            return f"Erro de validação: {base_message}"
        else:
            return f"Erro interno: {base_message}"
    
    def _extract_error_details(
        self, 
        error: Exception, 
        error_type: ErrorType
    ) -> Dict[str, Any]:
        """
        Extrai detalhes específicos do erro.
        
        Args:
            error: Exceção
            error_type: Tipo do erro
            
        Returns:
            Detalhes do erro
        """
        details = {
            "error_type": error_type.value,
            "error_class": error.__class__.__name__,
        }
        
        # Detalhes específicos por tipo
        if error_type == ErrorType.CONNECTION_ERROR:
            if isinstance(error, AMQPConnectionError):
                details.update({
                    "connection_attempts": getattr(error, 'connection_attempts', None),
                    "retry_delay": getattr(error, 'retry_delay', None),
                })
        
        elif error_type == ErrorType.CHANNEL_ERROR:
            if isinstance(error, AMQPChannelError):
                details.update({
                    "reply_code": getattr(error, 'reply_code', None),
                    "reply_text": getattr(error, 'reply_text', None),
                })
        
        elif error_type == ErrorType.TIMEOUT_ERROR:
            details.update({
                "timeout_type": "asyncio" if isinstance(error, asyncio.TimeoutError) else "general",
            })
        
        return details
    
    def _log_error(self, error_info: ErrorInfo):
        """
        Registra o erro no log.
        
        Args:
            error_info: Informações do erro
        """
        log_data = {
            "error_type": error_info.error_type.value,
            "message": error_info.message,
            "context": error_info.context,
        }
        
        if error_info.details:
            log_data["details"] = error_info.details
        
        if error_info.error_type in [ErrorType.INTERNAL_ERROR, ErrorType.UNKNOWN_ERROR]:
            self.logger.error("Erro processado", **log_data)
        else:
            self.logger.warning("Erro processado", **log_data)
    
    def create_error_result(
        self,
        error_info: ErrorInfo,
        include_details: bool = True,
    ) -> CallToolResult:
        """
        Cria resultado de erro MCP.
        
        Args:
            error_info: Informações do erro
            include_details: Se deve incluir detalhes
            
        Returns:
            Resultado de erro MCP
        """
        error_data = {
            "status": "error",
            "error_type": error_info.error_type.value,
            "message": error_info.message,
        }
        
        if include_details and error_info.details:
            error_data["details"] = error_info.details
        
        if error_info.context:
            error_data["context"] = error_info.context
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(error_data, indent=2, ensure_ascii=False)
            )]
        )
    
    async def handle_async_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> CallToolResult:
        """
        Trata erro assíncrono e retorna resultado MCP.
        
        Args:
            error: Exceção
            context: Contexto adicional
            
        Returns:
            Resultado de erro MCP
        """
        error_info = self.handle_error(error, context, include_traceback=True)
        return self.create_error_result(error_info)
    
    def get_error_suggestions(self, error_type: ErrorType) -> List[str]:
        """
        Obtém sugestões para resolver o erro.
        
        Args:
            error_type: Tipo do erro
            
        Returns:
            Lista de sugestões
        """
        suggestions = {
            ErrorType.CONNECTION_ERROR: [
                "Verifique se o servidor RabbitMQ está rodando",
                "Confirme as credenciais de conexão",
                "Verifique a conectividade de rede",
                "Confirme a porta e host do servidor",
            ],
            ErrorType.CHANNEL_ERROR: [
                "Verifique se o canal está ativo",
                "Confirme as permissões do usuário",
                "Verifique se o exchange/fila existe",
                "Tente recriar o canal",
            ],
            ErrorType.TIMEOUT_ERROR: [
                "Aumente o timeout da operação",
                "Verifique a performance do servidor",
                "Reduza o tamanho da operação",
                "Verifique a conectividade de rede",
            ],
            ErrorType.PERMISSION_ERROR: [
                "Verifique as permissões do usuário",
                "Confirme o virtual host",
                "Verifique as políticas de acesso",
            ],
            ErrorType.NOT_FOUND_ERROR: [
                "Verifique se o recurso existe",
                "Confirme o nome do recurso",
                "Verifique o virtual host",
            ],
            ErrorType.VALIDATION_ERROR: [
                "Verifique os parâmetros fornecidos",
                "Confirme os tipos de dados",
                "Verifique os valores obrigatórios",
            ],
        }
        
        return suggestions.get(error_type, [
            "Verifique os logs para mais detalhes",
            "Tente novamente em alguns instantes",
            "Entre em contato com o suporte se o problema persistir",
        ])


# Instância global do tratador de erros
error_handler = ErrorHandler()
