"""
ProServe Enhanced Logging System
Advanced logging functionality with structured logs, WebSocket broadcasting, file rotation,
console coordination, and manifest-driven configuration
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Set, List, Union
from datetime import datetime
from pathlib import Path
import threading
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Core logging imports
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

# Optional WebSocket support for log broadcasting
try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import WebSocketResponse
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class LoggingConfig:
    """Enhanced logging configuration from manifest"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Basic settings
        self.level = config.get('level', 'INFO').upper()
        self.format_type = config.get('format', 'structured')  # structured, json, plain
        self.enable_websocket = config.get('enable_websocket', True)
        
        # Console output settings
        self.console_output = config.get('console_output', True)
        self.console_colors = config.get('console_colors', True)
        self.include_timestamps = config.get('include_timestamps', True)
        self.include_caller = config.get('include_caller', False)
        
        # File output settings
        self.file_output = config.get('file_output', False)
        self.log_file = config.get('log_file', '/tmp/proserve.log')
        
        # File rotation settings
        rotation = config.get('rotation', {})
        self.max_size = rotation.get('max_size', '10MB')
        self.backup_count = rotation.get('backup_count', 5)
        self.rotation_type = rotation.get('type', 'size')  # size, time
        self.rotation_when = rotation.get('when', 'midnight')  # for time rotation
        
        # Advanced settings
        self.buffer_size = config.get('buffer_size', 1024)
        self.flush_interval = config.get('flush_interval', 1.0)
        self.async_logging = config.get('async_logging', True)
        
        # Filter settings
        self.exclude_modules = config.get('exclude_modules', [])
        self.include_only = config.get('include_only', [])
        self.min_level_console = config.get('min_level_console', self.level)
        self.min_level_file = config.get('min_level_file', self.level)


