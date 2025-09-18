"""
ProServe Service Fallback Integration
Integrates mock system with main service for automatic failover
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING
from aiohttp import web
from pathlib import Path

from .mock_system import MockSystemManager, get_mock_system

if TYPE_CHECKING:
    from .service import ProServeService


class ServiceFallbackManager:
    """Manages service fallbacks and automatic mock activation"""
    
    def __init__(self, service: "ProServeService", enable_auto_fallback: bool = True):
        self.service = service
        self.enable_auto_fallback = enable_auto_fallback
        self.logger = logging.getLogger(__name__)
        
        # Initialize mock system
        mock_data_dir = Path(service.manifest._manifest_path).parent / 'mock_data'
        self.mock_system = get_mock_system(mock_data_dir)
        
        # Track failed endpoints
        self.failed_endpoints: Dict[str, int] = {}  # endpoint_key -> failure_count
        self.fallback_active: Dict[str, bool] = {}  # endpoint_key -> is_fallback_active
        self.max_failures = 3  # Max failures before activating fallback
        
        # Fallback configuration from manifest
        self.fallback_config = service.manifest.deployment.get('fallback', {})
        if self.fallback_config.get('enabled', True):
            self.enable_auto_fallback = True
    
    async def wrap_endpoint_handler(self, original_handler: Callable, endpoint_key: str) -> Callable:
        """Wrap an endpoint handler with fallback logic"""
        
        async def fallback_wrapper(request: web.Request) -> web.Response:
            # Check if fallback is already active for this endpoint
            if self.fallback_active.get(endpoint_key, False):
                return await self._execute_fallback(request, endpoint_key)
            
            try:
                # Try original handler
                response = await original_handler(request)
                
                # Reset failure count on success
                if endpoint_key in self.failed_endpoints:
                    self.failed_endpoints[endpoint_key] = 0
                    self.logger.info(f"Endpoint {endpoint_key} recovered, failure count reset")
                
                return response
                
            except Exception as e:
                # Increment failure count
                self.failed_endpoints[endpoint_key] = self.failed_endpoints.get(endpoint_key, 0) + 1
                failure_count = self.failed_endpoints[endpoint_key]
                
                self.logger.warning(f"Endpoint {endpoint_key} failed (count: {failure_count}): {e}")
                
                # Check if we should activate fallback
                if self.enable_auto_fallback and failure_count >= self.max_failures:
                    self.fallback_active[endpoint_key] = True
                    self.logger.error(f"Activating fallback for {endpoint_key} after {failure_count} failures")
                    
                    return await self._execute_fallback(request, endpoint_key)
                else:
                    # Re-raise the exception if fallback not activated
                    raise
        
        return fallback_wrapper
    
    async def _execute_fallback(self, request: web.Request, endpoint_key: str) -> web.Response:
        """Execute fallback mock response for failed endpoint"""
        
        try:
            # Extract method and path from endpoint_key
            method, path = endpoint_key.split(' ', 1)
            
            # Find matching mock endpoint
            mock_endpoint = self._find_mock_endpoint(method, path)
            
            if mock_endpoint:
                # Create mock handler and execute it
                mock_handler = await self.mock_system.create_mock_handler(mock_endpoint)
                self.mock_system.current_service = self.mock_system.get_mock_service(
                    self._get_service_name_for_endpoint(path)
                )
                
                response = await mock_handler(request)
                
                # Add fallback headers
                response.headers['X-Fallback-Active'] = 'true'
                response.headers['X-Original-Endpoint'] = endpoint_key
                
                return response
            else:
                # No mock found, return generic fallback response
                return await self._generic_fallback_response(request, endpoint_key)
                
        except Exception as e:
            self.logger.error(f"Fallback execution failed for {endpoint_key}: {e}")
            return await self._generic_fallback_response(request, endpoint_key)
    
    def _find_mock_endpoint(self, method: str, path: str):
        """Find matching mock endpoint for method and path"""
        
        for service_name, mock_service in self.mock_system.mock_services.items():
            for endpoint in mock_service.endpoints:
                if endpoint.method.upper() == method.upper():
                    # Simple path matching (could be enhanced with path parameters)
                    if endpoint.path == path or self._path_matches(endpoint.path, path):
                        return endpoint
        
        return None
    
    def _path_matches(self, pattern: str, path: str) -> bool:
        """Check if path matches pattern (with path parameters)"""
        # Simple pattern matching for {param} style parameters
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False
        
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                continue  # Path parameter, matches anything
            elif pattern_part != path_part:
                return False
        
        return True
    
    def _get_service_name_for_endpoint(self, path: str) -> str:
        """Determine service name based on endpoint path"""
        if '/api/users' in path:
            return 'user-service-mock'
        elif '/api/system' in path:
            return 'system-service-mock'
        elif '/health' in path:
            return 'health-service-mock'
        elif '/grpc/' in path:
            return 'grpc-service-mock'
        else:
            return 'user-service-mock'  # Default fallback
    
    async def _generic_fallback_response(self, request: web.Request, endpoint_key: str) -> web.Response:
        """Generate generic fallback response when no mock is available"""
        
        method, path = endpoint_key.split(' ', 1)
        
        fallback_data = {
            'status': 'service_unavailable',
            'message': 'Original service is temporarily unavailable',
            'endpoint': endpoint_key,
            'fallback_type': 'generic',
            'timestamp': asyncio.get_event_loop().time(),
            'retry_after': 300  # 5 minutes
        }
        
        # Add some endpoint-specific mock data
        if 'users' in path:
            if method == 'GET' and path.endswith('/users'):
                fallback_data['data'] = {
                    'users': [],
                    'total': 0,
                    'message': 'User service unavailable'
                }
            elif method == 'POST':
                fallback_data['data'] = {
                    'id': 'temp_id',
                    'status': 'pending',
                    'message': 'User creation queued for retry'
                }
        elif 'health' in path:
            fallback_data['data'] = {
                'status': 'degraded',
                'checks': {'main_service': 'unhealthy'},
                'fallback_active': True
            }
        elif 'system' in path:
            fallback_data['data'] = {
                'system_info': 'unavailable',
                'fallback_mode': True
            }
        
        return web.json_response(
            fallback_data,
            status=503,
            headers={
                'X-Fallback-Active': 'true',
                'X-Fallback-Type': 'generic',
                'X-Original-Endpoint': endpoint_key,
                'Retry-After': '300'
            }
        )
    
    def manually_activate_fallback(self, endpoint_key: str) -> bool:
        """Manually activate fallback for an endpoint"""
        try:
            self.fallback_active[endpoint_key] = True
            self.logger.info(f"Manually activated fallback for {endpoint_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error activating fallback for {endpoint_key}: {e}")
            return False
    
    def manually_deactivate_fallback(self, endpoint_key: str) -> bool:
        """Manually deactivate fallback for an endpoint"""
        try:
            self.fallback_active[endpoint_key] = False
            self.failed_endpoints[endpoint_key] = 0  # Reset failure count
            self.logger.info(f"Manually deactivated fallback for {endpoint_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error deactivating fallback for {endpoint_key}: {e}")
            return False
    
    def get_fallback_status(self) -> Dict[str, Any]:
        """Get current fallback status"""
        return {
            'auto_fallback_enabled': self.enable_auto_fallback,
            'max_failures': self.max_failures,
            'failed_endpoints': dict(self.failed_endpoints),
            'active_fallbacks': dict(self.fallback_active),
            'mock_services': self.mock_system.list_mock_services(),
            'mock_stats': self.mock_system.get_mock_stats()
        }
    
    def reset_all_fallbacks(self):
        """Reset all fallback states"""
        self.failed_endpoints.clear()
        self.fallback_active.clear()
        self.logger.info("Reset all fallback states")
    
    async def setup_management_endpoints(self, app: web.Application):
        """Setup management endpoints for fallback control"""
        
        async def get_fallback_status(request: web.Request) -> web.Response:
            """Get fallback system status"""
            return web.json_response(self.get_fallback_status())
        
        async def activate_fallback(request: web.Request) -> web.Response:
            """Manually activate fallback for endpoint"""
            data = await request.json()
            endpoint_key = data.get('endpoint_key')
            
            if not endpoint_key:
                return web.json_response(
                    {'error': 'endpoint_key required'}, 
                    status=400
                )
            
            success = self.manually_activate_fallback(endpoint_key)
            return web.json_response({
                'success': success,
                'endpoint_key': endpoint_key,
                'fallback_active': self.fallback_active.get(endpoint_key, False)
            })
        
        async def deactivate_fallback(request: web.Request) -> web.Response:
            """Manually deactivate fallback for endpoint"""
            data = await request.json()
            endpoint_key = data.get('endpoint_key')
            
            if not endpoint_key:
                return web.json_response(
                    {'error': 'endpoint_key required'}, 
                    status=400
                )
            
            success = self.manually_deactivate_fallback(endpoint_key)
            return web.json_response({
                'success': success,
                'endpoint_key': endpoint_key,
                'fallback_active': self.fallback_active.get(endpoint_key, False)
            })
        
        async def reset_fallbacks(request: web.Request) -> web.Response:
            """Reset all fallback states"""
            self.reset_all_fallbacks()
            return web.json_response({
                'success': True,
                'message': 'All fallback states reset'
            })
        
        async def get_mock_logs(request: web.Request) -> web.Response:
            """Get mock request logs"""
            limit = int(request.query.get('limit', 100))
            logs = self.mock_system.get_request_logs(limit)
            return web.json_response({
                'logs': logs,
                'total': len(self.mock_system.request_logs)
            })
        
        # Add management routes
        app.router.add_get('/_fallback/status', get_fallback_status)
        app.router.add_post('/_fallback/activate', activate_fallback)
        app.router.add_post('/_fallback/deactivate', deactivate_fallback)
        app.router.add_post('/_fallback/reset', reset_fallbacks)
        app.router.add_get('/_fallback/logs', get_mock_logs)
        
        self.logger.info("Fallback management endpoints registered")


async def integrate_fallback_system(service: "ProServeService") -> Optional[ServiceFallbackManager]:
    """Integrate fallback system with ProServe service"""
    
    try:
        # Check if fallback is enabled in manifest
        fallback_config = service.manifest.deployment.get('fallback', {})
        if not fallback_config.get('enabled', True):
            return None
        
        # Create fallback manager
        fallback_manager = ServiceFallbackManager(service)
        
        # Wrap existing endpoint handlers with fallback logic
        for route in service.app.router.routes():
            if hasattr(route, '_handler') and route.method != 'OPTIONS':
                # Get path from route resource safely
                try:
                    if hasattr(route.resource, 'path'):
                        path = route.resource.path
                    elif hasattr(route.resource, '_path'):
                        path = route.resource._path
                    elif hasattr(route.resource, 'canonical'):
                        path = route.resource.canonical
                    else:
                        path = str(route.resource)
                    
                    endpoint_key = f"{route.method} {path}"
                    
                    # Wrap handler with fallback
                    original_handler = route._handler
                    wrapped_handler = await fallback_manager.wrap_endpoint_handler(
                        original_handler, endpoint_key
                    )
                    route._handler = wrapped_handler
                    
                except Exception as e:
                    logging.warning(f"Could not wrap route {route}: {e}")
                    continue
        
        # Setup management endpoints
        await fallback_manager.setup_management_endpoints(service.app)
        
        logging.info("Service fallback system integrated successfully")
        return fallback_manager
        
    except Exception as e:
        logging.error(f"Error integrating fallback system: {e}")
        return None
