"""
ProServe - Professional Service Framework
Advanced manifest-based microservice framework with multi-environment isolation

A powerful Python library for building scalable microservices with declarative YAML manifests,
supporting deployment across diverse environments from cloud containers to embedded devices
like RP2040 and Arduino.
"""

__version__ = "1.0.0"
__author__ = "ProServe Team"
__email__ = "team@proserve.dev"
__license__ = "MIT"
__url__ = "https://github.com/proserve/proserve"

# Core imports - Original API (backward compatibility)
from .core.manifest import ServiceManifest, expand_env_vars
# Updated imports for new modular architecture (fixed to use Servos)
try:
    from servos.core.isolation import ProcessIsolationManager
except ImportError:
    # Backward compatibility fallback if Servos not available
    class ProcessIsolationManager:
        """Backward compatibility isolation manager"""
        def __init__(self, *args, **kwargs):
            pass

from .core.service import ProServeService
from .core.logging import setup_logging, create_logger

# New Simplified API - Recommended for new projects
from .core.service_builder import Service, ServiceBuilder, ModularProServeService
from .core.service_refactored import ProServeService as ProServeServiceModular
from .core.mock_system import MockSystemManager, MockService, MockEndpoint, MockResponse, get_mock_system
from .core.service_fallback import ServiceFallbackManager, integrate_fallback_system
from .core.shell import ShellCommandHandler
from .core.grpc_handler import (
    GrpcServiceManager,
    GrpcServiceConfig,
    GrpcMethodConfig,
    ProtoFileGenerator,
    create_grpc_service_manager,
    is_grpc_service,
    create_hybrid_service
)

# CLI interface
from .cli import ProServeCLI

# Utilities
from .utils.config import ProServeConfig, get_config, set_config, load_config
from .utils.helpers import (
    get_framework_info, validate_environment, detect_service_framework,
    generate_service_id, sanitize_service_name, get_platform_info,
    detect_devices, is_embedded_platform, get_available_ports
)
from .utils.runner import ServiceRunner, EmbeddedRunner, DockerRunner, create_runner, run_service

# Discovery tools
from .discovery import (
    ServiceDetector, FrameworkDetector, ServiceInfo, ManifestGenerator,
    detect_service_framework, detect_services_in_directory,
    generate_manifest_from_service, scan_for_services
)

# Migration tools  
from .migration import (
    MigrationOrchestrator, ServiceMigrator, EDPMTMigrator, ServiceDeployer,
    MigrationResult, MigrationConfig, MigrationStrategy, BlueGreenStrategy, RollingStrategy,
    orchestrate_migration, migrate_service_to_proserve, migrate_framework_service, validate_migration
)

# SDK imports
from .sdk.manifest_builder import (
    ManifestBuilder,
    EndpointBuilder,
    DatabaseBuilder,
    LoggingBuilder,
    GrpcServiceBuilder,
    from_template,
    TEMPLATES
)
from .sdk.api_server import (
    ManifestAPIServer,
    start_api_server,
    create_manifest_api
)

# Tools imports
from .tools.command_generator import (
    CommandGenerator,
    GeneratedCommand,
    generate_commands_from_manifest,
    export_commands_as_script,
    generate_documentation
)

# Export main API
__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    
    # Core classes
    "ServiceManifest",
    "ProcessIsolationManager", 
    "ProServeService",
    "ShellCommandHandler",
    "expand_env_vars",
    "setup_logging",
    "create_logger",
    
    # gRPC classes
    "GrpcServiceManager",
    "GrpcServiceConfig",
    "GrpcMethodConfig",
    "ProtoFileGenerator",
    "create_grpc_service_manager",
    "is_grpc_service",
    "create_hybrid_service",
    
    # Mock System and Fallbacks
    "MockSystemManager",
    "MockService",
    "MockEndpoint", 
    "MockResponse",
    "get_mock_system",
    "ServiceFallbackManager",
    "integrate_fallback_system",
    
    # CLI interface
    "ProServeCLI",
    
    # Service runners
    "ServiceRunner",
    "EmbeddedRunner",
    "DockerRunner",
    "create_runner",
    "run_service",
    
    # Configuration
    "ProServeConfig",
    "get_config",
    "set_config", 
    "load_config",
    
    # Utilities
    "get_framework_info",
    "validate_environment",
    "detect_service_framework",
    "generate_service_id",
    "sanitize_service_name",
    "get_platform_info",
    "detect_devices",
    "is_embedded_platform",
    "get_available_ports",
    
    # Discovery tools
    "ServiceDetector",
    "FrameworkDetector",
    "ServiceInfo",
    "ManifestGenerator",
    "detect_services_in_directory",
    "generate_manifest_from_service",
    "scan_for_services",
    
    # Migration tools
    "MigrationOrchestrator",
    "ServiceMigrator",
    "EDPMTMigrator",
    "ServiceDeployer",
    "MigrationResult",
    "MigrationConfig",
    "MigrationStrategy",
    "BlueGreenStrategy",
    "RollingStrategy",
    "orchestrate_migration",
    "migrate_service_to_proserve",
    "migrate_framework_service",
    "validate_migration",
    
    # SDK tools
    "ManifestBuilder",
    "EndpointBuilder",
    "DatabaseBuilder",
    "LoggingBuilder",
    "GrpcServiceBuilder",
    "from_template",
    "TEMPLATES",
    "ManifestAPIServer",
    "start_api_server",
    "create_manifest_api",
    
    # Command generation tools
    "CommandGenerator",
    "GeneratedCommand",
    "generate_commands_from_manifest",
    "export_commands_as_script",
    "generate_documentation",
    
    # Convenience functions
    "quick_start",
    "create_http_service",
    "create_websocket_service",
    "create_micropython_service",
    "create_arduino_service",
    "get_info",
    "check_environment",
]

