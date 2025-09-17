#!/usr/bin/env python3
"""
WML (Websocket MQTT Logging) Package Setup
Centralized logging system for distributed applications
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="wmlog",
    version="1.0.0",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    description="Websocket MQTT Logging - Centralized logging system for distributed applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wml-org/wml",
    project_urls={
        "Documentation": "https://wml.softreck.dev/docs",
        "Source": "https://github.com/wml-org/wml",
        "Tracker": "https://github.com/wml-org/wml/issues",
    },
    
    packages=find_packages(),
    include_package_data=True,
    
    # Core dependencies
    install_requires=[
        "structlog>=23.1.0",
        "rich>=13.0.0", 
        "aiohttp>=3.8.0",
        "paho-mqtt>=1.6.0",
        "websockets>=11.0.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "click>=8.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "redis": ["redis>=4.3.0"],
        "influxdb": ["influxdb-client>=1.36.0"],
        "elasticsearch": ["elasticsearch>=8.0.0"],
        "kafka": ["kafka-python>=2.0.0"],
        "monitoring": ["prometheus-client>=0.16.0", "grafana-api>=1.0.3"],
        "development": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black>=22.0.0"],
        "all": [
            "redis>=4.3.0",
            "influxdb-client>=1.36.0", 
            "elasticsearch>=8.0.0",
            "kafka-python>=2.0.0",
            "prometheus-client>=0.16.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0"
        ]
    },
    
    # Console scripts
    entry_points={
        "console_scripts": [
            "wmlog=wmlog.cli:cli",
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
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Framework :: AsyncIO",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "logging", "websocket", "mqtt", "distributed", "microservices",
        "structured-logging", "real-time", "monitoring", "observability",
        "asyncio", "broadcasting", "centralized-logging"
    ],
    
    # License
    license="Apache-2.0",
    
    # Python version requirements
    python_requires=">=3.8",
    zip_safe=False,
)
