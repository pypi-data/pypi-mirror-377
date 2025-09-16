#!/usr/bin/env python3
"""
Comandos CLI de Queue

Comandos CLI para gerenciamento de filas RabbitMQ,
incluindo criar, deletar, listar e limpar filas.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

import asyncio
import json
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.mcp.tools.queue_tools import (
    queue_create, queue_delete, queue_list, queue_purge
)
from src.shared.utils.serialization import Serializer

console = Console()


@click.group(name="queue", help="Comandos de gerenciamento de filas RabbitMQ")
def queue_group():
    """Grupo de comandos para filas."""
    pass


@queue_group.command(name="create", help="Criar nova fila")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-n", required=True, help="Nome da fila a ser criada")
@click.option("--durable", is_flag=True, help="Fila sobrevive ao reinício do broker")
@click.option("--exclusive", is_flag=True, help="Fila é exclusiva da conexão")
@click.option("--auto-delete", is_flag=True, help="Fila é deletada quando não usada")
@click.option("--arguments", "-a", help="Argumentos adicionais da fila (JSON)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def create_command(connection_id: str, queue_name: str, durable: bool, 
                  exclusive: bool, auto_delete: bool, arguments: Optional[str], output: str):
    """Cria uma nova fila."""
    
    async def _create():
        try:
            # Parsear argumentos se fornecidos
            queue_arguments = {}
            if arguments:
                try:
                    queue_arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    console.print("[bold red]❌ Argumentos inválidos. Use formato JSON válido.")
                    return 1
            
            # Preparar parâmetros
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name,
                "durable": durable,
                "exclusive": exclusive,
                "auto_delete": auto_delete,
                "arguments": queue_arguments
            }
            
            # Mostrar progresso
            with console.status("[bold green]Criando fila..."):
                result = await queue_create(params)
            
            # Parsear resultado
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                queue_info = data.get("queue_info", {})
                
                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"✅ Fila '{queue_name}' criada com sucesso")
                    console.print(f"   Virtual Host: {queue_info.get('vhost', 'N/A')}")
                    console.print(f"   Durável: {'Sim' if queue_info.get('durable') else 'Não'}")
                    console.print(f"   Exclusiva: {'Sim' if queue_info.get('exclusive') else 'Não'}")
                    console.print(f"   Auto-delete: {'Sim' if queue_info.get('auto_delete') else 'Não'}")
                else:  # table
                    _display_queue_info(queue_info)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao criar fila: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_create())
    if exit_code != 0:
        raise click.Abort()


@queue_group.command(name="delete", help="Deletar fila existente")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-n", required=True, help="Nome da fila a ser deletada")
@click.option("--if-unused", is_flag=True, help="Deletar apenas se a fila não tiver consumidores")
@click.option("--if-empty", is_flag=True, help="Deletar apenas se a fila estiver vazia")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def delete_command(connection_id: str, queue_name: str, if_unused: bool, 
                  if_empty: bool, output: str):
    """Deleta uma fila existente."""
    
    async def _delete():
        try:
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name,
                "if_unused": if_unused,
                "if_empty": if_empty
            }
            
            with console.status("[bold yellow]Deletando fila..."):
                result = await queue_delete(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                messages_deleted = data.get("messages_deleted", 0)
                
                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Fila '{queue_name}' deletada com sucesso")
                    if messages_deleted > 0:
                        console.print(f"   Mensagens deletadas: {messages_deleted}")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao deletar fila: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_delete())
    if exit_code != 0:
        raise click.Abort()


@queue_group.command(name="list", help="Listar todas as filas")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--vhost", "-v", default="/", help="Virtual host para listar filas")
@click.option("--include-stats", "-s", is_flag=True, help="Incluir estatísticas das filas")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def list_command(connection_id: str, vhost: str, include_stats: bool, output: str):
    """Lista todas as filas."""
    
    async def _list():
        try:
            params = {
                "connection_id": connection_id,
                "vhost": vhost,
                "include_stats": include_stats
            }
            
            with console.status("[bold blue]Listando filas..."):
                result = await queue_list(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                queues = data.get("queues", [])
                stats = data.get("stats", {})
                
                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"📋 Total de filas: {data.get('total_count', 0)}")
                    console.print(f"🟢 Ativas: {data.get('active_count', 0)}")
                    console.print(f"📨 Total de mensagens: {data.get('total_messages', 0)}")
                    console.print(f"👥 Total de consumidores: {data.get('total_consumers', 0)}")
                    for queue in queues:
                        console.print(f"   📦 {queue.get('name', 'N/A')} - {queue.get('message_count', 0)} mensagens")
                else:  # table
                    _display_queues_list(queues, stats, include_stats, data)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao listar filas: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_list())
    if exit_code != 0:
        raise click.Abort()


@queue_group.command(name="purge", help="Limpar todas as mensagens de uma fila")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--queue-name", "-n", required=True, help="Nome da fila a ser limpa")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def purge_command(connection_id: str, queue_name: str, output: str):
    """Limpa todas as mensagens de uma fila."""
    
    async def _purge():
        try:
            params = {
                "connection_id": connection_id,
                "queue_name": queue_name
            }
            
            with console.status("[bold yellow]Limpando fila..."):
                result = await queue_purge(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                messages_purged = data.get("messages_purged", 0)
                
                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Fila '{queue_name}' limpa com sucesso")
                    console.print(f"   Mensagens removidas: {messages_purged}")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao limpar fila: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_purge())
    if exit_code != 0:
        raise click.Abort()


def _display_queue_info(queue_info: Dict[str, Any]) -> None:
    """Exibe informações da fila em formato de tabela."""
    table = Table(title="Informações da Fila", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")
    
    table.add_row("Nome", queue_info.get("name", "N/A"))
    table.add_row("Virtual Host", queue_info.get("vhost", "N/A"))
    table.add_row("Durável", "Sim" if queue_info.get("durable") else "Não")
    table.add_row("Exclusiva", "Sim" if queue_info.get("exclusive") else "Não")
    table.add_row("Auto-delete", "Sim" if queue_info.get("auto_delete") else "Não")
    table.add_row("Mensagens", str(queue_info.get("message_count", 0)))
    table.add_row("Consumidores", str(queue_info.get("consumer_count", 0)))
    table.add_row("Status", queue_info.get("status", "N/A"))
    table.add_row("Criada em", queue_info.get("created_at", "N/A"))
    table.add_row("Última atualização", queue_info.get("last_updated", "N/A"))
    
    # Argumentos se existirem
    arguments = queue_info.get("arguments", {})
    if arguments:
        table.add_row("Argumentos", json.dumps(arguments, indent=2))
    
    console.print(table)


def _display_queues_list(queues: list, stats: Dict[str, Any], include_stats: bool, data: Dict[str, Any]) -> None:
    """Exibe lista de filas em formato de tabela."""
    if not queues:
        console.print(Panel("Nenhuma fila encontrada", title="Filas", border_style="yellow"))
        return
    
    table = Table(title="Filas", box=box.ROUNDED)
    table.add_column("Nome", style="cyan", no_wrap=True)
    table.add_column("VHost", style="green")
    table.add_column("Durável", style="blue")
    table.add_column("Exclusiva", style="magenta")
    table.add_column("Auto-delete", style="red")
    table.add_column("Mensagens", style="yellow")
    table.add_column("Consumidores", style="green")
    table.add_column("Status", style="yellow")
    
    if include_stats:
        table.add_column("Mensagens/s", style="yellow")
        table.add_column("Memória", style="blue")
    
    for queue in queues:
        durable_icon = "✅" if queue.get("durable") else "❌"
        exclusive_icon = "✅" if queue.get("exclusive") else "❌"
        auto_delete_icon = "✅" if queue.get("auto_delete") else "❌"
        status_icon = "🟢" if queue.get("status") == "ACTIVE" else "🔴"
        
        row = [
            queue.get("name", "N/A"),
            queue.get("vhost", "N/A"),
            durable_icon,
            exclusive_icon,
            auto_delete_icon,
            str(queue.get("message_count", 0)),
            str(queue.get("consumer_count", 0)),
            f"{status_icon} {queue.get('status', 'N/A')}"
        ]
        
        if include_stats and queue.get("name") in stats:
            queue_stats = stats[queue.get("name")]
            row.extend([
                f"{queue_stats.get('messages_per_second', 0):.1f}",
                f"{queue_stats.get('memory_usage', 0)}B"
            ])
        
        table.add_row(*row)
    
    console.print(table)
    
    # Resumo
    total_count = data.get("total_count", 0)
    active_count = data.get("active_count", 0)
    total_messages = data.get("total_messages", 0)
    total_consumers = data.get("total_consumers", 0)
    
    summary = Text()
    summary.append(f"Total: {total_count} | ", style="bold")
    summary.append(f"Ativas: {active_count} | ", style="bold green")
    summary.append(f"Mensagens: {total_messages} | ", style="bold yellow")
    summary.append(f"Consumidores: {total_consumers}", style="bold blue")
    
    console.print(Panel(summary, title="Resumo", border_style="blue"))
