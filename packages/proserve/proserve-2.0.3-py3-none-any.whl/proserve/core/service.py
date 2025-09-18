"""
ProServe Service - Simplified and Modular
New streamlined service that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular service system.
The heavy lifting is done by the core modules:
- service_core.py - Core service infrastructure
- service_refactored.py - Main refactored ProServeService class
- endpoint_manager.py - HTTP and WebSocket endpoint management
- task_manager.py - Background task management
- static_handler.py - Static file serving
- service_builder.py - Fluent API service builder
- service_fallback.py - Fallback and mock system

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular service components
from .service_core import ServiceCore
from .service_refactored import ProServeService
from .endpoint_manager import EndpointManager
from .task_manager import BackgroundTaskManager
from .static_handler import StaticFileHandler
from .service_builder import ServiceBuilder, ModularProServeService
from .service_fallback import ServiceFallbackManager, integrate_fallback_system

# Legacy compatibility - expose the main classes
__all__ = [
    'ServiceCore',
    'ProServeService',
    'EndpointManager',
    'BackgroundTaskManager', 
    'StaticFileHandler',
    'ServiceBuilder',
    'ModularProServeService',
    'ServiceFallbackManager',
    'integrate_fallback_system'
]
