"""
ProServe E2E Testing Framework
Comprehensive automated testing for all manifest services
"""

import os
import sys
import asyncio
import pytest
import json
import yaml
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
import subprocess
import time
import requests
import socket
from contextlib import asynccontextmanager

# ProServe imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from proserve import (
    ServiceManifest, ProServeService, CommandGenerator, 
    ManifestBuilder, ServiceDetector, ServiceMigrator,
    start_api_server, ManifestAPIServer
)


@dataclass
class TestResult:
    """Result of a test execution"""
    name: str
    status: str  # passed, failed, skipped
    duration: float
    error: Optional[str] = None
    output: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[Callable]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    timeout: int = 300
    parallel: bool = False


class ProServeTestFramework:
    """Comprehensive E2E testing framework for ProServe"""
    
    def __init__(self, test_dir: Path = None):
        self.test_dir = test_dir or Path(__file__).parent
        self.temp_dir = None
        self.results: List[TestResult] = []
        self.services: Dict[str, ProServeService] = {}
        self.servers: Dict[str, Any] = {}
        self.test_suites: List[TestSuite] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix='proserve_test_'))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    async def cleanup(self):
        """Clean up test resources"""
        # Stop all services
        for name, service in self.services.items():
            try:
                await service.stop()
            except Exception as e:
                print(f"Error stopping service {name}: {e}")
                
        # Stop all servers
        for name, server in self.servers.items():
            try:
                if hasattr(server, 'stop'):
                    await server.stop()
            except Exception as e:
                print(f"Error stopping server {name}: {e}")
                
        self.services.clear()
        self.servers.clear()
        
    def get_free_port(self) -> int:
        """Get a free port for testing"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
        
    def create_test_manifest(self, name: str, **kwargs) -> Path:
        """Create a test manifest file"""
        port = self.get_free_port()
        grpc_port = self.get_free_port()
        
        # Default health endpoint
        default_endpoints = [
            {
                'path': '/health',
                'method': 'get',
                'handler': 'handlers.health.check'
            }
        ]
        
        # Handle custom endpoints - merge with defaults instead of overriding
        custom_endpoints = kwargs.pop('endpoints', [])
        if custom_endpoints:
            # Merge custom endpoints with default health endpoint
            all_endpoints = default_endpoints + custom_endpoints
        else:
            # If no custom endpoints, add default test endpoint
            all_endpoints = default_endpoints + [
                {
                    'path': '/api/test',
                    'method': 'get', 
                    'handler': 'handlers.test.simple_get'
                }
            ]
        
        manifest_data = {
            'name': name,
            'version': '1.0.0',
            'framework': 'proserve',
            'server': {
                'host': '127.0.0.1',
                'port': port
            },
            'grpc_port': grpc_port,
            'endpoints': all_endpoints,
            'logging': {
                'level': 'INFO',
                'handlers': [
                    {'type': 'console'}
                ]
            },
            **kwargs
        }
        
        manifest_path = self.temp_dir / f"{name}_manifest.yml"
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest_data, f)
            
        return manifest_path
        
    def create_test_handler(self, handler_path: str, content: str = None) -> Path:
        """Create a test handler file with proper Python module structure"""
        if content is None:
            content = '''
async def handle(request):
    """Test handler"""
    return {"status": "ok", "message": "test handler response"}
'''
        
        full_path = self.temp_dir / handler_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for proper Python module imports
        current_dir = full_path.parent
        while current_dir != self.temp_dir:
            init_file = current_dir / '__init__.py'
            if not init_file.exists():
                init_file.touch()
            current_dir = current_dir.parent
        
        # Create root __init__.py
        root_init = self.temp_dir / '__init__.py'
        if not root_init.exists():
            root_init.touch()
        
        # Add temp_dir to sys.path if not already there
        import sys
        if str(self.temp_dir) not in sys.path:
            sys.path.insert(0, str(self.temp_dir))
        
        with open(full_path, 'w') as f:
            f.write(content)
            
        return full_path
        
    async def run_test(self, test_func: Callable, name: str = None) -> TestResult:
        """Run a single test function"""
        test_name = name or test_func.__name__
        start_time = time.time()
        
        try:
            result = await test_func(self)
            duration = time.time() - start_time
            
            if result is True or result is None:
                return TestResult(
                    name=test_name,
                    status='passed',
                    duration=duration
                )
            elif isinstance(result, dict):
                return TestResult(
                    name=test_name,
                    status='passed',
                    duration=duration,
                    output=json.dumps(result, indent=2),
                    metadata=result
                )
            else:
                return TestResult(
                    name=test_name,
                    status='failed',
                    duration=duration,
                    error=f"Unexpected result: {result}"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name,
                status='failed', 
                duration=duration,
                error=str(e)
            )
            
    async def run_test_suite(self, suite: TestSuite) -> List[TestResult]:
        """Run a complete test suite"""
        results = []
        
        # Setup
        if suite.setup:
            try:
                await suite.setup(self)
            except Exception as e:
                print(f"Suite setup failed: {e}")
                return [TestResult(
                    name=f"{suite.name}_setup",
                    status='failed',
                    duration=0,
                    error=str(e)
                )]
        
        # Run tests
        if suite.parallel:
            # Run tests in parallel
            tasks = [self.run_test(test, f"{suite.name}_{test.__name__}") 
                    for test in suite.tests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to TestResult
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    results[i] = TestResult(
                        name=f"{suite.name}_{suite.tests[i].__name__}",
                        status='failed',
                        duration=0,
                        error=str(result)
                    )
        else:
            # Run tests sequentially
            for test in suite.tests:
                result = await self.run_test(test, f"{suite.name}_{test.__name__}")
                results.append(result)
                
                # Stop on first failure if configured
                if result.status == 'failed' and not suite.get('continue_on_failure', True):
                    break
        
        # Teardown
        if suite.teardown:
            try:
                await suite.teardown(self)
            except Exception as e:
                print(f"Suite teardown failed: {e}")
        
        return results
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all registered test suites"""
        all_results = []
        
        start_time = time.time()
        
        for suite in self.test_suites:
            print(f"\n🧪 Running test suite: {suite.name}")
            print(f"   Description: {suite.description}")
            
            suite_results = await self.run_test_suite(suite)
            all_results.extend(suite_results)
            
            # Print suite summary
            passed = sum(1 for r in suite_results if r.status == 'passed')
            failed = sum(1 for r in suite_results if r.status == 'failed')
            print(f"   Results: {passed} passed, {failed} failed")
        
        total_duration = time.time() - start_time
        
        # Generate summary
        summary = {
            'total_tests': len(all_results),
            'passed': sum(1 for r in all_results if r.status == 'passed'),
            'failed': sum(1 for r in all_results if r.status == 'failed'),
            'skipped': sum(1 for r in all_results if r.status == 'skipped'),
            'total_duration': total_duration,
            'results': [asdict(r) for r in all_results]
        }
        
        self.results = all_results
        return summary
        
    def register_test_suite(self, suite: TestSuite):
        """Register a test suite"""
        self.test_suites.append(suite)
        
    async def wait_for_service(self, host: str, port: int, timeout: int = 30) -> bool:
        """Wait for a service to be ready"""
        start_time = time.time()
        print(f"DEBUG: wait_for_service starting - checking {host}:{port} for {timeout}s")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://{host}:{port}/health", timeout=15)
                print(f"DEBUG: Health check response: {response.status_code} - {response.text[:50]}")
                if response.status_code == 200:
                    print(f"DEBUG: Service ready! Returning True")
                    return True
            except Exception as e:
                print(f"DEBUG: Health check failed: {e}")
                
            await asyncio.sleep(0.5)
            
        print(f"DEBUG: Timeout reached, returning False")
        return False
        
    async def start_test_service(self, manifest_path: Path, service_name: str = None) -> ProServeService:
        """Start a test service"""
        if service_name is None:
            service_name = f"test_service_{len(self.services)}"
            
        manifest = ServiceManifest.from_yaml(manifest_path)
        service = ProServeService(manifest)
        
        # Start service in background
        await service.start()
        
        # Wait for service to be ready
        host = getattr(manifest, 'host', '127.0.0.1')
        port = getattr(manifest, 'port', 8000)
        
        if await self.wait_for_service(host, port):
            self.services[service_name] = service
            return service
        else:
            await service.stop()
            raise Exception(f"Service {service_name} failed to start")
            
    def export_results(self, format: str = 'json', output_path: Path = None) -> Path:
        """Export test results"""
        if not self.results:
            raise ValueError("No test results to export")
            
        if output_path is None:
            timestamp = int(time.time())
            output_path = self.temp_dir / f"test_results_{timestamp}.{format}"
            
        summary = {
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.status == 'passed'),
            'failed': sum(1 for r in self.results if r.status == 'failed'),
            'results': [asdict(r) for r in self.results]
        }
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
        elif format == 'yaml':
            with open(output_path, 'w') as f:
                yaml.dump(summary, f)
        elif format == 'html':
            html_content = self._generate_html_report(summary)
            with open(output_path, 'w') as f:
                f.write(html_content)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        return output_path
        
    def _generate_html_report(self, summary: Dict[str, Any]) -> str:
        """Generate HTML test report"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>ProServe Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; margin-bottom: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .test-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        .test-result.passed {{ border-left-color: green; }}
        .test-result.failed {{ border-left-color: red; }}
        .error {{ background: #ffe6e6; padding: 10px; margin: 5px 0; }}
        .output {{ background: #f0f0f0; padding: 10px; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>ProServe Test Results</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {summary['total_tests']}</p>
        <p class="passed">Passed: {summary['passed']}</p>
        <p class="failed">Failed: {summary['failed']}</p>
    </div>
    
    <h2>Test Results</h2>
'''
        
        for result in summary['results']:
            status_class = result['status']
            html += f'''
    <div class="test-result {status_class}">
        <h3>{result['name']} - {result['status'].upper()}</h3>
        <p>Duration: {result['duration']:.2f}s</p>
'''
            
            if result.get('error'):
                html += f'<div class="error"><strong>Error:</strong> {result["error"]}</div>'
                
            if result.get('output'):
                html += f'<div class="output"><strong>Output:</strong><pre>{result["output"]}</pre></div>'
                
            html += '</div>'
            
        html += '''
</body>
</html>'''
        
        return html


# Test helper functions
async def assert_http_response(url: str, expected_status: int = 200, 
                              expected_data: Dict = None, timeout: int = 5):
    """Assert HTTP response matches expectations"""
    try:
        response = requests.get(url, timeout=timeout)
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"
            
        if expected_data:
            actual_data = response.json()
            for key, value in expected_data.items():
                assert key in actual_data, f"Missing key: {key}"
                assert actual_data[key] == value, \
                    f"Expected {key}={value}, got {actual_data[key]}"
                    
        return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"HTTP request failed: {e}")


async def assert_service_health(host: str, port: int):
    """Assert service health endpoint is working"""
    health_url = f"http://{host}:{port}/health"
    data = await assert_http_response(health_url, 200, {"status": "healthy"})
    return data


def create_test_framework() -> ProServeTestFramework:
    """Create a new test framework instance"""
    return ProServeTestFramework()


# Export main testing interface
__all__ = [
    'ProServeTestFramework',
    'TestResult', 
    'TestSuite',
    'assert_http_response',
    'assert_service_health',
    'create_test_framework'
]
