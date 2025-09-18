"""
ProServe Service Builder - Fluent API for Easy Service Creation
Provides a simplified, decorator-based API for creating ProServe services without complex manifests
"""

import asyncio
import json
from typing import Dict, Any, Callable, Optional, Union, List
from functools import wraps
from aiohttp import web
import structlog

from .manifest import ServiceManifest
from .service_core import ServiceCore
from .endpoint_manager import EndpointManager
from .task_manager import BackgroundTaskManager
from .static_handler import StaticFileHandler


class ServiceBuilder:
    """Fluent API builder for creating ProServe services with decorators"""
    
    def __init__(self, name: str, **kwargs):
        """Initialize service builder with basic configuration"""
        self.name = name
        self.version = kwargs.get('version', '1.0.0')
        self.description = kwargs.get('description', f'{name} ProServe service')
        
        # Service configuration
        self.config = {
            'name': name,
            'version': self.version,
            'description': self.description,
            'platform': kwargs.get('platform', 'python'),
            'enable_cors': kwargs.get('enable_cors', True),
            'enable_health_check': kwargs.get('enable_health_check', True),
            'enable_metrics': kwargs.get('enable_metrics', True),
            'isolation': kwargs.get('isolation', {'mode': 'none'}),
            'endpoints': [],
            'websockets': [],
            'background_tasks': [],
            'static': {
                'directories': [],
                'files': []
            }
        }
        
        # Runtime components
        self.endpoint_handlers = {}
        self.websocket_handlers = {}
        self.background_task_functions = {}
        self.middleware_functions = []
        
        # Service instance (created when built)
        self._service = None
        self.logger = structlog.get_logger(name)
    
    def endpoint(self, path: str, method: str = 'GET', **kwargs):
        """Decorator to register HTTP endpoint handlers"""
        def decorator(func: Callable):
            endpoint_config = {
                'path': path,
                'method': method.upper(),
                'handler_function': func,
                **kwargs
            }
            
            self.config['endpoints'].append(endpoint_config)
            self.endpoint_handlers[f"{method.upper()}:{path}"] = func
            
            self.logger.info(f"Registered endpoint: {method.upper()} {path}")
            return func
        
        return decorator
    
    def get(self, path: str, **kwargs):
        """Shortcut decorator for GET endpoints"""
        return self.endpoint(path, 'GET', **kwargs)
    
    def post(self, path: str, **kwargs):
        """Shortcut decorator for POST endpoints"""
        return self.endpoint(path, 'POST', **kwargs)
    
    def put(self, path: str, **kwargs):
        """Shortcut decorator for PUT endpoints"""
        return self.endpoint(path, 'PUT', **kwargs)
    
    def delete(self, path: str, **kwargs):
        """Shortcut decorator for DELETE endpoints"""
        return self.endpoint(path, 'DELETE', **kwargs)
    
    def websocket(self, path: str, **kwargs):
        """Decorator to register WebSocket handlers"""
        def decorator(func: Callable):
            websocket_config = {
                'path': path,
                'handler_function': func,
                **kwargs
            }
            
            self.config['websockets'].append(websocket_config)
            self.websocket_handlers[path] = func
            
            self.logger.info(f"Registered WebSocket endpoint: {path}")
            return func
        
        return decorator
    
    def background_task(self, interval: int = 60, **kwargs):
        """Decorator to register background tasks"""
        def decorator(func: Callable):
            task_name = kwargs.get('name', func.__name__)
            
            task_config = {
                'name': task_name,
                'interval': interval,
                'handler_function': func,
                **kwargs
            }
            
            self.config['background_tasks'].append(task_config)
            self.background_task_functions[task_name] = func
            
            self.logger.info(f"Registered background task: {task_name} (interval: {interval}s)")
            return func
        
        return decorator
    
    def middleware(self, func: Callable):
        """Decorator to register middleware"""
        self.middleware_functions.append(func)
        self.logger.info(f"Registered middleware: {func.__name__}")
        return func
    
    def static_directory(self, url_path: str, local_path: str, **kwargs):
        """Add static directory serving"""
        dir_config = {
            'path': local_path,
            'url_path': url_path,
            **kwargs
        }
        self.config['static']['directories'].append(dir_config)
        self.logger.info(f"Added static directory: {url_path} -> {local_path}")
        return self
    
    def static_file(self, url_path: str, local_file: str, **kwargs):
        """Add static file serving"""
        file_config = {
            'file': local_file,
            'url_path': url_path,
            **kwargs
        }
        self.config['static']['files'].append(file_config)
        self.logger.info(f"Added static file: {url_path} -> {local_file}")
        return self
    
    def enable_cors(self, enabled: bool = True):
        """Enable/disable CORS"""
        self.config['enable_cors'] = enabled
        return self
    
    def enable_health_check(self, enabled: bool = True):
        """Enable/disable health check endpoints"""
        self.config['enable_health_check'] = enabled
        return self
    
    def enable_metrics(self, enabled: bool = True):
        """Enable/disable metrics endpoints"""
        self.config['enable_metrics'] = enabled
        return self
    
    def set_isolation(self, mode: str = 'none', **kwargs):
        """Set isolation configuration"""
        self.config['isolation'] = {'mode': mode, **kwargs}
        return self
    
    def add_env_var(self, name: str, default: Any = None, required: bool = False):
        """Add environment variable requirement"""
        if 'env_vars' not in self.config:
            self.config['env_vars'] = []
        
        self.config['env_vars'].append({
            'name': name,
            'default': default,
            'required': required
        })
        return self
    
    def build(self) -> 'ModularProServeService':
        """Build the service with all registered components"""
        # Create manifest from configuration
        manifest = ServiceManifest.from_dict(self.config)
        
        # Create the modular service
        self._service = ModularProServeService(
            manifest=manifest,
            endpoint_handlers=self.endpoint_handlers,
            websocket_handlers=self.websocket_handlers,
            background_task_functions=self.background_task_functions,
            middleware_functions=self.middleware_functions
        )
        
        self.logger.info(f"Service built successfully: {self.name}")
        return self._service
    
    async def run(self, host: str = '0.0.0.0', port: int = 8000, **kwargs):
        """Build and run the service"""
        if not self._service:
            self._service = self.build()
        
        return await self._service.run(host=host, port=port, **kwargs)


