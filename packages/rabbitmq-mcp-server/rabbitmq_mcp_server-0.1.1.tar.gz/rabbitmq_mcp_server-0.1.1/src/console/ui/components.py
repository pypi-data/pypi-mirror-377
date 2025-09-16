#!/usr/bin/env python3
"""
Componentes de UI Console

Componentes reutilizáveis de interface para o console RabbitMQ MCP,
incluindo tabelas, painéis e formatação de dados.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.columns import Columns
from rich.rule import Rule

console = Console()


class ConnectionDisplay:
    """Componente para exibir informações de conexão."""
    
    @staticmethod
    def create_connection_table(connection_info: Dict[str, Any]) -> Table:
        """Cria tabela de informações de conexão."""
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
        
        return table
    
    @staticmethod
    def create_connection_status_table(data: Dict[str, Any], connection_info: Dict[str, Any], 
                                     stats: Optional[Dict[str, Any]] = None) -> Table:
        """Cria tabela de status da conexão."""
        table = Table(title="Status da Conexão", box=box.ROUNDED)
        table.add_column("Propriedade", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")
        
        status_icon = "🟢" if data.get("is_connected") else "🔴"
        table.add_row("Status", f"{status_icon} {data.get('status', 'N/A')}")
        table.add_row("Conectado", "Sim" if data.get("is_connected") else "Não")
        table.add_row("ID da Conexão", connection_info.get("connection_id", "N/A"))
        table.add_row("Host", f"{connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}")
        table.add_row("Virtual Host", connection_info.get("virtual_host", "N/A"))
        
        if stats:
            table.add_row("Uptime", f"{stats.get('uptime_seconds', 0):.0f} segundos")
            table.add_row("Mensagens Enviadas", str(stats.get('messages_sent', 0)))
            table.add_row("Mensagens Recebidas", str(stats.get('messages_received', 0)))
            table.add_row("Bytes Enviados", str(stats.get('bytes_sent', 0)))
            table.add_row("Bytes Recebidos", str(stats.get('bytes_received', 0)))
            table.add_row("Canais", str(stats.get('channels_count', 0)))
            table.add_row("Filas Gerenciadas", str(stats.get('queues_managed', 0)))
            table.add_row("Exchanges Gerenciados", str(stats.get('exchanges_managed', 0)))
        
        return table
    
    @staticmethod
    def create_connections_list_table(connections: List[Dict[str, Any]], 
                                    stats: Optional[Dict[str, Any]] = None,
                                    include_stats: bool = False) -> Table:
        """Cria tabela de lista de conexões."""
        if not connections:
            return Table(title="Conexões Ativas", box=box.ROUNDED)
        
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
        
        return table


class QueueDisplay:
    """Componente para exibir informações de filas."""
    
    @staticmethod
    def create_queue_info_table(queue_info: Dict[str, Any]) -> Table:
        """Cria tabela de informações da fila."""
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
            table.add_row("Argumentos", str(arguments))
        
        return table
    
    @staticmethod
    def create_queues_list_table(queues: List[Dict[str, Any]], 
                               stats: Optional[Dict[str, Any]] = None,
                               include_stats: bool = False,
                               data: Optional[Dict[str, Any]] = None) -> Table:
        """Cria tabela de lista de filas."""
        if not queues:
            return Table(title="Filas", box=box.ROUNDED)
        
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
        
        return table


class MessageDisplay:
    """Componente para exibir informações de mensagens."""
    
    @staticmethod
    def create_message_info_table(message_info: Dict[str, Any]) -> Table:
        """Cria tabela de informações da mensagem."""
        table = Table(title="Informações da Mensagem", box=box.ROUNDED)
        table.add_column("Propriedade", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")
        
        table.add_row("ID da Mensagem", message_info.get("message_id", "N/A"))
        table.add_row("Routing Key", message_info.get("routing_key", "N/A"))
        table.add_row("Exchange", message_info.get("exchange", "N/A"))
        table.add_row("Fila", message_info.get("queue", "N/A"))
        table.add_row("Prioridade", str(message_info.get("priority", 0)))
        table.add_row("Timestamp", message_info.get("timestamp", "N/A"))
        table.add_row("Tipo de Conteúdo", message_info.get("content_type", "N/A"))
        table.add_row("Reentregue", "Sim" if message_info.get("redelivered") else "Não")
        
        # Headers se existirem
        headers = message_info.get("headers", {})
        if headers:
            table.add_row("Headers", str(headers))
        
        # Corpo da mensagem (truncado se muito longo)
        body = message_info.get("body", "")
        if len(body) > 100:
            body = body[:100] + "..."
        table.add_row("Corpo", body)
        
        return table
    
    @staticmethod
    def create_messages_list_table(messages: List[Dict[str, Any]]) -> Table:
        """Cria tabela de lista de mensagens."""
        if not messages:
            return Table(title="Mensagens", box=box.ROUNDED)
        
        table = Table(title="Mensagens", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Routing Key", style="green")
        table.add_column("Exchange", style="blue")
        table.add_column("Fila", style="magenta")
        table.add_column("Prioridade", style="yellow")
        table.add_column("Timestamp", style="red")
        table.add_column("Status", style="green")
        
        for msg in messages:
            status_icon = "🟢" if not msg.get("redelivered") else "🟡"
            
            row = [
                msg.get("message_id", "N/A")[:8] + "...",
                msg.get("routing_key", "N/A"),
                msg.get("exchange", "N/A"),
                msg.get("queue", "N/A"),
                str(msg.get("priority", 0)),
                msg.get("timestamp", "N/A"),
                f"{status_icon} {'Reentregue' if msg.get('redelivered') else 'Nova'}"
            ]
            
            table.add_row(*row)
        
        return table


class ProgressDisplay:
    """Componente para exibir barras de progresso."""
    
    @staticmethod
    def create_progress_spinner(message: str = "Processando...") -> Progress:
        """Cria barra de progresso com spinner."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        )
    
    @staticmethod
    def create_progress_bar(message: str = "Processando...", total: int = 100) -> Progress:
        """Cria barra de progresso com porcentagem."""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True
        )


