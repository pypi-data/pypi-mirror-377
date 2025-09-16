"""
Cliente CLI para RabbitMQ MCP Server.

Este módulo implementa um cliente de linha de comando para interagir
com o servidor MCP RabbitMQ.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from src.mcp.server import RabbitMQMCPServer
from src.shared.utils.logging import get_logger


class RabbitMQCLIClient:
    """Cliente CLI para RabbitMQ MCP Server."""
    
    def __init__(self):
        """Inicializa o cliente CLI."""
        self.console = Console()
        self.server = RabbitMQMCPServer()
        self.logger = get_logger(__name__)
        self.connection_id: Optional[str] = None
        self.config_file = Path.home() / ".rabbitmq-mcp" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar configuração: {e}")
        
        return {
            "default_connection": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest",
                "virtual_host": "/",
                "ssl_enabled": False,
            },
            "output_format": "table",
            "auto_connect": False,
        }
    
    def _save_config(self):
        """Salva configuração no arquivo."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
    
    async def _execute_command(self, command: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um comando MCP.
        
        Args:
            command: Nome do comando
            arguments: Argumentos do comando
            
        Returns:
            Resultado do comando
        """
        from mcp.types import CallToolRequest
        
        request = CallToolRequest(name=command, arguments=arguments)
        result = await self.server._call_tool(request)
        
        if result.content:
            result_text = result.content[0].text
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                return {"raw_output": result_text}
        
        return {"error": "Nenhum resultado retornado"}
    
    def _display_result(self, result: Dict[str, Any], title: str = "Resultado"):
        """
        Exibe resultado formatado.
        
        Args:
            result: Resultado a ser exibido
            title: Título do painel
        """
        if "error" in result:
            self.console.print(Panel(
                f"[red]Erro: {result['error']}[/red]",
                title=title,
                border_style="red"
            ))
            return
        
        if "raw_output" in result:
            self.console.print(Panel(
                result["raw_output"],
                title=title,
                border_style="blue"
            ))
            return
        
        # Formatar como tabela se possível
        if isinstance(result.get("data"), list) and result["data"]:
            self._display_table(result["data"], title)
        elif isinstance(result.get("data"), dict):
            self._display_dict(result["data"], title)
        else:
            self.console.print(Panel(
                json.dumps(result, indent=2, ensure_ascii=False),
                title=title,
                border_style="green"
            ))
    
    def _display_table(self, data: List[Dict[str, Any]], title: str):
        """Exibe dados como tabela."""
        if not data:
            self.console.print(f"[yellow]Nenhum dado encontrado para {title}[/yellow]")
            return
        
        table = Table(title=title)
        
        # Adicionar colunas baseadas nas chaves do primeiro item
        first_item = data[0]
        for key in first_item.keys():
            table.add_column(key, style="cyan")
        
        # Adicionar linhas
        for item in data:
            row = [str(item.get(key, "")) for key in first_item.keys()]
            table.add_row(*row)
        
        self.console.print(table)
    
    def _display_dict(self, data: Dict[str, Any], title: str):
        """Exibe dicionário formatado."""
        table = Table(title=title)
        table.add_column("Propriedade", style="cyan")
        table.add_column("Valor", style="green")
        
        for key, value in data.items():
            table.add_row(key, str(value))
        
        self.console.print(table)
    
    async def connect(self, **kwargs) -> bool:
        """
        Conecta ao RabbitMQ.
        
        Args:
            **kwargs: Parâmetros de conexão
            
        Returns:
            True se conectado com sucesso
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Conectando ao RabbitMQ...", total=None)
                
                result = await self._execute_command("connection_connect", kwargs)
                
                if "error" in result:
                    self.console.print(f"[red]Erro na conexão: {result['error']}[/red]")
                    return False
                
                # Extrair connection_id do resultado
                if "data" in result and isinstance(result["data"], dict):
                    self.connection_id = result["data"].get("connection_id")
                
                progress.update(task, description="Conectado com sucesso!")
                return True
                
        except Exception as e:
            self.console.print(f"[red]Erro na conexão: {e}[/red]")
            return False
    
    async def disconnect(self) -> bool:
        """
        Desconecta do RabbitMQ.
        
        Returns:
            True se desconectado com sucesso
        """
        if not self.connection_id:
            self.console.print("[yellow]Nenhuma conexão ativa[/yellow]")
            return False
        
        try:
            result = await self._execute_command("connection_disconnect", {
                "connection_id": self.connection_id
            })
            
            if "error" in result:
                self.console.print(f"[red]Erro na desconexão: {result['error']}[/red]")
                return False
            
            self.connection_id = None
            self.console.print("[green]Desconectado com sucesso[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Erro na desconexão: {e}[/red]")
            return False
    
    async def list_connections(self):
        """Lista conexões ativas."""
        result = await self._execute_command("connection_list", {
            "include_stats": True
        })
        self._display_result(result, "Conexões Ativas")
    
    async def create_queue(self, name: str, **kwargs):
        """
        Cria uma fila.
        
        Args:
            name: Nome da fila
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "queue_name": name,
            **kwargs
        }
        
        result = await self._execute_command("queue_create", arguments)
        self._display_result(result, f"Fila '{name}' Criada")
    
    async def list_queues(self):
        """Lista filas."""
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        result = await self._execute_command("queue_list", {
            "connection_id": self.connection_id,
            "include_stats": True
        })
        self._display_result(result, "Filas")
    
    async def delete_queue(self, name: str, **kwargs):
        """
        Deleta uma fila.
        
        Args:
            name: Nome da fila
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "queue_name": name,
            **kwargs
        }
        
        result = await self._execute_command("queue_delete", arguments)
        self._display_result(result, f"Fila '{name}' Deletada")
    
    async def publish_message(self, exchange: str, routing_key: str, body: str, **kwargs):
        """
        Publica uma mensagem.
        
        Args:
            exchange: Nome do exchange
            routing_key: Chave de roteamento
            body: Corpo da mensagem
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "exchange_name": exchange,
            "routing_key": routing_key,
            "message_body": body,
            **kwargs
        }
        
        result = await self._execute_command("message_publish", arguments)
        self._display_result(result, "Mensagem Publicada")
    
    async def consume_messages(self, queue: str, count: int = 1, **kwargs):
        """
        Consome mensagens de uma fila.
        
        Args:
            queue: Nome da fila
            count: Número de mensagens
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "queue_name": queue,
            "count": count,
            **kwargs
        }
        
        result = await self._execute_command("message_consume", arguments)
        self._display_result(result, f"Mensagens da Fila '{queue}'")
    
    async def create_exchange(self, name: str, exchange_type: str, **kwargs):
        """
        Cria um exchange.
        
        Args:
            name: Nome do exchange
            exchange_type: Tipo do exchange
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "exchange_name": name,
            "exchange_type": exchange_type,
            **kwargs
        }
        
        result = await self._execute_command("exchange_create", arguments)
        self._display_result(result, f"Exchange '{name}' Criado")
    
    async def bind_queue(self, exchange: str, queue: str, routing_key: str, **kwargs):
        """
        Faz bind de uma fila a um exchange.
        
        Args:
            exchange: Nome do exchange
            queue: Nome da fila
            routing_key: Chave de roteamento
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "exchange_name": exchange,
            "queue_name": queue,
            "routing_key": routing_key,
            **kwargs
        }
        
        result = await self._execute_command("exchange_bind", arguments)
        self._display_result(result, f"Bind '{queue}' -> '{exchange}'")
    
    async def get_stats(self, resource_type: str = "all", **kwargs):
        """
        Obtém estatísticas.
        
        Args:
            resource_type: Tipo de recurso
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "resource_type": resource_type,
            **kwargs
        }
        
        result = await self._execute_command("monitor_stats", arguments)
        self._display_result(result, f"Estatísticas - {resource_type}")
    
    async def health_check(self, check_type: str = "all", **kwargs):
        """
        Verifica saúde do sistema.
        
        Args:
            check_type: Tipo de verificação
            **kwargs: Parâmetros adicionais
        """
        if not self.connection_id:
            self.console.print("[red]Nenhuma conexão ativa. Use 'connect' primeiro.[/red]")
            return
        
        arguments = {
            "connection_id": self.connection_id,
            "check_type": check_type,
            **kwargs
        }
        
        result = await self._execute_command("monitor_health", arguments)
        self._display_result(result, f"Verificação de Saúde - {check_type}")
    
    async def interactive_mode(self):
        """Modo interativo do CLI."""
        self.console.print(Panel(
            "[bold blue]RabbitMQ MCP CLI[/bold blue]\n"
            "Digite 'help' para ver comandos disponíveis\n"
            "Digite 'exit' para sair",
            title="Bem-vindo",
            border_style="blue"
        ))
        
        # Conectar automaticamente se configurado
        if self.config.get("auto_connect", False):
            default_conn = self.config.get("default_connection", {})
            if default_conn:
                await self.connect(**default_conn)
        
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]rabbitmq-mcp[/bold cyan]")
                
                if command.lower() in ['exit', 'quit', 'q']:
                    if self.connection_id:
                        await self.disconnect()
                    break
                
                await self._handle_command(command)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' para sair[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Erro: {e}[/red]")
    
    async def _handle_command(self, command: str):
        """Processa comando interativo."""
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "help":
            self._show_help()
        elif cmd == "connect":
            await self._handle_connect(args)
        elif cmd == "disconnect":
            await self.disconnect()
        elif cmd == "connections":
            await self.list_connections()
        elif cmd == "queue":
            await self._handle_queue_command(args)
        elif cmd == "publish":
            await self._handle_publish_command(args)
        elif cmd == "consume":
            await self._handle_consume_command(args)
        elif cmd == "exchange":
            await self._handle_exchange_command(args)
        elif cmd == "bind":
            await self._handle_bind_command(args)
        elif cmd == "stats":
            await self._handle_stats_command(args)
        elif cmd == "health":
            await self._handle_health_command(args)
        elif cmd == "config":
            await self._handle_config_command(args)
        else:
            self.console.print(f"[red]Comando desconhecido: {cmd}[/red]")
            self.console.print("[yellow]Digite 'help' para ver comandos disponíveis[/yellow]")
    
    def _show_help(self):
        """Exibe ajuda dos comandos."""
        help_text = """
