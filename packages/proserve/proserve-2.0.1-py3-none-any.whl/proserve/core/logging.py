"""
ProServe Logging System - WML Integration
Provides unified logging capabilities for ProServe services using the WML logging system.

This module serves as the main interface for logging functionality,
integrating all components from the WML package.
"""

import asyncio
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Import wmlog logging system
from wmlog import WMLLogger, LoggingConfig as WMLLoggingConfig, LogContext as WMLLogContext

# Optional WebSocket support for backward compatibility
try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import WebSocketResponse
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


# Backward compatibility aliases
LoggingConfig = WMLLoggingConfig
LogContext = WMLLogContext


# Backward compatibility class for ProServe LoggingConfig
class ProServeLoggingConfig:
    """ProServe logging configuration - now uses WML logging system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Map ProServe config to WML logging config
        self.wml_config = WMLLoggingConfig(
            service_name=config.get('service_name', 'proserve'),
            log_level=config.get('level', 'info'),
            console_enabled=config.get('console_output', True),
            console_format='rich' if config.get('console_colors', True) else 'plain',
            file_enabled=config.get('file_output', False),
            file_path=config.get('log_file', '/tmp/proserve.log'),
            websocket_enabled=config.get('websocket_enabled', False),
            include_timestamp=True,
            include_caller=config.get('debug', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'service_name': self.wml_config.service_name,
            'level': self.wml_config.log_level,
            'console_output': self.wml_config.console_enabled,
            'file_output': self.wml_config.file_enabled,
            'log_file': self.wml_config.file_path,
            'websocket_enabled': self.wml_config.websocket_enabled
        }


# Backward compatibility class for ProServe LogContext
class ProServeLogContext:
    """ProServe logging context - now uses WML logging system"""
    
    def __init__(self, service_name: str = "proserve", **kwargs):
        self.wml_context = WMLLogContext(
            service_name=service_name,
            custom_fields=kwargs
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return self.wml_context.to_dict()


# Global logger instance for ProServe
_proserve_logger: Optional[WMLLogger] = None


def get_proserve_logger(config: Optional[Dict[str, Any]] = None) -> WMLLogger:
    """Get the global ProServe logger instance"""
    global _proserve_logger
    
    if _proserve_logger is None:
        # Create default config if none provided
        if config is None:
            config = {'service_name': 'proserve'}
        
        proserve_config = ProServeLoggingConfig(config)
        context = WMLLogContext(service_name=proserve_config.wml_config.service_name)
        _proserve_logger = WMLLogger.get_logger(proserve_config.wml_config, context)
    
    return _proserve_logger


def setup_file_logging(log_file_path: str = "/tmp/proserve.log", **kwargs):
    """Backward compatibility wrapper for file logging"""
    config = {
        'service_name': kwargs.get('service_name', 'proserve'),
        'file_output': True,
        'log_file': log_file_path,
        'level': 'DEBUG' if kwargs.get('debug', False) else 'INFO'
    }
    proserve_config = ProServeLoggingConfig(config)
    context = WMLLogContext(service_name=config['service_name'], **kwargs)
    return WMLLogger.get_logger(proserve_config.wml_config, context)


async def start_async_logging(**kwargs):
    """Backward compatibility wrapper for async logging"""
    pass  # WML system handles async logging automatically


def setup_websocket_endpoints(app, websocket_path: str = '/ws/logs'):
    """Backward compatibility wrapper for WebSocket log streaming"""
    
    if not WEBSOCKET_AVAILABLE:
        return
    
    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        async for msg in ws:
            if msg.type == WSMsgType.ERROR:
                break
        
        return ws
    
    app.router.add_get(websocket_path, websocket_handler)
    return app


def setup_logging(
    service_name: str = "proserve",
    log_level: str = "INFO", 
    log_file: Optional[str] = None,
    console_output: bool = True,
    websocket_enabled: bool = False,
    websocket_port: int = 8765,
    debug: bool = False,
    **kwargs
) -> WMLLogger:
    """
    Setup ProServe logging system using WML - main interface function
    
    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Enable console logging
        websocket_enabled: Enable WebSocket log streaming
        websocket_port: Port for WebSocket server
        debug: Enable debug mode
        **kwargs: Additional configuration options
        
    Returns:
        WML Logger instance with ProServe context
    """
    
    # Create WML configuration
    config = {
        'service_name': service_name,
        'level': log_level,
        'console_output': console_output,
        'file_output': bool(log_file),
        'log_file': log_file or '/tmp/proserve.log',
        'websocket_enabled': websocket_enabled
    }
    
    proserve_config = ProServeLoggingConfig(config)
    context = WMLLogContext(
        service_name=service_name,
        custom_fields=kwargs
    )
    return WMLLogger.get_logger(proserve_config.wml_config, context)


def create_logger(name: str, **context):
    """Create a logger with optional context - WML integration"""
    config = {
        'service_name': name,
        'level': 'DEBUG' if context.get('debug', False) else 'INFO',
        'console_output': True,
        'file_output': False
    }
    proserve_config = ProServeLoggingConfig(config)
    wml_context = WMLLogContext(service_name=name, **context)
    return WMLLogger.get_logger(proserve_config.wml_config, wml_context)


def setup_log_endpoints(app, websocket_path: str = '/ws/logs', **kwargs):
    """Setup WebSocket endpoints for log streaming - WML system integration"""
    return setup_websocket_endpoints(app, websocket_path)


# Convenience functions for backward compatibility
def setup_simple_logging(service_name: str, debug: bool = False, log_file: Optional[str] = None) -> WMLLogger:
    """Setup simple logging configuration"""
    return setup_logging(service_name=service_name, debug=debug, log_file=log_file)

def log_service_start(logger: WMLLogger, service_name: str, port: int = None, **kwargs):
    """Log service start event"""
    logger.logger.info("Service starting", 
                      service_name=service_name, 
                      port=port, 
                      **kwargs)

def log_service_stop(logger: WMLLogger, service_name: str, **kwargs):
    """Log service stop event"""
    logger.logger.info("Service stopping", 
                      service_name=service_name, 
                      **kwargs)

def log_endpoint_access(logger: WMLLogger, method: str, path: str, status: int = None, **kwargs):
    """Log endpoint access"""
    logger.logger.info("Endpoint access", 
                      method=method, 
                      path=path, 
                      status=status, 
                      **kwargs)

def log_background_task(logger: WMLLogger, task_name: str, status: str = "started", **kwargs):
    """Log background task events"""
    logger.logger.info("Background task", 
                      task_name=task_name, 
                      status=status, 
                      **kwargs)

def log_error_with_context(logger: WMLLogger, error: Exception, context: dict = None, **kwargs):
    """Log error with context information"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        **kwargs
    }
    logger.logger.error("Error occurred", **error_info)


# Simplified convenience functions using global logger
def info(message: str, **context):
    """Log info message"""
    logger = get_proserve_logger()
    logger.logger.info(message, **context)


def error(message: str, **context):
    """Log error message"""
    logger = get_proserve_logger()
    logger.logger.error(message, **context)


def debug(message: str, **context):
    """Log debug message"""
    logger = get_proserve_logger()
    logger.logger.debug(message, **context)


def warning(message: str, **context):
    """Log warning message"""
    logger = get_proserve_logger()
    logger.logger.warning(message, **context)


# Export main functions for backward compatibility
__all__ = [
    'setup_logging',
    'create_logger', 
    'ProServeLoggingConfig',
    'ProServeLogContext',
    'get_proserve_logger',
    'setup_file_logging',
    'setup_log_endpoints',
    'info',
    'error',
    'debug', 
    'warning'
]
