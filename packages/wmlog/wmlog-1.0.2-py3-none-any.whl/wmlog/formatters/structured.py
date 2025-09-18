"""
WML Structured Formatters
=========================

Advanced formatting classes for structured logging output with support for
JSON, Rich console, compact formats, and custom structured formats.
"""

import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
import sys

# Optional rich support
try:
    from rich.console import Console
    from rich.text import Text
    from rich.logging import RichHandler
    from rich.highlighter import ReprHighlighter
    from rich.traceback import Traceback
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Text = None
    RichHandler = None
    ReprHighlighter = None
    Traceback = None


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging output
    Produces clean, parseable JSON logs for centralized logging systems
    """
    
    def __init__(self, 
                 include_timestamp: bool = True,
                 include_level: bool = True,
                 include_logger_name: bool = True,
                 include_process_info: bool = False,
                 include_thread_info: bool = False,
                 timestamp_format: str = "iso",
                 indent: Optional[int] = None,
                 ensure_ascii: bool = False):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_logger_name = include_logger_name
        self.include_process_info = include_process_info
        self.include_thread_info = include_thread_info
        self.timestamp_format = timestamp_format
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {}
        
        # Basic message
        log_data["message"] = record.getMessage()
        
        # Timestamp
        if self.include_timestamp:
            if self.timestamp_format == "iso":
                log_data["timestamp"] = datetime.fromtimestamp(record.created).isoformat()
            elif self.timestamp_format == "epoch":
                log_data["timestamp"] = record.created
            else:
                log_data["timestamp"] = self.formatTime(record)
        
        # Level
        if self.include_level:
            log_data["level"] = record.levelname
            log_data["level_no"] = record.levelno
        
        # Logger name
        if self.include_logger_name:
            log_data["logger"] = record.name
        
        # Process/thread info
        if self.include_process_info:
            log_data["process_id"] = record.process
            log_data["process_name"] = record.processName
        
        if self.include_thread_info:
            log_data["thread_id"] = record.thread
            log_data["thread_name"] = record.threadName
        
        # Source location
        log_data["source"] = {
            "filename": record.filename,
            "function": record.funcName,
            "line": record.lineno,
            "module": record.module,
            "pathname": record.pathname
        }
        
        # Exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from record
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message'):
                extra_fields[key] = value
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        return json.dumps(log_data, indent=self.indent, ensure_ascii=self.ensure_ascii)


class StructuredFormatter(logging.Formatter):
    """
    Human-readable structured formatter with key-value pairs
    Good balance between readability and structure
    """
    
    def __init__(self,
                 include_timestamp: bool = True,
                 include_level: bool = True,
                 include_source: bool = True,
                 timestamp_format: str = "%Y-%m-%d %H:%M:%S",
                 field_separator: str = " | ",
                 key_value_separator: str = "="):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_source = include_source
        self.timestamp_format = timestamp_format
        self.field_separator = field_separator
        self.key_value_separator = key_value_separator
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured key-value pairs"""
        parts = []
        
        # Timestamp
        if self.include_timestamp:
            timestamp = datetime.fromtimestamp(record.created).strftime(self.timestamp_format)
            parts.append(f"time{self.key_value_separator}{timestamp}")
        
        # Level
        if self.include_level:
            parts.append(f"level{self.key_value_separator}{record.levelname}")
        
        # Logger name
        parts.append(f"logger{self.key_value_separator}{record.name}")
        
        # Source location
        if self.include_source:
            parts.append(f"source{self.key_value_separator}{record.filename}:{record.lineno}")
        
        # Message
        parts.append(f"msg{self.key_value_separator}{record.getMessage()}")
        
        # Extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message'):
                if isinstance(value, (str, int, float, bool)):
                    parts.append(f"{key}{self.key_value_separator}{value}")
                else:
                    parts.append(f"{key}{self.key_value_separator}{json.dumps(value)}")
        
        # Exception info
        if record.exc_info:
            parts.append(f"exception{self.key_value_separator}{record.exc_info[0].__name__}")
        
        result = self.field_separator.join(parts)
        
        # Add exception traceback if present
        if record.exc_info:
            result += "\n" + self.formatException(record.exc_info)
        
        return result


