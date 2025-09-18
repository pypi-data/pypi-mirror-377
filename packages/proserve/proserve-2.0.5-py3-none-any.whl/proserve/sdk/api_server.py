"""
ProServe API Server - Simplified and Modular
New streamlined API server that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular API system.
The heavy lifting is done by the api/ package modules:
- api/models.py - API data models and structures
- api/storage.py - Manifest storage and persistence
- api/endpoints.py - API endpoint handlers and routing
- api/server.py - Main API server implementation

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular API server components
from .api import (
    APIModel,
    ManifestModel,
    ServiceModel,
    EndpointModel,
    ManifestStorage,
    FileStorage,
    MemoryStorage,
    APIEndpoints,
    ManifestEndpoints,
    ServiceEndpoints,
    APIServer,
    ManifestAPIServer,
    create_api_server,
    start_api_server
)

# Backward compatibility aliases
def create_manifest_api(*args, **kwargs):
    """Backward compatibility alias for create_api_server"""
    return create_api_server(*args, **kwargs)

# Legacy compatibility - expose the main classes
__all__ = [
    'APIModel',
    'ManifestModel',
    'ServiceModel',
    'EndpointModel',
    'ManifestStorage',
    'FileStorage',
    'MemoryStorage',
    'APIEndpoints',
    'ManifestEndpoints',
    'ServiceEndpoints',
    'APIServer',
    'ManifestAPIServer',
    'create_api_server',
    'create_manifest_api',
    'start_api_server'
]
