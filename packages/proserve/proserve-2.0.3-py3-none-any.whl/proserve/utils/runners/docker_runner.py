"""
ProServe Docker Runner - Containerized Service Runner
Handles running services in Docker containers with container management and health checking
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base_runner import ServiceRunner, HealthChecker
from .runner_config import DockerRunnerConfig, RunnerConfig
from ...core.manifest import ServiceManifest


class DockerRunner(ServiceRunner):
    """Runner for Docker containerized services"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        if config is None:
            config = DockerRunnerConfig()
        elif not isinstance(config, DockerRunnerConfig):
            # Convert generic config to DockerRunnerConfig
            config = DockerRunnerConfig(**config.to_dict())
        
        super().__init__(manifest, config)
        self.config: DockerRunnerConfig = config
        
        # Docker-specific attributes
        self.container = None
        self.docker_client = None
        self.container_id = None
        self.image_built = False
        
    async def start(self) -> bool:
        """Start Docker containerized service"""
        if self.is_running:
            self.logger.warning("Docker service is already running")
            return True
        
        self.logger.info(f"Starting Docker service: {self.manifest.name}")
        
        try:
            # Initialize Docker client
            if not await self._init_docker_client():
                return False
            
            # Build or pull image if needed
            if not await self._prepare_image():
                return False
            
            # Create and start container
            if not await self._start_container():
                return False
            
            self.is_running = True
            self.start_time = time.time()
            self.logger.info(f"Docker service started successfully: {self.container_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Docker service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop Docker container"""
        if not self.is_running:
            self.logger.info("Docker service is not running")
            return True
        
        self.logger.info("Stopping Docker container...")
        
        try:
            if self.container_id:
                # Stop container gracefully
                await self._run_docker_command(['stop', self.container_id, '--time', str(int(self.config.shutdown_timeout))])
                
                # Remove container if configured to do so
                try:
                    await self._run_docker_command(['rm', self.container_id])
                    self.logger.info("Container removed")
                except Exception:
                    self.logger.warning("Failed to remove container (may need manual cleanup)")
            
            self.is_running = False
            self.container_id = None
            self.logger.info("Docker service stopped successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Docker service: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Docker container health"""
        if not self.container_id:
            return {'healthy': False, 'error': 'No container running'}
        
        try:
            # Get container status
            result = await self._run_docker_command(['inspect', self.container_id])
            
            if result['returncode'] != 0:
                return {'healthy': False, 'error': 'Container inspect failed'}
            
            inspect_data = json.loads(result['stdout'])[0]
            container_state = inspect_data.get('State', {})
            
            # Check if container is running
            if not container_state.get('Running', False):
                return {
                    'healthy': False,
                    'error': f"Container not running. Status: {container_state.get('Status', 'unknown')}",
                    'exit_code': container_state.get('ExitCode')
                }
            
            # Check container health if health check is configured
            health_status = container_state.get('Health', {})
            if health_status:
                health = health_status.get('Status', 'none')
                if health == 'healthy':
                    return {
                        'healthy': True,
                        'container_health': health,
                        'uptime': container_state.get('StartedAt')
                    }
                else:
                    return {
                        'healthy': False,
                        'container_health': health,
                        'error': 'Container health check failed'
                    }
            
            # If no health check configured, check if service port is responsive
            if hasattr(self.manifest, 'server') and self.manifest.server:
                service_port = self.manifest.server.get('port', 8000)
                host_port = self.config.ports.get(service_port)
                
                if host_port:
                    tcp_health = await HealthChecker.tcp_health_check('localhost', host_port, timeout=3.0)
                    return {
                        'healthy': tcp_health['healthy'],
                        'container_running': True,
                        'tcp_check': tcp_health
                    }
            
            # Container is running but no specific health check available
            return {'healthy': True, 'container_running': True}
            
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get Docker container status"""
        status = super().get_status()
        status.update({
            'container_id': self.container_id,
            'image': self.config.image,
            'ports': self.config.ports,
            'volumes': self.config.volumes,
            'memory_limit': self.config.memory_limit,
            'cpu_limit': self.config.cpu_limit
        })
        
        return status
    
    async def _init_docker_client(self) -> bool:
        """Initialize Docker client (verify Docker is available)"""
        try:
            result = await self._run_docker_command(['version'])
            
            if result['returncode'] == 0:
                self.logger.debug("Docker client initialized successfully")
                return True
            else:
                self.logger.error("Docker is not available or not running")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Docker client: {e}")
            return False
    
    async def _prepare_image(self) -> bool:
        """Build or pull Docker image"""
        try:
            # If Dockerfile exists, build image
            if self.config.dockerfile and self.config.dockerfile.exists():
                return await self._build_image()
            
            # Otherwise, pull the specified image
            return await self._pull_image()
            
        except Exception as e:
            self.logger.error(f"Failed to prepare image: {e}")
            return False
    
    async def _build_image(self) -> bool:
        """Build Docker image from Dockerfile"""
        self.logger.info(f"Building Docker image from {self.config.dockerfile}")
        
        try:
            build_context = self.config.build_context or self.config.dockerfile.parent
            image_tag = f"{self.manifest.name}:latest"
            
            cmd = [
                'build',
                '-t', image_tag,
                '-f', str(self.config.dockerfile),
                str(build_context)
            ]
            
            result = await self._run_docker_command(cmd, timeout=300)  # 5 minute timeout for build
            
            if result['returncode'] == 0:
                self.config.image = image_tag  # Update image reference
                self.image_built = True
                self.logger.info(f"Image built successfully: {image_tag}")
                return True
            else:
                self.logger.error(f"Image build failed: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Image build error: {e}")
            return False
    
    async def _pull_image(self) -> bool:
        """Pull Docker image from registry"""
        self.logger.info(f"Pulling Docker image: {self.config.image}")
        
        try:
            result = await self._run_docker_command(['pull', self.config.image])
            
            if result['returncode'] == 0:
                self.logger.info(f"Image pulled successfully: {self.config.image}")
                return True
            else:
                self.logger.error(f"Image pull failed: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Image pull error: {e}")
            return False
    
    async def _start_container(self) -> bool:
        """Create and start Docker container"""
        self.logger.info("Starting Docker container...")
        
        try:
            # Build docker run command
            cmd = self._build_run_command()
            
            # Start container
            result = await self._run_docker_command(cmd)
            
            if result['returncode'] == 0:
                self.container_id = result['stdout'].strip()
                self.logger.info(f"Container started: {self.container_id}")
                
                # Wait a moment for container to initialize
                await asyncio.sleep(2)
                
                # Verify container is running
                inspect_result = await self._run_docker_command(['inspect', self.container_id])
                if inspect_result['returncode'] == 0:
                    inspect_data = json.loads(inspect_result['stdout'])[0]
                    if inspect_data['State']['Running']:
                        return True
                    else:
                        self.logger.error(f"Container exited immediately: {inspect_data['State']}")
                        return False
                
                return True
            else:
                self.logger.error(f"Container start failed: {result['stderr']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Container start error: {e}")
            return False
    
    def _build_run_command(self) -> List[str]:
        """Build docker run command with all configuration"""
        cmd = ['run', '--detach']
        
        # Container name
        if self.config.container_name:
            cmd.extend(['--name', self.config.container_name])
        else:
            cmd.extend(['--name', f"{self.manifest.name}-{int(time.time())}"])
        
        # Port mappings
        for container_port, host_port in self.config.ports.items():
            cmd.extend(['-p', f"{host_port}:{container_port}"])
        
        # Volume mappings
        for host_path, container_path in self.config.volumes.items():
            cmd.extend(['-v', f"{host_path}:{container_path}"])
        
        # Environment variables
        env_vars = self._get_container_env()
        for key, value in env_vars.items():
            cmd.extend(['-e', f"{key}={value}"])
        
        # Resource limits
        if self.config.memory_limit:
            cmd.extend(['--memory', self.config.memory_limit])
        
        if self.config.cpu_limit:
            cmd.extend(['--cpus', self.config.cpu_limit])
        
        # Network mode
        cmd.extend(['--network', self.config.network_mode])
        
        # Add restart policy for production
        cmd.extend(['--restart', 'unless-stopped'])
        
        # Image
        cmd.append(self.config.image)
        
        return cmd
    
    def _get_container_env(self) -> Dict[str, str]:
        """Get environment variables for container"""
        env_vars = {}
        
        # Add custom environment variables
        env_vars.update(self.config.env_vars)
        
        # Add service-specific variables
        env_vars['PROSERVE_SERVICE_NAME'] = self.manifest.name
        env_vars['PROSERVE_PLATFORM'] = 'docker'
        
        # Add manifest-based environment variables
        if hasattr(self.manifest, 'env_vars'):
            for env_var in self.manifest.env_vars or []:
                name = env_var.get('name')
                default = env_var.get('default')
                if name and default is not None:
                    env_vars[name] = str(default)
        
        return env_vars
    
    async def _run_docker_command(self, cmd: List[str], timeout: float = 30) -> Dict[str, Any]:
        """Run Docker command and return result"""
        full_cmd = ['docker'] + cmd
        
        try:
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode().strip(),
                'stderr': stderr.decode().strip()
            }
            
        except asyncio.TimeoutError:
            self.logger.error(f"Docker command timeout: {' '.join(cmd)}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timeout'
            }
        except Exception as e:
            self.logger.error(f"Docker command error: {e}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }
    
    async def get_container_logs(self, lines: int = 100) -> str:
        """Get container logs"""
        if not self.container_id:
            return "No container running"
        
        try:
            result = await self._run_docker_command(['logs', '--tail', str(lines), self.container_id])
            
            if result['returncode'] == 0:
                return result['stdout']
            else:
                return f"Failed to get logs: {result['stderr']}"
                
        except Exception as e:
            return f"Error getting logs: {e}"
    
    async def execute_in_container(self, command: str) -> Dict[str, Any]:
        """Execute command inside container"""
        if not self.container_id:
            return {'success': False, 'error': 'No container running'}
        
        try:
            cmd = ['exec', self.container_id] + command.split()
            result = await self._run_docker_command(cmd)
            
            return {
                'success': result['returncode'] == 0,
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'returncode': result['returncode']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def scale_container(self, replicas: int) -> bool:
        """Scale container (using docker-compose if available)"""
        # This is a placeholder - actual scaling would require docker-compose or orchestration
        self.logger.warning("Container scaling requires orchestration system (docker-compose, kubernetes, etc.)")
        return False
    
    async def get_container_stats(self) -> Dict[str, Any]:
        """Get container resource usage statistics"""
        if not self.container_id:
            return {'error': 'No container running'}
        
        try:
            result = await self._run_docker_command(['stats', '--no-stream', '--format', 'json', self.container_id])
            
            if result['returncode'] == 0:
                stats_data = json.loads(result['stdout'])
                return {
                    'cpu_percent': stats_data.get('CPUPerc', '0%'),
                    'memory_usage': stats_data.get('MemUsage', '0B / 0B'),
                    'memory_percent': stats_data.get('MemPerc', '0%'),
                    'network_io': stats_data.get('NetIO', '0B / 0B'),
                    'block_io': stats_data.get('BlockIO', '0B / 0B'),
                    'pids': stats_data.get('PIDs', '0')
                }
            else:
                return {'error': f"Failed to get stats: {result['stderr']}"}
                
        except Exception as e:
            return {'error': str(e)}


# Utility functions for Docker runners
def check_docker_availability() -> bool:
    """Check if Docker is available and running"""
    import subprocess
    
    try:
        result = subprocess.run(['docker', 'version'], capture_output=True, timeout=10)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def generate_dockerfile(manifest: ServiceManifest, working_dir: Path) -> str:
    """Generate Dockerfile content for service"""
    lines = [
        "# Generated Dockerfile for ProServe service",
        f"# Service: {manifest.name}",
        "",
        "FROM python:3.11-slim",
        "",
        "WORKDIR /app",
        "",
        "# Install system dependencies",
        "RUN apt-get update && apt-get install -y \\",
        "    gcc \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "",
        "# Copy requirements and install Python dependencies",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "",
        "# Copy service code",
        "COPY . .",
        "",
        "# Expose service port"
    ]
    
    # Add port exposure
    if hasattr(manifest, 'server') and manifest.server:
        port = manifest.server.get('port', 8000)
        lines.append(f"EXPOSE {port}")
    else:
        lines.append("EXPOSE 8000")
    
    lines.extend([
        "",
        "# Run service",
        "CMD [\"python\", \"-m\", \"proserve.cli\", \"run\", \"manifest.yaml\"]"
    ])
    
    return '\n'.join(lines)


def create_docker_compose_config(manifest: ServiceManifest, config: DockerRunnerConfig) -> Dict[str, Any]:
    """Create docker-compose configuration for service"""
    service_config = {
        'build': '.',
        'ports': [f"{host}:{container}" for container, host in config.ports.items()],
        'environment': config.env_vars,
        'volumes': [f"{host}:{container}" for host, container in config.volumes.items()],
        'restart': 'unless-stopped'
    }
    
    if config.memory_limit:
        service_config['mem_limit'] = config.memory_limit
    
    if config.cpu_limit:
        service_config['cpus'] = float(config.cpu_limit)
    
    return {
        'version': '3.8',
        'services': {
            manifest.name: service_config
        }
    }
