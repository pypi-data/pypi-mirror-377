"""
ProServe Endpoint Manager - HTTP and WebSocket Endpoint Registration
Handles registration and management of service endpoints
"""

import asyncio
import json
import os
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from aiohttp import web, WSMsgType
from aiohttp.web import WebSocketResponse
import structlog


class EndpointManager:
    """Manages HTTP and WebSocket endpoint registration and handling"""
    
    def __init__(self, service_core, manifest):
        """Initialize endpoint manager with service core and manifest"""
        self.service_core = service_core
        self.manifest = manifest
        self.app = service_core.get_app()
        self.logger = service_core.get_logger()
        
        # Endpoint tracking
        self.registered_endpoints = {}
        self.websocket_handlers = {}
    
    def register_all_endpoints(self):
        """Register all endpoints from manifest"""
        self._register_http_endpoints()
        self._register_websocket_endpoints()
        self._register_proxy_endpoints()
    
    def _register_http_endpoints(self):
        """Register HTTP endpoints from manifest"""
        if not self.manifest.endpoints:
            return
            
        for endpoint in self.manifest.endpoints:
            self._register_single_endpoint(endpoint)
    
    def _register_single_endpoint(self, endpoint: Dict[str, Any]):
        """Register a single HTTP endpoint"""
        method = endpoint.get('method', 'GET').upper()
        path = endpoint['path']
        handler = endpoint.get('handler')
        script = endpoint.get('script')
        shell_command = endpoint.get('shell_command')
        action = endpoint.get('action')
        
        # Create appropriate handler function
        if shell_command:
            handler_func = self._create_shell_handler(endpoint)
        elif script:
            handler_func = self._create_script_handler(endpoint)
        elif action:
            handler_func = self._create_action_handler(endpoint)
        elif handler:
            handler_func = self._load_handler_function(handler)
        else:
            handler_func = self._create_generic_handler(endpoint)
        
        # Register the route
        route = self.app.router.add_route(method, path, handler_func)
        
        # Add CORS if enabled
        if self.manifest.enable_cors and hasattr(self.service_core, 'cors'):
            self.service_core.cors.add(route)
        
        # Track the endpoint
        endpoint_key = f"{method}:{path}"
        self.registered_endpoints[endpoint_key] = {
            'config': endpoint,
            'handler': handler_func,
            'route': route
        }
        
        self.logger.info(f"Registered {method} {path}")
    
    def _create_shell_handler(self, endpoint_config: Dict[str, Any]) -> Callable:
        """Create handler for shell command execution"""
        shell_command = endpoint_config['shell_command']
        converter = endpoint_config.get('converter')
        timeout = endpoint_config.get('timeout')
        env_vars = endpoint_config.get('env_vars', {})
        
        async def shell_handler(request):
            try:
                # Prepare parameters from request
                parameters = {}
                parameters.update(dict(request.query))
                
                # Add path parameters if available
                if hasattr(request, 'match_info'):
                    parameters.update(request.match_info)
                
                # Add JSON body if present
                if request.content_type == 'application/json':
                    try:
                        body_data = await request.json()
                        parameters.update(body_data)
                    except:
                        pass
                
                # Execute shell command
                result = await self.service_core.shell_handler.execute_command(
                    command=shell_command,
                    parameters=parameters,
                    converter=converter,
                    timeout=timeout,
                    env_vars=env_vars
                )
                
                if result['returncode'] == 0:
                    return web.json_response({
                        'success': True,
                        'data': result.get('converted_output', result['stdout']),
                        'execution_time': result.get('execution_time', 0)
                    })
                else:
                    error_data = {
                        'success': False,
                        'error': 'Command execution failed',
                        'command': result['command'],
                        'returncode': result['returncode'],
                        'stderr': result['stderr'],
                        'execution_time': result.get('execution_time', 0)
                    }
                    return web.json_response(error_data, status=500)
                    
            except Exception as e:
                self.logger.error(f"Shell handler error: {e}")
                return web.json_response({
                    'error': 'Internal server error',
                    'details': str(e)
                }, status=500)
        
        return shell_handler
    
    def _create_script_handler(self, endpoint_config: Dict[str, Any]) -> Callable:
        """Create handler for Python script execution"""
        script_path = endpoint_config['script']
        
        async def script_handler(request):
            try:
                # Load the script
                script_func = self._load_script(script_path, endpoint_config)
                
                # Prepare request data
                request_data = {
                    'method': request.method,
                    'path': request.path,
                    'query': dict(request.query),
                    'headers': dict(request.headers)
                }
                
                # Add body data if present
                if request.content_type == 'application/json':
                    try:
                        request_data['json'] = await request.json()
                    except:
                        pass
                
                # Execute script
                result = await script_func(request_data)
                
                if isinstance(result, dict):
                    return web.json_response(result)
                else:
                    return web.Response(text=str(result))
                    
            except Exception as e:
                self.logger.error(f"Script handler error: {e}")
                return web.json_response({
                    'error': 'Script execution failed',
                    'details': str(e)
                }, status=500)
        
        return script_handler
    
    def _create_action_handler(self, endpoint_config: Dict[str, Any]) -> Callable:
        """Create handler based on action type"""
        action = endpoint_config['action']
        
        async def action_handler(request):
            if action == 'serve_static':
                static_file = endpoint_config.get('static_file')
                static_dir = endpoint_config.get('static_dir')
                
                if static_file:
                    return web.FileResponse(static_file)
                elif static_dir:
                    path_info = request.match_info.get('path', '')
                    file_path = Path(static_dir) / path_info
                    if file_path.exists():
                        return web.FileResponse(file_path)
                    else:
                        raise web.HTTPNotFound()
                        
            elif action == 'system_status':
                return await self.service_core._health_handler(request)
                
            elif action == 'proserve_proxy':
                return await self._proserve_proxy_handler(request)
                
            else:
                return web.json_response({'error': f'Unknown action: {action}'}, status=400)
        
        return action_handler
    
    def _create_generic_handler(self, endpoint_config: Dict[str, Any]) -> Callable:
        """Create generic handler for simple responses"""
        async def generic_handler(request):
            return web.json_response({
                'message': f"Handler for {endpoint_config['path']} not implemented",
                'endpoint': endpoint_config
            })
        
        return generic_handler
    
    def _register_websocket_endpoints(self):
        """Register WebSocket endpoints from manifest"""
        if not hasattr(self.manifest, 'websockets') or not self.manifest.websockets:
            return
        
        for ws_config in self.manifest.websockets:
            path = ws_config['path']
            handler = ws_config.get('handler')
            script = ws_config.get('script')
            
            if script:
                ws_handler = self._create_websocket_script_handler(script, ws_config)
            elif handler:
                ws_handler = self._load_websocket_handler(handler)
            else:
                ws_handler = self._create_default_websocket_handler()
            
            self.app.router.add_get(path, ws_handler)
            self.websocket_handlers[path] = ws_handler
            
            self.logger.info(f"Registered WebSocket endpoint: {path}")
    
    def _create_websocket_script_handler(self, script_path: str, ws_config: Dict[str, Any]) -> Callable:
        """Create WebSocket handler for script execution"""
        async def websocket_handler(request):
            ws = WebSocketResponse()
            await ws.prepare(request)
            
            self.service_core.websocket_connections.add(ws)
            self.logger.info("WebSocket connection established")
            
            try:
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            
                            # Load and execute script
                            script_func = self._load_script(script_path, ws_config)
                            result = await script_func(data)
                            
                            # Send response
                            if result:
                                await ws.send_str(json.dumps(result))
                                
                        except Exception as e:
                            await ws.send_str(json.dumps({
                                'error': str(e),
                                'type': 'script_error'
                            }))
                    
                    elif msg.type == WSMsgType.ERROR:
                        self.logger.error(f'WebSocket error: {ws.exception()}')
                        break
            
            except Exception as e:
                self.logger.error(f"WebSocket handler error: {e}")
            finally:
                self.service_core.websocket_connections.discard(ws)
                self.logger.info("WebSocket connection closed")
            
            return ws
        
        return websocket_handler
    
    def _create_default_websocket_handler(self) -> Callable:
        """Create default WebSocket handler"""
        async def websocket_handler(request):
            ws = WebSocketResponse()
            await ws.prepare(request)
            
            self.service_core.websocket_connections.add(ws)
            self.logger.info("WebSocket connection established")
            
            try:
                async for msg in ws:
                    if msg.type == WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            response = await self._handle_websocket_message(data)
                            if response:
                                await ws.send_str(json.dumps(response))
                        except Exception as e:
                            await ws.send_str(json.dumps({
                                'error': str(e),
                                'type': 'message_error'
                            }))
                    elif msg.type == WSMsgType.ERROR:
                        self.logger.error(f'WebSocket error: {ws.exception()}')
                        break
            finally:
                self.service_core.websocket_connections.discard(ws)
                self.logger.info("WebSocket connection closed")
            
            return ws
        
        return websocket_handler
    
    async def _handle_websocket_message(self, data: Dict) -> Optional[Dict]:
        """Handle incoming WebSocket message"""
        action = data.get('action')
        
        if action == 'ping':
            return {'action': 'pong', 'timestamp': asyncio.get_event_loop().time()}
        
        elif action == 'status':
            return {
                'action': 'status',
                'data': {
                    'service': self.manifest.name,
                    'connections': len(self.service_core.websocket_connections),
                    'platform': self.manifest.platform,
                    'isolation_mode': self.manifest.isolation.get('mode', 'none')
                }
            }
        
        return {'action': 'error', 'error': f'Unknown action: {action}'}
    
    def _register_proxy_endpoints(self):
        """Register proxy endpoints for backward compatibility"""
        # ProServe proxy endpoint
        self.app.router.add_post('/api/proserve', self._proserve_proxy_handler)
        self.logger.info("Registered ProServe proxy endpoint")
    
    async def _proserve_proxy_handler(self, request):
        """Proxy requests to ProServe backend (backward compatible)"""
        if not self.service_core.proserve_client:
            return web.json_response({'error': 'ProServe client not available'}, status=503)
        
        try:
            data = await request.json()
            result = await self.service_core.proserve_client.execute(
                data.get('action'),
                data.get('target'),
                **data.get('params', {})
            )
            return web.json_response(result)
        except Exception as e:
            self.logger.error(f"ProServe proxy error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    def _load_script(self, script_path: str, config: Dict[str, Any] = None) -> Callable:
        """Load and return executable script function"""
        # Convert relative path to absolute
        if not os.path.isabs(script_path):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                project_root = manifest_dir.parent
                script_path = str(project_root / script_path)
            else:
                script_path = str(Path.cwd() / script_path)
        
        if not Path(script_path).exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Load the script module
        spec = importlib.util.spec_from_file_location("endpoint_script", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Return the main function or handler
        if hasattr(module, 'main'):
            return module.main
        elif hasattr(module, 'handler'):
            return module.handler
        else:
            raise AttributeError(f"Script {script_path} must have 'main' or 'handler' function")
    
    def _load_handler_function(self, handler_path: str) -> Callable:
        """Load handler function from module path"""
        try:
            module_path, func_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            # Try pytest-compatible fallback for test handlers
            try:
                import sys
                from pathlib import Path
                
                # For test execution, try loading from test handlers directly
                test_handlers_dir = Path(__file__).parent.parent.parent / "tests"
                
                if test_handlers_dir.exists():
                    # Try pytest-compatible approach: direct file loading
                    if module_path.startswith('handlers.'):
                        handler_module_name = module_path.split('.', 1)[1]  # Remove 'handlers.' prefix
                        handler_file = test_handlers_dir / "handlers" / f"{handler_module_name}.py"
                        
                        if handler_file.exists():
                            # Load module directly from file path
                            spec = importlib.util.spec_from_file_location(module_path, handler_file)
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                sys.modules[module_path] = module  # Cache the module
                                spec.loader.exec_module(module)
                                return getattr(module, func_name)
                
                # If direct file loading fails, try sys.path approach
                if str(test_handlers_dir) not in sys.path:
                    sys.path.insert(0, str(test_handlers_dir))
                
                # Clear any cached import failures
                if module_path in sys.modules:
                    del sys.modules[module_path]
                
                # Retry import using the module-level importlib
                import importlib as imp  # Use alias to avoid scoping issues
                module = imp.import_module(module_path)
                return getattr(module, func_name)
                
            except Exception as fallback_error:
                # If all attempts fail, provide detailed error information
                raise ImportError(f"Cannot load handler {handler_path}: Original error: {e}, Fallback error: {fallback_error}")
    
    def _load_websocket_handler(self, handler_path: str) -> Callable:
        """Load WebSocket handler function"""
        return self._load_handler_function(handler_path)
    
    def get_registered_endpoints(self) -> Dict[str, Any]:
        """Get information about all registered endpoints"""
        return {
            'http_endpoints': list(self.registered_endpoints.keys()),
            'websocket_endpoints': list(self.websocket_handlers.keys()),
            'total_endpoints': len(self.registered_endpoints) + len(self.websocket_handlers)
        }
