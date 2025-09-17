#!/usr/bin/env python3
"""
Servos CLI - Service Environment Isolation & Orchestration System
==================================================================

Command-line interface for managing environment isolation and container orchestration.

Author: Tom Sapletta
License: Apache 2.0
"""

import argparse
import sys
from typing import Optional

from . import __version__
from .core.isolation import IsolationManager, EnvironmentConfig

try:
    from .isolation.platforms import PlatformDetector
    PLATFORM_DETECTION_AVAILABLE = True
except ImportError:
    PLATFORM_DETECTION_AVAILABLE = False
    PlatformDetector = None


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog='servos',
        description='Servos - Service Environment Isolation & Orchestration System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  servos detect                    # Detect current platform
  servos isolate script.py         # Run script in isolated environment
  servos list-platforms            # List supported platforms
  servos version                   # Show version information

For more information: https://github.com/servos/servos
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'Servos {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Detect platform command
    detect_parser = subparsers.add_parser(
        'detect', 
        help='Detect current platform and environment'
    )
    detect_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed platform information'
    )
    
    # Isolate command
    isolate_parser = subparsers.add_parser(
        'isolate',
        help='Run script in isolated environment'
    )
    isolate_parser.add_argument(
        'script',
        help='Script file to execute in isolation'
    )
    isolate_parser.add_argument(
        '--platform', '-p',
        help='Target platform (auto-detected if not specified)'
    )
    isolate_parser.add_argument(
        '--environment', '-e',
        help='Environment configuration file'
    )
    
    # List platforms command
    list_parser = subparsers.add_parser(
        'list-platforms',
        help='List supported platforms'
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    
    return parser


def cmd_detect(args) -> int:
    """Handle platform detection command."""
    if not PLATFORM_DETECTION_AVAILABLE:
        print("❌ Platform detection not available. Install with: pip install servos[all]")
        return 1
    
    try:
        detector = PlatformDetector()
        platform = detector.detect_platform()
        
        print(f"🔍 Platform Detection Results:")
        print(f"   Platform: {platform}")
        
        if args.verbose:
            # Add more detailed platform information if available
            print(f"   Architecture: {detector.get_architecture() if hasattr(detector, 'get_architecture') else 'Unknown'}")
            print(f"   OS: {detector.get_os() if hasattr(detector, 'get_os') else 'Unknown'}")
        
        return 0
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
        return 1


def cmd_isolate(args) -> int:
    """Handle script isolation command."""
    try:
        # Create environment config
        config = EnvironmentConfig()
        if args.environment:
            config.load_from_file(args.environment)
        
        # Create isolation manager
        manager = IsolationManager(platform=args.platform, config=config)
        
        print(f"🚀 Executing script in isolated environment: {args.script}")
        result = manager.execute_isolated(args.script)
        
        if result:
            print("✅ Script executed successfully")
            return 0
        else:
            print("❌ Script execution failed")
            return 1
            
    except Exception as e:
        print(f"❌ Isolation failed: {e}")
        return 1


def cmd_list_platforms(args) -> int:
    """Handle list platforms command."""
    platforms = [
        "arduino - Arduino and compatible microcontrollers",
        "micropython - MicroPython environments",
        "arm64 - ARM64 processors",
        "x86_64 - Standard x86_64 processors",
        "rpi-arm - Raspberry Pi ARM"
    ]
    
    print("🌍 Supported Platforms:")
    for platform in platforms:
        print(f"   • {platform}")
    
    return 0


def cmd_version(args) -> int:
    """Handle version command."""
    print(f"Servos {__version__}")
    print("Service Environment Isolation & Orchestration System")
    print("Author: Tom Sapletta")
    print("License: Apache 2.0")
    print("Homepage: https://github.com/servos/servos")
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to appropriate command handler
    handlers = {
        'detect': cmd_detect,
        'isolate': cmd_isolate,
        'list-platforms': cmd_list_platforms,
        'version': cmd_version,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
