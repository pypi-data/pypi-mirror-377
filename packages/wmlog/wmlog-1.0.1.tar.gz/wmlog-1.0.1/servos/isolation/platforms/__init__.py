"""
ProServe Isolation Platforms - Modular Embedded Platform Support
Refactored from monolithic extended_environments.py into focused platform modules
"""

from .platform_config import (
    PlatformConfig,
    MICROPYTHON_PLATFORMS, ARDUINO_PLATFORMS, ALL_PLATFORMS,
    get_platform_config, list_supported_platforms,
    validate_platform_compatibility, get_memory_recommendations,
    get_platform_limitations, recommend_libraries
)
from .micropython_manager import (
    MicroPythonIsolationManager, ExtendedIsolationManager,
    optimize_for_micropython, get_micropython_memory_info
)
from .arduino_manager import (
    ArduinoIsolationManager,
    optimize_for_arduino, get_arduino_memory_info
)
from .device_detection import (
    DetectedDevice, DeviceDetector,
    detect_connected_devices, get_best_device_for_platform,
    auto_select_isolation_manager, get_system_info, check_development_tools
)

__all__ = [
    # Platform Configuration
    'PlatformConfig',
    'MICROPYTHON_PLATFORMS', 'ARDUINO_PLATFORMS', 'ALL_PLATFORMS',
    'get_platform_config', 'list_supported_platforms',
    'validate_platform_compatibility', 'get_memory_recommendations',
    'get_platform_limitations', 'recommend_libraries',
    
    # Isolation Managers
    'ExtendedIsolationManager',
    'MicroPythonIsolationManager',
    'ArduinoIsolationManager',
    
    # Optimization Utilities
    'optimize_for_micropython', 'get_micropython_memory_info',
    'optimize_for_arduino', 'get_arduino_memory_info',
    
    # Device Detection
    'DetectedDevice', 'DeviceDetector',
    'detect_connected_devices', 'get_best_device_for_platform',
    'auto_select_isolation_manager', 'get_system_info', 'check_development_tools'
]


# Factory function for creating isolation managers (backward compatibility)
def create_extended_isolation_manager(platform_type: str, platform: str, **kwargs):
    """Factory function to create appropriate isolation manager"""
    if platform_type == 'micropython':
        return MicroPythonIsolationManager(platform=platform, **kwargs)
    elif platform_type == 'arduino':
        return ArduinoIsolationManager(platform=platform, **kwargs)
    else:
        raise ValueError(f"Unsupported platform type: {platform_type}")


# Export factory function
__all__.append('create_extended_isolation_manager')
