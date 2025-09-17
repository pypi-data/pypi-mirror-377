#!/usr/bin/env python3
"""
Comandos CLI de Exchange

Comandos CLI para gerenciamento de exchanges RabbitMQ,
incluindo criar, deletar, vincular e desvincular exchanges.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

import asyncio
import json
from typing import Any

import click
from rich import box
from rich.console import Console
from rich.table import Table

from mcp.tools.exchange_tools import (
    exchange_bind,
    exchange_create,
    exchange_delete,
    exchange_unbind,
)

# from shared.utils.serialization import Serializer  # Não usado

console = Console()


@click.group(name="exchange", help="Comandos de gerenciamento de exchanges RabbitMQ")
def exchange_group():
    """Grupo de comandos para exchanges."""
    pass


@exchange_group.command(name="create", help="Criar novo exchange")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--exchange-name", "-n", required=True, help="Nome do exchange")
@click.option("--exchange-type", "-t", required=True,
              type=click.Choice(["direct", "topic", "fanout", "headers"]),
              help="Tipo do exchange")
@click.option("--durable", is_flag=True, help="Exchange sobrevive ao reinício do broker")
@click.option("--auto-delete", is_flag=True, help="Exchange é deletado quando não usado")
@click.option("--internal", is_flag=True, help="Exchange é interno")
@click.option("--arguments", "-a", help="Argumentos adicionais do exchange (JSON)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def create_command(connection_id: str, exchange_name: str, exchange_type: str,
                  durable: bool, auto_delete: bool, internal: bool,
                  arguments: str | None, output: str):
    """Cria um novo exchange."""

    async def _create():
        try:
            # Parsear argumentos se fornecidos
            exchange_arguments = {}
            if arguments:
                try:
                    exchange_arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    console.print("[bold red]❌ Argumentos inválidos. Use formato JSON válido.")
                    return 1

            # Preparar parâmetros
            params = {
                "connection_id": connection_id,
                "exchange_name": exchange_name,
                "exchange_type": exchange_type,
                "durable": durable,
                "auto_delete": auto_delete,
                "internal": internal,
                "arguments": exchange_arguments
            }

            # Mostrar progresso
            with console.status("[bold green]Criando exchange..."):
                result = exchange_create(params)

            # Parsear resultado
            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                exchange_info = data.get("exchange_info", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"✅ Exchange '{exchange_name}' criado com sucesso")
                    console.print(f"   Tipo: {exchange_info.get('type', 'N/A')}")
                    console.print(f"   Virtual Host: {exchange_info.get('vhost', 'N/A')}")
                    console.print(f"   Durável: {'Sim' if exchange_info.get('durable') else 'Não'}")
                    console.print(f"   Auto-delete: {'Sim' if exchange_info.get('auto_delete') else 'Não'}")
                    console.print(f"   Interno: {'Sim' if exchange_info.get('internal') else 'Não'}")
                else:  # table
                    _display_exchange_info(exchange_info)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao criar exchange: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_create())
    if exit_code != 0:
        raise click.Abort()


@exchange_group.command(name="delete", help="Deletar exchange existente")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--exchange-name", "-n", required=True, help="Nome do exchange a ser deletado")
@click.option("--if-unused", is_flag=True, help="Deletar apenas se o exchange não tiver bindings")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def delete_command(connection_id: str, exchange_name: str, if_unused: bool, output: str):
    """Deleta um exchange existente."""

    async def _delete():
        try:
            params = {
                "connection_id": connection_id,
                "exchange_name": exchange_name,
                "if_unused": if_unused
            }

            with console.status("[bold yellow]Deletando exchange..."):
                result = exchange_delete(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Exchange '{exchange_name}' deletado com sucesso")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao deletar exchange: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_delete())
    if exit_code != 0:
        raise click.Abort()


@exchange_group.command(name="bind", help="Vincular fila ao exchange")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--exchange-name", "-e", required=True, help="Nome do exchange")
@click.option("--queue-name", "-q", required=True, help="Nome da fila")
@click.option("--routing-key", "-r", default="", help="Chave de roteamento")
@click.option("--arguments", "-a", help="Argumentos do binding (JSON)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def bind_command(connection_id: str, exchange_name: str, queue_name: str,
                routing_key: str, arguments: str | None, output: str):
    """Vincula uma fila a um exchange."""

    async def _bind():
        try:
            # Parsear argumentos se fornecidos
            binding_arguments = {}
            if arguments:
                try:
                    binding_arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    console.print("[bold red]❌ Argumentos inválidos. Use formato JSON válido.")
                    return 1

            params = {
                "connection_id": connection_id,
                "exchange_name": exchange_name,
                "queue_name": queue_name,
                "routing_key": routing_key,
                "arguments": binding_arguments
            }

            with console.status("[bold blue]Vinculando fila ao exchange..."):
                result = exchange_bind(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                binding_info = data.get("binding_info", {})

                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Fila '{queue_name}' vinculada ao exchange '{exchange_name}'")
                    console.print(f"   Routing Key: {binding_info.get('routing_key', 'N/A')}")
                    console.print(f"   Virtual Host: {binding_info.get('vhost', 'N/A')}")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao vincular fila: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_bind())
    if exit_code != 0:
        raise click.Abort()


@exchange_group.command(name="unbind", help="Desvincular fila do exchange")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--exchange-name", "-e", required=True, help="Nome do exchange")
@click.option("--queue-name", "-q", required=True, help="Nome da fila")
@click.option("--routing-key", "-r", default="", help="Chave de roteamento")
@click.option("--arguments", "-a", help="Argumentos do binding (JSON)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def unbind_command(connection_id: str, exchange_name: str, queue_name: str,
                  routing_key: str, arguments: str | None, output: str):
    """Desvincula uma fila de um exchange."""

    async def _unbind():
        try:
            # Parsear argumentos se fornecidos
            binding_arguments = {}
            if arguments:
                try:
                    binding_arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    console.print("[bold red]❌ Argumentos inválidos. Use formato JSON válido.")
                    return 1

            params = {
                "connection_id": connection_id,
                "exchange_name": exchange_name,
                "queue_name": queue_name,
                "routing_key": routing_key,
                "arguments": binding_arguments
            }

            with console.status("[bold yellow]Desvinculando fila do exchange..."):
                result = exchange_unbind(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Fila '{queue_name}' desvinculada do exchange '{exchange_name}'")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao desvincular fila: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_unbind())
    if exit_code != 0:
        raise click.Abort()


def _display_exchange_info(exchange_info: dict[str, Any]) -> None:
    """Exibe informações do exchange em formato de tabela."""
    table = Table(title="Informações do Exchange", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    table.add_row("Nome", exchange_info.get("name", "N/A"))
    table.add_row("Tipo", exchange_info.get("type", "N/A"))
    table.add_row("Virtual Host", exchange_info.get("vhost", "N/A"))
    table.add_row("Durável", "Sim" if exchange_info.get("durable") else "Não")
    table.add_row("Auto-delete", "Sim" if exchange_info.get("auto_delete") else "Não")
    table.add_row("Interno", "Sim" if exchange_info.get("internal") else "Não")
    table.add_row("Status", exchange_info.get("status", "N/A"))
    table.add_row("Criado em", exchange_info.get("created_at", "N/A"))
    table.add_row("Última atualização", exchange_info.get("last_updated", "N/A"))

    # Argumentos se existirem
    arguments = exchange_info.get("arguments", {})
    if arguments:
        table.add_row("Argumentos", json.dumps(arguments, indent=2))

    console.print(table)
