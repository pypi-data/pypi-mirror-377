"""
ProServe Service Manifest Framework
Handles service configuration and YAML manifest processing
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from dotenv import load_dotenv


def expand_env_vars(content: str) -> str:
    """
    Expand environment variables in content with support for bash-style default values.
    Supports both ${VAR} and ${VAR:-default} syntax.
    """
    def replace_var(match):
        var_expr = match.group(1)
        if ':-' in var_expr:
            var_name, default_value = var_expr.split(':-', 1)
            return os.environ.get(var_name, default_value)
        else:
            return os.environ.get(var_expr, '')
    
    # Pattern to match ${VAR} or ${VAR:-default}
    pattern = r'\$\{([^}]+)\}'
    expanded = re.sub(pattern, replace_var, content)
    
    # Also handle simple $VAR format for backward compatibility
    expanded = os.path.expandvars(expanded)
    
    return expanded


@dataclass
class ServiceManifest:
    """Service configuration from YAML manifest"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    type: str = "http"  # http, websocket, grpc, hybrid, mqtt, micropython, arduino
    port: int = 8080
    host: str = "0.0.0.0"
    
    # gRPC specific configuration
    grpc_port: Optional[int] = None  # Optional separate gRPC port (for hybrid services)
    grpc_reflection: bool = True  # Enable gRPC reflection
    grpc_health_check: bool = True  # Enable gRPC health checking
    grpc_max_workers: int = 10  # Max concurrent gRPC workers
    
    # Framework selection
    framework: str = "python"  # python, fastapi, django, flask, express, nestjs, spring, aspnet, rails, go, phoenix
    framework_config: Dict[str, Any] = field(default_factory=dict)
    
    # Proxy server selection
    proxy_server: str = "none"  # none, nginx, caddy, apache, haproxy, traefik, envoy
    proxy_config: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    requires_proserve: bool = True  # Changed from requires_edpmt
    proserve_url: Optional[str] = None  # Changed from edpmt_url
    
    # Legacy EDPMT compatibility
    requires_edpmt: bool = False
    edpmt_url: Optional[str] = None
    
    # Features
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_health: bool = True
    enable_metrics: bool = False
    enable_tracing: bool = False
    
    # TLS/SSL Configuration
    enable_tls: bool = False
    tls_cert: Optional[str] = None
    tls_key: Optional[str] = None
    tls_ca_cert: Optional[str] = None
    ssl_context: Optional[str] = None
    tls_provider: Optional[str] = "selfsigned"  # selfsigned, letsencrypt, cloudflare
    domain: Optional[str] = "localhost"
    
    # MicroPython/IoT Configuration
    platform: Optional[str] = None  # rp2040, raspberry_pi, arduino
    board: Optional[str] = None  # raspberry_pi_pico, raspberry_pi_4, etc
    device_config: Optional[Dict[str, Any]] = None  # GPIO pins, I2C devices, etc
    micropython_scripts: Optional[List[Dict[str, Any]]] = None  # MicroPython scripts
    wifi_config: Optional[Dict[str, Any]] = None  # WiFi configuration
    background_tasks: Optional[List[Dict[str, Any]]] = None  # Background tasks
    automation_rules: Optional[List[Dict[str, Any]]] = None  # Home automation rules
    monitoring: Optional[Dict[str, Any]] = None  # Monitoring configuration
    
    # Endpoints (for HTTP services)
    # Endpoints can use either:
    # - script: path to handler script file
    # - shell_command: shell command to execute
    # - converter: function to convert shell output to desired format
    endpoints: List[Dict] = field(default_factory=list)
    
    # gRPC services configuration
    grpc_services: List[Dict] = field(default_factory=list)  # gRPC service definitions
    proto_files: List[str] = field(default_factory=list)  # Proto file paths
    proto_generate: bool = True  # Auto-generate proto files from services
    grpc_interceptors: List[str] = field(default_factory=list)  # Custom interceptors
    
    # WebSocket handlers
    websocket_handlers: List[Dict] = field(default_factory=list)
    
    # Background tasks
    background_tasks: List[Dict] = field(default_factory=list)
    
    # Shell command configuration
    shell_config: Dict[str, Any] = field(default_factory=dict)
    
    # Output format converters
    converters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Environment variables to load
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Logging configuration
    logging: Dict[str, Any] = field(default_factory=dict)
    
    # Database configuration
    database: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics configuration
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Health check configuration
    health: Dict[str, Any] = field(default_factory=dict)
    
    # Deployment configuration
    deployment: Dict[str, Any] = field(default_factory=dict)
    
    # Shell commands configuration
    shell_commands: List[Dict[str, Any]] = field(default_factory=list)
    
    # Static file serving (legacy)
    static_dirs: Dict[str, str] = field(default_factory=dict)
    static_files: Dict[str, str] = field(default_factory=dict)
    
    # Static website hosting configuration
    static_hosting: Dict[str, Any] = field(default_factory=dict)
    
    # CDN resource management
    cdn_resources: List[Dict[str, Any]] = field(default_factory=list)
    
    # API proxy rules
    api_proxy_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Middleware configuration
    middleware: Dict[str, Any] = field(default_factory=dict)
    
    # Security configuration
    security: Dict[str, Any] = field(default_factory=dict)
    
    # Monitoring and metrics
    monitoring: Dict[str, Any] = field(default_factory=dict)
    
    # Service dependencies
    dependencies: Dict[str, Any] = field(default_factory=dict)
    
    # Environment-specific configuration
    development: Dict[str, Any] = field(default_factory=dict)
    production: Dict[str, Any] = field(default_factory=dict)
    
    # Additional configuration sections
    environment: Dict[str, str] = field(default_factory=dict)
    
    # Custom initialization
    init_module: Optional[str] = None
    handler_module: Optional[str] = None
    
    # Process isolation and virtualization
    isolation: Dict[str, Any] = field(default_factory=dict)
    env_files: List[str] = field(default_factory=list)  # Additional .env files to load
    
    # Extended platform support
    platform: Optional[str] = None  # rp2040, esp32, esp8266, arduino_uno, etc.
    board: Optional[str] = None     # Specific board configuration
    
    # Default isolation settings
    _default_isolation: Dict[str, Any] = field(default_factory=lambda: {
        'mode': 'none',  # none, process, container, sandbox, micropython, arduino
        'timeout': 30,
        'memory_limit': None,
        'cpu_limit': None,
        'network_isolation': False,
        'filesystem_isolation': False,
        'environment_isolation': True,
        'auto_environment': False,  # Auto-detect and setup environment
        'platform': None,
        'board': None
    })
    
    @classmethod
    def from_yaml(cls, path: str) -> 'ServiceManifest':
        """Load manifest from YAML file with enhanced .env loading support"""
        with open(path, 'r') as f:
            content = f.read()
        
        # Load .env files before expanding variables
        manifest_dir = Path(path).parent
        project_root = manifest_dir.parent if manifest_dir.name == 'manifests' else manifest_dir
        
        # Load default .env from project root
        default_env_path = project_root / '.env'
        if default_env_path.exists():
            load_dotenv(default_env_path)
        
        # Parse manifest to get additional env_files
        temp_data = yaml.safe_load(content)
        if 'env_files' in temp_data:
            for env_file in temp_data['env_files']:
                env_path = project_root / env_file if not os.path.isabs(env_file) else Path(env_file)
                if env_path.exists():
                    load_dotenv(env_path, override=True)
        
        # Expand environment variables in the content with bash-style default support
        expanded_content = expand_env_vars(content)
        data = yaml.safe_load(expanded_content)
        
        # Handle legacy server format compatibility
        if 'server' in data and isinstance(data['server'], dict):
            server_config = data.pop('server')
            if 'host' in server_config:
                data['host'] = server_config['host']
            if 'port' in server_config:
                data['port'] = server_config['port']
        
        # Convert port to int if it's a string (after env var expansion)
        if 'port' in data and isinstance(data['port'], str):
            try:
                data['port'] = int(data['port'])
            except ValueError:
                pass  # Keep as string if not a valid integer
        
        # Store the manifest path for relative script loading
        manifest = cls(**data)
        manifest._manifest_path = path
        
        # Merge default isolation settings with manifest settings
        if manifest.isolation:
            merged_isolation = manifest._default_isolation.copy()
            merged_isolation.update(manifest.isolation)
            manifest.isolation = merged_isolation
        else:
            manifest.isolation = manifest._default_isolation.copy()
        
        # Handle legacy EDPMT compatibility
        if manifest.requires_edpmt and not manifest.requires_proserve:
            manifest.requires_proserve = True
        
        if manifest.edpmt_url and not manifest.proserve_url:
            manifest.proserve_url = manifest.edpmt_url
        
        return manifest
    
    @staticmethod
    def _has_callable(obj) -> bool:
        """Recursively check if an object contains any callable objects"""
        if callable(obj):
            return True
        if isinstance(obj, dict):
            return any(ServiceManifest._has_callable(v) for v in obj.values())
        if isinstance(obj, (list, tuple)):
            return any(ServiceManifest._has_callable(item) for item in obj)
        return False
    
    @staticmethod 
    def _filter_callables(obj):
        """Recursively remove callable objects from a data structure"""
        if callable(obj):
            return None  # Skip callables
        if isinstance(obj, dict):
            filtered = {}
            for k, v in obj.items():
                if not ServiceManifest._has_callable(v):
                    filtered[k] = ServiceManifest._filter_callables(v)
            return filtered
        if isinstance(obj, list):
            return [ServiceManifest._filter_callables(item) for item in obj if not ServiceManifest._has_callable(item)]
        if isinstance(obj, tuple):
            return tuple(ServiceManifest._filter_callables(item) for item in obj if not ServiceManifest._has_callable(item))
        return obj
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], load_env_files: bool = True) -> 'ServiceManifest':
        """Load manifest from dictionary with environment variable expansion"""
        # Separate function objects from serializable data using robust filtering
        serializable_data = cls._filter_callables(data)
        
        # Only serialize the serializable parts for environment expansion
        if serializable_data:
            try:
                json_content = json.dumps(serializable_data)
                
                # Load .env files if specified and they exist
                if load_env_files and 'env_files' in serializable_data:
                    for env_file in serializable_data['env_files']:
                        env_path = Path(env_file)
                        if env_path.exists():
                            load_dotenv(env_path, override=True)
                
                # Expand environment variables
                expanded_content = expand_env_vars(json_content)
                expanded_data = json.loads(expanded_content)
            except (TypeError, ValueError) as e:
                # Fallback: if serialization still fails, use original data without expansion
                print(f"Warning: Could not serialize manifest for env expansion: {e}")
                expanded_data = {}
        else:
            expanded_data = {}
        
        # Merge back original data (including functions) with expanded data
        # Original data takes precedence to preserve functions
        final_data = dict(expanded_data)
        final_data.update(data)
        
        # Convert port to int if it's a string (after env var expansion)
        if 'port' in expanded_data and isinstance(expanded_data['port'], str):
            try:
                expanded_data['port'] = int(expanded_data['port'])
            except ValueError:
                pass  # Keep as string if not a valid integer
        
        # Create manifest
        manifest = cls(**expanded_data)
        
        # Merge default isolation settings with manifest settings
        if manifest.isolation:
            merged_isolation = manifest._default_isolation.copy()
            merged_isolation.update(manifest.isolation)
            manifest.isolation = merged_isolation
        else:
            manifest.isolation = manifest._default_isolation.copy()
        
        # Handle legacy EDPMT compatibility
        if manifest.requires_edpmt and not manifest.requires_proserve:
            manifest.requires_proserve = True
        
        if manifest.edpmt_url and not manifest.proserve_url:
            manifest.proserve_url = manifest.edpmt_url
        
        return manifest
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'type': self.type,
            'port': self.port,
            'host': self.host,
            'requires_proserve': self.requires_proserve,
            'proserve_url': self.proserve_url,
            'requires_edpmt': self.requires_edpmt,  # Legacy compatibility
            'edpmt_url': self.edpmt_url,
            'enable_cors': self.enable_cors,
            'cors_origins': self.cors_origins,
            'enable_health': self.enable_health,
            'enable_metrics': self.enable_metrics,
            'enable_tracing': self.enable_tracing,
            'endpoints': self.endpoints,
            'grpc_services': self.grpc_services,
            'proto_files': self.proto_files,
            'websocket_handlers': self.websocket_handlers,
            'background_tasks': self.background_tasks,
            'converters': self.converters,
            'env_vars': self.env_vars,
            'environment': self.environment,
            'logging': self.logging,
            'static_dirs': self.static_dirs,
            'static_files': self.static_files,
            'static_hosting': self.static_hosting,
            'cdn_resources': self.cdn_resources,
            'api_proxy_rules': self.api_proxy_rules,
            'middleware': self.middleware,
            'security': self.security,
            'monitoring': self.monitoring,
            'dependencies': self.dependencies,
            'development': self.development,
            'production': self.production,
            'isolation': self.isolation,
            'env_files': self.env_files,
            'platform': self.platform,
            'board': self.board
        }

    def validate(self) -> List[str]:
        """Validate manifest configuration and return list of errors"""
        errors = []
        
        if not self.name:
            errors.append("Service name is required")
        
        if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
            errors.append(f"Invalid port number: {self.port}")
        
        # Extended service types for ProServe
        valid_types = ['http', 'websocket', 'grpc', 'hybrid', 'static', 'mqtt', 'micropython', 'arduino']
        if self.type not in valid_types:
            errors.append(f"Unsupported service type: {self.type}. Valid types: {valid_types}")
        
        # Validate endpoints
        for i, endpoint in enumerate(self.endpoints):
            if 'path' not in endpoint:
                errors.append(f"Endpoint {i}: missing 'path' field")
            if 'script' not in endpoint and 'handler' not in endpoint:
                errors.append(f"Endpoint {i}: missing 'script' or 'handler' field")
        
        # Validate background tasks
        for i, task in enumerate(self.background_tasks):
            if 'script' not in task and 'handler' not in task:
                errors.append(f"Background task {i}: missing 'script' or 'handler' field")
            if 'interval' not in task:
                errors.append(f"Background task {i}: missing 'interval' field")
        
        # Validate isolation settings for extended platforms
        if self.isolation.get('mode') in ['micropython', 'arduino']:
            if not self.isolation.get('platform') and not self.platform:
                errors.append("Platform must be specified for MicroPython/Arduino isolation")
        
        return errors

    def get_manifest_dir(self) -> Path:
        """Get the directory containing the manifest file"""
        if hasattr(self, '_manifest_path'):
            return Path(self._manifest_path).parent
        return Path.cwd()

    def resolve_script_path(self, script_path: str) -> Path:
        """Resolve script path relative to manifest directory"""
        if os.path.isabs(script_path):
            return Path(script_path)
        return self.get_manifest_dir() / script_path

    def is_embedded_platform(self) -> bool:
        """Check if this manifest is for an embedded platform"""
        return (
            self.type in ['micropython', 'arduino'] or
            self.isolation.get('mode') in ['micropython', 'arduino'] or
            self.platform in ['rp2040', 'esp32', 'esp8266', 'arduino_uno', 'arduino_nano']
        )

    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform-specific information"""
        return {
            'type': self.type,
            'platform': self.platform or self.isolation.get('platform'),
            'board': self.board or self.isolation.get('board'),
            'is_embedded': self.is_embedded_platform(),
            'isolation_mode': self.isolation.get('mode', 'none')
        }

    def create_embedded_manifest(
        self, 
        name: str, 
        platform: str, 
        board: Optional[str] = None,
        **kwargs
    ) -> 'ServiceManifest':
        """Create a manifest optimized for embedded platforms"""
        embedded_data = {
            'name': name,
            'version': kwargs.get('version', '1.0.0'),
            'type': 'micropython' if platform.startswith(('rp2040', 'esp')) else 'arduino',
            'platform': platform,
            'board': board,
            'isolation': {
                'mode': 'micropython' if platform.startswith(('rp2040', 'esp')) else 'arduino',
                'platform': platform,
                'board': board,
                'auto_environment': True,
                'timeout': kwargs.get('timeout', 60),
                'memory_limit': kwargs.get('memory_limit', '1MB')
            },
            'enable_health': False,  # Usually not needed on embedded
            'enable_metrics': False,
            'enable_cors': False,
            **kwargs
        }
        
        return ServiceManifest.from_dict(embedded_data, load_env_files=False)
