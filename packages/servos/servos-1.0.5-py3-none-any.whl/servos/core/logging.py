"""
Servos Logging Integration with WML
WML (Websocket MQTT Logging) integration for Servos environment isolation framework
"""

import os
from typing import Dict, Any, Optional

# WML integration - provides centralized logging for Servos
from wmlog import WMLLogger, LoggingConfig, LogContext as WMLLogContext
from wmlog.mqtt import WebSocketBroadcaster
from wmlog.formatters import RichConsoleFormatter


# Backward compatibility aliases for Servos LoggingConfig
class ServosLoggingConfig:
    """Servos logging configuration - delegates to WML LoggingConfig"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Map Servos config to WML config
        self.wml_config = LoggingConfig(
            service_name=config.get('service_name', 'servos'),
            log_level=config.get('level', 'info').lower(),
            console_enabled=config.get('console_output', True),
            console_format='rich' if config.get('console_colors', True) else 'compact',
            file_enabled=config.get('file_output', False),
            file_path=config.get('log_file', '/tmp/servos.log'),
            websocket_enabled=config.get('enable_websocket', True),
            websocket_port=config.get('websocket_port', 8766),
            include_timestamp=config.get('include_timestamps', True),
            include_caller=config.get('include_caller', False)
        )


# Backward compatibility aliases for Servos LogContext
class ServosLogContext:
    """Servos log context - delegates to WML LogContext"""
    
    def __init__(self, service_name: str = 'servos', isolation_mode: str = 'none', 
                 platform: Optional[str] = None, **kwargs):
        # Create WML LogContext with Servos-specific context
        self.wml_context = WMLLogContext(
            service_name=service_name,
            environment='servos-isolation',
            custom_fields={
                'framework': 'servos',
                'isolation_mode': isolation_mode,
                'platform': platform,
                **kwargs
            }
        )
        
        # Store original attributes for backward compatibility
        self.service_name = service_name
        self.isolation_mode = isolation_mode
        self.platform = platform
        self.extra_context = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging"""
        return self.wml_context.to_dict()


# Backward compatibility alias - use WML LogContext directly to avoid recursion
LogContext = WMLLogContext


# Global WML logger instance for Servos
_servos_logger: Optional[WMLLogger] = None


def get_servos_logger(config: Optional[Dict[str, Any]] = None) -> WMLLogger:
    """Get the global Servos WML logger instance"""
    global _servos_logger
    if _servos_logger is None:
        servos_config = ServosLoggingConfig(config)
        context = LogContext(
            service_name='servos',
            isolation_mode='multi-environment',
            custom_data={'framework': 'servos'}
        )
        _servos_logger = WMLLogger.get_logger(servos_config.wml_config, context)
    return _servos_logger


