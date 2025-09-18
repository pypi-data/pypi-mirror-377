"""
ProServe gRPC Builder - gRPC Service Configuration Builder
Fluent API for building gRPC service configurations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class GrpcMethodBuilder:
    """Builder for individual gRPC methods"""
    name: str
    request_type: str
    response_type: str
    stream_request: bool = False
    stream_response: bool = False
    handler: Optional[str] = None
    shell_command: Optional[str] = None
    timeout: Optional[int] = None
    options: Dict[str, Any] = field(default_factory=dict)
    
    def with_streaming(self, request: bool = False, response: bool = False) -> 'GrpcMethodBuilder':
        """Configure streaming for request and/or response"""
        self.stream_request = request
        self.stream_response = response
        return self
        
    def with_handler(self, handler: str) -> 'GrpcMethodBuilder':
        """Set handler function path"""
        self.handler = handler
        return self
        
    def with_shell_command(self, command: str, timeout: int = 30) -> 'GrpcMethodBuilder':
        """Set shell command to execute"""
        self.shell_command = command
        self.timeout = timeout
        return self
        
    def with_timeout(self, seconds: int) -> 'GrpcMethodBuilder':
        """Set method timeout"""
        self.timeout = seconds
        return self
        
    def with_option(self, key: str, value: Any) -> 'GrpcMethodBuilder':
        """Add method option"""
        self.options[key] = value
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build method configuration"""
        config = {
            'name': self.name,
            'request_type': self.request_type,
            'response_type': self.response_type,
            'stream_request': self.stream_request,
            'stream_response': self.stream_response
        }
        
        if self.handler:
            config['handler'] = self.handler
        elif self.shell_command:
            config['shell_command'] = self.shell_command
            
        if self.timeout:
            config['timeout'] = self.timeout
        if self.options:
            config['options'] = self.options
            
        return config


