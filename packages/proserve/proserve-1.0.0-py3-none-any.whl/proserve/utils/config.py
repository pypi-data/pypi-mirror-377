"""
ProServe Configuration Management
Handles configuration loading, validation, and management for ProServe framework
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "sqlite:///proserve.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration"""
    backend: str = "memory"  # memory, redis, memcached
    url: Optional[str] = None
    ttl: int = 3600
    max_size: int = 1000
    compression: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "structured"  # structured, json, console
    output: str = "console"  # console, file, syslog, websocket
    file_path: Optional[str] = None
    max_file_size: str = "100MB"
    backup_count: int = 5
    broadcast_logs: bool = True
    websocket_port: Optional[int] = None


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_authentication: bool = False
    auth_backend: str = "jwt"  # jwt, oauth2, apikey
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    rate_limiting: bool = False
    rate_limit: str = "100/minute"


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    enable_metrics: bool = True
    metrics_port: Optional[int] = None
    metrics_path: str = "/metrics"
    enable_health_checks: bool = True
    health_check_path: str = "/health"
    enable_prometheus: bool = False
    prometheus_registry: Optional[str] = None
    enable_tracing: bool = False
    tracing_backend: str = "jaeger"
    tracing_endpoint: Optional[str] = None


@dataclass
class IsolationConfig:
    """Default isolation configuration"""
    default_mode: str = "none"  # none, process, docker, container, micropython, arduino
    default_timeout: int = 30
    docker_image: str = "python:3.11-slim"
    docker_network: Optional[str] = None
    docker_volumes: List[str] = field(default_factory=list)
    micropython_board: str = "rp2040"
    arduino_board: str = "uno"
    sandbox_enabled: bool = False
    resource_limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    supported_platforms: List[str] = field(default_factory=lambda: [
        "linux", "darwin", "windows", "rp2040", "esp32", "esp8266", "arduino-uno", "arduino-nano"
    ])
    embedded_platforms: List[str] = field(default_factory=lambda: [
        "rp2040", "esp32", "esp8266", "arduino-uno", "arduino-nano"
    ])
    device_detection: bool = True
    auto_flash: bool = False
    firmware_path: Optional[str] = None


