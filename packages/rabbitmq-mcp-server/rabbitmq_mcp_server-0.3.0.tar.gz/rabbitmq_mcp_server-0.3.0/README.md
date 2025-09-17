# RabbitMQ MCP Server

A complete MCP (Model Context Protocol) server for RabbitMQ management, offering a standardized interface for connection, queue, message, exchange, and monitoring operations.

## 📄 License

This project is licensed under the **GNU Lesser General Public License v2.1 (LGPL-2.1)**. See the [LICENSE](LICENSE) file for more details.

The LGPL allows you to use this library in proprietary projects, but requires that modifications to the library be distributed under the same license.

## 🚀 Features

- **MCP Protocol**: Standardized interface for MCP client integration
- **Complete Management**: Connections, queues, messages, exchanges, and dead-letter queues
- **Monitoring**: Real-time statistics and health checks
- **Interactive CLI**: Command-line client with rich interface
- **Connection Pool**: Efficient management of multiple connections
- **Error Handling**: Robust error handling and recovery system
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Structured Logging**: Detailed logs with different levels and formats

## 📋 Prerequisites

- Python 3.11+
- RabbitMQ Server
- Dependencies listed in `pyproject.toml`

## 🛠️ Installation

### Installation via uvx (Recommended)

```bash
# Install and run directly
uvx rabbitmq-mcp-server

# Or install globally
uvx pip install rabbitmq-mcp-server
```

### Installation via pip

```bash
# Install via pip
pip install rabbitmq-mcp-server

# Or with development dependencies
pip install rabbitmq-mcp-server[dev]
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/your-username/rabbitmq-mcp-server.git
cd rabbitmq-mcp-server

# Install in development mode
pip install -e ".[dev]"
```

## 🚀 Usage

### MCP Configuration

To use with MCP clients (VS Code, Cursor, Claude Desktop), add to your configuration file:

```json
{
  "mcpServers": {
    "rabbitmq": {
      "command": "uvx",
      "args": ["rabbitmq-mcp-server"],
      "env": {
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_PORT": "5672",
        "RABBITMQ_USERNAME": "guest",
        "RABBITMQ_PASSWORD": "guest",
        "RABBITMQ_VHOST": "/"
      }
    }
  }
}
```

### MCP Server

To start the MCP server:

```bash
# Via uvx
uvx rabbitmq-mcp-server

# Or via pip
python -m src.mcp.server
```

### Interactive CLI

To use the CLI client:

```bash
python -m src.cli
```

Or use interactive mode:

```bash
python -m src.cli interactive
```

### CLI Commands

#### Connection

```bash
# Connect to RabbitMQ
rabbitmq-mcp-server connection connect --host localhost --port 5672 --username guest --password guest

# List connections
rabbitmq-mcp-server connection list

# Check connection status
rabbitmq-mcp-server connection status --connection-id <id>

# Disconnect
rabbitmq-mcp-server connection disconnect --connection-id <id>
```

#### Queues

```bash
# Create queue
rabbitmq-mcp-server queue create --connection-id <id> --queue-name my-queue --durable

# List queues
rabbitmq-mcp-server queue list --connection-id <id>

# Delete queue
rabbitmq-mcp-server queue delete --connection-id <id> --queue-name my-queue

# Purge queue
rabbitmq-mcp-server queue purge --connection-id <id> --queue-name my-queue
```

#### Messages

```bash
# Publish message
rabbitmq-mcp-server message publish --connection-id <id> --exchange-name my-exchange --routing-key my.key --message-body '{"message": "Hello World"}'

# Consume messages
rabbitmq-mcp-server message consume --connection-id <id> --queue-name my-queue --count 5

# Acknowledge messages
rabbitmq-mcp-server message acknowledge --connection-id <id> --delivery-tags 1,2,3

# Reject messages
rabbitmq-mcp-server message reject --connection-id <id> --delivery-tags 4,5 --requeue
```

#### Exchanges

```bash
# Create exchange
rabbitmq-mcp-server exchange create --connection-id <id> --exchange-name my-exchange --exchange-type direct --durable

# Delete exchange
rabbitmq-mcp-server exchange delete --connection-id <id> --exchange-name my-exchange

# Bind queue to exchange
rabbitmq-mcp-server exchange bind --connection-id <id> --exchange-name my-exchange --queue-name my-queue --routing-key my.key

# Unbind queue from exchange
rabbitmq-mcp-server exchange unbind --connection-id <id> --exchange-name my-exchange --queue-name my-queue --routing-key my.key
```

#### Dead Letter Queues

