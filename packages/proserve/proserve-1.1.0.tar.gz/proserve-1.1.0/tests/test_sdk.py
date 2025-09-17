"""
SDK Component Tests
E2E tests for ManifestBuilder, API server, and programmatic manifest creation
"""

import asyncio
import json
import requests
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, TestSuite


async def test_manifest_builder_basic(framework: ProServeTestFramework):
    """Test basic ManifestBuilder functionality"""
    from proserve.sdk.manifest_builder import ManifestBuilder
    
    # Create builder and configure basic service
    builder = ManifestBuilder('test-sdk-service', '1.0.0')
    builder.with_server('127.0.0.1', framework.get_free_port())
    builder.with_logging('INFO')
    
    # Add endpoint
    builder.add_endpoint('/api/test', 'GET', 'handlers.test.get')
    
    # Build manifest
    manifest_dict = builder.build()
    
    # Validate structure
    assert manifest_dict['name'] == 'test-sdk-service'
    assert manifest_dict['version'] == '1.0.0'
    assert manifest_dict['server']['host'] == '127.0.0.1'
    assert len(manifest_dict['endpoints']) == 1
    assert manifest_dict['endpoints'][0]['path'] == '/api/test'
    
    return {
        'builder_created': True,
        'manifest_name': manifest_dict['name'],
        'endpoints_count': len(manifest_dict['endpoints']),
        'server_configured': 'server' in manifest_dict
    }


async def test_manifest_builder_advanced(framework: ProServeTestFramework):
    """Test advanced ManifestBuilder features"""
    from proserve.sdk.manifest_builder import (
        ManifestBuilder, EndpointBuilder, DatabaseBuilder, 
        LoggingBuilder, GrpcServiceBuilder
    )
    
    # Create advanced manifest
    builder = ManifestBuilder('advanced-sdk-service', '2.0.0')
    
    # Configure server
    builder.with_server('0.0.0.0', framework.get_free_port())
    
    # Add database
    db_builder = DatabaseBuilder('postgresql')
    db_builder.with_host('localhost', 5432)
    db_builder.with_credentials('user', 'password', 'testdb')
    db_config = db_builder.build()
    builder.with_database(db_config)
    
    # Add logging
    log_builder = LoggingBuilder('DEBUG')
    log_builder.with_console_handler()
    log_builder.with_file_handler('test.log')
    log_config = log_builder.build()
    builder.with_logging_config(log_config)
    
    # Add gRPC service
    grpc_builder = GrpcServiceBuilder('TestService')
    grpc_builder.with_package('test.service')
    grpc_builder.with_method('GetTest', 'GetTestRequest', 'TestResponse')
    grpc_config = grpc_builder.build()
    builder.add_grpc_service(grpc_config)
    
    # Add multiple endpoints
    endpoints = [
        {'path': '/api/users', 'method': 'GET', 'handler': 'handlers.users.list'},
        {'path': '/api/users', 'method': 'POST', 'handler': 'handlers.users.create'},
        {'path': '/api/users/{id}', 'method': 'GET', 'handler': 'handlers.users.get'}
    ]
    
    for ep in endpoints:
        builder.add_endpoint(ep['path'], ep['method'], ep['handler'])
    
    # Build manifest
    manifest_dict = builder.build()
    
    # Validate advanced features
    assert manifest_dict['name'] == 'advanced-sdk-service'
    assert manifest_dict['database']['type'] == 'postgresql'
    assert manifest_dict['logging']['level'] == 'DEBUG'
    assert len(manifest_dict['logging']['handlers']) == 2
    assert len(manifest_dict['grpc_services']) == 1
    assert len(manifest_dict['endpoints']) == 3
    
    return {
        'advanced_manifest': True,
        'database_configured': 'database' in manifest_dict,
        'logging_configured': 'logging' in manifest_dict,
        'grpc_configured': 'grpc_services' in manifest_dict,
        'endpoints_count': len(manifest_dict['endpoints'])
    }