class SummaryDisplay:
    """Componente para exibir resumos e estatísticas."""
    
    @staticmethod
    def create_connections_summary(data: Dict[str, Any]) -> Panel:
        """Cria painel de resumo de conexões."""
        total_count = data.get("total_count", 0)
        connected_count = data.get("connected_count", 0)
        
        summary_text = Text()
        summary_text.append(f"Total: {total_count} | ", style="bold")
        summary_text.append(f"Conectadas: {connected_count} | ", style="bold green")
        summary_text.append(f"Desconectadas: {total_count - connected_count}", style="bold red")
        
        return Panel(summary_text, title="Resumo de Conexões", border_style="blue")
    
    @staticmethod
    def create_queues_summary(data: Dict[str, Any]) -> Panel:
        """Cria painel de resumo de filas."""
        total_count = data.get("total_count", 0)
        active_count = data.get("active_count", 0)
        total_messages = data.get("total_messages", 0)
        total_consumers = data.get("total_consumers", 0)
        
        summary_text = Text()
        summary_text.append(f"Total: {total_count} | ", style="bold")
        summary_text.append(f"Ativas: {active_count} | ", style="bold green")
        summary_text.append(f"Mensagens: {total_messages} | ", style="bold yellow")
        summary_text.append(f"Consumidores: {total_consumers}", style="bold blue")
        
        return Panel(summary_text, title="Resumo de Filas", border_style="blue")
    
    @staticmethod
    def create_messages_summary(data: Dict[str, Any]) -> Panel:
        """Cria painel de resumo de mensagens."""
        total_count = data.get("total_count", 0)
        processed_count = data.get("processed_count", 0)
        failed_count = data.get("failed_count", 0)
        
        summary_text = Text()
        summary_text.append(f"Total: {total_count} | ", style="bold")
        summary_text.append(f"Processadas: {processed_count} | ", style="bold green")
        summary_text.append(f"Falharam: {failed_count}", style="bold red")
        
        return Panel(summary_text, title="Resumo de Mensagens", border_style="blue")


