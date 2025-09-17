#!/usr/bin/env python3
"""
Comandos CLI de Message

Comandos CLI para gerenciamento de mensagens RabbitMQ,
incluindo publicar, consumir, confirmar e rejeitar mensagens.

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

from mcp.tools.message_tools import (
    message_acknowledge,
    message_consume,
    message_publish,
    message_reject,
)

# from shared.utils.serialization import Serializer  # Não usado

console = Console()


@click.group(name="message", help="Comandos de gerenciamento de mensagens RabbitMQ")
def message_group():
    """Grupo de comandos para mensagens."""
    pass


@message_group.command(name="publish", help="Publicar mensagem em um exchange")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--exchange-name", "-e", required=True, help="Nome do exchange")
@click.option("--routing-key", "-r", required=True, help="Chave de roteamento")
@click.option("--message-body", "-b", required=True, help="Corpo da mensagem")
@click.option("--headers", "-h", help="Cabeçalhos da mensagem (JSON)")
@click.option("--priority", "-p", default=0, type=int, help="Prioridade da mensagem (0-255)")
@click.option("--content-type", default="application/json", help="Tipo de conteúdo")
@click.option("--persistent", is_flag=True, help="Mensagem persistente")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def publish_command(connection_id: str, exchange_name: str, routing_key: str,
                   message_body: str, headers: str | None, priority: int,
                   content_type: str, persistent: bool, output: str):
    """Publica uma mensagem em um exchange."""

    async def _publish():
        try:
            # Parsear cabeçalhos se fornecidos
            message_headers = {}
            if headers:
                try:
                    message_headers = json.loads(headers)
                except json.JSONDecodeError:
                    console.print("[bold red]❌ Cabeçalhos inválidos. Use formato JSON válido.")
                    return 1

            # Preparar parâmetros
            params = {
                "connection_id": connection_id,
                "exchange_name": exchange_name,
                "routing_key": routing_key,
                "message_body": message_body,
                "headers": message_headers,
                "priority": priority,
                "content_type": content_type,
                "persistent": persistent
            }

            # Mostrar progresso
            with console.status("[bold green]Publicando mensagem..."):
                result = message_publish(params)

            # Parsear resultado
            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                message_info = data.get("message_info", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print("✅ Mensagem publicada com sucesso")
                    console.print(f"   ID: {message_info.get('message_id', 'N/A')}")
                    console.print(f"   Exchange: {message_info.get('exchange_name', 'N/A')}")
                    console.print(f"   Routing Key: {message_info.get('routing_key', 'N/A')}")
                    console.print(f"   Timestamp: {message_info.get('published_at', 'N/A')}")
                else:  # table
                    _display_message_info(message_info)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao publicar mensagem: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_publish())
    if exit_code != 0:
        raise click.Abort()


@message_group.command(name="consume", help="Consumir mensagens de uma fila")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-q", required=True, help="Nome da fila")
@click.option("--count", "-n", default=1, type=int, help="Número de mensagens para consumir")
@click.option("--timeout", "-t", default=30, type=int, help="Timeout em segundos")
@click.option("--auto-ack", is_flag=True, help="Confirmação automática")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def consume_command(connection_id: str, queue_name: str, count: int,
                   timeout: int, auto_ack: bool, output: str):
    """Consome mensagens de uma fila."""

    async def _consume():
        try:
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name,
                "count": count,
                "timeout": timeout,
                "auto_ack": auto_ack
            }

            with console.status("[bold blue]Consumindo mensagens..."):
                result = message_consume(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                messages = data.get("messages", [])

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"📨 {len(messages)} mensagem(s) consumida(s)")
                    for i, msg in enumerate(messages, 1):
                        console.print(f"   {i}. ID: {msg.get('message_id', 'N/A')}")
                        console.print(f"      Body: {msg.get('body', 'N/A')[:100]}...")
                        console.print(f"      Delivery Tag: {msg.get('delivery_tag', 'N/A')}")
                else:  # table
                    _display_messages_list(messages)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao consumir mensagens: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_consume())
    if exit_code != 0:
        raise click.Abort()


@message_group.command(name="ack", help="Confirmar mensagem(s)")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--delivery-tags", "-t", required=True, help="Tags de entrega (separadas por vírgula)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def ack_command(connection_id: str, delivery_tags: str, output: str):
    """Confirma uma ou mais mensagens."""

    async def _ack():
        try:
            # Parsear tags de entrega
            try:
                tags = [int(tag.strip()) for tag in delivery_tags.split(",")]
            except ValueError:
                console.print("[bold red]❌ Tags de entrega devem ser números inteiros separados por vírgula.")
                return 1

            params = {
                "connection_id": connection_id,
                "delivery_tags": tags
            }

            with console.status("[bold green]Confirmando mensagens..."):
                result = message_acknowledge(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                acknowledged_count = data.get("acknowledged_count", 0)

                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ {acknowledged_count} mensagem(s) confirmada(s)")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao confirmar mensagens: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_ack())
    if exit_code != 0:
        raise click.Abort()


@message_group.command(name="reject", help="Rejeitar mensagem(s)")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--delivery-tags", "-t", required=True, help="Tags de entrega (separadas por vírgula)")
@click.option("--requeue", is_flag=True, help="Reenfileirar mensagem")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def reject_command(connection_id: str, delivery_tags: str, requeue: bool, output: str):
    """Rejeita uma ou mais mensagens."""

    async def _reject():
        try:
            # Parsear tags de entrega
            try:
                tags = [int(tag.strip()) for tag in delivery_tags.split(",")]
            except ValueError:
                console.print("[bold red]❌ Tags de entrega devem ser números inteiros separados por vírgula.")
                return 1

            params = {
                "connection_id": connection_id,
                "delivery_tags": tags,
                "requeue": requeue
            }

            with console.status("[bold yellow]Rejeitando mensagens..."):
                result = message_reject(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                rejected_count = data.get("rejected_count", 0)

                if output == "json":
                    console.print_json(result)
                else:
                    action = "reenfileirada(s)" if requeue else "rejeitada(s)"
                    console.print(f"❌ {rejected_count} mensagem(s) {action}")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao rejeitar mensagens: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_reject())
    if exit_code != 0:
        raise click.Abort()


def _display_message_info(message_info: dict[str, Any]) -> None:
    """Exibe informações da mensagem em formato de tabela."""
    table = Table(title="Informações da Mensagem", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    table.add_row("ID da Mensagem", message_info.get("message_id", "N/A"))
    table.add_row("Exchange", message_info.get("exchange_name", "N/A"))
    table.add_row("Routing Key", message_info.get("routing_key", "N/A"))
    table.add_row("Content Type", message_info.get("content_type", "N/A"))
    table.add_row("Prioridade", str(message_info.get("priority", 0)))
    table.add_row("Persistente", "Sim" if message_info.get("persistent") else "Não")
    table.add_row("Publicado em", message_info.get("published_at", "N/A"))

    # Cabeçalhos se existirem
    headers = message_info.get("headers", {})
    if headers:
        table.add_row("Cabeçalhos", json.dumps(headers, indent=2))

    console.print(table)


def _display_messages_list(messages: list) -> None:
    """Exibe lista de mensagens em formato de tabela."""
    if not messages:
        console.print(Panel("Nenhuma mensagem encontrada", title="Mensagens", border_style="yellow"))
        return

    table = Table(title="Mensagens Consumidas", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Exchange", style="green")
    table.add_column("Routing Key", style="blue")
    table.add_column("Content Type", style="magenta")
    table.add_column("Body (Preview)", style="yellow")
    table.add_column("Delivery Tag", style="red")

    for msg in messages:
        body_preview = msg.get("body", "")[:50] + "..." if len(msg.get("body", "")) > 50 else msg.get("body", "")

        table.add_row(
            msg.get("message_id", "N/A")[:8] + "...",
            msg.get("exchange", "N/A"),
            msg.get("routing_key", "N/A"),
            msg.get("content_type", "N/A"),
            body_preview,
            str(msg.get("delivery_tag", "N/A"))
        )

    console.print(table)

    # Resumo
    total_count = len(messages)
    summary = Text()
    summary.append(f"Total: {total_count} mensagem(s) consumida(s)", style="bold green")

    console.print(Panel(summary, title="Resumo", border_style="blue"))