```bash
# Configure DLQ
rabbitmq-mcp-server dlq configure --connection-id <id> --queue-name my-queue --dlq-name my-dlq --dlq-exchange my-dlq-exchange

# Manage DLQ
rabbitmq-mcp-server dlq manage --connection-id <id> --queue-name my-queue --action list
rabbitmq-mcp-server dlq manage --connection-id <id> --queue-name my-queue --action purge
rabbitmq-mcp-server dlq manage --connection-id <id> --queue-name my-queue --action retry
```

#### Monitoring

```bash
# Get statistics
rabbitmq-mcp-server monitor stats --connection-id <id>

# Check health
rabbitmq-mcp-server monitor health --connection-id <id>

# Real-time monitoring
rabbitmq-mcp-server monitor watch --connection-id <id> --interval 5 --duration 60
```

## 🏗️ Architecture

### Project Structure

```
src/
├── mcp/                    # MCP Server
│   ├── server.py          # Main server
│   ├── command_processor.py # Command processing
│   ├── error_handler.py   # Error handling
│   ├── tools/             # MCP Tools
│   └── schemas/           # Validation schemas
├── rabbitmq/              # RabbitMQ Integration
│   ├── connection_manager.py # Connection manager
│   ├── queue_manager.py   # Queue manager
│   ├── message_manager.py # Message manager
│   ├── exchange_manager.py # Exchange manager
│   ├── connection_pool.py # Connection pool
│   └── health_monitor.py  # Health monitor
├── shared/                # Shared code
│   ├── models/           # Data models
│   └── utils/            # Utilities
└── cli/                  # CLI Client
    ├── client.py         # Main client
    └── __main__.py       # Entry point
```

### Main Components

1. **MCP Server**: Implements MCP protocol and exposes RabbitMQ tools
2. **Managers**: Specialized classes for different RabbitMQ operations
3. **Models**: Data definitions using Pydantic
4. **CLI**: Interactive command-line interface
5. **Tests**: Complete test suite

## 🔧 Configuration

### Configuration File

The CLI uses a configuration file at `~/.rabbitmq-mcp-server/config.json`:

```json
{
  "default_connection": {
    "host": "localhost",
    "port": 5672,
    "username": "guest",
    "password": "guest",
    "virtual_host": "/",
    "ssl_enabled": false
  },
  "output_format": "table",
  "auto_connect": false
}
```

### Environment Variables

- `RABBITMQ_HOST`: RabbitMQ host (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USERNAME`: Username (default: guest)
- `RABBITMQ_PASSWORD`: Password (default: guest)
- `RABBITMQ_VHOST`: Virtual host (default: /)

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Tests by Category

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/

# Contract tests
pytest tests/contract/
```

### Code Coverage

```bash
pytest --cov=src --cov-report=html
```

## 📊 Monitoring

### Available Metrics

- **Connections**: Number of active connections, uptime, statistics
- **Queues**: Message count, consumers, processing rate
- **Exchanges**: Bindings, routed messages
- **System**: Memory usage, CPU, connectivity

### Health Checks

The system includes automatic health checks:

- Connection status
- Server connectivity
- Channel health
- Overall performance

## 🔒 Security

### Authentication

- Support for RabbitMQ basic authentication
- SSL/TLS for secure connections
- Credential validation

### Authorization

- Respects RabbitMQ permissions
- Resource access validation
- Audit logs

## 🚀 Performance

### Optimizations

- Connection pool for reuse
- Async operations
- Metadata caching
- Batch processing

### Benchmarks

The project includes performance tests that verify:

- Operation response times
- Message throughput
- Memory usage
- Scalability

## 🤝 Contributing

### Development

1. Clone the repository
2. Install dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
4. Make your changes
5. Add tests for new functionality
6. Run linting: `ruff check src tests`
7. Format code: `ruff format src tests`

### Code Standards

- Use type hints
- Document functions and classes
- Follow PEP 8
- Write tests for new functionality
- Use structured logging

## 📝 License

This project is licensed under the GNU Lesser General Public License v2.1 (LGPL-2.1) - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Known Issues

- SSL connections require additional configuration
- Some monitoring operations require HTTP management API

### Troubleshooting

1. Check if RabbitMQ is running
2. Verify credentials and permissions
3. Check logs for detailed errors
4. Use `monitor health` for diagnosis

### Logs

Logs are structured in JSON by default. For more readable logs:

```bash
python -m src.cli --verbose
```

## 🔄 Changelog

### v0.1.0

- Initial MCP server implementation
- Complete RabbitMQ operation support
- Interactive CLI
- Comprehensive testing
- Complete documentation

## 📚 References

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Pika Python Client](https://pika.readthedocs.io/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Click](https://click.palletsprojects.com/)
- [Rich](https://rich.readthedocs.io/)