async def test_manifest_builder_templates(framework: ProServeTestFramework):
    """Test ManifestBuilder template system"""
    from proserve.sdk.manifest_builder import from_template, TEMPLATES
    
    # Test template availability
    assert 'basic_web' in TEMPLATES
    assert 'rest_api' in TEMPLATES
    assert 'microservice' in TEMPLATES
    
    # Create from template
    builder = from_template('rest_api', name='template-test-service', port=framework.get_free_port())
    manifest_dict = builder.build()
    
    # Validate template structure
    assert manifest_dict['name'] == 'template-test-service'
    assert 'endpoints' in manifest_dict
    assert len(manifest_dict['endpoints']) > 0  # Templates should have endpoints
    
    # Test template customization
    builder.add_endpoint('/custom', 'POST', 'handlers.custom.post')
    updated_manifest = builder.build()
    
    # Should have original template endpoints plus custom one
    assert len(updated_manifest['endpoints']) > len(manifest_dict['endpoints'])
    
    return {
        'templates_available': len(TEMPLATES),
        'template_created': True,
        'customization_works': len(updated_manifest['endpoints']) > len(manifest_dict['endpoints']),
        'template_name': manifest_dict['name']
    }


async def test_manifest_builder_export(framework: ProServeTestFramework):
    """Test ManifestBuilder export functionality"""
    from proserve.sdk.manifest_builder import ManifestBuilder
    
    # Create builder
    builder = ManifestBuilder('export-test-service', '1.0.0')
    builder.with_server('127.0.0.1', framework.get_free_port())
    builder.add_endpoint('/test', 'GET', 'handlers.test.get')
    
    # Export as YAML
    yaml_content = builder.to_yaml()
    assert 'name: export-test-service' in yaml_content
    assert 'version: 1.0.0' in yaml_content
    assert 'endpoints:' in yaml_content
    
    # Export as JSON
    json_content = builder.to_json()
    json_data = json.loads(json_content)
    assert json_data['name'] == 'export-test-service'
    assert json_data['version'] == '1.0.0'
    
    # Export to file
    yaml_file = framework.temp_dir / 'exported_manifest.yml'
    builder.to_yaml_file(yaml_file)
    assert yaml_file.exists()
    
    file_content = yaml_file.read_text()
    assert 'name: export-test-service' in file_content
    
    return {
        'yaml_export': 'name: export-test-service' in yaml_content,
        'json_export': json_data['name'] == 'export-test-service',
        'file_export': yaml_file.exists(),
        'exports_working': True
    }


async def test_command_generator_integration(framework: ProServeTestFramework):
    """Test CommandGenerator with SDK-built manifests"""
    from proserve.sdk.manifest_builder import ManifestBuilder
    from proserve.tools.command_generator import CommandGenerator
    
    # Create manifest with SDK
    builder = ManifestBuilder('command-gen-test', '1.0.0')
    port = framework.get_free_port()
    grpc_port = framework.get_free_port()
    
    builder.with_server('127.0.0.1', port)
    builder.add_endpoint('/api/test', 'GET', 'handlers.test.get')
    builder.add_endpoint('/api/data', 'POST', 'handlers.data.create')
    
    # Add gRPC service
    from proserve.sdk.manifest_builder import GrpcServiceBuilder
    grpc_builder = GrpcServiceBuilder('TestService')
    grpc_builder.with_method('GetData', 'GetDataRequest', 'DataResponse')
    builder.add_grpc_service(grpc_builder.build())
    builder.with_grpc_port(grpc_port)
    
    # Export to temporary file
    manifest_file = framework.temp_dir / 'command_test_manifest.yml'
    builder.to_yaml_file(manifest_file)
    
    # Generate commands
    generator = CommandGenerator(manifest_file)
    commands = generator.generate_all()
    
    # Validate generated commands
    command_types = set(cmd.type for cmd in commands)
    assert 'curl' in command_types
    assert 'shell' in command_types
    assert 'python' in command_types
    assert 'grpc' in command_types
    
    # Check specific commands
    curl_commands = [cmd for cmd in commands if cmd.type == 'curl']
    assert any(f'127.0.0.1:{port}' in cmd.command for cmd in curl_commands)
    
    grpc_commands = [cmd for cmd in commands if cmd.type == 'grpc']
    assert any(f'127.0.0.1:{grpc_port}' in cmd.command for cmd in grpc_commands)
    
    return {
        'commands_generated': len(commands),
        'command_types': list(command_types),
        'curl_commands': len(curl_commands),
        'grpc_commands': len(grpc_commands),
        'integration_successful': True
    }


