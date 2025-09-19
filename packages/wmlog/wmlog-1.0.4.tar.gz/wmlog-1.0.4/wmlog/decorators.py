#!/usr/bin/env python3
"""
WML Decorators - Dynamic Logging and Instrumentation System
Automatically instrument ProServe code with comprehensive logging
"""

import functools
import inspect
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
import importlib.util
import sys
from pathlib import Path
import logging  # Import standard logging for fallback

from .logging.core import WMLLogger, LogContext, get_global_logger


class LoggingDecorator:
    """Base class for all wmlog decorators"""
    
    def __init__(self, logger: Optional[WMLLogger] = None, **kwargs):
        self.logger = logger
        self.config = kwargs
    
    def get_logger(self, func: Callable) -> Union[WMLLogger, logging.Logger]:
        """Get a logger instance, falling back gracefully."""
        # 1. Use the logger passed directly to the decorator if available
        if self.logger:
            return self.logger
        
        # 2. Try to get the globally configured WML logger
        global_logger = get_global_logger()
        if global_logger:
            return global_logger
        
        # 3. Fallback to a standard Python logger if WML is not configured.
        # This prevents crashes during import or in unconfigured test environments.
        fallback_logger = logging.getLogger(func.__module__ or 'wmlog_decorator_fallback')
        if not fallback_logger.handlers:
            # Add a handler if none exist to ensure logs are visible
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            fallback_logger.addHandler(handler)
            fallback_logger.setLevel(logging.INFO) # Default to INFO
        return fallback_logger


