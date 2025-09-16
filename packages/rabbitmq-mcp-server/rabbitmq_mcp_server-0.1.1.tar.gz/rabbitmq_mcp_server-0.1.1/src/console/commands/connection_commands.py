#!/usr/bin/env python3
"""
Comandos CLI de Connection

Comandos CLI para gerenciamento de conexões RabbitMQ,
incluindo conectar, desconectar, status e listagem.

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

from src.mcp.tools.connection_tools import (
    connection_connect, connection_disconnect, 
    connection_status, connection_list
)
from src.shared.utils.serialization import Serializer

console = Console()


@click.group(name="connection", help="Comandos de gerenciamento de conexões RabbitMQ")
def connection_group():
    """Grupo de comandos para conexões."""
    pass


@connection_group.command(name="connect", help="Conectar ao servidor RabbitMQ")
@click.option("--host", "-h", required=True, help="Hostname ou IP do servidor RabbitMQ")
@click.option("--port", "-p", default=5672, type=int, help="Porta do servidor RabbitMQ")
@click.option("--username", "-u", required=True, help="Nome de usuário para autenticação")
@click.option("--password", "-w", required=True, help="Senha para autenticação")
@click.option("--virtual-host", "-v", default="/", help="Virtual host")
@click.option("--ssl", is_flag=True, help="Habilitar SSL/TLS")
@click.option("--timeout", "-t", default=30, type=int, help="Timeout de conexão em segundos")
@click.option("--heartbeat", default=600, type=int, help="Intervalo de heartbeat em segundos")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def connect_command(host: str, port: int, username: str, password: str, 
                   virtual_host: str, ssl: bool, timeout: int, heartbeat: int, output: str):
    """Conecta ao servidor RabbitMQ."""
    
    async def _connect():
        try:
            # Preparar parâmetros
            params = {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "virtual_host": virtual_host,
                "ssl_enabled": ssl,
                "connection_timeout": timeout,
                "heartbeat_interval": heartbeat
            }
            
            # Mostrar progresso
            with console.status("[bold green]Conectando ao RabbitMQ..."):
                result = await connection_connect(params)
            
            # Parsear resultado
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                connection_info = data.get("connection_info", {})
                
                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"✅ Conexão estabelecida: {connection_info.get('connection_id', 'N/A')}")
                    console.print(f"   Host: {connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}")
                    console.print(f"   Usuário: {connection_info.get('username', 'N/A')}")
                    console.print(f"   Virtual Host: {connection_info.get('virtual_host', 'N/A')}")
                    console.print(f"   SSL: {'Sim' if connection_info.get('ssl_enabled') else 'Não'}")
                else:  # table
                    _display_connection_info(connection_info)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro na conexão: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_connect())
    if exit_code != 0:
        raise click.Abort()


@connection_group.command(name="disconnect", help="Desconectar do servidor RabbitMQ")
@click.option("--connection-id", "-c", required=True, help="ID da conexão para desconectar")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="text", help="Formato de saída")
def disconnect_command(connection_id: str, output: str):
    """Desconecta do servidor RabbitMQ."""
    
    async def _disconnect():
        try:
            params = {"connection_id": connection_id}
            
            with console.status("[bold yellow]Desconectando..."):
                result = await connection_disconnect(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                if output == "json":
                    console.print_json(result)
                else:
                    console.print(f"✅ Conexão {connection_id} desconectada com sucesso")
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro na desconexão: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_disconnect())
    if exit_code != 0:
        raise click.Abort()


@connection_group.command(name="status", help="Verificar status da conexão")
@click.option("--connection-id", "-c", required=True, help="ID da conexão para verificar")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def status_command(connection_id: str, output: str):
    """Verifica o status da conexão."""
    
    async def _status():
        try:
            params = {"connection_id": connection_id}
            
            with console.status("[bold blue]Verificando status..."):
                result = await connection_status(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                connection_info = data.get("connection_info", {})
                stats = data.get("stats")
                
                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    status_icon = "🟢" if data.get("is_connected") else "🔴"
                    console.print(f"{status_icon} Status: {data.get('status', 'N/A')}")
                    console.print(f"   Conectado: {'Sim' if data.get('is_connected') else 'Não'}")
                    console.print(f"   Host: {connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}")
                    console.print(f"   Virtual Host: {connection_info.get('virtual_host', 'N/A')}")
                    if stats:
                        console.print(f"   Uptime: {stats.get('uptime_seconds', 0):.0f}s")
                else:  # table
                    _display_connection_status(data, connection_info, stats)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao verificar status: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_status())
    if exit_code != 0:
        raise click.Abort()


@connection_group.command(name="list", help="Listar todas as conexões ativas")
@click.option("--include-stats", "-s", is_flag=True, help="Incluir estatísticas das conexões")
@click.option("--output", "-o", type=click.Choice(["table", "json", "text"]), default="table", help="Formato de saída")
def list_command(include_stats: bool, output: str):
    """Lista todas as conexões ativas."""
    
    async def _list():
        try:
            params = {"include_stats": include_stats}
            
            with console.status("[bold blue]Listando conexões..."):
                result = await connection_list(params)
            
            result_data = json.loads(result)
            
            if result_data.get("status") == "success":
                data = result_data.get("data", {})
                connections = data.get("connections", [])
                stats = data.get("stats", {})
                
                if output == "json":
                    console.print_json(result)
                elif output == "text":
                    console.print(f"📋 Total de conexões: {data.get('total_count', 0)}")
                    console.print(f"🟢 Conectadas: {data.get('connected_count', 0)}")
                    for conn in connections:
                        status_icon = "🟢" if conn.get("status") == "CONNECTED" else "🔴"
                        console.print(f"   {status_icon} {conn.get('connection_id', 'N/A')} - {conn.get('host', 'N/A')}:{conn.get('port', 'N/A')}")
                else:  # table
                    _display_connections_list(connections, stats, include_stats)
            else:
                error_msg = result_data.get("error_message", "Erro desconhecido")
                console.print(f"[bold red]❌ Erro ao listar conexões: {error_msg}")
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Erro inesperado: {str(e)}")
            return 1
        
        return 0
    
    exit_code = asyncio.run(_list())
    if exit_code != 0:
        raise click.Abort()


def _display_connection_info(connection_info: Dict[str, Any]) -> None:
    """Exibe informações da conexão em formato de tabela."""
    table = Table(title="Informações da Conexão", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")
    
    table.add_row("ID da Conexão", connection_info.get("connection_id", "N/A"))
    table.add_row("Host", f"{connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}")
    table.add_row("Usuário", connection_info.get("username", "N/A"))
    table.add_row("Virtual Host", connection_info.get("virtual_host", "N/A"))
    table.add_row("SSL", "Sim" if connection_info.get("ssl_enabled") else "Não")
    table.add_row("Status", connection_info.get("status", "N/A"))
    table.add_row("Criado em", connection_info.get("created_at", "N/A"))
    table.add_row("Último uso", connection_info.get("last_used", "N/A"))
    
    console.print(table)


def _display_connection_status(data: Dict[str, Any], connection_info: Dict[str, Any], stats: Optional[Dict[str, Any]]) -> None:
    """Exibe status da conexão em formato de tabela."""
    # Tabela principal de status
    table = Table(title="Status da Conexão", box=box.ROUNDED)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="green")
    
    status_icon = "🟢" if data.get("is_connected") else "🔴"
    table.add_row("Status", f"{status_icon} {data.get('status', 'N/A')}")
    table.add_row("Conectado", "Sim" if data.get("is_connected") else "Não")
    table.add_row("ID da Conexão", connection_info.get("connection_id", "N/A"))
    table.add_row("Host", f"{connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}")
    table.add_row("Virtual Host", connection_info.get("virtual_host", "N/A"))
    
    console.print(table)
    
    # Tabela de estatísticas se disponível
    if stats:
        stats_table = Table(title="Estatísticas da Conexão", box=box.ROUNDED)
        stats_table.add_column("Métrica", style="cyan", no_wrap=True)
        stats_table.add_column("Valor", style="yellow")
        
        stats_table.add_row("Uptime", f"{stats.get('uptime_seconds', 0):.0f} segundos")
        stats_table.add_row("Mensagens Enviadas", str(stats.get('messages_sent', 0)))
        stats_table.add_row("Mensagens Recebidas", str(stats.get('messages_received', 0)))
        stats_table.add_row("Bytes Enviados", str(stats.get('bytes_sent', 0)))
        stats_table.add_row("Bytes Recebidos", str(stats.get('bytes_received', 0)))
        stats_table.add_row("Canais", str(stats.get('channels_count', 0)))
        stats_table.add_row("Filas Gerenciadas", str(stats.get('queues_managed', 0)))
        stats_table.add_row("Exchanges Gerenciados", str(stats.get('exchanges_managed', 0)))
        
        console.print(stats_table)


def _display_connections_list(connections: list, stats: Dict[str, Any], include_stats: bool) -> None:
    """Exibe lista de conexões em formato de tabela."""
    if not connections:
        console.print(Panel("Nenhuma conexão encontrada", title="Conexões", border_style="yellow"))
        return
    
    table = Table(title="Conexões Ativas", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Host", style="green")
    table.add_column("Usuário", style="blue")
    table.add_column("VHost", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("SSL", style="red")
    
    if include_stats:
        table.add_column("Uptime", style="yellow")
        table.add_column("Mensagens", style="green")
    
    for conn in connections:
        status_icon = "🟢" if conn.get("status") == "CONNECTED" else "🔴"
        ssl_icon = "🔒" if conn.get("ssl_enabled") else "🔓"
        
        row = [
            conn.get("connection_id", "N/A")[:8] + "...",
            f"{conn.get('host', 'N/A')}:{conn.get('port', 'N/A')}",
            conn.get("username", "N/A"),
            conn.get("virtual_host", "N/A"),
            f"{status_icon} {conn.get('status', 'N/A')}",
            ssl_icon
        ]
        
        if include_stats and conn.get("connection_id") in stats:
            conn_stats = stats[conn.get("connection_id")]
            row.extend([
                f"{conn_stats.get('uptime_seconds', 0):.0f}s",
                f"{conn_stats.get('messages_sent', 0)}/{conn_stats.get('messages_received', 0)}"
            ])
        
        table.add_row(*row)
    
    console.print(table)
    
    # Resumo
    total_count = len(connections)
    connected_count = len([c for c in connections if c.get("status") == "CONNECTED"])
    
    summary = Text()
    summary.append(f"Total: {total_count} | ", style="bold")
    summary.append(f"Conectadas: {connected_count} | ", style="bold green")
    summary.append(f"Desconectadas: {total_count - connected_count}", style="bold red")
    
    console.print(Panel(summary, title="Resumo", border_style="blue"))
