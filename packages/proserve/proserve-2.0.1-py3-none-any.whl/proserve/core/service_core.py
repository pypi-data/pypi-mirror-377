"""
ProServe Service Core - Basic Service Infrastructure
Handles service initialization, lifecycle management, and core functionality
"""

import os
import structlog
from typing import Dict, Any, Union, Optional
from aiohttp import web
from dotenv import load_dotenv

from .manifest import ServiceManifest
# Updated import for new modular architecture
try:
    from ..isolation.platforms.platform_config import get_isolation_manager as ProcessIsolationManager
except ImportError:
    # Backward compatibility fallback
    class ProcessIsolationManager:
        """Backward compatibility isolation manager"""
        def __init__(self, *args, **kwargs):
            pass
from .shell import ShellCommandHandler

# ProServe logging imports
try:
    from .logging import setup_logging, create_logger
    PROSERVE_LOGGING_AVAILABLE = True
except ImportError:
    PROSERVE_LOGGING_AVAILABLE = False
    def setup_logging(**kwargs):
        return structlog.get_logger()
    def create_logger(name):
        return structlog.get_logger(name)


class ServiceCore:
    """Core service infrastructure for ProServe applications"""
    
    def __init__(self, manifest: Union[ServiceManifest, str, Dict]):
        """Initialize service core with manifest configuration"""
        # Handle different manifest input types
        if isinstance(manifest, str):
            self.manifest = ServiceManifest.from_yaml(manifest)
        elif isinstance(manifest, dict):
            self.manifest = ServiceManifest.from_dict(manifest)
        else:
            self.manifest = manifest
            
        # Core components
        self.app = web.Application()
        self.logger = self._setup_logging()
        
        # Managers and handlers
        self.isolation_manager = ProcessIsolationManager(self.manifest.isolation)
        self.shell_handler = ShellCommandHandler(
            shell_config=getattr(self.manifest, 'shell_config', {}),
            converters=getattr(self.manifest, 'converters', {})
        )
        
        # State tracking
        self.websocket_connections = set()
        self.background_task_handles = []
        self.proserve_client = None
        
        # Initialize environment and features
        load_dotenv()
        self._load_env_vars()
        self._setup_features()
        
        # Setup app lifecycle
        self.app.on_startup.append(self._on_startup)
        self.app.on_cleanup.append(self._on_cleanup)
    
    def _setup_logging(self) -> structlog.BoundLogger:
        """Setup enhanced structured logging with contextual information"""
        debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        # Create enhanced logging context
        manifest_path = getattr(self.manifest, '_manifest_path', None)
        isolation_mode = self.manifest.isolation.get('mode', 'none') if self.manifest.isolation else 'none'
        
        if PROSERVE_LOGGING_AVAILABLE:
            logger = setup_logging(
                service_name=self.manifest.name,
                manifest_path=manifest_path,
                isolation_mode=isolation_mode,
                debug=debug_mode
            )
            logger.info("ProServe logging initialized", service_name=self.manifest.name)
            return logger
        else:
            logger = structlog.get_logger(self.manifest.name)
            logger.info("Basic logging initialized", service_name=self.manifest.name)
            return logger
    
    def _load_env_vars(self):
        """Load and validate environment variables from manifest"""
        if not hasattr(self.manifest, 'env_vars'):
            return
            
        for env_var in self.manifest.env_vars or []:
            var_name = env_var.get('name')
            default_value = env_var.get('default')
            required = env_var.get('required', False)
            
            value = os.getenv(var_name, default_value)
            
            if required and value is None:
                raise ValueError(f"Required environment variable {var_name} not set")
            
            if value is not None:
                os.environ[var_name] = str(value)
                self.logger.debug(f"Environment variable loaded: {var_name}")
    
    def _setup_features(self):
        """Setup service features based on manifest configuration"""
        # CORS setup
        if self.manifest.enable_cors:
            import aiohttp_cors
            self.cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            self.logger.info("CORS enabled for all origins")
        
        # Health check endpoints (with fallback for compatibility)
        enable_health_check = getattr(self.manifest, 'enable_health_check', True)
        if enable_health_check:
            self.app.router.add_get('/health', self._health_handler)
            self.app.router.add_get('/api/health', self._health_handler)
            self.logger.info("Health check endpoints registered")
        
        # Metrics endpoints (with fallback for compatibility)
        enable_metrics = getattr(self.manifest, 'enable_metrics', True)
        if enable_metrics:
            self.app.router.add_get('/metrics', self._metrics_handler)
            self.logger.info("Metrics endpoint registered")
    
    async def _health_handler(self, request):
        """Handle health check requests"""
        return web.json_response({
            'status': 'healthy',
            'service': self.manifest.name,
            'version': getattr(self.manifest, 'version', '1.0.0'),
            'platform': self.manifest.platform,
            'isolation_mode': self.manifest.isolation.get('mode', 'none'),
            'connections': len(self.websocket_connections)
        })
    
    async def _metrics_handler(self, request):
        """Handle metrics requests"""
        return web.json_response({
            'service': self.manifest.name,
            'connections': len(self.websocket_connections),
            'background_tasks': len(self.background_task_handles),
            'platform': self.manifest.platform
        })
    
    async def _on_startup(self, app):
        """Service startup handler"""
        self.logger.info(f"Starting ProServe service: {self.manifest.name}")
        
        # Initialize ProServe client if required
        if self.manifest.requires_proserve or self.manifest.requires_edpmt:
            await self._init_proserve_client()
    
    async def _on_cleanup(self, app):
        """Service cleanup handler"""
        self.logger.info(f"Shutting down ProServe service: {self.manifest.name}")
        
        # Cancel background tasks
        for task in self.background_task_handles:
            if not task.done():
                task.cancel()
        
        # Close WebSocket connections
        for ws in list(self.websocket_connections):
            await ws.close()
        
        self.logger.info("Service cleanup completed")
    
    async def _init_proserve_client(self):
        """Initialize ProServe client connection (backward compatibility)"""
        try:
            # This would be implemented based on your specific ProServe client needs
            self.logger.info("ProServe client would be initialized here")
            # self.proserve_client = ProServeClient(...)
        except Exception as e:
            self.logger.error(f"Failed to initialize ProServe client: {e}")
    
    def get_app(self) -> web.Application:
        """Get the aiohttp application instance"""
        return self.app
    
    def get_logger(self) -> structlog.BoundLogger:
        """Get the service logger"""
        return self.logger
