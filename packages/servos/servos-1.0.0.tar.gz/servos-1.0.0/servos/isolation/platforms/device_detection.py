"""
ProServe Device Detection - Automatic Device Type Detection
Detects connected embedded devices and determines appropriate isolation manager
"""

import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import subprocess
    import platform
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False


@dataclass
class DetectedDevice:
    """Information about a detected device"""
    port: str
    device_type: str  # 'micropython', 'arduino', 'unknown'
    platform: str     # 'rp2040', 'esp32', etc.
    description: str
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'port': self.port,
            'device_type': self.device_type,
            'platform': self.platform,
            'description': self.description,
            'vid': self.vid,
            'pid': self.pid,
            'serial_number': self.serial_number,
            'manufacturer': self.manufacturer
        }


class DeviceDetector:
    """Detects and identifies connected embedded devices"""
    
    def __init__(self):
        # VID:PID mappings for common embedded devices
        self.device_signatures = {
            # MicroPython devices
            (0x2E8A, 0x0005): {'type': 'micropython', 'platform': 'rp2040', 'name': 'Raspberry Pi Pico'},
            (0x2E8A, 0x000A): {'type': 'micropython', 'platform': 'rp2040', 'name': 'Raspberry Pi Pico W'},
            (0x10C4, 0xEA60): {'type': 'micropython', 'platform': 'esp32', 'name': 'ESP32 Development Board'},
            (0x1A86, 0x7523): {'type': 'micropython', 'platform': 'esp32', 'name': 'ESP32/ESP8266 Board'},
            (0x0483, 0x5740): {'type': 'micropython', 'platform': 'pyboard', 'name': 'MicroPython PyBoard'},
            
            # Arduino devices
            (0x2341, 0x0043): {'type': 'arduino', 'platform': 'uno', 'name': 'Arduino Uno'},
            (0x2341, 0x0001): {'type': 'arduino', 'platform': 'uno', 'name': 'Arduino Uno (old bootloader)'},
            (0x2341, 0x8036): {'type': 'arduino', 'platform': 'leonardo', 'name': 'Arduino Leonardo'},
            (0x2341, 0x0036): {'type': 'arduino', 'platform': 'leonardo', 'name': 'Arduino Leonardo (bootloader)'},
            (0x2341, 0x003B): {'type': 'arduino', 'platform': 'micro', 'name': 'Arduino Micro'},
            (0x2341, 0x8037): {'type': 'arduino', 'platform': 'micro', 'name': 'Arduino Micro (bootloader)'},
            (0x2341, 0x805A): {'type': 'arduino', 'platform': 'nano33iot', 'name': 'Arduino Nano 33 IoT'},
            (0x2341, 0x025B): {'type': 'arduino', 'platform': 'uno_r4_wifi', 'name': 'Arduino Uno R4 WiFi'},
            
            # Generic ESP32/ESP8266 (could be Arduino or MicroPython)
            (0x10C4, 0xEA60): {'type': 'esp_generic', 'platform': 'esp32', 'name': 'ESP32/ESP8266 Generic'},
            (0x1A86, 0x7523): {'type': 'esp_generic', 'platform': 'esp32', 'name': 'ESP32/ESP8266 CH340'},
        }
        
        # Manufacturer name mappings
        self.manufacturer_patterns = {
            'arduino': ['Arduino', 'Arduino LLC', 'Arduino S.r.l.'],
            'raspberry_pi': ['Raspberry Pi', 'MicroPython', 'Raspberry Pi Foundation'],
            'espressif': ['Espressif', 'Silicon Labs', 'FTDI', 'Prolific'],
            'adafruit': ['Adafruit', 'Adafruit Industries']
        }
    
    def detect_connected_devices(self) -> List[DetectedDevice]:
        """Detect all connected embedded devices"""
        devices = []
        
        if not SERIAL_AVAILABLE:
            print("⚠️  Serial library not available - cannot detect devices")
            return devices
        
        print("🔍 Scanning for connected embedded devices...")
        
        for port_info in serial.tools.list_ports.comports():
            device = self._analyze_port(port_info)
            if device:
                devices.append(device)
        
        if devices:
            print(f"✅ Found {len(devices)} embedded device(s)")
            for device in devices:
                print(f"  📱 {device.description} on {device.port}")
        else:
            print("❌ No embedded devices detected")
        
        return devices
    
    def _analyze_port(self, port_info) -> Optional[DetectedDevice]:
        """Analyze a single serial port to identify the device"""
        # Skip system ports that are unlikely to be embedded devices
        if self._is_system_port(port_info):
            return None
        
        # Try VID:PID identification first
        if port_info.vid and port_info.pid:
            device_info = self._identify_by_vid_pid(port_info.vid, port_info.pid)
            if device_info:
                return DetectedDevice(
                    port=port_info.device,
                    device_type=device_info['type'],
                    platform=device_info['platform'],
                    description=device_info['name'],
                    vid=port_info.vid,
                    pid=port_info.pid,
                    serial_number=port_info.serial_number,
                    manufacturer=port_info.manufacturer
                )
        
        # Try identification by manufacturer
        if port_info.manufacturer:
            device_info = self._identify_by_manufacturer(port_info.manufacturer)
            if device_info:
                return DetectedDevice(
                    port=port_info.device,
                    device_type=device_info['type'],
                    platform=device_info['platform'],
                    description=f"{device_info['name']} ({port_info.manufacturer})",
                    vid=port_info.vid,
                    pid=port_info.pid,
                    serial_number=port_info.serial_number,
                    manufacturer=port_info.manufacturer
                )
        
        # Try device description parsing
        if port_info.description:
            device_info = self._identify_by_description(port_info.description)
            if device_info:
                return DetectedDevice(
                    port=port_info.device,
                    device_type=device_info['type'],
                    platform=device_info['platform'],
                    description=device_info['name'],
                    vid=port_info.vid,
                    pid=port_info.pid,
                    serial_number=port_info.serial_number,
                    manufacturer=port_info.manufacturer
                )
        
        # If we can't identify it, still report as unknown embedded device
        if self._looks_like_embedded_device(port_info):
            return DetectedDevice(
                port=port_info.device,
                device_type='unknown',
                platform='unknown',
                description=port_info.description or 'Unknown embedded device',
                vid=port_info.vid,
                pid=port_info.pid,
                serial_number=port_info.serial_number,
                manufacturer=port_info.manufacturer
            )
        
        return None
    
    def _is_system_port(self, port_info) -> bool:
        """Check if port is likely a system port (not an embedded device)"""
        system_patterns = [
            'bluetooth', 'internal', 'built-in', 'integrated',
            'system', 'virtual', 'pty'
        ]
        
        description = (port_info.description or '').lower()
        device_name = port_info.device.lower()
        
        return any(pattern in description or pattern in device_name 
                  for pattern in system_patterns)
    
    def _identify_by_vid_pid(self, vid: int, pid: int) -> Optional[Dict[str, str]]:
        """Identify device by VID:PID"""
        return self.device_signatures.get((vid, pid))
    
    def _identify_by_manufacturer(self, manufacturer: str) -> Optional[Dict[str, str]]:
        """Identify device by manufacturer name"""
        manufacturer_lower = manufacturer.lower()
        
        for category, patterns in self.manufacturer_patterns.items():
            for pattern in patterns:
                if pattern.lower() in manufacturer_lower:
                    if category == 'arduino':
                        return {'type': 'arduino', 'platform': 'uno', 'name': 'Arduino Board'}
                    elif category == 'raspberry_pi':
                        return {'type': 'micropython', 'platform': 'rp2040', 'name': 'Raspberry Pi Device'}
                    elif category == 'espressif':
                        return {'type': 'esp_generic', 'platform': 'esp32', 'name': 'ESP32/ESP8266 Board'}
                    elif category == 'adafruit':
                        return {'type': 'micropython', 'platform': 'circuitpython', 'name': 'Adafruit Board'}
        
        return None
    
    def _identify_by_description(self, description: str) -> Optional[Dict[str, str]]:
        """Identify device by port description"""
        description_lower = description.lower()
        
        # Arduino patterns
        arduino_patterns = ['arduino', 'genuino']
        if any(pattern in description_lower for pattern in arduino_patterns):
            if 'leonardo' in description_lower:
                return {'type': 'arduino', 'platform': 'leonardo', 'name': 'Arduino Leonardo'}
            elif 'micro' in description_lower:
                return {'type': 'arduino', 'platform': 'micro', 'name': 'Arduino Micro'}
            elif 'nano' in description_lower:
                return {'type': 'arduino', 'platform': 'nano33iot', 'name': 'Arduino Nano'}
            else:
                return {'type': 'arduino', 'platform': 'uno', 'name': 'Arduino Board'}
        
        # MicroPython patterns
        micropython_patterns = ['pico', 'micropython', 'pyboard']
        if any(pattern in description_lower for pattern in micropython_patterns):
            if 'pico' in description_lower:
                return {'type': 'micropython', 'platform': 'rp2040', 'name': 'Raspberry Pi Pico'}
            elif 'pyboard' in description_lower:
                return {'type': 'micropython', 'platform': 'pyboard', 'name': 'MicroPython PyBoard'}
            else:
                return {'type': 'micropython', 'platform': 'unknown', 'name': 'MicroPython Device'}
        
        # ESP patterns
        esp_patterns = ['esp32', 'esp8266', 'wemos', 'nodemcu']
        if any(pattern in description_lower for pattern in esp_patterns):
            return {'type': 'esp_generic', 'platform': 'esp32', 'name': 'ESP32/ESP8266 Board'}
        
        return None
    
    def _looks_like_embedded_device(self, port_info) -> bool:
        """Heuristic to determine if port looks like an embedded device"""
        # Check for common embedded device indicators
        indicators = [
            'usb', 'serial', 'uart', 'cp210x', 'ch340', 'ftdi',
            'development', 'board', 'module'
        ]
        
        text_to_check = ' '.join(filter(None, [
            port_info.description,
            port_info.manufacturer,
            port_info.product
        ])).lower()
        
        return any(indicator in text_to_check for indicator in indicators)
    
    async def probe_device_type(self, port: str, timeout: float = 3.0) -> Optional[str]:
        """Probe a device to determine if it's running MicroPython or Arduino"""
        if not SERIAL_AVAILABLE:
            return None
        
        try:
            conn = serial.Serial(port, 115200, timeout=timeout)
            
            # Try MicroPython detection
            conn.write(b'\x03')  # Ctrl+C to interrupt any running program
            conn.read_all()  # Clear buffer
            conn.write(b'print("micropython-test")\r\n')
            
            import time
            time.sleep(1)
            
            response = conn.read_all().decode('utf-8', errors='ignore')
            
            if 'micropython-test' in response.lower():
                conn.close()
                return 'micropython'
            
            # Try Arduino/bootloader detection
            conn.write(b'hello\r\n')
            time.sleep(0.5)
            response = conn.read_all().decode('utf-8', errors='ignore')
            
            # Look for Arduino-like responses
            if any(keyword in response.lower() for keyword in ['arduino', 'sketch', 'bootloader']):
                conn.close()
                return 'arduino'
            
            conn.close()
            return 'unknown'
            
        except Exception:
            return None
    
    def get_recommended_manager(self, device: DetectedDevice) -> Tuple[str, Dict[str, Any]]:
        """Get recommended isolation manager for detected device"""
        if device.device_type == 'micropython':
            return 'MicroPythonIsolationManager', {
                'platform': device.platform,
                'device_port': device.port,
                'auto_detect_device': False
            }
        
        elif device.device_type == 'arduino':
            return 'ArduinoIsolationManager', {
                'platform': device.platform if device.platform != 'unknown' else 'esp32dev',
                'upload_port': device.port,
                'compile_only': False
            }
        
        elif device.device_type == 'esp_generic':
            # For ESP devices, we might need to probe further
            return 'MicroPythonIsolationManager', {
                'platform': 'esp32',
                'device_port': device.port,
                'auto_detect_device': False,
                'use_emulator': False
            }
        
        else:
            # Unknown device - default to MicroPython emulation
            return 'MicroPythonIsolationManager', {
                'platform': 'rp2040',
                'use_emulator': True
            }


