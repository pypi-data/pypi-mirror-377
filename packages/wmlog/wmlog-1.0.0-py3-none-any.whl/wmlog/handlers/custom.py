"""
WML Custom Logging Handlers
===========================

Advanced logging handlers for various destinations including WebSocket broadcasting,
MQTT publishing, Redis caching, and enhanced file handling with buffering.
"""

import json
import logging
import asyncio
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
import time
from logging.handlers import RotatingFileHandler as StdRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler as StdTimedRotatingFileHandler

# Optional Redis support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Import WML components
from ..mqtt.broadcaster import LogMessage, WebSocketBroadcaster, MQTTBroadcaster


class WebSocketHandler(logging.Handler):
    """
    Logging handler that broadcasts log messages via WebSocket
    Integrates with WML WebSocketBroadcaster
    """
    
    def __init__(self, broadcaster: Optional[WebSocketBroadcaster] = None, 
                 service_name: str = "unknown", 
                 buffer_size: int = 100,
                 flush_interval: float = 1.0):
        super().__init__()
        self.broadcaster = broadcaster
        self.service_name = service_name
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._buffer: List[LogMessage] = []
        self._last_flush = time.time()
        self._lock = threading.Lock()
        
        # Start flush timer if we have a broadcaster
        if self.broadcaster:
            self._start_flush_timer()
    
    def set_broadcaster(self, broadcaster: WebSocketBroadcaster):
        """Set the WebSocket broadcaster"""
        self.broadcaster = broadcaster
        self._start_flush_timer()
    
    def _start_flush_timer(self):
        """Start periodic flush timer"""
        def flush_timer():
            while True:
                time.sleep(self.flush_interval)
                self._flush_buffer()
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record via WebSocket"""
        if not self.broadcaster:
            return
        
        try:
            # Create log message
            log_message = LogMessage(
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
                level=record.levelname,
                service_name=self.service_name,
                message=record.getMessage(),
                logger_name=record.name,
                thread_name=getattr(record, 'threadName', None),
                process_id=getattr(record, 'process', None),
                correlation_id=getattr(record, 'correlation_id', None),
                trace_id=getattr(record, 'trace_id', None),
                extra_data=self._extract_extra_data(record)
            )
            
            # Add to buffer
            with self._lock:
                self._buffer.append(log_message)
                
                # Flush if buffer is full
                if len(self._buffer) >= self.buffer_size:
                    self._flush_buffer_unsafe()
        
        except Exception as e:
            self.handleError(record)
    
    def _extract_extra_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract extra data from log record"""
        extra_data = {}
        
        # Standard fields to exclude
        standard_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'message'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_fields:
                try:
                    # Ensure value is JSON serializable
                    json.dumps(value)
                    extra_data[key] = value
                except (TypeError, ValueError):
                    extra_data[key] = str(value)
        
        return extra_data
    
    def _flush_buffer(self):
        """Flush buffer with locking"""
        with self._lock:
            self._flush_buffer_unsafe()
    
    def _flush_buffer_unsafe(self):
        """Flush buffer without locking (unsafe)"""
        if not self._buffer or not self.broadcaster:
            return
        
        # Send all buffered messages
        for log_message in self._buffer:
            try:
                # Use asyncio to broadcast
                asyncio.create_task(self.broadcaster.broadcast_log(log_message))
            except Exception as e:
                # Can't use logging here to avoid recursion
                print(f"WebSocket broadcast error: {e}")
        
        self._buffer.clear()
        self._last_flush = time.time()
    
    def close(self):
        """Close handler and flush buffer"""
        self._flush_buffer()
        super().close()


