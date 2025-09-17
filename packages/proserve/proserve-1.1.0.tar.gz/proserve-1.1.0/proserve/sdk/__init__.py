"""
ProServe SDK Package
Python SDK and API tools for programmatic manifest creation
Alternative to YAML-based configuration
"""

from .manifest_builder import (
    ManifestBuilder,
    EndpointBuilder,
    DatabaseBuilder,
    LoggingBuilder,
    GrpcServiceBuilder,
    ManifestTemplate,
    BasicWebServiceTemplate,
    RestApiTemplate,
    MicroserviceTemplate,
    create_http_service,
    create_api_service,
    create_grpc_service,
    create_microservice,
    from_template,
    TEMPLATES
)

from .api_server import (
    ManifestAPIServer,
    start_api_server,
    create_manifest_api
)

__all__ = [
    # Builders
    'ManifestBuilder',
    'EndpointBuilder',
    'DatabaseBuilder',
    'LoggingBuilder',
    'GrpcServiceBuilder',
    
    # Templates
    'ManifestTemplate',
    'BasicWebServiceTemplate',
    'RestApiTemplate',
    'MicroserviceTemplate',
    'TEMPLATES',
    
    # Convenience functions
    'create_http_service',
    'create_api_service',
    'create_grpc_service',
    'create_microservice',
    'from_template',
    
    # API Server
    'ManifestAPIServer',
    'start_api_server',
    'create_manifest_api'
]