class LogContext:
    """Enhanced logging context with service and platform information"""
    
    def __init__(
        self,
        service_name: str,
        manifest_path: Optional[str] = None,
        handler_script: Optional[str] = None,
        isolation_mode: str = "none",
        platform: Optional[str] = None,
        board: Optional[str] = None,
        task_name: Optional[str] = None,
        **kwargs
    ):
        self.service_name = service_name
        self.manifest_path = manifest_path
        self.handler_script = handler_script
        self.isolation_mode = isolation_mode
        self.platform = platform
        self.board = board
        self.task_name = task_name
        self.extra_context = kwargs
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging"""
        context = {
            'service_name': self.service_name,
            'isolation_mode': self.isolation_mode,
            'timestamp': self.timestamp
        }
        
        if self.manifest_path:
            context['manifest_path'] = self.manifest_path
        if self.handler_script:
            context['handler_script'] = self.handler_script
        if self.platform:
            context['platform'] = self.platform
        if self.board:
            context['board'] = self.board
        if self.task_name:
            context['task_name'] = self.task_name
            
        context.update(self.extra_context)
        return context


class EnhancedFileHandler:
    """Enhanced file handler with rotation, buffering, and async support"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.handler: Optional[logging.Handler] = None
        self.buffer: List[str] = []
        self.buffer_lock = threading.Lock()
        self.flush_task: Optional[asyncio.Task] = None
        self.is_running = False
        
    def setup_handler(self) -> Optional[logging.Handler]:
        """Setup appropriate file handler based on configuration"""
        if not self.config.file_output:
            return None
            
        # Ensure log directory exists
        log_file_path = Path(self.config.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup rotation handler
        if self.config.rotation_type == 'size':
            max_bytes = self._parse_size(self.config.max_size)
            handler = RotatingFileHandler(
                filename=self.config.log_file,
                maxBytes=max_bytes,
                backupCount=self.config.backup_count
            )
        elif self.config.rotation_type == 'time':
            handler = TimedRotatingFileHandler(
                filename=self.config.log_file,
                when=self.config.rotation_when,
                backupCount=self.config.backup_count
            )
        else:
            # Simple file handler
            handler = logging.FileHandler(self.config.log_file)
        
        # Set formatter
        if self.config.format_type == 'json':
            formatter = logging.Formatter('%(message)s')
        elif self.config.format_type == 'structured':
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # plain
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        handler.setLevel(getattr(logging, self.config.min_level_file))
        
        self.handler = handler
        return handler
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        if not isinstance(size_str, str):
            return int(size_str)
        
        size_str = size_str.upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                return int(float(size_str[:-len(suffix)]) * multiplier)
        
        return int(size_str)
    
    async def start_async_logging(self):
        """Start async logging with buffering"""
        if not self.config.async_logging or self.is_running:
            return
        
        self.is_running = True
        self.flush_task = asyncio.create_task(self._flush_buffer_periodically())
    
    async def stop_async_logging(self):
        """Stop async logging and flush remaining buffer"""
        self.is_running = False
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        self._flush_buffer()
    
    async def _flush_buffer_periodically(self):
        """Periodically flush log buffer to file"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.flush_interval)
                self._flush_buffer()
            except asyncio.CancelledError:
                break
    
    def _flush_buffer(self):
        """Flush buffered logs to file"""
        if not self.handler or not self.buffer:
            return
        
        with self.buffer_lock:
            for log_entry in self.buffer:
                self.handler.emit(logging.LogRecord(
                    name="proserve",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=log_entry,
                    args=(),
                    exc_info=None
                ))
            self.buffer.clear()
    
    def add_to_buffer(self, log_entry: str):
        """Add log entry to buffer"""
        if not self.config.async_logging:
            return
        
        with self.buffer_lock:
            self.buffer.append(log_entry)
            if len(self.buffer) >= self.config.buffer_size:
                self._flush_buffer()


class LogBroadcaster:
    """WebSocket log broadcaster for real-time log streaming"""
    
    def __init__(self):
        self.connections: Set[WebSocketResponse] = set()
        self.log_buffer: List[Dict] = []
        self.max_buffer_size = 1000
        self.broadcaster_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    def add_connection(self, ws: WebSocketResponse):
        """Add WebSocket connection for log broadcasting"""
        self.connections.add(ws)
        
        # Send buffered logs to new connection
        if self.log_buffer:
            asyncio.create_task(self._send_buffered_logs(ws))
    
    def remove_connection(self, ws: WebSocketResponse):
        """Remove WebSocket connection"""
        self.connections.discard(ws)
    
    async def _send_buffered_logs(self, ws: WebSocketResponse):
        """Send buffered logs to a specific connection"""
        try:
            for log_entry in self.log_buffer[-50:]:  # Send last 50 logs
                await ws.send_str(json.dumps(log_entry))
        except Exception:
            self.remove_connection(ws)
    
    async def broadcast_log(self, log_entry: Dict):
        """Broadcast log entry to all connected WebSocket clients"""
        if not self.connections:
            # Buffer logs even when no connections
            self.log_buffer.append(log_entry)
            if len(self.log_buffer) > self.max_buffer_size:
                self.log_buffer.pop(0)
            return
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)
        
        # Broadcast to all connections
        disconnected = set()
        for ws in self.connections:
            try:
                await ws.send_str(json.dumps(log_entry))
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected connections
        self.connections -= disconnected
    
    async def start_broadcaster(self):
        """Start the log broadcaster"""
        if self.is_running:
            return
        
        self.is_running = True
        # Broadcaster is event-driven, no background task needed
    
    async def stop_broadcaster(self):
        """Stop the log broadcaster"""
        self.is_running = False
        
        # Close all connections
        for ws in list(self.connections):
            try:
                await ws.close()
            except Exception:
                pass
        
        self.connections.clear()


# Global log broadcaster instance
_log_broadcaster: Optional[LogBroadcaster] = None


def get_log_broadcaster() -> Optional[LogBroadcaster]:
    """Get the global log broadcaster instance"""
    global _log_broadcaster
    if _log_broadcaster is None and WEBSOCKET_AVAILABLE:
        _log_broadcaster = LogBroadcaster()
    return _log_broadcaster


class ProServeLogProcessor:
    """Custom log processor for ProServe with WebSocket broadcasting"""
    
    def __init__(self, broadcaster: Optional[LogBroadcaster] = None):
        self.broadcaster = broadcaster or get_log_broadcaster()
    
    def __call__(self, logger, method_name, event_dict):
        """Process log entry and broadcast if WebSocket broadcaster available"""
        
        # Add ProServe-specific fields
        event_dict['framework'] = 'proserve'
        event_dict['log_level'] = method_name.upper()
        event_dict['timestamp'] = datetime.utcnow().isoformat()
        
        # Broadcast to WebSocket connections if available
        if self.broadcaster and self.broadcaster.is_running:
            log_entry = {
                'type': 'log',
                'level': method_name.upper(),
                'message': event_dict.get('event', ''),
                'timestamp': event_dict['timestamp'],
                'context': event_dict
            }
            
            # Schedule broadcast (non-blocking)
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.broadcaster.broadcast_log(log_entry))
            except RuntimeError:
                # No event loop running, skip broadcast
                pass
        
        return event_dict


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
    
    # Create enhanced logging configuration
    config = LoggingConfig(logging_config)
    
    # Override config with explicit parameters
    if debug:
        config.level = 'DEBUG'
        config.include_caller = True
    if console_output is not None:
        config.console_output = console_output
    if json_output:
        config.format_type = 'json'
    if log_file:
        config.file_output = True
        config.log_file = log_file
    
    # Create log context
    context = LogContext(
        service_name=service_name,
        manifest_path=manifest_path,
        isolation_mode=isolation_mode,
        platform=platform,
        board=board,
        **kwargs
    )
    
    # Setup enhanced file handler
    file_handler_manager = EnhancedFileHandler(config)
    file_handler = file_handler_manager.setup_handler()
    
    # Configure processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        add_log_level,
        TimeStamper(fmt="ISO" if config.include_timestamps else None),
    ]
    
    # Add ProServe log processor for WebSocket broadcasting
    if enable_websocket_broadcast and config.enable_websocket:
        processors.append(ProServeLogProcessor())
    
    # Add callsite information if requested
    if config.include_caller or debug:
        processors.append(CallsiteParameterAdder())
    
    # Configure output format based on config
    if config.format_type == 'json':
        processors.append(JSONRenderer())
    elif config.format_type == 'structured':
        processors.append(structlog.dev.ConsoleRenderer(colors=config.console_colors))
    else:  # plain
        processors.append(structlog.dev.ConsoleRenderer(colors=False))
    
    # Configure structlog
    configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Setup console handler if enabled
    if config.console_output:
        if RICH_AVAILABLE and config.console_colors and config.format_type != 'json':
            console = Console()
            console_handler = RichHandler(
                console=console,
                show_time=config.include_timestamps,
                show_path=config.include_caller,
                enable_link_path=config.include_caller
            )
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            if config.format_type == 'json':
                formatter = logging.Formatter('%(message)s')
            elif config.format_type == 'structured':
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            else:
                formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(formatter)
        
        console_handler.setLevel(getattr(logging, config.min_level_console))
        root_logger.addHandler(console_handler)
    
    # Add enhanced file handler if configured
    if file_handler:
        root_logger.addHandler(file_handler)
        # Start async logging if enabled
        if config.async_logging:
            asyncio.create_task(file_handler_manager.start_async_logging())
    
    # Set root logger level
    root_logger.setLevel(getattr(logging, config.level))
    
    # Create bound logger with service context
    logger = get_logger(service_name)
    bound_logger = logger.bind(**context.to_dict())
    
    # Store config and file handler for later access
    bound_logger._proserve_config = config
    bound_logger._proserve_file_handler = file_handler_manager
    
    return bound_logger


def create_logger(name: str, **context) -> structlog.BoundLogger:
    """Create a logger with optional context"""
    logger = get_logger(name)
    if context:
        return logger.bind(**context)
    return logger


def setup_log_endpoints(app: web.Application, websocket_path: str = "/logs"):
    """Setup WebSocket endpoints for log streaming"""
    if not WEBSOCKET_AVAILABLE:
        return app
    
    broadcaster = get_log_broadcaster()
    if not broadcaster:
        return app
    
    async def websocket_logs_handler(request):
        """WebSocket handler for log streaming"""
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        broadcaster.add_connection(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        # Handle client messages (e.g., log level changes)
                        if data.get('action') == 'set_log_level':
                            level = data.get('level', 'INFO')
                            logging.getLogger().setLevel(getattr(logging, level.upper()))
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    break
        except Exception:
            pass
        finally:
            broadcaster.remove_connection(ws)
        
        return ws
    
    # Add WebSocket route
    app.router.add_get(websocket_path, websocket_logs_handler)
    
    return app


# Convenience functions for common logging patterns
def log_service_start(logger: structlog.BoundLogger, service_name: str, version: str, host: str, port: int):
    """Log service startup information"""
    logger.info(
        "Service starting",
        service=service_name,
        version=version,
        host=host,
        port=port,
        event_type="service_start"
    )


def log_service_stop(logger: structlog.BoundLogger, service_name: str):
    """Log service shutdown information"""
    logger.info(
        "Service stopping",
        service=service_name,
        event_type="service_stop"
    )


def log_script_execution(
    logger: structlog.BoundLogger,
    script_path: str,
    isolation_mode: str,
    execution_time: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None
):
    """Log script execution information"""
    log_data = {
        "script_path": script_path,
        "isolation_mode": isolation_mode,
        "event_type": "script_execution",
        "success": success
    }
    
    if execution_time is not None:
        log_data["execution_time"] = execution_time
    
    if error:
        log_data["error"] = error
        logger.error("Script execution failed", **log_data)
    else:
        logger.info("Script execution completed", **log_data)


def log_platform_info(
    logger: structlog.BoundLogger,
    platform: str,
    board: Optional[str] = None,
    isolation_mode: str = "none"
):
    """Log platform and board information"""
    log_data = {
        "platform": platform,
        "isolation_mode": isolation_mode,
        "event_type": "platform_info"
    }
    
    if board:
        log_data["board"] = board
    
    logger.info("Platform configuration", **log_data)


def log_websocket_connection(logger: structlog.BoundLogger, action: str, connection_count: int):
    """Log WebSocket connection events"""
    logger.info(
        f"WebSocket connection {action}",
        action=action,
        connection_count=connection_count,
        event_type="websocket_connection"
    )


# Legacy compatibility functions (for EDPMT migration)
def create_context_from_manifest(service_name: str, **kwargs) -> LogContext:
    """Create log context from manifest information (EDPMT compatibility)"""
    return LogContext(service_name=service_name, **kwargs)


def setup_enhanced_logging(**kwargs) -> structlog.BoundLogger:
    """Enhanced logging setup (EDPMT compatibility)"""
    return setup_logging(**kwargs)
