"""
ProServe Service Alternatives and MOCK System
Provides fallback mechanisms for failed services with JSON demo responses
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from pathlib import Path
from aiohttp import web
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import random


@dataclass
class MockResponse:
    """Mock response configuration"""
    status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Union[Dict, List, str] = field(default_factory=dict)
    delay: float = 0.0  # Simulated delay in seconds
    probability: float = 1.0  # Probability of success (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'headers': self.headers,
            'body': self.body,
            'delay': self.delay,
            'probability': self.probability
        }


@dataclass
class MockEndpoint:
    """Mock endpoint configuration"""
    path: str
    method: str
    responses: List[MockResponse] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    fallback_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'method': self.method,
            'responses': [resp.to_dict() for resp in self.responses],
            'description': self.description,
            'tags': self.tags,
            'fallback_enabled': self.fallback_enabled
        }


@dataclass
class MockService:
    """Mock service configuration"""
    name: str
    version: str = "1.0.0"
    description: str = "Mock service for development and testing"
    endpoints: List[MockEndpoint] = field(default_factory=list)
    global_delay: float = 0.0
    global_headers: Dict[str, str] = field(default_factory=dict)
    failure_simulation: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'endpoints': [ep.to_dict() for ep in self.endpoints],
            'global_delay': self.global_delay,
            'global_headers': self.global_headers,
            'failure_simulation': self.failure_simulation
        }


class MockSystemManager:
    """Manages service alternatives and mock responses"""
    
    def __init__(self, mock_data_dir: Path = None):
        self.mock_data_dir = mock_data_dir or Path('mock_data')
        self.mock_data_dir.mkdir(exist_ok=True)
        
        self.mock_services: Dict[str, MockService] = {}
        self.active_mocks: Dict[str, bool] = {}  # endpoint_key -> enabled
        self.request_logs: List[Dict[str, Any]] = []
        self.max_log_size = 1000
        
        self.logger = logging.getLogger(__name__)
        
        # Load existing mock configurations
        self._load_mock_configurations()
        
        # Create default demo data
        self._ensure_demo_data()
    
    def _load_mock_configurations(self):
        """Load mock configurations from JSON files"""
        for mock_file in self.mock_data_dir.glob('*.json'):
            try:
                with open(mock_file, 'r') as f:
                    data = json.load(f)
                
                # Parse mock service configuration
                service = self._parse_mock_service(data)
                self.mock_services[service.name] = service
                
                self.logger.info(f"Loaded mock service: {service.name}")
                
            except Exception as e:
                self.logger.error(f"Error loading mock config {mock_file}: {e}")
    
    def _parse_mock_service(self, data: Dict[str, Any]) -> MockService:
        """Parse mock service from configuration data"""
        endpoints = []
        
        for ep_data in data.get('endpoints', []):
            responses = []
            for resp_data in ep_data.get('responses', []):
                response = MockResponse(
                    status=resp_data.get('status', 200),
                    headers=resp_data.get('headers', {}),
                    body=resp_data.get('body', {}),
                    delay=resp_data.get('delay', 0.0),
                    probability=resp_data.get('probability', 1.0)
                )
                responses.append(response)
            
            endpoint = MockEndpoint(
                path=ep_data['path'],
                method=ep_data['method'].upper(),
                responses=responses,
                description=ep_data.get('description', ''),
                tags=ep_data.get('tags', []),
                fallback_enabled=ep_data.get('fallback_enabled', True)
            )
            endpoints.append(endpoint)
        
        return MockService(
            name=data['name'],
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            endpoints=endpoints,
            global_delay=data.get('global_delay', 0.0),
            global_headers=data.get('global_headers', {}),
            failure_simulation=data.get('failure_simulation', {})
        )
    
    def _ensure_demo_data(self):
        """Create demo mock data if none exists"""
        demo_files = [
            ('user_service_mock.json', self._create_user_service_mock),
            ('system_service_mock.json', self._create_system_service_mock),
            ('health_service_mock.json', self._create_health_service_mock),
            ('grpc_service_mock.json', self._create_grpc_service_mock)
        ]
        
        for filename, creator_func in demo_files:
            mock_file = self.mock_data_dir / filename
            if not mock_file.exists():
                try:
                    mock_data = creator_func()
                    with open(mock_file, 'w') as f:
                        json.dump(mock_data, f, indent=2)
                    
                    self.logger.info(f"Created demo mock file: {filename}")
                    
                    # Load the created mock
                    service = self._parse_mock_service(mock_data)
                    self.mock_services[service.name] = service
                    
                except Exception as e:
                    self.logger.error(f"Error creating demo mock {filename}: {e}")
    
    def _create_user_service_mock(self) -> Dict[str, Any]:
        """Create demo user service mock"""
        return {
            "name": "user-service-mock",
            "version": "1.0.0",
            "description": "Mock user service for development and testing",
            "global_delay": 0.1,
            "global_headers": {
                "X-Mock-Service": "user-service",
                "X-Mock-Version": "1.0.0"
            },
            "endpoints": [
                {
                    "path": "/api/users",
                    "method": "GET",
                    "description": "List all users",
                    "tags": ["users", "list"],
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "users": [
                                    {
                                        "id": 1,
                                        "name": "John Doe",
                                        "email": "john@example.com",
                                        "role": "admin",
                                        "created_at": "2024-01-15T10:30:00Z",
                                        "last_login": "2024-01-20T14:22:33Z"
                                    },
                                    {
                                        "id": 2,
                                        "name": "Jane Smith",
                                        "email": "jane@example.com",
                                        "role": "user",
                                        "created_at": "2024-01-16T09:15:00Z",
                                        "last_login": "2024-01-19T16:45:12Z"
                                    },
                                    {
                                        "id": 3,
                                        "name": "Bob Wilson",
                                        "email": "bob@example.com",
                                        "role": "user",
                                        "created_at": "2024-01-17T11:20:00Z",
                                        "last_login": "2024-01-18T13:30:45Z"
                                    }
                                ],
                                "total": 3,
                                "page": 1,
                                "per_page": 10
                            },
                            "delay": 0.2
                        }
                    ]
                },
                {
                    "path": "/api/users",
                    "method": "POST",
                    "description": "Create new user",
                    "tags": ["users", "create"],
                    "responses": [
                        {
                            "status": 201,
                            "body": {
                                "id": 4,
                                "name": "New User",
                                "email": "newuser@example.com",
                                "role": "user",
                                "created_at": "2024-01-21T12:00:00Z",
                                "last_login": null
                            },
                            "delay": 0.3
                        },
                        {
                            "status": 400,
                            "body": {
                                "error": "validation_error",
                                "message": "Invalid email format",
                                "field": "email"
                            },
                            "probability": 0.1
                        }
                    ]
                },
                {
                    "path": "/api/users/{user_id}",
                    "method": "GET",
                    "description": "Get user by ID",
                    "tags": ["users", "get"],
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "id": 1,
                                "name": "John Doe",
                                "email": "john@example.com",
                                "role": "admin",
                                "created_at": "2024-01-15T10:30:00Z",
                                "last_login": "2024-01-20T14:22:33Z",
                                "profile": {
                                    "avatar": "https://example.com/avatars/john.jpg",
                                    "bio": "System administrator",
                                    "location": "San Francisco, CA"
                                }
                            }
                        },
                        {
                            "status": 404,
                            "body": {
                                "error": "user_not_found",
                                "message": "User with ID {user_id} not found"
                            },
                            "probability": 0.2
                        }
                    ]
                },
                {
                    "path": "/api/users/{user_id}",
                    "method": "PUT",
                    "description": "Update user",
                    "tags": ["users", "update"],
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "id": 1,
                                "name": "John Doe Updated",
                                "email": "john.updated@example.com",
                                "role": "admin",
                                "updated_at": "2024-01-21T15:45:00Z"
                            }
                        }
                    ]
                },
                {
                    "path": "/api/users/{user_id}",
                    "method": "DELETE",
                    "description": "Delete user",
                    "tags": ["users", "delete"],
                    "responses": [
                        {
                            "status": 204,
                            "body": ""
                        },
                        {
                            "status": 403,
                            "body": {
                                "error": "permission_denied",
                                "message": "Cannot delete admin user"
                            },
                            "probability": 0.15
                        }
                    ]
                }
            ]
        }
    
    def _create_system_service_mock(self) -> Dict[str, Any]:
        """Create demo system service mock"""
        return {
            "name": "system-service-mock",
            "version": "1.0.0",
            "description": "Mock system service for shell commands and system info",
            "global_delay": 0.05,
            "endpoints": [
                {
                    "path": "/api/system/info",
                    "method": "GET",
                    "description": "Get system information",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "hostname": "mock-server",
                                "platform": "Linux",
                                "architecture": "x86_64",
                                "kernel": "5.15.0-generic",
                                "uptime": "7 days, 14:32:15",
                                "load_average": [0.15, 0.25, 0.18],
                                "memory": {
                                    "total": "16.0 GB",
                                    "used": "8.2 GB",
                                    "free": "7.8 GB",
                                    "usage_percent": 51.25
                                },
                                "disk": {
                                    "total": "500 GB",
                                    "used": "180 GB",
                                    "free": "320 GB",
                                    "usage_percent": 36.0
                                },
                                "cpu": {
                                    "cores": 8,
                                    "model": "Intel Core i7-10700K",
                                    "usage_percent": 23.5
                                }
                            }
                        }
                    ]
                },
                {
                    "path": "/api/system/processes",
                    "method": "GET",
                    "description": "List running processes",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "processes": [
                                    {
                                        "pid": 1,
                                        "name": "systemd",
                                        "cpu_percent": 0.1,
                                        "memory_percent": 0.2,
                                        "status": "running"
                                    },
                                    {
                                        "pid": 1234,
                                        "name": "proserve",
                                        "cpu_percent": 2.5,
                                        "memory_percent": 1.8,
                                        "status": "running"
                                    },
                                    {
                                        "pid": 5678,
                                        "name": "python3",
                                        "cpu_percent": 1.2,
                                        "memory_percent": 3.4,
                                        "status": "running"
                                    }
                                ],
                                "total_processes": 156,
                                "running": 142,
                                "sleeping": 14
                            },
                            "delay": 0.5
                        }
                    ]
                },
                {
                    "path": "/api/system/execute",
                    "method": "POST",
                    "description": "Execute shell command",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "command": "ps aux | head -5",
                                "exit_code": 0,
                                "stdout": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.1  22548  1234 ?        Ss   Jan15   0:01 /sbin/init\nroot         2  0.0  0.0      0     0 ?        S    Jan15   0:00 [kthreadd]\nroot         3  0.0  0.0      0     0 ?        I<   Jan15   0:00 [rcu_gp]\nroot         4  0.0  0.0      0     0 ?        I<   Jan15   0:00 [rcu_par_gp]",
                                "stderr": "",
                                "execution_time": 0.123
                            },
                            "delay": 0.8
                        },
                        {
                            "status": 403,
                            "body": {
                                "error": "command_not_allowed",
                                "message": "Command not in whitelist"
                            },
                            "probability": 0.1
                        }
                    ]
                }
            ]
        }
    
    def _create_health_service_mock(self) -> Dict[str, Any]:
        """Create demo health service mock"""
        return {
            "name": "health-service-mock",
            "version": "1.0.0",
            "description": "Mock health check service",
            "endpoints": [
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "Health check endpoint",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "status": "healthy",
                                "timestamp": "2024-01-21T12:00:00Z",
                                "version": "1.0.0",
                                "uptime": "7d 14h 32m",
                                "checks": {
                                    "database": "healthy",
                                    "cache": "healthy",
                                    "external_api": "healthy"
                                },
                                "metrics": {
                                    "requests_per_second": 15.2,
                                    "average_response_time": 0.045,
                                    "error_rate": 0.001
                                }
                            }
                        },
                        {
                            "status": 503,
                            "body": {
                                "status": "unhealthy",
                                "timestamp": "2024-01-21T12:00:00Z",
                                "version": "1.0.0",
                                "checks": {
                                    "database": "unhealthy",
                                    "cache": "healthy",
                                    "external_api": "degraded"
                                },
                                "errors": [
                                    "Database connection timeout",
                                    "External API slow response"
                                ]
                            },
                            "probability": 0.05
                        }
                    ]
                }
            ]
        }
    
    def _create_grpc_service_mock(self) -> Dict[str, Any]:
        """Create demo gRPC service mock (HTTP representation)"""
        return {
            "name": "grpc-service-mock",
            "version": "1.0.0",
            "description": "Mock gRPC service with HTTP fallback endpoints",
            "endpoints": [
                {
                    "path": "/grpc/UserService/GetUser",
                    "method": "POST",
                    "description": "gRPC UserService.GetUser via HTTP",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "id": "123",
                                "name": "gRPC User",
                                "email": "grpc@example.com",
                                "metadata": {
                                    "grpc_method": "GetUser",
                                    "service": "UserService"
                                }
                            }
                        }
                    ]
                },
                {
                    "path": "/grpc/SystemService/GetSystemInfo",
                    "method": "POST",
                    "description": "gRPC SystemService.GetSystemInfo via HTTP",
                    "responses": [
                        {
                            "status": 200,
                            "body": {
                                "hostname": "grpc-mock-server",
                                "version": "1.0.0",
                                "uptime_seconds": 604800,
                                "grpc_services": [
                                    "UserService",
                                    "SystemService"
                                ],
                                "metadata": {
                                    "grpc_method": "GetSystemInfo",
                                    "service": "SystemService"
                                }
                            }
                        }
                    ]
                }
            ]
        }
    
    async def create_mock_handler(self, endpoint: MockEndpoint) -> Callable:
        """Create an aiohttp handler for a mock endpoint"""
        async def mock_handler(request: web.Request) -> web.Response:
            # Log the request
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'path': str(request.url.path),
                'query': dict(request.query),
                'headers': dict(request.headers),
                'endpoint': f"{endpoint.method} {endpoint.path}",
                'mock_service': True
            }
            
            # Add request body if present
            if request.content_type and 'json' in request.content_type:
                try:
                    log_entry['body'] = await request.json()
                except:
                    pass
            
            self.request_logs.append(log_entry)
            
            # Trim logs if too large
            if len(self.request_logs) > self.max_log_size:
                self.request_logs = self.request_logs[-self.max_log_size:]
            
            # Select response based on probability
            available_responses = [r for r in endpoint.responses if r.probability > 0]
            if not available_responses:
                return web.json_response(
                    {'error': 'no_mock_responses', 'message': 'No mock responses configured'},
                    status=500
                )
            
            # Weighted random selection based on probability
            weights = [r.probability for r in available_responses]
            selected_response = random.choices(available_responses, weights=weights)[0]
            
            # Apply delay
            total_delay = selected_response.delay
            if hasattr(self, 'current_service'):
                total_delay += self.current_service.global_delay
            
            if total_delay > 0:
                await asyncio.sleep(total_delay)
            
            # Prepare headers
            headers = {}
            if hasattr(self, 'current_service'):
                headers.update(self.current_service.global_headers)
            headers.update(selected_response.headers)
            headers['X-Mock-Response'] = 'true'
            headers['X-Mock-Endpoint'] = f"{endpoint.method} {endpoint.path}"
            
            # Return response
            if isinstance(selected_response.body, str):
                return web.Response(
                    text=selected_response.body,
                    status=selected_response.status,
                    headers=headers
                )
            else:
                return web.json_response(
                    selected_response.body,
                    status=selected_response.status,
                    headers=headers
                )
        
        return mock_handler
    
    def get_mock_service(self, service_name: str) -> Optional[MockService]:
        """Get mock service by name"""
        return self.mock_services.get(service_name)
    
    def list_mock_services(self) -> List[str]:
        """List available mock service names"""
        return list(self.mock_services.keys())
    
    def get_request_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request logs"""
        return self.request_logs[-limit:]
    
    def clear_request_logs(self):
        """Clear request logs"""
        self.request_logs.clear()
    
    def export_mock_configuration(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Export mock service configuration"""
        service = self.mock_services.get(service_name)
        return service.to_dict() if service else None
    
    def import_mock_configuration(self, config: Dict[str, Any]) -> bool:
        """Import mock service configuration"""
        try:
            service = self._parse_mock_service(config)
            self.mock_services[service.name] = service
            
            # Save to file
            config_file = self.mock_data_dir / f"{service.name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error importing mock configuration: {e}")
            return False
    
    def get_mock_stats(self) -> Dict[str, Any]:
        """Get mock system statistics"""
        total_endpoints = sum(len(service.endpoints) for service in self.mock_services.values())
        total_responses = sum(
            len(endpoint.responses) 
            for service in self.mock_services.values() 
            for endpoint in service.endpoints
        )
        
        return {
            'services': len(self.mock_services),
            'endpoints': total_endpoints,
            'responses': total_responses,
            'request_logs': len(self.request_logs),
            'mock_data_dir': str(self.mock_data_dir)
        }


# Global mock system instance
_mock_system: Optional[MockSystemManager] = None

def get_mock_system(mock_data_dir: Path = None) -> MockSystemManager:
    """Get or create global mock system instance"""
    global _mock_system
    if _mock_system is None:
        _mock_system = MockSystemManager(mock_data_dir)
    return _mock_system
