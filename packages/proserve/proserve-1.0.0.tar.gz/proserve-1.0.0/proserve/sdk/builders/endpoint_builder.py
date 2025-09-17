"""
ProServe Endpoint Builder - HTTP Endpoint Configuration Builder
Fluent API for building HTTP endpoint configurations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class EndpointBuilder:
    """Builder for HTTP endpoints with fluent API"""
    path: str
    method: str = 'GET'
    handler: Optional[str] = None
    script: Optional[str] = None
    shell_command: Optional[str] = None
    middleware: List[str] = field(default_factory=list)
    authentication: Optional[Dict[str, Any]] = None
    rate_limit: Optional[Dict[str, Any]] = None
    cache: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    retry: Optional[Dict[str, Any]] = None
    cors: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    
    def with_method(self, method: str) -> 'EndpointBuilder':
        """Set HTTP method"""
        self.method = method.upper()
        return self
        
    def with_handler(self, handler: str) -> 'EndpointBuilder':
        """Set handler function path"""
        self.handler = handler
        return self
        
    def with_script(self, script: str) -> 'EndpointBuilder':
        """Set Python script path"""
        self.script = script
        return self
        
    def with_shell_command(self, command: str, timeout: int = 30) -> 'EndpointBuilder':
        """Set shell command to execute"""
        self.shell_command = command
        self.timeout = timeout
        return self
        
    def with_middleware(self, *middleware: str) -> 'EndpointBuilder':
        """Add middleware functions"""
        self.middleware.extend(middleware)
        return self
        
    def with_auth(self, auth_type: str = 'bearer', **config) -> 'EndpointBuilder':
        """Add authentication configuration"""
        self.authentication = {'type': auth_type, **config}
        return self
        
    def with_rate_limit(self, requests: int, window: str = '1m', 
                       strategy: str = 'memory') -> 'EndpointBuilder':
        """Add rate limiting configuration"""
        self.rate_limit = {
            'requests': requests,
            'window': window,
            'strategy': strategy
        }
        return self
        
    def with_cache(self, ttl: int = 300, strategy: str = 'memory',
                  vary_on: List[str] = None) -> 'EndpointBuilder':
        """Add caching configuration"""
        self.cache = {
            'ttl': ttl,
            'strategy': strategy,
            'vary_on': vary_on or []
        }
        return self
        
    def with_validation(self, schema: Dict[str, Any] = None,
                       validator: str = None) -> 'EndpointBuilder':
        """Add request validation"""
        self.validation = {}
        if schema:
            self.validation['schema'] = schema
        if validator:
            self.validation['validator'] = validator
        return self
        
    def with_timeout(self, seconds: int) -> 'EndpointBuilder':
        """Set request timeout"""
        self.timeout = seconds
        return self
        
    def with_retry(self, count: int = 3, delay: float = 1.0,
                  backoff: str = 'exponential') -> 'EndpointBuilder':
        """Add retry configuration"""
        self.retry = {
            'count': count,
            'delay': delay,
            'backoff': backoff
        }
        return self
        
    def with_cors(self, origins: List[str] = None, methods: List[str] = None,
                 headers: List[str] = None, credentials: bool = False) -> 'EndpointBuilder':
        """Add CORS configuration"""
        self.cors = {
            'origins': origins or ['*'],
            'methods': methods or ['GET', 'POST', 'PUT', 'DELETE'],
            'headers': headers or ['*'],
            'credentials': credentials
        }
        return self
        
    def with_header(self, name: str, value: str) -> 'EndpointBuilder':
        """Add custom response header"""
        self.headers[name] = value
        return self
        
    def with_query_param(self, name: str, required: bool = False,
                        default: Any = None, description: str = None) -> 'EndpointBuilder':
        """Add query parameter specification"""
        self.query_params[name] = {
            'required': required,
            'default': default,
            'description': description
        }
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build endpoint configuration dictionary"""
        config = {
            'path': self.path,
            'method': self.method
        }
        
        # Add handler information
        if self.handler:
            config['handler'] = self.handler
        elif self.script:
            config['script'] = self.script
        elif self.shell_command:
            config['shell_command'] = self.shell_command
            
        # Add optional configurations
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
        if self.cors:
            config['cors'] = self.cors
        if self.headers:
            config['headers'] = self.headers
        if self.query_params:
            config['query_params'] = self.query_params
            
        return config


# Convenience methods for common HTTP methods
def get_endpoint(path: str) -> EndpointBuilder:
    """Create GET endpoint builder"""
    return EndpointBuilder(path=path, method='GET')


def post_endpoint(path: str) -> EndpointBuilder:
    """Create POST endpoint builder"""
    return EndpointBuilder(path=path, method='POST')


def put_endpoint(path: str) -> EndpointBuilder:
    """Create PUT endpoint builder"""
    return EndpointBuilder(path=path, method='PUT')


def delete_endpoint(path: str) -> EndpointBuilder:
    """Create DELETE endpoint builder"""
    return EndpointBuilder(path=path, method='DELETE')


def patch_endpoint(path: str) -> EndpointBuilder:
    """Create PATCH endpoint builder"""
    return EndpointBuilder(path=path, method='PATCH')


# REST endpoint patterns
def rest_endpoint(resource: str, action: str = 'list') -> EndpointBuilder:
    """Create REST endpoint with common patterns"""
    patterns = {
        'list': ('GET', f'/{resource}'),
        'create': ('POST', f'/{resource}'),
        'get': ('GET', f'/{resource}/{{id}}'),
        'update': ('PUT', f'/{resource}/{{id}}'),
        'patch': ('PATCH', f'/{resource}/{{id}}'),
        'delete': ('DELETE', f'/{resource}/{{id}}')
    }
    
    if action not in patterns:
        raise ValueError(f"Unknown REST action: {action}. Available: {list(patterns.keys())}")
    
    method, path = patterns[action]
    return EndpointBuilder(path=path, method=method)


def crud_endpoints(resource: str) -> List[EndpointBuilder]:
    """Create full CRUD endpoint set for a resource"""
    return [
        rest_endpoint(resource, 'list'),
        rest_endpoint(resource, 'create'),
        rest_endpoint(resource, 'get'),
        rest_endpoint(resource, 'update'),
        rest_endpoint(resource, 'delete')
    ]
