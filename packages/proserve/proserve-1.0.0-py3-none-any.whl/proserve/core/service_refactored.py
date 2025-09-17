"""
ProServe Service - Refactored Modular Version
Main service class using composition of focused components for better maintainability
"""

from typing import Dict, Any, Union, Optional
from aiohttp import web
import structlog

from .manifest import ServiceManifest
from .service_core import ServiceCore
from .endpoint_manager import EndpointManager
from .task_manager import BackgroundTaskManager
from .static_handler import StaticFileHandler


class ProServeService:
    """
    Refactored ProServe service using modular components
    
    This is a drop-in replacement for the original ProServeService class,
    but with much better separation of concerns and testability.
    """
    
    def __init__(self, manifest: Union[ServiceManifest, str, Dict]):
        """Initialize service with modular components"""
        # Initialize core service infrastructure
        self.service_core = ServiceCore(manifest)
        self.manifest = self.service_core.manifest
        self.logger = self.service_core.get_logger()
        
        # Initialize component managers
        self.endpoint_manager = EndpointManager(self.service_core, self.manifest)
        self.task_manager = BackgroundTaskManager(self.service_core, self.manifest)
        self.static_handler = StaticFileHandler(self.service_core, self.manifest)
        
        # Setup complete service
        self._setup_service()
        
        self.logger.info(f"ProServe service initialized: {self.manifest.name}")
    
    def _setup_service(self):
        """Setup the complete service using all components"""
        # Register all endpoints
        self.endpoint_manager.register_all_endpoints()
        
        # Setup fallback system integration if available
        self._setup_fallback_integration()
    
    def _setup_fallback_integration(self):
        """Setup fallback system integration on startup"""
        async def integrate_fallback(app):
            try:
                from .service_fallback import integrate_fallback_system
                fallback_manager = await integrate_fallback_system(self)
                self.fallback_manager = fallback_manager
                if fallback_manager:
                    self.logger.info("Fallback system integrated successfully")
            except ImportError:
                self.logger.info("Fallback system not available")
            except Exception as e:
                self.logger.error(f"Failed to integrate fallback system: {e}")
        
        self.service_core.app.on_startup.append(integrate_fallback)
    
    async def run(self, host: str = '0.0.0.0', port: int = 8000, **kwargs):
        """Run the service"""
        # Setup background tasks
        await self.task_manager.setup_background_tasks()
        
        # Create and start web server
        runner = web.AppRunner(self.service_core.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        self.logger.info(f"ProServe service '{self.manifest.name}' running on http://{host}:{port}")
        
        return runner, site
    
    async def stop(self, runner=None, site=None):
        """Stop the service gracefully"""
        self.logger.info(f"Stopping ProServe service: {self.manifest.name}")
        
        # Stop background tasks
        await self.task_manager.stop_all_tasks()
        
        # Close WebSocket connections
        for ws in list(self.service_core.websocket_connections):
            await ws.close()
        
        # Cleanup web server
        if site:
            await site.stop()
        if runner:
            await runner.cleanup()
        
        self.logger.info("Service stopped successfully")
    
    # Backward compatibility methods - delegate to appropriate components
    
    @property
    def app(self) -> web.Application:
        """Get the aiohttp application (backward compatibility)"""
        return self.service_core.get_app()
    
    @property
    def websocket_connections(self):
        """Get WebSocket connections (backward compatibility)"""
        return self.service_core.websocket_connections
    
    @property
    def background_task_handles(self):
        """Get background task handles (backward compatibility)"""
        return self.task_manager.task_handles
    
    @property
    def isolation_manager(self):
        """Get isolation manager (backward compatibility)"""
        return self.service_core.isolation_manager
    
    @property
    def shell_handler(self):
        """Get shell handler (backward compatibility)"""
        return self.service_core.shell_handler
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information"""
        return {
            'service': {
                'name': self.manifest.name,
                'version': getattr(self.manifest, 'version', '1.0.0'),
                'platform': self.manifest.platform,
                'isolation_mode': self.manifest.isolation.get('mode', 'none')
            },
            'endpoints': self.endpoint_manager.get_registered_endpoints(),
            'background_tasks': self.task_manager.get_task_status(),
            'static_files': self.static_handler.get_static_info(),
            'connections': {
                'websocket_count': len(self.service_core.websocket_connections)
            },
            'features': {
                'cors_enabled': self.manifest.enable_cors,
                'health_check_enabled': self.manifest.enable_health_check,
                'metrics_enabled': self.manifest.enable_metrics
            }
        }
    
    # Component access methods for advanced usage
    
    def get_endpoint_manager(self) -> EndpointManager:
        """Get the endpoint manager for advanced endpoint operations"""
        return self.endpoint_manager
    
    def get_task_manager(self) -> BackgroundTaskManager:
        """Get the task manager for advanced background task operations"""
        return self.task_manager
    
    def get_static_handler(self) -> StaticFileHandler:
        """Get the static handler for advanced static file operations"""
        return self.static_handler
    
    def get_service_core(self) -> ServiceCore:
        """Get the service core for low-level operations"""
        return self.service_core


# Backward compatibility - keep the original class name available
ProServeServiceLegacy = ProServeService
