"""
ProServe SDK API - Modular Manifest API Components
Refactored from monolithic api_server.py into focused, testable API modules
"""

from .models import (
    ManifestProject, APIResponse, ProjectFilter, ProjectStats, ValidationResult,
    create_project_from_manifest, calculate_project_stats, validate_project_data
)
from .storage import (
    ManifestStore, AsyncManifestStore,
    create_in_memory_store, create_persistent_store, create_async_store,
    migrate_storage_format
)
from .endpoints import ManifestAPIEndpoints
from .server import (
    ManifestAPIServer, start_api_server, create_manifest_api, main
)

__all__ = [
    # Data Models
    'ManifestProject', 'APIResponse', 'ProjectFilter', 'ProjectStats', 'ValidationResult',
    'create_project_from_manifest', 'calculate_project_stats', 'validate_project_data',
    
    # Storage Management
    'ManifestStore', 'AsyncManifestStore',
    'create_in_memory_store', 'create_persistent_store', 'create_async_store',
    'migrate_storage_format',
    
    # API Endpoints
    'ManifestAPIEndpoints',
    
    # Main Server
    'ManifestAPIServer', 'start_api_server', 'create_manifest_api', 'main'
]

# Backward compatibility exports
ManifestAPIServer = ManifestAPIServer
ManifestProject = ManifestProject
ManifestStore = ManifestStore
