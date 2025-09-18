"""
Servos Isolation Module
=======================

Environment isolation and platform management for multi-target deployments.

This module provides:
- Extended isolation environments (MicroPython, Arduino)
- Platform detection and management
- Cross-platform deployment capabilities
- Hardware-specific environment setup
"""

try:
    from .extended_environments import (
        MicroPythonIsolationManager,
        ArduinoIsolationManager,
        create_extended_isolation_manager
    )
    EXTENDED_ENVIRONMENTS_AVAILABLE = True
except ImportError:
    EXTENDED_ENVIRONMENTS_AVAILABLE = False
    MicroPythonIsolationManager = None
    ArduinoIsolationManager = None

try:
    from .platforms import PlatformDetector, PlatformManager
    PLATFORM_DETECTION_AVAILABLE = True
except ImportError:
    PLATFORM_DETECTION_AVAILABLE = False
    PlatformDetector = None
    PlatformManager = None

__all__ = [
    "MicroPythonIsolationManager",
    "ArduinoIsolationManager", 
    "create_extended_isolation_manager",
    "PlatformDetector",
    "PlatformManager",
    "EXTENDED_ENVIRONMENTS_AVAILABLE",
    "PLATFORM_DETECTION_AVAILABLE"
]