# Framework information
def get_info():
    """Get ProServe framework information"""
    return {
        "name": "ProServe",
        "version": __version__,
        "description": "Professional Service Framework",
        "author": __author__,
        "license": __license__,
        "url": __url__,
        "features": [
            "Manifest-driven architecture",
            "Multi-environment isolation",
            "Auto-discovery & migration",
            "Zero vendor lock-in",
            "MicroPython & Arduino support",
            "Docker & Kubernetes ready",
            "Structured logging",
            "Health & metrics endpoints"
        ],
        "environments": [
            "cloud", "docker", "kubernetes", 
            "micropython", "arduino", "rp2040",
            "esp32", "esp8266"
        ]
    }

# Environment validation
def check_environment():
    """Check if ProServe environment is properly configured"""
    try:
        # Test core imports
        from .core.service import ProServeService
        from .core.manifest import ServiceManifest
        
        # Test extended environments
        try:
            from servos.core.isolation import ProcessIsolationManager as MicroPythonIsolationManager
            micropython_available = True
        except ImportError:
            micropython_available = False
        
        try:
            from servos.core.isolation import ProcessIsolationManager as ArduinoIsolationManager
            arduino_available = True
        except ImportError:
            arduino_available = False
        
        return {
            "status": "ok",
            "core_available": True,
            "micropython_available": micropython_available,
            "arduino_available": arduino_available,
            "version": __version__
        }
        
    except ImportError as e:
        return {
            "status": "error",
            "error": str(e),
            "core_available": False
        }

# Quick start function
def quick_start(manifest_path: str, **kwargs):
    """Quick start a ProServe service from manifest"""
    try:
        manifest = ServiceManifest.from_yaml(manifest_path)
        service = ProServeService(manifest, **kwargs)
        return service
    except Exception as e:
        raise Exception(f"Quick start failed: {e}")

# Convenience functions for common use cases
def create_http_service(name: str, port: int = 8080, **kwargs):
    """Create a simple HTTP service"""
    manifest_data = {
        "name": name,
        "version": "1.0.0", 
        "type": "http",
        "port": port,
        "host": "0.0.0.0",
        **kwargs
    }
    
    manifest = ServiceManifest(**manifest_data)
    return ProServeService(manifest)

def create_websocket_service(name: str, port: int = 8080, **kwargs):
    """Create a WebSocket service"""
    manifest_data = {
        "name": name,
        "version": "1.0.0",
        "type": "websocket", 
        "port": port,
        "host": "0.0.0.0",
        "websocket_handlers": [
            {"path": "/ws", "script": "handlers/websocket.py"}
        ],
        **kwargs
    }
    
    manifest = ServiceManifest(**manifest_data)
    return ProServeService(manifest)

def create_micropython_service(name: str, platform: str = "rp2040", **kwargs):
    """Create a MicroPython service for embedded devices"""
    manifest_data = {
        "name": name,
        "version": "1.0.0",
        "type": "micropython",
        "isolation": {
            "mode": "micropython",
            "platform": platform,
            "auto_environment": True
        },
        **kwargs
    }
    
    manifest = ServiceManifest(**manifest_data)
    return ProServeService(manifest)

def create_arduino_service(name: str, board: str = "esp32dev", **kwargs):
    """Create an Arduino service"""
    manifest_data = {
        "name": name,
        "version": "1.0.0", 
        "type": "arduino",
        "isolation": {
            "mode": "arduino",
            "board": board,
            "auto_environment": True
        },
        **kwargs
    }
    
    manifest = ServiceManifest(**manifest_data)
    return ProServeService(manifest)

# Module initialization
def _initialize_proserve():
    """Initialize ProServe framework"""
    import logging
    
    # Set up basic logging
    logging.getLogger("proserve").setLevel(logging.INFO)
    
    # Check environment on import
    env_status = check_environment()
    if env_status["status"] != "ok":
        logging.warning(f"ProServe environment check failed: {env_status}")

# Initialize on import
_initialize_proserve()

# Print welcome message in debug mode
import os
if os.getenv("PROSERVE_DEBUG"):
    print(f"🚀 ProServe v{__version__} initialized")
    print(f"   Environment: {check_environment()['status']}")
    print(f"   Info: {__url__}")
