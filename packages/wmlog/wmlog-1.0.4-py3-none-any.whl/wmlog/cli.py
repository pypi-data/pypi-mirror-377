#!/usr/bin/env python3
"""
WML (Websocket MQTT Logging) CLI
Command-line interface for log management and monitoring
"""

import click
import asyncio
import json
import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import time
import yaml

# Import WML components
from .logging.core import WMLLogger, LoggingConfig, LogContext
from .mqtt.broadcaster import MQTTBroadcaster, WebSocketBroadcaster
from .formatters.structured import JSONFormatter, RichConsoleFormatter
from . import __version__


@click.group()
@click.version_option(__version__)
def cli():
    """WML (Websocket MQTT Logging) - Centralized logging system"""
    pass


@cli.command()
def version():
    """Show WML version"""
    click.echo(f"WML (Websocket MQTT Logging) v{__version__}")


@cli.command()
@click.option('--service-name', required=True, help='Service name to write into config')
@click.option('--config', 'config_path', required=True, help='Path to output YAML config')
def init(service_name: str, config_path: str):
    """Initialize a minimal WML configuration file"""
    cfg_dir = os.path.dirname(config_path)
    if cfg_dir and not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir, exist_ok=True)
    data = {
        'service_name': service_name,
        'log_level': 'INFO',
        'console_enabled': True,
        'file_enabled': True,
        'file_path': 'cli_test.log'
    }
    with open(config_path, 'w') as f:
        yaml.safe_dump(data, f, sort_keys=False)
    click.echo(f"✅ Configuration created at {config_path}")

@cli.command()
@click.option('--service', '-s', default='wml-cli', help='Service name')
@click.option('--level', '-l', default='INFO', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False),
              help='Log level')
@click.option('--format', '-f', default='rich',
              type=click.Choice(['json', 'rich', 'compact']),
              help='Output format')
@click.option('--file', help='Log to file')
@click.option('--config', 'config_path', help='Path to YAML/JSON config file')
@click.option('--message', 'message_opt', help='Log message (alternative to positional)')
@click.option('--mqtt-broker', help='MQTT broker URL')
@click.option('--mqtt-topic', default='wml/logs', help='MQTT topic')
@click.option('--websocket-port', type=int, default=8765, help='WebSocket port')
@click.argument('message', required=False)
def log(service: str, level: str, format: str, file: Optional[str], config_path: Optional[str],
        message_opt: Optional[str], mqtt_broker: Optional[str], mqtt_topic: str, websocket_port: int, message: Optional[str]):
    """Send a log message through WML"""
    # Resolve message
    msg = message_opt or message or ""
    
    # Load config if provided
    cfg = None
    cfg_dir = None
    if config_path and os.path.exists(config_path):
        cfg_dir = os.path.dirname(config_path)
        try:
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f)
        except Exception:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
    
    if cfg:
        # Adjust relative file_path to config directory
        fp = cfg.get('file_path')
        if fp and not os.path.isabs(fp) and cfg_dir:
            cfg['file_path'] = os.path.join(cfg_dir, fp)
        config = LoggingConfig(**cfg)
    else:
        config = LoggingConfig(
            service_name=service,
            log_level=level.upper(),
            console_format=format,
            file_enabled=bool(file),
            file_path=file,
            mqtt_enabled=bool(mqtt_broker),
            mqtt_broker=mqtt_broker or 'localhost:1883',
            mqtt_topic=mqtt_topic,
            websocket_enabled=True,
            websocket_port=websocket_port
        )
    
    logger = WMLLogger.get_logger(config)
    
    # Send log message
    level_func = getattr(logger.logger, level.lower())
    level_func(msg, command='wml-cli')
    
    click.echo(f"✅ Log message sent: {msg}")


@cli.command()
@click.option('--broker', '-b', default='localhost:1883', help='MQTT broker')
@click.option('--topic', '-t', default='wml/logs/#', help='MQTT topic pattern')
@click.option('--format', '-f', default='rich',
              type=click.Choice(['json', 'rich', 'compact']),
              help='Output format')
