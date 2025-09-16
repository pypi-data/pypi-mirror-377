"""
Ponto de entrada principal do CLI.

Este módulo implementa o ponto de entrada principal para o cliente CLI
do RabbitMQ MCP Server.
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console

from src.cli.client import cli_client
from src.shared.utils.logging import configure_logging


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Modo verboso')
@click.option('--config', '-c', help='Arquivo de configuração')
@click.pass_context
def cli(ctx, verbose, config):
    """RabbitMQ MCP CLI - Cliente de linha de comando para RabbitMQ MCP Server."""
    # Configurar logging
    log_level = "DEBUG" if verbose else "INFO"
    configure_logging(level=log_level, format_type="console")
    
    # Carregar configuração personalizada se fornecida
    if config:
        config_path = Path(config)
        if config_path.exists():
            cli_client.config_file = config_path
            cli_client.config = cli_client._load_config()
    
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--host', default='localhost', help='Host do RabbitMQ')
@click.option('--port', default=5672, help='Porta do RabbitMQ')
@click.option('--username', default='guest', help='Nome de usuário')
@click.option('--password', default='guest', help='Senha')
@click.option('--virtual-host', default='/', help='Virtual host')
@click.option('--ssl', is_flag=True, help='Habilitar SSL')
@click.option('--save', is_flag=True, help='Salvar como conexão padrão')
def connect(host, port, username, password, virtual_host, ssl, save):
    """Conecta ao servidor RabbitMQ."""
    async def _connect():
        connection_params = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'virtual_host': virtual_host,
            'ssl_enabled': ssl,
        }
        
        success = await cli_client.connect(**connection_params)
        
        if success and save:
            cli_client.config['default_connection'] = connection_params
            cli_client._save_config()
            cli_client.console.print("[green]Conexão salva como padrão[/green]")
    
    asyncio.run(_connect())


@cli.command()
def disconnect():
    """Desconecta do servidor RabbitMQ."""
    async def _disconnect():
        await cli_client.disconnect()
    
    asyncio.run(_disconnect())


@cli.command()
def connections():
    """Lista conexões ativas."""
    async def _list_connections():
        await cli_client.list_connections()
    
    asyncio.run(_list_connections())


@cli.group()
def queue():
    """Operações com filas."""
    pass


@queue.command('create')
@click.argument('name')
@click.option('--durable/--no-durable', default=True, help='Fila durável')
@click.option('--exclusive/--no-exclusive', default=False, help='Fila exclusiva')
@click.option('--auto-delete/--no-auto-delete', default=False, help='Auto-deletar quando não usada')
def queue_create(name, durable, exclusive, auto_delete):
    """Cria uma nova fila."""
    async def _create_queue():
        await cli_client.create_queue(
            name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete
        )
    
    asyncio.run(_create_queue())


@queue.command('list')
def queue_list():
    """Lista todas as filas."""
    async def _list_queues():
        await cli_client.list_queues()
    
    asyncio.run(_list_queues())


@queue.command('delete')
@click.argument('name')
@click.option('--if-unused', is_flag=True, help='Deletar apenas se não tiver consumidores')
@click.option('--if-empty', is_flag=True, help='Deletar apenas se estiver vazia')
def queue_delete(name, if_unused, if_empty):
    """Deleta uma fila."""
    async def _delete_queue():
        await cli_client.delete_queue(
            name,
            if_unused=if_unused,
            if_empty=if_empty
        )
    
    asyncio.run(_delete_queue())


@cli.group()
def message():
    """Operações com mensagens."""
    pass


@message.command('publish')
@click.argument('exchange')
@click.argument('routing_key')
@click.argument('body')
@click.option('--headers', help='Cabeçalhos JSON')
@click.option('--priority', default=0, help='Prioridade da mensagem')
@click.option('--content-type', default='application/json', help='Tipo de conteúdo')
@click.option('--persistent/--no-persistent', default=True, help='Mensagem persistente')
def message_publish(exchange, routing_key, body, headers, priority, content_type, persistent):
    """Publica uma mensagem."""
    async def _publish_message():
        kwargs = {
            'priority': priority,
            'content_type': content_type,
            'persistent': persistent,
        }
        
        if headers:
            import json
            try:
                kwargs['headers'] = json.loads(headers)
            except json.JSONDecodeError:
                cli_client.console.print("[red]Erro: Cabeçalhos devem ser JSON válido[/red]")
                return
        
        await cli_client.publish_message(exchange, routing_key, body, **kwargs)
    
    asyncio.run(_publish_message())


@message.command('consume')
@click.argument('queue')
@click.option('--count', default=1, help='Número de mensagens a consumir')
@click.option('--auto-ack/--no-auto-ack', default=False, help='Acknowledge automático')
@click.option('--timeout', default=30, help='Timeout em segundos')
def message_consume(queue, count, auto_ack, timeout):
    """Consome mensagens de uma fila."""
    async def _consume_messages():
        await cli_client.consume_messages(
            queue,
            count=count,
            auto_ack=auto_ack,
            timeout=timeout
        )
    
    asyncio.run(_consume_messages())


@cli.group()
def exchange():
    """Operações com exchanges."""
    pass


@exchange.command('create')
@click.argument('name')
@click.argument('type', type=click.Choice(['direct', 'topic', 'fanout', 'headers']))
@click.option('--durable/--no-durable', default=True, help='Exchange durável')
@click.option('--auto-delete/--no-auto-delete', default=False, help='Auto-deletar quando não usado')
@click.option('--internal/--no-internal', default=False, help='Exchange interno')
def exchange_create(name, type, durable, auto_delete, internal):
    """Cria um novo exchange."""
    async def _create_exchange():
        await cli_client.create_exchange(
            name,
            type,
            durable=durable,
            auto_delete=auto_delete,
            internal=internal
        )
    
    asyncio.run(_create_exchange())


@cli.command('bind')
@click.argument('exchange')
@click.argument('queue')
@click.argument('routing_key')
def bind(exchange, queue, routing_key):
    """Faz bind de uma fila a um exchange."""
    async def _bind_queue():
        await cli_client.bind_queue(exchange, queue, routing_key)
    
    asyncio.run(_bind_queue())


@cli.group()
def monitor():
    """Operações de monitoramento."""
    pass


@monitor.command('stats')
@click.option('--type', 'resource_type', default='all', 
              type=click.Choice(['queue', 'exchange', 'connection', 'all']),
              help='Tipo de recurso')
@click.option('--name', help='Nome específico do recurso')
@click.option('--include-rates/--no-include-rates', default=True, help='Incluir estatísticas de taxa')
@click.option('--time-range', default='5m',
              type=click.Choice(['1m', '5m', '15m', '1h', '24h']),
              help='Intervalo de tempo')
def monitor_stats(resource_type, name, include_rates, time_range):
    """Obtém estatísticas do sistema."""
    async def _get_stats():
        kwargs = {
            'include_rates': include_rates,
            'time_range': time_range,
        }
        
        if name:
            kwargs['resource_name'] = name
        
        await cli_client.get_stats(resource_type, **kwargs)
    
    asyncio.run(_get_stats())


@monitor.command('health')
@click.option('--type', 'check_type', default='all',
              type=click.Choice(['connection', 'server', 'cluster', 'all']),
              help='Tipo de verificação')
@click.option('--include-details/--no-include-details', default=False, help='Incluir detalhes')
def monitor_health(check_type, include_details):
    """Verifica a saúde do sistema."""
    async def _health_check():
        await cli_client.health_check(
            check_type,
            include_details=include_details
        )
    
    asyncio.run(_health_check())


@cli.group()
def config():
    """Operações de configuração."""
    pass


@config.command('show')
def config_show():
    """Mostra configuração atual."""
    cli_client._display_dict(cli_client.config, "Configuração")


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Define uma configuração."""
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
    
    cli_client.config[key] = value
    cli_client._save_config()
    cli_client.console.print(f"[green]Configuração '{key}' definida como '{value}'[/green]")


@cli.command()
def interactive():
    """Inicia modo interativo."""
    async def _interactive():
        await cli_client.interactive_mode()
    
    asyncio.run(_interactive())


@cli.command()
def version():
    """Mostra versão do CLI."""
    console = Console()
    console.print("[bold blue]RabbitMQ MCP CLI[/bold blue]")
    console.print("Versão: 0.1.0")
    console.print("Servidor MCP RabbitMQ")


def main():
    """Função principal do CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
        sys.exit(1)
    except Exception as e:
        console = Console()
        console.print(f"[red]Erro: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
