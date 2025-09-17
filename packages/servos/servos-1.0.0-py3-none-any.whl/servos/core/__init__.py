"""
Servos Core Module
==================

Core functionality for environment isolation and service orchestration.

This module provides the foundational classes and utilities for:
- Environment isolation management
- Docker container orchestration
- Cross-platform service execution
- Resource management and cleanup
"""

from .isolation import IsolationManager, EnvironmentConfig

__all__ = [
    "IsolationManager",
    "EnvironmentConfig"
]
