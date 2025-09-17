"""
ProServe Manifest Builder SDK
Programmatic manifest creation with fluent API
Alternative to YAML-based configuration
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime

from ..core.manifest import ServiceManifest


@dataclass
class EndpointBuilder:
    """Builder for HTTP endpoints"""
    path: str
    method: str = 'GET'
    handler: Optional[str] = None
    middleware: List[str] = field(default_factory=list)
    authentication: Optional[Dict[str, Any]] = None
    rate_limit: Optional[Dict[str, Any]] = None
    cache: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    retry: Optional[Dict[str, Any]] = None
    
    def with_method(self, method: str) -> 'EndpointBuilder':
        """Set HTTP method"""
        self.method = method.upper()
        return self
        
    def with_handler(self, handler: str) -> 'EndpointBuilder':
        """Set handler function path"""
        self.handler = handler
        return self
        
    def with_middleware(self, *middleware: str) -> 'EndpointBuilder':
        """Add middleware functions"""
        self.middleware.extend(middleware)
        return self
        
    def with_auth(self, auth_type: str = 'bearer', **config) -> 'EndpointBuilder':
        """Add authentication"""
        self.authentication = {'type': auth_type, **config}
        return self
        
    def with_rate_limit(self, requests: int, window: str = '1m') -> 'EndpointBuilder':
        """Add rate limiting"""
        self.rate_limit = {'requests': requests, 'window': window}
        return self
        
    def with_cache(self, ttl: int = 300, strategy: str = 'memory') -> 'EndpointBuilder':
        """Add caching"""
        self.cache = {'ttl': ttl, 'strategy': strategy}
        return self
        
    def with_validation(self, schema: Dict[str, Any]) -> 'EndpointBuilder':
        """Add request validation"""
        self.validation = schema
        return self
        
    def with_timeout(self, timeout: int) -> 'EndpointBuilder':
        """Set request timeout"""
        self.timeout = timeout
        return self
        
    def with_retry(self, attempts: int = 3, backoff: str = 'exponential') -> 'EndpointBuilder':
        """Add retry configuration"""
        self.retry = {'attempts': attempts, 'backoff': backoff}
        return self

    def build(self) -> Dict[str, Any]:
        """Build endpoint configuration"""
        config = {
            'path': self.path,
            'method': self.method.lower()
        }
        
        if self.handler:
            config['handler'] = self.handler
        if self.middleware:
            config['middleware'] = self.middleware
        if self.authentication:
            config['authentication'] = self.authentication
        if self.rate_limit:
            config['rate_limit'] = self.rate_limit
        if self.cache:
            config['cache'] = self.cache
        if self.validation:
            config['validation'] = self.validation
        if self.timeout:
            config['timeout'] = self.timeout
        if self.retry:
            config['retry'] = self.retry
            
        return config


@dataclass  
class DatabaseBuilder:
    """Builder for database configuration"""
    db_type: str
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 10
    pool_timeout: int = 30
    migrations: List[str] = field(default_factory=list)
    ssl: bool = False
    options: Dict[str, Any] = field(default_factory=dict)
    
    def with_url(self, url: str) -> 'DatabaseBuilder':
        """Set database URL"""
        self.url = url
        return self
        
    def with_host(self, host: str, port: int) -> 'DatabaseBuilder':
        """Set host and port"""
        self.host = host
        self.port = port
        return self
        
    def with_credentials(self, username: str, password: str) -> 'DatabaseBuilder':
        """Set credentials"""
        self.username = username
        self.password = password
        return self
        
    def with_database(self, database: str) -> 'DatabaseBuilder':
        """Set database name"""
        self.database = database
        return self
        
    def with_pool(self, size: int = 10, timeout: int = 30) -> 'DatabaseBuilder':
        """Configure connection pool"""
        self.pool_size = size
        self.pool_timeout = timeout
        return self
        
    def with_migrations(self, *migrations: str) -> 'DatabaseBuilder':
        """Add migration files"""
        self.migrations.extend(migrations)
        return self
        
    def with_ssl(self, enabled: bool = True) -> 'DatabaseBuilder':
        """Enable SSL"""
        self.ssl = enabled
        return self
        
    def with_option(self, key: str, value: Any) -> 'DatabaseBuilder':
        """Add custom option"""
        self.options[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build database configuration"""
        config = {'type': self.db_type}
        
        if self.url:
            config['url'] = self.url
        else:
            if self.host:
                config['host'] = self.host
            if self.port:
                config['port'] = self.port
            if self.database:
                config['database'] = self.database
            if self.username:
                config['username'] = self.username
            if self.password:
                config['password'] = self.password
                
        config.update({
            'pool_size': self.pool_size,
            'pool_timeout': self.pool_timeout,
            'ssl': self.ssl
        })
        
        if self.migrations:
            config['migrations'] = self.migrations
        if self.options:
            config['options'] = self.options
            
        return config


