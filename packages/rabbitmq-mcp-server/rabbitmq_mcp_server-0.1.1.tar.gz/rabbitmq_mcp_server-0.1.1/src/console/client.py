#!/usr/bin/env python3
"""
RabbitMQ MCP Server - Console Client
Copyright (C) 2025 RabbitMQ MCP Server

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

Cliente Console RabbitMQ MCP Server

Interface de linha de comando para gerenciamento de RabbitMQ através do servidor MCP.
Fornece comandos para conexão, filas, mensagens, exchanges e monitoramento.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Importar comandos
from src.console.commands.connection_commands import connection_group
from src.console.commands.queue_commands import queue_group

# Configurar logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
console = Console()


class RabbitMQMCPClient:
    """Cliente principal para o servidor MCP RabbitMQ."""
    
    def __init__(self):
        self.console = Console()
        self.logger = logger
        
    def display_banner(self) -> None:
        """Exibe o banner de boas-vindas."""
        banner_text = Text()
        banner_text.append("🐰 RabbitMQ MCP Server Console\n", style="bold blue")
        banner_text.append("Gerenciamento completo de RabbitMQ via MCP\n", style="italic")
        banner_text.append("Versão 0.1.0", style="dim")
        
        panel = Panel(
            banner_text,
            title="[bold green]Bem-vindo[/bold green]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def display_help(self) -> None:
        """Exibe ajuda detalhada dos comandos disponíveis."""
        help_text = """
[bold]Comandos Disponíveis:[/bold]

[bold blue]Conexão:[/bold blue]
  connect     - Conectar ao servidor RabbitMQ
  disconnect  - Desconectar do servidor
  status      - Verificar status da conexão
  list        - Listar conexões ativas

[bold blue]Filas:[/bold blue]
  queue create    - Criar nova fila
  queue delete    - Deletar fila
  queue list      - Listar filas
  queue purge     - Limpar fila

[bold blue]Mensagens:[/bold blue]
  message publish   - Publicar mensagem
  message consume   - Consumir mensagens
  message ack       - Confirmar mensagem
  message reject    - Rejeitar mensagem

[bold blue]Exchanges:[/bold blue]
  exchange create   - Criar exchange
  exchange delete   - Deletar exchange
  exchange bind     - Vincular fila ao exchange
  exchange unbind   - Desvincular fila do exchange

[bold blue]Dead Letter Queues:[/bold blue]
  dlq configure     - Configurar DLQ
  dlq manage        - Gerenciar DLQ

[bold blue]Monitoramento:[/bold blue]
  monitor stats     - Estatísticas do sistema
  monitor health    - Health check

[bold blue]Utilitários:[/bold blue]
  help              - Exibir esta ajuda
  version           - Exibir versão
  config            - Configurações
        """
        
        panel = Panel(
            help_text,
            title="[bold green]Ajuda[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(panel)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Modo verboso')
@click.option('--config', '-c', type=click.Path(), help='Arquivo de configuração')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """Cliente Console RabbitMQ MCP Server.
    
    Interface de linha de comando para gerenciamento completo de RabbitMQ
    através do servidor MCP com ferramentas avançadas de filas, mensagens
    e monitoramento.
    """
    # Configurar contexto
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    ctx.obj['client'] = RabbitMQMCPClient()
    
    # Configurar logging baseado na verbosidade
    if verbose:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Exibir banner
    ctx.obj['client'].display_banner()


# Adicionar grupos de comandos
cli.add_command(connection_group)
cli.add_command(queue_group)


@cli.command()
def version() -> None:
    """Exibir versão do cliente."""
    console.print("[bold blue]RabbitMQ MCP Server Console[/bold blue]")
    console.print("Versão: [green]0.1.0[/green]")
    console.print("Python: [green]3.11+[/green]")
    console.print("Licença: [green]LGPL-3.0[/green]")


@cli.command()
@click.pass_context
def help(ctx: click.Context) -> None:
    """Exibir ajuda detalhada."""
    ctx.obj['client'].display_help()


@cli.command()
def info() -> None:
    """Exibir informações sobre o sistema."""
    info_text = Text()
    info_text.append("🐰 RabbitMQ MCP Console v0.1.0\n\n", style="bold green")
    info_text.append("Interface CLI moderna para gerenciamento de RabbitMQ\n", style="cyan")
    info_text.append("através do protocolo MCP (Model Context Protocol).\n\n", style="cyan")
    
    info_text.append("Comandos disponíveis:\n", style="bold yellow")
    info_text.append("  connection  - Gerenciar conexões RabbitMQ\n", style="green")
    info_text.append("  queue       - Gerenciar filas RabbitMQ\n", style="green")
    info_text.append("  message     - Gerenciar mensagens (em breve)\n", style="dim")
    info_text.append("  exchange    - Gerenciar exchanges (em breve)\n", style="dim")
    info_text.append("  monitor     - Monitoramento e estatísticas (em breve)\n", style="dim")
    
    info_text.append("\nExemplos:\n", style="bold yellow")
    info_text.append("  rabbitmq-mcp connection connect --host localhost --username guest --password guest\n", style="blue")
    info_text.append("  rabbitmq-mcp queue list --connection-id <id> --include-stats\n", style="blue")
    info_text.append("  rabbitmq-mcp queue create --connection-id <id> --queue-name my-queue --durable\n", style="blue")
    
    info_text.append("\nPara mais informações, use --help com qualquer comando.", style="italic")
    
    console.print(Panel(
        info_text,
        title="🐰 RabbitMQ MCP Console",
        border_style="green"
    ))


def main() -> None:
    """Função principal do cliente console."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
