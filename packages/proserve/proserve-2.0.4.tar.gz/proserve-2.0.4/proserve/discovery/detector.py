"""
ProServe Service Discovery - Simplified and Modular
New streamlined service detection that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular detection system.
The heavy lifting is done by the detection/ package modules:
- detection/service_models.py - Service detection data structures and types
- detection/framework_detector.py - Framework detection and analysis logic
- detection/service_detector.py - Main service detection and discovery logic

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular service detection components
from .detection import (
    ServiceModel,
    FrameworkModel,
    DetectionResult,
    ServiceConfig,
    FrameworkDetector,
    PythonFrameworkDetector,
    NodeFrameworkDetector,
    JavaFrameworkDetector,
    ServiceDetector,
    DirectoryScanner,
    ConfigurationAnalyzer,
    detect_services,
    detect_framework,
    detect_service_framework,
    detect_services_in_directory,
    analyze_service_file,
    scan_project_directory
)

# Legacy compatibility - expose the main classes
__all__ = [
    'ServiceModel',
    'ServiceInfo',  # Backward compatibility alias
    'FrameworkModel',
    'DetectionResult',
    'ServiceConfig',
    'FrameworkDetector',
    'PythonFrameworkDetector',
    'NodeFrameworkDetector',
    'JavaFrameworkDetector',
    'ServiceDetector',
    'DirectoryScanner',
    'ConfigurationAnalyzer',
    'detect_services',
    'detect_framework',
    'detect_service_framework',
    'detect_services_in_directory',
    'analyze_service_file',
    'scan_project_directory'
]

# Backward compatibility aliases
ServiceInfo = ServiceModel  # Alias for backward compatibility
