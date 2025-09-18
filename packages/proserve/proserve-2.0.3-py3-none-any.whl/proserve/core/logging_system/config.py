"""
ProServe Logging Configuration - Logging System Configuration Management
Handles logging configuration from manifests and provides configuration validation
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LoggingConfig:
    """Enhanced logging configuration from manifest"""
    
    # Basic settings
    enabled: bool = True
    level: str = "INFO"
    format: str = "text"  # text, json, structured
    
    # Console settings
    console_enabled: bool = True
    console_level: str = "INFO"
    console_format: str = "text"
    rich_console: bool = True
    
    # File settings
    file_enabled: bool = False
    file_path: Optional[str] = None
    file_level: str = "INFO"
    file_format: str = "structured"
    
    # File rotation settings
    rotation_enabled: bool = True
    rotation_type: str = "size"  # size, time
    max_file_size: str = "10MB"
    backup_count: int = 5
    rotation_interval: str = "midnight"  # for time-based rotation
    
    # Buffering settings
    buffer_enabled: bool = True
    buffer_size: int = 1000
    flush_interval: float = 5.0  # seconds
    
    # WebSocket broadcasting
    websocket_enabled: bool = True
    websocket_path: str = "/logs"
    websocket_buffer_size: int = 100
    
    # Structured logging settings
    include_caller: bool = False
    include_timestamp: bool = True
    include_level: bool = True
    include_logger_name: bool = True
    
    # Context fields to include
    context_fields: List[str] = field(default_factory=lambda: [
        'service_name', 'platform', 'isolation_mode', 'task_name'
    ])
    
    # Log filtering
    exclude_loggers: List[str] = field(default_factory=lambda: [
        'asyncio', 'aiohttp.access'
    ])
    min_log_interval: float = 0.1  # Minimum interval between similar logs
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Normalize log levels
        self.level = self.level.upper()
        self.console_level = self.console_level.upper()
        self.file_level = self.file_level.upper()
        
        # Validate log levels
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}")
        if self.console_level not in valid_levels:
            raise ValueError(f"Invalid console log level: {self.console_level}")
        if self.file_level not in valid_levels:
            raise ValueError(f"Invalid file log level: {self.file_level}")
        
        # Validate formats
        valid_formats = ['text', 'json', 'structured']
        if self.format not in valid_formats:
            raise ValueError(f"Invalid log format: {self.format}")
        if self.console_format not in valid_formats:
            raise ValueError(f"Invalid console format: {self.console_format}")
        if self.file_format not in valid_formats:
            raise ValueError(f"Invalid file format: {self.file_format}")
        
        # Validate rotation settings
        if self.rotation_type not in ['size', 'time']:
            raise ValueError(f"Invalid rotation type: {self.rotation_type}")
        
        # Create file path if file logging is enabled but no path specified
        if self.file_enabled and not self.file_path:
            self.file_path = "proserve.log"
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LoggingConfig':
        """Create configuration from dictionary (manifest)"""
        return cls(**config_dict)
    
    @classmethod
    def from_manifest(cls, manifest_config: Optional[Dict[str, Any]] = None) -> 'LoggingConfig':
        """Create configuration from manifest logging section"""
        if not manifest_config:
            return cls()
        
        # Extract logging configuration from manifest
        logging_config = manifest_config.get('logging', {})
        
        # Map manifest keys to config attributes
        config_data = {}
        
        # Basic settings
        config_data['enabled'] = logging_config.get('enabled', True)
        config_data['level'] = logging_config.get('level', 'INFO')
        config_data['format'] = logging_config.get('format', 'text')
        
        # Console settings
        console_config = logging_config.get('console', {})
        config_data['console_enabled'] = console_config.get('enabled', True)
        config_data['console_level'] = console_config.get('level', 'INFO')
        config_data['console_format'] = console_config.get('format', 'text')
        config_data['rich_console'] = console_config.get('rich', True)
        
        # File settings
        file_config = logging_config.get('file', {})
        config_data['file_enabled'] = file_config.get('enabled', False)
        config_data['file_path'] = file_config.get('path')
        config_data['file_level'] = file_config.get('level', 'INFO')
        config_data['file_format'] = file_config.get('format', 'structured')
        
        # File rotation
        rotation_config = file_config.get('rotation', {})
        config_data['rotation_enabled'] = rotation_config.get('enabled', True)
        config_data['rotation_type'] = rotation_config.get('type', 'size')
        config_data['max_file_size'] = rotation_config.get('max_size', '10MB')
        config_data['backup_count'] = rotation_config.get('backup_count', 5)
        config_data['rotation_interval'] = rotation_config.get('interval', 'midnight')
        
        # Buffering
        buffer_config = logging_config.get('buffering', {})
        config_data['buffer_enabled'] = buffer_config.get('enabled', True)
        config_data['buffer_size'] = buffer_config.get('size', 1000)
        config_data['flush_interval'] = buffer_config.get('flush_interval', 5.0)
        
        # WebSocket broadcasting
        websocket_config = logging_config.get('websocket', {})
        config_data['websocket_enabled'] = websocket_config.get('enabled', True)
        config_data['websocket_path'] = websocket_config.get('path', '/logs')
        config_data['websocket_buffer_size'] = websocket_config.get('buffer_size', 100)
        
        # Structured logging
        structured_config = logging_config.get('structured', {})
        config_data['include_caller'] = structured_config.get('include_caller', False)
        config_data['include_timestamp'] = structured_config.get('include_timestamp', True)
        config_data['include_level'] = structured_config.get('include_level', True)
        config_data['include_logger_name'] = structured_config.get('include_logger_name', True)
        config_data['context_fields'] = structured_config.get('context_fields', [
            'service_name', 'platform', 'isolation_mode', 'task_name'
        ])
        
        # Filtering
        filter_config = logging_config.get('filtering', {})
        config_data['exclude_loggers'] = filter_config.get('exclude_loggers', [
            'asyncio', 'aiohttp.access'
        ])
        config_data['min_log_interval'] = filter_config.get('min_log_interval', 0.1)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'enabled': self.enabled,
            'level': self.level,
            'format': self.format,
            'console': {
                'enabled': self.console_enabled,
                'level': self.console_level,
                'format': self.console_format,
                'rich': self.rich_console
            },
            'file': {
                'enabled': self.file_enabled,
                'path': self.file_path,
                'level': self.file_level,
                'format': self.file_format,
                'rotation': {
                    'enabled': self.rotation_enabled,
                    'type': self.rotation_type,
                    'max_size': self.max_file_size,
                    'backup_count': self.backup_count,
                    'interval': self.rotation_interval
                }
            },
            'buffering': {
                'enabled': self.buffer_enabled,
                'size': self.buffer_size,
                'flush_interval': self.flush_interval
            },
            'websocket': {
                'enabled': self.websocket_enabled,
                'path': self.websocket_path,
                'buffer_size': self.websocket_buffer_size
            },
            'structured': {
                'include_caller': self.include_caller,
                'include_timestamp': self.include_timestamp,
                'include_level': self.include_level,
                'include_logger_name': self.include_logger_name,
                'context_fields': self.context_fields
            },
            'filtering': {
                'exclude_loggers': self.exclude_loggers,
                'min_log_interval': self.min_log_interval
            }
        }
    
    def get_log_level_numeric(self, level_name: str = None) -> int:
        """Get numeric log level"""
        import logging
        level_name = level_name or self.level
        return getattr(logging, level_name.upper())
    
    def should_log_to_console(self, level: str) -> bool:
        """Check if message should be logged to console"""
        if not self.console_enabled:
            return False
        
        import logging
        message_level = getattr(logging, level.upper())
        console_level = getattr(logging, self.console_level.upper())
        
        return message_level >= console_level
    
    def should_log_to_file(self, level: str) -> bool:
        """Check if message should be logged to file"""
        if not self.file_enabled:
            return False
        
        import logging
        message_level = getattr(logging, level.upper())
        file_level = getattr(logging, self.file_level.upper())
        
        return message_level >= file_level
    
    def is_logger_excluded(self, logger_name: str) -> bool:
        """Check if logger is excluded from logging"""
        for excluded in self.exclude_loggers:
            if logger_name.startswith(excluded):
                return True
        return False
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of validation errors"""
        errors = []
        
        # Check file path validity if file logging is enabled
        if self.file_enabled and self.file_path:
            try:
                file_path = Path(self.file_path)
                # Check if parent directory exists or can be created
                if not file_path.parent.exists():
                    try:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        errors.append(f"Cannot create log directory: {e}")
            except Exception as e:
                errors.append(f"Invalid file path: {e}")
        
        # Validate buffer settings
        if self.buffer_size <= 0:
            errors.append("Buffer size must be positive")
        
        if self.flush_interval <= 0:
            errors.append("Flush interval must be positive")
        
        # Validate rotation settings
        if self.rotation_enabled:
            if self.backup_count < 0:
                errors.append("Backup count must be non-negative")
            
            if self.rotation_type == 'size':
                try:
                    self._parse_size(self.max_file_size)
                except ValueError as e:
                    errors.append(f"Invalid max file size: {e}")
        
        return errors
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper().strip()
        
        # Extract number and unit
        import re
        match = re.match(r'(\d+(?:\.\d+)?)\s*([KMGT]?B?)', size_str)
        if not match:
            raise ValueError(f"Invalid size format: {size_str}")
        
        number = float(match.group(1))
        unit = match.group(2) or 'B'
        
        # Convert to bytes
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3,
            'TB': 1024 ** 4
        }
        
        if unit not in multipliers:
            raise ValueError(f"Unknown size unit: {unit}")
        
        return int(number * multipliers[unit])


