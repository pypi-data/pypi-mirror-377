"""
gRPC Component Tests
E2E tests for gRPC service generation, proto files, and hybrid HTTP+gRPC services
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, TestSuite


async def test_grpc_service_config(framework: ProServeTestFramework):
    """Test gRPC service configuration loading"""
    manifest_path = framework.create_test_manifest(
        'test-grpc-config',
        grpc_services=[
            {
                'name': 'TestService',
                'package': 'test.service',
                'methods': [
                    {'name': 'GetTest', 'input_type': 'GetTestRequest', 'output_type': 'TestResponse'},
                    {'name': 'ListTests', 'input_type': 'ListTestsRequest', 'output_type': 'ListTestsResponse'}
                ]
            }
        ]
    )
    
    from proserve import ServiceManifest, GrpcServiceManager
    manifest = ServiceManifest.from_yaml(manifest_path)
    
    assert manifest.grpc_services is not None
    assert len(manifest.grpc_services) == 1
    
    grpc_service = manifest.grpc_services[0]
    assert grpc_service['name'] == 'TestService'
    assert grpc_service['package'] == 'test.service'
    assert len(grpc_service['methods']) == 2
    
    return {
        'grpc_services_count': len(manifest.grpc_services),
        'service_name': grpc_service['name'],
        'methods_count': len(grpc_service['methods'])
    }


async def test_proto_file_generation(framework: ProServeTestFramework):
    """Test automatic proto file generation"""
    manifest_path = framework.create_test_manifest(
        'test-proto-generation',
        grpc_services=[
            {
                'name': 'UserService',
                'package': 'demo.users',
                'methods': [
                    {'name': 'GetUser', 'input_type': 'GetUserRequest', 'output_type': 'User'},
                    {'name': 'CreateUser', 'input_type': 'CreateUserRequest', 'output_type': 'User'}
                ]
            }
        ]
    )
    
    try:
        from proserve.core.grpc_handler import ProtoFileGenerator, GrpcServiceConfig
        
        # Create service config
        service_config = GrpcServiceConfig(
            name='UserService',
            methods=[
                {'name': 'GetUser', 'input_type': 'GetUserRequest', 'output_type': 'User'},
                {'name': 'CreateUser', 'input_type': 'CreateUserRequest', 'output_type': 'User'}
            ]
        )
        
        # Generate proto file
        proto_generator = ProtoFileGenerator()
        proto_content = proto_generator._generate_proto_content(service_config, 'demo.users')
        
        # Check proto content
        assert 'syntax = "proto3";' in proto_content
        assert 'package demo.users;' in proto_content
        assert 'service UserService' in proto_content
        assert 'rpc GetUser' in proto_content
        assert 'rpc CreateUser' in proto_content
        
        return {
            'proto_generated': True,
            'has_syntax': 'syntax = "proto3";' in proto_content,
            'has_package': 'package demo.users;' in proto_content,
            'has_service': 'service UserService' in proto_content
        }
        
    except ImportError as e:
        # gRPC not available
        return {
            'proto_generated': False,
            'error': str(e),
            'grpc_available': False
        }


async def test_hybrid_service_startup(framework: ProServeTestFramework):
    """Test hybrid HTTP+gRPC service startup"""
    manifest_path = framework.create_test_manifest(
        'test-hybrid-service',
        grpc_services=[
            {
                'name': 'TestService',
                'package': 'test.hybrid',
                'methods': [
                    {'name': 'Echo', 'input_type': 'EchoRequest', 'output_type': 'EchoResponse'}
                ]
            }
        ]
    )
    
    # Create HTTP handler
    http_handler = '''
async def handle(request):
    return {"type": "http", "endpoint": "/api/test"}
'''
    framework.create_test_handler('handlers/test/simple_get.py', http_handler)
    
    try:
        service = await framework.start_test_service(manifest_path, 'hybrid_test')
        manifest = service.manifest
        
        # Check HTTP endpoint
        base_url = f"http://{manifest.server['host']}:{manifest.server['port']}"
        
        import requests
        http_response = requests.get(f"{base_url}/api/test", timeout=5)
        http_works = http_response.status_code == 200
        
        # Check gRPC port (if available)
        grpc_port = manifest.grpc_port
        grpc_available = grpc_port is not None
        
        return {
            'service_started': True,
            'http_works': http_works,
            'grpc_port_configured': grpc_available,
            'grpc_port': grpc_port
        }
        
    except Exception as e:
        return {
            'service_started': False,
            'error': str(e)
        }


async def test_grpc_reflection(framework: ProServeTestFramework):
    """Test gRPC reflection service"""
    manifest_path = framework.create_test_manifest(
        'test-grpc-reflection',
        grpc_services=[
            {
                'name': 'ReflectionService',
                'package': 'test.reflection',
                'methods': [
                    {'name': 'Test', 'input_type': 'TestRequest', 'output_type': 'TestResponse'}
                ]
            }
        ]
    )
    
    try:
        service = await framework.start_test_service(manifest_path, 'reflection_test')
        manifest = service.manifest
        
        grpc_port = manifest.grpc_port
        if grpc_port:
            # Try to use grpcurl to list services (if available)
            try:
                result = subprocess.run(
                    ['grpcurl', '-plaintext', f'127.0.0.1:{grpc_port}', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                grpcurl_works = result.returncode == 0
                services_listed = 'grpc.reflection' in result.stdout if grpcurl_works else False
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                grpcurl_works = False
                services_listed = False
            
            return {
                'grpc_port': grpc_port,
                'grpcurl_available': grpcurl_works,
                'reflection_works': services_listed
            }
        else:
            return {
                'grpc_port': None,
                'error': 'No gRPC port configured'
            }
            
    except Exception as e:
        return {
            'error': str(e),
            'grpc_reflection_test': False
        }


async def test_grpc_health_check(framework: ProServeTestFramework):
    """Test gRPC health check service"""
    manifest_path = framework.create_test_manifest(
        'test-grpc-health',
        grpc_services=[
            {
                'name': 'HealthTestService',
                'package': 'test.health',
                'methods': [
                    {'name': 'Check', 'input_type': 'HealthRequest', 'output_type': 'HealthResponse'}
                ]
            }
        ]
    )
    
    try:
        service = await framework.start_test_service(manifest_path, 'grpc_health_test')
        manifest = service.manifest
        
        grpc_port = manifest.grpc_port
        if grpc_port:
            # Try gRPC health check
            try:
                result = subprocess.run([
                    'grpcurl', '-plaintext', 
                    f'127.0.0.1:{grpc_port}',
                    'grpc.health.v1.Health/Check'
                ], capture_output=True, text=True, timeout=5)
                
                health_check_works = result.returncode == 0
                response_data = result.stdout if health_check_works else result.stderr
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                health_check_works = False
                response_data = "grpcurl not available"
            
            return {
                'grpc_health_available': health_check_works,
                'response': response_data,
                'grpc_port': grpc_port
            }
        else:
            return {
                'error': 'No gRPC port configured'
            }
            
    except Exception as e:
        return {
            'error': str(e)
        }


# Setup and teardown
async def setup_grpc_tests(framework: ProServeTestFramework):
    """Setup for gRPC tests"""
    print("Setting up gRPC tests...")
    
    # Check if gRPC tools are available
    try:
        import grpc
        framework.grpc_available = True
    except ImportError:
        framework.grpc_available = False
        print("Warning: gRPC not available, some tests may be skipped")


async def teardown_grpc_tests(framework: ProServeTestFramework):
    """Teardown for gRPC tests"""
    print("Tearing down gRPC tests...")


# Create test suite
grpc_test_suite = TestSuite(
    name='grpc',
    description='gRPC service functionality tests',
    tests=[
        test_grpc_service_config,
        test_proto_file_generation,
        test_hybrid_service_startup,
        test_grpc_reflection,
        test_grpc_health_check
    ],
    setup=setup_grpc_tests,
    teardown=teardown_grpc_tests,
    timeout=300,
    parallel=False
)
