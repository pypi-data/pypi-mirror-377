"""
ProServe Extended Isolation Environments
Support for MicroPython, RP2040, Arduino, and embedded platforms
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

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


@dataclass
class PlatformConfig:
    """Configuration for embedded platform"""
    name: str
    architecture: str
    flash_size: str
    memory_limit: int
    supported_languages: List[str] = field(default_factory=list)
    firmware_versions: List[str] = field(default_factory=list)
    tools: Dict[str, str] = field(default_factory=dict)
    libraries: List[str] = field(default_factory=list)


class ExtendedIsolationManager(ABC):
    """Abstract base for extended isolation environments"""
    
    def __init__(self, platform_config: PlatformConfig, **kwargs):
        self.platform_config = platform_config
        self.config = kwargs
        self.logger = None
        self.device_port = None
        self.temp_dir = None
    
    @abstractmethod
    async def setup_environment(self) -> bool:
        """Setup the isolation environment"""
        pass
    
    @abstractmethod
    async def execute_script(self, script_content: str, context: Dict[str, Any]) -> Any:
        """Execute script in isolated environment"""
        pass
    
    @abstractmethod
    async def cleanup_environment(self) -> bool:
        """Clean up the isolation environment"""
        pass
    
    def _create_temp_dir(self) -> Path:
        """Create temporary directory for script execution"""
        if not self.temp_dir:
            self.temp_dir = Path(tempfile.mkdtemp(prefix=f'proserve_{self.platform_config.name}_'))
        return self.temp_dir


class MicroPythonIsolationManager(ExtendedIsolationManager):
    """MicroPython isolation for RP2040, ESP32, ESP8266, etc."""
    
    # Predefined platform configurations
    PLATFORMS = {
        'rp2040': PlatformConfig(
            name='rp2040',
            architecture='arm-cortex-m0+',
            flash_size='2MB',
            memory_limit=256 * 1024,  # 256KB RAM
            supported_languages=['micropython', 'circuitpython'],
            firmware_versions=['1.19.1', '1.20.0', '1.21.0'],
            tools={'flash': 'picotool', 'serial': 'minicom'},
            libraries=['machine', 'utime', 'ujson', 'urequests', 'network']
        ),
        'esp32': PlatformConfig(
            name='esp32',
            architecture='xtensa-esp32',
            flash_size='4MB',
            memory_limit=512 * 1024,  # 512KB RAM
            supported_languages=['micropython'],
            firmware_versions=['1.19.1', '1.20.0', '1.21.0'],
            tools={'flash': 'esptool.py', 'serial': 'minicom'},
            libraries=['machine', 'network', 'esp32', 'bluetooth']
        ),
        'esp8266': PlatformConfig(
            name='esp8266',
            architecture='xtensa-esp8266',
            flash_size='1MB',
            memory_limit=80 * 1024,  # 80KB RAM
            supported_languages=['micropython'],
            firmware_versions=['1.19.1', '1.20.0'],
            tools={'flash': 'esptool.py', 'serial': 'minicom'},
            libraries=['machine', 'network', 'esp']
        ),
        'pyboard': PlatformConfig(
            name='pyboard',
            architecture='arm-cortex-m4',
            flash_size='1MB',
            memory_limit=192 * 1024,  # 192KB RAM
            supported_languages=['micropython'],
            firmware_versions=['1.19.1', '1.20.0', '1.21.0'],
            tools={'flash': 'dfu-util', 'serial': 'minicom'},
            libraries=['machine', 'pyb', 'utime', 'ujson']
        )
    }
    
    def __init__(self, platform: str = 'rp2040', **kwargs):
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unsupported MicroPython platform: {platform}")
        
        config = self.PLATFORMS[platform]
        super().__init__(config, **kwargs)
        self.firmware_version = kwargs.get('firmware_version', config.firmware_versions[0])
        self.auto_detect_device = kwargs.get('auto_detect_device', True)
    
    async def setup_environment(self) -> bool:
        """Setup MicroPython environment"""
        try:
            # Detect connected device
            if self.auto_detect_device:
                self.device_port = await self._detect_device()
                if not self.device_port:
                    raise Exception(f"No {self.platform_config.name} device detected")
            
            # Create workspace
            workspace = self._create_temp_dir()
            
            # Setup MicroPython libraries
            await self._setup_micropython_libs(workspace)
            
            # Verify connection
            if self.device_port and SERIAL_AVAILABLE:
                await self._verify_device_connection()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"MicroPython setup failed: {e}")
            return False
    
    async def _detect_device(self) -> Optional[str]:
        """Auto-detect connected MicroPython device"""
        if not SERIAL_AVAILABLE:
            return None
        
        platform_vid_pids = {
            'rp2040': [(0x2E8A, 0x0005), (0x2E8A, 0x000A)],  # Raspberry Pi Pico
            'esp32': [(0x10C4, 0xEA60), (0x1A86, 0x7523)],   # ESP32 dev boards
            'esp8266': [(0x10C4, 0xEA60), (0x1A86, 0x55D4)], # ESP8266 dev boards
            'pyboard': [(0xF055, 0x9800)]                     # PyBoard
        }
        
        target_vid_pids = platform_vid_pids.get(self.platform_config.name, [])
        
        for port in serial.tools.list_ports.comports():
            if port.vid and port.pid:
                if (port.vid, port.pid) in target_vid_pids:
                    return port.device
        
        # Fallback: look for common MicroPython device names
        common_names = ['/dev/ttyACM0', '/dev/ttyUSB0', 'COM3', 'COM4']
        for name in common_names:
            if os.path.exists(name):
                return name
        
        return None
    
    async def _setup_micropython_libs(self, workspace: Path):
        """Setup MicroPython libraries in workspace"""
        lib_dir = workspace / 'lib'
        lib_dir.mkdir(exist_ok=True)
        
        # Create basic library stubs for IDE support
        for lib_name in self.platform_config.libraries:
            lib_file = lib_dir / f'{lib_name}.py'
            lib_file.write_text(f'# {lib_name} library stub for {self.platform_config.name}\n')
    
    async def _verify_device_connection(self) -> bool:
        """Verify MicroPython device connection"""
        try:
            import serial
            with serial.Serial(self.device_port, 115200, timeout=2) as ser:
                ser.write(b'\r\n')
                time.sleep(0.1)
                ser.write(b'print("ProServe MicroPython Test")\r\n')
                response = ser.read(100).decode('utf-8', errors='ignore')
                return 'ProServe MicroPython Test' in response
        except Exception:
            return False
    
    async def execute_script(self, script_content: str, context: Dict[str, Any]) -> Any:
        """Execute MicroPython script on device"""
        try:
            # Prepare script with context injection
            enhanced_script = self._prepare_micropython_script(script_content, context)
            
            if self.device_port and SERIAL_AVAILABLE:
                # Execute on real device
                return await self._execute_on_device(enhanced_script)
            else:
                # Execute in emulator/simulator
                return await self._execute_in_emulator(enhanced_script, context)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"MicroPython execution failed: {e}")
            raise
    
    def _prepare_micropython_script(self, script_content: str, context: Dict[str, Any]) -> str:
        """Prepare script with MicroPython optimizations and context"""
        # Memory-optimized imports
        imports = [
            "import gc",
            "import utime as time",
            "import ujson as json", 
            "import sys"
        ]
        
        # Add platform-specific imports
        if self.platform_config.name == 'rp2040':
            imports.extend(["import machine", "from machine import Pin, PWM"])
        elif self.platform_config.name in ['esp32', 'esp8266']:
            imports.extend(["import machine", "import network", "import esp"])
        
        # Context injection
        context_setup = f"""
