"""
ProServe Runner Configuration - Configuration Classes for Service Runners
Defines configuration options and settings for different types of service runners
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RunnerConfig:
    """Configuration for service runners"""
    
    # Basic settings
    auto_restart: bool = True
    max_restarts: int = 5
    restart_delay: float = 1.0
    health_check_interval: float = 30.0
    shutdown_timeout: float = 30.0
    
    # Platform settings
    platform: Optional[str] = None
    board: Optional[str] = None
    device_port: Optional[str] = None
    
    # Environment settings
    env_vars: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[Path] = None
    
    # Monitoring settings
    enable_monitoring: bool = True
    log_level: str = "INFO"
    metrics_enabled: bool = True
    
    # Performance settings
    memory_limit: Optional[int] = None  # MB
    cpu_limit: Optional[float] = None   # CPU cores
    
    # Security settings
    run_as_user: Optional[str] = None
    enable_sandbox: bool = False
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if self.max_restarts < 0:
            errors.append("max_restarts must be non-negative")
        
        if self.restart_delay < 0:
            errors.append("restart_delay must be non-negative")
        
        if self.health_check_interval <= 0:
            errors.append("health_check_interval must be positive")
        
        if self.shutdown_timeout <= 0:
            errors.append("shutdown_timeout must be positive")
        
        if self.memory_limit is not None and self.memory_limit <= 0:
            errors.append("memory_limit must be positive")
        
        if self.cpu_limit is not None and self.cpu_limit <= 0:
            errors.append("cpu_limit must be positive")
        
        if self.working_dir and not isinstance(self.working_dir, Path):
            errors.append("working_dir must be a Path object")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'auto_restart': self.auto_restart,
            'max_restarts': self.max_restarts,
            'restart_delay': self.restart_delay,
            'health_check_interval': self.health_check_interval,
            'shutdown_timeout': self.shutdown_timeout,
            'platform': self.platform,
            'board': self.board,
            'device_port': self.device_port,
            'env_vars': self.env_vars,
            'working_dir': str(self.working_dir) if self.working_dir else None,
            'enable_monitoring': self.enable_monitoring,
            'log_level': self.log_level,
            'metrics_enabled': self.metrics_enabled,
            'memory_limit': self.memory_limit,
            'cpu_limit': self.cpu_limit,
            'run_as_user': self.run_as_user,
            'enable_sandbox': self.enable_sandbox
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RunnerConfig':
        """Create from dictionary"""
        working_dir = data.get('working_dir')
        if working_dir:
            data['working_dir'] = Path(working_dir)
        
        return cls(**data)


@dataclass
class StandardRunnerConfig(RunnerConfig):
    """Configuration specific to standard Python runners"""
    
    # Python-specific settings
    python_executable: str = "python3"
    virtual_env: Optional[Path] = None
    requirements_file: Optional[Path] = None
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Process management
    use_uvicorn: bool = True
    workers: int = 1
    
    def validate(self) -> List[str]:
        """Validate standard runner configuration"""
        errors = super().validate()
        
        if self.port < 1 or self.port > 65535:
            errors.append("port must be between 1 and 65535")
        
        if self.workers < 1:
            errors.append("workers must be at least 1")
        
        if self.virtual_env and not self.virtual_env.exists():
            errors.append(f"virtual_env path does not exist: {self.virtual_env}")
        
        if self.requirements_file and not self.requirements_file.exists():
            errors.append(f"requirements_file does not exist: {self.requirements_file}")
        
        return errors


@dataclass
class EmbeddedRunnerConfig(RunnerConfig):
    """Configuration specific to embedded device runners"""
    
    # Device connection settings
    baud_rate: int = 115200
    timeout: float = 30.0
    auto_detect_device: bool = True
    
    # Firmware settings
    firmware_version: Optional[str] = None
    flash_before_deploy: bool = False
    
    # Code generation settings
    optimize_code: bool = True
    strip_comments: bool = True
    minify_code: bool = False
    
    # Memory management
    enable_gc: bool = True
    gc_threshold: Optional[int] = None
    
    def validate(self) -> List[str]:
        """Validate embedded runner configuration"""
        errors = super().validate()
        
        if self.baud_rate not in [9600, 19200, 38400, 57600, 115200, 230400, 460800]:
            errors.append("baud_rate must be a standard baud rate")
        
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        
        if self.gc_threshold is not None and self.gc_threshold <= 0:
            errors.append("gc_threshold must be positive")
        
        return errors


@dataclass
class DockerRunnerConfig(RunnerConfig):
    """Configuration specific to Docker runners"""
    
    # Docker settings
    image: str = "python:3.11-slim"
    dockerfile: Optional[Path] = None
    build_context: Optional[Path] = None
    
    # Container settings
    container_name: Optional[str] = None
    network_mode: str = "bridge"
    ports: Dict[int, int] = field(default_factory=dict)  # container_port: host_port
    volumes: Dict[str, str] = field(default_factory=dict)  # host_path: container_path
    
    # Resource limits
    memory_limit: str = "512m"
    cpu_limit: str = "1"
    
    # Docker daemon settings
    docker_host: Optional[str] = None
    registry: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate Docker runner configuration"""
        errors = super().validate()
        
        if not self.image:
            errors.append("image is required for Docker runner")
        
        if self.dockerfile and not self.dockerfile.exists():
            errors.append(f"dockerfile does not exist: {self.dockerfile}")
        
        if self.build_context and not self.build_context.exists():
            errors.append(f"build_context does not exist: {self.build_context}")
        
        # Validate port mappings
        for container_port, host_port in self.ports.items():
            if not (1 <= container_port <= 65535):
                errors.append(f"invalid container port: {container_port}")
            if not (1 <= host_port <= 65535):
                errors.append(f"invalid host port: {host_port}")
        
        return errors


# Convenience functions for creating configurations
def create_standard_config(**kwargs) -> StandardRunnerConfig:
    """Create standard runner configuration with defaults"""
    return StandardRunnerConfig(**kwargs)


def create_embedded_config(platform: str = "rp2040", **kwargs) -> EmbeddedRunnerConfig:
    """Create embedded runner configuration with platform defaults"""
    config = EmbeddedRunnerConfig(platform=platform, **kwargs)
    
    # Platform-specific defaults
    if platform == "esp32":
        config.baud_rate = 115200
        config.memory_limit = 512  # KB
    elif platform == "esp8266":
        config.baud_rate = 115200
        config.memory_limit = 80   # KB
    elif platform == "rp2040":
        config.baud_rate = 115200
        config.memory_limit = 256  # KB
    
    return config


def create_docker_config(image: str = "python:3.11-slim", **kwargs) -> DockerRunnerConfig:
    """Create Docker runner configuration with defaults"""
    return DockerRunnerConfig(image=image, **kwargs)


def auto_detect_runner_config(manifest_path: Optional[str] = None) -> RunnerConfig:
    """Auto-detect appropriate runner configuration based on environment"""
    # Try to detect platform from environment or manifest
    try:
        import platform
        system = platform.system().lower()
        
        # Check for embedded platforms
        if system == "linux":
            # Check if running on Raspberry Pi
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read().lower()
                    if "raspberry pi" in cpuinfo:
                        return create_embedded_config("rp2040")
            except FileNotFoundError:
                pass
        
        # Check for Docker environment
        if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER"):
            return create_docker_config()
        
        # Default to standard runner
        return create_standard_config()
        
    except Exception:
        # Fallback to standard configuration
        return create_standard_config()