@dataclass
class LogContext:
    """Enhanced logging context with service and platform information"""
    
    service_name: str
    manifest_path: Optional[str] = None
    handler_script: Optional[str] = None
    isolation_mode: str = "none"
    platform: Optional[str] = None
    board: Optional[str] = None
    task_name: Optional[str] = None
    extra_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging"""
        context = {
            'service_name': self.service_name,
            'timestamp': self.timestamp,
            'isolation_mode': self.isolation_mode
        }
        
        # Add optional fields if present
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
        
        # Add extra context
        context.update(self.extra_context)
        
        return context
    
    def bind_to_logger(self, logger):
        """Bind context to a structlog logger"""
        return logger.bind(**self.to_dict())
    
    def update_context(self, **kwargs):
        """Update extra context with new values"""
        self.extra_context.update(kwargs)
        # Update timestamp when context changes
        self.timestamp = datetime.utcnow().isoformat()
    
    def copy_with_updates(self, **kwargs) -> 'LogContext':
        """Create a copy of the context with updates"""
        new_context = LogContext(
            service_name=kwargs.get('service_name', self.service_name),
            manifest_path=kwargs.get('manifest_path', self.manifest_path),
            handler_script=kwargs.get('handler_script', self.handler_script),
            isolation_mode=kwargs.get('isolation_mode', self.isolation_mode),
            platform=kwargs.get('platform', self.platform),
            board=kwargs.get('board', self.board),
            task_name=kwargs.get('task_name', self.task_name),
            extra_context=self.extra_context.copy(),
        )
        
        # Update with any additional context
        extra_updates = {k: v for k, v in kwargs.items() 
                        if k not in ['service_name', 'manifest_path', 'handler_script', 
                                   'isolation_mode', 'platform', 'board', 'task_name']}
        new_context.update_context(**extra_updates)
        
        return new_context


# Utility functions for configuration
def create_default_config() -> LoggingConfig:
    """Create default logging configuration"""
    return LoggingConfig()


def create_config_from_env() -> LoggingConfig:
    """Create logging configuration from environment variables"""
    config = LoggingConfig()
    
    # Override with environment variables
    if 'PROSERVE_LOG_LEVEL' in os.environ:
        config.level = os.environ['PROSERVE_LOG_LEVEL'].upper()
    
    if 'PROSERVE_LOG_FILE' in os.environ:
        config.file_enabled = True
        config.file_path = os.environ['PROSERVE_LOG_FILE']
    
    if 'PROSERVE_LOG_FORMAT' in os.environ:
        config.format = os.environ['PROSERVE_LOG_FORMAT']
    
    if 'PROSERVE_LOG_CONSOLE' in os.environ:
        config.console_enabled = os.environ['PROSERVE_LOG_CONSOLE'].lower() in ['true', '1', 'yes']
    
    return config


def merge_configs(base_config: LoggingConfig, override_config: Dict[str, Any]) -> LoggingConfig:
    """Merge base configuration with overrides"""
    base_dict = base_config.to_dict()
    
    # Deep merge the configurations
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    merged_dict = deep_merge(base_dict, override_config)
    return LoggingConfig.from_dict(merged_dict)
