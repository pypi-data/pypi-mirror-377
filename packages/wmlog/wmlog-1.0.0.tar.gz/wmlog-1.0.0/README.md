# WML (Websocket MQTT Logging)

[![PyPI version](https://badge.fury.io/py/wml.svg)](https://badge.fury.io/py/wml)
[![Python versions](https://img.shields.io/pypi/pyversions/wml.svg)](https://pypi.org/project/wml/)
[![License](https://img.shields.io/pypi/l/wml.svg)](https://github.com/your-org/wml/blob/main/LICENSE)

**WML** is a centralized logging system that enables structured logging with real-time broadcasting over WebSocket and MQTT. Designed for microservices, embedded systems, and distributed applications that need unified, observable logging across multiple services and environments.

## 🚀 Features

- **Structured Logging**: Built on `structlog` with rich context and metadata
- **Real-time Broadcasting**: WebSocket and MQTT streaming for live log monitoring
- **Multiple Formatters**: JSON, Rich Console, Compact, and Structured output
- **Custom Handlers**: WebSocket, MQTT, Redis, File, and more
- **CLI Tools**: Command-line interface for log management and monitoring
- **Context Enrichment**: Automatic service, environment, and request context
- **Async Support**: Full async/await support for high-performance applications
- **Redis Integration**: Optional Redis backend for log storage and analysis
- **Rich Console Output**: Beautiful console logging with syntax highlighting

## 📦 Installation

```bash
# Install from PyPI
pip install wml

# Install with optional dependencies
pip install wml[redis,mqtt,websocket]

# Development installation
git clone https://github.com/your-org/wml.git
cd wml
pip install -e .
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WML Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────────┐ │
│  │   Application   │    │         WML Logger               │ │
│  │                 │────┤                                  │ │
│  │  - Service A    │    │  • Structured Logging            │ │
│  │  - Service B    │    │  • Context Enrichment            │ │
│  │  - Service C    │    │  • Multiple Handlers             │ │
│  └─────────────────┘    └──────────────────────────────────┘ │
│                                     │                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Formatters                            │ │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐  │ │
│  │  │  JSON   │ │   Rich   │ │ Compact │ │  Structured  │  │ │
│  │  └─────────┘ └──────────┘ └─────────┘ └──────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                     │                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Handlers                             │ │
│  │  ┌──────────┐ ┌──────┐ ┌───────┐ ┌──────┐ ┌──────────┐  │ │
│  │  │WebSocket │ │ MQTT │ │ Redis │ │ File │ │ Console  │  │ │
│  │  └──────────┘ └──────┘ └───────┘ └──────┘ └──────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                     │                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Outputs                               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │ │
│  │  │WebSocket │ │   MQTT   │ │  Redis   │ │   File       │ │ │
│  │  │Clients   │ │ Broker   │ │ Database │ │  System      │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Quick Start

### Basic Logging

```python
from wml import WMLLogger, LoggingConfig

# Create logging configuration
config = LoggingConfig(
    service_name="my-service",
    log_level="info",
    console_enabled=True,
    console_format="rich"
)

# Get logger instance
logger = WMLLogger.get_logger(config)

# Log messages with structured data
logger.logger.info("Service started", port=8080, environment="production")
logger.logger.error("Database connection failed", 
                   error="Connection timeout", 
                   retry_count=3)
```

### WebSocket Broadcasting

```python
from wml import WMLLogger, LoggingConfig

config = LoggingConfig(
    service_name="websocket-service",
    websocket_enabled=True,
    websocket_port=8765,
    websocket_host="0.0.0.0"
)

logger = WMLLogger.get_logger(config)

# Logs will be automatically broadcast to WebSocket clients
logger.logger.info("WebSocket message", client_count=42)
```

### MQTT Integration

```python
from wml import WMLLogger, LoggingConfig

config = LoggingConfig(
    service_name="mqtt-service",
    mqtt_enabled=True,
    mqtt_broker="mqtt://localhost:1883",
    mqtt_topic="logs/my-service"
)

logger = WMLLogger.get_logger(config)

# Logs will be published to MQTT broker
logger.logger.warning("High memory usage", memory_percent=85)
```

### Context Enrichment

```python
from wml import WMLLogger, LoggingConfig, LogContext

# Create context with additional metadata
context = LogContext(
    service_name="api-service",
    environment="staging",
    version="1.2.3",
    custom_data={"region": "us-east-1", "datacenter": "dc-01"}
)

config = LoggingConfig(service_name="api-service")
logger = WMLLogger.get_logger(config, context)

# All logs will include context information
logger.logger.info("Request processed", 
                   request_id="req-123", 
                   response_time=0.045)
```

## 🖥️ CLI Usage

WML provides a comprehensive CLI for log management and monitoring:

### Send Log Messages

```bash
# Send a simple log message
wml log "Hello, World!"

# Send with specific service and level
wml log --service my-service --level error "Something went wrong"

# Send with MQTT broadcasting
wml log --mqtt-broker localhost:1883 --mqtt-topic logs/test "MQTT log message"
```

### Monitor Logs

```bash
# Monitor MQTT logs
wml monitor --broker localhost:1883 --topic "logs/#"

# Monitor with filtering
wml monitor --broker localhost:1883 --filter-service my-service --filter-level error

# Monitor WebSocket logs
wml websocket-monitor --port 8765 --host localhost
```

### Start Broadcasting Server

```bash
# Start WebSocket and MQTT broadcasting server
wml server --websocket-port 8765 --mqtt-broker localhost:1883

# Start WebSocket-only server
wml server --websocket-port 8765
```

### Test Configuration

```bash
# Test with default configuration
wml test

# Test with custom configuration file
wml test --config-file config.json
```

### Package Information

```bash
# Show package information
wml info
```

## ⚙️ Configuration

### Environment Variables

WML supports configuration via environment variables:

```bash
# Logging configuration
export WML_LOG_LEVEL=debug
export WML_SERVICE_NAME=my-service
export WML_CONSOLE_FORMAT=rich

# WebSocket configuration
export WML_WEBSOCKET_ENABLED=true
export WML_WEBSOCKET_PORT=8765
export WML_WEBSOCKET_HOST=0.0.0.0

# MQTT configuration
export WML_MQTT_ENABLED=true
export WML_MQTT_BROKER=mqtt://localhost:1883
export WML_MQTT_TOPIC=logs/my-service
export WML_MQTT_QOS=1

# File configuration
export WML_FILE_ENABLED=true
export WML_FILE_PATH=/var/log/my-service.log
export WML_FILE_MAX_SIZE=10485760
export WML_FILE_BACKUP_COUNT=5

# Redis configuration (optional)
export WML_REDIS_ENABLED=false
export WML_REDIS_URL=redis://localhost:6379/0
export WML_REDIS_KEY_PREFIX=logs:
```

### Configuration File

```json
{
  "service_name": "my-service",
  "log_level": "info",
  "console_enabled": true,
  "console_format": "rich",
  "file_enabled": true,
  "file_path": "/var/log/my-service.log",
  "file_max_size": 10485760,
  "file_backup_count": 5,
  "websocket_enabled": true,
  "websocket_port": 8765,
  "websocket_host": "0.0.0.0",
  "mqtt_enabled": true,
  "mqtt_broker": "mqtt://localhost:1883",
  "mqtt_topic": "logs/my-service",
  "mqtt_qos": 1,
  "include_timestamp": true,
  "include_caller": true,
  "timestamp_format": "iso"
}
```

## 🔧 Advanced Usage

### Custom Formatters

```python
from wml.formatters import JSONFormatter, RichConsoleFormatter

# Custom JSON formatter with additional fields
json_formatter = JSONFormatter(
    include_extra_fields=True,
    timestamp_format="iso",
    pretty_print=True
)

# Custom Rich formatter with specific styling
rich_formatter = RichConsoleFormatter(
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True
)
```

### Custom Handlers

```python
from wml.handlers import WebSocketHandler, MQTTHandler, RedisHandler

# WebSocket handler for real-time streaming
ws_handler = WebSocketHandler(
    host="0.0.0.0",
    port=8765,
    path="/logs"
)

# MQTT handler for pub/sub messaging
mqtt_handler = MQTTHandler(
    broker_url="mqtt://localhost:1883",
    topic="logs/my-service",
    qos=1,
    retain=False
)

# Redis handler for log storage
redis_handler = RedisHandler(
    redis_url="redis://localhost:6379/0",
    key_prefix="logs:",
    expire_seconds=86400
)
```

### Async Logging

```python
import asyncio
from wml import WMLLogger, LoggingConfig

async def async_application():
    config = LoggingConfig(
        service_name="async-service",
        websocket_enabled=True
    )
    
    logger = WMLLogger.get_logger(config)
    
    # Async logging with context
    async with logger.context(request_id="req-456"):
        logger.logger.info("Processing async request")
        
        # Simulate async work
        await asyncio.sleep(1)
        
        logger.logger.info("Async request completed")

# Run async application
asyncio.run(async_application())
```

## 🔌 Integration Examples

### Flask Application

```python
from flask import Flask, request
from wml import WMLLogger, LoggingConfig, LogContext

app = Flask(__name__)

# Initialize WML logger
config = LoggingConfig(
    service_name="flask-api",
    console_format="rich",
    websocket_enabled=True,
    mqtt_enabled=True,
    mqtt_broker="mqtt://localhost:1883"
)

logger = WMLLogger.get_logger(config)

@app.before_request
def log_request_info():
    logger.logger.info("Request started",
                      method=request.method,
                      url=request.url,
                      remote_addr=request.remote_addr)

@app.after_request
def log_response_info(response):
    logger.logger.info("Request completed",
                      status_code=response.status_code,
                      content_length=response.content_length)
    return response

@app.route('/api/health')
def health():
    logger.logger.info("Health check requested")
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Application

```python
from fastapi import FastAPI, Request
from wml import WMLLogger, LoggingConfig
import time

app = FastAPI()

# Initialize WML logger
config = LoggingConfig(
    service_name="fastapi-service",
    console_format="rich",
    websocket_enabled=True
)

logger = WMLLogger.get_logger(config)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.logger.info("Request started",
                      method=request.method,
                      url=str(request.url))
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.logger.info("Request completed",
                      status_code=response.status_code,
                      process_time=process_time)
    
    return response

@app.get("/")
async def root():
    logger.logger.info("Root endpoint accessed")
    return {"message": "Hello World"}
```

### Docker Integration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install WML
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables for WML
ENV WML_SERVICE_NAME=docker-service
ENV WML_LOG_LEVEL=info
ENV WML_CONSOLE_FORMAT=json
ENV WML_WEBSOCKET_ENABLED=true
ENV WML_WEBSOCKET_PORT=8765
ENV WML_MQTT_ENABLED=true
ENV WML_MQTT_BROKER=mqtt://mqtt-broker:1883

EXPOSE 8000 8765

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "8765:8765"
    environment:
      - WML_MQTT_BROKER=mqtt://mqtt:1883
    depends_on:
      - mqtt
      - redis

  mqtt:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  log-monitor:
    image: wml-cli
    command: wml monitor --broker mqtt:1883 --topic "logs/#"
    depends_on:
      - mqtt
```

## 📊 Monitoring and Observability

### Grafana Dashboard

WML integrates seamlessly with monitoring stacks:

```python
# Send metrics alongside logs
logger.logger.info("Request processed",
                  request_count=1,
                  response_time=0.045,
                  memory_usage=256.5,
                  cpu_percent=12.3)
```

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, Gauge
from wml import WMLLogger, LoggingConfig

# Prometheus metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage')

config = LoggingConfig(service_name="metrics-service")
logger = WMLLogger.get_logger(config)

def process_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    
    with REQUEST_DURATION.time():
        # Process request
        logger.logger.info("Request processed",
                          method=method,
                          endpoint=endpoint,
                          metrics_exported=True)
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e .[dev]

# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest tests/ --cov=wml --cov-report=html

# Test CLI commands
wml test
wml info
```

## 📚 API Reference

### Core Classes

- **`WMLLogger`**: Main logging class with structured logging support
- **`LoggingConfig`**: Configuration class for logger settings
- **`LogContext`**: Context enrichment for adding metadata to logs

### Formatters

- **`JSONFormatter`**: JSON output with structured data
- **`RichConsoleFormatter`**: Rich console output with colors and styling
- **`StructuredFormatter`**: Structured text format with key-value pairs
- **`CompactFormatter`**: Minimal compact format for high-volume logging

### Handlers

- **`WebSocketHandler`**: Real-time WebSocket broadcasting
- **`MQTTHandler`**: MQTT pub/sub messaging
- **`RedisHandler`**: Redis storage and retrieval
- **`BufferedHandler`**: Buffered output with configurable flushing

### Broadcasters

- **`WebSocketBroadcaster`**: WebSocket server for real-time log streaming
- **`MQTTBroadcaster`**: MQTT client for pub/sub log distribution

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/wml.git
cd wml

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [structlog](https://www.structlog.org/) for structured logging
- Uses [rich](https://github.com/Textualize/rich) for beautiful console output
- MQTT support via [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- WebSocket support via [aiohttp](https://aiohttp.readthedocs.io/) and [websockets](https://websockets.readthedocs.io/)

## 🔗 Related Projects

- **[ProServe](https://github.com/your-org/proserve)**: Microservice framework using WML
- **[Servos](https://github.com/your-org/servos)**: Environment isolation and Docker orchestration
- **[EDPMT](https://github.com/your-org/edpmt)**: Embedded development platform with WML integration

---

**WML** - Unifying logs across services, platforms, and environments. 🚀