class CompactFormatter(logging.Formatter):
    """
    Ultra-compact formatter for high-volume logging
    Minimal overhead, maximum information density
    """
    
    def __init__(self, 
                 include_microseconds: bool = True,
                 level_width: int = 1):  # W, E, I, D, C for WARN, ERROR, INFO, DEBUG, CRITICAL
        super().__init__()
        self.include_microseconds = include_microseconds
        self.level_width = level_width
        
        # Level abbreviations
        self.level_abbrev = {
            "DEBUG": "D",
            "INFO": "I", 
            "WARNING": "W",
            "ERROR": "E",
            "CRITICAL": "C"
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record in ultra-compact format"""
        # Timestamp (compact)
        dt = datetime.fromtimestamp(record.created)
        if self.include_microseconds:
            timestamp = dt.strftime("%H:%M:%S.%f")[:-3]  # milliseconds
        else:
            timestamp = dt.strftime("%H:%M:%S")
        
        # Level (abbreviated)
        level = self.level_abbrev.get(record.levelname, record.levelname[0])
        
        # Source (compact)
        source = f"{record.filename}:{record.lineno}"
        
        # Message
        message = record.getMessage()
        
        # Compact format: TIME LEVEL SOURCE MESSAGE
        result = f"{timestamp} {level} {source} {message}"
        
        # Add extra fields compactly
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message'):
                if isinstance(value, (str, int, float, bool)):
                    extra_fields.append(f"{key}={value}")
        
        if extra_fields:
            result += f" [{','.join(extra_fields)}]"
        
        return result


class RichConsoleFormatter(logging.Formatter):
    """
    Rich console formatter with colors, highlighting, and beautiful output
    Best for development and interactive use
    """
    
    def __init__(self,
                 console: Optional[Console] = None,
                 show_time: bool = True,
                 show_level: bool = True,
                 show_path: bool = True,
                 enable_link_path: bool = True,
                 highlighter: Optional[ReprHighlighter] = None,
                 markup: bool = False,
                 rich_tracebacks: bool = True,
                 tracebacks_width: Optional[int] = None,
                 tracebacks_extra_lines: int = 3,
                 tracebacks_theme: Optional[str] = None,
                 tracebacks_word_wrap: bool = False,
                 tracebacks_show_locals: bool = False,
                 tracebacks_suppress: Optional[list] = None):
        super().__init__()
        
        if not RICH_AVAILABLE:
            raise RuntimeError("Rich console formatter requires 'rich' package")
        
        self.console = console if console is not None else Console(file=sys.stderr)
        self.show_time = show_time
        self.show_level = show_level
        self.show_path = show_path
        self.enable_link_path = enable_link_path
        self.highlighter = highlighter if highlighter is not None else ReprHighlighter()
        self.markup = markup
        self.rich_tracebacks = rich_tracebacks
        self.tracebacks_width = tracebacks_width
        self.tracebacks_extra_lines = tracebacks_extra_lines
        self.tracebacks_theme = tracebacks_theme
        self.tracebacks_word_wrap = tracebacks_word_wrap
        self.tracebacks_show_locals = tracebacks_show_locals
        self.tracebacks_suppress = tracebacks_suppress or []
        
        # Level colors
        self.level_colors = {
            "DEBUG": "dim blue",
            "INFO": "dim green", 
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold red"
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with Rich styling"""
        # This formatter is primarily used with RichHandler
        # So we return the plain message and let RichHandler do the formatting
        return record.getMessage()
    
    def emit_rich(self, record: logging.LogRecord, console: Optional[Console] = None) -> None:
        """Emit log record using Rich console (for custom handlers)"""
        console = console or self.console
        
        # Build message parts
        message_parts = []
        
        # Timestamp
        if self.show_time:
            timestamp = datetime.fromtimestamp(record.created)
            time_text = Text(timestamp.strftime("%H:%M:%S.%f")[:-3], style="dim")
            message_parts.append(time_text)
        
        # Level
        if self.show_level:
            level_color = self.level_colors.get(record.levelname, "white")
            level_text = Text(f"[{record.levelname}]", style=level_color)
            message_parts.append(level_text)
        
        # Logger name
        logger_text = Text(record.name, style="dim cyan")
        message_parts.append(logger_text)
        
        # Source path
        if self.show_path:
            path_text = f"{record.filename}:{record.lineno}"
            if self.enable_link_path:
                path_text = Text(path_text, style=f"link file://{record.pathname}")
            else:
                path_text = Text(path_text, style="dim")
            message_parts.append(path_text)
        
        # Message
        message = record.getMessage()
        if self.highlighter:
            message_text = self.highlighter(message)
        else:
            message_text = Text(message)
        
        # Combine parts
        final_message = Text(" ").join(message_parts) + Text(" - ") + message_text
        
        # Print to console
        console.print(final_message, markup=self.markup)
        
        # Handle exception
        if record.exc_info and self.rich_tracebacks:
            console.print(
                Traceback.from_exception(
                    *record.exc_info,
                    width=self.tracebacks_width,
                    extra_lines=self.tracebacks_extra_lines,
                    theme=self.tracebacks_theme,
                    word_wrap=self.tracebacks_word_wrap,
                    show_locals=self.tracebacks_show_locals,
                    suppress=self.tracebacks_suppress
                )
            )


class MultiFormatter:
    """
    Multi-formatter that can switch formats based on output destination
    """
    
    def __init__(self, formatters: Dict[str, logging.Formatter]):
        self.formatters = formatters
        self.default_formatter = list(formatters.values())[0] if formatters else JSONFormatter()
    
    def format(self, record: logging.LogRecord, destination: str = "default") -> str:
        """Format record using specified formatter"""
        formatter = self.formatters.get(destination, self.default_formatter)
        return formatter.format(record)
    
    def add_formatter(self, name: str, formatter: logging.Formatter):
        """Add a new formatter"""
        self.formatters[name] = formatter
    
    def remove_formatter(self, name: str):
        """Remove a formatter"""
        if name in self.formatters:
            del self.formatters[name]