# ProServe Context Injection
_proserve_context = {json.dumps(context)}
def get_context(key=None):
    if key:
        return _proserve_context.get(key)
    return _proserve_context

# Memory management
gc.collect()
"""
        
        # Combine all parts
        enhanced_script = '\n'.join(imports) + '\n' + context_setup + '\n' + script_content
        
        # Add result capture
        enhanced_script += """

# Result capture for ProServe
if 'result' not in locals():
    result = None
print('PROSERVE_RESULT:', json.dumps(result))
"""
        
        return enhanced_script
    
    async def _execute_on_device(self, script: str) -> Any:
        """Execute script on real MicroPython device"""
        import serial
        
        try:
            with serial.Serial(self.device_port, 115200, timeout=10) as ser:
                # Enter raw REPL mode
                ser.write(b'\x03\x03')  # Ctrl+C twice
                time.sleep(0.1)
                ser.write(b'\x01')      # Ctrl+A for raw REPL
                time.sleep(0.1)
                
                # Send script
                ser.write(script.encode('utf-8'))
                ser.write(b'\x04')      # Ctrl+D to execute
                
                # Read response
                response = b''
                start_time = time.time()
                while time.time() - start_time < 10:  # 10 second timeout
                    if ser.in_waiting:
                        chunk = ser.read(ser.in_waiting)
                        response += chunk
                        if b'PROSERVE_RESULT:' in response:
                            break
                    time.sleep(0.1)
                
                # Parse result
                response_str = response.decode('utf-8', errors='ignore')
                return self._parse_micropython_result(response_str)
                
        except Exception as e:
            raise Exception(f"Device execution failed: {e}")
    
    async def _execute_in_emulator(self, script: str, context: Dict[str, Any]) -> Any:
        """Execute script in MicroPython emulator/simulator"""
        # For now, simulate execution with limited functionality
        # In a real implementation, this could use micropython-lib or similar
        
        # Create simulated result
        simulated_result = {
            'platform': self.platform_config.name,
            'executed': True,
            'context': context,
            'memory_usage': f"{self.platform_config.memory_limit // 1024}KB available",
            'simulation': True
        }
        
        # Add platform-specific simulation
        if 'machine' in script:
            simulated_result['gpio_pins'] = list(range(0, 29)) if self.platform_config.name == 'rp2040' else list(range(0, 39))
        
        if 'network' in script:
            simulated_result['wifi_available'] = True
            
        return simulated_result
    
    def _parse_micropython_result(self, response: str) -> Any:
        """Parse result from MicroPython execution"""
        try:
            # Find result line
            for line in response.split('\n'):
                if 'PROSERVE_RESULT:' in line:
                    result_json = line.split('PROSERVE_RESULT:')[1].strip()
                    return json.loads(result_json)
            
            # No explicit result, return execution info
            return {
                'executed': True,
                'output': response,
                'platform': self.platform_config.name
            }
            
        except Exception as e:
            return {
                'executed': False,
                'error': str(e),
                'raw_output': response
            }
    
    async def cleanup_environment(self) -> bool:
        """Clean up MicroPython environment"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            return True
        except Exception:
            return False