class ErrorDisplay:
    """Componente para exibir erros e avisos."""
    
    @staticmethod
    def create_error_panel(error_message: str, error_code: str = "UNKNOWN_ERROR", 
                          details: Optional[Dict[str, Any]] = None) -> Panel:
        """Cria painel de erro."""
        error_text = Text()
        error_text.append(f"❌ {error_message}\n", style="bold red")
        error_text.append(f"Código: {error_code}\n", style="red")
        
        if details:
            error_text.append("Detalhes:\n", style="bold yellow")
            for key, value in details.items():
                error_text.append(f"  {key}: {value}\n", style="yellow")
        
        return Panel(error_text, title="Erro", border_style="red")
    
    @staticmethod
    def create_warning_panel(warning_message: str, details: Optional[str] = None) -> Panel:
        """Cria painel de aviso."""
        warning_text = Text()
        warning_text.append(f"⚠️  {warning_message}\n", style="bold yellow")
        
        if details:
            warning_text.append(f"{details}", style="yellow")
        
        return Panel(warning_text, title="Aviso", border_style="yellow")
    
    @staticmethod
    def create_success_panel(success_message: str, details: Optional[str] = None) -> Panel:
        """Cria painel de sucesso."""
        success_text = Text()
        success_text.append(f"✅ {success_message}\n", style="bold green")
        
        if details:
            success_text.append(f"{details}", style="green")
        
        return Panel(success_text, title="Sucesso", border_style="green")


class LayoutDisplay:
    """Componente para layouts complexos."""
    
    @staticmethod
    def create_dashboard_layout(connections: List[Dict[str, Any]], 
                              queues: List[Dict[str, Any]],
                              messages: List[Dict[str, Any]]) -> Layout:
        """Cria layout de dashboard."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header"),
            Layout(name="main"),
            Layout(name="footer")
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="connections"),
            Layout(name="queues")
        )
        
        layout["right"].split_column(
            Layout(name="messages"),
            Layout(name="stats")
        )
        
        # Header
        header_text = Text("🐰 RabbitMQ MCP Dashboard", style="bold blue")
        layout["header"].update(Align.center(header_text))
        
        # Connections
        if connections:
            conn_table = ConnectionDisplay.create_connections_list_table(connections)
            layout["connections"].update(conn_table)
        else:
            layout["connections"].update(Panel("Nenhuma conexão ativa", title="Conexões"))
        
        # Queues
        if queues:
            queue_table = QueueDisplay.create_queues_list_table(queues)
            layout["queues"].update(queue_table)
        else:
            layout["queues"].update(Panel("Nenhuma fila encontrada", title="Filas"))
        
        # Messages
        if messages:
            msg_table = MessageDisplay.create_messages_list_table(messages)
            layout["messages"].update(msg_table)
        else:
            layout["messages"].update(Panel("Nenhuma mensagem recente", title="Mensagens"))
        
        # Stats
        stats_text = Text("📊 Estatísticas do Sistema\n\n", style="bold")
        stats_text.append("Conexões: 0\n", style="green")
        stats_text.append("Filas: 0\n", style="blue")
        stats_text.append("Mensagens: 0\n", style="yellow")
        layout["stats"].update(Panel(stats_text, title="Estatísticas"))
        
        # Footer
        footer_text = Text(f"Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        layout["footer"].update(Align.center(footer_text))
        
        return layout


def format_bytes(size_bytes: int) -> str:
    """Formata tamanho em bytes para string legível."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """Formata duração em segundos para string legível."""
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} min"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} h"


def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """Formata timestamp para string legível."""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return str(timestamp)
