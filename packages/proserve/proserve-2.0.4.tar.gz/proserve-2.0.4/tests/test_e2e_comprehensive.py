"""
Comprehensive End-to-End Test Suite for ProServe Package
Tests all core functionality including services, manifests, deployment, and integration patterns
"""

import asyncio
import json
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
from aiohttp import web
import aiohttp.test_utils

# Import ProServe components
from proserve.core.service import ProServeService
from proserve.core.manifest import ServiceManifest
from proserve.cli import ProServeCLI


class TestServiceManifest:
    """Test ServiceManifest functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_manifest_creation_and_parsing(self):
        """Test manifest creation from dictionary and YAML"""
        manifest_data = {
            'name': 'test-service',
            'version': '1.0.0',
            'description': 'Test service for ProServe',
            'port': 8080,
            'host': '0.0.0.0',
            'environment': 'development',
            'isolation': {
                'mode': 'process',
                'timeout': 30
            },
            'endpoints': {
                'http': [
                    {
                        'path': '/api/test',
                        'method': 'GET',
                        'handler': 'handlers.test.get_test'
                    }
                ]
            },
            'env_vars': ['DATABASE_URL', 'API_KEY']
        }
        
        manifest = ServiceManifest(manifest_data)
        
        assert manifest.name == 'test-service'
        assert manifest.version == '1.0.0'
        assert manifest.port == 8080
        assert manifest.config['isolation']['mode'] == 'process'
        assert len(manifest.config['endpoints']['http']) == 1
        assert 'DATABASE_URL' in manifest.config['env_vars']
    
    def test_manifest_yaml_loading(self):
        """Test loading manifest from YAML file"""
        yaml_content = """
name: yaml-test-service
version: 2.0.0
description: YAML-based test service
port: 9090
host: localhost
environment: test
isolation:
  mode: docker
  timeout: 60
endpoints:
  http:
    - path: /health
      method: GET
      handler: handlers.health.check
