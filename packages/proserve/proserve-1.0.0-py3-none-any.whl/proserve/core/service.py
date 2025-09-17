"""
ProServe Service Framework - Base Service Class
Core ProServeService class that handles manifest-based service creation with automatic features
"""

import asyncio
import json
import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from aiohttp import web, WSMsgType
from aiohttp.web import WebSocketResponse
import aiohttp_cors
import structlog
from dotenv import load_dotenv

# Import from ProServe refactored modules
from .manifest import ServiceManifest
from .isolation import ProcessIsolationManager
from .shell import ShellCommandHandler
from .service_fallback import integrate_fallback_system

# ProServe logging imports
try:
    from .logging import (
        setup_logging,
        create_logger,
        get_log_broadcaster,
        setup_log_endpoints,
    )
    PROSERVE_LOGGING_AVAILABLE = True
except ImportError:
    PROSERVE_LOGGING_AVAILABLE = False
    def setup_logging(**kwargs):
        return structlog.get_logger()
    def create_logger(name):
        return structlog.get_logger(name)
    def get_log_broadcaster():
        return None
    def setup_log_endpoints(app, websocket_path="/logs"):
        return app


class ProServeService:
    """Base service class that handles common patterns with multi-environment support"""
    
    def __init__(self, manifest: Union[ServiceManifest, str, Dict]):
        # Handle different manifest input types
        if isinstance(manifest, str):
            self.manifest = ServiceManifest.from_yaml(manifest)
        elif isinstance(manifest, dict):
            self.manifest = ServiceManifest.from_dict(manifest)
        else:
            self.manifest = manifest
            
        self.app = web.Application()
        self.logger = self._setup_logging()
        self.proserve_client = None  # Changed from edpmt_client
        self.websocket_connections = set()
        self.background_task_handles = []
        
        # Initialize process isolation manager
        self.isolation_manager = ProcessIsolationManager(self.manifest.isolation)
        
        # Initialize shell command handler
        self.shell_handler = ShellCommandHandler(
            shell_config=getattr(self.manifest, 'shell_config', {}),
            converters=getattr(self.manifest, 'converters', {})
        )
        
        # Load environment variables
        load_dotenv()
        self._load_env_vars()
        
        # Setup features based on manifest
        self._setup_features()
        
        # Initialize ProServe if required (backward compatibility with EDPMT)
        if self.manifest.requires_proserve or self.manifest.requires_edpmt:
            self._init_proserve_client()
        
        # Setup static file serving
        self._setup_static_files()
        
        # Register endpoints
        self._register_endpoints()
        
        # Setup WebSocket handlers
        self._setup_websocket_handlers()
        
        # Setup WebSocket log endpoints
        self._setup_log_endpoints()
        
        # Setup background tasks
        self._setup_background_tasks()
        
        # Setup fallback system (will be integrated on startup)
        self._configure_fallback_system()
        
        # Setup app lifecycle
        self.app.on_startup.append(self._on_startup)
        self.app.on_cleanup.append(self._on_cleanup)
    
    def _setup_logging(self) -> structlog.BoundLogger:
        """Setup enhanced structured logging with WebSocket broadcasting and contextual information"""
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        # Create enhanced logging context with manifest and service information
        manifest_path = getattr(self.manifest, '_manifest_path', None)
        isolation_mode = self.manifest.isolation.get('mode', 'none') if self.manifest.isolation else 'none'
        
        # Use ProServe logging system with contextual information
        if PROSERVE_LOGGING_AVAILABLE:
            logger = setup_logging(
                service_name=self.manifest.name,
                manifest_path=manifest_path,
                isolation_mode=isolation_mode,
                debug=debug_mode,
                console_output=True,
                json_output=not debug_mode
            )
        else:
            # Fallback to basic logging
            logger = structlog.get_logger(self.manifest.name)
        
        # Store log broadcaster for later use in script execution
        self.log_broadcaster = get_log_broadcaster()
        
        return logger
    
    def _load_env_vars(self):
        """Load required environment variables"""
        self.env = {}
        if self.manifest.env_vars:
            for var in self.manifest.env_vars:
                value = os.getenv(var)
                self.env[var] = value
                if value is None:
                    self.logger.warning(f"Environment variable {var} not set")
                else:
                    self.logger.debug(f"Loaded env var {var}")
    
    def _setup_features(self):
        """Setup common features based on manifest"""
        # CORS
        if self.manifest.enable_cors:
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            self.cors = cors
            
        # Health check
        if self.manifest.enable_health:
            self.app.router.add_get('/health', self._health_handler)
            self.app.router.add_get('/api/health', self._health_handler)
            
        # Metrics
        if self.manifest.enable_metrics:
            self.app.router.add_get('/metrics', self._metrics_handler)
    
    def _setup_log_endpoints(self):
        """Setup WebSocket endpoints for log broadcasting"""
        setup_log_endpoints(self.app, "/logs")
        self.logger.info("WebSocket log broadcasting endpoint setup at /logs")
    
    def _init_proserve_client(self):
        """Initialize ProServe client connection (backward compatibility with EDPMT)"""
        try:
            # Try ProServe client first
            url = self.manifest.proserve_url or self.manifest.edpmt_url or os.getenv('PROSERVE_BACKEND_URL') or os.getenv('EDPMT_BACKEND_URL', 'https://localhost:8888')
            
            # Try to import ProServe client, fallback to EDPMT for compatibility
            try:
                from proserve.client import ProServeClient
                self.proserve_client = ProServeClient(url=url)
                self.logger.info(f"ProServe client initialized: {url}")
            except ImportError:
                try:
                    from edpmt.cli import EDPMClient
                    self.proserve_client = EDPMClient(url=url)  # Store as proserve_client for consistency
                    self.logger.info(f"EDPMT client initialized (compatibility mode): {url}")
                except ImportError:
                    self.logger.warning("Neither ProServe nor EDPMT client available - running in local mode")
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize ProServe/EDPMT client: {e}")
    
    def _setup_static_files(self):
        """Setup static file serving"""
        # Static directories
        for route_path, dir_path in self.manifest.static_dirs.items():
            self.app.router.add_static(route_path, dir_path)
            self.logger.info(f"Serving static directory {dir_path} at {route_path}")
        
        # Individual static files
        for route_path, file_path in self.manifest.static_files.items():
            async def serve_static_file(request, file_path=file_path):
                return web.FileResponse(file_path)
            
            self.app.router.add_get(route_path, serve_static_file)
            self.logger.info(f"Serving static file {file_path} at {route_path}")
    
    def _register_endpoints(self):
        """Register HTTP endpoints from manifest"""
        if not self.manifest.endpoints:
            return
            
        for endpoint in self.manifest.endpoints:
            method = endpoint.get('method', 'GET').upper()
            path = endpoint['path']
            handler = endpoint.get('handler')
            script = endpoint.get('script')
            shell_command = endpoint.get('shell_command')
            action = endpoint.get('action')
            
            if shell_command:
                # Shell command execution (new feature)
                try:
                    handler_func = self._create_shell_handler(endpoint)
                    route = self.app.router.add_route(method, path, handler_func)
                    
                    # Add CORS if enabled
                    if self.manifest.enable_cors and hasattr(self, 'cors'):
                        self.cors.add(route)
                        
                    self.logger.info(f"Registered {method} {path} -> shell: {shell_command}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to create shell handler for {shell_command}: {e}")
                    continue
                    
            elif script:
                # Script-based execution (new preferred method)
                try:
                    handler_func = self._load_script(script, endpoint)
                    route = self.app.router.add_route(method, path, handler_func)
                    
                    # Add CORS if enabled
                    if self.manifest.enable_cors and hasattr(self, 'cors'):
                        self.cors.add(route)
                        
                except Exception as e:
                    self.logger.error(f"Failed to load script {script}: {e}")
                    continue
                    
            elif handler:
                # Dynamic handler loading (legacy support)
                try:
                    handler_func = self._load_handler(handler)
                    
                    # Create wrapper to pass manifest parameters to handler
                    if 'params' in endpoint:
                        async def param_wrapper(request, original_handler=handler_func, params=endpoint['params']):
                            return await original_handler(request, **params)
                        route = self.app.router.add_route(method, path, param_wrapper)
                    else:
                        route = self.app.router.add_route(method, path, handler_func)
                    
                    # Add CORS if enabled
                    if self.manifest.enable_cors and hasattr(self, 'cors'):
                        self.cors.add(route)
                        
                except Exception as e:
                    self.logger.error(f"Failed to load handler {handler}: {e}")
                    continue
                    
            elif action:
                # Use built-in action handler
                handler_func = self._create_action_handler(endpoint)
                route = self.app.router.add_route(method, path, handler_func)
                
                if self.manifest.enable_cors and hasattr(self, 'cors'):
                    self.cors.add(route)
            else:
                # Use generic handler
                handler_func = lambda req, ep=endpoint: self._generic_handler(req, ep)
                route = self.app.router.add_route(method, path, handler_func)
                
                if self.manifest.enable_cors and hasattr(self, 'cors'):
                    self.cors.add(route)
            
            self.logger.info(f"Registered {method} {path}")
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket handlers from manifest"""
        if not self.manifest.websocket_handlers:
            return
            
        for ws_handler in self.manifest.websocket_handlers:
            path = ws_handler['path']
            handler = ws_handler.get('handler')
            script = ws_handler.get('script')
            
            if script:
                # Script-based execution (new preferred method)
                try:
                    handler_func = self._load_script(script)
                    self.app.router.add_get(path, handler_func)
                except Exception as e:
                    self.logger.error(f"Failed to load WebSocket script {script}: {e}")
                    continue
                    
            elif handler:
                # Legacy handler support
                try:
                    handler_func = self._load_handler(handler)
                    self.app.router.add_get(path, handler_func)
                except Exception as e:
                    self.logger.error(f"Failed to load WebSocket handler {handler}: {e}")
                    continue
            else:
                # Use default WebSocket handler
                self.app.router.add_get(path, self._default_websocket_handler)
            
            self.logger.info(f"Registered WebSocket handler at {path}")
    
    def _load_handler(self, handler_spec: str) -> Callable:
        """Dynamically load handler function (legacy support)"""
        if '.' not in handler_spec:
            # If no module specified, try the handler module from manifest
            if self.manifest.handler_module:
                handler_spec = f"{self.manifest.handler_module}.{handler_spec}"
            else:
                raise ValueError(f"Handler {handler_spec} needs module path")
        
        module_name, func_name = handler_spec.rsplit('.', 1)
        
        try:
            module = importlib.import_module(module_name)
            return getattr(module, func_name)
        except ImportError as e:
            raise ImportError(f"Could not import handler module {module_name}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Handler {func_name} not found in {module_name}: {e}")
    
    def _load_script(self, script_path: str, endpoint_config: Dict[str, Any] = None) -> Callable:
        """Load and execute individual Python script file with isolation support"""
        # Convert relative path to absolute based on service location
        if not os.path.isabs(script_path):
            # If relative, look for script relative to project root (not manifest location)
            if hasattr(self.manifest, '_manifest_path'):
                # Find project root by going up from manifest directory
                manifest_dir = Path(self.manifest._manifest_path).parent
                project_root = manifest_dir.parent  # Go up one level from manifests/
                script_path = str(project_root / script_path)
            else:
                script_path = str(Path.cwd() / script_path)
        
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")
        
        # Get isolation settings - endpoint can override service defaults
        isolation_config = self.manifest.isolation.copy()
        if endpoint_config and 'isolation' in endpoint_config:
            isolation_config.update(endpoint_config['isolation'])
        
        # Create endpoint-specific isolation manager if different from service default
        if isolation_config != self.manifest.isolation:
            endpoint_isolation_manager = ProcessIsolationManager(isolation_config)
        else:
            endpoint_isolation_manager = self.isolation_manager
        
        # Create wrapper that handles isolation and passes the service instance
        async def script_wrapper(request):
            try:
                self.logger.info(f"Executing script handler", script=str(script_path), isolation_mode=isolation_config.get('mode', 'none'))
                
                # Use isolation manager to execute script
                result = await endpoint_isolation_manager.execute_script(str(script_path), self, request, None)
                
                self.logger.info(f"Script execution completed successfully", script=str(script_path))
                return result
            except Exception as e:
                self.logger.error(f"Script execution failed: {e}", 
                                script=str(script_path), 
                                isolation_mode=isolation_config.get('mode', 'none'),
                                error_type=type(e).__name__)
                raise
        
        isolation_mode = isolation_config.get('mode', 'none')
        self.logger.info(f"Loaded script: {script_path} (isolation: {isolation_mode})")
        return script_wrapper
    
    def _load_script_for_background_task(self, script_path: str, task_config: Dict[str, Any] = None) -> Callable:
        """Load and execute individual Python script file for background tasks with isolation support"""
        # Convert relative path to absolute based on service location
        if not os.path.isabs(script_path):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                project_root = manifest_dir.parent
                script_path = str(project_root / script_path)
            else:
                script_path = str(Path.cwd() / script_path)
        
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Background task script file not found: {script_path}")
        
        # Get isolation settings - task can override service defaults
        isolation_config = self.manifest.isolation.copy()
        if task_config and 'isolation' in task_config:
            isolation_config.update(task_config['isolation'])
        
        # Create task-specific isolation manager if different from service default
        if isolation_config != self.manifest.isolation:
            task_isolation_manager = ProcessIsolationManager(isolation_config)
        else:
            task_isolation_manager = self.isolation_manager
        
        # Background tasks only need the service instance, not request
        async def bg_script_wrapper(service):
            task_name = task_config.get('name', 'unnamed_task') if task_config else 'unnamed_task'
            try:
                self.logger.info(f"Starting background task: {task_name}", script=str(script_path))
                result = await task_isolation_manager.execute_script(str(script_path), service, None, None)
                self.logger.info(f"Background task completed: {task_name}")
                return result
            except Exception as e:
                self.logger.error(f"Background task execution failed: {e}", script=str(script_path))
                raise
        
        task_name = task_config.get('name', 'unnamed_task') if task_config else 'unnamed_task'
        isolation_mode = isolation_config.get('mode', 'none')
        self.logger.info(f"Loaded background task script: {script_path} (task: {task_name}, isolation: {isolation_mode})")
        return bg_script_wrapper
    
    def _create_action_handler(self, endpoint_config: Dict) -> Callable:
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
                    if file_path.exists() and file_path.is_file():
                        return web.FileResponse(file_path)
                    else:
                        raise web.HTTPNotFound()
                        
            elif action == 'system_status':
                return await self._system_status_handler(request)
                
            elif action == 'proserve_proxy':
                return await self._proserve_proxy_handler(request)
                
            elif action == 'runtime_config':
                return await self._runtime_config_handler(request, endpoint_config)
                
            else:
                return web.json_response({'error': f'Unknown action: {action}'}, status=400)
        
        return action_handler
    
    def _setup_background_tasks(self):
        """Setup background tasks from manifest"""
        if not self.manifest.background_tasks:
            return
            
        async def start_background_tasks(app):
            self.background_task_handles = []
            
            for task_spec in self.manifest.background_tasks:
                try:
                    handler = task_spec.get('handler')
                    script = task_spec.get('script')
                    
                    if script:
                        # Script-based execution (new preferred method)
                        task_func = self._load_script_for_background_task(script, task_spec)
                        task_name = script
                    elif handler:
                        # Legacy handler support
                        task_func = self._load_handler(handler)
                        task_name = handler
                    else:
                        self.logger.error("Background task must specify either 'script' or 'handler'")
                        continue
                    
                    interval = task_spec.get('interval', 60)
                    broadcast = task_spec.get('broadcast', False)
                    
                    task = asyncio.create_task(
                        self._run_periodic(task_func, interval, broadcast)
                    )
                    self.background_task_handles.append(task)
                    self.logger.info(f"Started background task: {task_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to start background task {task_spec.get('script') or task_spec.get('handler')}: {e}")
        
        self.app.on_startup.append(start_background_tasks)
    
    def _configure_fallback_system(self):
        """Configure fallback system (synchronous setup)"""
        try:
            # Check if fallback is enabled in manifest
            fallback_config = getattr(self.manifest, 'deployment', {}).get('fallback', {})
            self.fallback_enabled = fallback_config.get('enabled', False)
            
            if self.fallback_enabled:
                self.logger.info("Fallback system configured - will integrate on startup")
            else:
                self.logger.info("Fallback system disabled in manifest")
                
        except Exception as e:
            self.logger.error(f"Error configuring fallback system: {e}")
            self.fallback_enabled = False
    
    async def _run_periodic(self, func: Callable, interval: int, broadcast: bool = False):
        """Run function periodically"""
        while True:
            try:
                result = await func(self)
                
                # If broadcast is enabled and we have WebSocket connections
                if broadcast and self.websocket_connections and result:
                    await self._broadcast_to_websockets(result)
                    
            except Exception as e:
                self.logger.error(f"Background task error: {e}")
            
            await asyncio.sleep(interval)
    
    async def _broadcast_to_websockets(self, message: Dict):
        """Broadcast message to all WebSocket connections"""
        if not self.websocket_connections:
            return
            
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_str(json.dumps(message))
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected connections
        self.websocket_connections -= disconnected
    
    async def _on_startup(self, app):
        """Service startup handler"""
        self.logger.info(f"Service {self.manifest.name} starting up")
        
        # Start log broadcaster
        if self.log_broadcaster:
            try:
                await self.log_broadcaster.start_broadcaster()
                self.logger.info("WebSocket log broadcasting started")
            except Exception as e:
                self.logger.warning(f"Failed to start log broadcaster: {e}")
        
        # Setup fallback system integration
        if getattr(self, 'fallback_enabled', False):
            try:
                fallback_manager = await integrate_fallback_system(self)
                if fallback_manager:
                    self.fallback_manager = fallback_manager
                    self.logger.info("Service fallback system integrated successfully")
                else:
                    self.logger.warning("Failed to integrate fallback system")
            except Exception as e:
                self.logger.error(f"Error integrating fallback system: {e}")
        
        # Run custom initialization if specified
        if self.manifest.init_module:
            try:
                init_module = importlib.import_module(self.manifest.init_module)
                if hasattr(init_module, 'init_service'):
                    await init_module.init_service(self)
            except Exception as e:
                self.logger.error(f"Custom initialization failed: {e}")
    
    async def _on_cleanup(self, app):
        """Service cleanup handler"""
        self.logger.info(f"Service {self.manifest.name} shutting down")
        
        # Stop log broadcaster
        if self.log_broadcaster:
            try:
                await self.log_broadcaster.stop_broadcaster()
                self.logger.info("WebSocket log broadcasting stopped")
            except Exception as e:
                self.logger.warning(f"Failed to stop log broadcaster: {e}")
        
        # Cancel background tasks
        for task in self.background_task_handles:
            task.cancel()
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            try:
                await ws.close()
            except Exception:
                pass
    
    async def _health_handler(self, request):
        """Standard health check endpoint"""
        health_data = {
            'status': 'healthy',
            'service': self.manifest.name,
            'version': self.manifest.version,
            'type': self.manifest.type,
            'timestamp': asyncio.get_event_loop().time(),
            'platform_info': self.manifest.get_platform_info() if hasattr(self.manifest, 'get_platform_info') else {},
            'isolation_environments': self.isolation_manager.get_available_environments() if hasattr(self.isolation_manager, 'get_available_environments') else {}
        }
        
        # Check ProServe/EDPMT connection if required
        if self.manifest.requires_proserve or self.manifest.requires_edpmt:
            if self.proserve_client:
                health_data['proserve_client'] = 'connected'
            else:
                health_data['proserve_client'] = 'disconnected'
                health_data['status'] = 'degraded'
        
        return web.json_response(health_data)
    
    async def _metrics_handler(self, request):
        """Metrics endpoint for monitoring"""
        metrics = {
            'service_info': {
                'name': self.manifest.name,
                'version': self.manifest.version,
                'type': self.manifest.type,
                'platform': self.manifest.platform,
                'board': self.manifest.board
            },
            'websocket_connections': len(self.websocket_connections),
            'background_tasks': len(self.background_task_handles),
            'isolation_info': self.isolation_manager.get_platform_info() if hasattr(self.isolation_manager, 'get_platform_info') else {}
        }
        return web.json_response(metrics)
    
    async def _system_status_handler(self, request):
        """System status handler"""
        status = {
            'service': self.manifest.name,
            'status': 'running',
            'websocket_connections': len(self.websocket_connections),
            'proserve_client_available': self.proserve_client is not None,
            'platform': self.manifest.platform,
            'isolation_mode': self.manifest.isolation.get('mode', 'none')
        }
        return web.json_response(status)
    
    async def _proserve_proxy_handler(self, request):
        """Proxy requests to ProServe backend (backward compatible with EDPMT)"""
        if not self.proserve_client:
            return web.json_response({'error': 'ProServe client not available'}, status=503)
        
        try:
            data = await request.json()
            result = await self.proserve_client.execute(
                data.get('action'),
                data.get('target'),
                **data.get('params', {})
            )
            return web.json_response(result)
        except Exception as e:
            self.logger.error(f"ProServe proxy error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def _runtime_config_handler(self, request, endpoint_config):
        """Generate runtime configuration"""
        template = endpoint_config.get('template', {})
        
        # Expand environment variables in template
        config = {}
        for key, value in template.items():
            if isinstance(value, str):
                config[key] = os.path.expandvars(value)
            else:
                config[key] = value
        
        # Generate JavaScript configuration with ProServe branding
        js_config = f"window.PROSERVE_CONFIG = {json.dumps(config, indent=2)};"
        
        return web.Response(
            text=js_config,
            content_type='application/javascript'
        )
    
    async def _default_websocket_handler(self, request):
        """Default WebSocket handler"""
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        self.logger.info("New WebSocket connection established")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        response = await self._handle_websocket_message(data)
                        if response:
                            await ws.send_str(json.dumps(response))
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({'error': 'Invalid JSON'}))
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
        except Exception as e:
            self.logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websocket_connections.discard(ws)
            self.logger.info("WebSocket connection closed")
        
        return ws
    
    async def _handle_websocket_message(self, data: Dict) -> Optional[Dict]:
        """Handle incoming WebSocket message"""
        action = data.get('action')
        
        if action == 'ping':
            return {'action': 'pong', 'timestamp': asyncio.get_event_loop().time()}
        
        elif action == 'execute' and self.proserve_client:
            try:
                result = await self.proserve_client.execute(
                    data.get('target'),
                    data.get('method'),
                    **data.get('params', {})
                )
                return {'action': 'result', 'data': result}
            except Exception as e:
                return {'action': 'error', 'error': str(e)}
        
        elif action == 'status':
            return {
                'action': 'status',
                'data': {
                    'service': self.manifest.name,
                    'connections': len(self.websocket_connections),
                    'platform': self.manifest.platform,
                    'isolation_mode': self.manifest.isolation.get('mode', 'none')
                }
            }
        
        return {'action': 'error', 'error': f'Unknown action: {action}'}
    
    async def _generic_handler(self, request, endpoint_config):
        """Generic handler for simple endpoints"""
        action = endpoint_config.get('action', 'echo')
        
        if action == 'echo':
            if request.body_exists:
                data = await request.json()
            else:
                data = dict(request.query)
            return web.json_response({'echo': data})
        
        return web.json_response({'error': 'Not implemented'}, status=501)
    
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
                
                # Add query parameters
                parameters.update(dict(request.query))
                
                # Add path parameters if available
                if hasattr(request, 'match_info'):
                    parameters.update(dict(request.match_info))
                
                # Add body parameters for POST/PUT requests
                if request.body_exists:
                    try:
                        if request.content_type == 'application/json':
                            body_data = await request.json()
                            parameters.update(body_data)
                        elif request.content_type == 'application/x-www-form-urlencoded':
                            form_data = await request.post()
                            parameters.update(dict(form_data))
                    except Exception as e:
                        self.logger.warning(f"Could not parse request body: {e}")
                
                # Merge with endpoint environment variables
                merged_env_vars = {}
                merged_env_vars.update(self.manifest.env_vars)
                merged_env_vars.update(env_vars)
                
                # Execute shell command
                result = await self.shell_handler.execute_shell_command(
                    command=shell_command,
                    parameters=parameters,
                    converter=converter,
                    timeout=timeout,
                    env_vars=merged_env_vars
                )
                
                # Log execution
                self.logger.info(
                    f"Shell command executed",
                    command=shell_command,
                    success=result['success'],
                    converter=converter,
                    execution_time=result.get('execution_time', 0)
                )
                
                # Return appropriate response
                if result['success']:
                    # If converter was used, return converted output
                    if result['converted_output'] is not None:
                        if isinstance(result['converted_output'], (dict, list)):
                            return web.json_response(result['converted_output'])
                        else:
                            return web.Response(
                                text=str(result['converted_output']),
                                content_type='text/plain'
                            )
                    else:
                        # Return raw stdout
                        return web.Response(
                            text=result['stdout'],
                            content_type='text/plain'
                        )
                else:
                    # Return error response
                    error_data = {
                        'error': 'Shell command execution failed',
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
    
    async def run(self):
        """Run the service"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        # Use port from environment if available, otherwise use manifest
        port = int(os.getenv(f"{self.manifest.name.upper().replace('-', '_')}_PORT", self.manifest.port))
        
        site = web.TCPSite(runner, self.manifest.host, port)
        
        self.logger.info(f"Starting {self.manifest.name} v{self.manifest.version} on {self.manifest.host}:{port}")
        
        # Log platform and isolation information
        if self.manifest.platform:
            self.logger.info(f"Platform: {self.manifest.platform}")
        if self.manifest.board:
            self.logger.info(f"Board: {self.manifest.board}")
        
        isolation_mode = self.manifest.isolation.get('mode', 'none')
        self.logger.info(f"Isolation mode: {isolation_mode}")
        
        await site.start()
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            await runner.cleanup()
            self.logger.info("Service stopped")