[bold]Comandos Disponíveis:[/bold]

[cyan]Conexão:[/cyan]
  connect [host] [port] [username] [password]  - Conecta ao RabbitMQ
  disconnect                                   - Desconecta
  connections                                  - Lista conexões

[cyan]Filas:[/cyan]
  queue create <nome> [--durable] [--exclusive]  - Cria fila
  queue list                                     - Lista filas
  queue delete <nome> [--if-unused] [--if-empty] - Deleta fila

[cyan]Mensagens:[/cyan]
  publish <exchange> <routing_key> <body>     - Publica mensagem
  consume <queue> [count]                     - Consome mensagens

[cyan]Exchanges:[/cyan]
  exchange create <nome> <tipo> [--durable]   - Cria exchange
  bind <exchange> <queue> <routing_key>       - Faz bind

[cyan]Monitoramento:[/cyan]
  stats [type]                                - Estatísticas
  health [type]                               - Verificação de saúde

[cyan]Configuração:[/cyan]
  config show                                 - Mostra configuração
  config set <key> <value>                    - Define configuração

[cyan]Outros:[/cyan]
  help                                        - Mostra esta ajuda
  exit                                        - Sai do programa
        """
        
        self.console.print(Panel(help_text, title="Ajuda", border_style="green"))
    
    async def _handle_connect(self, args: List[str]):
        """Processa comando connect."""
        if len(args) >= 4:
            host, port, username, password = args[0], int(args[1]), args[2], args[3]
            virtual_host = args[4] if len(args) > 4 else "/"
            
            await self.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                virtual_host=virtual_host
            )
        else:
            # Usar configuração padrão
            default_conn = self.config.get("default_connection", {})
            await self.connect(**default_conn)
    
    async def _handle_queue_command(self, args: List[str]):
        """Processa comandos de fila."""
        if len(args) < 2:
            self.console.print("[red]Uso: queue <create|list|delete> [args][/red]")
            return
        
        subcmd = args[0].lower()
        
        if subcmd == "create":
            if len(args) < 2:
                self.console.print("[red]Uso: queue create <nome>[/red]")
                return
            
            name = args[1]
            kwargs = {}
            
            # Processar flags
            for i in range(2, len(args)):
                if args[i] == "--durable":
                    kwargs["durable"] = True
                elif args[i] == "--exclusive":
                    kwargs["exclusive"] = True
            
            await self.create_queue(name, **kwargs)
            
        elif subcmd == "list":
            await self.list_queues()
            
        elif subcmd == "delete":
            if len(args) < 2:
                self.console.print("[red]Uso: queue delete <nome>[/red]")
                return
            
            name = args[1]
            kwargs = {}
            
            # Processar flags
            for i in range(2, len(args)):
                if args[i] == "--if-unused":
                    kwargs["if_unused"] = True
                elif args[i] == "--if-empty":
                    kwargs["if_empty"] = True
            
            await self.delete_queue(name, **kwargs)
        
        else:
            self.console.print(f"[red]Subcomando desconhecido: {subcmd}[/red]")
    
    async def _handle_publish_command(self, args: List[str]):
        """Processa comando publish."""
        if len(args) < 3:
            self.console.print("[red]Uso: publish <exchange> <routing_key> <body>[/red]")
            return
        
        exchange, routing_key, body = args[0], args[1], " ".join(args[2:])
        await self.publish_message(exchange, routing_key, body)
    
    async def _handle_consume_command(self, args: List[str]):
        """Processa comando consume."""
        if len(args) < 1:
            self.console.print("[red]Uso: consume <queue> [count][/red]")
            return
        
        queue = args[0]
        count = int(args[1]) if len(args) > 1 else 1
        await self.consume_messages(queue, count)
    
    async def _handle_exchange_command(self, args: List[str]):
        """Processa comandos de exchange."""
        if len(args) < 3:
            self.console.print("[red]Uso: exchange create <nome> <tipo>[/red]")
            return
        
        if args[0].lower() == "create":
            name, exchange_type = args[1], args[2]
            kwargs = {}
            
            # Processar flags
            for i in range(3, len(args)):
                if args[i] == "--durable":
                    kwargs["durable"] = True
            
            await self.create_exchange(name, exchange_type, **kwargs)
        else:
            self.console.print(f"[red]Subcomando desconhecido: {args[0]}[/red]")
    
    async def _handle_bind_command(self, args: List[str]):
        """Processa comando bind."""
        if len(args) < 3:
            self.console.print("[red]Uso: bind <exchange> <queue> <routing_key>[/red]")
            return
        
        exchange, queue, routing_key = args[0], args[1], args[2]
        await self.bind_queue(exchange, queue, routing_key)
    
    async def _handle_stats_command(self, args: List[str]):
        """Processa comando stats."""
        resource_type = args[0] if args else "all"
        await self.get_stats(resource_type)
    
    async def _handle_health_command(self, args: List[str]):
        """Processa comando health."""
        check_type = args[0] if args else "all"
        await self.health_check(check_type)
    
    async def _handle_config_command(self, args: List[str]):
        """Processa comandos de configuração."""
        if not args:
            self.console.print("[red]Uso: config <show|set> [args][/red]")
            return
        
        subcmd = args[0].lower()
        
        if subcmd == "show":
            self._display_dict(self.config, "Configuração")
            
        elif subcmd == "set":
            if len(args) < 3:
                self.console.print("[red]Uso: config set <key> <value>[/red]")
                return
            
            key, value = args[1], args[2]
            
            # Tentar converter valor
            try:
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
            except ValueError:
                pass  # Manter como string
            
            self.config[key] = value
            self._save_config()
            self.console.print(f"[green]Configuração '{key}' definida como '{value}'[/green]")
        
        else:
            self.console.print(f"[red]Subcomando desconhecido: {subcmd}[/red]")


# Instância global do cliente
cli_client = RabbitMQCLIClient()
