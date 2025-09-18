"""
ProServe SDK Builders - Modular Manifest Building Components
Refactored from monolithic manifest_builder.py into focused, reusable builders
"""

from .endpoint_builder import (
    EndpointBuilder, 
    get_endpoint, post_endpoint, put_endpoint, delete_endpoint, patch_endpoint,
    rest_endpoint, crud_endpoints
)
from .database_builder import (
    DatabaseBuilder,
    postgresql, mysql, sqlite, mongodb, redis, cassandra, elasticsearch,
    postgresql_cluster, mysql_cluster, mongodb_replica_set,
    validate_database_config
)
from .logging_builder import (
    LoggingBuilder,
    console_logging, file_logging, production_logging, development_logging,
    centralized_logging, monitoring_logging,
    validate_logging_config
)
from .grpc_builder import (
    GrpcServiceBuilder, GrpcMethodBuilder,
    unary_method, server_streaming_method, client_streaming_method, bidirectional_streaming_method,
    grpc_service, crud_grpc_service,
    generate_proto_message, generate_proto_service, generate_full_proto_file,
    validate_grpc_config
)
from .manifest_builder import (
    ManifestBuilder,
    create_http_service, create_api_service, create_grpc_service, create_microservice,
    create_worker_service, create_static_website,
    ManifestTemplate, BasicWebServiceTemplate, RestApiTemplate, MicroserviceTemplate,
    TEMPLATES, from_template,
    example_usage
)

__all__ = [
    # Endpoint Builder
    'EndpointBuilder',
    'get_endpoint', 'post_endpoint', 'put_endpoint', 'delete_endpoint', 'patch_endpoint',
    'rest_endpoint', 'crud_endpoints',
    
    # Database Builder
    'DatabaseBuilder',
    'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'cassandra', 'elasticsearch',
    'postgresql_cluster', 'mysql_cluster', 'mongodb_replica_set',
    'validate_database_config',
    
    # Logging Builder
    'LoggingBuilder',
    'console_logging', 'file_logging', 'production_logging', 'development_logging',
    'centralized_logging', 'monitoring_logging',
    'validate_logging_config',
    
    # gRPC Builder
    'GrpcServiceBuilder', 'GrpcMethodBuilder',
    'unary_method', 'server_streaming_method', 'client_streaming_method', 'bidirectional_streaming_method',
    'grpc_service', 'crud_grpc_service',
    'generate_proto_message', 'generate_proto_service', 'generate_full_proto_file',
    'validate_grpc_config',
    
    # Main Manifest Builder
    'ManifestBuilder',
    'create_http_service', 'create_api_service', 'create_grpc_service', 'create_microservice',
    'create_worker_service', 'create_static_website',
    'ManifestTemplate', 'BasicWebServiceTemplate', 'RestApiTemplate', 'MicroserviceTemplate',
    'TEMPLATES', 'from_template',
    'example_usage',
    
    # Backward Compatibility Aliases
    'ValidationManager'  # Alias for backward compatibility
]

# Backward compatibility aliases
ValidationManager = ManifestBuilder  # Simple alias for now
