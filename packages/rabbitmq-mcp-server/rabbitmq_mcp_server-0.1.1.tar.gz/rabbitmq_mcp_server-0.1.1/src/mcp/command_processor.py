"""
Processador de comandos MCP.

Este módulo implementa o processamento avançado de comandos MCP,
incluindo validação, roteamento e tratamento de erros.
"""

import asyncio
import json
import traceback
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum

from mcp.types import CallToolRequest, CallToolResult, TextContent

from src.shared.utils.logging import get_logger
from src.shared.utils.validation import validate_required_fields, validate_field_types


class CommandStatus(str, Enum):
    """Status de processamento de comando."""
    SUCCESS = "success"
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    INTERNAL_ERROR = "internal_error"


@dataclass
class CommandResult:
    """Resultado do processamento de comando."""
    status: CommandStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict] = None


@dataclass
class CommandHandler:
    """Handler de comando MCP."""
    name: str
    handler: Callable
    schema: Dict[str, Any]
    timeout: int = 30
    retry_count: int = 0
    description: str = ""


class CommandProcessor:
    """Processador de comandos MCP."""
    
    def __init__(self):
        """Inicializa o processador de comandos."""
        self.handlers: Dict[str, CommandHandler] = {}
        self.logger = get_logger(__name__)
        self.middleware: List[Callable] = []
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Registra handlers padrão."""
        # Handlers serão registrados pelos módulos de ferramentas
        pass
    
    def register_handler(
        self,
        name: str,
        handler: Callable,
        schema: Dict[str, Any],
        timeout: int = 30,
        retry_count: int = 0,
        description: str = "",
    ):
        """
        Registra um handler de comando.
        
        Args:
            name: Nome do comando
            handler: Função handler
            schema: Schema de validação
            timeout: Timeout em segundos
            retry_count: Número de tentativas
            description: Descrição do comando
        """
        command_handler = CommandHandler(
            name=name,
            handler=handler,
            schema=schema,
            timeout=timeout,
            retry_count=retry_count,
            description=description,
        )
        
        self.handlers[name] = command_handler
        self.logger.info("Handler registrado", command_name=name)
    
    def add_middleware(self, middleware: Callable):
        """
        Adiciona middleware ao processador.
        
        Args:
            middleware: Função de middleware
        """
        self.middleware.append(middleware)
        self.logger.info("Middleware adicionado", middleware=str(middleware))
    
    async def process_command(self, request: CallToolRequest) -> CallToolResult:
        """
        Processa um comando MCP.
        
        Args:
            request: Requisição de comando
            
        Returns:
            Resultado do processamento
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Verificar se handler existe
            if request.name not in self.handlers:
                return self._create_error_result(
                    f"Comando não encontrado: {request.name}",
                    CommandStatus.ERROR
                )
            
            handler = self.handlers[request.name]
            
            # Executar middleware
            for middleware in self.middleware:
                try:
                    await middleware(request, handler)
                except Exception as e:
                    self.logger.warning("Erro no middleware", 
                                      middleware=str(middleware),
                                      error=str(e))
            
            # Validar argumentos
            validation_result = await self._validate_arguments(request, handler)
            if validation_result.status != CommandStatus.SUCCESS:
                return self._create_error_result(
                    validation_result.error,
                    CommandStatus.VALIDATION_ERROR
                )
            
            # Executar comando com timeout
            try:
                result = await asyncio.wait_for(
                    self._execute_handler(handler, request.arguments),
                    timeout=handler.timeout
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "status": CommandStatus.SUCCESS.value,
                            "data": result,
                            "execution_time": execution_time,
                            "command": request.name,
                        }, indent=2, ensure_ascii=False)
                    )]
                )
                
            except asyncio.TimeoutError:
                return self._create_error_result(
                    f"Timeout ao executar comando {request.name}",
                    CommandStatus.TIMEOUT
                )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error("Erro interno no processamento de comando",
                            command=request.name,
                            error=str(e),
                            traceback=traceback.format_exc())
            
            return self._create_error_result(
                f"Erro interno: {str(e)}",
                CommandStatus.INTERNAL_ERROR,
                execution_time
            )
    
    async def _validate_arguments(
        self, 
        request: CallToolRequest, 
        handler: CommandHandler
    ) -> CommandResult:
        """
        Valida argumentos do comando.
        
        Args:
            request: Requisição
            handler: Handler do comando
            
        Returns:
            Resultado da validação
        """
        try:
            schema = handler.schema
            
            # Verificar campos obrigatórios
            if "required" in schema:
                missing_fields = validate_required_fields(
                    request.arguments, 
                    schema["required"]
                )
                if missing_fields:
                    return CommandResult(
                        status=CommandStatus.VALIDATION_ERROR,
                        error=f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"
                    )
            
            # Verificar tipos de campos
            if "properties" in schema:
                type_errors = validate_field_types(
                    request.arguments,
                    schema["properties"]
                )
                if type_errors:
                    return CommandResult(
                        status=CommandStatus.VALIDATION_ERROR,
                        error=f"Erros de tipo: {', '.join(type_errors)}"
                    )
            
            return CommandResult(status=CommandStatus.SUCCESS)
            
        except Exception as e:
            return CommandResult(
                status=CommandStatus.VALIDATION_ERROR,
                error=f"Erro na validação: {str(e)}"
            )
    
    async def _execute_handler(
        self, 
        handler: CommandHandler, 
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Executa o handler do comando.
        
        Args:
            handler: Handler do comando
            arguments: Argumentos do comando
            
        Returns:
            Resultado da execução
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= handler.retry_count:
            try:
                if asyncio.iscoroutinefunction(handler.handler):
                    result = await handler.handler(arguments)
                else:
                    result = handler.handler(arguments)
                
                return result
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                if retry_count <= handler.retry_count:
                    self.logger.warning("Tentativa de comando falhou, tentando novamente",
                                      command=handler.name,
                                      attempt=retry_count,
                                      error=str(e))
                    await asyncio.sleep(1)  # Delay entre tentativas
                else:
                    raise e
        
        raise last_error
    
    def _create_error_result(
        self, 
        error_message: str, 
        status: CommandStatus,
        execution_time: float = 0.0
    ) -> CallToolResult:
        """
        Cria resultado de erro.
        
        Args:
            error_message: Mensagem de erro
            status: Status do erro
            execution_time: Tempo de execução
            
        Returns:
            Resultado de erro
        """
        error_data = {
            "status": status.value,
            "error": error_message,
            "execution_time": execution_time,
        }
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(error_data, indent=2, ensure_ascii=False)
            )]
        )
    
    def get_handler_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um handler.
        
        Args:
            name: Nome do handler
            
        Returns:
            Informações do handler ou None
        """
        if name not in self.handlers:
            return None
        
        handler = self.handlers[name]
        return {
            "name": handler.name,
            "description": handler.description,
            "schema": handler.schema,
            "timeout": handler.timeout,
            "retry_count": handler.retry_count,
        }
    
    def list_handlers(self) -> List[str]:
        """
        Lista todos os handlers registrados.
        
        Returns:
            Lista de nomes dos handlers
        """
        return list(self.handlers.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do processador.
        
        Returns:
            Status de saúde
        """
        return {
            "status": "healthy",
            "handlers_count": len(self.handlers),
            "middleware_count": len(self.middleware),
            "handlers": list(self.handlers.keys()),
        }


# Middleware de exemplo
async def logging_middleware(request: CallToolRequest, handler: CommandHandler):
    """Middleware de logging."""
    logger = get_logger(__name__)
    logger.info("Processando comando",
               command=request.name,
               arguments=request.arguments)


async def metrics_middleware(request: CallToolRequest, handler: CommandHandler):
    """Middleware de métricas."""
    # Implementar coleta de métricas
    pass


# Instância global do processador
command_processor = CommandProcessor()

# Registrar middleware padrão
command_processor.add_middleware(logging_middleware)
command_processor.add_middleware(metrics_middleware)
