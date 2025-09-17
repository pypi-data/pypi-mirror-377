"""
ProServe Standard Runner - Standard Python Service Runner
Handles running regular Python services with process management and health checking
"""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from .base_runner import ServiceRunner, HealthChecker
from .runner_config import StandardRunnerConfig, RunnerConfig
from ...core.manifest import ServiceManifest


class StandardRunner(ServiceRunner):
    """Standard runner for regular Python services"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        if config is None:
            config = StandardRunnerConfig()
        elif not isinstance(config, StandardRunnerConfig):
            # Convert generic config to StandardRunnerConfig
            config = StandardRunnerConfig(**config.to_dict())
        
        super().__init__(manifest, config)
        self.config: StandardRunnerConfig = config
        
        # Service-specific attributes
        self.service_module = None
        self.service_port = None
        
    async def start(self) -> bool:
        """Start standard Python service"""
        if self.is_running:
            self.logger.warning("Service is already running")
            return True
        
        self.logger.info(f"Starting standard Python service: {self.manifest.name}")
        
        try:
            # Prepare environment
            env = self._prepare_environment()
            
            # Determine service port
            self.service_port = self._determine_service_port()
            
            # Build command
            cmd = self._build_command()
            
            # Start process
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                cwd=self.config.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for the process to start
            await asyncio.sleep(1)
            
            # Check if process is still running
            if self.process.returncode is None:
                self.is_running = True
                self.start_time = time.time()
                self.logger.info(f"Service started successfully with PID {self.process.pid}")
                
                # Start output monitoring
                asyncio.create_task(self._monitor_output())
                
                return True
            else:
                self.logger.error(f"Service process exited immediately with code {self.process.returncode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop standard Python service"""
        if not self.is_running:
            self.logger.info("Service is not running")
            return True
        
        self.logger.info("Stopping standard Python service...")
        
        try:
            if self.process:
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=self.config.shutdown_timeout)
                    self.logger.info("Service stopped gracefully")
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown failed
                    self.logger.warning("Graceful shutdown timeout, forcing kill...")
                    self.process.kill()
                    await self.process.wait()
                    self.logger.info("Service force-killed")
            
            self.is_running = False
            self.process = None
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health via HTTP endpoint"""
        # First check if process is running
        process_health = HealthChecker.process_health_check(self.process)
        if not process_health['healthy']:
            return process_health
        
        # If service has HTTP endpoints, check HTTP health
        if self.service_port and self.manifest.enable_health_check:
            health_url = f"http://{self.config.host}:{self.service_port}/health"
            http_health = await HealthChecker.http_health_check(health_url, timeout=5.0)
            
            if http_health['healthy']:
                return {
                    'healthy': True,
                    'process': process_health,
                    'http': http_health,
                    'port': self.service_port
                }
            else:
                # HTTP health failed but process is running - might be starting up
                return {
                    'healthy': False,
                    'process': process_health,
                    'http': http_health,
                    'error': 'HTTP health check failed'
                }
        
        # No HTTP health check available, rely on process health
        return process_health
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        status = super().get_status()
        status.update({
            'port': self.service_port,
            'host': self.config.host,
            'python_executable': self.config.python_executable,
            'workers': self.config.workers,
            'use_uvicorn': self.config.use_uvicorn
        })
        
        return status
    
    def _prepare_environment(self) -> Dict[str, str]:
        """Prepare environment variables for the service"""
        env = os.environ.copy()
        
        # Add custom environment variables
        env.update(self.config.env_vars)
        
        # Add service-specific variables
        if self.service_port:
            env['PORT'] = str(self.service_port)
        env['HOST'] = self.config.host
        
        # Add Python path if needed
        if self.config.working_dir:
            python_path = env.get('PYTHONPATH', '')
            if python_path:
                env['PYTHONPATH'] = f"{self.config.working_dir}:{python_path}"
            else:
                env['PYTHONPATH'] = str(self.config.working_dir)
        
        return env
    
    def _determine_service_port(self) -> int:
        """Determine the port the service should run on"""
        # Check manifest for server configuration
        if hasattr(self.manifest, 'server') and self.manifest.server:
            return self.manifest.server.get('port', self.config.port)
        
        # Use config port
        return self.config.port
    
    def _build_command(self) -> List[str]:
        """Build command to start the service"""
        cmd = [self.config.python_executable]
        
        # Add service module or script
        if self.config.use_uvicorn and self._has_asgi_app():
            # Use uvicorn for ASGI applications
            cmd.extend([
                '-m', 'uvicorn',
                self._get_asgi_app(),
                '--host', self.config.host,
                '--port', str(self.service_port),
                '--workers', str(self.config.workers)
            ])
        else:
            # Direct Python execution
            service_script = self._get_service_script()
            if service_script:
                cmd.append(str(service_script))
            else:
                # Use ProServe CLI to run the service
                cmd.extend(['-m', 'proserve.cli', 'run', str(self.manifest._manifest_path)])
        
        return cmd
    
    def _has_asgi_app(self) -> bool:
        """Check if service has ASGI application"""
        # Simple heuristic - check if there's an app.py or main.py with ASGI patterns
        if self.config.working_dir:
            for app_file in ['app.py', 'main.py', 'server.py']:
                app_path = self.config.working_dir / app_file
                if app_path.exists():
                    try:
                        with open(app_path, 'r') as f:
                            content = f.read()
                            if any(pattern in content for pattern in ['FastAPI', 'Starlette', 'app = ', 'application = ']):
                                return True
                    except Exception:
                        continue
        
        return False
    
    def _get_asgi_app(self) -> str:
        """Get ASGI application module path"""
        if self.config.working_dir:
            # Look for common ASGI app patterns
            for app_file in ['app.py', 'main.py', 'server.py']:
                app_path = self.config.working_dir / app_file
                if app_path.exists():
                    module_name = app_file[:-3]  # Remove .py extension
                    return f"{module_name}:app"
        
        # Default fallback
        return "main:app"
    
    def _get_service_script(self) -> Optional[Path]:
        """Get the main service script to execute"""
        if self.config.working_dir:
            # Look for common entry points
            for script_name in ['main.py', 'app.py', 'server.py', 'run.py']:
                script_path = self.config.working_dir / script_name
                if script_path.exists():
                    return script_path
        
        return None
    
    async def _monitor_output(self):
        """Monitor service output for logging"""
        if not self.process:
            return
        
        try:
            # Monitor stdout
            async def read_stdout():
                async for line in self.process.stdout:
                    line_str = line.decode().strip()
                    if line_str:
                        self.logger.info(f"[STDOUT] {line_str}")
            
            # Monitor stderr
            async def read_stderr():
                async for line in self.process.stderr:
                    line_str = line.decode().strip()
                    if line_str:
                        self.logger.warning(f"[STDERR] {line_str}")
            
            # Run both monitors concurrently
            await asyncio.gather(read_stdout(), read_stderr(), return_exceptions=True)
            
        except Exception as e:
            self.logger.debug(f"Output monitoring stopped: {e}")
    
    async def reload(self) -> bool:
        """Reload service (for development)"""
        self.logger.info("Reloading service...")
        
        # Send SIGHUP if process supports it
        if self.process and hasattr(self.process, 'send_signal'):
            try:
                import signal
                self.process.send_signal(signal.SIGHUP)
                self.logger.info("Sent SIGHUP signal for reload")
                return True
            except Exception as e:
                self.logger.warning(f"Could not send SIGHUP: {e}")
        
        # Fallback to restart
        return await self.restart()
    
    async def scale(self, workers: int) -> bool:
        """Scale service workers (if supported)"""
        if workers == self.config.workers:
            self.logger.info(f"Service already has {workers} workers")
            return True
        
        self.logger.info(f"Scaling service from {self.config.workers} to {workers} workers")
        
        # Update config
        old_workers = self.config.workers
        self.config.workers = workers
        
        # Restart service with new worker count
        success = await self.restart()
        
        if success:
            self.logger.info(f"Successfully scaled to {workers} workers")
        else:
            # Rollback on failure
            self.config.workers = old_workers
            self.logger.error(f"Failed to scale workers, rolling back to {old_workers}")
        
        return success


# Utility functions for standard runners
def detect_python_framework(working_dir: Path) -> str:
    """Detect Python framework used in the project"""
    if not working_dir.exists():
        return 'unknown'
    
    # Check for framework files
    frameworks = {
        'fastapi': ['main.py', 'app.py'],
        'flask': ['app.py', 'main.py'],
        'django': ['manage.py', 'wsgi.py'],
        'starlette': ['app.py', 'main.py'],
        'tornado': ['app.py', 'main.py']
    }
    
    # Check requirements.txt for framework dependencies
    requirements_file = working_dir / 'requirements.txt'
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().lower()
                
                if 'fastapi' in requirements:
                    return 'fastapi'
                elif 'flask' in requirements:
                    return 'flask'
                elif 'django' in requirements:
                    return 'django'
                elif 'starlette' in requirements:
                    return 'starlette'
                elif 'tornado' in requirements:
                    return 'tornado'
        except Exception:
            pass
    
    # Check for framework-specific files
    for framework, files in frameworks.items():
        for file_name in files:
            file_path = working_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read().lower()
                        if framework in content:
                            return framework
                except Exception:
                    continue
    
    return 'unknown'


def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find a free port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")


def create_virtual_environment(venv_path: Path, python_executable: str = "python3") -> bool:
    """Create virtual environment for the service"""
    try:
        import subprocess
        
        # Create virtual environment
        subprocess.run([
            python_executable, '-m', 'venv', str(venv_path)
        ], check=True)
        
        return True
        
    except Exception as e:
        return False


def install_requirements(venv_path: Path, requirements_file: Path) -> bool:
    """Install requirements in virtual environment"""
    try:
        import subprocess
        
        pip_path = venv_path / 'bin' / 'pip'
        if not pip_path.exists():
            pip_path = venv_path / 'Scripts' / 'pip.exe'  # Windows
        
        if not pip_path.exists():
            return False
        
        subprocess.run([
            str(pip_path), 'install', '-r', str(requirements_file)
        ], check=True)
        
        return True
        
    except Exception:
        return False
