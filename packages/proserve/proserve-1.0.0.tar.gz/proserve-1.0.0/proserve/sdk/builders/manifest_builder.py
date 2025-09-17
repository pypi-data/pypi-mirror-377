"""
ProServe Manifest Builder - Main Manifest Configuration Builder
Orchestrates all individual builders to create comprehensive service manifests
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from .endpoint_builder import EndpointBuilder, rest_endpoint, crud_endpoints
from .database_builder import DatabaseBuilder
from .logging_builder import LoggingBuilder
from .grpc_builder import GrpcServiceBuilder
from ...core.manifest import ServiceManifest


@dataclass
class ManifestBuilder:
    """Fluent API builder for ProServe manifests"""
    
    def __init__(self, name: str = None):
        self._manifest = {
            'name': name or 'service',
            'version': '1.0.0',
            'framework': 'proserve',
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        self._endpoints = []
        self._databases = []
        self._grpc_services = []
        self._background_tasks = []
        self._middleware = []
        self._converters = []
        self._shell_commands = []
    
    # Basic service information
    def with_name(self, name: str) -> 'ManifestBuilder':
        """Set service name"""
        self._manifest['name'] = name
        return self
        
    def with_version(self, version: str) -> 'ManifestBuilder':
        """Set service version"""
        self._manifest['version'] = version
        return self
        
    def with_description(self, description: str) -> 'ManifestBuilder':
        """Set service description"""
        self._manifest['description'] = description
        return self
        
    def with_author(self, author: str, email: str = None) -> 'ManifestBuilder':
        """Set author information"""
        author_info = {'name': author}
        if email:
            author_info['email'] = email
        self._manifest['author'] = author_info
        return self
        
    def with_tags(self, *tags: str) -> 'ManifestBuilder':
        """Add service tags"""
        self._manifest['tags'] = list(tags)
        return self
        
    def with_platform(self, platform: str) -> 'ManifestBuilder':
        """Set target platform (python, micropython, arduino, etc.)"""
        self._manifest['platform'] = platform
        return self
    
    # Server configuration
    def with_server(self, host: str = '0.0.0.0', port: int = 8000, 
                   **options) -> 'ManifestBuilder':
        """Configure HTTP server"""
        server_config = {
            'host': host,
            'port': port,
            **options
        }
        self._manifest['server'] = server_config
        return self
        
    def with_grpc_server(self, port: int = 50051, reflection: bool = True,
                        health_check: bool = True, **options) -> 'ManifestBuilder':
        """Configure gRPC server"""
        grpc_config = {
            'port': port,
            'reflection': reflection,
            'health_check': health_check,
            **options
        }
        self._manifest['grpc'] = grpc_config
        return self
    
    # Endpoint management
    def with_endpoint(self, path: str, method: str = 'GET') -> EndpointBuilder:
        """Add HTTP endpoint and return builder for chaining"""
        endpoint_builder = EndpointBuilder(path=path, method=method)
        # We'll add it when build() is called
        return endpoint_builder
        
    def add_endpoint(self, endpoint: Union[EndpointBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built endpoint to manifest"""
        if isinstance(endpoint, EndpointBuilder):
            self._endpoints.append(endpoint.build())
        else:
            self._endpoints.append(endpoint)
        return self
        
    def with_rest_endpoints(self, resource: str, base_path: str = None) -> 'ManifestBuilder':
        """Add full CRUD REST endpoints for a resource"""
        if not base_path:
            base_path = f'/{resource}'
        
        endpoints = crud_endpoints(resource)
        for endpoint in endpoints:
            # Adjust paths to use base_path
            endpoint_config = endpoint.build()
            endpoint_config['path'] = base_path + endpoint_config['path'].replace(f'/{resource}', '')
            self._endpoints.append(endpoint_config)
        
        return self
    
    # Database management
    def with_database(self, db_type: str) -> DatabaseBuilder:
        """Add database configuration and return builder for chaining"""
        return DatabaseBuilder(db_type=db_type)
        
    def add_database(self, database: Union[DatabaseBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built database to manifest"""
        if isinstance(database, DatabaseBuilder):
            self._databases.append(database.build())
        else:
            self._databases.append(database)
        return self
    
    # Logging management
    def with_logging(self, level: str = 'INFO') -> LoggingBuilder:
        """Add logging configuration and return builder for chaining"""
        return LoggingBuilder(level=level)
        
    def add_logging(self, logging_config: Union[LoggingBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built logging to manifest"""
        if isinstance(logging_config, LoggingBuilder):
            self._manifest['logging'] = logging_config.build()
        else:
            self._manifest['logging'] = logging_config
        return self
    
    # gRPC management
    def with_grpc_service(self, name: str) -> GrpcServiceBuilder:
        """Add gRPC service and return builder for chaining"""
        return GrpcServiceBuilder(name=name)
        
    def add_grpc_service(self, service: Union[GrpcServiceBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built gRPC service to manifest"""
        if isinstance(service, GrpcServiceBuilder):
            self._grpc_services.append(service.build())
        else:
            self._grpc_services.append(service)
        return self
    
    # Middleware and features
    def with_middleware(self, *middleware: str) -> 'ManifestBuilder':
        """Add global middleware"""
        self._middleware.extend(middleware)
        return self
        
    def with_cors(self, origins: List[str] = None, methods: List[str] = None,
                 headers: List[str] = None, credentials: bool = False) -> 'ManifestBuilder':
        """Configure CORS"""
        cors_config = {
            'enabled': True,
            'origins': origins or ['*'],
            'methods': methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'headers': headers or ['*'],
            'credentials': credentials
        }
        self._manifest['cors'] = cors_config
        return self
        
    def with_authentication(self, auth_type: str = 'bearer', **config) -> 'ManifestBuilder':
        """Configure global authentication"""
        auth_config = {'type': auth_type, **config}
        self._manifest['authentication'] = auth_config
        return self
        
    def with_rate_limiting(self, requests: int, window: str = '1m', 
                          strategy: str = 'memory') -> 'ManifestBuilder':
        """Configure global rate limiting"""
        rate_limit_config = {
            'requests': requests,
            'window': window,
            'strategy': strategy
        }
        self._manifest['rate_limiting'] = rate_limit_config
        return self
    
    # Monitoring and observability
    def with_health_check(self, endpoint: str = '/health', 
                         checks: List[str] = None) -> 'ManifestBuilder':
        """Configure health checks"""
        health_config = {
            'endpoint': endpoint,
            'checks': checks or ['database', 'memory', 'disk']
        }
        self._manifest['health_check'] = health_config
        return self
        
    def with_metrics(self, endpoint: str = '/metrics', 
                    providers: List[str] = None) -> 'ManifestBuilder':
        """Configure metrics collection"""
        metrics_config = {
            'endpoint': endpoint,
            'providers': providers or ['prometheus']
        }
        self._manifest['metrics'] = metrics_config
        return self
    
    # Background tasks
    def with_background_task(self, name: str, handler: str = None, 
                           script: str = None, interval: str = '1m', 
                           **options) -> 'ManifestBuilder':
        """Add background task"""
        task_config = {
            'name': name,
            'interval': interval,
            **options
        }
        
        if handler:
            task_config['handler'] = handler
        elif script:
            task_config['script'] = script
        else:
            raise ValueError("Either handler or script must be provided")
            
        self._background_tasks.append(task_config)
        return self
    
    # Converters and shell commands
    def with_converter(self, name: str, handler: str, 
                      input_type: str = 'text', output_type: str = 'json') -> 'ManifestBuilder':
        """Add output converter"""
        converter_config = {
            'name': name,
            'handler': handler,
            'input_type': input_type,
            'output_type': output_type
        }
        self._converters.append(converter_config)
        return self
        
    def with_shell_command(self, name: str, command: str, 
                          timeout: int = 30, **options) -> 'ManifestBuilder':
        """Add shell command"""
        shell_config = {
            'name': name,
            'command': command,
            'timeout': timeout,
            **options
        }
        self._shell_commands.append(shell_config)
        return self
    
    # Environment and deployment
    def with_environment(self, **env_vars) -> 'ManifestBuilder':
        """Add environment variables"""
        env_config = []
        for name, value in env_vars.items():
            if isinstance(value, dict):
                env_config.append({'name': name, **value})
            else:
                env_config.append({'name': name, 'default': value})
        
        self._manifest['environment'] = env_config
        return self
        
    def with_deployment(self, target: str = 'docker', **config) -> 'ManifestBuilder':
        """Add deployment configuration"""
        deployment_config = {'target': target, **config}
        self._manifest['deployment'] = deployment_config
        return self
        
    def with_isolation(self, mode: str = 'none', **config) -> 'ManifestBuilder':
        """Configure process isolation"""
        isolation_config = {'mode': mode, **config}
        self._manifest['isolation'] = isolation_config
        return self
        
    def with_static(self, directories: List[Dict] = None, 
                   files: List[Dict] = None) -> 'ManifestBuilder':
        """Configure static file serving"""
        static_config = {}
        if directories:
            static_config['directories'] = directories
        if files:
            static_config['files'] = files
        
        self._manifest['static'] = static_config
        return self
    
    # Build and export methods
    def build(self) -> Dict[str, Any]:
        """Build final manifest dictionary"""
        manifest = self._manifest.copy()
        
        # Add collected components
        if self._endpoints:
            manifest['endpoints'] = self._endpoints
        if self._databases:
            manifest['databases'] = self._databases
        if self._grpc_services:
            manifest['grpc_services'] = self._grpc_services
        if self._background_tasks:
            manifest['background_tasks'] = self._background_tasks
        if self._middleware:
            manifest['middleware'] = self._middleware
        if self._converters:
            manifest['converters'] = self._converters
        if self._shell_commands:
            manifest['shell_commands'] = self._shell_commands
            
        return manifest
        
    def to_manifest(self) -> ServiceManifest:
        """Convert to ServiceManifest instance"""
        return ServiceManifest.from_dict(self.build())
        
    def to_yaml(self, file_path: Union[str, Path] = None) -> str:
        """Export as YAML string or file"""
        manifest_dict = self.build()
        yaml_content = yaml.dump(manifest_dict, default_flow_style=False, indent=2)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(yaml_content)
                
        return yaml_content
        
    def to_json(self, file_path: Union[str, Path] = None, indent: int = 2) -> str:
        """Export as JSON string or file"""
        manifest_dict = self.build()
        json_content = json.dumps(manifest_dict, indent=indent, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_content)
                
        return json_content
        
    def save(self, file_path: Union[str, Path], format: str = 'auto') -> 'ManifestBuilder':
        """Save manifest to file (auto-detect format from extension)"""
        path = Path(file_path)
        
        if format == 'auto':
            format = path.suffix.lower().lstrip('.')
            
        if format in ['yml', 'yaml']:
            self.to_yaml(path)
        elif format == 'json':
            self.to_json(path)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'")
            
        return self
        
    def validate(self) -> List[str]:
        """Validate manifest configuration and return list of errors"""
        from ..validators.manifest_validator import validate_manifest
        return validate_manifest(self.build())


# Convenience functions for common service patterns
def create_http_service(name: str, port: int = 8000) -> ManifestBuilder:
    """Create basic HTTP service"""
    return (ManifestBuilder(name)
            .with_server(port=port)
            .with_cors()
            .with_health_check())


def create_api_service(name: str, port: int = 8000, version: str = 'v1') -> ManifestBuilder:
    """Create REST API service with common patterns"""
    return (ManifestBuilder(name)
            .with_version(version)
            .with_server(port=port)
            .with_cors()
            .with_health_check()
            .with_metrics()
            .with_authentication()
            .with_rate_limiting(requests=100, window='1m'))


def create_grpc_service(name: str, grpc_port: int = 50051, 
                       http_port: int = 8000) -> ManifestBuilder:
    """Create hybrid HTTP + gRPC service"""
    return (ManifestBuilder(name)
            .with_server(port=http_port)
            .with_grpc_server(port=grpc_port)
            .with_cors()
            .with_health_check()
            .with_metrics())


def create_microservice(name: str, database_type: str = 'postgresql',
                       port: int = 8000) -> ManifestBuilder:
    """Create full microservice with database"""
    return (ManifestBuilder(name)
            .with_server(port=port)
            .with_cors()
            .with_health_check()
            .with_metrics()
            .with_authentication()
            .with_rate_limiting(requests=1000, window='1m')
            .add_database(
                DatabaseBuilder(database_type)
                .with_host('localhost')
                .with_database(name)
                .with_pool(size=20)
            ))


def create_worker_service(name: str) -> ManifestBuilder:
    """Create background worker service"""
    return (ManifestBuilder(name)
            .with_health_check()
            .with_metrics()
            .with_logging('INFO')
            .add_logging(
                LoggingBuilder()
                .with_console_handler()
                .with_file_handler(f'{name}.log', rotation='daily')
            ))


def create_static_website(name: str, static_dir: str = './web', 
                         port: int = 8000) -> ManifestBuilder:
    """Create static website service"""
    return (ManifestBuilder(name)
            .with_server(port=port)
            .with_cors()
            .with_static(directories=[{
                'path': static_dir,
                'url_path': '/'
            }]))


# Template-based creation
class ManifestTemplate:
    """Base class for manifest templates"""
    
    @classmethod
    def create(cls, **params) -> ManifestBuilder:
        """Create manifest from template"""
        raise NotImplementedError


class BasicWebServiceTemplate(ManifestTemplate):
    """Template for basic web service"""
    
    @classmethod
    def create(cls, name: str, port: int = 8000, **params) -> ManifestBuilder:
        return create_http_service(name, port)


class RestApiTemplate(ManifestTemplate):
    """Template for REST API service"""
    
    @classmethod
    def create(cls, name: str, version: str = 'v1', port: int = 8000, 
              database: str = None, **params) -> ManifestBuilder:
        builder = create_api_service(name, port, version)
        
        if database:
            db_builder = DatabaseBuilder(database).with_database(name)
            builder.add_database(db_builder)
            
        return builder


class MicroserviceTemplate(ManifestTemplate):
    """Template for full microservice"""
    
    @classmethod
    def create(cls, name: str, database: str = 'postgresql', 
              port: int = 8000, grpc_port: int = None, **params) -> ManifestBuilder:
        
        if grpc_port:
            builder = create_grpc_service(name, grpc_port, port)
        else:
            builder = create_microservice(name, database, port)
            
        return builder


# Registry of templates
TEMPLATES = {
    'web': BasicWebServiceTemplate,
    'api': RestApiTemplate,
    'microservice': MicroserviceTemplate,
}


def from_template(template_name: str, **params) -> ManifestBuilder:
    """Create manifest from predefined template"""
    if template_name not in TEMPLATES:
        available = ', '.join(TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template_name}. Available: {available}")
    
    template_class = TEMPLATES[template_name]
    return template_class.create(**params)


# Example usage
def example_usage():
    """Example usage of the manifest builder SDK"""
    
    # Simple HTTP service
    simple_service = (ManifestBuilder('simple-api')
                     .with_description('A simple API service')
                     .with_author('Developer', 'dev@example.com')
                     .with_server(port=8080)
                     .with_cors()
                     .add_endpoint(
                         EndpointBuilder('/users', 'GET')
                         .with_handler('handlers.users.list_users')
                         .with_auth()
                     ))
    
    # Full microservice
    microservice = (ManifestBuilder('user-service')
                   .with_version('2.0.0')
                   .with_description('User management microservice')
                   .with_server(port=8000)
                   .with_grpc_server(port=50051)
                   .with_cors()
                   .with_authentication('jwt', secret_key='${JWT_SECRET}')
                   .with_rate_limiting(requests=1000, window='1m')
                   .with_health_check()
                   .with_metrics()
                   .add_database(
                       DatabaseBuilder('postgresql')
                       .with_host('localhost')
                       .with_database('users')
                       .with_credentials('user', '${DB_PASSWORD}')
                       .with_pool(size=20)
                       .with_migrations('migrations/')
                   )
                   .add_logging(
                       LoggingBuilder('INFO')
                       .with_console_handler()
                       .with_file_handler('app.log', rotation='daily')
                       .with_elasticsearch_handler(['localhost:9200'], 'user-service-logs')
                   )
                   .with_background_task('user_cleanup', 'tasks.cleanup', interval='1h')
                   .with_environment(
                       JWT_SECRET={'required': True},
                       DB_PASSWORD={'required': True},
                       DEBUG={'default': False}
                   ))
    
    # Save manifests
    simple_service.save('simple-service.yaml')
    microservice.save('user-service.yaml')
    
    print("Manifest examples created!")


if __name__ == '__main__':
    example_usage()
