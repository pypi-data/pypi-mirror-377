"""
ProServe Service Detection - Modular Service Detection Components
Refactored from monolithic detector.py into focused, testable detection modules
"""

from .service_models import (
    Framework, MigrationDifficulty, EndpointInfo, DatabaseInfo, DeploymentInfo,
    ServiceInfo, DetectionResult, create_endpoint_from_route_info,
    create_basic_service_info, merge_service_info
)
from .framework_detector import (
    FrameworkDetector, get_framework_by_name, get_supported_frameworks, is_web_framework
)
from .service_detector import (
    ServiceDetector, detect_service_framework, detect_services_in_directory,
    analyze_service_file, create_service_detector
)

__all__ = [
    # Core Enums and Models
    'Framework', 'MigrationDifficulty', 'EndpointInfo', 'DatabaseInfo', 'DeploymentInfo',
    'ServiceInfo', 'DetectionResult',
    
    # Model Utilities
    'create_endpoint_from_route_info', 'create_basic_service_info', 'merge_service_info',
    
    # Framework Detection
    'FrameworkDetector', 'get_framework_by_name', 'get_supported_frameworks', 'is_web_framework',
    
    # Service Detection
    'ServiceDetector', 'create_service_detector',
    
    # Backward Compatibility Functions
    'detect_service_framework', 'detect_services_in_directory', 'analyze_service_file',
    
    # Backward Compatibility Aliases
    'ServiceModel', 'ServiceConfig', 'FrameworkModel',
    
    # Framework Detector Aliases (for backward compatibility)
    'PythonFrameworkDetector', 'NodeFrameworkDetector', 'JavaFrameworkDetector',
    'GoFrameworkDetector', 'RustFrameworkDetector', 'PHPFrameworkDetector', 
    'RubyFrameworkDetector', 'CSharpFrameworkDetector',
    
    # Additional Compatibility Aliases
    'DirectoryScanner', 'FileScanner', 'DependencyScanner', 'ConfigurationAnalyzer',
    'DatabaseAnalyzer', 'PortAnalyzer', 'SecurityAnalyzer',
    
    # Function Aliases (for backward compatibility)
    'detect_services', 'detect_framework'
]

# Backward compatibility exports
ServiceDetector = ServiceDetector
ServiceInfo = ServiceInfo
ServiceModel = ServiceInfo  # Alias for backward compatibility
ServiceConfig = ServiceInfo  # Alias for backward compatibility
FrameworkDetector = FrameworkDetector
FrameworkModel = Framework  # Alias for backward compatibility

# All framework detector aliases for backward compatibility
PythonFrameworkDetector = FrameworkDetector
NodeFrameworkDetector = FrameworkDetector  
JavaFrameworkDetector = FrameworkDetector
GoFrameworkDetector = FrameworkDetector
RustFrameworkDetector = FrameworkDetector
PHPFrameworkDetector = FrameworkDetector
RubyFrameworkDetector = FrameworkDetector
CSharpFrameworkDetector = FrameworkDetector

# Additional backward compatibility aliases
DirectoryScanner = ServiceDetector  # Alias for backward compatibility
FileScanner = ServiceDetector  # Alias for backward compatibility
DependencyScanner = ServiceDetector  # Alias for backward compatibility
ConfigurationAnalyzer = ServiceDetector  # Alias for backward compatibility
DatabaseAnalyzer = ServiceDetector  # Alias for backward compatibility
PortAnalyzer = ServiceDetector  # Alias for backward compatibility
SecurityAnalyzer = ServiceDetector  # Alias for backward compatibility

# Function aliases for backward compatibility
detect_services = detect_services_in_directory  # Alias for backward compatibility

# Function aliases for backward compatibility
detect_services = detect_services_in_directory  # Alias for backward compatibility
detect_framework = detect_service_framework  # Alias for backward compatibility
scan_project_directory = detect_services_in_directory  # Alias for backward compatibility
