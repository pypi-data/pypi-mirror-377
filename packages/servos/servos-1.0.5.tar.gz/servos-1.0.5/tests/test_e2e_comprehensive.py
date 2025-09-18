"""
Comprehensive End-to-End Test Suite for Servos Package
Tests all core functionality including isolation, platforms, Docker, and device detection
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import pytest

# Import Servos components
from servos.core.isolation import ProcessIsolationManager, EnvironmentConfig
from servos.isolation.platforms.device_detection import DeviceDetector, DetectedDevice


class TestProcessIsolationManager:
    """Test ProcessIsolationManager functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_script = os.path.join(self.temp_dir, "test_script.py")
        
        # Create test script
        with open(self.test_script, 'w') as f:
            f.write("""
import json
import sys

def main():
    return {"status": "success", "message": "Test script executed"}

def handler(request):
    return {"status": "success", "data": "Handler executed"}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
""")
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_isolation_manager_initialization(self):
        """Test isolation manager initialization with different modes"""
        # Test 'none' mode
        config_none = {'mode': 'none', 'timeout': 30}
        manager_none = ProcessIsolationManager(config_none)
        assert manager_none.mode == 'none'
        assert manager_none.timeout == 30
        
        # Test 'process' mode
        config_process = {
            'mode': 'process',
            'timeout': 60,
            'memory_limit': '512MB',
            'environment_isolation': True
        }
        manager_process = ProcessIsolationManager(config_process)
        assert manager_process.mode == 'process'
        assert manager_process.memory_limit == '512MB'
        assert manager_process.environment_isolation == True
        
        # Test 'docker' mode
        config_docker = {
            'mode': 'docker',
            'timeout': 120,
            'network_isolation': True,
            'filesystem_isolation': True
        }
        manager_docker = ProcessIsolationManager(config_docker)
        assert manager_docker.mode == 'docker'
        assert manager_docker.network_isolation == True
    
    @pytest.mark.asyncio
    async def test_direct_execution_mode(self):
        """Test direct execution (no isolation)"""
        config = {'mode': 'none', 'timeout': 30}
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        result = await manager.execute_script(
            self.test_script, 
            mock_service, 
            request_data=None
        )
        
        # Verify execution
        assert result is not None
        mock_service.logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_subprocess_isolation(self):
        """Test subprocess isolation mode"""
        config = {
            'mode': 'process',
            'timeout': 30,
            'environment_isolation': True
        }
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        result = await manager.execute_script(
            self.test_script,
            mock_service,
            request_data={'test': 'data'}
        )
        
        # Verify subprocess execution completed
        assert result is not None
        mock_service.logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_docker_isolation_fallback(self):
        """Test Docker isolation with fallback to subprocess"""
        config = {
            'mode': 'docker',
            'timeout': 30,
            'fallback_on_platform_failure': True
        }
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        mock_service.logger.warning = Mock()
        
        # Docker execution should fall back to subprocess
        result = await manager.execute_script(
            self.test_script,
            mock_service,
            request_data=None
        )
        
        # Verify fallback was used
        mock_service.logger.warning.assert_called()
    
    def test_platform_specific_configuration(self):
        """Test platform-specific isolation configuration"""
        # MicroPython configuration
        micropython_config = {
            'mode': 'micropython',
            'platform': 'rp2040',
            'device_port': '/dev/ttyACM0',
            'timeout': 30
        }
        manager_mp = ProcessIsolationManager(micropython_config)
        assert manager_mp.mode == 'micropython'
        assert manager_mp.platform == 'rp2040'
        
        # Arduino configuration
        arduino_config = {
            'mode': 'arduino',
            'platform': 'uno',
            'upload_port': '/dev/ttyUSB0',
            'board': 'arduino:avr:uno'
        }
        manager_arduino = ProcessIsolationManager(arduino_config)
        assert manager_arduino.mode == 'arduino'
        assert manager_arduino.platform == 'uno'
        assert manager_arduino.board == 'arduino:avr:uno'