class ModularProServeService:
    """Modular ProServe service using composition of focused components"""
    
    def __init__(self, manifest: ServiceManifest, 
                 endpoint_handlers: Dict[str, Callable] = None,
                 websocket_handlers: Dict[str, Callable] = None,
                 background_task_functions: Dict[str, Callable] = None,
                 middleware_functions: List[Callable] = None):
        
        self.manifest = manifest
        
        # Initialize core components
        self.service_core = ServiceCore(manifest)
        self.endpoint_manager = EndpointManager(self.service_core, manifest)
        self.task_manager = BackgroundTaskManager(self.service_core, manifest)
        self.static_handler = StaticFileHandler(self.service_core, manifest)
        
        # Store function handlers
        self.endpoint_handlers = endpoint_handlers or {}
        self.websocket_handlers = websocket_handlers or {}
        self.background_task_functions = background_task_functions or {}
        self.middleware_functions = middleware_functions or []
        
        # Setup service
        self._setup_service()
    
    def _setup_service(self):
        """Setup the complete service with all components"""
        # Register custom endpoint handlers
        self._register_custom_handlers()
        
        # Register standard endpoints from manifest
        self.endpoint_manager.register_all_endpoints()
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup fallback system integration
        self._setup_fallback_system()
    
    def _register_custom_handlers(self):
        """Register custom endpoint and websocket handlers"""
        app = self.service_core.get_app()
        
        # Register endpoint handlers
        for endpoint_key, handler_func in self.endpoint_handlers.items():
            method, path = endpoint_key.split(':', 1)
            
            # Wrap handler to convert return values
            async def wrapped_handler(request, func=handler_func):
                try:
                    result = await func(request) if asyncio.iscoroutinefunction(func) else func(request)
                    
                    if isinstance(result, dict):
                        return web.json_response(result)
                    elif isinstance(result, (str, bytes)):
                        return web.Response(text=result)
                    elif isinstance(result, web.Response):
                        return result
                    else:
                        return web.json_response({'result': result})
                        
                except Exception as e:
                    self.service_core.logger.error(f"Handler error: {e}")
                    return web.json_response({'error': str(e)}, status=500)
            
            app.router.add_route(method, path, wrapped_handler)
            
            # Add CORS if enabled
            if self.manifest.enable_cors and hasattr(self.service_core, 'cors'):
                route = app.router._resources[-1]._routes[0]
                self.service_core.cors.add(route)
        
        # Register WebSocket handlers
        for path, handler_func in self.websocket_handlers.items():
            ws_handler = self._create_websocket_handler(handler_func)
            app.router.add_get(path, ws_handler)
    
    def _create_websocket_handler(self, handler_func: Callable):
        """Create aiohttp WebSocket handler from user function"""
        async def websocket_handler(request):
            from aiohttp.web import WebSocketResponse, WSMsgType
            
            ws = WebSocketResponse()
            await ws.prepare(request)
            
            self.service_core.websocket_connections.add(ws)
            self.service_core.logger.info("WebSocket connection established")
            
            try:
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            
                            # Call user handler
                            if asyncio.iscoroutinefunction(handler_func):
                                result = await handler_func(data, ws)
                            else:
                                result = handler_func(data, ws)
                            
                            # Send response if provided
                            if result is not None:
                                await ws.send_str(json.dumps(result))
                                
                        except Exception as e:
                            await ws.send_str(json.dumps({
                                'error': str(e),
                                'type': 'handler_error'
                            }))
                    
                    elif msg.type == WSMsgType.ERROR:
                        self.service_core.logger.error(f'WebSocket error: {ws.exception()}')
                        break
            
            except Exception as e:
                self.service_core.logger.error(f"WebSocket handler error: {e}")
            finally:
                self.service_core.websocket_connections.discard(ws)
                self.service_core.logger.info("WebSocket connection closed")
            
            return ws
        
        return websocket_handler
    
    def _setup_middleware(self):
        """Setup middleware functions"""
        app = self.service_core.get_app()
        
        for middleware_func in self.middleware_functions:
            app.middlewares.append(middleware_func)
    
    def _setup_fallback_system(self):
        """Setup fallback system integration"""
        # This would integrate with the existing fallback system
        # For now, we'll add it to the startup tasks
        async def setup_fallback(app):
            try:
                from .service_fallback import integrate_fallback_system
                await integrate_fallback_system(self)
            except ImportError:
                self.service_core.logger.warning("Fallback system not available")
        
        self.service_core.app.on_startup.append(setup_fallback)
    
    async def run(self, host: str = '0.0.0.0', port: int = 8000, **kwargs):
        """Run the service"""
        # Start background tasks
        await self.task_manager.setup_background_tasks()
        
        # Run the web application
        from aiohttp import web
        runner = web.AppRunner(self.service_core.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        self.service_core.logger.info(f"Service running on http://{host}:{port}")
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.service_core.logger.info("Shutting down service...")
        finally:
            await self.task_manager.stop_all_tasks()
            await runner.cleanup()
    
    def get_app(self) -> web.Application:
        """Get the underlying aiohttp application"""
        return self.service_core.get_app()
    
    def get_logger(self):
        """Get the service logger"""
        return self.service_core.get_logger()


# Convenience function to create services
def Service(name: str, **kwargs) -> ServiceBuilder:
    """Create a new ProServe service builder"""
    return ServiceBuilder(name, **kwargs)