class ArduinoIsolationManager(ExtendedIsolationManager):
    """Arduino IDE isolation for various Arduino boards"""
    
    PLATFORMS = {
        'uno_r4_wifi': PlatformConfig(
            name='uno_r4_wifi',
            architecture='arm-cortex-m4',
            flash_size='256KB',
            memory_limit=32 * 1024,  # 32KB RAM
            supported_languages=['arduino-c++'],
            firmware_versions=['1.0.0'],
            tools={'compile': 'arduino-cli', 'upload': 'arduino-cli'},
            libraries=['WiFi', 'ArduinoJson', 'PubSubClient', 'HTTPClient']
        ),
        'esp32dev': PlatformConfig(
            name='esp32dev',
            architecture='xtensa-esp32',
            flash_size='4MB',
            memory_limit=320 * 1024,  # 320KB RAM
            supported_languages=['arduino-c++'],
            firmware_versions=['2.0.0', '2.0.11'],
            tools={'compile': 'arduino-cli', 'upload': 'esptool'},
            libraries=['WiFi', 'WebServer', 'ArduinoJson', 'PubSubClient', 'BLE']
        ),
        'nano33iot': PlatformConfig(
            name='nano33iot',
            architecture='arm-cortex-m0+',
            flash_size='256KB',
            memory_limit=32 * 1024,  # 32KB RAM
            supported_languages=['arduino-c++'],
            firmware_versions=['1.8.0'],
            tools={'compile': 'arduino-cli', 'upload': 'arduino-cli'},
            libraries=['WiFiNINA', 'ArduinoJson', 'RTCZero', 'IMU']
        )
    }
    
    def __init__(self, platform: str = 'esp32dev', **kwargs):
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unsupported Arduino platform: {platform}")
        
        config = self.PLATFORMS[platform]
        super().__init__(config, **kwargs)
        self.arduino_cli = kwargs.get('arduino_cli_path', 'arduino-cli')
        self.board_fqbn = kwargs.get('board_fqbn', self._get_default_fqbn())
    
    def _get_default_fqbn(self) -> str:
        """Get default Fully Qualified Board Name"""
        fqbn_mapping = {
            'uno_r4_wifi': 'arduino:renesas_uno:unor4wifi',
            'esp32dev': 'esp32:esp32:esp32',
            'nano33iot': 'arduino:samd:nano_33_iot'
        }
        return fqbn_mapping.get(self.platform_config.name, 'arduino:avr:uno')
    
    async def setup_environment(self) -> bool:
        """Setup Arduino development environment"""
        try:
            # Check arduino-cli availability
            result = await self._run_command([self.arduino_cli, 'version'])
            if result.returncode != 0:
                raise Exception("arduino-cli not found")
            
            # Create workspace
            workspace = self._create_temp_dir()
            
            # Install required cores and libraries
            await self._setup_arduino_environment()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Arduino setup failed: {e}")
            return False
    
    async def _setup_arduino_environment(self):
        """Setup Arduino cores and libraries"""
        # Update core index
        await self._run_command([self.arduino_cli, 'core', 'update-index'])
        
        # Install platform-specific core
        core_map = {
            'uno_r4_wifi': 'arduino:renesas_uno',
            'esp32dev': 'esp32:esp32',
            'nano33iot': 'arduino:samd'
        }
        
        core = core_map.get(self.platform_config.name)
        if core:
            await self._run_command([self.arduino_cli, 'core', 'install', core])
        
        # Install common libraries
        for library in self.platform_config.libraries:
            await self._run_command([self.arduino_cli, 'lib', 'install', library])
    
    async def execute_script(self, script_content: str, context: Dict[str, Any]) -> Any:
        """Execute Arduino C++ script"""
        try:
            # Convert Python-like script to Arduino C++
            arduino_code = self._convert_to_arduino_cpp(script_content, context)
            
            # Create Arduino sketch
            sketch_dir = self._create_arduino_sketch(arduino_code)
            
            # Compile sketch
            compile_result = await self._compile_sketch(sketch_dir)
            
            if compile_result['success']:
                # For now, return compilation success
                # In full implementation, could upload and execute
                return {
                    'compiled': True,
                    'platform': self.platform_config.name,
                    'sketch_size': compile_result.get('sketch_size'),
                    'memory_usage': compile_result.get('memory_usage')
                }
            else:
                raise Exception(f"Compilation failed: {compile_result['error']}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Arduino execution failed: {e}")
            raise
    
    def _convert_to_arduino_cpp(self, script_content: str, context: Dict[str, Any]) -> str:
        """Convert Python-like script to Arduino C++"""
        # Basic template for Arduino sketch
        arduino_template = f"""
// Generated by ProServe for {self.platform_config.name}
#include <Arduino.h>

// Platform-specific includes
{self._get_platform_includes()}

// Context data (converted from Python)
{self._generate_context_code(context)}

// User code (converted from Python-like syntax)
void setup() {{
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("ProServe Arduino Script Starting...");
    
    // Initialize platform-specific features
    {self._get_setup_code()}
    
    // User setup code
    {self._convert_setup_code(script_content)}
}}

void loop() {{
    // User loop code  
    {self._convert_loop_code(script_content)}
    
    delay(1000);
}}

// Helper functions
{self._generate_helper_functions()}
"""
        
        return arduino_template
    
    def _get_platform_includes(self) -> str:
        """Get platform-specific include statements"""
        includes_map = {
            'uno_r4_wifi': '#include <WiFi.h>\n#include <ArduinoJson.h>',
            'esp32dev': '#include <WiFi.h>\n#include <WebServer.h>\n#include <ArduinoJson.h>',
            'nano33iot': '#include <WiFiNINA.h>\n#include <ArduinoJson.h>'
        }
        return includes_map.get(self.platform_config.name, '')
    
    def _generate_context_code(self, context: Dict[str, Any]) -> str:
        """Generate C++ code for context data"""
        # Convert simple Python context to Arduino variables
        code_lines = []
        for key, value in context.items():
            if isinstance(value, str):
                code_lines.append(f'String context_{key} = "{value}";')
            elif isinstance(value, (int, float)):
                code_lines.append(f'const float context_{key} = {value};')
            elif isinstance(value, bool):
                code_lines.append(f'const bool context_{key} = {"true" if value else "false"};')
        
        return '\n'.join(code_lines)
    
    def _get_setup_code(self) -> str:
        """Get platform-specific setup code"""
        setup_map = {
            'uno_r4_wifi': 'WiFi.begin("", ""); // Configure WiFi',
            'esp32dev': 'WiFi.mode(WIFI_STA);',
            'nano33iot': 'WiFi.begin("", "");'
        }
        return setup_map.get(self.platform_config.name, '')
    
    def _convert_setup_code(self, script: str) -> str:
        """Convert Python setup code to Arduino C++"""
        # Basic conversion (in real implementation, would be more sophisticated)
        converted = script.replace('print(', 'Serial.println(')
        converted = converted.replace('time.sleep(', 'delay(')
        return f'// Converted setup code\n{converted}'
    
    def _convert_loop_code(self, script: str) -> str:
        """Convert Python loop code to Arduino C++"""
        # Basic conversion
        converted = script.replace('while True:', '// while True converted to loop()')
        converted = converted.replace('print(', 'Serial.println(')
        return f'// Converted loop code\n{converted}'
    
    def _generate_helper_functions(self) -> str:
        """Generate Arduino helper functions"""
        return """
// ProServe helper functions
void proserve_log(String message) {
    Serial.print("[ProServe] ");
    Serial.println(message);
}

String proserve_get_context(String key) {
    // Simple context getter (in real implementation, would use map)
    return "context_value";
}
"""
    
    def _create_arduino_sketch(self, arduino_code: str) -> Path:
        """Create Arduino sketch directory and files"""
        sketch_name = f"proserve_sketch_{int(time.time())}"
        sketch_dir = self.temp_dir / sketch_name
        sketch_dir.mkdir(exist_ok=True)
        
        # Create .ino file
        ino_file = sketch_dir / f"{sketch_name}.ino"
        ino_file.write_text(arduino_code)
        
        return sketch_dir
    
    async def _compile_sketch(self, sketch_dir: Path) -> Dict[str, Any]:
        """Compile Arduino sketch"""
        try:
            cmd = [
                self.arduino_cli, 'compile', 
                '--fqbn', self.board_fqbn,
                str(sketch_dir)
            ]
            
            result = await self._run_command(cmd)
            
            if result.returncode == 0:
                # Parse compilation output for size info
                output = result.stdout.decode('utf-8')
                return {
                    'success': True,
                    'sketch_size': self._parse_sketch_size(output),
                    'memory_usage': self._parse_memory_usage(output)
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr.decode('utf-8')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_sketch_size(self, compile_output: str) -> str:
        """Parse sketch size from compilation output"""
        # Look for size information in output
        for line in compile_output.split('\n'):
            if 'bytes' in line and 'program storage' in line:
                return line.strip()
        return "Size information not available"
    
    def _parse_memory_usage(self, compile_output: str) -> str:
        """Parse memory usage from compilation output"""
        # Look for memory usage information
        for line in compile_output.split('\n'):
            if 'dynamic memory' in line:
                return line.strip()
        return "Memory usage information not available"
    
    async def _run_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # Create result object similar to subprocess.run
        result = type('Result', (), {})()
        result.returncode = process.returncode
        result.stdout = stdout
        result.stderr = stderr
        
        return result
    
    async def cleanup_environment(self) -> bool:
        """Clean up Arduino environment"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            return True
        except Exception:
            return False


# Factory function for creating isolation managers
def create_extended_isolation_manager(platform_type: str, platform: str, **kwargs) -> ExtendedIsolationManager:
    """Factory function to create appropriate isolation manager"""
    if platform_type == 'micropython':
        return MicroPythonIsolationManager(platform, **kwargs)
    elif platform_type == 'arduino':
        return ArduinoIsolationManager(platform, **kwargs)
    else:
        raise ValueError(f"Unknown platform type: {platform_type}")


# Platform detection utilities
def detect_connected_devices() -> Dict[str, List[str]]:
    """Detect connected embedded devices"""
    devices = {
        'micropython': [],
        'arduino': []
    }
    
    if SERIAL_AVAILABLE:
        for port in serial.tools.list_ports.comports():
            if port.vid and port.pid:
                # Check for known MicroPython devices
                if (port.vid, port.pid) in [(0x2E8A, 0x0005), (0x2E8A, 0x000A)]:
                    devices['micropython'].append(f"RP2040 on {port.device}")
                elif (port.vid, port.pid) in [(0x10C4, 0xEA60), (0x1A86, 0x7523)]:
                    devices['micropython'].append(f"ESP32 on {port.device}")
                # Check for Arduino devices
                elif (port.vid, port.pid) in [(0x2341, 0x0043), (0x2341, 0x0001)]:
                    devices['arduino'].append(f"Arduino on {port.device}")
    
    return devices


# Example usage and testing
if __name__ == '__main__':
    async def test_micropython():
        """Test MicroPython isolation"""
        manager = MicroPythonIsolationManager('rp2040')
        
        if await manager.setup_environment():
            script = """
import machine
led = machine.Pin(25, machine.Pin.OUT)
led.on()
result = {"led_status": "on", "platform": "rp2040"}
"""
            
            context = {"test_mode": True, "device_id": "pico_001"}
            result = await manager.execute_script(script, context)
            print(f"MicroPython result: {result}")
            
            await manager.cleanup_environment()
    
    async def test_arduino():
        """Test Arduino isolation"""
        manager = ArduinoIsolationManager('esp32dev')
        
        if await manager.setup_environment():
            script = """
// Simple LED blink script
digitalWrite(2, HIGH);
delay(1000);
digitalWrite(2, LOW);
"""
            
            context = {"blink_interval": 1000, "led_pin": 2}
            result = await manager.execute_script(script, context)
            print(f"Arduino result: {result}")
            
            await manager.cleanup_environment()
    
    # Run tests
    print("🔧 Testing Extended Isolation Environments")
    print("Connected devices:", detect_connected_devices())
    
    asyncio.run(test_micropython())
    asyncio.run(test_arduino())