@click.option('--filter-service', help='Filter by service name')
@click.option('--filter-level', help='Filter by log level')
@click.option('--output', help='Save to file')
@click.option('--file', 'file_path', type=click.Path(exists=True), help='Tail a log file instead of MQTT')
@click.option('--lines', 'num_lines', type=int, default=10, help='Number of lines to show when using --file')
def monitor(broker: str, topic: str, format: str, 
           filter_service: Optional[str], filter_level: Optional[str], 
           output: Optional[str], file_path: Optional[str], num_lines: int):
    """Monitor log messages from MQTT broker or tail a file with --file"""
    # File tailing mode for tests
    if file_path:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()[-num_lines:]
            for line in lines:
                click.echo(line.strip())
            return
        except Exception as e:
            click.echo(f"❌ Error reading file: {e}", err=True)
            sys.exit(1)
    
    async def monitor_logs():
        try:
            # Create MQTT client for monitoring
            mqtt_client = MQTTBroadcaster(
                broker_host=broker.split(':')[0],
                broker_port=int(broker.split(':')[1]) if ':' in broker else 1883,
                topic_prefix=topic.replace('/#', '')
            )
            
            received_logs = []
            
            def on_message(client, userdata, message):
                try:
                    log_data = json.loads(message.payload.decode())
                    
                    # Apply filters
                    if filter_service and log_data.get('service') != filter_service:
                        return
                    if filter_level and log_data.get('level') != filter_level:
                        return
                    
                    # Format output
                    if format == 'json':
                        output_line = json.dumps(log_data, indent=2)
                    elif format == 'rich':
                        timestamp = log_data.get('timestamp', 'N/A')
                        service = log_data.get('service', 'unknown')
                        level = log_data.get('level', 'INFO')
                        message = log_data.get('message', '')
                        output_line = f"[{timestamp}] {service} [{level}] {message}"
                    else:  # compact
                        service = log_data.get('service', 'unknown')
                        level = log_data.get('level', 'INFO')
                        message = log_data.get('message', '')
                        output_line = f"{service}[{level}]: {message}"
                    
                    # Output
                    click.echo(output_line)
                    
                    # Save to file if specified
                    if output:
                        received_logs.append(output_line)
                        with open(output, 'a') as f:
                            f.write(output_line + '\n')
                            
                except Exception as e:
                    click.echo(f"Error processing message: {e}", err=True)
            
            # Setup MQTT client
            mqtt_client.start()
            mqtt_client.client.on_message = on_message
            mqtt_client.client.subscribe(topic)
            
            click.echo(f"🔍 Monitoring logs from {broker} on topic {topic}")
            click.echo("Press Ctrl+C to stop...")
            
            # Keep monitoring
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            click.echo("\n👋 Monitoring stopped")
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(monitor_logs())


@cli.command()
@click.option('--port', '-p', default=8765, type=int, help='WebSocket port')
@click.option('--host', '-h', default='localhost', help='WebSocket host')
@click.option('--format', '-f', default='json',
              type=click.Choice(['json', 'rich', 'compact']),
              help='Output format')
