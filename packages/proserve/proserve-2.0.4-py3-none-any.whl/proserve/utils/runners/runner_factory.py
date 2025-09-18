"""
ProServe Runner Factory - Dynamic Runner Selection and Creation
Factory functions for creating appropriate runners based on manifest and configuration
"""

from typing import Optional, Dict, Any, Type
from pathlib import Path

from ...core.manifest import ServiceManifest
from .runner_config import RunnerConfig, StandardRunnerConfig, EmbeddedRunnerConfig, DockerRunnerConfig
from .base_runner import ServiceRunner
from .standard_runner import StandardRunner, detect_python_framework
from .embedded_runner import EmbeddedRunner, detect_platform_from_device
from .docker_runner import DockerRunner, check_docker_availability


def create_runner(manifest: ServiceManifest, config: Optional[RunnerConfig] = None) -> ServiceRunner:
    """Create appropriate runner based on manifest and configuration"""
    
    # If config specifies platform explicitly, use that
    if config and config.platform:
        return _create_runner_for_platform(manifest, config)
    
    # Auto-detect runner type from manifest
    runner_type = detect_runner_type(manifest)
    
    # Create appropriate config if not provided
    if config is None:
        config = _create_default_config_for_type(runner_type, manifest)
    
    # Create runner
    if runner_type == 'standard':
        return StandardRunner(manifest, config)
    elif runner_type == 'embedded':
        return EmbeddedRunner(manifest, config)
    elif runner_type == 'docker':
        return DockerRunner(manifest, config)
    else:
        # Default to standard runner
        return StandardRunner(manifest, config)


def _create_runner_for_platform(manifest: ServiceManifest, config: RunnerConfig) -> ServiceRunner:
    """Create runner for explicitly specified platform"""
    platform = config.platform.lower()
    
    # Embedded platforms
    embedded_platforms = [
        'rp2040', 'esp32', 'esp8266', 'pyboard',
        'uno_r4_wifi', 'esp32dev', 'nano33iot', 'leonardo'
    ]
    
    if platform in embedded_platforms:
        if not isinstance(config, EmbeddedRunnerConfig):
            config = EmbeddedRunnerConfig(**config.to_dict())
        return EmbeddedRunner(manifest, config)
    
    elif platform == 'docker':
        if not isinstance(config, DockerRunnerConfig):
            config = DockerRunnerConfig(**config.to_dict())
        return DockerRunner(manifest, config)
    
    else:
        # Default to standard runner for unknown platforms
        if not isinstance(config, StandardRunnerConfig):
            config = StandardRunnerConfig(**config.to_dict())
        return StandardRunner(manifest, config)


def detect_runner_type(manifest: ServiceManifest) -> str:
    """Detect appropriate runner type from manifest"""
    
    # Check platform from manifest
    platform = getattr(manifest, 'platform', 'python').lower()
    
    # Embedded platforms
    if platform in ['micropython', 'arduino', 'rp2040', 'esp32', 'esp8266']:
        return 'embedded'
    
    # Docker deployment
    deployment = getattr(manifest, 'deployment', {})
    if isinstance(deployment, dict):
        target = deployment.get('target', '').lower()
        if target in ['docker', 'kubernetes', 'container']:
            return 'docker'
    
    # Check if Dockerfile exists
    manifest_dir = Path(getattr(manifest, '_manifest_path', '.')).parent
    if (manifest_dir / 'Dockerfile').exists():
        return 'docker'
    
    # Check environment variables for deployment hints
    import os
    if os.getenv('DOCKER_CONTAINER') or os.path.exists('/.dockerenv'):
        return 'docker'
    
    # Default to standard Python service
    return 'standard'


def _create_default_config_for_type(runner_type: str, manifest: ServiceManifest) -> RunnerConfig:
    """Create default configuration for runner type"""
    
    if runner_type == 'embedded':
        # Try to detect platform from manifest or environment
        platform = getattr(manifest, 'platform', 'rp2040')
        return EmbeddedRunnerConfig(platform=platform)
    
    elif runner_type == 'docker':
        # Use sensible Docker defaults
        config = DockerRunnerConfig()
        
        # Set up port mapping if manifest specifies server
        if hasattr(manifest, 'server') and manifest.server:
            service_port = manifest.server.get('port', 8000)
            config.ports[service_port] = service_port
        
        return config
    
    else:  # standard
        config = StandardRunnerConfig()
        
        # Set server configuration from manifest
        if hasattr(manifest, 'server') and manifest.server:
            config.host = manifest.server.get('host', '0.0.0.0')
            config.port = manifest.server.get('port', 8000)
        
        # Try to detect Python framework
        if hasattr(manifest, '_manifest_path'):
            manifest_dir = Path(manifest._manifest_path).parent
            framework = detect_python_framework(manifest_dir)
            
            # Adjust config based on framework
            if framework == 'fastapi':
                config.use_uvicorn = True
            elif framework == 'flask':
                config.use_uvicorn = False
            elif framework == 'django':
                config.use_uvicorn = False
                config.python_executable = 'python'  # Django manage.py
        
        return config


async def run_service(manifest: ServiceManifest, config: Optional[RunnerConfig] = None) -> None:
    """Run service with appropriate runner"""
    runner = create_runner(manifest, config)
    
    try:
        await runner.run()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    finally:
        if runner.is_running:
            await runner.stop()


