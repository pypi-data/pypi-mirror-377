"""
ProServe Logging Builder - Logging Configuration Builder
Fluent API for building comprehensive logging configurations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class LoggingBuilder:
    """Builder for logging configuration with multiple handlers and formatters"""
    level: str = 'INFO'
    format: str = 'json'
    handlers: List[Dict[str, Any]] = field(default_factory=list)
    loggers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    filters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def with_level(self, level: str) -> 'LoggingBuilder':
        """Set global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"""
        self.level = level.upper()
        return self
        
    def with_format(self, format_type: str) -> 'LoggingBuilder':
        """Set log format (json, text, structured, custom)"""
        self.format = format_type
        return self
        
    def with_console_handler(self, level: str = 'INFO', 
                            format_str: str = None, 
                            colored: bool = True) -> 'LoggingBuilder':
        """Add console/stdout handler"""
        handler = {
            'type': 'console',
            'level': level.upper(),
            'colored': colored
        }
        if format_str:
            handler['format'] = format_str
        
        self.handlers.append(handler)
        return self
        
    def with_file_handler(self, filename: str, level: str = 'INFO', 
                         rotation: str = None, retention: str = None,
                         max_size: str = '10MB') -> 'LoggingBuilder':
        """Add file handler with optional rotation"""
        handler = {
            'type': 'file',
            'filename': filename,
            'level': level.upper(),
            'max_size': max_size
        }
        
        if rotation:
            handler['rotation'] = rotation  # e.g., 'daily', 'weekly', 'hourly'
        if retention:
            handler['retention'] = retention  # e.g., '30 days', '1 week'
            
        self.handlers.append(handler)
        return self
        
    def with_rotating_file_handler(self, filename: str, max_size: str = '10MB',
                                  backup_count: int = 5, level: str = 'INFO') -> 'LoggingBuilder':
        """Add rotating file handler"""
        handler = {
            'type': 'rotating_file',
            'filename': filename,
            'max_size': max_size,
            'backup_count': backup_count,
            'level': level.upper()
        }
        
        self.handlers.append(handler)
        return self
        
    def with_syslog_handler(self, address: str = 'localhost', 
                           facility: str = 'user', level: str = 'INFO',
                           port: int = 514) -> 'LoggingBuilder':
        """Add syslog handler"""
        handler = {
            'type': 'syslog',
            'address': address,
            'port': port,
            'facility': facility,
            'level': level.upper()
        }
        
        self.handlers.append(handler)
        return self
        
    def with_websocket_handler(self, url: str, level: str = 'DEBUG',
                              buffer_size: int = 100) -> 'LoggingBuilder':
        """Add WebSocket handler for live logging"""
        handler = {
            'type': 'websocket',
            'url': url,
            'level': level.upper(),
            'buffer_size': buffer_size
        }
        
        self.handlers.append(handler)
        return self
        
    def with_http_handler(self, url: str, method: str = 'POST',
                         level: str = 'ERROR', headers: Dict[str, str] = None) -> 'LoggingBuilder':
        """Add HTTP handler for remote logging"""
        handler = {
            'type': 'http',
            'url': url,
            'method': method.upper(),
            'level': level.upper(),
            'headers': headers or {}
        }
        
        self.handlers.append(handler)
        return self
        
    def with_elasticsearch_handler(self, hosts: List[str], index: str,
                                  level: str = 'INFO') -> 'LoggingBuilder':
        """Add Elasticsearch handler for centralized logging"""
        handler = {
            'type': 'elasticsearch',
            'hosts': hosts,
            'index': index,
            'level': level.upper()
        }
        
        self.handlers.append(handler)
        return self
        
    def with_slack_handler(self, webhook_url: str, channel: str = None,
                          level: str = 'ERROR', username: str = 'ProServe') -> 'LoggingBuilder':
        """Add Slack handler for notifications"""
        handler = {
            'type': 'slack',
            'webhook_url': webhook_url,
            'username': username,
            'level': level.upper()
        }
        if channel:
            handler['channel'] = channel
            
        self.handlers.append(handler)
        return self
        
    def with_email_handler(self, smtp_host: str, from_addr: str, to_addrs: List[str],
                          subject: str = 'ProServe Log Alert', level: str = 'ERROR',
                          smtp_port: int = 587, use_tls: bool = True) -> 'LoggingBuilder':
        """Add email handler for alerts"""
        handler = {
            'type': 'email',
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'from_addr': from_addr,
            'to_addrs': to_addrs,
            'subject': subject,
            'level': level.upper(),
            'use_tls': use_tls
        }
        
        self.handlers.append(handler)
        return self
        
    def with_custom_handler(self, handler_class: str, level: str = 'INFO',
                           **config) -> 'LoggingBuilder':
        """Add custom handler"""
        handler = {
            'type': 'custom',
            'class': handler_class,
            'level': level.upper(),
            **config
        }
        
        self.handlers.append(handler)
        return self
        
    def with_logger(self, name: str, level: str = 'INFO', 
                   handlers: List[str] = None, propagate: bool = True,
                   **options) -> 'LoggingBuilder':
        """Add custom logger configuration"""
        logger_config = {
            'level': level.upper(),
            'propagate': propagate,
            **options
        }
        
        if handlers:
            logger_config['handlers'] = handlers
            
        self.loggers[name] = logger_config
        return self
        
    def with_filter(self, name: str, filter_class: str = None,
                   filter_func: str = None, **config) -> 'LoggingBuilder':
        """Add log filter"""
        filter_config = config.copy()
        
        if filter_class:
            filter_config['class'] = filter_class
        elif filter_func:
            filter_config['function'] = filter_func
        else:
            raise ValueError("Either filter_class or filter_func must be provided")
            
        self.filters[name] = filter_config
        return self
        
    def with_structured_logging(self, service_name: str = None,
                               version: str = None, environment: str = None,
                               add_timestamp: bool = True,
                               add_correlation_id: bool = True) -> 'LoggingBuilder':
        """Configure structured logging with common fields"""
        structured_config = {
            'structured': True,
            'add_timestamp': add_timestamp,
            'add_correlation_id': add_correlation_id
        }
        
        if service_name:
            structured_config['service_name'] = service_name
        if version:
            structured_config['version'] = version
        if environment:
            structured_config['environment'] = environment
            
        # Store as special configuration
        if not hasattr(self, '_structured_config'):
            self._structured_config = structured_config
        else:
            self._structured_config.update(structured_config)
            
        return self
        
    def with_sampling(self, rate: float = 0.1, level: str = 'DEBUG') -> 'LoggingBuilder':
        """Add log sampling to reduce volume"""
        sampling_config = {
            'enabled': True,
            'rate': rate,
            'level': level.upper()
        }
        
        if not hasattr(self, '_sampling_config'):
            self._sampling_config = sampling_config
        else:
            self._sampling_config.update(sampling_config)
            
        return self
        
    def build(self) -> Dict[str, Any]:
        """Build logging configuration dictionary"""
        config = {
            'level': self.level,
            'format': self.format,
            'handlers': self.handlers
        }
        
        if self.loggers:
            config['loggers'] = self.loggers
        if self.filters:
            config['filters'] = self.filters
            
        # Add structured logging config if set
        if hasattr(self, '_structured_config'):
            config['structured'] = self._structured_config
            
        # Add sampling config if set
        if hasattr(self, '_sampling_config'):
            config['sampling'] = self._sampling_config
            
        return config


# Convenience functions for common logging patterns
def console_logging(level: str = 'INFO', colored: bool = True) -> LoggingBuilder:
    """Create simple console logging configuration"""
    return LoggingBuilder().with_level(level).with_console_handler(level, colored=colored)


def file_logging(filename: str, level: str = 'INFO', rotation: str = 'daily') -> LoggingBuilder:
    """Create file logging configuration with rotation"""
    return (LoggingBuilder()
            .with_level(level)
            .with_file_handler(filename, level, rotation=rotation))


def production_logging(service_name: str, log_dir: str = './logs') -> LoggingBuilder:
    """Create production-ready logging configuration"""
    return (LoggingBuilder()
            .with_level('INFO')
            .with_format('json')
            .with_structured_logging(service_name=service_name)
            .with_console_handler('ERROR', colored=False)
            .with_file_handler(f'{log_dir}/application.log', 'INFO', rotation='daily', retention='30 days')
            .with_file_handler(f'{log_dir}/errors.log', 'ERROR', rotation='daily', retention='90 days'))


def development_logging(level: str = 'DEBUG') -> LoggingBuilder:
    """Create development logging configuration"""
    return (LoggingBuilder()
            .with_level(level)
            .with_format('text')
            .with_console_handler(level, colored=True))


def centralized_logging(service_name: str, elasticsearch_hosts: List[str],
                       slack_webhook: str = None) -> LoggingBuilder:
    """Create centralized logging configuration"""
    builder = (LoggingBuilder()
               .with_level('INFO')
               .with_format('json')
               .with_structured_logging(service_name=service_name)
               .with_console_handler('ERROR')
               .with_elasticsearch_handler(elasticsearch_hosts, f'{service_name}-logs'))
    
    if slack_webhook:
        builder.with_slack_handler(slack_webhook, level='ERROR')
    
    return builder


def monitoring_logging(service_name: str, http_endpoint: str = None,
                      websocket_url: str = None) -> LoggingBuilder:
    """Create monitoring-focused logging configuration"""
    builder = (LoggingBuilder()
               .with_level('INFO')
               .with_structured_logging(service_name=service_name)
               .with_sampling(rate=0.1, level='DEBUG'))
    
    if http_endpoint:
        builder.with_http_handler(http_endpoint, level='WARNING')
    if websocket_url:
        builder.with_websocket_handler(websocket_url, level='DEBUG')
    
    return builder


# Validation
def validate_logging_config(config: Dict[str, Any]) -> List[str]:
    """Validate logging configuration and return list of errors"""
    errors = []
    
    # Check log level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config.get('level') not in valid_levels:
        errors.append(f"Invalid log level. Must be one of: {valid_levels}")
    
    # Check handlers
    handlers = config.get('handlers', [])
    if not handlers:
        errors.append("At least one handler is required")
    
    for i, handler in enumerate(handlers):
        if 'type' not in handler:
            errors.append(f"Handler {i}: type is required")
        
        handler_type = handler.get('type')
        if handler_type == 'file' and 'filename' not in handler:
            errors.append(f"Handler {i}: filename is required for file handler")
        elif handler_type == 'websocket' and 'url' not in handler:
            errors.append(f"Handler {i}: url is required for websocket handler")
        elif handler_type == 'http' and 'url' not in handler:
            errors.append(f"Handler {i}: url is required for http handler")
        elif handler_type == 'email':
            required_fields = ['smtp_host', 'from_addr', 'to_addrs']
            for field in required_fields:
                if field not in handler:
                    errors.append(f"Handler {i}: {field} is required for email handler")
    
    return errors