@click.option('--output', help='Save to file')
def websocket_monitor(port: int, host: str, format: str, output: Optional[str]):
    """Monitor log messages from WebSocket server"""
    
    async def monitor_websocket():
        try:
            import websockets
            
            uri = f"ws://{host}:{port}/logs"
            click.echo(f"🔗 Connecting to WebSocket at {uri}")
            
            received_logs = []
            
            async with websockets.connect(uri) as websocket:
                click.echo("✅ Connected! Monitoring logs...")
                click.echo("Press Ctrl+C to stop...")
                
                async for message in websocket:
                    try:
                        log_data = json.loads(message)
                        
                        # Format output
                        if format == 'json':
                            output_line = json.dumps(log_data, indent=2)
                        elif format == 'rich':
                            timestamp = log_data.get('timestamp', 'N/A')
                            service = log_data.get('service', 'unknown')
                            level = log_data.get('level', 'INFO')
                            msg = log_data.get('message', '')
                            output_line = f"[{timestamp}] {service} [{level}] {msg}"
                        else:  # compact
                            service = log_data.get('service', 'unknown')
                            level = log_data.get('level', 'INFO')
                            msg = log_data.get('message', '')
                            output_line = f"{service}[{level}]: {msg}"
                        
                        # Output
                        click.echo(output_line)
                        
                        # Save to file if specified
                        if output:
                            received_logs.append(output_line)
                            with open(output, 'a') as f:
                                f.write(output_line + '\n')
                                
                    except Exception as e:
                        click.echo(f"Error processing message: {e}", err=True)
                        
        except KeyboardInterrupt:
            click.echo("\n👋 Monitoring stopped")
        except Exception as e:
            click.echo(f"❌ Error connecting to WebSocket: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(monitor_websocket())


@cli.command()
@click.option('--config-file', '-c', help='Configuration file path')
def test(config_file: Optional[str]):
    """Test WML logging configuration"""
    
    click.echo("🧪 Testing WML logging configuration...")
    
    # Load config from file or use defaults
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        config = LoggingConfig(**config_data)
    else:
        config = LoggingConfig(
            service_name='wml-test',
            console_enabled=True,
            console_format='rich'
        )
    
    # Create logger
    logger = WMLLogger.get_logger(config)
    
    # Test different log levels
    test_messages = [
        ('debug', 'This is a debug message'),
        ('info', 'This is an info message'),
        ('warning', 'This is a warning message'),
        ('error', 'This is an error message'),
        ('critical', 'This is a critical message')
    ]
    
    click.echo("📝 Sending test log messages...")
    
    for level, message in test_messages:
        log_method = getattr(logger.logger, level)
        log_method(message, test_type='configuration_test')
        time.sleep(0.5)  # Small delay for readability
    
    click.echo("✅ Test completed!")


@cli.command()
@click.option('--service', '-s', default='wml-server', help='Service name')
@click.option('--mqtt-broker', help='MQTT broker URL')
@click.option('--mqtt-topic', default='wml/logs', help='MQTT topic')
@click.option('--websocket-port', type=int, default=8765, help='WebSocket port')
@click.option('--websocket-host', default='localhost', help='WebSocket host')
def server(service: str, mqtt_broker: Optional[str], mqtt_topic: str, 
          websocket_port: int, websocket_host: str):
    """Start WML log broadcasting server"""
    
    async def start_server():
        broadcasters = []
        
        try:
            # Start WebSocket broadcaster
            click.echo(f"🚀 Starting WebSocket server on {websocket_host}:{websocket_port}")
            ws_broadcaster = WebSocketBroadcaster(
                host=websocket_host,
                port=websocket_port
            )
            await ws_broadcaster.start()
            broadcasters.append(ws_broadcaster)
            
            # Start MQTT broadcaster if configured
            if mqtt_broker:
                click.echo(f"📡 Starting MQTT broadcaster on {mqtt_broker}")
                mqtt_broadcaster = MQTTBroadcaster(
                    broker_url=mqtt_broker,
                    topic_prefix=mqtt_topic
                )
                await mqtt_broadcaster.start()
                broadcasters.append(mqtt_broadcaster)
            
            click.echo("✅ WML server started successfully!")
            click.echo("Press Ctrl+C to stop...")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            click.echo("\n🛑 Shutting down WML server...")
            
            # Stop all broadcasters
            for broadcaster in broadcasters:
                try:
                    await broadcaster.stop()
                except Exception as e:
                    click.echo(f"Warning: Error stopping broadcaster: {e}")
            
            click.echo("👋 WML server stopped")
            
        except Exception as e:
            click.echo(f"❌ Server error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(start_server())


@cli.command()
def info():
    """Show WML package information"""
    
    click.echo(f"""
🔧 WML (Websocket MQTT Logging) v{__version__}

📋 Package Information:
  • Centralized logging system with structured logging
  • WebSocket and MQTT broadcasting support
  • Rich console output with multiple formatters
  • Redis backend integration
  • Custom handlers for various outputs

🌐 Components:
  • Core Logging: WMLLogger with structured logging
  • Broadcasters: MQTT and WebSocket real-time streaming
  • Formatters: JSON, Rich Console, Compact, Structured
  • Handlers: WebSocket, MQTT, Redis, File handlers
  • CLI: Management and monitoring tools

📖 Usage Examples:
  wml log "Hello World"                    # Send log message
  wml monitor --broker localhost:1883      # Monitor MQTT logs
  wml websocket-monitor --port 8765        # Monitor WebSocket logs
  wml test                                 # Test configuration
  wml server                               # Start broadcasting server

📚 Documentation: https://github.com/your-org/wml
🐛 Issues: https://github.com/your-org/wml/issues
""")


if __name__ == '__main__':
    cli()