def get_available_runners() -> Dict[str, Type[ServiceRunner]]:
    """Get dictionary of available runner types"""
    return {
        'standard': StandardRunner,
        'embedded': EmbeddedRunner,
        'docker': DockerRunner
    }


def get_runner_capabilities() -> Dict[str, Dict[str, Any]]:
    """Get capabilities and requirements for each runner type"""
    return {
        'standard': {
            'platforms': ['python', 'any'],
            'requirements': ['python3'],
            'features': ['http_server', 'websockets', 'background_tasks', 'auto_restart'],
            'deployment_targets': ['local', 'vm', 'bare_metal']
        },
        'embedded': {
            'platforms': ['micropython', 'arduino', 'rp2040', 'esp32', 'esp8266'],
            'requirements': ['device_connection', 'serial_port'],
            'features': ['device_deployment', 'memory_optimization', 'real_time'],
            'deployment_targets': ['embedded_device', 'microcontroller']
        },
        'docker': {
            'platforms': ['docker', 'any'],
            'requirements': ['docker_engine'],
            'features': ['containerization', 'resource_limits', 'scaling', 'isolation'],
            'deployment_targets': ['docker', 'kubernetes', 'cloud']
        }
    }


def recommend_runner(manifest: ServiceManifest, environment_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Recommend best runner based on manifest and environment"""
    environment_info = environment_info or {}
    
    recommendations = []
    
    # Check each runner type
    runners = get_runner_capabilities()
    
    for runner_type, capabilities in runners.items():
        score = 0
        reasons = []
        
        # Platform compatibility
        manifest_platform = getattr(manifest, 'platform', 'python').lower()
        if manifest_platform in capabilities['platforms'] or 'any' in capabilities['platforms']:
            score += 10
            reasons.append(f"Platform compatible ({manifest_platform})")
        
        # Deployment target
        deployment = getattr(manifest, 'deployment', {})
        if isinstance(deployment, dict):
            target = deployment.get('target', '').lower()
            if target in capabilities['deployment_targets']:
                score += 15
                reasons.append(f"Deployment target match ({target})")
        
        # Feature requirements
        if hasattr(manifest, 'endpoints') and manifest.endpoints:
            if 'http_server' in capabilities['features']:
                score += 5
                reasons.append("HTTP server support")
        
        if hasattr(manifest, 'background_tasks') and manifest.background_tasks:
            if 'background_tasks' in capabilities['features']:
                score += 5
                reasons.append("Background tasks support")
        
        # Environment availability
        if runner_type == 'docker':
            if environment_info.get('docker_available', check_docker_availability()):
                score += 10
                reasons.append("Docker available")
            else:
                score -= 20
                reasons.append("Docker not available")
        
        if runner_type == 'embedded':
            if environment_info.get('devices_connected', []):
                score += 15
                reasons.append("Embedded devices detected")
            else:
                score -= 10
                reasons.append("No embedded devices detected")
        
        recommendations.append({
            'type': runner_type,
            'score': score,
            'reasons': reasons,
            'suitable': score > 0
        })
    
    # Sort by score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'recommended': recommendations[0]['type'] if recommendations and recommendations[0]['suitable'] else 'standard',
        'all_options': recommendations
    }


def validate_runner_requirements(runner_type: str, environment_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate that requirements are met for a specific runner type"""
    environment_info = environment_info or {}
    capabilities = get_runner_capabilities()
    
    if runner_type not in capabilities:
        return {'valid': False, 'errors': [f'Unknown runner type: {runner_type}']}
    
    requirements = capabilities[runner_type]['requirements']
    errors = []
    warnings = []
    
    for requirement in requirements:
        if requirement == 'python3':
            # Check Python availability
            import sys
            if sys.version_info.major < 3:
                errors.append('Python 3 is required')
        
        elif requirement == 'docker_engine':
            if not environment_info.get('docker_available', check_docker_availability()):
                errors.append('Docker engine is not available or not running')
        
        elif requirement == 'device_connection':
            if not environment_info.get('devices_connected', []):
                warnings.append('No embedded devices detected - will use emulation mode')
        
        elif requirement == 'serial_port':
            try:
                import serial
            except ImportError:
                errors.append('PySerial library is required for embedded devices')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


# Auto-detection utilities
def detect_environment_capabilities() -> Dict[str, Any]:
    """Detect current environment capabilities"""
    import os
    import sys
    
    capabilities = {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
        'platform': sys.platform,
        'docker_available': check_docker_availability(),
        'devices_connected': [],
        'in_container': os.path.exists('/.dockerenv') or bool(os.getenv('DOCKER_CONTAINER'))
    }
    
    # Try to detect connected devices
    try:
        from ...isolation.platforms import detect_connected_devices
        capabilities['devices_connected'] = [d.to_dict() for d in detect_connected_devices()]
    except Exception:
        pass
    
    # Check for common development tools
    tools = {}
    for tool in ['docker', 'arduino-cli', 'micropython', 'picotool']:
        try:
            import subprocess
            result = subprocess.run([tool, '--version'], capture_output=True, timeout=5)
            tools[tool] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools[tool] = False
    
    capabilities['development_tools'] = tools
    
    return capabilities
