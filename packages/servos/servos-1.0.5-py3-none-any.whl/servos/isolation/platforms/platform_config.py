"""
ProServe Platform Configuration - Embedded Platform Definitions
Defines configurations for various embedded platforms and architectures
"""

from typing import Dict, List
from dataclasses import dataclass, field


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
    
    def __post_init__(self):
        """Validate platform configuration after initialization"""
        if not self.name:
            raise ValueError("Platform name is required")
        if not self.architecture:
            raise ValueError("Platform architecture is required")
        if self.memory_limit <= 0:
            raise ValueError("Memory limit must be positive")


# MicroPython Platform Configurations
MICROPYTHON_PLATFORMS = {
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


# Arduino Platform Configurations
ARDUINO_PLATFORMS = {
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
    ),
    'leonardo': PlatformConfig(
        name='leonardo',
        architecture='avr',
        flash_size='32KB',
        memory_limit=2560,  # 2.5KB RAM
        supported_languages=['arduino-c++'],
        firmware_versions=['1.8.0'],
        tools={'compile': 'arduino-cli', 'upload': 'avrdude'},
        libraries=['SPI', 'Wire', 'SoftwareSerial']
    )
}


# All supported platforms
ALL_PLATFORMS = {
    **MICROPYTHON_PLATFORMS,
    **ARDUINO_PLATFORMS
}


def get_platform_config(platform_type: str, platform_name: str) -> PlatformConfig:
    """Get platform configuration by type and name"""
    if platform_type == 'micropython':
        if platform_name not in MICROPYTHON_PLATFORMS:
            raise ValueError(f"Unsupported MicroPython platform: {platform_name}")
        return MICROPYTHON_PLATFORMS[platform_name]
    
    elif platform_type == 'arduino':
        if platform_name not in ARDUINO_PLATFORMS:
            raise ValueError(f"Unsupported Arduino platform: {platform_name}")
        return ARDUINO_PLATFORMS[platform_name]
    
    else:
        raise ValueError(f"Unsupported platform type: {platform_type}")


def list_supported_platforms() -> Dict[str, List[str]]:
    """List all supported platforms by type"""
    return {
        'micropython': list(MICROPYTHON_PLATFORMS.keys()),
        'arduino': list(ARDUINO_PLATFORMS.keys())
    }


def validate_platform_compatibility(platform1: PlatformConfig, platform2: PlatformConfig) -> bool:
    """Check if two platforms are compatible (same architecture)"""
    return platform1.architecture == platform2.architecture


def get_memory_recommendations(platform: PlatformConfig) -> Dict[str, int]:
    """Get memory usage recommendations for platform"""
    total_memory = platform.memory_limit
    
    return {
        'max_script_size': total_memory // 4,  # 25% for script
        'max_variables': total_memory // 8,    # 12.5% for variables
        'reserved_system': total_memory // 2,  # 50% for system
        'available_user': total_memory // 4    # 25% available for user code
    }


def get_platform_limitations(platform: PlatformConfig) -> List[str]:
    """Get known limitations for platform"""
    limitations = []
    
    # Memory-based limitations
    if platform.memory_limit < 100 * 1024:  # Less than 100KB
        limitations.append("Very limited memory - avoid large data structures")
        limitations.append("String operations should be minimized")
        limitations.append("Consider using generators instead of lists")
    
    if platform.memory_limit < 50 * 1024:   # Less than 50KB
        limitations.append("Extremely limited memory - use micro-optimizations")
        limitations.append("Avoid importing large modules")
    
    # Architecture-based limitations
    if 'avr' in platform.architecture:
        limitations.append("8-bit architecture - limited integer operations")
        limitations.append("No floating point unit - avoid heavy math")
    
    if 'cortex-m0' in platform.architecture:
        limitations.append("No hardware division - optimize mathematical operations")
    
    # Platform-specific limitations
    if platform.name == 'esp8266':
        limitations.append("Single-core processor - avoid complex multitasking")
        limitations.append("Limited GPIO pins available")
    
    if platform.name.startswith('uno'):
        limitations.append("No wireless connectivity without shields")
        limitations.append("Limited serial communication options")
    
    return limitations


def recommend_libraries(platform: PlatformConfig, use_case: str) -> List[str]:
    """Recommend libraries based on platform and use case"""
    available_libs = set(platform.libraries)
    recommendations = []
    
    if use_case == 'iot':
        if 'network' in available_libs:
            recommendations.append('network')
        if 'WiFi' in available_libs:
            recommendations.append('WiFi')
        if 'urequests' in available_libs:
            recommendations.append('urequests')
        if 'ArduinoJson' in available_libs:
            recommendations.append('ArduinoJson')
    
    elif use_case == 'sensors':
        if 'machine' in available_libs:
            recommendations.append('machine')
        if 'Wire' in available_libs:
            recommendations.append('Wire')
        if 'SPI' in available_libs:
            recommendations.append('SPI')
    
    elif use_case == 'communication':
        if 'bluetooth' in available_libs:
            recommendations.append('bluetooth')
        if 'PubSubClient' in available_libs:
            recommendations.append('PubSubClient')
        if 'SoftwareSerial' in available_libs:
            recommendations.append('SoftwareSerial')
    
    elif use_case == 'web_server':
        if 'WebServer' in available_libs:
            recommendations.append('WebServer')
        if 'HTTPClient' in available_libs:
            recommendations.append('HTTPClient')
    
    return recommendations
