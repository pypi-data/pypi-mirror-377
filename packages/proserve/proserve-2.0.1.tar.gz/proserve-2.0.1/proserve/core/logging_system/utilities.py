"""
ProServe Logging Utilities - Logging Helper Functions and Convenience Methods
Provides utility functions for common logging patterns and service-specific logging
"""

from typing import Optional, Dict, Any
import structlog

from .config import LogContext


logger = structlog.get_logger(__name__)


def log_service_start(logger: structlog.BoundLogger, service_name: str, 
                     version: str, host: str, port: int, **kwargs):
    """Log service startup information"""
    logger.info(
        "Service started",
        service_name=service_name,
        version=version,
        host=host,
        port=port,
        **kwargs
    )


def log_service_stop(logger: structlog.BoundLogger, service_name: str, **kwargs):
    """Log service shutdown information"""
    logger.info(
        "Service stopped",
        service_name=service_name,
        **kwargs
    )


def log_script_execution(logger: structlog.BoundLogger, script_path: str,
                        isolation_mode: str, execution_time: Optional[float] = None,
                        success: bool = True, error: Optional[str] = None, **kwargs):
    """Log script execution information"""
    log_data = {
        "script_path": script_path,
        "isolation_mode": isolation_mode,
        "success": success,
        **kwargs
    }
    
    if execution_time is not None:
        log_data["execution_time"] = f"{execution_time:.3f}s"
    
    if success:
        logger.info("Script executed successfully", **log_data)
    else:
        log_data["error"] = error or "Unknown error"
        logger.error("Script execution failed", **log_data)


def log_platform_info(logger: structlog.BoundLogger, platform: str,
                      board: Optional[str] = None, isolation_mode: str = "none", **kwargs):
    """Log platform and board information"""
    log_data = {
        "platform": platform,
        "isolation_mode": isolation_mode,
        **kwargs
    }
    
    if board:
        log_data["board"] = board
    
    logger.info("Platform information", **log_data)


def log_websocket_connection(logger: structlog.BoundLogger, action: str, 
                           connection_count: int, **kwargs):
    """Log WebSocket connection events"""
    logger.info(
        f"WebSocket {action}",
        action=action,
        active_connections=connection_count,
        **kwargs
    )


def log_endpoint_access(logger: structlog.BoundLogger, method: str, path: str,
                       status_code: int, response_time: Optional[float] = None,
                       user_agent: Optional[str] = None, **kwargs):
    """Log HTTP endpoint access"""
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        **kwargs
    }
    
    if response_time is not None:
        log_data["response_time"] = f"{response_time:.3f}s"
    
    if user_agent:
        log_data["user_agent"] = user_agent
    
    if 200 <= status_code < 400:
        logger.info("HTTP request", **log_data)
    elif 400 <= status_code < 500:
        logger.warning("HTTP client error", **log_data)
    else:
        logger.error("HTTP server error", **log_data)


def log_database_operation(logger: structlog.BoundLogger, operation: str,
                          table: Optional[str] = None, duration: Optional[float] = None,
                          affected_rows: Optional[int] = None, **kwargs):
    """Log database operation"""
    log_data = {
        "operation": operation,
        **kwargs
    }
    
    if table:
        log_data["table"] = table
    
    if duration is not None:
        log_data["duration"] = f"{duration:.3f}s"
    
    if affected_rows is not None:
        log_data["affected_rows"] = affected_rows
    
    logger.info("Database operation", **log_data)


def log_background_task(logger: structlog.BoundLogger, task_name: str,
                       status: str, duration: Optional[float] = None,
                       error: Optional[str] = None, **kwargs):
    """Log background task execution"""
    log_data = {
        "task_name": task_name,
        "status": status,
        **kwargs
    }
    
    if duration is not None:
        log_data["duration"] = f"{duration:.3f}s"
    
    if status == "started":
        logger.info("Background task started", **log_data)
    elif status == "completed":
        logger.info("Background task completed", **log_data)
    elif status == "failed":
        log_data["error"] = error or "Unknown error"
        logger.error("Background task failed", **log_data)
    else:
        logger.info("Background task status", **log_data)


def log_file_operation(logger: structlog.BoundLogger, operation: str, file_path: str,
                      success: bool = True, error: Optional[str] = None, **kwargs):
    """Log file system operation"""
    log_data = {
        "operation": operation,
        "file_path": file_path,
        "success": success,
        **kwargs
    }
    
    if success:
        logger.info("File operation completed", **log_data)
    else:
        log_data["error"] = error or "Unknown error"
        logger.error("File operation failed", **log_data)


def log_network_request(logger: structlog.BoundLogger, method: str, url: str,
                       status_code: Optional[int] = None, duration: Optional[float] = None,
                       error: Optional[str] = None, **kwargs):
    """Log outbound network request"""
    log_data = {
        "method": method,
        "url": url,
        **kwargs
    }
    
    if status_code is not None:
        log_data["status_code"] = status_code
    
    if duration is not None:
        log_data["duration"] = f"{duration:.3f}s"
    
    if error:
        log_data["error"] = error
        logger.error("Network request failed", **log_data)
    elif status_code and status_code >= 400:
        logger.warning("Network request error", **log_data)
    else:
        logger.info("Network request", **log_data)


