"""
ProServe Core Module
Core components for the ProServe framework
"""

from .manifest import ServiceManifest, expand_env_vars
# Updated imports for new modular architecture
try:
    # Try importing from new modular structure first
    from ..isolation.platforms.platform_config import get_isolation_manager as ProcessIsolationManager
except ImportError:
    # Fallback for backward compatibility
    class ProcessIsolationManager:
        """Backward compatibility isolation manager"""
        pass

from .service import ProServeService
from .logging import setup_logging, create_logger
from .shell import ShellCommandHandler
from .grpc_handler import (
    GrpcServiceManager,
    GrpcServiceConfig,
    GrpcMethodConfig,
    ProtoFileGenerator,
    create_grpc_service_manager,
    is_grpc_service,
    create_hybrid_service
)
from .mock_system import MockSystemManager, MockService, MockEndpoint, MockResponse, get_mock_system
from .service_fallback import ServiceFallbackManager, integrate_fallback_system

__all__ = [
    "ServiceManifest",
    "ProcessIsolationManager", 
    "ProServeService",
    "expand_env_vars",
    "setup_logging",
    "create_logger",
    "ShellCommandHandler",
    "GrpcServiceManager",
    "GrpcServiceConfig",
    "GrpcMethodConfig", 
    "ProtoFileGenerator",
    "create_grpc_service_manager",
    "is_grpc_service",
    "create_hybrid_service",
    "MockSystemManager",
    "MockService",
    "MockEndpoint", 
    "MockResponse",
    "get_mock_system",
    "ServiceFallbackManager",
    "integrate_fallback_system"
]
