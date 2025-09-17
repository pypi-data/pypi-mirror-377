"""
WML (Websocket MQTT Logging) - Centralized Logging System
=========================================================

A comprehensive logging system for distributed applications with real-time
WebSocket broadcasting, MQTT integration, and structured logging capabilities.

Example Usage:
    Basic logging setup:
    
    >>> from wmlog import WMLLogger, LoggingConfig
    >>> config = LoggingConfig(service_name="my-service")
    >>> logger = WMLLogger.get_logger(config)
    >>> logger.info("Hello WML!", extra={"component": "main"})
    
    WebSocket broadcasting:
    
    >>> from wmlog.mqtt import MQTTBroadcaster
    >>> broadcaster = MQTTBroadcaster("mqtt://localhost:1883")
    >>> await broadcaster.start()
    >>> logger.info("This will be broadcast via MQTT")
    
    Rich console logging:
    
    >>> from wmlog.formatters import RichConsoleFormatter
    >>> config = LoggingConfig(
    ...     service_name="my-service",
    ...     console_formatter=RichConsoleFormatter()
    ... )
"""

__version__ = "1.0.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"
__license__ = "Apache-2.0"

# Core exports
from .logging import WMLLogger, LoggingConfig, LogContext
from .mqtt import MQTTBroadcaster, WebSocketBroadcaster
from .formatters import (
    JSONFormatter, 
    RichConsoleFormatter, 
    StructuredFormatter,
    CompactFormatter
)
from .handlers import (
    WebSocketHandler,
    MQTTHandler, 
    RotatingFileHandler,
    TimedRotatingFileHandler,
    RedisHandler
)

# Make key classes available at package level 
__all__ = [
    # Core classes
    "WMLLogger",
    "LoggingConfig", 
    "LogContext",
    
    # Broadcasting
    "MQTTBroadcaster",
    "WebSocketBroadcaster",
    
    # Formatters
    "JSONFormatter",
    "RichConsoleFormatter", 
    "StructuredFormatter",
    "CompactFormatter",
    
    # Handlers
    "WebSocketHandler",
    "MQTTHandler",
    "RotatingFileHandler", 
    "TimedRotatingFileHandler",
    "RedisHandler",
    
    # Package info
    "__version__"
]