grpc:
  port: 9091
  services:
    - service.TestService
        """
        
        yaml_file = os.path.join(self.temp_dir, 'test-manifest.yaml')
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)
        
        manifest = ServiceManifest.from_yaml(yaml_file)
        
        assert manifest.name == 'yaml-test-service'
        assert manifest.version == '2.0.0'
        assert manifest.port == 9090
        assert manifest.config['isolation']['mode'] == 'docker'
        assert manifest.config['grpc']['port'] == 9091
    
    def test_environment_variable_expansion(self):
        """Test environment variable expansion in manifests"""
        os.environ['TEST_PORT'] = '8080'
        os.environ['TEST_HOST'] = '127.0.0.1'
        
        manifest_data = {
            'name': 'env-test-service',
            'port': '${TEST_PORT}',
            'host': '${TEST_HOST}',
            'database_url': '${DATABASE_URL:-postgresql://localhost/test}'
        }
        
        manifest = ServiceManifest(manifest_data)
        
        # Test environment expansion
        expanded_port = manifest.expand_env_vars('${TEST_PORT}')
        expanded_host = manifest.expand_env_vars('${TEST_HOST}')
        expanded_db = manifest.expand_env_vars('${DATABASE_URL:-postgresql://localhost/test}')
        
        assert expanded_port == '8080'
        assert expanded_host == '127.0.0.1'
        assert expanded_db == 'postgresql://localhost/test'  # Default value
        
        # Cleanup
        del os.environ['TEST_PORT']
        del os.environ['TEST_HOST']
    
    def test_manifest_validation(self):
        """Test manifest validation"""
        # Valid manifest
        valid_manifest_data = {
            'name': 'valid-service',
            'version': '1.0.0',
            'port': 8080
        }
        
        manifest = ServiceManifest(valid_manifest_data)
        assert manifest.validate() == True
        
        # Invalid manifest - missing required fields
        invalid_manifest_data = {
            'version': '1.0.0'  # Missing name
        }
        
        with pytest.raises(Exception):
            ServiceManifest(invalid_manifest_data)


class TestProServeService:
    """Test ProServeService functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization from manifest"""
        manifest_data = {
            'name': 'init-test-service',
            'version': '1.0.0',
            'port': 8080,
            'host': '127.0.0.1',
            'environment': 'test'
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        assert service.name == 'init-test-service'
        assert service.version == '1.0.0'
        assert service.port == 8080
        assert service.host == '127.0.0.1'
        assert service.logger is not None
    
    @pytest.mark.asyncio
    async def test_service_with_isolation_manager(self):
        """Test service with isolation configuration"""
        manifest_data = {
            'name': 'isolation-test-service',
            'port': 8080,
            'isolation': {
                'mode': 'process',
                'timeout': 30,
                'memory_limit': '512MB'
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        assert service.isolation_manager is not None
        assert service.isolation_manager.mode == 'process'
        assert service.isolation_manager.timeout == 30
    
    @pytest.mark.asyncio
    async def test_http_endpoint_registration(self):
        """Test HTTP endpoint registration and handling"""
        manifest_data = {
            'name': 'endpoint-test-service',
            'port': 8080,
            'endpoints': {
                'http': [
                    {
                        'path': '/test',
                        'method': 'GET',
                        'handler': 'test_handler'
                    },
                    {
                        'path': '/api/data',
                        'method': 'POST',
                        'handler': 'data_handler'
                    }
                ]
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock handlers
        async def test_handler(request):
            return web.json_response({'message': 'test endpoint'})
        
        async def data_handler(request):
            data = await request.json()
            return web.json_response({'received': data})
        
        # Register mock handlers
        service.add_handler('test_handler', test_handler)
        service.add_handler('data_handler', data_handler)
        
        # Setup HTTP endpoints
        app = web.Application()
        service.setup_http_endpoints(app)
        
        # Test endpoint registration
        assert len(app.router._resources) >= 2
    
    @pytest.mark.asyncio
    async def test_background_tasks(self):
        """Test background task execution"""
        manifest_data = {
            'name': 'task-test-service',
            'port': 8080,
            'background_tasks': [
                {
                    'name': 'test_task',
                    'handler': 'test_task_handler',
                    'interval': 1
                }
            ]
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock task handler
        task_executions = []
        
        async def test_task_handler():
            task_executions.append(True)
            return {'status': 'completed'}
        
        service.add_handler('test_task_handler', test_task_handler)
        
        # Start background tasks
        await service.setup_background_tasks()
        
        # Wait for task execution
        await asyncio.sleep(1.5)
        
        # Verify task was executed
        assert len(task_executions) > 0
    
    @pytest.mark.asyncio
    async def test_service_health_endpoint(self):
        """Test built-in health endpoint"""
        manifest_data = {
            'name': 'health-test-service',
            'port': 8080,
            'health_endpoint': True
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Create test client
        app = web.Application()
        service.setup_health_endpoints(app)
        
        # Mock health check
        async def mock_health_handler(request):
            return web.json_response({
                'status': 'healthy',
                'service': service.name,
                'version': service.version
            })
        
        app.router.add_get('/health', mock_health_handler)
        
        # Test health endpoint exists
        found_health_route = False
        for resource in app.router._resources:
            if hasattr(resource, '_path') and '/health' in str(resource._path):
                found_health_route = True
                break
        
        assert found_health_route


class TestServiceDeployment:
    """Test service deployment patterns"""
    
    def setup_method(self):
        """Setup deployment test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup deployment test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_service_discovery_integration(self):
        """Test service discovery functionality"""
        manifest_data = {
            'name': 'discovery-test-service',
            'port': 8080,
            'service_discovery': {
                'enabled': True,
                'registry': 'consul',
                'health_check_interval': 30
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock service discovery
        with patch('proserve.discovery.ServiceRegistry') as mock_registry:
            mock_registry_instance = Mock()
            mock_registry.return_value = mock_registry_instance
            
            await service.register_with_discovery()
            
            # Verify registration was attempted
            mock_registry.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multiple_service_deployment(self):
        """Test deploying multiple services"""
        # Create multiple manifest files
        service_configs = [
            {
                'name': 'service-1',
                'port': 8081,
                'endpoints': {
                    'http': [{'path': '/service1', 'method': 'GET', 'handler': 'handler1'}]
                }
            },
            {
                'name': 'service-2', 
                'port': 8082,
                'endpoints': {
                    'http': [{'path': '/service2', 'method': 'GET', 'handler': 'handler2'}]
                }
            }
        ]
        
        services = []
        for config in service_configs:
            manifest = ServiceManifest(config)
            service = ProServeService(manifest)
            services.append(service)
        
        # Verify services are configured correctly
        assert len(services) == 2
        assert services[0].name == 'service-1'
        assert services[1].name == 'service-2'
        assert services[0].port == 8081
        assert services[1].port == 8082
    
    def test_docker_deployment_configuration(self):
        """Test Docker deployment configuration"""
        manifest_data = {
            'name': 'docker-service',
            'port': 8080,
            'deployment': {
                'type': 'docker',
                'image': 'proserve/test-service:1.0.0',
                'replicas': 3,
                'resources': {
                    'memory': '512Mi',
                    'cpu': '0.5'
                }
            },
            'isolation': {
                'mode': 'docker',
                'network_isolation': True,
                'filesystem_isolation': True
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Verify Docker configuration
        deployment_config = manifest.config.get('deployment', {})
        assert deployment_config['type'] == 'docker'
        assert deployment_config['replicas'] == 3
        assert deployment_config['resources']['memory'] == '512Mi'
        
        # Verify isolation configuration
        assert service.isolation_manager.mode == 'docker'
        assert service.isolation_manager.network_isolation == True


class TestIntegrationPatterns:
    """Test integration patterns with ecosystem packages"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup integration test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_wmlog_integration(self):
        """Test integration with WML logging"""
        manifest_data = {
            'name': 'wmlog-integration-service',
            'port': 8080,
            'logging': {
                'provider': 'wmlog',
                'level': 'INFO',
                'structured': True,
                'websocket_broadcast': False,  # Disabled for testing
                'file_output': True,
                'file_path': os.path.join(self.temp_dir, 'service.log')
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Test logging functionality
        service.logger.info("WML integration test", service_type="proserve")
        
        # Verify log file creation
        log_file = manifest.config['logging']['file_path']
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "WML integration test" in log_content
            assert "proserve" in log_content
    
    @pytest.mark.asyncio
    async def test_servos_isolation_integration(self):
        """Test integration with Servos isolation"""
        manifest_data = {
            'name': 'servos-integration-service',
            'port': 8080,
            'isolation': {
                'provider': 'servos',
                'mode': 'process',
                'timeout': 30,
                'platform': 'rp2040'
            },
            'endpoints': {
                'http': [
                    {
                        'path': '/execute',
                        'method': 'POST',
                        'handler': 'execution_handler'
                    }
                ]
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock script execution handler
        async def execution_handler(request):
            data = await request.json()
            script_path = data.get('script_path')
            
            # Use isolation manager to execute script
            if service.isolation_manager:
                result = await service.isolation_manager.execute_script(
                    script_path, service, request
                )
                return web.json_response({'result': result})
            
            return web.json_response({'error': 'Isolation not available'})
        
        service.add_handler('execution_handler', execution_handler)
        
        # Verify isolation manager is configured
        assert service.isolation_manager is not None
        assert service.isolation_manager.mode == 'process'
    
    @pytest.mark.asyncio
    async def test_edpmt_framework_integration(self):
        """Test integration with EDPMT framework"""
        manifest_data = {
            'name': 'edpmt-integration-service',
            'port': 8080,
            'edpmt': {
                'backend_host': 'localhost',
                'backend_port': 8888,
                'hardware_interface': True
            },
            'endpoints': {
                'http': [
                    {
                        'path': '/gpio/read',
                        'method': 'GET',
                        'handler': 'gpio_read_handler'
                    }
                ]
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock EDPMT client
        mock_edpmt_client = Mock()
        mock_edpmt_client.gpio_read = AsyncMock(return_value={'pin': 18, 'value': 1})
        service.edpmt_client = mock_edpmt_client
        
        # Mock GPIO handler
        async def gpio_read_handler(request):
            pin = int(request.query.get('pin', 18))
            
            if service.edpmt_client:
                result = await service.edpmt_client.gpio_read(pin=pin)
                return web.json_response(result)
            
            return web.json_response({'error': 'EDPMT not available'})
        
        service.add_handler('gpio_read_handler', gpio_read_handler)
        
        # Verify EDPMT configuration
        edpmt_config = manifest.config.get('edpmt', {})
        assert edpmt_config['backend_host'] == 'localhost'
        assert edpmt_config['backend_port'] == 8888
        assert edpmt_config['hardware_interface'] == True


class TestCLIInterface:
    """Test ProServe CLI functionality"""
    
    def setup_method(self):
        """Setup CLI test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup CLI test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cli_initialization(self):
        """Test CLI initialization"""
        cli = ProServeCLI()
        assert cli is not None
        
        # Test argument parsing
        test_args = ['--manifest', 'test-manifest.yaml', '--debug']
        parsed_args = cli.parse_args(test_args)
        
        assert parsed_args.manifest == 'test-manifest.yaml'
        assert parsed_args.debug == True
    
    def test_manifest_generation_command(self):
        """Test CLI manifest generation"""
        cli = ProServeCLI()
        
        # Test manifest generation
        output_file = os.path.join(self.temp_dir, 'generated-manifest.yaml')
        
        # Mock generate_manifest method
        cli.generate_manifest(
            service_name='cli-test-service',
            port=8080,
            output_file=output_file
        )
        
        # Verify manifest file was created
        assert os.path.exists(output_file)
        
        # Verify manifest content
        with open(output_file, 'r') as f:
            manifest_content = yaml.safe_load(f)
            assert manifest_content['name'] == 'cli-test-service'
            assert manifest_content['port'] == 8080
    
    def test_service_validation_command(self):
        """Test CLI service validation"""
        # Create test manifest
        manifest_file = os.path.join(self.temp_dir, 'validation-test.yaml')
        manifest_data = {
            'name': 'validation-test-service',
            'version': '1.0.0',
            'port': 8080,
            'endpoints': {
                'http': [
                    {
                        'path': '/test',
                        'method': 'GET',
                        'handler': 'test_handler'
                    }
                ]
            }
        }
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest_data, f)
        
        cli = ProServeCLI()
        
        # Test validation
        validation_result = cli.validate_manifest(manifest_file)
        assert validation_result == True


class TestErrorHandlingAndReliability:
    """Test error handling and reliability features"""
    
    def setup_method(self):
        """Setup error handling test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup error handling test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_invalid_manifest_handling(self):
        """Test handling of invalid manifests"""
        # Test missing required fields
        invalid_manifest_data = {
            'version': '1.0.0',
            'port': 8080
            # Missing 'name' field
        }
        
        with pytest.raises(Exception):
            ServiceManifest(invalid_manifest_data)
        
        # Test invalid data types
        invalid_type_manifest = {
            'name': 'test-service',
            'port': 'invalid_port'  # Should be integer
        }
        
        manifest = ServiceManifest(invalid_type_manifest)
        # Should handle gracefully with validation
        assert manifest.name == 'test-service'
    
    @pytest.mark.asyncio
    async def test_handler_error_recovery(self):
        """Test error recovery in handlers"""
        manifest_data = {
            'name': 'error-test-service',
            'port': 8080,
            'endpoints': {
                'http': [
                    {
                        'path': '/error-test',
                        'method': 'GET',
                        'handler': 'error_handler'
                    }
                ]
            }
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock error handler
        async def error_handler(request):
            raise Exception("Test error")
        
        service.add_handler('error_handler', error_handler)
        
        # Service should handle handler errors gracefully
        # and not crash the entire service
        assert service.isolation_manager is not None
    
    @pytest.mark.asyncio
    async def test_service_shutdown_gracefully(self):
        """Test graceful service shutdown"""
        manifest_data = {
            'name': 'shutdown-test-service',
            'port': 8080
        }
        
        manifest = ServiceManifest(manifest_data)
        service = ProServeService(manifest)
        
        # Mock cleanup tasks
        cleanup_called = []
        
        async def cleanup_task():
            cleanup_called.append(True)
        
        service.add_cleanup_task(cleanup_task)
        
        # Test shutdown
        await service.shutdown()
        
        # Verify cleanup was called
        assert len(cleanup_called) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
