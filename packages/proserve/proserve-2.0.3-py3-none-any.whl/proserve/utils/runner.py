"""
ProServe Runner - Simplified and Modular
New streamlined runner system that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular runner system.
The heavy lifting is done by the runners/ package modules:
- runners/base_runner.py - Abstract base runner class
- runners/standard_runner.py - Standard Python service runner
- runners/docker_runner.py - Docker container runner
- runners/embedded_runner.py - Embedded device runner
- runners/runner_config.py - Runner configuration classes
- runners/runner_factory.py - Dynamic runner selection factory

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular runner components (fixed imports)
from .runners import (
    ServiceRunner as BaseRunner,  # ServiceRunner is the actual base class
    HealthChecker,
    StandardRunner,
    DockerRunner,
    EmbeddedRunner,
    RunnerConfig,
    StandardRunnerConfig as DockerConfig,  # Alias for compatibility
    EmbeddedRunnerConfig as EmbeddedConfig,  # Alias for compatibility
    create_runner,
    get_available_runners
)

# Create missing factory alias
class RunnerFactory:
    """Factory for creating runners"""
    @staticmethod
    def create_runner(*args, **kwargs):
        return create_runner(*args, **kwargs)

# Legacy compatibility - expose the main classes
__all__ = [
    'BaseRunner',
    'ServiceRunner', 
    'HealthChecker',
    'StandardRunner',
    'DockerRunner',
    'EmbeddedRunner',
    'RunnerConfig',
    'DockerConfig',
    'EmbeddedConfig',
    'RunnerFactory',
    'create_runner',
    'get_available_runners'
]

# Export aliases for backward compatibility
ServiceRunner = BaseRunner  # Make ServiceRunner available for import

# Add missing run_service function for backward compatibility
def run_service(manifest, config=None):
    """Run service using appropriate runner"""
    return create_runner(manifest, config)
