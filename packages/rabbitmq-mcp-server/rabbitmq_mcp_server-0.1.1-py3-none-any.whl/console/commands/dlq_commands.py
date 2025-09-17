#!/usr/bin/env python3
"""
Comandos CLI de DLQ (Dead Letter Queue)

Comandos CLI para gerenciamento de Dead Letter Queues RabbitMQ,
incluindo configurar e gerenciar DLQs.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

import asyncio
import json
from typing import Any

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mcp.tools.dlq_tools import dlq_configure, dlq_manage

# from shared.utils.serialization import Serializer  # Não usado

console = Console()


@click.group(name="dlq", help="Comandos de gerenciamento de Dead Letter Queues RabbitMQ")
def dlq_group():
    """Grupo de comandos para DLQs."""
    pass


@dlq_group.command(name="configure", help="Configurar Dead Letter Queue")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-q", required=True, help="Nome da fila principal")
@click.option("--dlq-name", "-d", required=True, help="Nome da fila de dead letter")
@click.option("--dlq-exchange", "-e", required=True, help="Nome do exchange de dead letter")
@click.option("--routing-key", "-r", default="failed", help="Chave de roteamento para DLQ")
@click.option("--ttl", default=3600000, type=int, help="Tempo de vida da mensagem em milissegundos")
@click.option("--max-retries", default=3, type=int, help="Número máximo de tentativas")
@click.option("--retry-delay", default=5000, type=int, help="Delay entre tentativas em milissegundos")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def configure_command(connection_id: str, queue_name: str, dlq_name: str,
                     dlq_exchange: str, routing_key: str, ttl: int,
                     max_retries: int, retry_delay: int, output: str):
    """Configura uma Dead Letter Queue."""

    async def _configure():
        try:
            # Preparar parâmetros
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name,
                "dlq_name": dlq_name,
                "dlq_exchange": dlq_exchange,
                "routing_key": routing_key,
                "ttl": ttl,
                "max_retries": max_retries,
                "retry_delay": retry_delay
            }

            # Mostrar progresso
            with console.status("[bold green]Configurando Dead Letter Queue..."):
                result = dlq_configure(params)

            # Parsear resultado
            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                dlq_info = data.get("dlq_info", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print("✅ Dead Letter Queue configurada com sucesso")
                    console.print(f"   Fila Principal: {dlq_info.get('queue_name', 'N/A')}")
                    console.print(f"   DLQ: {dlq_info.get('dlq_name', 'N/A')}")
                    console.print(f"   Exchange DLQ: {dlq_info.get('dlq_exchange', 'N/A')}")
                    console.print(f"   Routing Key: {dlq_info.get('routing_key', 'N/A')}")
                    console.print(f"   TTL: {dlq_info.get('ttl', 0)}ms")
                    console.print(f"   Max Retries: {dlq_info.get('max_retries', 0)}")
                else:  # table
                    _display_dlq_info(dlq_info)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao configurar DLQ: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_configure())
    if exit_code != 0:
        raise click.Abort()


@dlq_group.command(name="manage", help="Gerenciar Dead Letter Queue")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-q", required=True, help="Nome da fila principal")
@click.option("--action", "-a", required=True,
              type=click.Choice(["list", "purge", "retry", "stats"]),
              help="Ação a ser executada")
@click.option("--count", "-n", default=10, type=int, help="Número de mensagens para listar/retry")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def manage_command(connection_id: str, queue_name: str, action: str,
                  count: int, output: str):
    """Gerencia uma Dead Letter Queue."""

    async def _manage():
        try:
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name,
                "action": action,
                "count": count
            }

            action_text = {
                "list": "Listando mensagens da DLQ",
                "purge": "Limpando DLQ",
                "retry": "Reenviando mensagens da DLQ",
                "stats": "Obtendo estatísticas da DLQ"
            }

            with console.status(f"[bold blue]{action_text.get(action, 'Processando')}..."):
                result = dlq_manage(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    if action == "list":
                        messages = data.get("messages", [])
                        console.print(f"📋 {len(messages)} mensagem(s) na DLQ")
                        for i, msg in enumerate(messages, 1):
                            console.print(f"   {i}. ID: {msg.get('message_id', 'N/A')}")
                            console.print(f"      Body: {msg.get('body', 'N/A')[:100]}...")
                            console.print(f"      Erro: {msg.get('error_reason', 'N/A')}")
                    elif action == "purge":
                        purged_count = data.get("purged_count", 0)
                        console.print(f"✅ {purged_count} mensagem(s) removida(s) da DLQ")
                    elif action == "retry":
                        retried_count = data.get("retried_count", 0)
                        console.print(f"🔄 {retried_count} mensagem(s) reenviada(s) para processamento")
                    elif action == "stats":
                        stats = data.get("stats", {})
                        console.print("📊 Estatísticas da DLQ:")
                        console.print(f"   Total de mensagens: {stats.get('total_messages', 0)}")
                        console.print(f"   Mensagens processadas: {stats.get('processed_messages', 0)}")
                        console.print(f"   Taxa de erro: {stats.get('error_rate', 0):.2%}")
                else:  # table
                    if action == "list":
                        _display_dlq_messages(data.get("messages", []))
                    elif action == "stats":
                        _display_dlq_stats(data.get("stats", {}))
                    else:
                        console.print(f"✅ Ação '{action}' executada com sucesso")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao gerenciar DLQ: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_manage())
    if exit_code != 0:
        raise click.Abort()


def _display_dlq_info(dlq_info: dict[str, Any]) -> None:
    """Exibe informações da DLQ em formato de tabela."""
    table = Table(title="Informações da Dead Letter Queue", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    table.add_row("Fila Principal", dlq_info.get("queue_name", "N/A"))
    table.add_row("DLQ", dlq_info.get("dlq_name", "N/A"))
    table.add_row("Exchange DLQ", dlq_info.get("dlq_exchange", "N/A"))
    table.add_row("Routing Key", dlq_info.get("routing_key", "N/A"))
    table.add_row("TTL", f"{dlq_info.get('ttl', 0)}ms")
    table.add_row("Max Retries", str(dlq_info.get("max_retries", 0)))
    table.add_row("Retry Delay", f"{dlq_info.get('retry_delay', 0)}ms")
    table.add_row("Virtual Host", dlq_info.get("vhost", "N/A"))
    table.add_row("Status", dlq_info.get("status", "N/A"))
    table.add_row("Criado em", dlq_info.get("created_at", "N/A"))

    console.print(table)


def _display_dlq_messages(messages: list) -> None:
    """Exibe lista de mensagens da DLQ em formato de tabela."""
    if not messages:
        console.print(Panel("Nenhuma mensagem encontrada na DLQ", title="DLQ Messages", border_style="yellow"))
        return

    table = Table(title="Mensagens na Dead Letter Queue", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Exchange", style="green")
    table.add_column("Routing Key", style="blue")
    table.add_column("Body (Preview)", style="yellow")
    table.add_column("Erro", style="red")
    table.add_column("Tentativas", style="magenta")
    table.add_column("Timestamp", style="dim")

    for msg in messages:
        body_preview = msg.get("body", "")[:30] + "..." if len(msg.get("body", "")) > 30 else msg.get("body", "")

        table.add_row(
            msg.get("message_id", "N/A")[:8] + "...",
            msg.get("exchange", "N/A"),
            msg.get("routing_key", "N/A"),
            body_preview,
            msg.get("error_reason", "N/A")[:20] + "..." if len(msg.get("error_reason", "")) > 20 else msg.get("error_reason", "N/A"),
            str(msg.get("retry_count", 0)),
            msg.get("timestamp", "N/A")
        )

    console.print(table)

    # Resumo
    total_count = len(messages)
    summary = Text()
    summary.append(f"Total: {total_count} mensagem(s) na DLQ", style="bold red")

    console.print(Panel(summary, title="Resumo", border_style="red"))


def _display_dlq_stats(stats: dict[str, Any]) -> None:
    """Exibe estatísticas da DLQ em formato de tabela."""
    table = Table(title="Estatísticas da Dead Letter Queue", box=box.ROUNDED)
    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    table.add_row("Total de Mensagens", str(stats.get("total_messages", 0)))
    table.add_row("Mensagens Processadas", str(stats.get("processed_messages", 0)))
    table.add_row("Mensagens com Erro", str(stats.get("error_messages", 0)))
    table.add_row("Taxa de Erro", f"{stats.get('error_rate', 0):.2%}")
    table.add_row("Mensagens Reenviadas", str(stats.get("retried_messages", 0)))
    table.add_row("Última Atividade", stats.get("last_activity", "N/A"))

    console.print(table)
