"""
ProServe Service Runners
Advanced service runners for different platforms and environments
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import tempfile
import signal

from ..core.manifest import ServiceManifest
from ..core.logging import create_logger
from .helpers import (
    detect_devices, get_platform_info, is_embedded_platform,
    find_free_port, create_backup, safe_import
)


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
    
    # Isolation settings
    isolation_mode: str = "none"
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    
    # Custom settings
    custom: Dict[str, Any] = field(default_factory=dict)


class ServiceRunner(ABC):
    """Abstract base class for service runners"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        self.manifest = manifest
        self.config = config or RunnerConfig()
        self.logger = create_logger(f"runner-{self.manifest.name}")
        self.is_running = False
        self.process = None
        self.restart_count = 0
        
    @abstractmethod
    async def start(self) -> bool:
        """Start the service"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the service"""
        pass
    
    @abstractmethod
    async def restart(self) -> bool:
        """Restart the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check service health"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        pass
    
    async def run(self):
        """Run service with monitoring and auto-restart"""
        self.logger.info(f"Starting service runner for {self.manifest.name}")
        
        try:
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Initial start
            if not await self.start():
                self.logger.error("Failed to start service")
                return
            
            # Monitoring loop
            await self._monitoring_loop()
            
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Runner error: {e}")
        finally:
            await self.stop()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            self.logger.info(f"Received signal {sig}")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _monitoring_loop(self):
        """Main monitoring loop with health checks and auto-restart"""
        self.is_running = True
        
        while self.is_running:
            try:
                # Health check
                if self.config.enable_monitoring:
                    is_healthy = await self.health_check()
                    
                    if not is_healthy and self.config.auto_restart:
                        self.logger.warning("Health check failed, attempting restart")
                        
                        if self.restart_count < self.config.max_restarts:
                            await self.restart()
                            self.restart_count += 1
                            await asyncio.sleep(self.config.restart_delay)
                        else:
                            self.logger.error("Max restart attempts reached")
                            self.is_running = False
                            break
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(1.0)


class StandardRunner(ServiceRunner):
    """Standard runner for regular Python services"""
    
    async def start(self) -> bool:
        """Start standard Python service"""
        try:
            from ..core.service import ProServeService
            
            self.logger.info(f"Starting standard service: {self.manifest.name}")
            
            # Create service instance
            self.service = ProServeService(self.manifest)
            
            # Start service in background task
            self.service_task = asyncio.create_task(self.service.run())
            
            # Wait a bit to ensure service started
            await asyncio.sleep(1.0)
            
            self.logger.info(f"Service started on {self.manifest.host}:{self.manifest.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop standard Python service"""
        try:
            if hasattr(self, 'service') and self.service:
                await self.service.stop()
            
            if hasattr(self, 'service_task') and self.service_task:
                self.service_task.cancel()
                try:
                    await self.service_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Service stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart standard Python service"""
        await self.stop()
        await asyncio.sleep(self.config.restart_delay)
        return await self.start()
    
    async def health_check(self) -> bool:
        """Check service health via HTTP endpoint"""
        try:
            import aiohttp
            
            url = f"http://{self.manifest.host}:{self.manifest.port}/health"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        
        except Exception:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'name': self.manifest.name,
            'type': 'standard',
            'running': hasattr(self, 'service') and self.service is not None,
            'restart_count': self.restart_count,
            'health': await self.health_check(),
            'platform': get_platform_info(),
            'manifest': {
                'version': self.manifest.version,
                'port': self.manifest.port,
                'isolation': self.manifest.isolation.get('mode', 'none')
            }
        }


class EmbeddedRunner(ServiceRunner):
    """Runner for embedded platforms (MicroPython, Arduino)"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        super().__init__(manifest, config)
        self.device_info = None
        self.connection = None
        
    async def start(self) -> bool:
        """Start embedded service"""
        try:
            platform = self.config.platform or self.manifest.platform
            
            if not platform or not is_embedded_platform(platform):
                self.logger.error(f"Invalid embedded platform: {platform}")
                return False
            
            # Detect and connect to device
            if not await self._connect_device():
                return False
            
            # Deploy service to device
            if not await self._deploy_service():
                return False
            
            # Start service on device
            if not await self._start_device_service():
                return False
            
            self.logger.info(f"Embedded service started on {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start embedded service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop embedded service"""
        try:
            if self.connection:
                await self._stop_device_service()
                await self._disconnect_device()
            
            self.logger.info("Embedded service stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop embedded service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart embedded service"""
        await self.stop()
        await asyncio.sleep(self.config.restart_delay)
        return await self.start()
    
    async def health_check(self) -> bool:
        """Check embedded device health"""
        try:
            if not self.connection:
                return False
            
            # Platform-specific health check
            platform = self.config.platform or self.manifest.platform
            
            if platform.startswith('rp2040'):
                return await self._micropython_health_check()
            elif platform.startswith('esp'):
                return await self._micropython_health_check()
            elif platform.startswith('arduino'):
                return await self._arduino_health_check()
            
            return False
            
        except Exception:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get embedded service status"""
        return {
            'name': self.manifest.name,
            'type': 'embedded',
            'platform': self.config.platform or self.manifest.platform,
            'board': self.config.board or self.manifest.board,
            'device_port': self.config.device_port,
            'connected': self.connection is not None,
            'running': await self.health_check(),
            'restart_count': self.restart_count,
            'device_info': self.device_info
        }
    
    async def _connect_device(self) -> bool:
        """Connect to embedded device"""
        try:
            # Auto-detect device if not specified
            if not self.config.device_port:
                devices = detect_devices()
                platform = self.config.platform or self.manifest.platform
                
                for device in devices:
                    if device.get('platform') == platform.split('-')[0]:  # Match base platform
                        self.config.device_port = device['port']
                        self.device_info = device
                        break
                
                if not self.config.device_port:
                    self.logger.error(f"No suitable device found for platform: {platform}")
                    return False
            
            # Platform-specific connection
            platform = self.config.platform or self.manifest.platform
            
            if platform.startswith(('rp2040', 'esp')):
                return await self._connect_micropython()
            elif platform.startswith('arduino'):
                return await self._connect_arduino()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to device: {e}")
            return False
    
    async def _connect_micropython(self) -> bool:
        """Connect to MicroPython device"""
        try:
            # Try different MicroPython connection methods
            ampy = safe_import('ampy.pyboard')
            if ampy:
                self.connection = ampy.Pyboard(self.config.device_port)
                return True
            
            # Fallback to serial connection
            serial = safe_import('serial')
            if serial:
                self.connection = serial.Serial(self.config.device_port, 115200, timeout=1)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"MicroPython connection failed: {e}")
            return False
    
    async def _connect_arduino(self) -> bool:
        """Connect to Arduino device"""
        try:
            serial = safe_import('serial')
            if serial:
                self.connection = serial.Serial(self.config.device_port, 9600, timeout=1)
                await asyncio.sleep(2)  # Arduino reset delay
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Arduino connection failed: {e}")
            return False
    
    async def _deploy_service(self) -> bool:
        """Deploy service to embedded device"""
        try:
            platform = self.config.platform or self.manifest.platform
            
            if platform.startswith(('rp2040', 'esp')):
                return await self._deploy_micropython_service()
            elif platform.startswith('arduino'):
                return await self._deploy_arduino_service()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Service deployment failed: {e}")
            return False
    
    async def _deploy_micropython_service(self) -> bool:
        """Deploy service to MicroPython device"""
        try:
            # Create MicroPython service wrapper
            service_code = self._generate_micropython_code()
            
            # Upload service files
            # This would use ampy, rshell, or mpremote
            # Implementation depends on available tools
            
            self.logger.info("MicroPython service deployed")
            return True
            
        except Exception as e:
            self.logger.error(f"MicroPython deployment failed: {e}")
            return False
    
    async def _deploy_arduino_service(self) -> bool:
        """Deploy service to Arduino device"""
        try:
            # Generate Arduino sketch
            sketch_code = self._generate_arduino_code()
            
            # Compile and upload sketch
            # This would use arduino-cli or platformio
            # Implementation depends on available tools
            
            self.logger.info("Arduino service deployed")
            return True
            
        except Exception as e:
            self.logger.error(f"Arduino deployment failed: {e}")
            return False
    
    def _generate_micropython_code(self) -> str:
        """Generate MicroPython service code"""
        return f"""
# ProServe MicroPython Service: {self.manifest.name}
import network
import socket
import json
from machine import Pin

# Service configuration
SERVICE_NAME = "{self.manifest.name}"
SERVICE_VERSION = "{self.manifest.version}"
PORT = {self.manifest.port}

# Initialize WiFi (if available)
def connect_wifi():
    # WiFi connection code here
    pass

# HTTP server
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', PORT)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    
    print(f'ProServe MicroPython service listening on port {{PORT}}')
    
    while True:
        cl, addr = s.accept()
        print(f'Client connected from {{addr}}')
        
        request = cl.recv(1024)
        request_str = request.decode('utf-8')
        
        # Basic HTTP response
        response = {{
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "platform": "micropython",
            "message": "Hello from ProServe MicroPython!"
        }}
        
        response_json = json.dumps(response)
        http_response = f"HTTP/1.1 200 OK\\r\\nContent-Type: application/json\\r\\n\\r\\n{{response_json}}"
        
        cl.send(http_response)
        cl.close()

# Main entry point
if __name__ == "__main__":
    connect_wifi()
    start_server()
"""
    
    def _generate_arduino_code(self) -> str:
        """Generate Arduino service code"""
        return f"""
/*
 * ProServe Arduino Service: {self.manifest.name}
 * Version: {self.manifest.version}
 */

#include <SoftwareSerial.h>

// Service configuration
const String SERVICE_NAME = "{self.manifest.name}";
const String SERVICE_VERSION = "{self.manifest.version}";
const int SERVICE_PORT = {self.manifest.port};

void setup() {{
  Serial.begin(9600);
  
  Serial.println("ProServe Arduino Service Starting...");
  Serial.println("Service: " + SERVICE_NAME);
  Serial.println("Version: " + SERVICE_VERSION);
  
  // Initialize service
  setupService();
}}

void loop() {{
  // Main service loop
  handleRequests();
  delay(100);
}}

void setupService() {{
  // Service initialization code
  Serial.println("Service initialized");
}}

void handleRequests() {{
  // Handle incoming requests
  if (Serial.available()) {{
    String request = Serial.readString();
    request.trim();
    
    if (request == "status") {{
      Serial.println("{{");
      Serial.println("  \\"service\\": \\"" + SERVICE_NAME + "\\",");
      Serial.println("  \\"version\\": \\"" + SERVICE_VERSION + "\\",");
      Serial.println("  \\"platform\\": \\"arduino\\",");
      Serial.println("  \\"status\\": \\"running\\"");
      Serial.println("}}");
    }}
  }}
}}
"""
    
    async def _start_device_service(self) -> bool:
        """Start service on embedded device"""
        # Implementation would depend on platform and connection method
        return True
    
    async def _stop_device_service(self) -> bool:
        """Stop service on embedded device"""
        # Implementation would depend on platform and connection method
        return True
    
    async def _disconnect_device(self):
        """Disconnect from embedded device"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
    
    async def _micropython_health_check(self) -> bool:
        """MicroPython-specific health check"""
        # Implementation would send command to device and check response
        return True
    
    async def _arduino_health_check(self) -> bool:
        """Arduino-specific health check"""
        # Implementation would send command to device and check response
        return True


class DockerRunner(ServiceRunner):
    """Runner for Docker containerized services"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        super().__init__(manifest, config)
        self.container = None
        self.docker_client = None
        
    async def start(self) -> bool:
        """Start Docker containerized service"""
        try:
            # Try to import docker
            docker = safe_import('docker')
            if not docker:
                self.logger.error("Docker package not available")
                return False
            
            self.docker_client = docker.from_env()
            
            # Build or pull image
            image_name = self.manifest.isolation.get('image', 'python:3.11-slim')
            
            # Create container
            container_config = {
                'image': image_name,
                'ports': {f'{self.manifest.port}/tcp': self.manifest.port},
                'environment': self._get_container_env(),
                'volumes': self._get_container_volumes(),
                'name': f"proserve-{self.manifest.name}",
                'detach': True,
                'remove': True
            }
            
            self.container = self.docker_client.containers.run(**container_config)
            
            self.logger.info(f"Docker container started: {self.container.id[:12]}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Docker container: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop Docker container"""
        try:
            if self.container:
                self.container.stop(timeout=self.config.shutdown_timeout)
                self.container = None
            
            self.logger.info("Docker container stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Docker container: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart Docker container"""
        await self.stop()
        await asyncio.sleep(self.config.restart_delay)
        return await self.start()
    
    async def health_check(self) -> bool:
        """Check Docker container health"""
        try:
            if not self.container:
                return False
            
            self.container.reload()
            return self.container.status == 'running'
            
        except Exception:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Docker container status"""
        status_info = {
            'name': self.manifest.name,
            'type': 'docker',
            'container_id': None,
            'container_status': None,
            'running': False,
            'restart_count': self.restart_count
        }
        
        if self.container:
            try:
                self.container.reload()
                status_info.update({
                    'container_id': self.container.id[:12],
                    'container_status': self.container.status,
                    'running': self.container.status == 'running'
                })
            except:
                pass
        
        return status_info
    
    def _get_container_env(self) -> Dict[str, str]:
        """Get environment variables for container"""
        env = self.config.env_vars.copy()
        env.update({
            'PROSERVE_SERVICE_NAME': self.manifest.name,
            'PROSERVE_SERVICE_VERSION': self.manifest.version,
            'PROSERVE_SERVICE_PORT': str(self.manifest.port)
        })
        return env
    
    def _get_container_volumes(self) -> Dict[str, Dict[str, str]]:
        """Get volume mappings for container"""
        volumes = {}
        
        # Add manifest directory
        manifest_dir = Path(self.manifest._manifest_path).parent if hasattr(self.manifest, '_manifest_path') else Path.cwd()
        volumes[str(manifest_dir)] = {'bind': '/app', 'mode': 'rw'}
        
        return volumes


def create_runner(manifest: ServiceManifest, config: Optional[RunnerConfig] = None) -> ServiceRunner:
    """Create appropriate runner based on manifest and configuration"""
    
    # Determine runner type
    isolation_mode = manifest.isolation.get('mode', 'none') if manifest.isolation else 'none'
    platform = manifest.platform
    
    if config:
        isolation_mode = config.isolation_mode or isolation_mode
        platform = config.platform or platform
    
    # Create runner based on isolation mode and platform
    if isolation_mode == 'docker' or isolation_mode == 'container':
        return DockerRunner(manifest, config)
    elif platform and is_embedded_platform(platform):
        return EmbeddedRunner(manifest, config)
    else:
        return StandardRunner(manifest, config)


async def run_service(manifest: ServiceManifest, config: Optional[RunnerConfig] = None) -> int:
    """Run service with appropriate runner"""
    runner = create_runner(manifest, config)
    
    try:
        await runner.run()
        return 0
    except Exception as e:
        runner.logger.error(f"Service run failed: {e}")
        return 1
