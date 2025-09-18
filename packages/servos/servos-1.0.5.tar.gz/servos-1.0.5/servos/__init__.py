#!/usr/bin/env python3
"""
Servos - Service Environment Isolation & Orchestration System
==============================================================

A lightweight Python library for environment isolation, Docker orchestration, 
and multi-platform service deployment.

Main Components:
- Environment Isolation: Docker-based isolated execution environments
- Platform Support: Arduino, MicroPython, ARM64, x86_64
- Container Management: Automated Docker container lifecycle
- Device Detection: Hardware platform auto-detection
- Service Orchestration: Multi-environment service coordination

Usage:
    from servos import IsolationManager, PlatformDetector
    from servos.docker import ContainerManager
    
    # Detect platform
    detector = PlatformDetector()
    platform = detector.detect_platform()
    
    # Create isolated environment
    manager = IsolationManager(platform=platform)
    result = manager.execute_isolated(script_path="my_script.py")
"""

__version__ = "1.0.0"
__author__ = "Servos Team"
__email__ = "team@servos.dev"
__license__ = "MIT"

# Core imports
from .core.isolation import IsolationManager, EnvironmentConfig
from .isolation.platforms import DeviceDetector, PlatformConfig

# Make key classes available at package level
__all__ = [
    "IsolationManager",
    "EnvironmentConfig", 
    "DeviceDetector",
    "PlatformConfig",
    "__version__"
]
