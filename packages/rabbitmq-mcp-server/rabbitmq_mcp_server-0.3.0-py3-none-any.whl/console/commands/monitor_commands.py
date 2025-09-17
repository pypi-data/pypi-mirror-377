#!/usr/bin/env python3
"""
Comandos CLI de Monitor

Comandos CLI para monitoramento de RabbitMQ,
incluindo estatísticas e health checks.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

import asyncio
import json
import time
from typing import Any

import click
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from mcp.tools.monitor_tools import monitor_health, monitor_stats

# from shared.utils.serialization import Serializer  # Não usado

console = Console()


@click.group(name="monitor", help="Comandos de monitoramento RabbitMQ")
def monitor_group():
    """Grupo de comandos para monitoramento."""
    pass


@monitor_group.command(name="stats", help="Obter estatísticas do RabbitMQ")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def stats_command(connection_id: str, output: str):
    """Obtém estatísticas detalhadas do RabbitMQ."""

    async def _stats():
        try:
            params = {
                "connection_id": connection_id
            }

            with console.status("[bold green]Obtendo estatísticas do RabbitMQ..."):
                result = monitor_stats(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                stats = data.get("stats", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    _display_stats_text(stats)
                else:  # table
                    _display_stats_table(stats)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao obter estatísticas: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_stats())
    if exit_code != 0:
        raise click.Abort()


@monitor_group.command(name="health", help="Verificar saúde do RabbitMQ")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def health_command(connection_id: str, output: str):
    """Verifica a saúde do RabbitMQ."""

    async def _health():
        try:
            params = {
                "connection_id": connection_id
            }

            with console.status("[bold green]Verificando saúde do RabbitMQ..."):
                result = monitor_health(params)

            result_data = json.loads(result)

            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                health = data.get("health", {})

                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    _display_health_text(health)
                else:  # table
                    _display_health_table(health)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao verificar saúde: {error_msg}")
                return 1

        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_health())
    if exit_code != 0:
        raise click.Abort()


@monitor_group.command(name="watch", help="Monitoramento em tempo real")
@click.option("--connection-id", "-c", required=True, help="ID da conexão RabbitMQ")
@click.option("--interval", "-i", default=5, type=int, help="Intervalo de atualização em segundos")
@click.option("--duration", "-d", default=60, type=int, help="Duração do monitoramento em segundos")
def watch_command(connection_id: str, interval: int, duration: int):
    """Monitoramento em tempo real do RabbitMQ."""

    async def _watch():
        try:
            start_time = time.time()
            end_time = start_time + duration

            def create_layout():
                layout = Layout()
                layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="main", ratio=1),
                    Layout(name="footer", size=3)
                )
                layout["main"].split_row(
                    Layout(name="stats", ratio=1),
                    Layout(name="health", ratio=1)
                )
                return layout

            with Live(create_layout(), refresh_per_second=1, screen=True) as live:
                while time.time() < end_time:
                    # Atualizar header
                    elapsed = int(time.time() - start_time)
                    remaining = int(end_time - time.time())
                    live.layout["header"].update(
                        Panel(
                            f"Monitoramento RabbitMQ - Tempo: {elapsed}s | Restante: {remaining}s",
                            style="bold blue"
                        )
                    )

                    # Obter estatísticas
                    try:
                        stats_params = {"connection_id": connection_id}
                        stats_result = await monitor_stats(stats_params)
                        stats_data = json.loads(stats_result)

                        if stats_data.get("status") == "success":
                            stats = stats_data.get("data", {}).get("stats", {})
                            live.layout["stats"].update(_create_stats_panel(stats))
                    except Exception as e:
                        live.layout["stats"].update(
                            Panel(f"Erro ao obter stats: {str(e)}", style="red")
                        )

                    # Obter health
                    try:
                        health_params = {"connection_id": connection_id}
                        health_result = await monitor_health(health_params)
                        health_data = json.loads(health_result)

                        if health_data.get("status") == "success":
                            health = health_data.get("data", {}).get("health", {})
                            live.layout["health"].update(_create_health_panel(health))
                    except Exception as e:
                        live.layout["health"].update(
                            Panel(f"Erro ao obter health: {str(e)}", style="red")
                        )

                    # Atualizar footer
                    live.layout["footer"].update(
                        Panel(
                            f"Próxima atualização em {interval}s | Pressione Ctrl+C para sair",
                            style="dim"
                        )
                    )

                    await asyncio.sleep(interval)

            console.print("\n[bold green]✅ Monitoramento concluído!")

        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️ Monitoramento interrompido pelo usuário")
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1

        return 0

    exit_code = asyncio.run(_watch())
    if exit_code != 0:
        raise click.Abort()


def _display_stats_text(stats: dict[str, Any]) -> None:
    """Exibe estatísticas em formato texto."""
    console.print("📊 Estatísticas do RabbitMQ:")
    console.print(f"   Conexões: {stats.get('connections', 0)}")
    console.print(f"   Filas: {stats.get('queues', 0)}")
    console.print(f"   Exchanges: {stats.get('exchanges', 0)}")
    console.print(f"   Mensagens: {stats.get('messages', 0)}")
    console.print(f"   Consumidores: {stats.get('consumers', 0)}")
    console.print(f"   Taxa de mensagens/s: {stats.get('message_rate', 0):.2f}")
    console.print(f"   Uso de memória: {stats.get('memory_usage', 0):.2f}MB")
    console.print(f"   Uso de disco: {stats.get('disk_usage', 0):.2f}MB")


def _display_stats_table(stats: dict[str, Any]) -> None:
    """Exibe estatísticas em formato de tabela."""
    table = Table(title="Estatísticas do RabbitMQ", box=box.ROUNDED)
    table.add_column("Métrica", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")

    table.add_row("Conexões", str(stats.get("connections", 0)))
    table.add_row("Filas", str(stats.get("queues", 0)))
    table.add_row("Exchanges", str(stats.get("exchanges", 0)))
    table.add_row("Mensagens", str(stats.get("messages", 0)))
    table.add_row("Consumidores", str(stats.get("consumers", 0)))
    table.add_row("Taxa de Mensagens/s", f"{stats.get('message_rate', 0):.2f}")
    table.add_row("Uso de Memória", f"{stats.get('memory_usage', 0):.2f}MB")
    table.add_row("Uso de Disco", f"{stats.get('disk_usage', 0):.2f}MB")
    table.add_row("Última Atualização", stats.get("last_updated", "N/A"))

    console.print(table)


def _display_health_text(health: dict[str, Any]) -> None:
    """Exibe health check em formato texto."""
    status = health.get("status", "unknown")
    status_icon = "✅" if status == "healthy" else "❌" if status == "unhealthy" else "⚠️"

    console.print(f"{status_icon} Status: {status.upper()}")
    console.print(f"   Uptime: {health.get('uptime', 'N/A')}")
    console.print(f"   Versão: {health.get('version', 'N/A')}")
    console.print(f"   Node: {health.get('node', 'N/A')}")

    checks = health.get("checks", {})
    for check_name, check_result in checks.items():
        check_status = check_result.get("status", "unknown")
        check_icon = "✅" if check_status == "pass" else "❌"
        console.print(f"   {check_icon} {check_name}: {check_status}")


def _display_health_table(health: dict[str, Any]) -> None:
    """Exibe health check em formato de tabela."""
    status = health.get("status", "unknown")
    status_style = "green" if status == "healthy" else "red" if status == "unhealthy" else "yellow"

    table = Table(title="Health Check do RabbitMQ", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style=status_style)

    table.add_row("Status", status.upper())
    table.add_row("Uptime", health.get("uptime", "N/A"))
    table.add_row("Versão", health.get("version", "N/A"))
    table.add_row("Node", health.get("node", "N/A"))
    table.add_row("Timestamp", health.get("timestamp", "N/A"))

    console.print(table)

    # Tabela de checks
    checks = health.get("checks", {})
    if checks:
        checks_table = Table(title="Verificações de Saúde", box=box.ROUNDED)
        checks_table.add_column("Check", style="cyan", no_wrap=True)
        checks_table.add_column("Status", style="green")
        checks_table.add_column("Mensagem", style="yellow")

        for check_name, check_result in checks.items():
            check_status = check_result.get("status", "unknown")
            check_message = check_result.get("message", "")
            status_style = "green" if check_status == "pass" else "red"

            checks_table.add_row(
                check_name,
                f"[{status_style}]{check_status}[/{status_style}]",
                check_message
            )

        console.print(checks_table)


def _create_stats_panel(stats: dict[str, Any]) -> Panel:
    """Cria painel de estatísticas para live view."""
    content = f"""