def detect_connected_devices() -> List[DetectedDevice]:
    """Convenience function to detect connected devices"""
    detector = DeviceDetector()
    return detector.detect_connected_devices()


def get_best_device_for_platform(platform_type: str, platform_name: str = None) -> Optional[DetectedDevice]:
    """Get the best connected device for a specific platform type"""
    devices = detect_connected_devices()
    
    if not devices:
        return None
    
    # Filter by platform type
    filtered_devices = [d for d in devices if d.device_type == platform_type]
    
    # If platform name specified, filter further
    if platform_name:
        platform_filtered = [d for d in filtered_devices if d.platform == platform_name]
        if platform_filtered:
            return platform_filtered[0]
    
    # Return first matching device type
    return filtered_devices[0] if filtered_devices else None


def auto_select_isolation_manager(platform_hint: str = None) -> Tuple[str, Dict[str, Any]]:
    """Automatically select and configure isolation manager based on connected devices"""
    detector = DeviceDetector()
    devices = detector.detect_connected_devices()
    
    if not devices:
        print("🤖 No devices detected - using emulation mode")
        return 'MicroPythonIsolationManager', {
            'platform': platform_hint or 'rp2040',
            'use_emulator': True
        }
    
    # If platform hint provided, try to find matching device
    if platform_hint:
        matching_devices = [d for d in devices if platform_hint in d.platform or platform_hint in d.device_type]
        if matching_devices:
            device = matching_devices[0]
        else:
            device = devices[0]  # Use first available
    else:
        device = devices[0]  # Use first detected device
    
    manager_class, config = detector.get_recommended_manager(device)
    
    print(f"🎯 Auto-selected {manager_class} for {device.description}")
    return manager_class, config