@dataclass
class LoggingBuilder:
    """Builder for logging configuration"""
    level: str = 'INFO'
    format: str = 'json'
    handlers: List[Dict[str, Any]] = field(default_factory=list)
    loggers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def with_level(self, level: str) -> 'LoggingBuilder':
        """Set log level"""
        self.level = level.upper()
        return self
        
    def with_format(self, format_type: str) -> 'LoggingBuilder':
        """Set log format (json, text, structured)"""
        self.format = format_type
        return self
        
    def with_console_handler(self, level: str = 'INFO', format_str: str = None) -> 'LoggingBuilder':
        """Add console handler"""
        handler = {
            'type': 'console',
            'level': level.upper()
        }
        if format_str:
            handler['format'] = format_str
        self.handlers.append(handler)
        return self
        
    def with_file_handler(self, filename: str, level: str = 'INFO', 
                         rotation: str = None, retention: str = None) -> 'LoggingBuilder':
        """Add file handler with optional rotation"""
        handler = {
            'type': 'file',
            'filename': filename,
            'level': level.upper()
        }
        if rotation:
            handler['rotation'] = rotation
        if retention:
            handler['retention'] = retention
        self.handlers.append(handler)
        return self
        
    def with_syslog_handler(self, address: str = 'localhost', 
                           facility: str = 'user', level: str = 'INFO') -> 'LoggingBuilder':
        """Add syslog handler"""
        handler = {
            'type': 'syslog',
            'address': address,
            'facility': facility,
            'level': level.upper()
        }
        self.handlers.append(handler)
        return self
        
    def with_websocket_handler(self, url: str, level: str = 'DEBUG') -> 'LoggingBuilder':
        """Add websocket handler for live logging"""
        handler = {
            'type': 'websocket',
            'url': url,
            'level': level.upper()
        }
        self.handlers.append(handler)
        return self
        
    def with_logger(self, name: str, level: str = 'INFO', **options) -> 'LoggingBuilder':
        """Add custom logger configuration"""
        self.loggers[name] = {
            'level': level.upper(),
            **options
        }
        return self

    def build(self) -> Dict[str, Any]:
        """Build logging configuration"""
        config = {
            'level': self.level,
            'format': self.format
        }
        
        if self.handlers:
            config['handlers'] = self.handlers
        if self.loggers:
            config['loggers'] = self.loggers
            
        return config


