"""
ProServe Discovery Package
Service discovery, framework detection, and manifest generation tools
"""

from .detector import (
    ServiceDetector,
    FrameworkDetector,
    ServiceModel as ServiceInfo,  # Alias for backward compatibility
    detect_service_framework,
    detect_services_in_directory,
    analyze_service_file
)

from .generator import (
    ManifestGenerator,
    generate_manifest_from_service,
    generate_manifest_from_directory,
    create_default_manifest
)

from .scanner import (
    DirectoryScanner,
    ServiceScanner,
    scan_for_services,
    find_service_files
)

__all__ = [
    'ServiceDetector',
    'FrameworkDetector',
    'ServiceInfo',
    'detect_service_framework',
    'detect_services_in_directory',
    'analyze_service_file',
    'ManifestGenerator',
    'generate_manifest_from_service',
    'generate_manifest_from_directory',
    'create_default_manifest',
    'DirectoryScanner',
    'ServiceScanner',
    'scan_for_services',
    'find_service_files'
]