# Platform detection utilities
def get_system_info() -> Dict[str, str]:
    """Get system information for platform detection"""
    info = {
        'system': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }
    
    # Add OS-specific information
    if info['system'] == 'Linux':
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                if 'raspberry' in os_info.lower() or 'raspbian' in os_info.lower():
                    info['is_raspberry_pi'] = True
        except FileNotFoundError:
            pass
    
    return info


def check_development_tools() -> Dict[str, bool]:
    """Check availability of development tools"""
    tools = {}
    
    if SUBPROCESS_AVAILABLE:
        # Check for Arduino CLI
        try:
            result = subprocess.run(['arduino-cli', 'version'], 
                                  capture_output=True, timeout=5)
            tools['arduino_cli'] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools['arduino_cli'] = False
        
        # Check for MicroPython
        try:
            result = subprocess.run(['micropython', '--version'], 
                                  capture_output=True, timeout=5)
            tools['micropython'] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools['micropython'] = False
        
        # Check for esptool
        try:
            result = subprocess.run(['esptool.py', 'version'], 
                                  capture_output=True, timeout=5)
            tools['esptool'] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools['esptool'] = False
        
        # Check for picotool (Raspberry Pi Pico)
        try:
            result = subprocess.run(['picotool', 'version'], 
                                  capture_output=True, timeout=5)
            tools['picotool'] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools['picotool'] = False
    
    return tools
