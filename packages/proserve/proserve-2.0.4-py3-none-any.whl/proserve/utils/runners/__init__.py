"""
ProServe Service Runners - Modular Service Runner Components
Refactored from monolithic runner.py into focused, testable runner modules
"""

from .runner_config import (
    RunnerConfig, StandardRunnerConfig, EmbeddedRunnerConfig, DockerRunnerConfig,
    create_standard_config, create_embedded_config, create_docker_config,
    auto_detect_runner_config
)
from .base_runner import ServiceRunner, HealthChecker
from .standard_runner import (
    StandardRunner, detect_python_framework, find_free_port,
    create_virtual_environment, install_requirements
)
from .embedded_runner import (
    EmbeddedRunner, detect_platform_from_device, optimize_code_for_platform
)
from .docker_runner import (
    DockerRunner, check_docker_availability, generate_dockerfile,
    create_docker_compose_config
)
from .runner_factory import (
    create_runner, run_service, detect_runner_type,
    get_available_runners, get_runner_capabilities, recommend_runner,
    validate_runner_requirements, detect_environment_capabilities
)

__all__ = [
    # Configuration Classes
    'RunnerConfig', 'StandardRunnerConfig', 'EmbeddedRunnerConfig', 'DockerRunnerConfig',
    'create_standard_config', 'create_embedded_config', 'create_docker_config',
    'auto_detect_runner_config',
    
    # Base Classes
    'ServiceRunner', 'HealthChecker',
    
    # Runner Implementations
    'StandardRunner', 'EmbeddedRunner', 'DockerRunner',
    
    # Standard Runner Utilities
    'detect_python_framework', 'find_free_port',
    'create_virtual_environment', 'install_requirements',
    
    # Embedded Runner Utilities
    'detect_platform_from_device', 'optimize_code_for_platform',
    
    # Docker Runner Utilities
    'check_docker_availability', 'generate_dockerfile', 'create_docker_compose_config',
    
    # Factory Functions
    'create_runner', 'run_service', 'detect_runner_type',
    'get_available_runners', 'get_runner_capabilities', 'recommend_runner',
    'validate_runner_requirements', 'detect_environment_capabilities'
]

# Backward compatibility exports
ServiceRunner = ServiceRunner
StandardRunner = StandardRunner
EmbeddedRunner = EmbeddedRunner
DockerRunner = DockerRunner
