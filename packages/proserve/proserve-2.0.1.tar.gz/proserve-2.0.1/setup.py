#!/usr/bin/env python3
"""
ProServe - Professional Service Framework
Advanced manifest-based microservice framework with multi-environment isolation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
README = (Path(__file__).parent / "README.md").read_text(encoding='utf-8')

# Define requirements directly (for reliable building)
REQUIREMENTS = [
    "aiohttp>=3.8.0",
    "aiohttp-cors>=0.7.0", 
    "structlog>=25.0.0",
    "rich>=14.0.0",
    "python-dotenv>=1.0.0",
    "PyYAML>=6.0",
    "astor>=0.8.1",
    "setuptools>=60.0.0",
    "typing-extensions>=4.0.0",
    "wmlog>=1.0.0",  # wmlog logging system integration
]

setup(
    name="proserve",
    version="2.0.1",
    description="Professional Service Framework - Revolutionary modular microservice framework with zero-config API",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Tom Sapletta", 
    author_email="info@softreck.dev",
    url="https://github.com/tom-sapletta-com/proserve",
    project_urls={
        "Documentation": "https://github.com/tom-sapletta-com/proserve",
        "Source": "https://github.com/tom-sapletta-com/proserve",
        "Tracker": "https://github.com/tom-sapletta-com/proserve/issues",
        "Servos": "https://pypi.org/project/servos/",
    },
    
    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    package_data={
        "proserve": [
            "templates/*.yaml",
            "templates/*.yml", 
            "templates/*.json",
        ]
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=REQUIREMENTS,
    python_requires=">=3.8",
    
    # Optional dependencies
    extras_require={
        "docker": ["docker>=6.0.0"],
        "kubernetes": ["kubernetes>=25.0.0"],
        "monitoring": ["prometheus-client>=0.15.0", "grafana-api>=1.0.3"],
        "micropython": ["adafruit-circuitpython-bundle", "esptool>=4.4"],
        "arduino": ["platformio>=6.1.0", "arduino-cli>=0.30.0"],
        "rp2040": ["picotool>=1.1.0", "rp2040-tools>=0.1.0"],
        "testing": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.0.0", "requests>=2.28.0"],
        "development": ["black>=22.0.0", "flake8>=5.0.0", "mypy>=0.991"],
        "all": [
            "docker>=6.0.0", 
            "kubernetes>=25.0.0",
            "prometheus-client>=0.15.0",
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
            "proserve=proserve.cli:main",
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
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "microservices", "manifest", "service-framework", "docker", 
        "kubernetes", "isolation", "micropython", "arduino", "rp2040",
        "deployment", "migration", "monitoring", "asyncio", "aiohttp"
    ],
    
    # License
    license="Apache-2.0",
    
    # Minimum version requirements
    zip_safe=False,
)
