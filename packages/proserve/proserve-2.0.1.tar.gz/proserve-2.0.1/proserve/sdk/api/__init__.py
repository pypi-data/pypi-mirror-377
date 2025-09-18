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
    'ManifestAPIServer', 'start_api_server', 'create_manifest_api', 'main',
    
    # Backward Compatibility Aliases
    'APIModel', 'EndpointModel', 'ManifestModel', 'ServiceModel', 'ManifestStorage', 'FileStorage', 'MemoryStorage', 'APIEndpoints', 'ManifestEndpoints', 'ServiceEndpoints', 'APIServer', 'create_api_server'
]

# Backward compatibility exports
ManifestAPIServer = ManifestAPIServer
ManifestProject = ManifestProject
ManifestStore = ManifestStore
APIModel = ManifestProject  # Alias for backward compatibility
EndpointModel = ManifestProject  # Alias for backward compatibility
ManifestModel = ManifestProject  # Alias for backward compatibility
ServiceModel = ManifestProject  # Alias for backward compatibility
ManifestStorage = ManifestStore  # Alias for backward compatibility
FileStorage = ManifestStore  # Alias for backward compatibility
MemoryStorage = ManifestStore  # Alias for backward compatibility
APIEndpoints = ManifestAPIEndpoints  # Alias for backward compatibility
ManifestEndpoints = ManifestAPIEndpoints  # Alias for backward compatibility
ServiceEndpoints = ManifestAPIEndpoints  # Alias for backward compatibility
APIServer = ManifestAPIServer  # Alias for backward compatibility
create_api_server = create_manifest_api  # Alias for backward compatibility