async def test_api_server_startup(framework: ProServeTestFramework):
    """Test ManifestAPIServer startup and basic endpoints"""
    from proserve.sdk.api_server import ManifestAPIServer
    
    # Create API server
    api_port = framework.get_free_port()
    server = ManifestAPIServer(host='127.0.0.1', port=api_port)
    
    try:
        # Start server
        await server.start()
        framework.servers['api_server'] = server
        
        # Wait for server to be ready
        server_ready = await framework.wait_for_service('127.0.0.1', api_port, timeout=10)
        
        if server_ready:
            base_url = f"http://127.0.0.1:{api_port}"
            
            # Test health endpoint
            health_response = requests.get(f"{base_url}/health", timeout=5)
            health_ok = health_response.status_code == 200
            
            # Test API docs endpoint
            docs_response = requests.get(f"{base_url}/docs", timeout=5)
            docs_ok = docs_response.status_code == 200
            
            # Test projects list (should be empty initially)
            projects_response = requests.get(f"{base_url}/api/v1/projects", timeout=5)
            projects_ok = projects_response.status_code == 200
            projects_empty = len(projects_response.json()) == 0
            
            return {
                'server_started': True,
                'health_endpoint': health_ok,
                'docs_endpoint': docs_ok,
                'projects_endpoint': projects_ok,
                'initially_empty': projects_empty,
                'api_port': api_port
            }
        else:
            return {
                'server_started': False,
                'error': 'Server not ready within timeout'
            }
            
    except Exception as e:
        return {
            'server_started': False,
            'error': str(e)
        }


async def test_api_server_project_crud(framework: ProServeTestFramework):
    """Test API server project CRUD operations"""
    from proserve.sdk.api_server import ManifestAPIServer
    
    # Create API server
    api_port = framework.get_free_port()
    server = ManifestAPIServer(host='127.0.0.1', port=api_port)
    
    try:
        # Start server
        await server.start()
        framework.servers['api_server_crud'] = server
        
        if await framework.wait_for_service('127.0.0.1', api_port, timeout=10):
            base_url = f"http://127.0.0.1:{api_port}"
            
            # Create project
            project_data = {
                'name': 'test-api-project',
                'description': 'Test project for API',
                'version': '1.0.0',
                'author': 'test@example.com',
                'tags': ['test', 'api']
            }
            
            create_response = requests.post(f"{base_url}/api/v1/projects", json=project_data, timeout=5)
            create_ok = create_response.status_code == 201
            
            if create_ok:
                project = create_response.json()
                project_id = project['id']
                
                # Get project
                get_response = requests.get(f"{base_url}/api/v1/projects/{project_id}", timeout=5)
                get_ok = get_response.status_code == 200
                
                # Update project
                update_data = {'description': 'Updated description'}
                update_response = requests.put(f"{base_url}/api/v1/projects/{project_id}", json=update_data, timeout=5)
                update_ok = update_response.status_code == 200
                
                # List projects
                list_response = requests.get(f"{base_url}/api/v1/projects", timeout=5)
                list_ok = list_response.status_code == 200
                has_project = len(list_response.json()) == 1
                
                # Delete project
                delete_response = requests.delete(f"{base_url}/api/v1/projects/{project_id}", timeout=5)
                delete_ok = delete_response.status_code == 200
                
                return {
                    'crud_test': True,
                    'create_ok': create_ok,
                    'get_ok': get_ok,
                    'update_ok': update_ok,
                    'list_ok': list_ok,
                    'delete_ok': delete_ok,
                    'has_project': has_project,
                    'project_id': project_id
                }
            else:
                return {
                    'crud_test': False,
                    'create_failed': True,
                    'create_status': create_response.status_code
                }
                
        else:
            return {
                'crud_test': False,
                'server_not_ready': True
            }
            
    except Exception as e:
        return {
            'crud_test': False,
            'error': str(e)
        }