def setup_logging(
    service_name: str = 'servos',
    isolation_mode: str = "none",
    platform: Optional[str] = None,
    debug: bool = False,
    console_output: bool = True,
    json_output: bool = False,
    log_file: Optional[str] = None,
    enable_websocket_broadcast: bool = True,
    context: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Setup Servos logging system using WML - simplified implementation
    
    Args:
        service_name: Name of the service
        isolation_mode: Current isolation mode (docker, micropython, arduino, etc.)
        platform: Target platform (e.g., rp2040, esp32, arm64)
        debug: Enable debug logging
        console_output: Enable console output
        json_output: Use JSON format for logs
        log_file: Optional log file path
        enable_websocket_broadcast: Enable WebSocket log broadcasting
        context: Additional context for logging
        **kwargs: Additional context parameters
    
    Returns:
        WML logger instance with Servos context
    """
    
    # Prepare configuration for WML
    config_dict = context or {}
    
    # Override config with explicit parameters
    if debug:
        config_dict['level'] = 'debug'
        config_dict['include_caller'] = True
    else:
        config_dict.setdefault('level', 'info')
        
    if console_output is not None:
        config_dict['console_output'] = console_output
    if json_output:
        config_dict['format'] = 'json'
    if log_file:
        config_dict['file_output'] = True
        config_dict['log_file'] = log_file
    if enable_websocket_broadcast:
        config_dict['enable_websocket'] = True
        
    # Set service name
    config_dict['service_name'] = service_name
    
    # Create WML configuration
    wml_config = LoggingConfig(
        service_name=service_name,
        log_level=config_dict.get('level', 'info'),
        console_enabled=config_dict.get('console_output', True),
        console_format='json' if json_output else 'rich',
        file_enabled=config_dict.get('file_output', False),
        file_path=config_dict.get('log_file', f'/tmp/{service_name}.log'),
        websocket_enabled=config_dict.get('enable_websocket', enable_websocket_broadcast),
        websocket_port=config_dict.get('websocket_port', 8766),
        include_timestamp=config_dict.get('include_timestamps', True),
        include_caller=config_dict.get('include_caller', debug)
    )
    
    # Create Servos-specific context using our wrapper
    servos_context = ServosLogContext(
        service_name=service_name,
        isolation_mode=isolation_mode,
        platform=platform,
        **kwargs
    )
    
    # Get WML logger with Servos context
    wml_logger = WMLLogger.get_logger(wml_config, servos_context.wml_context)
    
    # Return the WML logger for backward compatibility
    return wml_logger


def create_logger(name: str, **context):
    """Create a logger with optional context - simplified WML version"""
    wml_config = LoggingConfig(service_name=name, console_enabled=True, console_format='rich')
    ctx = LogContext(service_name=name, custom_data=context) if context else None
    return WMLLogger.get_logger(wml_config, ctx)


# Convenience functions for common Servos logging patterns
def log_isolation_start(logger, isolation_mode: str, platform: Optional[str] = None):
    """Log isolation environment startup"""
    logger.logger.info(
        "Starting isolation environment",
        isolation_mode=isolation_mode,
        platform=platform,
        event_type="isolation_start"
    )


def log_isolation_stop(logger, isolation_mode: str):
    """Log isolation environment shutdown"""
    logger.logger.info(
        "Stopping isolation environment",
        isolation_mode=isolation_mode,
        event_type="isolation_stop"
    )


def log_script_execution(
    logger,
    script_path: str,
    isolation_mode: str,
    platform: Optional[str] = None,
    execution_time: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """Log script execution in isolation environment"""
    log_data = {
        "script_path": script_path,
        "isolation_mode": isolation_mode,
        "platform": platform,
        "event_type": "script_execution",
        "success": success
    }
    
    if execution_time is not None:
        log_data["execution_time"] = execution_time
    
    if error:
        log_data["error"] = error
        logger.logger.error("Script execution failed in isolation", **log_data)
    else:
        logger.logger.info("Script execution completed in isolation", **log_data)


def log_docker_operation(logger, operation: str, container_name: str, success: bool = True, error: Optional[str] = None):
    """Log Docker operations in isolation environment"""
    log_data = {
        "operation": operation,
        "container_name": container_name,
        "event_type": "docker_operation",
        "success": success
    }
    
    if error:
        log_data["error"] = error
        logger.logger.error(f"Docker {operation} failed", **log_data)
    else:
        logger.logger.info(f"Docker {operation} completed", **log_data)


def log_platform_detection(logger, detected_platform: str, confidence: float = 1.0):
    """Log platform detection results"""
    logger.logger.info(
        "Platform detected",
        platform=detected_platform,
        confidence=confidence,
        event_type="platform_detection"
    )


# Legacy compatibility functions
def create_context_from_isolation(isolation_mode: str, platform: Optional[str] = None, **kwargs) -> LogContext:
    """Create log context from isolation information"""
    return LogContext(
        service_name='servos',
        isolation_mode=isolation_mode,
        platform=platform,
        **kwargs
    )


def setup_enhanced_logging(**kwargs):
    """Enhanced logging setup (compatibility)"""
    return setup_logging(**kwargs)
