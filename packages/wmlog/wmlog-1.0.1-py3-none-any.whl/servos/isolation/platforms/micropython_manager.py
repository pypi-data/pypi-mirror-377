"""
ProServe MicroPython Isolation Manager - MicroPython Environment Support
Handles MicroPython script execution on embedded devices like RP2040, ESP32, ESP8266
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .platform_config import PlatformConfig, MICROPYTHON_PLATFORMS

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import esptool
    ESP_TOOLS_AVAILABLE = True
except ImportError:
    ESP_TOOLS_AVAILABLE = False


class ExtendedIsolationManager(ABC):
    """Abstract base for extended isolation environments"""
    
    def __init__(self, platform_config: PlatformConfig, **kwargs):
        self.platform_config = platform_config
        self.config = kwargs
        self.workspace = None
        
    @abstractmethod
    async def setup_environment(self):
        """Setup the isolation environment"""
        pass
        
    @abstractmethod
    async def execute_script(self, script_content: str, context: Dict[str, Any] = None):
        """Execute script in the isolation environment"""
        pass
        
    @abstractmethod
    async def cleanup_environment(self):
        """Clean up the isolation environment"""
        pass


class MicroPythonIsolationManager(ExtendedIsolationManager):
    """MicroPython isolation for RP2040, ESP32, ESP8266, etc."""
    
    def __init__(self, platform: str = 'rp2040', **kwargs):
        if platform not in MICROPYTHON_PLATFORMS:
            raise ValueError(f"Unsupported MicroPython platform: {platform}")
        
        config = MICROPYTHON_PLATFORMS[platform]
        super().__init__(config, **kwargs)
        
        self.firmware_version = kwargs.get('firmware_version', config.firmware_versions[0])
        self.auto_detect_device = kwargs.get('auto_detect_device', True)
        self.device_port = kwargs.get('device_port')
        self.baud_rate = kwargs.get('baud_rate', 115200)
        self.timeout = kwargs.get('timeout', 30)
        self.use_emulator = kwargs.get('use_emulator', False)
        
        # Device connection
        self.serial_connection = None
        self.device_detected = False
        
    async def setup_environment(self):
        """Setup MicroPython environment"""
        print(f"🐍 Setting up MicroPython environment for {self.platform_config.name}")
        
        # Create workspace
        self.workspace = Path(tempfile.mkdtemp(prefix=f'proserve_micropython_{self.platform_config.name}_'))
        
        # Setup MicroPython libraries
        await self._setup_micropython_libs(self.workspace)
        
        # Detect and verify device connection
        if not self.use_emulator:
            if self.auto_detect_device:
                self.device_port = await self._detect_device()
            
            if self.device_port:
                self.device_detected = await self._verify_device_connection()
                
        print(f"✅ MicroPython environment ready (Device: {'Connected' if self.device_detected else 'Emulated'})")
        
    async def _detect_device(self) -> Optional[str]:
        """Auto-detect connected MicroPython device"""
        if not SERIAL_AVAILABLE:
            print("⚠️  Serial library not available for device detection")
            return None
        
        print("🔍 Detecting MicroPython devices...")
        
        # Common VID:PID for MicroPython devices
        micropython_devices = {
            'rp2040': [(0x2E8A, 0x0005), (0x2E8A, 0x000A)],  # Raspberry Pi Pico
            'esp32': [(0x10C4, 0xEA60), (0x1A86, 0x7523)],   # ESP32 dev boards
            'esp8266': [(0x10C4, 0xEA60), (0x1A86, 0x7523)], # ESP8266 dev boards
            'pyboard': [(0x0483, 0x5740)]                     # MicroPython pyboard
        }
        
        platform_vids_pids = micropython_devices.get(self.platform_config.name, [])
        
        for port in serial.tools.list_ports.comports():
            if port.vid and port.pid:
                for vid, pid in platform_vids_pids:
                    if port.vid == vid and port.pid == pid:
                        print(f"✅ Found {self.platform_config.name} device on {port.device}")
                        return port.device
        
        print(f"❌ No {self.platform_config.name} device detected")
        return None
        
    async def _setup_micropython_libs(self, workspace: Path):
        """Setup MicroPython libraries in workspace"""
        libs_dir = workspace / 'lib'
        libs_dir.mkdir(exist_ok=True)
        
        # Create stub files for platform libraries
        for lib_name in self.platform_config.libraries:
            lib_file = libs_dir / f'{lib_name}.py'
            with open(lib_file, 'w') as f:
                f.write(f'# {lib_name} library stub for {self.platform_config.name}\n')
                f.write(f'# This is a placeholder for the actual {lib_name} module\n')
                
                # Add common functions for known libraries
                if lib_name == 'machine':
                    f.write('''
class Pin:
    def __init__(self, pin, mode=None):
        self.pin = pin
        self.mode = mode
    
    def value(self, val=None):
        if val is None:
            return 0
        return val

class PWM:
    def __init__(self, pin):
        self.pin = pin
    
    def duty_u16(self, duty):
        pass

class Timer:
    def __init__(self, id):
        self.id = id
''')
                elif lib_name == 'network':
                    f.write('''
class WLAN:
    def __init__(self, interface):
        self.interface = interface
    
    def active(self, state=None):
        return True
    
    def connect(self, ssid, password):
        pass
    
    def isconnected(self):
        return True
''')
        
        print(f"📚 Setup {len(self.platform_config.libraries)} MicroPython library stubs")
        
    async def _verify_device_connection(self) -> bool:
        """Verify MicroPython device connection"""
        if not self.device_port or not SERIAL_AVAILABLE:
            return False
            
        try:
            self.serial_connection = serial.Serial(
                self.device_port, 
                self.baud_rate, 
                timeout=2
            )
            
            # Send a simple command to verify MicroPython
            self.serial_connection.write(b'\r\n')
            time.sleep(0.5)
            self.serial_connection.write(b'print("ProServe-MicroPython-Test")\r\n')
            
            # Read response
            start_time = time.time()
            response = b''
            while time.time() - start_time < 3:
                if self.serial_connection.in_waiting:
                    response += self.serial_connection.read(self.serial_connection.in_waiting)
                if b'ProServe-MicroPython-Test' in response:
                    print(f"✅ MicroPython device verified on {self.device_port}")
                    return True
                time.sleep(0.1)
            
            print(f"❌ MicroPython verification failed on {self.device_port}")
            return False
            
        except Exception as e:
            print(f"❌ Device connection error: {e}")
            return False
        finally:
            if self.serial_connection:
                self.serial_connection.close()
                
    async def execute_script(self, script_content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MicroPython script on device or emulator"""
        context = context or {}
        
        print(f"🚀 Executing MicroPython script on {self.platform_config.name}")
        
        # Prepare script with MicroPython optimizations
        prepared_script = self._prepare_micropython_script(script_content, context)
        
        try:
            if self.device_detected and not self.use_emulator:
                result = await self._execute_on_device(prepared_script)
            else:
                result = await self._execute_in_emulator(prepared_script, context)
                
            return {
                'success': True,
                'result': result,
                'platform': self.platform_config.name,
                'memory_used': len(prepared_script),  # Approximation
                'execution_mode': 'device' if self.device_detected else 'emulator'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': self.platform_config.name,
                'execution_mode': 'device' if self.device_detected else 'emulator'
            }
            
    def _prepare_micropython_script(self, script_content: str, context: Dict[str, Any]) -> str:
        """Prepare script with MicroPython optimizations and context"""
        lines = []
        
        # Add platform-specific imports
        lines.append("# ProServe MicroPython Script")
        lines.append(f"# Platform: {self.platform_config.name}")
        lines.append("")
        
        # Import required libraries
        for lib in self.platform_config.libraries:
            if lib in ['machine', 'network', 'utime', 'ujson']:
                lines.append(f"try:")
                lines.append(f"    import {lib}")
                lines.append(f"except ImportError:")
                lines.append(f"    print('Warning: {lib} not available')")
        
        lines.append("")
        
        # Add context variables
        if context:
            lines.append("# Context variables")
            for key, value in context.items():
                if isinstance(value, str):
                    lines.append(f"{key} = '{value}'")
                else:
                    lines.append(f"{key} = {repr(value)}")
            lines.append("")
        
        # Memory optimization for constrained devices
        if self.platform_config.memory_limit < 100 * 1024:  # Less than 100KB
            lines.append("# Memory optimization for constrained device")
            lines.append("import gc")
            lines.append("gc.collect()")
            lines.append("")
        
        # Add user script
        lines.append("# User script")
        lines.append(script_content)
        
        # Add result capture
        lines.append("")
        lines.append("# Capture result for ProServe")
        lines.append("try:")
        lines.append("    if 'result' in locals():")
        lines.append("        print('PROSERVE_RESULT:', result)")
        lines.append("    else:")
        lines.append("        print('PROSERVE_RESULT: None')")
        lines.append("except Exception as e:")
        lines.append("    print('PROSERVE_ERROR:', str(e))")
        
        return '\n'.join(lines)
        
    async def _execute_on_device(self, script: str) -> Any:
        """Execute script on real MicroPython device"""
        if not SERIAL_AVAILABLE:
            raise RuntimeError("Serial library required for device execution")
            
        try:
            # Open serial connection
            conn = serial.Serial(self.device_port, self.baud_rate, timeout=self.timeout)
            
            # Clear any existing data
            conn.write(b'\x03')  # Ctrl+C to interrupt
            time.sleep(0.5)
            conn.read_all()
            
            # Send script line by line
            for line in script.split('\n'):
                if line.strip():
                    conn.write(line.encode() + b'\r\n')
                    time.sleep(0.1)  # Give device time to process
            
            # Read response
            start_time = time.time()
            response = b''
            
            while time.time() - start_time < self.timeout:
                if conn.in_waiting:
                    response += conn.read(conn.in_waiting)
                
                # Check for result markers
                if b'PROSERVE_RESULT:' in response or b'PROSERVE_ERROR:' in response:
                    break
                    
                time.sleep(0.1)
            
            conn.close()
            
            return self._parse_micropython_result(response.decode('utf-8', errors='ignore'))
            
        except Exception as e:
            raise RuntimeError(f"Device execution failed: {e}")
            
    async def _execute_in_emulator(self, script: str, context: Dict[str, Any]) -> Any:
        """Execute script in MicroPython emulator/simulator"""
        print("🖥️  Running in MicroPython emulator mode")
        
        # Create temporary script file
        script_file = self.workspace / 'script.py'
        with open(script_file, 'w') as f:
            f.write(script)
        
        try:
            # Try to run with micropython if available
            try:
                process = await asyncio.create_subprocess_exec(
                    'micropython', str(script_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.workspace
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
                
                if process.returncode == 0:
                    return self._parse_micropython_result(stdout.decode())
                else:
                    raise RuntimeError(f"MicroPython execution error: {stderr.decode()}")
                    
            except (FileNotFoundError, asyncio.TimeoutError):
                # Fall back to Python 3 with limited stdlib
                print("📝 Falling back to Python 3 simulation")
                
                # Create a restricted execution environment
                restricted_globals = {
                    '__builtins__': {
                        'print': print,
                        'len': len,
                        'str': str,
                        'int': int,
                        'float': float,
                        'bool': bool,
                        'list': list,
                        'dict': dict,
                        'range': range,
                        'enumerate': enumerate,
                        'zip': zip,
                    }
                }
                
                # Add context
                restricted_globals.update(context)
                
                # Execute script
                exec(script, restricted_globals)
                
                return restricted_globals.get('result', 'Script executed (no result captured)')
                
        except Exception as e:
            raise RuntimeError(f"Emulator execution failed: {e}")
            
    def _parse_micropython_result(self, response: str) -> Any:
        """Parse result from MicroPython execution"""
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('PROSERVE_RESULT:'):
                result_str = line[16:].strip()  # Remove 'PROSERVE_RESULT:' prefix
                try:
                    # Try to parse as JSON first
                    return json.loads(result_str)
                except json.JSONDecodeError:
                    # Return as string if not JSON
                    return result_str
            elif line.startswith('PROSERVE_ERROR:'):
                error_str = line[15:].strip()  # Remove 'PROSERVE_ERROR:' prefix
                raise RuntimeError(f"MicroPython script error: {error_str}")
        
        # If no explicit result found, return the full response
        return response.strip()
        
    async def cleanup_environment(self):
        """Clean up MicroPython environment"""
        print(f"🧹 Cleaning up MicroPython environment for {self.platform_config.name}")
        
        # Close serial connection
        if self.serial_connection:
            self.serial_connection.close()
            
        # Remove workspace
        if self.workspace and self.workspace.exists():
            import shutil
            shutil.rmtree(self.workspace)
            
        print("✅ MicroPython environment cleaned up")


# Utility functions for MicroPython development
def optimize_for_micropython(code: str, platform: str) -> str:
    """Optimize Python code for MicroPython execution"""
    lines = code.split('\n')
    optimized_lines = []
    
    platform_config = MICROPYTHON_PLATFORMS.get(platform)
    if not platform_config:
        return code
    
    # Memory-conscious optimizations
    for line in lines:
        # Replace list comprehensions with generators for memory-constrained devices
        if platform_config.memory_limit < 100 * 1024 and '[' in line and 'for' in line:
            # Simple heuristic - suggest generator instead
            optimized_lines.append(f"# Consider using generator: {line.replace('[', '(').replace(']', ')')}")
            
        optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)


def get_micropython_memory_info(platform: str) -> Dict[str, int]:
    """Get memory information for MicroPython platform"""
    platform_config = MICROPYTHON_PLATFORMS.get(platform)
    if not platform_config:
        return {}
    
    total_memory = platform_config.memory_limit
    
    return {
        'total_ram': total_memory,
        'recommended_script_size': total_memory // 8,
        'recommended_heap_size': total_memory // 4,
        'system_reserved': total_memory // 2
    }
