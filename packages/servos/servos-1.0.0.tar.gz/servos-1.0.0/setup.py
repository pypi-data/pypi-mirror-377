#!/usr/bin/env python3
"""
Servos - Service Environment Isolation & Orchestration System
==============================================================

A lightweight Python library for environment isolation, Docker orchestration, 
and multi-platform service deployment. Extracted from ProServe framework 
to provide focused environment isolation capabilities.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README and requirements
README = (Path(__file__).parent / "README.md").read_text(encoding='utf-8')
REQUIREMENTS = (Path(__file__).parent / "requirements.txt").read_text().strip().split('\n')

setup(
    name="servos",
    version="1.0.0",
    description="Service Environment Isolation & Orchestration System",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Tom Sapletta", 
    author_email="tom@sapletta.com",
    url="https://github.com/tom-sapletta-com/servos",
    project_urls={
        "Documentation": "https://github.com/tom-sapletta-com/servos",
        "Source": "https://github.com/tom-sapletta-com/servos",
        "Tracker": "https://github.com/tom-sapletta-com/servos/issues",
        "ProServe": "https://pypi.org/project/proserve/",
    },
    
    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    package_data={
        "servos": [
            "docker/*/requirements.txt",
            "docker/*/Dockerfile", 
            "docker/*/entrypoint.sh",
            "isolation/platforms/*.py",
        ]
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=REQUIREMENTS,
    python_requires=">=3.8",
    
    # Optional dependencies
    extras_require={
        "docker": ["docker>=6.0.0"],
        "micropython": ["adafruit-circuitpython-bundle", "esptool>=4.4"],
        "arduino": ["platformio>=6.1.0", "arduino-cli>=0.30.0"],
        "rp2040": ["picotool>=1.1.0", "rp2040-tools>=0.1.0"],
        "testing": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.0.0"],
        "development": ["black>=22.0.0", "flake8>=5.0.0", "mypy>=0.991"],
        "all": [
            "docker>=6.0.0",
            "adafruit-circuitpython-bundle",
            "esptool>=4.4", 
            "platformio>=6.1.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0"
        ]
    },
    
    # Console scripts
    entry_points={
        "console_scripts": [
            "servos=servos.cli:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "isolation", "docker", "environment", "orchestration", 
        "micropython", "arduino", "rp2040", "containers",
        "deployment", "virtualization", "asyncio", "embedded"
    ],
    
    # License
    license="Apache-2.0",
    
    # Minimum version requirements
    zip_safe=False,
)
