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
    'detect_service_framework', 'detect_services_in_directory', 'analyze_service_file'
]

# Backward compatibility exports
ServiceDetector = ServiceDetector
ServiceInfo = ServiceInfo
FrameworkDetector = FrameworkDetector
