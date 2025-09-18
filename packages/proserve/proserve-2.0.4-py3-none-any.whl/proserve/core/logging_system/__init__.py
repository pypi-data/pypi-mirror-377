"""
ProServe Logging System - Modular Logging Components
Refactored from monolithic logging.py into focused, testable logging modules
"""

from .config import (
    LoggingConfig, LogContext, create_default_config, create_config_from_env, merge_configs
)
from .file_handler import (
    EnhancedFileHandler, LogFileManager, create_file_handler, get_file_handler,
    start_async_file_logging, stop_async_file_logging, cleanup_all_file_handlers
)
from .broadcaster import (
    LogBroadcaster, ProServeLogProcessor, get_log_broadcaster, setup_log_endpoints,
    start_log_broadcasting, stop_log_broadcasting, is_websocket_available, get_broadcaster_stats
)
from .utilities import (
    log_service_start, log_service_stop, log_script_execution, log_platform_info,
    log_websocket_connection, log_endpoint_access, log_database_operation,
    log_background_task, log_file_operation, log_network_request, log_security_event,
    log_performance_metric, log_resource_usage, create_context_logger, create_request_logger,
    create_task_logger, sanitize_log_data, format_duration, format_bytes, truncate_message,
    extract_stack_info, log_with_context, log_exception, create_logger_with_context
)
from .setup import (
    setup_logging, initialize_async_logging, shutdown_logging, create_logger,
    reconfigure_logging, get_logging_status, configure_logging_from_env,
    setup_simple_logging, setup_production_logging, setup_development_logging
)

__all__ = [
    # Configuration
    'LoggingConfig', 'LogContext', 'create_default_config', 'create_config_from_env', 'merge_configs',
    
    # File Handling
    'EnhancedFileHandler', 'LogFileManager', 'create_file_handler', 'get_file_handler',
    'start_async_file_logging', 'stop_async_file_logging', 'cleanup_all_file_handlers',
    
    # WebSocket Broadcasting
    'LogBroadcaster', 'ProServeLogProcessor', 'get_log_broadcaster', 'setup_log_endpoints',
    'start_log_broadcasting', 'stop_log_broadcasting', 'is_websocket_available', 'get_broadcaster_stats',
    
    # Utility Functions
    'log_service_start', 'log_service_stop', 'log_script_execution', 'log_platform_info',
    'log_websocket_connection', 'log_endpoint_access', 'log_database_operation',
    'log_background_task', 'log_file_operation', 'log_network_request', 'log_security_event',
    'log_performance_metric', 'log_resource_usage', 'create_context_logger', 'create_request_logger',
    'create_task_logger', 'sanitize_log_data', 'format_duration', 'format_bytes', 'truncate_message',
    'extract_stack_info', 'log_with_context', 'log_exception', 'create_logger_with_context',
    
    # Main Setup Functions
    'setup_logging', 'initialize_async_logging', 'shutdown_logging', 'create_logger',
    'reconfigure_logging', 'get_logging_status', 'configure_logging_from_env',
    'setup_simple_logging', 'setup_production_logging', 'setup_development_logging'
]

# Backward compatibility exports
setup_logging = setup_logging
LoggingConfig = LoggingConfig
LogContext = LogContext
EnhancedFileHandler = EnhancedFileHandler
LogBroadcaster = LogBroadcaster

# Legacy compatibility functions (for EDPMT migration)
def create_context_from_manifest(service_name: str, **kwargs):
    """Create log context from manifest information (EDPMT compatibility)"""
    return LogContext(service_name=service_name, **kwargs)

def setup_enhanced_logging(**kwargs):
    """Enhanced logging setup (EDPMT compatibility)"""
    return setup_logging(**kwargs)
