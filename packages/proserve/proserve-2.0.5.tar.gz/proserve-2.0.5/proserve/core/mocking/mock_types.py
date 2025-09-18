"""
ProServe Mock Types - Mock System Data Structures
Defines mock response, endpoint, and service data structures for testing and development
"""

import json
import random
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class MockResponse:
    """Mock response configuration"""
    status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Union[Dict, List, str] = field(default_factory=dict)
    delay: float = 0.0  # Simulated delay in seconds
    probability: float = 1.0  # Probability of success (0.0-1.0)
    
    def __post_init__(self):
        """Validate mock response configuration"""
        if not 100 <= self.status <= 599:
            raise ValueError("HTTP status code must be between 100 and 599")
        if self.delay < 0:
            raise ValueError("Delay cannot be negative")
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("Probability must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'status': self.status,
            'headers': self.headers,
            'body': self.body,
            'delay': self.delay,
            'probability': self.probability
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockResponse':
        """Create from dictionary"""
        return cls(
            status=data.get('status', 200),
            headers=data.get('headers', {}),
            body=data.get('body', {}),
            delay=data.get('delay', 0.0),
            probability=data.get('probability', 1.0)
        )
    
    def is_success_response(self) -> bool:
        """Check if this is a success response (2xx status)"""
        return 200 <= self.status < 300
    
    def is_error_response(self) -> bool:
        """Check if this is an error response (4xx/5xx status)"""
        return self.status >= 400


@dataclass
class MockEndpoint:
    """Mock endpoint configuration"""
    path: str
    method: str
    responses: List[MockResponse] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    fallback_enabled: bool = True
    
    def __post_init__(self):
        """Validate mock endpoint configuration"""
        if not self.path:
            raise ValueError("Endpoint path cannot be empty")
        if not self.method:
            raise ValueError("HTTP method cannot be empty")
        self.method = self.method.upper()
        if not self.path.startswith('/'):
            self.path = '/' + self.path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'path': self.path,
            'method': self.method,
            'responses': [response.to_dict() for response in self.responses],
            'description': self.description,
            'tags': self.tags,
            'fallback_enabled': self.fallback_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockEndpoint':
        """Create from dictionary"""
        responses = [MockResponse.from_dict(resp) for resp in data.get('responses', [])]
        return cls(
            path=data['path'],
            method=data['method'],
            responses=responses,
            description=data.get('description', ''),
            tags=data.get('tags', []),
            fallback_enabled=data.get('fallback_enabled', True)
        )
    
    def add_response(self, response: MockResponse):
        """Add a mock response to this endpoint"""
        self.responses.append(response)
    
    def remove_response(self, index: int) -> bool:
        """Remove a response by index"""
        if 0 <= index < len(self.responses):
            del self.responses[index]
            return True
        return False
    
    def get_response_by_status(self, status: int) -> Optional[MockResponse]:
        """Get first response with specific status code"""
        for response in self.responses:
            if response.status == status:
                return response
        return None
    
    def get_success_responses(self) -> List[MockResponse]:
        """Get all success responses (2xx status codes)"""
        return [resp for resp in self.responses if resp.is_success_response()]
    
    def get_error_responses(self) -> List[MockResponse]:
        """Get all error responses (4xx/5xx status codes)"""
        return [resp for resp in self.responses if resp.is_error_response()]
    
    def get_endpoint_key(self) -> str:
        """Get unique key for this endpoint"""
        return f"{self.method}:{self.path}"


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
    
    def __post_init__(self):
        """Validate mock service configuration"""
        if not self.name:
            raise ValueError("Service name cannot be empty")
        if self.global_delay < 0:
            raise ValueError("Global delay cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'endpoints': [endpoint.to_dict() for endpoint in self.endpoints],
            'global_delay': self.global_delay,
            'global_headers': self.global_headers,
            'failure_simulation': self.failure_simulation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockService':
        """Create from dictionary"""
        endpoints = [MockEndpoint.from_dict(ep) for ep in data.get('endpoints', [])]
        return cls(
            name=data['name'],
            version=data.get('version', '1.0.0'),
            description=data.get('description', 'Mock service for development and testing'),
            endpoints=endpoints,
            global_delay=data.get('global_delay', 0.0),
            global_headers=data.get('global_headers', {}),
            failure_simulation=data.get('failure_simulation', {})
        )
    
    def add_endpoint(self, endpoint: MockEndpoint):
        """Add a mock endpoint to this service"""
        # Check for duplicate endpoints
        endpoint_key = endpoint.get_endpoint_key()
        existing = self.get_endpoint(endpoint.path, endpoint.method)
        if existing:
            raise ValueError(f"Endpoint {endpoint_key} already exists in service {self.name}")
        
        self.endpoints.append(endpoint)
    
    def remove_endpoint(self, path: str, method: str) -> bool:
        """Remove an endpoint by path and method"""
        method = method.upper()
        for i, endpoint in enumerate(self.endpoints):
            if endpoint.path == path and endpoint.method == method:
                del self.endpoints[i]
                return True
        return False
    
    def get_endpoint(self, path: str, method: str) -> Optional[MockEndpoint]:
        """Get endpoint by path and method"""
        method = method.upper()
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None
    
    def get_endpoints_by_path(self, path: str) -> List[MockEndpoint]:
        """Get all endpoints for a specific path"""
        return [ep for ep in self.endpoints if ep.path == path]
    
    def get_endpoints_by_method(self, method: str) -> List[MockEndpoint]:
        """Get all endpoints for a specific HTTP method"""
        method = method.upper()
        return [ep for ep in self.endpoints if ep.method == method]
    
    def get_endpoints_by_tag(self, tag: str) -> List[MockEndpoint]:
        """Get all endpoints with a specific tag"""
        return [ep for ep in self.endpoints if tag in ep.tags]
    
    def update_global_headers(self, headers: Dict[str, str]):
        """Update global headers for all responses"""
        self.global_headers.update(headers)
    
    def set_global_delay(self, delay: float):
        """Set global delay for all responses"""
        if delay < 0:
            raise ValueError("Global delay cannot be negative")
        self.global_delay = delay
    
    def enable_failure_simulation(self, failure_rate: float = 0.1, 
                                 failure_status: int = 500):
        """Enable failure simulation for testing"""
        if not 0.0 <= failure_rate <= 1.0:
            raise ValueError("Failure rate must be between 0.0 and 1.0")
        
        self.failure_simulation = {
            'enabled': True,
            'failure_rate': failure_rate,
            'failure_status': failure_status
        }
    
    def disable_failure_simulation(self):
        """Disable failure simulation"""
        self.failure_simulation = {'enabled': False}
    
    def export_to_file(self, file_path: Union[str, Path]):
        """Export service configuration to JSON file"""
        file_path = Path(file_path)
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def import_from_file(cls, file_path: Union[str, Path]) -> 'MockService':
        """Import service configuration from JSON file"""
        file_path = Path(file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class MockRequest:
    """Represents a mock request for logging purposes"""
    timestamp: datetime
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Any = None
    response_status: int = 200
    response_time: float = 0.0
    service_name: str = ""
    endpoint_matched: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'method': self.method,
            'path': self.path,
            'headers': self.headers,
            'query_params': self.query_params,
            'body': self.body,
            'response_status': self.response_status,
            'response_time': self.response_time,
            'service_name': self.service_name,
            'endpoint_matched': self.endpoint_matched
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MockRequest':
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            method=data['method'],
            path=data['path'],
            headers=data.get('headers', {}),
            query_params=data.get('query_params', {}),
            body=data.get('body'),
            response_status=data.get('response_status', 200),
            response_time=data.get('response_time', 0.0),
            service_name=data.get('service_name', ''),
            endpoint_matched=data.get('endpoint_matched', True)
        )


# Utility functions for mock data generation
def generate_sample_user_data() -> Dict[str, Any]:
    """Generate sample user data for mocking"""
    return {
        "id": random.randint(1, 1000),
        "name": f"User {random.randint(1, 100)}",
        "email": f"user{random.randint(1, 100)}@example.com",
        "age": random.randint(18, 80),
        "created_at": datetime.now().isoformat(),
        "active": random.choice([True, False])
    }


def generate_sample_product_data() -> Dict[str, Any]:
    """Generate sample product data for mocking"""
    products = ["Widget", "Gadget", "Tool", "Device", "Component"]
    return {
        "id": random.randint(1, 1000),
        "name": f"{random.choice(products)} {random.randint(1, 100)}",
        "price": round(random.uniform(10.0, 1000.0), 2),
        "category": random.choice(["electronics", "tools", "books", "clothing"]),
        "in_stock": random.choice([True, False]),
        "created_at": datetime.now().isoformat()
    }


def generate_sample_order_data() -> Dict[str, Any]:
    """Generate sample order data for mocking"""
    return {
        "id": str(uuid.uuid4()),
        "user_id": random.randint(1, 100),
        "total": round(random.uniform(20.0, 500.0), 2),
        "status": random.choice(["pending", "processing", "shipped", "delivered"]),
        "items": [
            {
                "product_id": random.randint(1, 100),
                "quantity": random.randint(1, 5),
                "price": round(random.uniform(10.0, 100.0), 2)
            }
            for _ in range(random.randint(1, 3))
        ],
        "created_at": datetime.now().isoformat()
    }


def create_error_response(status: int, message: str) -> MockResponse:
    """Create a standard error response"""
    return MockResponse(
        status=status,
        body={
            "error": {
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
    )


def create_success_response(data: Any = None, status: int = 200) -> MockResponse:
    """Create a standard success response"""
    body = data if data is not None else {"message": "Success"}
    return MockResponse(status=status, body=body)


def create_paginated_response(items: List[Any], page: int = 1, 
                            per_page: int = 10, total: int = None) -> MockResponse:
    """Create a paginated response"""
    total = total or len(items)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]
    
    return MockResponse(
        status=200,
        body={
            "data": page_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    )