@dataclass
class DiscoveryConfig:
    """Service discovery configuration"""
    enabled: bool = True
    discovery_paths: List[str] = field(default_factory=lambda: ["."])
    supported_frameworks: List[str] = field(default_factory=lambda: [
        "flask", "fastapi", "django", "aiohttp", "tornado", "bottle"
    ])
    auto_generate_manifests: bool = True
    manifest_template: Optional[str] = None
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*/node_modules/*", "*/__pycache__/*", "*/venv/*", "*/.git/*"
    ])


@dataclass
class MigrationConfig:
    """Migration configuration"""
    backup_enabled: bool = True
    backup_path: str = "./backups"
    default_strategy: str = "blue-green"  # blue-green, rolling, immediate
    rollback_enabled: bool = True
    health_check_timeout: int = 60
    traffic_shift_interval: int = 30
    max_rollback_versions: int = 5


@dataclass
class ProServeConfig:
    """Main ProServe configuration"""
    
    # Basic settings
    debug: bool = False
    environment: str = "development"  # development, staging, production
    project_name: str = "proserve-project"
    version: str = "1.0.0"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    isolation: IsolationConfig = field(default_factory=IsolationConfig)
    platform: PlatformConfig = field(default_factory=PlatformConfig)
    discovery: DiscoveryConfig = field(default_factory=DiscoveryConfig)
    migration: MigrationConfig = field(default_factory=MigrationConfig)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup"""
        self._load_environment_variables()
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        
        # Basic settings
        self.debug = os.getenv("PROSERVE_DEBUG", str(self.debug)).lower() == "true"
        self.environment = os.getenv("PROSERVE_ENV", self.environment)
        self.project_name = os.getenv("PROSERVE_PROJECT_NAME", self.project_name)
        self.version = os.getenv("PROSERVE_VERSION", self.version)
        
        # Database
        if db_url := os.getenv("DATABASE_URL"):
            self.database.url = db_url
        
        # Cache
        if cache_url := os.getenv("CACHE_URL"):
            self.cache.url = cache_url
        if cache_backend := os.getenv("CACHE_BACKEND"):
            self.cache.backend = cache_backend
        
        # Logging
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        if log_file := os.getenv("LOG_FILE"):
            self.logging.file_path = log_file
        
        # Security
        if jwt_secret := os.getenv("JWT_SECRET"):
            self.security.jwt_secret = jwt_secret
        
        # Monitoring
        if metrics_port := os.getenv("METRICS_PORT"):
            self.monitoring.metrics_port = int(metrics_port)
    
    @classmethod
    def load_from_file(cls, config_path: Union[str, Path]) -> 'ProServeConfig':
        """Load configuration from file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Load environment file if exists
        env_file = config_path.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # Load configuration based on file extension
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProServeConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update basic settings
        for key in ['debug', 'environment', 'project_name', 'version']:
            if key in data:
                setattr(config, key, data[key])
        
        # Update component configurations
        component_mapping = {
            'database': DatabaseConfig,
            'cache': CacheConfig,
            'logging': LoggingConfig,
            'security': SecurityConfig,
            'monitoring': MonitoringConfig,
            'isolation': IsolationConfig,
            'platform': PlatformConfig,
            'discovery': DiscoveryConfig,
            'migration': MigrationConfig
        }
        
        for component_name, component_class in component_mapping.items():
            if component_name in data:
                component_data = data[component_name]
                current_component = getattr(config, component_name)
                
                # Update component fields
                for field_name, field_value in component_data.items():
                    if hasattr(current_component, field_name):
                        setattr(current_component, field_name, field_value)
        
        # Update custom settings
        if 'custom' in data:
            config.custom.update(data['custom'])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def save_to_file(self, config_path: Union[str, Path], format: str = "yaml"):
        """Save configuration to file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        if format.lower() in ['yml', 'yaml']:
            with open(config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_env_specific_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration overrides"""
        env_configs = {
            'development': {
                'debug': True,
                'logging': {'level': 'DEBUG', 'output': 'console'},
                'security': {'enable_authentication': False},
                'monitoring': {'enable_metrics': True}
            },
            'staging': {
                'debug': False,
                'logging': {'level': 'INFO', 'output': 'file'},
                'security': {'enable_authentication': True},
                'monitoring': {'enable_metrics': True, 'enable_prometheus': True}
            },
            'production': {
                'debug': False,
                'logging': {'level': 'WARNING', 'output': 'syslog'},
                'security': {'enable_authentication': True, 'rate_limiting': True},
                'monitoring': {'enable_metrics': True, 'enable_prometheus': True, 'enable_tracing': True}
            }
        }
        
        return env_configs.get(self.environment, {})
    
    def apply_env_config(self):
        """Apply environment-specific configuration"""
        env_config = self.get_env_specific_config()
        
        for section, settings in env_config.items():
            if hasattr(self, section):
                component = getattr(self, section)
                for key, value in settings.items():
                    if hasattr(component, key):
                        setattr(component, key, value)
            else:
                # Apply to root level
                if hasattr(self, section):
                    setattr(self, section, settings)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate basic settings
        if not self.project_name:
            errors.append("project_name cannot be empty")
        
        if not self.version:
            errors.append("version cannot be empty")
        
        # Validate database configuration
        if not self.database.url:
            errors.append("database.url cannot be empty")
        
        # Validate security configuration
        if self.security.enable_authentication and not self.security.jwt_secret:
            errors.append("jwt_secret is required when authentication is enabled")
        
        # Validate isolation configuration
        valid_modes = ['none', 'process', 'docker', 'container', 'micropython', 'arduino', 'sandbox']
        if self.isolation.default_mode not in valid_modes:
            errors.append(f"isolation.default_mode must be one of: {', '.join(valid_modes)}")
        
        # Validate platform configuration
        if not self.platform.supported_platforms:
            errors.append("platform.supported_platforms cannot be empty")
        
        # Validate monitoring ports
        if self.monitoring.metrics_port and (self.monitoring.metrics_port < 1 or self.monitoring.metrics_port > 65535):
            errors.append("monitoring.metrics_port must be between 1 and 65535")
        
        return errors
    
    def get_default_config_path(self) -> Path:
        """Get default configuration file path"""
        return Path.cwd() / "proserve.yml"
    
    def create_default_config(self, config_path: Optional[Path] = None) -> Path:
        """Create default configuration file"""
        if config_path is None:
            config_path = self.get_default_config_path()
        
        # Apply environment-specific defaults
        self.apply_env_config()
        
        # Save configuration
        self.save_to_file(config_path)
        
        return config_path
    
    def merge_with(self, other: 'ProServeConfig') -> 'ProServeConfig':
        """Merge with another configuration (other takes precedence)"""
        merged_dict = self.to_dict()
        other_dict = other.to_dict()
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Deep merge dictionaries"""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_dict = deep_merge(merged_dict, other_dict)
        return ProServeConfig.from_dict(merged_dict)
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ProServeConfig(project={self.project_name}, env={self.environment}, debug={self.debug})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"ProServeConfig({self.to_dict()})"


# Global configuration instance
_config: Optional[ProServeConfig] = None


def get_config() -> ProServeConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = ProServeConfig()
    return _config


def set_config(config: ProServeConfig):
    """Set global configuration instance"""
    global _config
    _config = config


def load_config(config_path: Union[str, Path]) -> ProServeConfig:
    """Load and set global configuration from file"""
    config = ProServeConfig.load_from_file(config_path)
    set_config(config)
    return config


def create_default_config(config_path: Optional[Union[str, Path]] = None) -> Path:
    """Create default configuration file"""
    config = ProServeConfig()
    if config_path:
        config_path = Path(config_path)
    return config.create_default_config(config_path)