def log_execution(
    level: str = "INFO",
    include_args: bool = True,
    include_result: bool = True,
    include_timing: bool = True,
    max_arg_length: int = 200,
    logger: Optional[WMLLogger] = None
):
    """
    Log function execution with args, results, and timing
    
    Usage:
        @log_execution(level="DEBUG", include_timing=True)
        def my_function(arg1, arg2):
            return arg1 + arg2
    """
    def decorator(func: Callable) -> Callable:
        decorator_instance = LoggingDecorator(logger)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # LAZY LOADING: Get logger at runtime, not import time
            log = decorator_instance.get_logger(func)
            is_wml_logger = isinstance(log, WMLLogger)

            func_name = f"{func.__module__}.{func.__qualname__}"
            
            # Prepare logging context
            context = {
                'function': func_name,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
            
            if include_args:
                try:
                    args_str = str(args)[:max_arg_length]
                    kwargs_str = str(kwargs)[:max_arg_length]
                    context.update({
                        'args': args_str + ('...' if len(str(args)) > max_arg_length else ''),
                        'kwargs': kwargs_str + ('...' if len(str(kwargs)) > max_arg_length else '')
                    })
                except Exception:
                    context.update({'args': '<serialization_error>', 'kwargs': '<serialization_error>'})
            
            start_time = time.time() if include_timing else None
            
            try:
                if is_wml_logger:
                    getattr(log, level.lower())(f"Executing {func_name}", **context)
                else:
                    log.info(f"Executing {func_name}", extra=context)

                result = func(*args, **kwargs)
                
                end_context = {'function': func_name, 'status': 'success'}
                if include_timing and start_time:
                    end_context['execution_time'] = round(time.time() - start_time, 4)

                if include_result:
                    try:
                        result_str = str(result)[:max_arg_length]
                        end_context['result'] = result_str + ('...' if len(str(result)) > max_arg_length else '')
                    except Exception:
                        end_context['result'] = '<serialization_error>'

                if is_wml_logger:
                    getattr(log, level.lower())(f"Completed {func_name}", **end_context)
                else:
                    log.info(f"Completed {func_name}", extra=end_context)

                return result
                
            except Exception as e:
                error_context = {
                    'function': func_name,
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
                if include_timing and start_time:
                    error_context['execution_time'] = round(time.time() - start_time, 4)

                if is_wml_logger:
                    log.error(f"Error in {func_name}", **error_context)
                else:
                    log.error(f"Error in {func_name}", extra=error_context)
                raise
        
        return wrapper
    return decorator


def log_imports(
    track_missing: bool = True,
    track_timing: bool = True,
    logger: Optional[WMLLogger] = None
):
    """
    Log import operations and detect missing modules early
    
    Usage:
        @log_imports(track_missing=True)
        def setup_dependencies():
            import some_module
            return some_module
    """
    def decorator(func: Callable) -> Callable:
        decorator_instance = LoggingDecorator(logger)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = decorator_instance.get_logger(func)
            is_wml_logger = isinstance(log, WMLLogger)

            func_name = f"{func.__module__}.{func.__qualname__}"
            
            # Track imports before function execution
            pre_modules = set(sys.modules.keys())
            start_time = time.time() if track_timing else None
            
            try:
                result = func(*args, **kwargs)
                
                # Track new imports after execution
                post_modules = set(sys.modules.keys())
                new_imports = post_modules - pre_modules
                
                context = {
                    'function': func_name,
                    'new_imports_count': len(new_imports),
                    'status': 'success'
                }
                
                if track_timing and start_time:
                    context['import_time'] = round(time.time() - start_time, 4)
                
                if new_imports:
                    context['new_modules'] = list(new_imports)[:10]  # Limit to first 10
                
                if is_wml_logger:
                    log.info(f"Import tracking for {func_name}", **context)
                else:
                    log.info(f"Import tracking for {func_name}", extra=context)
                return result
                
            except ImportError as e:
                if track_missing:
                    error_context = {
                        'function': func_name,
                        'status': 'import_error',
                        'missing_module': str(e),
                        'error_type': 'ImportError'
                    }
                    
                    if is_wml_logger:
                        log.error(f"Import failure in {func_name}", **error_context)
                    else:
                        log.error(f"Import failure in {func_name}", extra=error_context)
                raise
            except Exception as e:
                error_context = {'function': func_name, 'error': str(e)}
                if is_wml_logger:
                    log.error(f"Error during import tracking in {func_name}", **error_context)
                else:
                    log.error(f"Error during import tracking in {func_name}", extra=error_context)
                raise
        
        return wrapper
    return decorator


def log_errors(
    include_traceback: bool = True,
    reraise: bool = True,
    fallback_return: Any = None,
    logger: Optional[WMLLogger] = None
):
    """
    Comprehensive error logging with optional fallback
    
    Usage:
        @log_errors(include_traceback=True, reraise=False, fallback_return={})
        def risky_operation():
            # This might fail
            return dangerous_call()
    """
    def decorator(func: Callable) -> Callable:
        decorator_instance = LoggingDecorator(logger)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = decorator_instance.get_logger(func)
            is_wml_logger = isinstance(log, WMLLogger)

            func_name = f"{func.__module__}.{func.__qualname__}"
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = {
                    'function': func_name,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
                
                if include_traceback:
                    error_context['traceback'] = traceback.format_exc()
                
                if is_wml_logger:
                    log.error(f"Exception in {func_name}", **error_context)
                else:
                    log.error(f"Exception in {func_name}", extra=error_context)
                
                if reraise:
                    raise
                else:
                    warn_context = {'fallback': fallback_return}
                    if is_wml_logger:
                        log.warning(f"Returning fallback value for {func_name}", **warn_context)
                    else:
                        log.warning(f"Returning fallback value for {func_name}", extra=warn_context)
                    return fallback_return
        
        return wrapper
    return decorator


def log_compatibility(
    check_attributes: Optional[List[str]] = None,
    check_methods: Optional[List[str]] = None,
    logger: Optional[WMLLogger] = None
):
    """
    Check object compatibility and log missing attributes/methods
    
    Usage:
        @log_compatibility(check_attributes=['static_hosting', 'endpoints'])
        def process_manifest(manifest):
            return manifest.static_hosting
    """
    def decorator(func: Callable) -> Callable:
        decorator_instance = LoggingDecorator(logger)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = decorator_instance.get_logger(func)
            is_wml_logger = isinstance(log, WMLLogger)

            func_name = f"{func.__module__}.{func.__qualname__}"
            
            if args and (check_attributes or check_methods):
                obj = args[0]
                present_attrs = [attr for attr in (check_attributes or []) if hasattr(obj, attr)]
                missing_attrs = [attr for attr in (check_attributes or []) if not hasattr(obj, attr)]

                context = {
                    'present_attributes': present_attrs,
                    'missing_attributes': missing_attrs,
                    'object_type': type(obj).__name__
                }
                if is_wml_logger:
                    log.info(f"Compatibility check for {func_name}", **context)
                else:
                    log.info(f"Compatibility check for {func_name}", extra=context)

                if missing_attrs:
                    warn_context = {
                        'missing': missing_attrs,
                        'object_type': type(obj).__name__
                    }
                    if is_wml_logger:
                        log.warning(f"Missing attributes detected in {func_name}", **warn_context)
                    else:
                        log.warning(f"Missing attributes detected in {func_name}", extra=warn_context)

            return func(*args, **kwargs)
        
        return wrapper
    return decorator


@contextmanager
def log_context(operation: str, logger: Optional[WMLLogger] = None, **context_data):
    """
    Context manager for logging operation blocks
    
    Usage:
        with log_context("static_file_setup", static_dir="./public"):
            setup_static_files()
    """
    log = logger or get_global_logger()
    is_wml_logger = isinstance(log, WMLLogger)

    if not log:
        log = logging.getLogger('wmlog_context_fallback')
        if not log.handlers:
            log.addHandler(logging.StreamHandler(sys.stderr))
            log.setLevel(logging.INFO)

    start_time = time.time()

    if is_wml_logger:
        log.info(f"Starting {operation}", **context_data)
    else:
        log.info(f"Starting {operation}", extra=context_data)

    try:
        yield log
        duration = round(time.time() - start_time, 4)
        success_context = {'duration': duration, 'status': 'success', **context_data}
        if is_wml_logger:
            log.info(f"Completed {operation}", **success_context)
        else:
            log.info(f"Completed {operation}", extra=success_context)

    except Exception as e:
        duration = round(time.time() - start_time, 4)
        error_context = {'duration': duration, 'status': 'error', 'error': str(e), **context_data}
        if is_wml_logger:
            log.error(f"Failed {operation}", **error_context)
        else:
            log.error(f"Failed {operation}", extra=error_context)
        raise


class DebugMode:
    """Global debug mode controller for wmlog decorators"""
    
    _enabled = False
    _level = "INFO"
    _filters = []
    
    @classmethod
    def enable(cls, level: str = "DEBUG", filters: Optional[List[str]] = None):
        """Enable debug mode with optional filters"""
        cls._enabled = True
        cls._level = level
        cls._filters = filters or []
    
    @classmethod
    def disable(cls):
        """Disable debug mode"""
        cls._enabled = False
    
    @classmethod
    def is_enabled(cls, module_name: str = "") -> bool:
        """Check if debug mode is enabled for module"""
        if not cls._enabled:
            return False
        
        if not cls._filters:
            return True
        
        return any(filter_name in module_name for filter_name in cls._filters)


# Convenience decorator combinators
def instrument_all(
    include_timing: bool = True,
    include_imports: bool = True,
    include_errors: bool = True,
    logger: Optional[WMLLogger] = None
):
    """Apply all logging decorators to a function"""
    def decorator(func: Callable) -> Callable:
        # Apply decorators in reverse order (inner to outer)
        instrumented = func
        
        if include_errors:
            instrumented = log_errors(logger=logger)(instrumented)
        
        if include_imports:
            instrumented = log_imports(logger=logger)(instrumented)
        
        if include_timing:
            instrumented = log_execution(include_timing=True, logger=logger)(instrumented)
        
        return instrumented
    return decorator


# Export main decorators
__all__ = [
    'log_execution',
    'log_imports', 
    'log_errors',
    'log_compatibility',
    'log_context',
    'instrument_all',
    'DebugMode',
]
