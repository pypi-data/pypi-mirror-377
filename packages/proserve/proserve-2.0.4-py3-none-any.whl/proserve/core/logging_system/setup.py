"""
ProServe Logging Setup - Main Logging System Initialization
Coordinates all logging components to provide comprehensive logging setup from manifests
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
import structlog
from structlog import configure, get_logger
from structlog.processors import JSONRenderer, TimeStamper, add_log_level, CallsiteParameterAdder

# Optional rich console support
try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install as install_rich_traceback
    RICH_AVAILABLE = True
    install_rich_traceback()
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    RichHandler = None

from .config import LoggingConfig, LogContext, create_default_config, create_config_from_env
from .file_handler import EnhancedFileHandler, create_file_handler, start_async_file_logging
from .broadcaster import (
    LogBroadcaster, ProServeLogProcessor, get_log_broadcaster, 
    start_log_broadcasting, setup_log_endpoints, is_websocket_available
)
from .utilities import create_context_logger


def setup_logging(
    service_name: str,
    manifest_path: Optional[str] = None,
    isolation_mode: str = "none",
    platform: Optional[str] = None,
    board: Optional[str] = None,
    debug: bool = False,
    console_output: bool = True,
    json_output: bool = False,
    log_file: Optional[str] = None,
    enable_websocket_broadcast: bool = True,
    logging_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> structlog.BoundLogger:
    """
    Setup enhanced ProServe logging system with manifest-driven configuration
    
    Args:
        service_name: Name of the service
        manifest_path: Path to the service manifest
        isolation_mode: Current isolation mode
        platform: Target platform (e.g., rp2040, esp32)
        board: Specific board configuration
        debug: Enable debug logging (overrides config)
        console_output: Enable console output (overrides config)
        json_output: Use JSON format for logs (overrides config)
        log_file: Optional log file path (overrides config)
        enable_websocket_broadcast: Enable WebSocket log broadcasting
        logging_config: Enhanced logging configuration from manifest
        **kwargs: Additional context parameters
    
    Returns:
        Configured structlog logger with enhanced file and console handling
    """
    
    # Create configuration from manifest or defaults
    if logging_config:
        config = LoggingConfig.from_dict(logging_config)
    else:
        config = create_default_config()
    
    # Apply parameter overrides
    if debug:
        config.level = "DEBUG"
        config.console_level = "DEBUG"
        config.file_level = "DEBUG"
    
    if not console_output:
        config.console_enabled = False
    
    if json_output:
        config.format = "json"
        config.console_format = "json"
        config.file_format = "json"
    
    if log_file:
        config.file_enabled = True
        config.file_path = log_file
    
    if not enable_websocket_broadcast:
        config.websocket_enabled = False
    
    # Validate configuration
    validation_errors = config.validate()
    if validation_errors:
        print(f"Logging configuration errors: {validation_errors}")
        # Continue with defaults for invalid settings
    
    # Setup console logging
    console_handler = None
    if config.console_enabled:
        console_handler = _setup_console_handler(config)
    
    # Setup file logging
    file_handler = None
    if config.file_enabled:
        file_handler = create_file_handler("main", config)
    
    # Setup WebSocket broadcasting
    log_broadcaster = None
    if config.websocket_enabled and is_websocket_available():
        log_broadcaster = get_log_broadcaster(config)
    
    # Setup structlog configuration
    processors = []
    
    # Add timestamp processor
    if config.include_timestamp:
        processors.append(TimeStamper(fmt="iso"))
    
    # Add log level processor
    if config.include_level:
        processors.append(add_log_level)
    
    # Add caller information if requested
    if config.include_caller:
        processors.append(CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ))
    
    # Add custom ProServe processor for WebSocket broadcasting
    if log_broadcaster:
        processors.append(ProServeLogProcessor(log_broadcaster))
    
    # Add final renderer based on format
    if config.format == "json":
        processors.append(JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add console handler if enabled
    if console_handler:
        root_logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if file_handler and file_handler.handler:
        root_logger.addHandler(file_handler.handler)
    
    # Filter out excluded loggers
    for logger_name in config.exclude_loggers:
        excluded_logger = logging.getLogger(logger_name)
        excluded_logger.setLevel(logging.WARNING)
    
    # Create service context
    context = LogContext(
        service_name=service_name,
        manifest_path=manifest_path,
        isolation_mode=isolation_mode,
        platform=platform,
        board=board,
        **kwargs
    )
    
    # Create and configure main logger
    logger = get_logger(service_name)
    bound_logger = context.bind_to_logger(logger)
    
    # Log setup completion
    bound_logger.info(
        "Logging system initialized",
        console_enabled=config.console_enabled,
        file_enabled=config.file_enabled,
        websocket_enabled=config.websocket_enabled,
        log_level=config.level
    )
    
    return bound_logger


def _setup_console_handler(config: LoggingConfig) -> logging.Handler:
    """Setup console handler based on configuration"""
    
    if RICH_AVAILABLE and config.rich_console:
        # Use Rich console handler
        console = Console()
        handler = RichHandler(
            console=console,
            show_time=config.include_timestamp,
            show_level=config.include_level,
            show_path=config.include_caller,
            markup=True,
            rich_tracebacks=True
        )
    else:
        # Use standard console handler
        handler = logging.StreamHandler(sys.stdout)
    
    # Set level
    handler.setLevel(getattr(logging, config.console_level.upper()))
    
    # Set formatter for non-Rich handlers
    if not (RICH_AVAILABLE and config.rich_console):
        if config.console_format == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            if config.include_caller:
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
                )
        
        handler.setFormatter(formatter)
    
    return handler


async def initialize_async_logging(service_name: str = "proserve", **kwargs):
    """Initialize async components of the logging system"""
    
    # Start async file logging
    await start_async_file_logging()
    
    # Start WebSocket broadcasting
    await start_log_broadcasting()
    
    logger = get_logger(service_name)
    logger.debug("Async logging components initialized")


async def shutdown_logging():
    """Shutdown logging system and cleanup resources"""
    from .file_handler import stop_async_file_logging, cleanup_all_file_handlers
    from .broadcaster import stop_log_broadcasting
    
    logger = get_logger("proserve.shutdown")
    logger.info("Shutting down logging system")
    
    try:
        # Stop async file logging
        await stop_async_file_logging()
        
        # Stop WebSocket broadcasting
        await stop_log_broadcasting()
        
        # Cleanup file handlers
        cleanup_all_file_handlers()
        
        logger.info("Logging system shutdown complete")
        
    except Exception as e:
        print(f"Error during logging shutdown: {e}")


def create_logger(name: str, **context) -> structlog.BoundLogger:
    """Create a logger with optional context"""
    logger = get_logger(name)
    return logger.bind(**context) if context else logger


def reconfigure_logging(new_config: Dict[str, Any], service_name: str = "proserve"):
    """Reconfigure logging system with new settings"""
    
    logger = get_logger(service_name)
    logger.info("Reconfiguring logging system", new_config=new_config)
    
    try:
        # This would require a more sophisticated approach to avoid disruption
        # For now, log the intent
        logger.warning("Dynamic reconfiguration not yet implemented")
        
    except Exception as e:
        logger.error("Failed to reconfigure logging", error=str(e))


def get_logging_status() -> Dict[str, Any]:
    """Get current logging system status"""
    from .file_handler import get_file_manager
    from .broadcaster import get_broadcaster_stats
    
    file_manager = get_file_manager()
    broadcaster_stats = get_broadcaster_stats()
    
    # Get standard library logging info
    root_logger = logging.getLogger()
    
    return {
        "root_logger_level": logging.getLevelName(root_logger.level),
        "handlers_count": len(root_logger.handlers),
        "file_handlers": file_manager.get_all_file_info(),
        "websocket_broadcaster": broadcaster_stats,
        "rich_available": RICH_AVAILABLE,
        "websocket_available": is_websocket_available()
    }


def configure_logging_from_env():
    """Configure logging from environment variables"""
    config = create_config_from_env()
    
    service_name = os.getenv('PROSERVE_SERVICE_NAME', 'proserve')
    
    return setup_logging(
        service_name=service_name,
        logging_config=config.to_dict()
    )


# Legacy compatibility functions
def setup_enhanced_logging(**kwargs):
    """Enhanced logging setup (EDPMT compatibility)"""
    return setup_logging(**kwargs)


def create_context_from_manifest(service_name: str, **kwargs) -> LogContext:
    """Create log context from manifest information (EDPMT compatibility)"""
    return LogContext(service_name=service_name, **kwargs)


# Convenience setup functions
def setup_simple_logging(service_name: str, debug: bool = False) -> structlog.BoundLogger:
    """Setup simple logging for basic use cases"""
    return setup_logging(
        service_name=service_name,
        debug=debug,
        console_output=True,
        file_enabled=False,
        enable_websocket_broadcast=False
    )


def setup_production_logging(service_name: str, log_file: str) -> structlog.BoundLogger:
    """Setup production logging with file output and WebSocket broadcasting"""
    return setup_logging(
        service_name=service_name,
        debug=False,
        console_output=True,
        log_file=log_file,
        json_output=True,
        enable_websocket_broadcast=True
    )


def setup_development_logging(service_name: str) -> structlog.BoundLogger:
    """Setup development logging with rich console output"""
    return setup_logging(
        service_name=service_name,
        debug=True,
        console_output=True,
        file_enabled=False,
        enable_websocket_broadcast=True
    )
