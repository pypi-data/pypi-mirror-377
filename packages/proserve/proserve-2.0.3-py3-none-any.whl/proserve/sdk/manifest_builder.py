"""
ProServe Manifest Builder - Simplified and Modular
New streamlined manifest builder that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular builder system.
The heavy lifting is done by the builders/ package modules:
- builders/manifest_builder.py - Main manifest building
- builders/endpoint_builder.py - Endpoint configuration
- builders/database_builder.py - Database setup
- builders/grpc_builder.py - gRPC service setup
- builders/logging_builder.py - Logging configuration

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular builders
from .builders import (
    ManifestBuilder,
    EndpointBuilder,
    DatabaseBuilder,
    GrpcServiceBuilder,
    LoggingBuilder,
    ValidationManager,
    ManifestTemplate,
    BasicWebServiceTemplate,
    RestApiTemplate,
    MicroserviceTemplate,
    TEMPLATES,
    from_template,
    create_http_service,
    create_api_service,
    create_grpc_service,
    create_microservice,
    create_worker_service,
    create_static_website
)

# Legacy compatibility - expose the main classes
__all__ = [
    'ManifestBuilder',
    'EndpointBuilder', 
    'DatabaseBuilder',
    'GrpcServiceBuilder',
    'LoggingBuilder',
    'ValidationManager',
    
    # Templates and Template Functions
    'ManifestTemplate',
    'BasicWebServiceTemplate',
    'RestApiTemplate', 
    'MicroserviceTemplate',
    'TEMPLATES',
    'from_template',
    
    # Service Creation Functions
    'create_http_service',
    'create_api_service',
    'create_grpc_service',
    'create_microservice',
    'create_worker_service',
    'create_static_website'
]