@dataclass
class GrpcServiceBuilder:
    """Builder for gRPC service configuration"""
    name: str
    package: str = ""
    methods: List[GrpcMethodBuilder] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    proto_file: Optional[str] = None
    
    def with_package(self, package: str) -> 'GrpcServiceBuilder':
        """Set package name"""
        self.package = package
        return self
        
    def with_proto_file(self, proto_file: str) -> 'GrpcServiceBuilder':
        """Set proto file path"""
        self.proto_file = proto_file
        return self
        
    def with_method(self, name: str, request_type: str, response_type: str,
                   streaming: str = 'none') -> GrpcMethodBuilder:
        """Add gRPC method and return builder for chaining"""
        stream_request = streaming in ['request', 'bidirectional']
        stream_response = streaming in ['response', 'bidirectional']
        
        method_builder = GrpcMethodBuilder(
            name=name,
            request_type=request_type,
            response_type=response_type,
            stream_request=stream_request,
            stream_response=stream_response
        )
        
        self.methods.append(method_builder)
        return method_builder
        
    def add_method(self, method: GrpcMethodBuilder) -> 'GrpcServiceBuilder':
        """Add pre-built method"""
        self.methods.append(method)
        return self
        
    def with_option(self, key: str, value: Any) -> 'GrpcServiceBuilder':
        """Add service option"""
        self.options[key] = value
        return self
        
    def with_reflection(self, enabled: bool = True) -> 'GrpcServiceBuilder':
        """Enable/disable gRPC reflection"""
        self.options['reflection'] = enabled
        return self
        
    def with_health_check(self, enabled: bool = True) -> 'GrpcServiceBuilder':
        """Enable/disable gRPC health check"""
        self.options['health_check'] = enabled
        return self
        
    def with_compression(self, algorithm: str = 'gzip') -> 'GrpcServiceBuilder':
        """Configure compression"""
        self.options['compression'] = algorithm
        return self
        
    def with_max_message_size(self, size: int) -> 'GrpcServiceBuilder':
        """Set maximum message size"""
        self.options['max_message_size'] = size
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build gRPC service configuration"""
        config = {
            'name': self.name,
            'package': self.package,
            'methods': [method.build() for method in self.methods]
        }
        
        if self.proto_file:
            config['proto_file'] = self.proto_file
        if self.options:
            config['options'] = self.options
            
        return config


# Convenience functions for common gRPC patterns
def unary_method(name: str, request_type: str, response_type: str) -> GrpcMethodBuilder:
    """Create unary gRPC method (request -> response)"""
    return GrpcMethodBuilder(
        name=name,
        request_type=request_type,
        response_type=response_type,
        stream_request=False,
        stream_response=False
    )


def server_streaming_method(name: str, request_type: str, response_type: str) -> GrpcMethodBuilder:
    """Create server streaming method (request -> stream of responses)"""
    return GrpcMethodBuilder(
        name=name,
        request_type=request_type,
        response_type=response_type,
        stream_request=False,
        stream_response=True
    )


def client_streaming_method(name: str, request_type: str, response_type: str) -> GrpcMethodBuilder:
    """Create client streaming method (stream of requests -> response)"""
    return GrpcMethodBuilder(
        name=name,
        request_type=request_type,
        response_type=response_type,
        stream_request=True,
        stream_response=False
    )


def bidirectional_streaming_method(name: str, request_type: str, response_type: str) -> GrpcMethodBuilder:
    """Create bidirectional streaming method (stream of requests -> stream of responses)"""
    return GrpcMethodBuilder(
        name=name,
        request_type=request_type,
        response_type=response_type,
        stream_request=True,
        stream_response=True
    )


def grpc_service(name: str, package: str = "") -> GrpcServiceBuilder:
    """Create gRPC service builder"""
    return GrpcServiceBuilder(name=name, package=package)


def crud_grpc_service(service_name: str, entity_type: str, package: str = "") -> GrpcServiceBuilder:
    """Create CRUD gRPC service with common methods"""
    service = GrpcServiceBuilder(name=service_name, package=package)
    
    # Add standard CRUD methods
    service.with_method(f'Create{entity_type}', f'Create{entity_type}Request', f'{entity_type}')
    service.with_method(f'Get{entity_type}', f'Get{entity_type}Request', f'{entity_type}')
    service.with_method(f'Update{entity_type}', f'Update{entity_type}Request', f'{entity_type}')
    service.with_method(f'Delete{entity_type}', f'Delete{entity_type}Request', 'google.protobuf.Empty')
    service.with_method(f'List{entity_type}s', f'List{entity_type}sRequest', f'List{entity_type}sResponse')
    
    return service


# Proto file generation helpers
def generate_proto_message(name: str, fields: Dict[str, str]) -> str:
    """Generate proto message definition"""
    lines = [f'message {name} {{']
    
    for i, (field_name, field_type) in enumerate(fields.items(), 1):
        lines.append(f'  {field_type} {field_name} = {i};')
    
    lines.append('}')
    return '\n'.join(lines)


def generate_proto_service(service: GrpcServiceBuilder) -> str:
    """Generate proto service definition from builder"""
    lines = [f'service {service.name} {{']
    
    for method in service.methods:
        method_config = method.build()
        
        request_stream = 'stream ' if method_config['stream_request'] else ''
        response_stream = 'stream ' if method_config['stream_response'] else ''
        
        line = f'  rpc {method_config["name"]}({request_stream}{method_config["request_type"]}) returns ({response_stream}{method_config["response_type"]});'
        lines.append(line)
    
    lines.append('}')
    return '\n'.join(lines)


def generate_full_proto_file(package: str, services: List[GrpcServiceBuilder],
                           messages: Dict[str, Dict[str, str]] = None) -> str:
    """Generate complete proto file"""
    lines = [
        'syntax = "proto3";',
        '',
        f'package {package};',
        '',
        'import "google/protobuf/empty.proto";',
        ''
    ]
    
    # Add message definitions
    if messages:
        for message_name, fields in messages.items():
            lines.append(generate_proto_message(message_name, fields))
            lines.append('')
    
    # Add service definitions
    for service in services:
        lines.append(generate_proto_service(service))
        lines.append('')
    
    return '\n'.join(lines)


# Validation
def validate_grpc_config(config: Dict[str, Any]) -> List[str]:
    """Validate gRPC configuration and return list of errors"""
    errors = []
    
    if 'name' not in config:
        errors.append("Service name is required")
    
    methods = config.get('methods', [])
    if not methods:
        errors.append("At least one method is required")
    
    method_names = set()
    for i, method in enumerate(methods):
        # Check required fields
        required_fields = ['name', 'request_type', 'response_type']
        for field in required_fields:
            if field not in method:
                errors.append(f"Method {i}: {field} is required")
        
        # Check for duplicate method names
        method_name = method.get('name')
        if method_name in method_names:
            errors.append(f"Duplicate method name: {method_name}")
        method_names.add(method_name)
        
        # Validate method name (should be PascalCase)
        if method_name and not method_name[0].isupper():
            errors.append(f"Method {method_name}: name should be PascalCase")
    
    return errors
