"""
ProServe Arduino Isolation Manager - Arduino IDE Environment Support
Handles Arduino C++ compilation and upload for various Arduino-compatible boards
"""

import os
import sys
import json
import asyncio
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from .platform_config import PlatformConfig, ARDUINO_PLATFORMS
from .micropython_manager import ExtendedIsolationManager


class ArduinoIsolationManager(ExtendedIsolationManager):
    """Arduino IDE isolation for various Arduino boards"""
    
    def __init__(self, platform: str = 'esp32dev', **kwargs):
        if platform not in ARDUINO_PLATFORMS:
            raise ValueError(f"Unsupported Arduino platform: {platform}")
        
        config = ARDUINO_PLATFORMS[platform]
        super().__init__(config, **kwargs)
        
        self.arduino_cli = kwargs.get('arduino_cli_path', 'arduino-cli')
        self.board_fqbn = kwargs.get('board_fqbn', self._get_default_fqbn())
        self.sketch_dir = None
        self.compile_only = kwargs.get('compile_only', True)
        self.upload_port = kwargs.get('upload_port')
        self.libraries_installed = False
        
    def _get_default_fqbn(self) -> str:
        """Get default Fully Qualified Board Name"""
        fqbn_map = {
            'uno_r4_wifi': 'arduino:renesas_uno:unor4wifi',
            'esp32dev': 'esp32:esp32:esp32',
            'nano33iot': 'arduino:samd:nano_33_iot',
            'leonardo': 'arduino:avr:leonardo'
        }
        return fqbn_map.get(self.platform_config.name, 'arduino:avr:uno')
    
    async def setup_environment(self):
        """Setup Arduino development environment"""
        print(f"🛠️  Setting up Arduino environment for {self.platform_config.name}")
        
        # Create workspace
        self.workspace = Path(tempfile.mkdtemp(prefix=f'proserve_arduino_{self.platform_config.name}_'))
        
        # Setup Arduino CLI environment
        await self._setup_arduino_environment()
        
        print(f"✅ Arduino environment ready for {self.platform_config.name}")
    
    async def _setup_arduino_environment(self):
        """Setup Arduino cores and libraries"""
        try:
            # Check if arduino-cli is available
            result = await self._run_command([self.arduino_cli, 'version'])
            print(f"📦 Arduino CLI version: {result['stdout'].strip()}")
            
            # Update core index
            print("📥 Updating Arduino core index...")
            await self._run_command([self.arduino_cli, 'core', 'update-index'])
            
            # Install required core based on platform
            core_map = {
                'esp32dev': 'esp32:esp32',
                'uno_r4_wifi': 'arduino:renesas_uno',
                'nano33iot': 'arduino:samd',
                'leonardo': 'arduino:avr'
            }
            
            required_core = core_map.get(self.platform_config.name, 'arduino:avr')
            print(f"📦 Installing core: {required_core}")
            
            try:
                await self._run_command([self.arduino_cli, 'core', 'install', required_core])
            except Exception as e:
                print(f"⚠️  Core installation warning: {e}")
            
            # Install required libraries
            await self._install_libraries()
            
        except Exception as e:
            print(f"⚠️  Arduino environment setup warning: {e}")
            print("🔧 Continuing with basic setup...")
    
    async def _install_libraries(self):
        """Install required libraries for the platform"""
        if self.libraries_installed:
            return
        
        print("📚 Installing Arduino libraries...")
        
        for library in self.platform_config.libraries:
            try:
                print(f"  Installing {library}...")
                await self._run_command([self.arduino_cli, 'lib', 'install', library])
            except Exception as e:
                print(f"  ⚠️  Library {library} installation warning: {e}")
        
        self.libraries_installed = True
        print("✅ Library installation completed")
    
    async def execute_script(self, script_content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Arduino C++ script"""
        context = context or {}
        
        print(f"🚀 Executing Arduino script on {self.platform_config.name}")
        
        try:
            # Convert Python-like script to Arduino C++
            arduino_code = self._convert_to_arduino_cpp(script_content, context)
            
            # Create Arduino sketch
            sketch_path = await self._create_arduino_sketch(arduino_code)
            
            # Compile sketch
            compile_result = await self._compile_sketch(sketch_path)
            
            result = {
                'success': True,
                'platform': self.platform_config.name,
                'compilation': compile_result,
                'arduino_code': arduino_code,
                'sketch_path': str(sketch_path)
            }
            
            # Upload if requested and port available
            if not self.compile_only and self.upload_port:
                upload_result = await self._upload_sketch(sketch_path)
                result['upload'] = upload_result
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': self.platform_config.name
            }
    
    def _convert_to_arduino_cpp(self, script_content: str, context: Dict[str, Any]) -> str:
        """Convert Python-like script to Arduino C++"""
        lines = []
        
        # Header comment
        lines.append("/*")
        lines.append(" * ProServe Generated Arduino Sketch")
        lines.append(f" * Platform: {self.platform_config.name}")
        lines.append(f" * Generated from Python-like script")
        lines.append(" */")
        lines.append("")
        
        # Platform-specific includes
        lines.extend(self._get_platform_includes())
        lines.append("")
        
        # Context variables as constants
        if context:
            lines.append("// Context variables")
            lines.extend(self._generate_context_code(context))
            lines.append("")
        
        # Global variables section
        lines.append("// Global variables")
        lines.append("")
        
        # Setup function
        lines.append("void setup() {")
        lines.append("  // Initialize serial communication")
        lines.append("  Serial.begin(115200);")
        lines.append("  while (!Serial) {")
        lines.append("    delay(10);")
        lines.append("  }")
        lines.append("  Serial.println(\"ProServe Arduino Sketch Starting...\");")
        lines.append("")
        
        # Platform-specific setup
        lines.extend(self._get_setup_code())
        lines.append("")
        
        # Convert user setup code
        setup_code = self._convert_setup_code(script_content)
        if setup_code:
            lines.append("  // User setup code")
            lines.extend([f"  {line}" for line in setup_code])
            lines.append("")
        
        lines.append("  Serial.println(\"Setup complete!\");")
        lines.append("}")
        lines.append("")
        
        # Loop function
        lines.append("void loop() {")
        loop_code = self._convert_loop_code(script_content)
        if loop_code:
            lines.append("  // User loop code")
            lines.extend([f"  {line}" for line in loop_code])
        else:
            lines.append("  // Default loop")
            lines.append("  delay(1000);")
        lines.append("}")
        lines.append("")
        
        # Helper functions
        lines.extend(self._generate_helper_functions())
        
        return '\n'.join(lines)
    
    def _get_platform_includes(self) -> List[str]:
        """Get platform-specific include statements"""
        includes = ["#include <Arduino.h>"]
        
        # Platform-specific includes
        if self.platform_config.name in ['esp32dev', 'esp8266']:
            includes.append("#include <WiFi.h>")
        elif self.platform_config.name == 'uno_r4_wifi':
            includes.append("#include <WiFi.h>")
        elif self.platform_config.name == 'nano33iot':
            includes.append("#include <WiFiNINA.h>")
        
        # Common libraries
        for lib in self.platform_config.libraries:
            if lib == 'ArduinoJson':
                includes.append("#include <ArduinoJson.h>")
            elif lib == 'PubSubClient':
                includes.append("#include <PubSubClient.h>")
            elif lib == 'HTTPClient':
                includes.append("#include <HTTPClient.h>")
            elif lib == 'WebServer':
                includes.append("#include <WebServer.h>")
        
        return includes
    
    def _generate_context_code(self, context: Dict[str, Any]) -> List[str]:
        """Generate C++ code for context data"""
        lines = []
        
        for key, value in context.items():
            if isinstance(value, str):
                lines.append(f'const char* {key} = "{value}";')
            elif isinstance(value, int):
                lines.append(f'const int {key} = {value};')
            elif isinstance(value, float):
                lines.append(f'const float {key} = {value};')
            elif isinstance(value, bool):
                lines.append(f'const bool {key} = {"true" if value else "false"};')
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON strings
                import json
                json_str = json.dumps(value).replace('"', '\\"')
                lines.append(f'const char* {key}_json = "{json_str}";')
        
        return lines
    
    def _get_setup_code(self) -> List[str]:
        """Get platform-specific setup code"""
        lines = []
        
        # Platform-specific initialization
        if 'WiFi' in self.platform_config.libraries:
            lines.append("  // WiFi initialization")
            lines.append("  // WiFi.mode(WIFI_STA);")
        
        return lines
    
    def _convert_setup_code(self, script: str) -> List[str]:
        """Convert Python setup code to Arduino C++"""
        lines = []
        
        # Look for setup-like patterns in the script
        script_lines = script.split('\n')
        for line in script_lines:
            line = line.strip()
            if line.startswith('setup') or 'init' in line.lower():
                # Simple conversion - this could be more sophisticated
                if 'print(' in line:
                    converted = line.replace('print(', 'Serial.println(')
                    lines.append(converted)
        
        return lines
    
    def _convert_loop_code(self, script: str) -> List[str]:
        """Convert Python loop code to Arduino C++"""
        lines = []
        
        # Simple conversion of common patterns
        script_lines = script.split('\n')
        
        for line in script_lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('setup') or line.startswith('import'):
                continue
            
            # Convert common patterns
            if 'print(' in line:
                converted = line.replace('print(', 'Serial.println(')
                lines.append(converted + ';')
            elif 'time.sleep(' in line:
                # Extract delay value
                import re
                match = re.search(r'time\.sleep\((\d+(?:\.\d+)?)\)', line)
                if match:
                    delay_sec = float(match.group(1))
                    delay_ms = int(delay_sec * 1000)
                    lines.append(f'delay({delay_ms});')
            else:
                # Generic conversion attempt
                if not line.endswith(';') and not line.endswith(':'):
                    line += ';'
                lines.append(line)
        
        # Add default delay if no delay found
        if not any('delay(' in line for line in lines):
            lines.append('delay(1000);')
        
        return lines
    
    def _generate_helper_functions(self) -> List[str]:
        """Generate Arduino helper functions"""
        lines = []
        
        # JSON parsing helper if ArduinoJson is available
        if 'ArduinoJson' in self.platform_config.libraries:
            lines.extend([
                "// JSON Helper Functions",
                "void parseJson(const char* jsonString) {",
                "  StaticJsonDocument<1024> doc;",
                "  DeserializationError error = deserializeJson(doc, jsonString);",
                "  if (error) {",
                "    Serial.print(\"JSON parsing failed: \");",
                "    Serial.println(error.c_str());",
                "  }",
                "}",
                ""
            ])
        
        # WiFi helper if WiFi is available
        if 'WiFi' in self.platform_config.libraries:
            lines.extend([
                "// WiFi Helper Functions",
                "bool connectWiFi(const char* ssid, const char* password) {",
                "  WiFi.begin(ssid, password);",
                "  int attempts = 0;",
                "  while (WiFi.status() != WL_CONNECTED && attempts < 20) {",
                "    delay(500);",
                "    Serial.print(\".\");",
                "    attempts++;",
                "  }",
                "  if (WiFi.status() == WL_CONNECTED) {",
                "    Serial.println();",
                "    Serial.print(\"Connected to WiFi. IP: \");",
                "    Serial.println(WiFi.localIP());",
                "    return true;",
                "  }",
                "  return false;",
                "}",
                ""
            ])
        
        return lines
    
    async def _create_arduino_sketch(self, arduino_code: str) -> Path:
        """Create Arduino sketch directory and files"""
        sketch_name = f"proserve_sketch_{self.platform_config.name}"
        self.sketch_dir = self.workspace / sketch_name
        self.sketch_dir.mkdir(exist_ok=True)
        
        # Write main sketch file
        sketch_file = self.sketch_dir / f"{sketch_name}.ino"
        with open(sketch_file, 'w') as f:
            f.write(arduino_code)
        
        print(f"📝 Created Arduino sketch: {sketch_file}")
        return self.sketch_dir
    
    async def _compile_sketch(self, sketch_dir: Path) -> Dict[str, Any]:
        """Compile Arduino sketch"""
        print(f"🔨 Compiling Arduino sketch for {self.platform_config.name}")
        
        try:
            cmd = [
                self.arduino_cli, 'compile',
                '--fqbn', self.board_fqbn,
                '--output-dir', str(sketch_dir / 'build'),
                str(sketch_dir)
            ]
            
            result = await self._run_command(cmd)
            
            # Parse compilation results
            compile_info = {
                'success': True,
                'board': self.board_fqbn,
                'output': result['stdout'],
                'warnings': result['stderr'] if result['stderr'] else None
            }
            
            # Try to extract sketch size information
            sketch_size = self._parse_sketch_size(result['stdout'])
            if sketch_size:
                compile_info['sketch_size'] = sketch_size
            
            # Try to extract memory usage
            memory_usage = self._parse_memory_usage(result['stdout'])
            if memory_usage:
                compile_info['memory_usage'] = memory_usage
            
            print(f"✅ Compilation successful for {self.platform_config.name}")
            return compile_info
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'board': self.board_fqbn
            }
    
    def _parse_sketch_size(self, compile_output: str) -> Optional[Dict[str, int]]:
        """Parse sketch size from compilation output"""
        # Look for sketch size information
        size_pattern = r'Sketch uses (\d+) bytes.*of program storage space'
        match = re.search(size_pattern, compile_output)
        
        if match:
            return {
                'program_size': int(match.group(1)),
                'max_program_size': self._parse_flash_size()
            }
        
        return None
    
    def _parse_memory_usage(self, compile_output: str) -> Optional[Dict[str, int]]:
        """Parse memory usage from compilation output"""
        # Look for global variable memory usage
        memory_pattern = r'Global variables use (\d+) bytes.*of dynamic memory'
        match = re.search(memory_pattern, compile_output)
        
        if match:
            return {
                'global_variables': int(match.group(1)),
                'max_dynamic_memory': self.platform_config.memory_limit
            }
        
        return None
    
    def _parse_flash_size(self) -> int:
        """Parse flash size from platform configuration"""
        flash_size = self.platform_config.flash_size
        if 'MB' in flash_size:
            return int(flash_size.replace('MB', '')) * 1024 * 1024
        elif 'KB' in flash_size:
            return int(flash_size.replace('KB', '')) * 1024
        else:
            return 0
    
    async def _upload_sketch(self, sketch_dir: Path) -> Dict[str, Any]:
        """Upload compiled sketch to device"""
        print(f"📤 Uploading sketch to {self.upload_port}")
        
        try:
            cmd = [
                self.arduino_cli, 'upload',
                '--fqbn', self.board_fqbn,
                '--port', self.upload_port,
                '--input-dir', str(sketch_dir / 'build'),
                str(sketch_dir)
            ]
            
            result = await self._run_command(cmd)
            
            print(f"✅ Upload successful to {self.upload_port}")
            return {
                'success': True,
                'port': self.upload_port,
                'output': result['stdout']
            }
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'port': self.upload_port
            }
    
    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed with code {process.returncode}: {stderr.decode()}")
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            }
            
        except asyncio.TimeoutError:
            raise RuntimeError("Command timeout after 5 minutes")
    
    async def cleanup_environment(self):
        """Clean up Arduino environment"""
        print(f"🧹 Cleaning up Arduino environment for {self.platform_config.name}")
        
        # Remove workspace
        if self.workspace and self.workspace.exists():
            import shutil
            shutil.rmtree(self.workspace)
        
        print("✅ Arduino environment cleaned up")


# Utility functions for Arduino development
def optimize_for_arduino(code: str, platform: str) -> str:
    """Optimize code for Arduino platform constraints"""
    platform_config = ARDUINO_PLATFORMS.get(platform)
    if not platform_config:
        return code
    
    lines = code.split('\n')
    optimized_lines = []
    
    for line in lines:
        # Memory optimization for very constrained devices
        if platform_config.memory_limit < 50 * 1024:
            # Suggest using F() macro for string literals
            if 'Serial.print(' in line and '"' in line:
                optimized_lines.append(f"// Consider F() macro: {line.replace('Serial.print(\"', 'Serial.print(F(\"')}")
        
        optimized_lines.append(line)
    
    return '\n'.join(optimized_lines)


def get_arduino_memory_info(platform: str) -> Dict[str, int]:
    """Get memory information for Arduino platform"""
    platform_config = ARDUINO_PLATFORMS.get(platform)
    if not platform_config:
        return {}
    
    flash_size = platform_config.flash_size
    if 'MB' in flash_size:
        flash_bytes = int(flash_size.replace('MB', '')) * 1024 * 1024
    elif 'KB' in flash_size:
        flash_bytes = int(flash_size.replace('KB', '')) * 1024
    else:
        flash_bytes = 0
    
    return {
        'flash_memory': flash_bytes,
        'ram_memory': platform_config.memory_limit,
        'recommended_sketch_size': flash_bytes // 2,  # Leave room for bootloader
        'recommended_variables': platform_config.memory_limit // 4
    }
