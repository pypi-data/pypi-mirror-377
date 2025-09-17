"""
WML Core Logging System
======================

Centralized logging system with structured logging, WebSocket broadcasting,
MQTT integration, and rich console output.

Extracted and enhanced from ProServe and EDPMT logging systems.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Set, List, Union
from datetime import datetime
from pathlib import Path
import threading
from dataclasses import dataclass, asdict, field
from logging.handlers import RotatingFileHandler as StdRotatingFileHandler

# Core structured logging imports
import structlog
from structlog import configure, get_logger
from structlog.processors import JSONRenderer, TimeStamper, add_log_level, CallsiteParameterAdder

# Optional rich console support
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install as install_rich_traceback
    RICH_AVAILABLE = True
    install_rich_traceback()
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    RichHandler = None

# Optional WebSocket support for log broadcasting
try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import WebSocketResponse
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


@dataclass
class LogContext:
    """Enhanced context information for log entries"""
    service_name: str
    version: Optional[str] = None
    environment: Optional[str] = None
    manifest_file: Optional[str] = None
    handler_script: Optional[str] = None
    shell_command: Optional[str] = None
    isolation_mode: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for structured logging"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class LoggingConfig:
    """Enhanced logging configuration"""
    
    # Basic settings
    service_name: str
    log_level: str = "INFO"
    environment: str = "development"
    version: Optional[str] = None
    
    # Console logging
    console_enabled: bool = True
    console_format: str = "rich"  # "rich", "json", "simple"
    console_level: Optional[str] = None
    
    # File logging
    file_enabled: bool = True
    file_path: Optional[str] = None
    file_level: Optional[str] = None
    file_format: str = "json"  # "json", "text"
    file_rotation: str = "size"  # "size", "time", "none"
    file_max_size: str = "100MB"
    file_backup_count: int = 5
    
    # WebSocket broadcasting
    websocket_enabled: bool = False
    websocket_port: int = 8080
    websocket_path: str = "/ws/logs"
    websocket_level: Optional[str] = None
    
    # MQTT broadcasting  
    mqtt_enabled: bool = False
    mqtt_broker: Optional[str] = None
    mqtt_port: int = 1883
    mqtt_topic: Optional[str] = None
    mqtt_qos: int = 1
    mqtt_level: Optional[str] = None
    
    # Structured logging
    structured_enabled: bool = True
    include_caller: bool = True
    include_timestamp: bool = True
    timestamp_format: str = "iso"
    
    # Context enrichment
    include_process_info: bool = True
    include_thread_info: bool = True
    include_system_info: bool = False
    
    # Advanced features
    correlation_tracking: bool = True
    sampling_rate: float = 1.0  # 0.0 to 1.0
    buffer_size: int = 1000
    flush_interval: float = 5.0
    
    def __post_init__(self):
        """Post-initialization validation and defaults"""
        # Set default file path
        if self.file_enabled and not self.file_path:
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            self.file_path = str(logs_dir / f"{self.service_name}.log")
        
        # Set default MQTT topic
        if self.mqtt_enabled and not self.mqtt_topic:
            self.mqtt_topic = f"logs/{self.service_name}"
        
        # Validate log levels
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log_level: {self.log_level}")


class WMLLogger:
    """
    WML (Websocket MQTT Logging) centralized logger
    
    Enhanced logging system with structured logging, WebSocket broadcasting,
    MQTT integration, and rich console output.
    """
    
    _instances: Dict[str, 'WMLLogger'] = {}
    _lock = threading.Lock()
    
    def __init__(self, config: LoggingConfig, context: Optional[LogContext] = None):
        self.config = config
        self.context = context or LogContext(service_name=config.service_name)
        self.logger = None
        self._websocket_connections: Set[Any] = set()
        self._mqtt_client = None
        self._setup_complete = False
        
        # Initialize logging system
        self._setup_logging()
    
    @classmethod
    def get_logger(cls, config: LoggingConfig, context: Optional[LogContext] = None) -> 'WMLLogger':
        """Get or create a WML logger instance (singleton per service)"""
        service_name = config.service_name
        
        with cls._lock:
            if service_name not in cls._instances:
                cls._instances[service_name] = cls(config, context)
            return cls._instances[service_name]
    
    def _setup_logging(self):
        """Setup structured logging with all configured outputs"""
        if self._setup_complete:
            return
            
        # Build processors chain
        processors = []
        
        if self.config.include_timestamp:
            processors.append(TimeStamper(fmt="iso" if self.config.timestamp_format == "iso" else None))
        
        if self.config.include_caller:
            processors.append(CallsiteParameterAdder(
                parameters=[structlog.processors.CallsiteParameter.FILENAME,
                           structlog.processors.CallsiteParameter.FUNC_NAME,
                           structlog.processors.CallsiteParameter.LINENO]
            ))
        
        processors.append(add_log_level)
        processors.append(self._add_context_processor)
        
        # Setup output handlers
        handlers = []
        
        # Console handler
        if self.config.console_enabled:
            console_handler = self._setup_console_handler()
            if console_handler:
                handlers.append(console_handler)
        
        # File handler
        if self.config.file_enabled:
            file_handler = self._setup_file_handler()
            if file_handler:
                handlers.append(file_handler)
        
        # Configure structlog
        if self.config.console_format == "json" or not RICH_AVAILABLE:
            processors.append(JSONRenderer())
        else:
            # Use ProcessorFormatter for non-JSON output
            processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)
        
        configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, self.config.log_level.upper())
            ),
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Add handlers to root logger
        for handler in handlers:
            root_logger.addHandler(handler)
        
        # Get structured logger
        self.logger = get_logger(self.config.service_name)
        
        # Setup broadcasting if enabled
        if self.config.websocket_enabled:
            try:
                asyncio.create_task(self._setup_websocket_broadcasting())
            except RuntimeError:
                # No event loop running - WebSocket broadcasting will be disabled
                # This is normal during testing or non-async usage
                pass
        
        if self.config.mqtt_enabled:
            self._setup_mqtt_broadcasting()
        
        self._setup_complete = True
    
    def _add_context_processor(self, logger, method_name, event_dict):
        """Add context information to log entries"""
        if self.context:
            event_dict.update(self.context.to_dict())
        
        # Add process/thread info if enabled
        if self.config.include_process_info:
            event_dict["process_id"] = os.getpid()
        
        if self.config.include_thread_info:
            event_dict["thread_id"] = threading.get_ident()
        
        return event_dict
    
    def _setup_console_handler(self) -> Optional[logging.Handler]:
        """Setup console handler with Rich support"""
        level = self.config.console_level or self.config.log_level
        
        if self.config.console_format == "rich" and RICH_AVAILABLE:
            handler = RichHandler(
                console=Console(stderr=True),
                show_time=True,
                show_level=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True
            )
        else:
            handler = logging.StreamHandler(sys.stderr)
            if self.config.console_format == "json":
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            handler.setFormatter(formatter)
        
        handler.setLevel(logging.getLevelName(level.upper()))
        return handler
    
    def _setup_file_handler(self) -> Optional[logging.Handler]:
        """Setup file handler with rotation"""
        if not self.config.file_path:
            return None
            
        level = self.config.file_level or self.config.log_level
        
        # Create log directory if it doesn't exist
        log_path = Path(self.config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.file_rotation == "size":
            # Parse size string (e.g., "100MB")
            size_str = self.config.file_max_size.upper()
            if size_str.endswith('KB'):
                max_bytes = int(size_str[:-2]) * 1024
            elif size_str.endswith('MB'):
                max_bytes = int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith('GB'):
                max_bytes = int(size_str[:-2]) * 1024 * 1024 * 1024
            else:
                max_bytes = int(size_str)
            
            handler = StdRotatingFileHandler(
                filename=self.config.file_path,
                maxBytes=max_bytes,
                backupCount=self.config.file_backup_count
            )
        else:
            handler = logging.FileHandler(self.config.file_path)
        
        # Set formatter
        if self.config.file_format == "json":
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        handler.setLevel(logging.getLevelName(level.upper()))
        return handler
    
    async def _setup_websocket_broadcasting(self):
        """Setup WebSocket server for log broadcasting"""
        if not WEBSOCKET_AVAILABLE:
            self.logger.warning("WebSocket support not available - install aiohttp")
            return
        
        # Implementation will be in the WebSocket handler module
        pass
    
    def _setup_mqtt_broadcasting(self):
        """Setup MQTT client for log broadcasting"""
        # Implementation will be in the MQTT handler module
        pass
    
    def update_context(self, **kwargs):
        """Update logging context"""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)
            else:
                self.context.custom_fields[key] = value
    
    def bind(self, **kwargs) -> structlog.BoundLogger:
        """Bind additional context to logger"""
        return self.logger.bind(**kwargs)
    
    # Convenience logging methods
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, **kwargs)


# Global logger instance for simple usage
_global_logger: Optional[WMLLogger] = None

def setup_global_logger(config: LoggingConfig, context: Optional[LogContext] = None):
    """Setup global WML logger instance"""
    global _global_logger
    _global_logger = WMLLogger.get_logger(config, context)

def get_global_logger() -> Optional[WMLLogger]:
    """Get global WML logger instance"""
    return _global_logger

# Convenience functions for global logger
def debug(message: str, **kwargs):
    """Log debug message using global logger"""
    if _global_logger:
        _global_logger.debug(message, **kwargs)

def info(message: str, **kwargs):
    """Log info message using global logger"""
    if _global_logger:
        _global_logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message using global logger"""
    if _global_logger:
        _global_logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log error message using global logger"""
    if _global_logger:
        _global_logger.error(message, **kwargs)

def critical(message: str, **kwargs):
    """Log critical message using global logger"""
    if _global_logger:
        _global_logger.critical(message, **kwargs)