async def test_api_server_manifest_operations(framework: ProServeTestFramework):
    """Test API server manifest export and template operations"""
    from proserve.sdk.api_server import ManifestAPIServer
    
    # Create API server
    api_port = framework.get_free_port()
    server = ManifestAPIServer(host='127.0.0.1', port=api_port)
    
    try:
        await server.start()
        framework.servers['api_server_manifest'] = server
        
        if await framework.wait_for_service('127.0.0.1', api_port, timeout=10):
            base_url = f"http://127.0.0.1:{api_port}"
            
            # Create project with manifest
            project_data = {
                'name': 'manifest-test-project',
                'manifest': {
                    'name': 'test-service',
                    'version': '1.0.0',
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [
                        {'path': '/test', 'method': 'GET', 'handler': 'handlers.test.get'}
                    ]
                }
            }
            
            create_response = requests.post(f"{base_url}/api/v1/projects", json=project_data, timeout=5)
            
            if create_response.status_code == 201:
                project_id = create_response.json()['id']
                
                # Export manifest as YAML
                yaml_response = requests.get(f"{base_url}/api/v1/projects/{project_id}/manifest/yaml", timeout=5)
                yaml_ok = yaml_response.status_code == 200
                yaml_content = yaml_response.text if yaml_ok else ''
                
                # Export manifest as JSON
                json_response = requests.get(f"{base_url}/api/v1/projects/{project_id}/manifest/json", timeout=5)
                json_ok = json_response.status_code == 200
                
                # List templates
                templates_response = requests.get(f"{base_url}/api/v1/templates", timeout=5)
                templates_ok = templates_response.status_code == 200
                templates = templates_response.json() if templates_ok else {}
                
                # Create from template
                template_data = {
                    'name': 'template-created-service',
                    'port': 8080
                }
                
                template_response = requests.post(f"{base_url}/api/v1/templates/rest_api", json=template_data, timeout=5)
                template_ok = template_response.status_code == 201
                
                return {
                    'manifest_operations': True,
                    'yaml_export': yaml_ok,
                    'json_export': json_ok,
                    'templates_list': templates_ok,
                    'template_creation': template_ok,
                    'templates_count': len(templates),
                    'yaml_has_content': 'name: test-service' in yaml_content
                }
            else:
                return {
                    'manifest_operations': False,
                    'project_creation_failed': True
                }
                
        else:
            return {
                'manifest_operations': False,
                'server_not_ready': True
            }
            
    except Exception as e:
        return {
            'manifest_operations': False,
            'error': str(e)
        }


# Setup and teardown
async def setup_sdk_tests(framework: ProServeTestFramework):
    """Setup for SDK tests"""
    print("Setting up SDK tests...")


async def teardown_sdk_tests(framework: ProServeTestFramework):
    """Teardown for SDK tests"""
    print("Tearing down SDK tests...")
    
    # Clean up any running API servers
    for name, server in list(framework.servers.items()):
        if 'api_server' in name:
            try:
                if hasattr(server, 'app') and server.app:
                    await server.app.shutdown()
            except Exception as e:
                print(f"Error shutting down {name}: {e}")


# Create test suite
sdk_test_suite = TestSuite(
    name='sdk',
    description='SDK and tools functionality tests',
    tests=[
        test_manifest_builder_basic,
        test_manifest_builder_advanced,
        test_manifest_builder_templates,
        test_manifest_builder_export,
        test_command_generator_integration,
        test_api_server_startup,
        test_api_server_project_crud,
        test_api_server_manifest_operations
    ],
    setup=setup_sdk_tests,
    teardown=teardown_sdk_tests,
    timeout=300,
    parallel=False
)