class MQTTHandler(logging.Handler):
    """
    Logging handler that publishes log messages via MQTT
    Integrates with WML MQTTBroadcaster
    """
    
    def __init__(self, broadcaster: Optional[MQTTBroadcaster] = None,
                 service_name: str = "unknown",
                 buffer_size: int = 50,
                 flush_interval: float = 2.0):
        super().__init__()
        self.broadcaster = broadcaster
        self.service_name = service_name
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._buffer: List[LogMessage] = []
        self._last_flush = time.time()
        self._lock = threading.Lock()
        
        if self.broadcaster:
            self._start_flush_timer()
    
    def set_broadcaster(self, broadcaster: MQTTBroadcaster):
        """Set the MQTT broadcaster"""
        self.broadcaster = broadcaster
        self._start_flush_timer()
    
    def _start_flush_timer(self):
        """Start periodic flush timer"""
        def flush_timer():
            while True:
                time.sleep(self.flush_interval)
                self._flush_buffer()
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record via MQTT"""
        if not self.broadcaster:
            return
        
        try:
            # Create log message
            log_message = LogMessage(
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
                level=record.levelname,
                service_name=self.service_name,
                message=record.getMessage(),
                logger_name=record.name,
                thread_name=getattr(record, 'threadName', None),
                process_id=getattr(record, 'process', None),
                correlation_id=getattr(record, 'correlation_id', None),
                trace_id=getattr(record, 'trace_id', None),
                extra_data=self._extract_extra_data(record)
            )
            
            # Add to buffer
            with self._lock:
                self._buffer.append(log_message)
                
                # Flush if buffer is full
                if len(self._buffer) >= self.buffer_size:
                    self._flush_buffer_unsafe()
        
        except Exception as e:
            self.handleError(record)
    
    def _extract_extra_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract extra data from log record"""
        extra_data = {}
        
        standard_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'message'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_fields:
                try:
                    json.dumps(value)
                    extra_data[key] = value
                except (TypeError, ValueError):
                    extra_data[key] = str(value)
        
        return extra_data
    
    def _flush_buffer(self):
        """Flush buffer with locking"""
        with self._lock:
            self._flush_buffer_unsafe()
    
    def _flush_buffer_unsafe(self):
        """Flush buffer without locking (unsafe)"""
        if not self._buffer or not self.broadcaster:
            return
        
        for log_message in self._buffer:
            try:
                self.broadcaster.broadcast_log(log_message)
            except Exception as e:
                print(f"MQTT broadcast error: {e}")
        
        self._buffer.clear()
        self._last_flush = time.time()
    
    def close(self):
        """Close handler and flush buffer"""
        self._flush_buffer()
        super().close()


class RedisHandler(logging.Handler):
    """
    Logging handler that stores log messages in Redis
    Useful for centralized log aggregation and analysis
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0",
                 key_prefix: str = "logs",
                 service_name: str = "unknown",
                 max_entries: int = 10000,
                 ttl_seconds: Optional[int] = None,
                 buffer_size: int = 100):
        super().__init__()
        
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis handler requires 'redis' package")
        
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.service_name = service_name
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.buffer_size = buffer_size
        
        # Connect to Redis
        self.redis_client = redis.from_url(redis_url)
        
        # Test connection
        try:
            self.redis_client.ping()
        except Exception as e:
            raise RuntimeError(f"Cannot connect to Redis: {e}")
        
        # Buffer for batch operations
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to Redis"""
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "service_name": self.service_name,
                "logger": record.name,
                "message": record.getMessage(),
                "source": {
                    "filename": record.filename,
                    "function": record.funcName,
                    "line": record.lineno
                }
            }
            
            # Add extra fields
            extra_data = {}
            standard_fields = {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
                'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'message'
            }
            
            for key, value in record.__dict__.items():
                if key not in standard_fields:
                    try:
                        json.dumps(value)
                        extra_data[key] = value
                    except (TypeError, ValueError):
                        extra_data[key] = str(value)
            
            if extra_data:
                log_entry["extra"] = extra_data
            
            # Exception info
            if record.exc_info:
                log_entry["exception"] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": self.format(record)
                }
            
            # Add to buffer
            with self._lock:
                self._buffer.append(log_entry)
                
                # Flush if buffer is full
                if len(self._buffer) >= self.buffer_size:
                    self._flush_buffer_unsafe()
        
        except Exception as e:
            self.handleError(record)
    
    def _flush_buffer_unsafe(self):
        """Flush buffer to Redis (unsafe)"""
        if not self._buffer:
            return
        
        try:
            # Redis key
            redis_key = f"{self.key_prefix}:{self.service_name}"
            
            # Use pipeline for efficiency
            pipe = self.redis_client.pipeline()
            
            # Add all log entries
            for log_entry in self._buffer:
                pipe.lpush(redis_key, json.dumps(log_entry))
            
            # Trim list to max entries
            pipe.ltrim(redis_key, 0, self.max_entries - 1)
            
            # Set TTL if specified
            if self.ttl_seconds:
                pipe.expire(redis_key, self.ttl_seconds)
            
            # Execute pipeline
            pipe.execute()
            
            self._buffer.clear()
        
        except Exception as e:
            print(f"Redis flush error: {e}")
    
    def flush(self):
        """Manually flush buffer"""
        with self._lock:
            self._flush_buffer_unsafe()
    
    def close(self):
        """Close handler and flush buffer"""
        self.flush()
        if self.redis_client:
            self.redis_client.close()
        super().close()


