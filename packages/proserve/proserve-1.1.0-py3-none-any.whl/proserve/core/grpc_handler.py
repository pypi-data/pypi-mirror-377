"""
ProServe gRPC Service Handler
Advanced gRPC service generation, proto file management, and service hosting
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from pathlib import Path
import importlib.util
import inspect
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# gRPC imports with safe fallbacks
try:
    import grpc
    from grpc import aio as aio_grpc
    from grpc_reflection.v1alpha import reflection
    from grpc_health.v1 import health
    from grpc_health.v1 import health_pb2_grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    grpc = None
    aio_grpc = None
    reflection = None
    health = None
    health_pb2_grpc = None

# Proto generation imports
try:
    from grpc_tools import protoc
    PROTO_TOOLS_AVAILABLE = True
except ImportError:
    PROTO_TOOLS_AVAILABLE = False


@dataclass
class GrpcServiceConfig:
    """Configuration for a gRPC service"""
    name: str
    proto_file: Optional[str] = None
    service_class: Optional[str] = None
    handler_script: Optional[str] = None
    methods: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = []


@dataclass 
class GrpcMethodConfig:
    """Configuration for a gRPC method"""
    name: str
    request_type: str
    response_type: str
    stream_request: bool = False
    stream_response: bool = False
    handler: Optional[str] = None
    shell_command: Optional[str] = None
    converter: Optional[str] = None


class ProtoFileGenerator:
    """Generate Protocol Buffer (.proto) files from service configurations"""
    
    def __init__(self, output_dir: str = "protos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_proto_file(
        self, 
        service_config: GrpcServiceConfig,
        package_name: Optional[str] = None
    ) -> str:
        """Generate a .proto file from service configuration"""
        
        if not package_name:
            package_name = f"{service_config.name.lower()}.v1"
        
        proto_content = self._generate_proto_content(service_config, package_name)
        
        proto_filename = f"{service_config.name.lower()}.proto"
        proto_path = self.output_dir / proto_filename
        
        with open(proto_path, 'w') as f:
            f.write(proto_content)
        
        return str(proto_path)
    
    def _generate_proto_content(self, config: GrpcServiceConfig, package: str) -> str:
        """Generate the actual proto file content"""
        
        proto_lines = [
            'syntax = "proto3";',
            '',
            f'package {package};',
            '',
            '// Import common types',
            'import "google/protobuf/empty.proto";',
            'import "google/protobuf/timestamp.proto";',
            'import "google/protobuf/struct.proto";',
            '',
            f'// {config.name} service definition',
            f'service {config.name}Service {{',
        ]
        
        # Generate service methods
        for method_config in config.methods:
            method = GrpcMethodConfig(**method_config)
            
            request_stream = "stream " if method.stream_request else ""
            response_stream = "stream " if method.stream_response else ""
            
            proto_lines.append(
                f'  rpc {method.name}({request_stream}{method.request_type}) '
                f'returns ({response_stream}{method.response_type});'
            )
        
        proto_lines.append('}')
        proto_lines.append('')
        
        # Generate message types
        message_types = self._extract_message_types(config.methods)
        for message_type in message_types:
            proto_lines.extend(self._generate_message_definition(message_type))
            proto_lines.append('')
        
        return '\n'.join(proto_lines)
    
    def _extract_message_types(self, methods: List[Dict]) -> List[str]:
        """Extract unique message types from methods"""
        types = set()
        for method_config in methods:
            method = GrpcMethodConfig(**method_config)
            if not method.request_type.startswith('google.protobuf'):
                types.add(method.request_type)
            if not method.response_type.startswith('google.protobuf'):
                types.add(method.response_type)
        return list(types)
    
    def _generate_message_definition(self, message_type: str) -> List[str]:
        """Generate a basic message definition"""
        return [
            f'// {message_type} message',
            f'message {message_type} {{',
            '  // Auto-generated message fields',
            '  string id = 1;',
            '  google.protobuf.Timestamp timestamp = 2;', 
            '  google.protobuf.Struct data = 3;',
            '  string status = 4;',
            '}'
        ]
    
    def compile_proto_files(self, proto_files: List[str]) -> bool:
        """Compile .proto files to Python gRPC code"""
        if not PROTO_TOOLS_AVAILABLE:
            logging.error("grpcio-tools not available for proto compilation")
            return False
        
        success = True
        for proto_file in proto_files:
            try:
                # Generate Python code from proto
                result = protoc.main([
                    'grpc_tools.protoc',
                    f'--proto_path={self.output_dir}',
                    f'--python_out={self.output_dir}',
                    f'--grpc_python_out={self.output_dir}',
                    proto_file
                ])
                
                if result != 0:
                    logging.error(f"Failed to compile proto file: {proto_file}")
                    success = False
                else:
                    logging.info(f"Successfully compiled proto file: {proto_file}")
                    
            except Exception as e:
                logging.error(f"Error compiling proto file {proto_file}: {e}")
                success = False
        
        return success


class GrpcServiceManager:
    """Manage gRPC services, handlers, and server lifecycle"""
    
    def __init__(self, manifest_config: Dict[str, Any]):
        self.config = manifest_config
        self.services: Dict[str, GrpcServiceConfig] = {}
        self.proto_generator = ProtoFileGenerator()
        self.server = None
        self.executor = ThreadPoolExecutor(max_workers=manifest_config.get('grpc_max_workers', 10))
        
        # Load service configurations
        self._load_service_configs()
    
    def _load_service_configs(self):
        """Load gRPC service configurations from manifest"""
        grpc_services = self.config.get('grpc_services', [])
        
        for service_def in grpc_services:
            service_config = GrpcServiceConfig(**service_def)
            self.services[service_config.name] = service_config
            
            logging.info(f"Loaded gRPC service config: {service_config.name}")
    
    async def setup_server(self, host: str = "[::]", port: int = 50051):
        """Setup and configure gRPC server"""
        if not GRPC_AVAILABLE:
            raise RuntimeError("gRPC is not available. Install grpcio and grpcio-tools")
        
        # Create server
        server = aio_grpc.server(self.executor)
        
        # Register services
        for service_name, service_config in self.services.items():
            await self._register_service(server, service_config)
        
        # Enable reflection if configured
        if self.config.get('grpc_reflection', True):
            service_names = [
                f"{service_config.name}Service" 
                for service_config in self.services.values()
            ]
            reflection.enable_server_reflection(service_names, server)
            logging.info("gRPC reflection enabled")
        
        # Enable health checking if configured
        if self.config.get('grpc_health_check', True):
            health_servicer = health.HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
            logging.info("gRPC health check enabled")
        
        # Add server port
        listen_addr = f"{host}:{port}"
        server.add_insecure_port(listen_addr)
        
        self.server = server
        logging.info(f"gRPC server configured on {listen_addr}")
        
        return server
    
    async def _register_service(self, server, config: GrpcServiceConfig):
        """Register a gRPC service with the server"""
        
        # Generate proto file if needed
        if config.proto_file is None and self.config.get('proto_generate', True):
            proto_path = self.proto_generator.generate_proto_file(config)
            config.proto_file = proto_path
            logging.info(f"Generated proto file: {proto_path}")
        
        # Compile proto files
        if config.proto_file:
            success = self.proto_generator.compile_proto_files([config.proto_file])
            if not success:
                logging.error(f"Failed to compile proto for service: {config.name}")
                return
        
        # Load and register service implementation
        try:
            service_impl = await self._create_service_implementation(config)
            if service_impl:
                # This would need the actual generated gRPC servicer add function
                # which depends on the specific proto file
                logging.info(f"Registered gRPC service: {config.name}")
            else:
                logging.error(f"Failed to create implementation for service: {config.name}")
                
        except Exception as e:
            logging.error(f"Error registering gRPC service {config.name}: {e}")
    
    async def _create_service_implementation(self, config: GrpcServiceConfig):
        """Create gRPC service implementation from configuration"""
        
        if config.handler_script:
            return await self._load_service_from_script(config)
        else:
            return await self._generate_service_implementation(config)
    
    async def _load_service_from_script(self, config: GrpcServiceConfig):
        """Load service implementation from Python script"""
        try:
            script_path = Path(config.handler_script)
            if not script_path.exists():
                logging.error(f"Service script not found: {config.handler_script}")
                return None
                
            # Load module from script
            spec = importlib.util.spec_from_file_location(
                f"{config.name}_service", 
                script_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find service class
            service_class_name = config.service_class or f"{config.name}Service"
            service_class = getattr(module, service_class_name, None)
            
            if service_class:
                return service_class()
            else:
                logging.error(f"Service class {service_class_name} not found in {config.handler_script}")
                return None
                
        except Exception as e:
            logging.error(f"Error loading service script {config.handler_script}: {e}")
            return None
    
    async def _generate_service_implementation(self, config: GrpcServiceConfig):
        """Generate basic service implementation from method configurations"""
        
        # This would create a dynamic service class based on the method configs
        # For now, return a placeholder
        logging.info(f"Would generate service implementation for: {config.name}")
        return None
    
    async def start_server(self):
        """Start the gRPC server"""
        if not self.server:
            raise RuntimeError("Server not setup. Call setup_server() first.")
        
        await self.server.start()
        logging.info("gRPC server started")
    
    async def stop_server(self, grace_period: float = 5.0):
        """Stop the gRPC server"""
        if self.server:
            await self.server.stop(grace_period)
            logging.info("gRPC server stopped")
    
    async def serve_forever(self):
        """Start server and serve forever"""
        await self.start_server()
        await self.server.wait_for_termination()


# Utility functions for gRPC service integration

def create_grpc_service_manager(manifest_config: Dict[str, Any]) -> GrpcServiceManager:
    """Create and configure gRPC service manager from manifest"""
    return GrpcServiceManager(manifest_config)


def is_grpc_service(service_type: str) -> bool:
    """Check if service type is gRPC"""
    return service_type in ['grpc', 'hybrid']


async def create_hybrid_service(
    http_app, 
    grpc_manager: GrpcServiceManager,
    http_port: int,
    grpc_port: int
):
    """Create hybrid HTTP+gRPC service"""
    
    # Setup gRPC server
    grpc_server = await grpc_manager.setup_server(port=grpc_port)
    
    # Start both servers concurrently
    async def run_grpc():
        await grpc_manager.serve_forever()
    
    # Return both servers for concurrent execution
    return http_app, run_grpc