[bold cyan]Conexões:[/bold cyan] {stats.get('connections', 0)}
[bold cyan]Filas:[/bold cyan] {stats.get('queues', 0)}
[bold cyan]Exchanges:[/bold cyan] {stats.get('exchanges', 0)}
[bold cyan]Mensagens:[/bold cyan] {stats.get('messages', 0)}
[bold cyan]Consumidores:[/bold cyan] {stats.get('consumers', 0)}
[bold cyan]Taxa/s:[/bold cyan] {stats.get('message_rate', 0):.2f}
[bold cyan]Memória:[/bold cyan] {stats.get('memory_usage', 0):.2f}MB
[bold cyan]Disco:[/bold cyan] {stats.get('disk_usage', 0):.2f}MB
"""
    return Panel(content, title="[bold green]Estatísticas", border_style="green")


def _create_health_panel(health: dict[str, Any]) -> Panel:
    """Cria painel de health para live view."""
    status = health.get("status", "unknown")
    status_style = "green" if status == "healthy" else "red" if status == "unhealthy" else "yellow"

    content = f"""
[bold {status_style}]Status:[/bold {status_style}] {status.upper()}
[bold cyan]Uptime:[/bold cyan] {health.get('uptime', 'N/A')}
[bold cyan]Versão:[/bold cyan] {health.get('version', 'N/A')}
[bold cyan]Node:[/bold cyan] {health.get('node', 'N/A')}
"""

    checks = health.get("checks", {})
    if checks:
        content += "\n[bold cyan]Checks:[/bold cyan]\n"
        for check_name, check_result in checks.items():
            check_status = check_result.get("status", "unknown")
            check_style = "green" if check_status == "pass" else "red"
            content += f"[{check_style}]• {check_name}: {check_status}[/{check_style}]\n"

    return Panel(content, title="[bold blue]Health Check", border_style="blue")