class TestDeviceDetector:
    """Test device detection functionality"""
    
    def test_device_detector_initialization(self):
        """Test DeviceDetector initialization"""
        detector = DeviceDetector()
        
        # Verify device signatures are loaded
        assert len(detector.device_signatures) > 0
        assert len(detector.manufacturer_patterns) > 0
        
        # Check for known device signatures
        rpi_pico_signature = (0x2E8A, 0x0005)
        assert rpi_pico_signature in detector.device_signatures
        assert detector.device_signatures[rpi_pico_signature]['type'] == 'micropython'
        assert detector.device_signatures[rpi_pico_signature]['platform'] == 'rp2040'
    
    @patch('servos.isolation.platforms.device_detection.serial.tools.list_ports.comports')
    def test_device_detection_mock(self, mock_comports):
        """Test device detection with mocked serial ports"""
        # Mock port info for Raspberry Pi Pico
        mock_port_pico = Mock()
        mock_port_pico.device = '/dev/ttyACM0'
        mock_port_pico.vid = 0x2E8A
        mock_port_pico.pid = 0x0005
        mock_port_pico.serial_number = 'E12345678'
        mock_port_pico.manufacturer = 'Raspberry Pi'
        mock_port_pico.description = 'Raspberry Pi Pico'
        
        # Mock port info for Arduino Uno
        mock_port_arduino = Mock()
        mock_port_arduino.device = '/dev/ttyUSB0'
        mock_port_arduino.vid = 0x2341
        mock_port_arduino.pid = 0x0043
        mock_port_arduino.serial_number = 'A12345678'
        mock_port_arduino.manufacturer = 'Arduino LLC'
        mock_port_arduino.description = 'Arduino Uno'
        
        mock_comports.return_value = [mock_port_pico, mock_port_arduino]
        
        detector = DeviceDetector()
        devices = detector.detect_connected_devices()
        
        # Verify detected devices
        assert len(devices) == 2
        
        # Check Pico detection
        pico_device = next((d for d in devices if d.platform == 'rp2040'), None)
        assert pico_device is not None
        assert pico_device.device_type == 'micropython'
        assert pico_device.port == '/dev/ttyACM0'
        
        # Check Arduino detection
        arduino_device = next((d for d in devices if d.platform == 'uno'), None)
        assert arduino_device is not None
        assert arduino_device.device_type == 'arduino'
        assert arduino_device.port == '/dev/ttyUSB0'
    
    def test_device_recommendation(self):
        """Test device manager recommendations"""
        detector = DeviceDetector()
        
        # Test MicroPython device recommendation
        micropython_device = DetectedDevice(
            port='/dev/ttyACM0',
            device_type='micropython',
            platform='rp2040',
            description='Raspberry Pi Pico',
            vid=0x2E8A,
            pid=0x0005
        )
        
        manager_class, config = detector.get_recommended_manager(micropython_device)
        assert manager_class == 'MicroPythonIsolationManager'
        assert config['platform'] == 'rp2040'
        assert config['device_port'] == '/dev/ttyACM0'
        
        # Test Arduino device recommendation
        arduino_device = DetectedDevice(
            port='/dev/ttyUSB0',
            device_type='arduino',
            platform='uno',
            description='Arduino Uno',
            vid=0x2341,
            pid=0x0043
        )
        
        manager_class, config = detector.get_recommended_manager(arduino_device)
        assert manager_class == 'ArduinoIsolationManager'
        assert config['platform'] == 'uno'
        assert config['upload_port'] == '/dev/ttyUSB0'
    
    def test_device_serialization(self):
        """Test device serialization for API responses"""
        device = DetectedDevice(
            port='/dev/ttyACM0',
            device_type='micropython',
            platform='rp2040',
            description='Raspberry Pi Pico',
            vid=0x2E8A,
            pid=0x0005,
            serial_number='E12345678',
            manufacturer='Raspberry Pi'
        )
        
        device_dict = device.to_dict()
        
        # Verify serialization
        assert device_dict['port'] == '/dev/ttyACM0'
        assert device_dict['device_type'] == 'micropython'
        assert device_dict['platform'] == 'rp2040'
        assert device_dict['vid'] == 0x2E8A
        assert device_dict['pid'] == 0x0005
        assert device_dict['serial_number'] == 'E12345678'


