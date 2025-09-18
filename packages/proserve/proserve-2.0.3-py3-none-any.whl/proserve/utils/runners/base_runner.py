"""
ProServe Base Runner - Abstract Base Class for Service Runners
Defines the common interface and functionality for all service runners
"""

import asyncio
import signal
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog

from ...core.manifest import ServiceManifest
from .runner_config import RunnerConfig


class ServiceRunner(ABC):
    """Abstract base class for service runners"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        self.manifest = manifest
        self.config = config or RunnerConfig()
        self.logger = structlog.get_logger(f"runner-{self.manifest.name}")
        
        # Runtime state
        self.is_running = False
        self.process = None
        self.restart_count = 0
        self.start_time = None
        self.last_health_check = None
        
        # Monitoring
        self.health_check_failures = 0
        self.max_health_failures = 3
        
        # Signal handling
        self._shutdown_requested = False
        
    @abstractmethod
    async def start(self) -> bool:
        """Start the service"""
        pass
        
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the service"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
        
    async def restart(self) -> bool:
        """Restart the service"""
        self.logger.info("Restarting service...")
        
        # Stop first
        stop_success = await self.stop()
        if not stop_success:
            self.logger.warning("Service stop failed during restart")
        
        # Wait before restart
        if self.config.restart_delay > 0:
            self.logger.info(f"Waiting {self.config.restart_delay}s before restart...")
            await asyncio.sleep(self.config.restart_delay)
        
        # Start again
        start_success = await self.start()
        
        if start_success:
            self.restart_count += 1
            self.logger.info(f"Service restarted successfully (restart #{self.restart_count})")
        else:
            self.logger.error("Service restart failed")
        
        return start_success
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            'name': self.manifest.name,
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'restart_count': self.restart_count,
            'last_health_check': self.last_health_check,
            'health_failures': self.health_check_failures,
            'platform': getattr(self.config, 'platform', 'unknown'),
            'pid': getattr(self.process, 'pid', None) if self.process else None
        }
    
    async def run(self) -> None:
        """Run service with monitoring and auto-restart"""
        self.logger.info(f"Starting service runner for {self.manifest.name}")
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        try:
            # Initial start
            if not await self.start():
                self.logger.error("Failed to start service initially")
                return
            
            # Start monitoring loop
            if self.config.enable_monitoring:
                await self._monitoring_loop()
            else:
                # Just wait for shutdown signal
                while not self._shutdown_requested:
                    await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Service runner error: {e}")
        finally:
            # Ensure service is stopped
            await self.stop()
            self.logger.info("Service runner stopped")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            self.logger.info(f"Received signal {sig}, initiating graceful shutdown...")
            self._shutdown_requested = True
        
        # Register signal handlers
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            if hasattr(signal, 'SIGHUP'):
                signal.signal(signal.SIGHUP, signal_handler)
        except ValueError:
            # Running in a thread where signals aren't supported
            self.logger.warning("Signal handlers not available in this context")
    
    async def _monitoring_loop(self):
        """Main monitoring loop with health checks and auto-restart"""
        self.logger.info("Starting monitoring loop...")
        
        while not self._shutdown_requested:
            try:
                # Perform health check
                if self.config.health_check_interval > 0:
                    health_result = await self.health_check()
                    self.last_health_check = time.time()
                    
                    if health_result.get('healthy', False):
                        self.health_check_failures = 0
                        self.logger.debug("Health check passed")
                    else:
                        self.health_check_failures += 1
                        self.logger.warning(
                            f"Health check failed ({self.health_check_failures}/{self.max_health_failures}): "
                            f"{health_result.get('error', 'Unknown error')}"
                        )
                        
                        # Auto-restart if too many failures
                        if (self.health_check_failures >= self.max_health_failures and 
                            self.config.auto_restart and 
                            self.restart_count < self.config.max_restarts):
                            
                            self.logger.warning("Too many health check failures, attempting restart...")
                            await self.restart()
                            self.health_check_failures = 0
                
                # Check if service process is still running
                if not self.is_running and self.config.auto_restart and self.restart_count < self.config.max_restarts:
                    self.logger.warning("Service not running, attempting restart...")
                    await self.restart()
                
                # Sleep until next check
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        self.logger.info("Monitoring loop stopped")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        status = self.get_status()
        
        metrics = {
            'uptime_seconds': status['uptime_seconds'],
            'restart_count': status['restart_count'],
            'health_failures': status['health_failures'],
            'memory_usage': None,
            'cpu_usage': None
        }
        
        # Try to get process metrics if available
        if self.process and hasattr(self.process, 'pid'):
            try:
                import psutil
                proc = psutil.Process(self.process.pid)
                
                metrics.update({
                    'memory_usage': proc.memory_info().rss / 1024 / 1024,  # MB
                    'cpu_usage': proc.cpu_percent(),
                    'num_threads': proc.num_threads(),
                    'num_fds': proc.num_fds() if hasattr(proc, 'num_fds') else None
                })
            except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return metrics
    
    async def send_signal(self, signal_name: str) -> bool:
        """Send signal to the service process"""
        if not self.process:
            self.logger.warning("No process to send signal to")
            return False
        
        try:
            if signal_name.upper() == 'TERM':
                self.process.terminate()
            elif signal_name.upper() == 'KILL':
                self.process.kill()
            elif signal_name.upper() == 'INT':
                self.process.send_signal(signal.SIGINT)
            else:
                self.logger.error(f"Unknown signal: {signal_name}")
                return False
            
            self.logger.info(f"Sent {signal_name} signal to process {self.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send {signal_name} signal: {e}")
            return False
    
    async def wait_for_shutdown(self, timeout: float = None) -> bool:
        """Wait for service to shutdown gracefully"""
        if not self.process:
            return True
        
        timeout = timeout or self.config.shutdown_timeout
        
        try:
            await asyncio.wait_for(self.process.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self.logger.warning(f"Service did not shutdown within {timeout}s")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.is_running:
            asyncio.create_task(self.stop())


class HealthChecker:
    """Utility class for performing various types of health checks"""
    
    @staticmethod
    async def http_health_check(url: str, timeout: float = 5.0) -> Dict[str, Any]:
        """Perform HTTP health check"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    return {
                        'healthy': response.status == 200,
                        'status_code': response.status,
                        'response_time': None  # Could be measured
                    }
                    
        except ImportError:
            return {'healthy': False, 'error': 'aiohttp not available'}
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    @staticmethod
    async def tcp_health_check(host: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Perform TCP connection health check"""
        try:
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)
            
            writer.close()
            await writer.wait_closed()
            
            return {'healthy': True, 'host': host, 'port': port}
            
        except Exception as e:
            return {'healthy': False, 'error': str(e), 'host': host, 'port': port}
    
    @staticmethod
    def process_health_check(process) -> Dict[str, Any]:
        """Check if process is still running and responsive"""
        if not process:
            return {'healthy': False, 'error': 'No process'}
        
        try:
            # Check if process is still running
            if process.poll() is not None:
                return {'healthy': False, 'error': f'Process exited with code {process.returncode}'}
            
            return {'healthy': True, 'pid': process.pid}
            
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
