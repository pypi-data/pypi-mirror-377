"""
ProServe Mock Handler - Mock Request Processing and Response Generation
Handles mock HTTP requests and generates appropriate responses based on mock configurations
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from aiohttp import web
import structlog

from .mock_types import MockService, MockEndpoint, MockResponse, MockRequest


logger = structlog.get_logger(__name__)


class MockRequestHandler:
    """Handles mock HTTP requests and generates responses"""
    
    def __init__(self):
        self.request_count = 0
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def handle_request(self, request: web.Request, 
                           mock_service: MockService) -> web.Response:
        """Handle incoming mock request and return appropriate response"""
        self.request_count += 1
        start_time = time.time()
        
        # Extract request information
        method = request.method.upper()
        path = request.path
        headers = dict(request.headers)
        query_params = dict(request.query)
        
        try:
            # Get request body if present
            body = None
            if method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = await request.json()
                except Exception:
                    try:
                        body = await request.text()
                    except Exception:
                        body = None
            
            # Find matching endpoint
            endpoint = self._find_matching_endpoint(mock_service, method, path)
            
            if not endpoint:
                # No matching endpoint found
                response_time = time.time() - start_time
                mock_request = MockRequest(
                    timestamp=datetime.now(),
                    method=method,
                    path=path,
                    headers=headers,
                    query_params=query_params,
                    body=body,
                    response_status=404,
                    response_time=response_time,
                    service_name=mock_service.name,
                    endpoint_matched=False
                )
                
                return self._create_not_found_response()
            
            # Check if endpoint is enabled for fallback
            if not endpoint.fallback_enabled:
                response_time = time.time() - start_time
                mock_request = MockRequest(
                    timestamp=datetime.now(),
                    method=method,
                    path=path,
                    headers=headers,
                    query_params=query_params,
                    body=body,
                    response_status=503,
                    response_time=response_time,
                    service_name=mock_service.name,
                    endpoint_matched=True
                )
                
                return self._create_service_unavailable_response()
            
            # Generate mock response
            mock_response = await self._generate_mock_response(
                endpoint, mock_service, request, body
            )
            
            # Apply global delay
            total_delay = mock_service.global_delay + mock_response.delay
            if total_delay > 0:
                await asyncio.sleep(total_delay)
            
            # Create web response
            web_response = await self._create_web_response(
                mock_response, mock_service.global_headers
            )
            
            response_time = time.time() - start_time
            
            # Log the request
            mock_request = MockRequest(
                timestamp=datetime.now(),
                method=method,
                path=path,
                headers=headers,
                query_params=query_params,
                body=body,
                response_status=mock_response.status,
                response_time=response_time,
                service_name=mock_service.name,
                endpoint_matched=True
            )
            
            logger.info("Mock request processed", 
                       service=mock_service.name,
                       method=method,
                       path=path,
                       status=mock_response.status,
                       response_time=response_time)
            
            return web_response
            
        except Exception as e:
            logger.error("Error handling mock request", 
                        error=str(e), 
                        service=mock_service.name,
                        method=method,
                        path=path)
            
            return self._create_error_response(500, "Internal mock system error")
    
    def _find_matching_endpoint(self, mock_service: MockService, 
                              method: str, path: str) -> Optional[MockEndpoint]:
        """Find matching endpoint for request"""
        # First try exact match
        for endpoint in mock_service.endpoints:
            if endpoint.method == method and endpoint.path == path:
                return endpoint
        
        # Try pattern matching for parameterized paths
        for endpoint in mock_service.endpoints:
            if endpoint.method == method and self._path_matches_pattern(path, endpoint.path):
                return endpoint
        
        return None
    
    def _path_matches_pattern(self, actual_path: str, pattern_path: str) -> bool:
        """Check if actual path matches pattern with parameters"""
        # Simple pattern matching - supports {param} style parameters
        actual_parts = actual_path.strip('/').split('/')
        pattern_parts = pattern_path.strip('/').split('/')
        
        if len(actual_parts) != len(pattern_parts):
            return False
        
        for actual, pattern in zip(actual_parts, pattern_parts):
            # If pattern part is a parameter (starts with {), it matches anything
            if pattern.startswith('{') and pattern.endswith('}'):
                continue
            # Otherwise, must be exact match
            elif actual != pattern:
                return False
        
        return True
    
    async def _generate_mock_response(self, endpoint: MockEndpoint, 
                                    mock_service: MockService,
                                    request: web.Request,
                                    body: Any) -> MockResponse:
        """Generate mock response for endpoint"""
        # Check if failure simulation is enabled
        failure_sim = mock_service.failure_simulation
        if failure_sim.get('enabled', False):
            failure_rate = failure_sim.get('failure_rate', 0.1)
            if random.random() < failure_rate:
                failure_status = failure_sim.get('failure_status', 500)
                return MockResponse(
                    status=failure_status,
                    body={"error": "Simulated failure", "code": failure_status}
                )
        
        # If no responses defined, create a default one
        if not endpoint.responses:
            return self._create_default_response(endpoint, request, body)
        
        # Select response based on probability
        available_responses = []
        for response in endpoint.responses:
            if random.random() < response.probability:
                available_responses.append(response)
        
        # If no responses passed probability check, use the first one
        if not available_responses:
            available_responses = endpoint.responses[:1]
        
        # Select random response from available ones
        selected_response = random.choice(available_responses)
        
        # Process dynamic content in response
        processed_response = await self._process_dynamic_content(
            selected_response, endpoint, request, body
        )
        
        return processed_response
    
    def _create_default_response(self, endpoint: MockEndpoint, 
                               request: web.Request, body: Any) -> MockResponse:
        """Create default response when none configured"""
        method = endpoint.method
        
        if method == 'GET':
            if '{' in endpoint.path:  # Single item endpoint
                return MockResponse(
                    status=200,
                    body={"id": 1, "message": f"Mock response for {endpoint.path}"}
                )
            else:  # Collection endpoint
                return MockResponse(
                    status=200,
                    body={
                        "items": [
                            {"id": 1, "name": "Item 1"},
                            {"id": 2, "name": "Item 2"}
                        ],
                        "total": 2
                    }
                )
        
        elif method == 'POST':
            return MockResponse(
                status=201,
                body={
                    "id": random.randint(1, 1000),
                    "message": "Created successfully",
                    "created_at": datetime.now().isoformat()
                }
            )
        
        elif method == 'PUT':
            return MockResponse(
                status=200,
                body={
                    "message": "Updated successfully",
                    "updated_at": datetime.now().isoformat()
                }
            )
        
        elif method == 'DELETE':
            return MockResponse(
                status=200,
                body={"message": "Deleted successfully"}
            )
        
        else:
            return MockResponse(
                status=200,
                body={"message": f"Mock response for {method} {endpoint.path}"}
            )
    
    async def _process_dynamic_content(self, response: MockResponse,
                                     endpoint: MockEndpoint,
                                     request: web.Request,
                                     body: Any) -> MockResponse:
        """Process dynamic content in mock response"""
        # Clone the response to avoid modifying the original
        processed_response = MockResponse(
            status=response.status,
            headers=response.headers.copy(),
            body=self._process_response_body(response.body, request, body),
            delay=response.delay,
            probability=response.probability
        )
        
        return processed_response
    
    def _process_response_body(self, body: Any, request: web.Request, 
                             request_body: Any) -> Any:
        """Process dynamic placeholders in response body"""
        if isinstance(body, dict):
            processed = {}
            for key, value in body.items():
                processed[key] = self._process_response_body(value, request, request_body)
            return processed
        
        elif isinstance(body, list):
            return [self._process_response_body(item, request, request_body) for item in body]
        
        elif isinstance(body, str):
            # Replace common placeholders
            processed = body
            processed = processed.replace('{{timestamp}}', datetime.now().isoformat())
            processed = processed.replace('{{random_id}}', str(random.randint(1, 1000)))
            processed = processed.replace('{{request_id}}', f"req_{self.request_count}")
            
            # Extract path parameters if present
            path_params = self._extract_path_parameters(request.path, request.match_info)
            for param_name, param_value in path_params.items():
                processed = processed.replace(f'{{{param_name}}}', str(param_value))
            
            return processed
        
        else:
            return body
    
    def _extract_path_parameters(self, path: str, match_info: dict) -> Dict[str, str]:
        """Extract path parameters from request"""
        params = {}
        
        # Add match_info parameters
        if match_info:
            params.update(match_info)
        
        # Extract numeric IDs from path segments
        path_parts = path.strip('/').split('/')
        for i, part in enumerate(path_parts):
            if part.isdigit():
                params[f'id_{i}'] = part
                params['id'] = part  # Common case
        
        return params
    
    async def _create_web_response(self, mock_response: MockResponse,
                                 global_headers: Dict[str, str]) -> web.Response:
        """Create aiohttp web response from mock response"""
        # Merge headers
        response_headers = global_headers.copy()
        response_headers.update(mock_response.headers)
        
        # Set default content type if not specified
        if 'Content-Type' not in response_headers:
            if isinstance(mock_response.body, (dict, list)):
                response_headers['Content-Type'] = 'application/json'
            else:
                response_headers['Content-Type'] = 'text/plain'
        
        # Add mock system headers
        response_headers['X-Mock-Service'] = 'ProServe'
        response_headers['X-Mock-Timestamp'] = datetime.now().isoformat()
        response_headers['X-Mock-Request-Count'] = str(self.request_count)
        
        # Create response body
        if isinstance(mock_response.body, (dict, list)):
            body = json.dumps(mock_response.body, indent=2, default=str)
        else:
            body = str(mock_response.body)
        
        return web.Response(
            text=body,
            status=mock_response.status,
            headers=response_headers
        )
    
    def _create_not_found_response(self) -> web.Response:
        """Create 404 Not Found response"""
        body = {
            "error": "Endpoint not found",
            "message": "No mock endpoint matches this request",
            "timestamp": datetime.now().isoformat()
        }
        
        return web.Response(
            text=json.dumps(body, indent=2),
            status=404,
            headers={
                'Content-Type': 'application/json',
                'X-Mock-Service': 'ProServe'
            }
        )
    
    def _create_service_unavailable_response(self) -> web.Response:
        """Create 503 Service Unavailable response"""
        body = {
            "error": "Service unavailable",
            "message": "Mock endpoint is disabled for fallback",
            "timestamp": datetime.now().isoformat()
        }
        
        return web.Response(
            text=json.dumps(body, indent=2),
            status=503,
            headers={
                'Content-Type': 'application/json',
                'X-Mock-Service': 'ProServe'
            }
        )
    
    def _create_error_response(self, status: int, message: str) -> web.Response:
        """Create error response"""
        body = {
            "error": "Mock system error",
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        return web.Response(
            text=json.dumps(body, indent=2),
            status=status,
            headers={
                'Content-Type': 'application/json',
                'X-Mock-Service': 'ProServe'
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return {
            'total_requests': self.request_count,
            'cache_entries': len(self.response_cache),
            'cache_ttl': self.cache_ttl
        }
    
    def reset_stats(self):
        """Reset handler statistics"""
        self.request_count = 0
        self.response_cache.clear()


def create_mock_handler_for_service(mock_service: MockService) -> callable:
    """Create an aiohttp handler function for a mock service"""
    handler = MockRequestHandler()
    
    async def mock_handler(request: web.Request) -> web.Response:
        """aiohttp handler function for mock requests"""
        return await handler.handle_request(request, mock_service)
    
    # Store handler instance for stats access
    mock_handler._handler_instance = handler
    return mock_handler


def create_mock_handler_for_endpoint(endpoint: MockEndpoint, 
                                   service_name: str = "mock") -> callable:
    """Create an aiohttp handler function for a single mock endpoint"""
    # Create a minimal mock service with just this endpoint
    mock_service = MockService(
        name=service_name,
        endpoints=[endpoint]
    )
    
    return create_mock_handler_for_service(mock_service)
