#!/usr/bin/env python3
"""
Formatadores de UI Console

Utilitários de formatação para exibição de dados no console RabbitMQ MCP,
incluindo formatação de dados, cores e estilos.

Licença: LGPL-3.0
Autor: RabbitMQ MCP Team
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from rich.text import Text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule

console = Console()


class DataFormatter:
    """Formatador de dados para exibição no console."""
    
    @staticmethod
    def format_connection_status(status: str) -> Text:
        """Formata status de conexão com cores."""
        status_text = Text()
        
        if status == "CONNECTED":
            status_text.append("🟢 Conectado", style="bold green")
        elif status == "CONNECTING":
            status_text.append("🟡 Conectando", style="bold yellow")
        elif status == "DISCONNECTED":
            status_text.append("🔴 Desconectado", style="bold red")
        elif status == "ERROR":
            status_text.append("❌ Erro", style="bold red")
        else:
            status_text.append(f"❓ {status}", style="bold white")
        
        return status_text
    
    @staticmethod
    def format_queue_status(status: str) -> Text:
        """Formata status de fila com cores."""
        status_text = Text()
        
        if status == "ACTIVE":
            status_text.append("🟢 Ativa", style="bold green")
        elif status == "INACTIVE":
            status_text.append("🔴 Inativa", style="bold red")
        elif status == "PENDING":
            status_text.append("🟡 Pendente", style="bold yellow")
        else:
            status_text.append(f"❓ {status}", style="bold white")
        
        return status_text
    
    @staticmethod
    def format_message_status(status: str) -> Text:
        """Formata status de mensagem com cores."""
        status_text = Text()
        
        if status == "NEW":
            status_text.append("🆕 Nova", style="bold green")
        elif status == "PROCESSING":
            status_text.append("🔄 Processando", style="bold yellow")
        elif status == "ACKNOWLEDGED":
            status_text.append("✅ Confirmada", style="bold green")
        elif status == "REJECTED":
            status_text.append("❌ Rejeitada", style="bold red")
        elif status == "REDELIVERED":
            status_text.append("🔄 Reentregue", style="bold yellow")
        else:
            status_text.append(f"❓ {status}", style="bold white")
        
        return status_text
    
    @staticmethod
    def format_ssl_status(ssl_enabled: bool) -> Text:
        """Formata status SSL com ícones."""
        if ssl_enabled:
            return Text("🔒 SSL", style="bold green")
        else:
            return Text("🔓 Sem SSL", style="bold red")
    
    @staticmethod
    def format_boolean(value: bool, true_text: str = "Sim", false_text: str = "Não") -> Text:
        """Formata valor booleano com cores."""
        if value:
            return Text(f"✅ {true_text}", style="bold green")
        else:
            return Text(f"❌ {false_text}", style="bold red")
    
    @staticmethod
    def format_number(value: Union[int, float], unit: str = "") -> Text:
        """Formata número com separadores de milhares."""
        if isinstance(value, float):
            formatted = f"{value:,.2f}"
        else:
            formatted = f"{value:,}"
        
        if unit:
            formatted += f" {unit}"
        
        return Text(formatted, style="cyan")
    
    @staticmethod
    def format_bytes(size_bytes: int) -> Text:
        """Formata tamanho em bytes para string legível."""
        if size_bytes == 0:
            return Text("0 B", style="cyan")
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        formatted = f"{size_bytes:.2f} {size_names[i]}"
        return Text(formatted, style="cyan")
    
    @staticmethod
    def format_duration(seconds: float) -> Text:
        """Formata duração em segundos para string legível."""
        if seconds < 1:
            formatted = f"{seconds * 1000:.0f} ms"
        elif seconds < 60:
            formatted = f"{seconds:.2f} s"
        elif seconds < 3600:
            minutes = seconds / 60
            formatted = f"{minutes:.2f} min"
        else:
            hours = seconds / 3600
            formatted = f"{hours:.2f} h"
        
        return Text(formatted, style="cyan")
    
    @staticmethod
    def format_timestamp(timestamp: Union[str, datetime]) -> Text:
        """Formata timestamp para string legível."""
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return Text(timestamp, style="dim")
        
        if isinstance(timestamp, datetime):
            formatted = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            return Text(formatted, style="dim")
        
        return Text(str(timestamp), style="dim")
    
    @staticmethod
    def format_percentage(value: float, total: float) -> Text:
        """Formata porcentagem com cores baseadas no valor."""
        if total == 0:
            percentage = 0
        else:
            percentage = (value / total) * 100
        
        if percentage >= 90:
            style = "bold red"
        elif percentage >= 70:
            style = "bold yellow"
        else:
            style = "bold green"
        
        formatted = f"{percentage:.1f}%"
        return Text(formatted, style=style)


class TableFormatter:
    """Formatador de tabelas para diferentes tipos de dados."""
    
    @staticmethod
    def format_connection_table_data(connection_info: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de conexão para tabela."""
        return {
            "ID": connection_info.get("connection_id", "N/A")[:8] + "...",
            "Host": f"{connection_info.get('host', 'N/A')}:{connection_info.get('port', 'N/A')}",
            "Usuário": connection_info.get("username", "N/A"),
            "VHost": connection_info.get("virtual_host", "N/A"),
            "SSL": DataFormatter.format_ssl_status(connection_info.get("ssl_enabled", False)),
            "Status": DataFormatter.format_connection_status(connection_info.get("status", "UNKNOWN")),
            "Criado": DataFormatter.format_timestamp(connection_info.get("created_at", "")),
            "Último Uso": DataFormatter.format_timestamp(connection_info.get("last_used", ""))
        }
    
    @staticmethod
    def format_queue_table_data(queue_info: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de fila para tabela."""
        return {
            "Nome": queue_info.get("name", "N/A"),
            "VHost": queue_info.get("vhost", "N/A"),
            "Durável": DataFormatter.format_boolean(queue_info.get("durable", False)),
            "Exclusiva": DataFormatter.format_boolean(queue_info.get("exclusive", False)),
            "Auto-delete": DataFormatter.format_boolean(queue_info.get("auto_delete", False)),
            "Mensagens": DataFormatter.format_number(queue_info.get("message_count", 0)),
            "Consumidores": DataFormatter.format_number(queue_info.get("consumer_count", 0)),
            "Status": DataFormatter.format_queue_status(queue_info.get("status", "UNKNOWN")),
            "Criada": DataFormatter.format_timestamp(queue_info.get("created_at", ""))
        }
    
    @staticmethod
    def format_message_table_data(message_info: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de mensagem para tabela."""
        return {
            "ID": message_info.get("message_id", "N/A")[:8] + "...",
            "Routing Key": message_info.get("routing_key", "N/A"),
            "Exchange": message_info.get("exchange", "N/A"),
            "Fila": message_info.get("queue", "N/A"),
            "Prioridade": DataFormatter.format_number(message_info.get("priority", 0)),
            "Status": DataFormatter.format_message_status(
                "REDELIVERED" if message_info.get("redelivered") else "NEW"
            ),
            "Timestamp": DataFormatter.format_timestamp(message_info.get("timestamp", ""))
        }


class PanelFormatter:
    """Formatador de painéis para diferentes tipos de informações."""
    
    @staticmethod
    def create_info_panel(title: str, data: Dict[str, Any], 
                         formatter_func: Optional[callable] = None) -> Panel:
        """Cria painel de informações formatado."""
        content = Text()
        
        for key, value in data.items():
            if formatter_func:
                formatted_value = formatter_func(key, value)
            else:
                formatted_value = str(value)
            
            content.append(f"{key}: ", style="bold cyan")
            content.append(f"{formatted_value}\n", style="green")
        
        return Panel(content, title=title, border_style="blue")
    
    @staticmethod
    def create_stats_panel(title: str, stats: Dict[str, Any]) -> Panel:
        """Cria painel de estatísticas formatado."""
        content = Text()
        
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                if "bytes" in key.lower() or "size" in key.lower():
                    formatted_value = DataFormatter.format_bytes(value)
                elif "duration" in key.lower() or "time" in key.lower():
                    formatted_value = DataFormatter.format_duration(value)
                else:
                    formatted_value = DataFormatter.format_number(value)
            else:
                formatted_value = str(value)
            
            content.append(f"{key}: ", style="bold cyan")
            content.append(f"{formatted_value}\n", style="green")
        
        return Panel(content, title=title, border_style="green")
    
    @staticmethod
    def create_summary_panel(title: str, summary_data: Dict[str, Any]) -> Panel:
        """Cria painel de resumo formatado."""
        content = Text()
        
        for key, value in summary_data.items():
            if isinstance(value, dict):
                content.append(f"{key}:\n", style="bold yellow")
                for sub_key, sub_value in value.items():
                    content.append(f"  {sub_key}: ", style="cyan")
                    content.append(f"{sub_value}\n", style="green")
                content.append("\n")
            else:
                content.append(f"{key}: ", style="bold cyan")
                content.append(f"{value}\n", style="green")
        
        return Panel(content, title=title, border_style="blue")


class ColorFormatter:
    """Formatador de cores para diferentes tipos de dados."""
    
    # Cores para diferentes tipos de status
    STATUS_COLORS = {
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "bold blue",
        "dim": "dim"
    }
    
    # Cores para diferentes tipos de dados
    DATA_COLORS = {
        "string": "green",
        "number": "cyan",
        "boolean": "yellow",
        "timestamp": "dim",
        "id": "magenta"
    }
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Retorna cor baseada no status."""
        status_lower = status.lower()
        
        if "success" in status_lower or "connected" in status_lower or "active" in status_lower:
            return ColorFormatter.STATUS_COLORS["success"]
        elif "error" in status_lower or "failed" in status_lower or "rejected" in status_lower:
            return ColorFormatter.STATUS_COLORS["error"]
        elif "warning" in status_lower or "pending" in status_lower or "processing" in status_lower:
            return ColorFormatter.STATUS_COLORS["warning"]
        else:
            return ColorFormatter.STATUS_COLORS["info"]
    
    @staticmethod
    def get_data_color(data_type: str) -> str:
        """Retorna cor baseada no tipo de dados."""
        return ColorFormatter.DATA_COLORS.get(data_type, "white")
    
    @staticmethod
    def format_with_color(text: str, color: str) -> Text:
        """Formata texto com cor específica."""
        return Text(text, style=color)


class ProgressFormatter:
    """Formatador de barras de progresso e indicadores."""
    
    @staticmethod
    def create_progress_text(current: int, total: int, label: str = "Progresso") -> Text:
        """Cria texto de progresso formatado."""
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        progress_text = Text()
        progress_text.append(f"{label}: ", style="bold")
        progress_text.append(f"{current}/{total} ", style="cyan")
        progress_text.append(f"({percentage:.1f}%)", style="green")
        
        return progress_text
    
    @staticmethod
    def create_loading_text(message: str = "Carregando...") -> Text:
        """Cria texto de carregamento formatado."""
        loading_text = Text()
        loading_text.append("⏳ ", style="yellow")
        loading_text.append(message, style="bold")
        
        return loading_text
    
    @staticmethod
    def create_completion_text(message: str = "Concluído!") -> Text:
        """Cria texto de conclusão formatado."""
        completion_text = Text()
        completion_text.append("✅ ", style="green")
        completion_text.append(message, style="bold green")
        
        return completion_text


def format_json_data(data: Any, max_length: int = 100) -> Text:
    """Formata dados JSON para exibição."""
    import json
    
    try:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if len(json_str) > max_length:
            json_str = json_str[:max_length] + "..."
        
        return Text(json_str, style="dim")
    except Exception:
        return Text(str(data), style="dim")


def format_list_data(data: List[Any], max_items: int = 10) -> Text:
    """Formata lista de dados para exibição."""
    if not data:
        return Text("(vazio)", style="dim")
    
    if len(data) <= max_items:
        items = [str(item) for item in data]
    else:
        items = [str(item) for item in data[:max_items]]
        items.append(f"... e mais {len(data) - max_items} itens")
    
    return Text(", ".join(items), style="cyan")


def format_dict_data(data: Dict[str, Any], max_items: int = 10) -> Text:
    """Formata dicionário de dados para exibição."""
    if not data:
        return Text("(vazio)", style="dim")
    
    items = []
    count = 0
    
    for key, value in data.items():
        if count >= max_items:
            items.append(f"... e mais {len(data) - max_items} itens")
            break
        
        items.append(f"{key}: {value}")
        count += 1
    
    return Text(", ".join(items), style="cyan")
