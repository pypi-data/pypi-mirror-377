"""
ProServe HTTP Command Generator - HTTP/REST API Command Generation
Generates HTTP commands, cURL requests, and client code for REST endpoints
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urljoin

from .command_types import (
    GeneratedCommand, CommandType, CommandLanguage, CommandTemplate,
    CURL_TEMPLATES, PYTHON_TEMPLATES, JAVASCRIPT_TEMPLATES
)


class HTTPCommandGenerator:
    """Generates HTTP/REST API commands from endpoint definitions"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def generate_endpoint_commands(self, endpoints: List[Dict[str, Any]]) -> List[GeneratedCommand]:
        """Generate commands for all HTTP endpoints"""
        commands = []
        
        for endpoint in endpoints:
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'GET').upper()
            
            # Generate cURL commands
            commands.extend(self._generate_curl_commands(method, path, endpoint))
            
            # Generate Python requests commands
            commands.extend(self._generate_python_commands(method, path, endpoint))
            
            # Generate JavaScript fetch commands
            commands.extend(self._generate_javascript_commands(method, path, endpoint))
            
        return commands
    
    def _generate_curl_commands(self, method: str, path: str, endpoint: Dict[str, Any]) -> List[GeneratedCommand]:
        """Generate cURL commands for an endpoint"""
        commands = []
        
        # Basic cURL command
        if method == 'GET':
            template = CURL_TEMPLATES['get']
            command = template.render(base_url=self.base_url, path=path)
            
        elif method == 'POST':
            template = CURL_TEMPLATES['post']
            sample_data = self._generate_sample_data(endpoint)
            command = template.render(
                base_url=self.base_url, 
                path=path, 
                data=json.dumps(sample_data)
            )
            
        elif method == 'PUT':
            template = CURL_TEMPLATES['put']
            sample_data = self._generate_sample_data(endpoint)
            command = template.render(
                base_url=self.base_url, 
                path=path, 
                data=json.dumps(sample_data)
            )
            
        elif method == 'DELETE':
            template = CURL_TEMPLATES['delete']
            command = template.render(base_url=self.base_url, path=path)
            
        else:
            # Generic method
            command = f'curl -X {method} {self.base_url}{path}'
        
        # Add authentication if specified
        auth = endpoint.get('authentication')
        if auth:
            command = self._add_auth_to_curl(command, auth)
        
        # Add custom headers
        headers = endpoint.get('headers', {})
        if headers:
            command = self._add_headers_to_curl(command, headers)
        
        commands.append(GeneratedCommand(
            type=CommandType.CURL,
            command=command,
            description=f'{method} {path} endpoint',
            example_output=self._generate_example_output(method, endpoint),
            language=CommandLanguage.BASH
        ))
        
        return commands
    
    def _generate_python_commands(self, method: str, path: str, endpoint: Dict[str, Any]) -> List[GeneratedCommand]:
        """Generate Python requests commands for an endpoint"""
        commands = []
        
        if method == 'GET':
            template = PYTHON_TEMPLATES['get']
            command = template.render(base_url=self.base_url, path=path)
            
        elif method == 'POST':
            template = PYTHON_TEMPLATES['post']
            sample_data = self._generate_sample_data(endpoint)
            command = template.render(
                base_url=self.base_url, 
                path=path, 
                data=repr(sample_data)
            )
            
        elif method == 'PUT':
            template = PYTHON_TEMPLATES['put']
            sample_data = self._generate_sample_data(endpoint)
            command = template.render(
                base_url=self.base_url, 
                path=path, 
                data=repr(sample_data)
            )
            
        elif method == 'DELETE':
            template = PYTHON_TEMPLATES['delete']
            command = template.render(base_url=self.base_url, path=path)
            
        else:
            # Generic method
            command = f'''import requests

url = "{self.base_url}{path}"
response = requests.request("{method}", url)
print(response.json())'''
        
        # Add authentication if specified
        auth = endpoint.get('authentication')
        if auth:
            command = self._add_auth_to_python(command, auth)
        
        commands.append(GeneratedCommand(
            type=CommandType.PYTHON,
            command=command,
            description=f'Python request to {method} {path}',
            language=CommandLanguage.PYTHON
        ))
        
        return commands
    
    def _generate_javascript_commands(self, method: str, path: str, endpoint: Dict[str, Any]) -> List[GeneratedCommand]:
        """Generate JavaScript fetch commands for an endpoint"""
        commands = []
        
        if method == 'GET':
            template = JAVASCRIPT_TEMPLATES['get']
            command = template.render(base_url=self.base_url, path=path)
            
        elif method == 'POST':
            template = JAVASCRIPT_TEMPLATES['post']
            sample_data = self._generate_sample_data(endpoint)
            command = template.render(
                base_url=self.base_url, 
                path=path, 
                data=json.dumps(sample_data)
            )
            
        else:
            # Generic method
            if method in ['POST', 'PUT', 'PATCH']:
                sample_data = self._generate_sample_data(endpoint)
                command = f'''fetch('{self.base_url}{path}', {{
  method: '{method}',
  headers: {{
    'Content-Type': 'application/json',
  }},
  body: JSON.stringify({json.dumps(sample_data)})
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));'''
            else:
                command = f'''fetch('{self.base_url}{path}', {{
  method: '{method}'
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));'''
        
        commands.append(GeneratedCommand(
            type=CommandType.JAVASCRIPT,
            command=command,
            description=f'JavaScript fetch to {method} {path}',
            language=CommandLanguage.JAVASCRIPT
        ))
        
        return commands
    
    def _generate_sample_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample data for POST/PUT requests"""
        # Check if endpoint has validation schema
        validation = endpoint.get('validation', {})
        schema = validation.get('schema', {})
        
        if schema:
            return self._generate_data_from_schema(schema)
        
        # Default sample data based on endpoint path
        path = endpoint.get('path', '/')
        
        if 'user' in path.lower():
            return {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30
            }
        elif 'product' in path.lower():
            return {
                "name": "Sample Product",
                "price": 29.99,
                "category": "electronics"
            }
        elif 'order' in path.lower():
            return {
                "product_id": 1,
                "quantity": 2,
                "total": 59.98
            }
        else:
            return {
                "key": "value",
                "status": "active",
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    def _generate_data_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample data from JSON schema"""
        data = {}
        properties = schema.get('properties', {})
        
        for field_name, field_schema in properties.items():
            field_type = field_schema.get('type', 'string')
            
            if field_type == 'string':
                if 'email' in field_name.lower():
                    data[field_name] = "user@example.com"
                elif 'name' in field_name.lower():
                    data[field_name] = "Sample Name"
                else:
                    data[field_name] = "sample_value"
                    
            elif field_type == 'integer':
                data[field_name] = 42
                
            elif field_type == 'number':
                data[field_name] = 3.14
                
            elif field_type == 'boolean':
                data[field_name] = True
                
            elif field_type == 'array':
                data[field_name] = ["item1", "item2"]
                
            elif field_type == 'object':
                data[field_name] = {"nested": "value"}
        
        return data
    
    def _generate_example_output(self, method: str, endpoint: Dict[str, Any]) -> str:
        """Generate example output for the endpoint"""
        path = endpoint.get('path', '/')
        
        if method == 'GET':
            if '{id}' in path or path.endswith('/1'):
                return '{"id": 1, "name": "Sample Item", "status": "active"}'
            else:
                return '{"items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}], "total": 2}'
                
        elif method == 'POST':
            return '{"id": 3, "message": "Created successfully", "status": "created"}'
            
        elif method == 'PUT':
            return '{"id": 1, "message": "Updated successfully", "status": "updated"}'
            
        elif method == 'DELETE':
            return '{"message": "Deleted successfully", "status": "deleted"}'
            
        else:
            return '{"result": "success", "message": "Operation completed"}'
    
    def _add_auth_to_curl(self, command: str, auth: Dict[str, Any]) -> str:
        """Add authentication to cURL command"""
        auth_type = auth.get('type', '').lower()
        
        if auth_type == 'bearer':
            return command + ' -H "Authorization: Bearer YOUR_TOKEN"'
        elif auth_type == 'basic':
            return command + ' -u "username:password"'
        elif auth_type == 'api_key':
            header = auth.get('header', 'X-API-Key')
            return command + f' -H "{header}: YOUR_API_KEY"'
        else:
            return command + ' -H "Authorization: YOUR_AUTH_TOKEN"'
    
    def _add_headers_to_curl(self, command: str, headers: Dict[str, str]) -> str:
        """Add custom headers to cURL command"""
        for key, value in headers.items():
            command += f' -H "{key}: {value}"'
        return command
    
    def _add_auth_to_python(self, command: str, auth: Dict[str, Any]) -> str:
        """Add authentication to Python requests command"""
        auth_type = auth.get('type', '').lower()
        
        if auth_type == 'bearer':
            auth_code = '''
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get(url, headers=headers)'''
            return command.replace('response = requests.get(url)', 'response = requests.get(url, headers=headers)')
            
        elif auth_type == 'basic':
            auth_code = '''
from requests.auth import HTTPBasicAuth
response = requests.get(url, auth=HTTPBasicAuth('username', 'password'))'''
            return command.replace('response = requests.get(url)', 
                                 'response = requests.get(url, auth=HTTPBasicAuth("username", "password"))')
                                 
        elif auth_type == 'api_key':
            header = auth.get('header', 'X-API-Key')
            return command.replace('response = requests.get(url)', 
                                 f'response = requests.get(url, headers={{"{header}": "YOUR_API_KEY"}})')
        
        return command
    
    def generate_health_check_commands(self) -> List[GeneratedCommand]:
        """Generate health check commands"""
        commands = []
        
        # cURL health check
        commands.append(GeneratedCommand(
            type=CommandType.CURL,
            command=f'curl -X GET {self.base_url}/health',
            description='Check service health',
            example_output='{"status": "healthy", "uptime": 3600, "version": "1.0.0"}',
            language=CommandLanguage.BASH
        ))
        
        # Python health check
        commands.append(GeneratedCommand(
            type=CommandType.PYTHON,
            command=f'''import requests

url = "{self.base_url}/health"
response = requests.get(url)
print(f"Status: {{response.status_code}}")
print(f"Health: {{response.json()}}")''',
            description='Python health check',
            language=CommandLanguage.PYTHON
        ))
        
        return commands
    
    def generate_metrics_commands(self) -> List[GeneratedCommand]:
        """Generate metrics/monitoring commands"""
        commands = []
        
        # Metrics endpoint
        commands.append(GeneratedCommand(
            type=CommandType.CURL,
            command=f'curl -X GET {self.base_url}/metrics',
            description='Get service metrics',
            example_output='{"requests_total": 1234, "response_time_avg": 0.05, "errors_total": 2}',
            language=CommandLanguage.BASH
        ))
        
        # Service info
        commands.append(GeneratedCommand(
            type=CommandType.CURL,
            command=f'curl -X GET {self.base_url}/info',
            description='Get service information',
            example_output='{"name": "my-service", "version": "1.0.0", "platform": "python"}',
            language=CommandLanguage.BASH
        ))
        
        return commands
    
    def generate_testing_commands(self, endpoints: List[Dict[str, Any]]) -> List[GeneratedCommand]:
        """Generate testing commands for endpoints"""
        commands = []
        
        # pytest command for API testing
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='pytest tests/test_api.py -v',
            description='Run API tests',
            example_output='test_get_users PASSED\ntest_create_user PASSED\n2 passed in 0.12s',
            language=CommandLanguage.BASH
        ))
        
        # Load testing with ab (Apache Bench)
        if endpoints:
            first_endpoint = endpoints[0]
            path = first_endpoint.get('path', '/')
            commands.append(GeneratedCommand(
                type=CommandType.SHELL,
                command=f'ab -n 1000 -c 10 {self.base_url}{path}',
                description='Load test endpoint with Apache Bench',
                example_output='Requests per second: 250.32 [#/sec]\nTime per request: 39.949 [ms]',
                language=CommandLanguage.BASH
            ))
        
        return commands


def generate_openapi_spec(manifest_data: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    """Generate OpenAPI specification from manifest"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": manifest_data.get('name', 'ProServe API'),
            "version": manifest_data.get('version', '1.0.0'),
            "description": manifest_data.get('description', 'Generated API documentation')
        },
        "servers": [
            {"url": base_url}
        ],
        "paths": {}
    }
    
    endpoints = manifest_data.get('endpoints', [])
    for endpoint in endpoints:
        path = endpoint.get('path', '/')
        method = endpoint.get('method', 'get').lower()
        
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        
        spec["paths"][path][method] = {
            "summary": f"{method.upper()} {path}",
            "description": endpoint.get('description', f'{method.upper()} endpoint for {path}'),
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }
        
        # Add request body for POST/PUT methods
        if method in ['post', 'put', 'patch']:
            spec["paths"][path][method]["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            }
    
    return spec