@dataclass
class GrpcServiceBuilder:
    """Builder for gRPC service configuration"""
    name: str
    package: str = ""
    methods: List[Dict[str, Any]] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    
    def with_package(self, package: str) -> 'GrpcServiceBuilder':
        """Set package name"""
        self.package = package
        return self
        
    def with_method(self, name: str, request_type: str, response_type: str,
                   streaming: str = 'none') -> 'GrpcServiceBuilder':
        """Add gRPC method"""
        method = {
            'name': name,
            'request_type': request_type,
            'response_type': response_type,
            'streaming': streaming
        }
        self.methods.append(method)
        return self
        
    def with_option(self, key: str, value: Any) -> 'GrpcServiceBuilder':
        """Add service option"""
        self.options[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build gRPC service configuration"""
        config = {
            'name': self.name,
            'methods': self.methods
        }
        
        if self.package:
            config['package'] = self.package
        if self.options:
            config['options'] = self.options
            
        return config


class ManifestBuilder:
    """Fluent API builder for ProServe manifests"""
    
    def __init__(self, name: str = None):
        self._manifest = {
            'name': name or 'service',
            'version': '1.0.0',
            'framework': 'proserve'
        }
        
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
        self._manifest['author'] = author
        if email:
            self._manifest['author_email'] = email
        return self
        
    def with_tags(self, *tags: str) -> 'ManifestBuilder':
        """Add service tags"""
        self._manifest['tags'] = list(tags)
        return self
        
    def with_server(self, host: str = '0.0.0.0', port: int = 8000, 
                   **options) -> 'ManifestBuilder':
        """Configure HTTP server"""
        self._manifest['server'] = {
            'host': host,
            'port': port,
            **options
        }
        return self
        
    def with_grpc_server(self, port: int = 50051, reflection: bool = True,
                        health_check: bool = True, **options) -> 'ManifestBuilder':
        """Configure gRPC server"""
        grpc_config = {
            'grpc_port': port,
            'grpc_reflection': reflection,
            'grpc_health_check': health_check
        }
        grpc_config.update(options)
        self._manifest.update(grpc_config)
        return self
        
    def with_endpoint(self, path: str, method: str = 'GET') -> EndpointBuilder:
        """Add HTTP endpoint (returns builder for chaining)"""
        return EndpointBuilder(path=path, method=method)
        
    def add_endpoint(self, endpoint: Union[EndpointBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built endpoint to manifest"""
        if 'endpoints' not in self._manifest:
            self._manifest['endpoints'] = []
            
        if isinstance(endpoint, EndpointBuilder):
            self._manifest['endpoints'].append(endpoint.build())
        else:
            self._manifest['endpoints'].append(endpoint)
        return self
        
    def with_database(self, db_type: str) -> DatabaseBuilder:
        """Add database configuration (returns builder for chaining)"""
        return DatabaseBuilder(db_type=db_type)
        
    def add_database(self, database: Union[DatabaseBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built database to manifest"""
        if isinstance(database, DatabaseBuilder):
            self._manifest['database'] = database.build()
        else:
            self._manifest['database'] = database
        return self
        
    def with_logging(self, level: str = 'INFO') -> LoggingBuilder:
        """Add logging configuration (returns builder for chaining)"""
        return LoggingBuilder(level=level)
        
    def add_logging(self, logging: Union[LoggingBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built logging to manifest"""
        if isinstance(logging, LoggingBuilder):
            self._manifest['logging'] = logging.build()
        else:
            self._manifest['logging'] = logging
        return self
        
    def with_grpc_service(self, name: str) -> GrpcServiceBuilder:
        """Add gRPC service (returns builder for chaining)"""
        return GrpcServiceBuilder(name=name)
        
    def add_grpc_service(self, service: Union[GrpcServiceBuilder, Dict[str, Any]]) -> 'ManifestBuilder':
        """Add built gRPC service to manifest"""
        if 'grpc_services' not in self._manifest:
            self._manifest['grpc_services'] = []
            
        if isinstance(service, GrpcServiceBuilder):
            self._manifest['grpc_services'].append(service.build())
        else:
            self._manifest['grpc_services'].append(service)
        return self
        
    def with_middleware(self, *middleware: str) -> 'ManifestBuilder':
        """Add global middleware"""
        self._manifest['middleware'] = list(middleware)
        return self
        
    def with_cors(self, origins: List[str] = None, methods: List[str] = None,
                 headers: List[str] = None, credentials: bool = False) -> 'ManifestBuilder':
        """Configure CORS"""
        cors_config = {'enabled': True}
        if origins:
            cors_config['origins'] = origins
        if methods:
            cors_config['methods'] = methods  
        if headers:
            cors_config['headers'] = headers
        if credentials:
            cors_config['credentials'] = credentials
        self._manifest['cors'] = cors_config
        return self
        
    def with_authentication(self, auth_type: str = 'bearer', **config) -> 'ManifestBuilder':
        """Configure global authentication"""
        self._manifest['authentication'] = {
            'type': auth_type,
            **config
        }
        return self
        
    def with_rate_limiting(self, requests: int, window: str = '1m', 
                          strategy: str = 'memory') -> 'ManifestBuilder':
        """Configure global rate limiting"""
        self._manifest['rate_limiting'] = {
            'requests': requests,
            'window': window,
            'strategy': strategy
        }
        return self
        
    def with_health_check(self, endpoint: str = '/health', 
                         checks: List[str] = None) -> 'ManifestBuilder':
        """Configure health checks"""
        health_config = {'endpoint': endpoint}
        if checks:
            health_config['checks'] = checks
        self._manifest['health'] = health_config
        return self
        
    def with_metrics(self, endpoint: str = '/metrics', 
                    providers: List[str] = None) -> 'ManifestBuilder':
        """Configure metrics collection"""
        metrics_config = {'endpoint': endpoint}
        if providers:
            metrics_config['providers'] = providers
        self._manifest['metrics'] = metrics_config
        return self
        
    def with_background_task(self, name: str, handler: str, 
                           interval: str = '1m', **options) -> 'ManifestBuilder':
        """Add background task"""
        if 'background_tasks' not in self._manifest:
            self._manifest['background_tasks'] = []
            
        task = {
            'name': name,
            'handler': handler,
            'interval': interval,
            **options
        }
        self._manifest['background_tasks'].append(task)
        return self
        
    def with_converter(self, name: str, handler: str, 
                      input_type: str = 'text', output_type: str = 'json') -> 'ManifestBuilder':
        """Add output converter"""
        if 'converters' not in self._manifest:
            self._manifest['converters'] = []
            
        converter = {
            'name': name,
            'handler': handler,
            'input_type': input_type,
            'output_type': output_type
        }
        self._manifest['converters'].append(converter)
        return self
        
    def with_shell_command(self, name: str, command: str, 
                          timeout: int = 30, **options) -> 'ManifestBuilder':
        """Add shell command"""
        if 'shell_commands' not in self._manifest:
            self._manifest['shell_commands'] = {}
            
        self._manifest['shell_commands'][name] = {
            'command': command,
            'timeout': timeout,
            **options
        }
        return self
        
    def with_environment(self, **env_vars) -> 'ManifestBuilder':
        """Add environment variables"""
        if 'environment' not in self._manifest:
            self._manifest['environment'] = {}
        self._manifest['environment'].update(env_vars)
        return self
        
    def with_deployment(self, target: str = 'docker', **config) -> 'ManifestBuilder':
        """Add deployment configuration"""
        self._manifest['deployment'] = {
            'target': target,
            **config
        }
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build final manifest dictionary"""
        return self._manifest.copy()
        
    def to_manifest(self) -> ServiceManifest:
        """Convert to ServiceManifest instance"""
        return ServiceManifest(**self._manifest)
        
    def to_yaml(self, file_path: Union[str, Path] = None) -> str:
        """Export as YAML string or file"""
        yaml_content = yaml.dump(self._manifest, default_flow_style=False, 
                                sort_keys=False, allow_unicode=True)
        
        if file_path:
            Path(file_path).write_text(yaml_content)
            
        return yaml_content
        
    def to_json(self, file_path: Union[str, Path] = None, indent: int = 2) -> str:
        """Export as JSON string or file"""
        json_content = json.dumps(self._manifest, indent=indent, ensure_ascii=False)
        
        if file_path:
            Path(file_path).write_text(json_content)
            
        return json_content
        
    def save(self, file_path: Union[str, Path], format: str = 'auto') -> None:
        """Save manifest to file (auto-detect format from extension)"""
        path = Path(file_path)
        
        if format == 'auto':
            format = path.suffix.lower().lstrip('.')
            
        if format in ['yml', 'yaml']:
            self.to_yaml(path)
        elif format == 'json':
            self.to_json(path)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Convenience functions for common patterns
def create_http_service(name: str, port: int = 8000) -> ManifestBuilder:
    """Create basic HTTP service"""
    return ManifestBuilder(name).with_server(port=port)


def create_api_service(name: str, port: int = 8000, version: str = 'v1') -> ManifestBuilder:
    """Create REST API service with common patterns"""
    builder = (ManifestBuilder(name)
              .with_server(port=port)
              .with_cors(origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE'])
              .with_health_check(f'/api/{version}/health')
              .with_metrics(f'/api/{version}/metrics'))
    
    # Add common API endpoints
    builder.add_endpoint(
        EndpointBuilder(f'/api/{version}/status')
        .with_handler('handlers.status.get_status')
    )
    
    return builder


def create_grpc_service(name: str, grpc_port: int = 50051, 
                       http_port: int = 8000) -> ManifestBuilder:
    """Create hybrid HTTP + gRPC service"""
    return (ManifestBuilder(name)
           .with_server(port=http_port)
           .with_grpc_server(port=grpc_port))


def create_microservice(name: str, database_type: str = 'postgresql',
                       port: int = 8000) -> ManifestBuilder:
    """Create full microservice with database"""
    builder = (create_api_service(name, port)
              .with_authentication('bearer')
              .with_rate_limiting(requests=100, window='1m'))
    
    # Add database
    db = DatabaseBuilder(database_type).with_pool(size=20)
    builder.add_database(db)
    
    # Add structured logging
    logging = (LoggingBuilder()
              .with_console_handler()
              .with_file_handler(f'{name}.log', rotation='1 day', retention='30 days'))
    builder.add_logging(logging)
    
    return builder


# Template system
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
        return (create_http_service(name, port)
               .with_description(f"Basic web service: {name}")
               .with_health_check()
               .with_metrics())


class RestApiTemplate(ManifestTemplate):
    """Template for REST API service"""
    
    @classmethod
    def create(cls, name: str, version: str = 'v1', port: int = 8000, 
              database: str = None, **params) -> ManifestBuilder:
        builder = create_api_service(name, port, version)
        
        if database:
            db = DatabaseBuilder(database).with_pool(size=10)
            builder.add_database(db)
            
        return builder


class MicroserviceTemplate(ManifestTemplate):
    """Template for full microservice"""
    
    @classmethod
    def create(cls, name: str, database: str = 'postgresql', 
              port: int = 8000, grpc_port: int = None, **params) -> ManifestBuilder:
        builder = create_microservice(name, database, port)
        
        if grpc_port:
            builder.with_grpc_server(port=grpc_port)
            
        return builder


# Registry of templates
TEMPLATES = {
    'web': BasicWebServiceTemplate,
    'api': RestApiTemplate,
    'microservice': MicroserviceTemplate
}


def from_template(template_name: str, **params) -> ManifestBuilder:
    """Create manifest from predefined template"""
    if template_name not in TEMPLATES:
        available = ', '.join(TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template_name}. Available: {available}")
    
    return TEMPLATES[template_name].create(**params)


# Usage examples and documentation
def example_usage():
    """Example usage of the manifest builder SDK"""
    
    # Basic HTTP service
    basic = (ManifestBuilder('my-service')
            .with_version('1.0.0')
            .with_description('My awesome service')
            .with_server(host='0.0.0.0', port=8080))
    
    # Add endpoints fluently
    basic.add_endpoint(
        basic.with_endpoint('/api/users', 'GET')
        .with_handler('handlers.users.list_users')
        .with_auth('bearer')
        .with_rate_limit(requests=50, window='1m')
        .with_cache(ttl=300)
    )
    
    # Add database
    basic.add_database(
        basic.with_database('postgresql')
        .with_url('postgresql://localhost:5432/mydb')
        .with_pool(size=20, timeout=30)
        .with_ssl(True)
    )
    
    # Add structured logging
    basic.add_logging(
        basic.with_logging('DEBUG')
        .with_console_handler()
        .with_file_handler('service.log', rotation='1 day')
        .with_websocket_handler('ws://localhost:8081/logs')
    )
    
    # Add gRPC service
    basic.add_grpc_service(
        basic.with_grpc_service('UserService')
        .with_package('myapp.users')
        .with_method('GetUser', 'GetUserRequest', 'User')
        .with_method('ListUsers', 'ListUsersRequest', 'User', streaming='server')
    )
    
    # Generate YAML
    yaml_output = basic.to_yaml()
    print(yaml_output)
    
    # Or use templates
    microservice = from_template('microservice', 
                                name='user-service',
                                database='postgresql',
                                port=8000,
                                grpc_port=50051)
    
    return basic, microservice