class RotatingFileHandler(StdRotatingFileHandler):
    """
    Enhanced rotating file handler with JSON formatting and metadata
    """
    
    def __init__(self, filename: Union[str, Path], 
                 maxBytes: int = 0, 
                 backupCount: int = 0,
                 encoding: Optional[str] = None,
                 delay: bool = False,
                 errors: Optional[str] = None,
                 json_format: bool = True,
                 include_metadata: bool = True):
        super().__init__(filename, maxBytes, backupCount, encoding, delay, errors)
        self.json_format = json_format
        self.include_metadata = include_metadata
    
    def emit(self, record: logging.LogRecord):
        """Emit a record with enhanced formatting"""
        if self.json_format:
            # Format as JSON
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            if self.include_metadata:
                log_data.update({
                    "source": {
                        "filename": record.filename,
                        "function": record.funcName,
                        "line": record.lineno
                    },
                    "process": record.process,
                    "thread": record.thread
                })
            
            # Add extra fields
            extra_data = {}
            standard_fields = {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
                'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'message'
            }
            
            for key, value in record.__dict__.items():
                if key not in standard_fields:
                    try:
                        json.dumps(value)
                        extra_data[key] = value
                    except (TypeError, ValueError):
                        extra_data[key] = str(value)
            
            if extra_data:
                log_data["extra"] = extra_data
            
            # Exception info
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            # Override record message with JSON
            record.msg = json.dumps(log_data)
            record.args = ()
        
        super().emit(record)


class TimedRotatingFileHandler(StdTimedRotatingFileHandler):
    """
    Enhanced timed rotating file handler with JSON formatting
    """
    
    def __init__(self, filename: Union[str, Path], 
                 when: str = 'h', 
                 interval: int = 1,
                 backupCount: int = 0, 
                 encoding: Optional[str] = None,
                 delay: bool = False, 
                 utc: bool = False,
                 atTime: Optional[datetime] = None,
                 errors: Optional[str] = None,
                 json_format: bool = True):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime, errors)
        self.json_format = json_format
    
    def emit(self, record: logging.LogRecord):
        """Emit a record with JSON formatting"""
        if self.json_format:
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "source": {
                    "filename": record.filename,
                    "function": record.funcName,
                    "line": record.lineno
                }
            }
            
            # Exception info
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            record.msg = json.dumps(log_data)
            record.args = ()
        
        super().emit(record)


class BufferedHandler(logging.Handler):
    """
    Buffered handler that can batch log records for efficiency
    """
    
    def __init__(self, target_handler: logging.Handler,
                 buffer_size: int = 100, 
                 flush_interval: float = 5.0,
                 flush_level: int = logging.ERROR):
        super().__init__()
        self.target_handler = target_handler
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.flush_level = flush_level
        
        self._buffer: List[logging.LogRecord] = []
        self._last_flush = time.time()
        self._lock = threading.Lock()
        
        # Start flush timer
        self._start_flush_timer()
    
    def _start_flush_timer(self):
        """Start periodic flush timer"""
        def flush_timer():
            while True:
                time.sleep(self.flush_interval)
                current_time = time.time()
                if current_time - self._last_flush >= self.flush_interval:
                    self.flush()
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def emit(self, record: logging.LogRecord):
        """Add record to buffer"""
        with self._lock:
            self._buffer.append(record)
            
            # Force flush on high-priority logs or full buffer
            if record.levelno >= self.flush_level or len(self._buffer) >= self.buffer_size:
                self._flush_unsafe()
    
    def _flush_unsafe(self):
        """Flush buffer without locking"""
        if not self._buffer:
            return
        
        # Send all buffered records to target handler
        for record in self._buffer:
            try:
                self.target_handler.emit(record)
            except Exception:
                self.target_handler.handleError(record)
        
        self._buffer.clear()
        self._last_flush = time.time()
    
    def flush(self):
        """Manually flush buffer"""
        with self._lock:
            self._flush_unsafe()
    
    def close(self):
        """Close handler and flush buffer"""
        self.flush()
        self.target_handler.close()
        super().close()