def log_security_event(logger: structlog.BoundLogger, event_type: str,
                      severity: str = "info", user_id: Optional[str] = None,
                      ip_address: Optional[str] = None, **kwargs):
    """Log security-related events"""
    log_data = {
        "event_type": event_type,
        "severity": severity,
        **kwargs
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if ip_address:
        log_data["ip_address"] = ip_address
    
    if severity == "critical":
        logger.critical("Security event", **log_data)
    elif severity == "error":
        logger.error("Security event", **log_data)
    elif severity == "warning":
        logger.warning("Security event", **log_data)
    else:
        logger.info("Security event", **log_data)


def log_performance_metric(logger: structlog.BoundLogger, metric_name: str,
                          value: float, unit: str = "ms", **kwargs):
    """Log performance metric"""
    logger.info(
        "Performance metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )


def log_resource_usage(logger: structlog.BoundLogger, cpu_percent: Optional[float] = None,
                      memory_mb: Optional[float] = None, disk_usage_percent: Optional[float] = None,
                      **kwargs):
    """Log system resource usage"""
    log_data = {"resource_type": "system", **kwargs}
    
    if cpu_percent is not None:
        log_data["cpu_percent"] = cpu_percent
    
    if memory_mb is not None:
        log_data["memory_mb"] = memory_mb
    
    if disk_usage_percent is not None:
        log_data["disk_usage_percent"] = disk_usage_percent
    
    logger.info("Resource usage", **log_data)


def create_context_logger(service_name: str, **context_kwargs) -> structlog.BoundLogger:
    """Create a logger with bound context"""
    context = LogContext(service_name=service_name, **context_kwargs)
    base_logger = structlog.get_logger(service_name)
    return context.bind_to_logger(base_logger)


def create_request_logger(base_logger: structlog.BoundLogger, request_id: str,
                         method: str, path: str, **kwargs) -> structlog.BoundLogger:
    """Create a logger for a specific request"""
    return base_logger.bind(
        request_id=request_id,
        method=method,
        path=path,
        **kwargs
    )


def create_task_logger(base_logger: structlog.BoundLogger, task_name: str,
                      task_id: Optional[str] = None, **kwargs) -> structlog.BoundLogger:
    """Create a logger for a specific task"""
    log_context = {"task_name": task_name, **kwargs}
    
    if task_id:
        log_context["task_id"] = task_id
    
    return base_logger.bind(**log_context)


def sanitize_log_data(data: Dict[str, Any], sensitive_keys: Optional[list] = None) -> Dict[str, Any]:
    """Sanitize log data by removing or masking sensitive information"""
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api_key',
            'authorization', 'auth', 'credential', 'private_key', 'session_id'
        ]
    
    sanitized = {}
    
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if key contains sensitive information
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                # Mask all but last 4 characters
                sanitized[key] = "*" * (len(value) - 4) + value[-4:]
            else:
                sanitized[key] = "***MASKED***"
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_log_data(value, sensitive_keys)
        elif isinstance(value, list):
            # Sanitize lists
            sanitized[key] = [
                sanitize_log_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def format_bytes(bytes_value: int) -> str:
    """Format bytes in human-readable format"""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    for unit in units:
        if bytes_value < 1024:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024
    
    return f"{bytes_value:.1f}PB"


def truncate_message(message: str, max_length: int = 1000) -> str:
    """Truncate long messages for logging"""
    if len(message) <= max_length:
        return message
    
    truncated = message[:max_length - 3] + "..."
    return truncated


def extract_stack_info(exception: Exception, max_frames: int = 10) -> Dict[str, Any]:
    """Extract stack trace information from exception"""
    import traceback
    
    stack_info = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "stack_trace": []
    }
    
    # Get traceback frames
    tb = exception.__traceback__
    frames = traceback.extract_tb(tb, limit=max_frames)
    
    for frame in frames:
        stack_info["stack_trace"].append({
            "filename": frame.filename,
            "line_number": frame.lineno,
            "function_name": frame.name,
            "code": frame.line
        })
    
    return stack_info


# Legacy compatibility functions (for EDPMT migration)
def create_context_from_manifest(service_name: str, **kwargs) -> LogContext:
    """Create log context from manifest information (EDPMT compatibility)"""
    return LogContext(service_name=service_name, **kwargs)


def setup_enhanced_logging(**kwargs):
    """Enhanced logging setup (EDPMT compatibility)"""
    # Import here to avoid circular imports
    from .setup import setup_logging
    return setup_logging(**kwargs)


# Structured logging helpers
def log_with_context(logger: structlog.BoundLogger, level: str, message: str, **context):
    """Log message with additional context"""
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, **context)


def log_exception(logger: structlog.BoundLogger, exception: Exception, 
                 message: str = "Exception occurred", **context):
    """Log exception with stack trace information"""
    stack_info = extract_stack_info(exception)
    logger.error(
        message,
        exception_info=stack_info,
        **context
    )


def create_logger_with_context(name: str, **context) -> structlog.BoundLogger:
    """Create a logger with optional context (convenience function)"""
    base_logger = structlog.get_logger(name)
    return base_logger.bind(**context) if context else base_logger