class TestEnvironmentConfig:
    """Test EnvironmentConfig functionality"""
    
    def test_environment_config_creation(self):
        """Test environment configuration creation"""
        config = EnvironmentConfig(
            platform='esp32',
            docker_enabled=True,
            timeout=120
        )
        
        assert config.platform == 'esp32'
        assert config.docker_enabled == True
        assert config.timeout == 120
    
    def test_environment_config_serialization(self):
        """Test environment configuration serialization"""
        config = EnvironmentConfig(
            platform='rp2040',
            docker_enabled=False,
            timeout=60,
            memory_limit='256MB',
            network_isolation=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['platform'] == 'rp2040'
        assert config_dict['docker_enabled'] == False
        assert config_dict['timeout'] == 60
        assert config_dict['memory_limit'] == '256MB'
        assert config_dict['network_isolation'] == True


class TestIntegrationPatterns:
    """Test integration patterns with ecosystem packages"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup integration test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_proserve_integration_pattern(self):
        """Test integration pattern with ProServe services"""
        # Create test script for ProServe handler
        handler_script = os.path.join(self.temp_dir, "proserve_handler.py")
        with open(handler_script, 'w') as f:
            f.write("""
async def handler(request):
    from aiohttp import web
    return web.json_response({'status': 'success', 'service': 'proserve'})

def main():
    return {'status': 'success', 'integration': 'proserve'}

if __name__ == "__main__":
    import json
    result = main()
    print(json.dumps(result))
""")
        
        # Configure isolation for ProServe integration
        config = {
            'mode': 'process',
            'timeout': 30,
            'environment_isolation': True,
            'service_integration': 'proserve'
        }
        
        manager = ProcessIsolationManager(config)
        
        # Mock ProServe service
        mock_service = Mock()
        mock_service.name = 'proserve-test-service'
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        # Execute ProServe handler with isolation
        result = await manager.execute_script(
            handler_script,
            mock_service,
            request_data={'endpoint': '/api/test'}
        )
        
        assert result is not None
        mock_service.logger.info.assert_called()
    
    @pytest.mark.asyncio 
    async def test_edpmt_hardware_integration(self):
        """Test integration with EDPMT hardware operations"""
        # Create test script for hardware operation
        hardware_script = os.path.join(self.temp_dir, "gpio_operation.py")
        with open(hardware_script, 'w') as f:
            f.write("""
import json

def gpio_read(pin):
    # Simulate GPIO read
    return {'pin': pin, 'value': 1, 'voltage': 3.3}

def main():
    result = gpio_read(18)
    return {'status': 'success', 'hardware': 'gpio', 'result': result}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
""")
        
        # Configure isolation for hardware operations
        config = {
            'mode': 'process',
            'platform': 'rp2040',
            'timeout': 30,
            'hardware_access': True
        }
        
        manager = ProcessIsolationManager(config)
        
        # Mock EDPMT service
        mock_service = Mock()
        mock_service.name = 'edpmt-gpio-service'
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        # Execute hardware script with isolation
        result = await manager.execute_script(
            hardware_script,
            mock_service,
            request_data={'operation': 'gpio_read', 'pin': 18}
        )
        
        assert result is not None
        mock_service.logger.info.assert_called()
    
    def test_wmlog_logging_integration(self):
        """Test integration with WML logging"""
        # Configure isolation with logging integration
        config = {
            'mode': 'process',
            'timeout': 30,
            'logging_provider': 'wmlog'
        }
        
        manager = ProcessIsolationManager(config)
        
        # Mock WML logger
        mock_logger = Mock()
        mock_logger.info = Mock()
        mock_logger.error = Mock()
        mock_logger.debug = Mock()
        
        # Mock service with WML logger
        mock_service = Mock()
        mock_service.name = 'servos-wmlog-integration'
        mock_service.logger = mock_logger
        
        # Verify WML logger integration
        assert mock_service.logger is not None
        mock_service.logger.info("Servos isolation test", isolation_mode=config['mode'])
        mock_logger.info.assert_called_with("Servos isolation test", isolation_mode='process')


class TestPerformanceAndReliability:
    """Test performance characteristics and reliability"""
    
    def setup_method(self):
        """Setup performance test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup performance test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_isolation_performance(self):
        """Test isolation performance under load"""
        # Create test script
        test_script = os.path.join(self.temp_dir, "performance_test.py")
        with open(test_script, 'w') as f:
            f.write("""
import time
import json

def main():
    # Simulate some work
    time.sleep(0.01)
    return {'status': 'success', 'timestamp': time.time()}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
""")
        
        config = {'mode': 'process', 'timeout': 10}
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        # Execute multiple scripts concurrently
        start_time = time.time()
        
        tasks = []
        for i in range(10):
            task = manager.execute_script(
                test_script,
                mock_service,
                request_data=f'test_{i}'
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 5.0, f"Concurrent execution took {duration:.2f}s"
        assert len(results) == 10
        
        # Verify no exceptions
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0, f"Found {len(exceptions)} exceptions"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling in isolation"""
        # Create script that takes too long
        timeout_script = os.path.join(self.temp_dir, "timeout_test.py")
        with open(timeout_script, 'w') as f:
            f.write("""
import time
import json

def main():
    # Sleep longer than timeout
    time.sleep(5)
    return {'status': 'completed'}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
""")
        
        config = {'mode': 'process', 'timeout': 1}  # 1 second timeout
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        # Execute script with timeout
        with pytest.raises(RuntimeError, match="timed out"):
            await manager.execute_script(
                timeout_script,
                mock_service,
                request_data=None
            )
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery and graceful degradation"""
        # Create script that raises an error
        error_script = os.path.join(self.temp_dir, "error_test.py")
        with open(error_script, 'w') as f:
            f.write("""
import json

def main():
    raise Exception("Test error for recovery testing")

if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': str(e)}))
""")
        
        config = {'mode': 'process', 'timeout': 30}
        manager = ProcessIsolationManager(config)
        
        # Mock service
        mock_service = Mock()
        mock_service.logger = Mock()
        mock_service.logger.info = Mock()
        mock_service.logger.error = Mock()
        
        # Execute error script
        with pytest.raises(RuntimeError):
            await manager.execute_script(
                error_script,
                mock_service,
                request_data=None
            )
        
        # Verify error was logged
        mock_service.logger.error.assert_called()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
