"""
Core ProServe Component Tests
E2E tests for manifest loading, service creation, HTTP endpoints
"""

import asyncio
import json
import pytest
import requests
from pathlib import Path
from .test_framework import ProServeTestFramework, TestSuite, assert_http_response, assert_service_health


@pytest.mark.asyncio
async def test_manifest_loading(framework: ProServeTestFramework):
    """Test manifest loading and validation"""
    manifest_path = framework.create_test_manifest(
        name='test-manifest-loading',
        endpoints=[
            {'path': '/test', 'method': 'get', 'handler': 'handlers.test.simple'}
        ]
    )
    
    from proserve import ServiceManifest
    manifest = ServiceManifest.from_yaml(manifest_path)
    
    assert manifest.name == 'test-manifest-loading'
    assert manifest.version == '1.0.0'
    assert len(manifest.endpoints) == 2  # /health + /test
    
    return {'manifest_name': manifest.name, 'endpoints_count': len(manifest.endpoints)}


@pytest.mark.asyncio
async def test_service_startup(framework: ProServeTestFramework):
    """Test service startup and health check"""
    manifest_path = framework.create_test_manifest('test-service-startup')
    
    # Create simple handler
    handler_content = '''
async def handle(request):
    return {"status": "ok", "handler": "simple_test"}
'''
    framework.create_test_handler('handlers/test/simple_get.py', handler_content)
    
    service = await framework.start_test_service(manifest_path, 'startup_test')
    
    # Check health endpoint
    manifest = service.manifest
    host = manifest.server['host']
    port = manifest.server['port']
    
    health_data = await assert_service_health(host, port)
    
    return {'service_started': True, 'health_check': health_data}


@pytest.mark.asyncio
async def test_http_endpoints(framework: ProServeTestFramework):
    """Test HTTP endpoint functionality"""
    manifest_path = framework.create_test_manifest(
        'test-http-endpoints',
        endpoints=[
            {'path': '/api/test', 'method': 'get', 'handler': 'handlers.api.test_get'},
            {'path': '/api/test', 'method': 'post', 'handler': 'handlers.api.test_post'},
            {'path': '/api/users/{user_id}', 'method': 'get', 'handler': 'handlers.api.get_user'}
        ]
    )
    
    # Create handlers
    get_handler = '''
async def handle(request):
    return {"method": "GET", "path": "/api/test", "data": "test_data"}
'''
    framework.create_test_handler('handlers/api/test_get.py', get_handler)
    
    post_handler = '''
async def handle(request):
    import json
    try:
        body = await request.json()
    except:
        body = {}
    return {"method": "POST", "received": body}
'''
    framework.create_test_handler('handlers/api/test_post.py', post_handler)
    
    user_handler = '''
async def handle(request):
    user_id = request.match_info.get('user_id', 'unknown')
    return {"user_id": user_id, "name": f"User {user_id}"}
'''
    framework.create_test_handler('handlers/api/get_user.py', user_handler)
    
    service = await framework.start_test_service(manifest_path, 'http_test')
    manifest = service.manifest
    base_url = f"http://{manifest.server['host']}:{manifest.server['port']}"
    
    # Test GET endpoint
    get_response = await assert_http_response(f"{base_url}/api/test")
    assert get_response['method'] == 'GET'
    
    # Test POST endpoint
    post_data = {"test": "data"}
    post_response = requests.post(f"{base_url}/api/test", json=post_data)
    assert post_response.status_code == 200
    assert post_response.json()['received'] == post_data
    
    # Test parameterized endpoint
    user_response = await assert_http_response(f"{base_url}/api/users/123")
    assert user_response['user_id'] == '123'
    
    return {
        'get_test': get_response,
        'post_test': post_response.json(),
        'user_test': user_response
    }


@pytest.mark.asyncio
async def test_logging_system(framework: ProServeTestFramework):
    """Test logging configuration and output"""
    manifest_path = framework.create_test_manifest(
        'test-logging',
        logging={
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'handlers': [
                {'type': 'console', 'level': 'INFO'},
                {'type': 'file', 'filename': str(framework.temp_dir / 'test.log'), 'level': 'DEBUG'}
            ]
        }
    )
    
    # Create logging handler
    logging_handler = '''
import logging
async def handle(request):
    logger = logging.getLogger("test_handler")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    return {"logged": True, "messages": 3}
'''
    framework.create_test_handler('handlers/test/simple_get.py', logging_handler)
    
    service = await framework.start_test_service(manifest_path, 'logging_test')
    manifest = service.manifest
    base_url = f"http://{manifest.server['host']}:{manifest.server['port']}"
    
    # Trigger logging
    response = await assert_http_response(f"{base_url}/api/test")
    
    # Check log file
    log_file = framework.temp_dir / 'test.log'
    if log_file.exists():
        log_content = log_file.read_text()
        has_debug = 'Debug message' in log_content
        has_info = 'Info message' in log_content
        has_warning = 'Warning message' in log_content
    else:
        has_debug = has_info = has_warning = False
    
    return {
        'response': response,
        'log_file_exists': log_file.exists(),
        'has_debug': has_debug,
        'has_info': has_info,
        'has_warning': has_warning
    }


@pytest.mark.asyncio
async def test_error_handling(framework: ProServeTestFramework):
    """Test error handling and 404 responses"""
    manifest_path = framework.create_test_manifest('test-error-handling')
    
    # Create error handler
    error_handler = '''
async def handle(request):
    raise Exception("Test error")
'''
    framework.create_test_handler('handlers/test/simple_get.py', error_handler)
    
    service = await framework.start_test_service(manifest_path, 'error_test')
    manifest = service.manifest
    base_url = f"http://{manifest.server['host']}:{manifest.server['port']}"
    
    # Test 404 for non-existent endpoint
    try:
        response = requests.get(f"{base_url}/nonexistent")
        status_404 = response.status_code == 404
    except:
        status_404 = False
    
    # Test error handling (should return 500)
    try:
        response = requests.get(f"{base_url}/api/test")
        status_500 = response.status_code == 500
    except:
        status_500 = False
    
    return {
        'handles_404': status_404,
        'handles_500': status_500
    }


# Setup test suite
async def setup_core_tests(framework: ProServeTestFramework):
    """Setup for core tests"""
    print("Setting up core tests...")


async def teardown_core_tests(framework: ProServeTestFramework):
    """Teardown for core tests"""
    print("Tearing down core tests...")


# Create test suite
core_test_suite = TestSuite(
    name='core',
    description='Core ProServe functionality tests',
    tests=[
        test_manifest_loading,
        test_service_startup,
        test_http_endpoints,
        test_logging_system,
        test_error_handling
    ],
    setup=setup_core_tests,
    teardown=teardown_core_tests,
    timeout=300,
    parallel=False
)
