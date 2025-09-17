"""
ProServe Embedded Runner - Embedded Device Service Runner
Handles running services on embedded platforms like MicroPython and Arduino devices
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional

from .base_runner import ServiceRunner, HealthChecker
from .runner_config import EmbeddedRunnerConfig, RunnerConfig
from ...core.manifest import ServiceManifest
from ...isolation.platforms import (
    MicroPythonIsolationManager, ArduinoIsolationManager,
    detect_connected_devices, auto_select_isolation_manager
)


class EmbeddedRunner(ServiceRunner):
    """Runner for embedded platforms (MicroPython, Arduino)"""
    
    def __init__(self, manifest: ServiceManifest, config: Optional[RunnerConfig] = None):
        if config is None:
            config = EmbeddedRunnerConfig()
        elif not isinstance(config, EmbeddedRunnerConfig):
            # Convert generic config to EmbeddedRunnerConfig
            config = EmbeddedRunnerConfig(**config.to_dict())
        
        super().__init__(manifest, config)
        self.config: EmbeddedRunnerConfig = config
        
        # Embedded-specific attributes
        self.device_info = None
        self.connection = None
        self.isolation_manager = None
        self.deployed_code = None
        
    async def start(self) -> bool:
        """Start embedded service"""
        if self.is_running:
            self.logger.warning("Embedded service is already running")
            return True
        
        self.logger.info(f"Starting embedded service: {self.manifest.name}")
        
        try:
            # Connect to embedded device
            if not await self._connect_device():
                self.logger.error("Failed to connect to embedded device")
                return False
            
            # Deploy service to device
            if not await self._deploy_service():
                self.logger.error("Failed to deploy service to device")
                return False
            
            # Start service on device
            if not await self._start_device_service():
                self.logger.error("Failed to start service on device")
                return False
            
            self.is_running = True
            self.start_time = time.time()
            self.logger.info(f"Embedded service started successfully on {self.config.platform}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start embedded service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop embedded service"""
        if not self.is_running:
            self.logger.info("Embedded service is not running")
            return True
        
        self.logger.info("Stopping embedded service...")
        
        try:
            # Stop service on device
            await self._stop_device_service()
            
            # Disconnect from device
            await self._disconnect_device()
            
            self.is_running = False
            self.logger.info("Embedded service stopped successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop embedded service: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check embedded device health"""
        if not self.isolation_manager:
            return {'healthy': False, 'error': 'No isolation manager'}
        
        # Check device connection
        if not self.connection:
            return {'healthy': False, 'error': 'Device not connected'}
        
        try:
            # Platform-specific health check
            if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                return await self._micropython_health_check()
            elif isinstance(self.isolation_manager, ArduinoIsolationManager):
                return await self._arduino_health_check()
            else:
                return {'healthy': False, 'error': 'Unknown platform'}
                
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get embedded service status"""
        status = super().get_status()
        status.update({
            'device_connected': self.connection is not None,
            'device_info': self.device_info,
            'device_port': self.config.device_port,
            'baud_rate': self.config.baud_rate,
            'firmware_version': self.config.firmware_version,
            'deployed': self.deployed_code is not None
        })
        
        return status
    
    async def _connect_device(self) -> bool:
        """Connect to embedded device"""
        self.logger.info(f"Connecting to {self.config.platform} device...")
        
        try:
            # Auto-detect device if not specified
            if self.config.auto_detect_device and not self.config.device_port:
                devices = detect_connected_devices()
                matching_devices = [d for d in devices if d.platform == self.config.platform]
                
                if matching_devices:
                    device = matching_devices[0]
                    self.config.device_port = device.port
                    self.device_info = device.to_dict()
                    self.logger.info(f"Auto-detected device: {device.description} on {device.port}")
                else:
                    self.logger.warning("No matching devices found, using emulation mode")
                    return await self._setup_emulation_mode()
            
            # Create appropriate isolation manager
            if self.config.platform in ['rp2040', 'esp32', 'esp8266', 'pyboard']:
                self.isolation_manager = MicroPythonIsolationManager(
                    platform=self.config.platform,
                    device_port=self.config.device_port,
                    baud_rate=self.config.baud_rate,
                    timeout=self.config.timeout,
                    auto_detect_device=False  # Already detected
                )
            elif self.config.platform in ['uno_r4_wifi', 'esp32dev', 'nano33iot', 'leonardo']:
                self.isolation_manager = ArduinoIsolationManager(
                    platform=self.config.platform,
                    upload_port=self.config.device_port,
                    compile_only=False
                )
            else:
                raise ValueError(f"Unsupported platform: {self.config.platform}")
            
            # Setup isolation environment
            await self.isolation_manager.setup_environment()
            
            self.connection = True  # Simplified connection tracking
            return True
            
        except Exception as e:
            self.logger.error(f"Device connection failed: {e}")
            return False
    
    async def _setup_emulation_mode(self) -> bool:
        """Setup emulation mode when no physical device is available"""
        self.logger.info("Setting up emulation mode...")
        
        try:
            # Use MicroPython emulation by default
            self.isolation_manager = MicroPythonIsolationManager(
                platform=self.config.platform or 'rp2040',
                use_emulator=True
            )
            
            await self.isolation_manager.setup_environment()
            
            self.connection = True
            self.device_info = {
                'mode': 'emulation',
                'platform': self.config.platform,
                'emulated': True
            }
            
            self.logger.info("Emulation mode setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Emulation setup failed: {e}")
            return False
    
    async def _deploy_service(self) -> bool:
        """Deploy service to embedded device"""
        self.logger.info("Deploying service to device...")
        
        try:
            # Generate platform-specific code
            if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                service_code = await self._generate_micropython_code()
            elif isinstance(self.isolation_manager, ArduinoIsolationManager):
                service_code = await self._generate_arduino_code()
            else:
                raise ValueError("Unknown isolation manager type")
            
            # Deploy code to device
            result = await self.isolation_manager.execute_script(service_code)
            
            if result.get('success', False):
                self.deployed_code = service_code
                self.logger.info("Service deployed successfully")
                return True
            else:
                self.logger.error(f"Service deployment failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Service deployment error: {e}")
            return False
    
    async def _generate_micropython_code(self) -> str:
        """Generate MicroPython service code from manifest"""
        lines = []
        
        # Header
        lines.extend([
            "# ProServe MicroPython Service",
            f"# Service: {self.manifest.name}",
            f"# Platform: {self.config.platform}",
            "",
            "import machine",
            "import time",
            "import gc",
            ""
        ])
        
        # Service configuration
        lines.extend([
            "# Service configuration",
            f"SERVICE_NAME = '{self.manifest.name}'",
            f"PLATFORM = '{self.config.platform}'",
            ""
        ])
        
        # Main service loop
        lines.extend([
            "def main():",
            "    print(f'Starting ProServe service: {SERVICE_NAME}')",
            "    print(f'Platform: {PLATFORM}')",
            "    ",
            "    # Service initialization",
            "    led = None",
            "    try:",
            "        led = machine.Pin('LED', machine.Pin.OUT)",
            "    except:",
            "        pass  # No LED available",
            "    ",
            "    # Main service loop", 
            "    while True:",
            "        try:",
            "            # Service heartbeat",
            "            if led:",
            "                led.toggle()",
            "            ",
            "            # Service logic would go here",
            "            print(f'{SERVICE_NAME}: Running...')",
            "            ",
            "            # Garbage collection",
            "            gc.collect()",
            "            ",
            "            time.sleep(1)",
            "        except KeyboardInterrupt:",
            "            print('Service stopped')",
            "            break",
            "        except Exception as e:",
            "            print(f'Service error: {e}')",
            "            time.sleep(5)  # Wait before retry",
            "",
            "if __name__ == '__main__':",
            "    main()"
        ])
        
        return '\n'.join(lines)
    
    async def _generate_arduino_code(self) -> str:
        """Generate Arduino service code from manifest"""
        lines = []
        
        # Header
        lines.extend([
            "/*",
            " * ProServe Arduino Service",
            f" * Service: {self.manifest.name}",
            f" * Platform: {self.config.platform}",
            " */",
            "",
            "#include <Arduino.h>",
            ""
        ])
        
        # Service configuration
        lines.extend([
            "// Service configuration",
            f"const char* SERVICE_NAME = \"{self.manifest.name}\";",
            f"const char* PLATFORM = \"{self.config.platform}\";",
            "",
            "// Global variables",
            "unsigned long lastHeartbeat = 0;",
            "const unsigned long HEARTBEAT_INTERVAL = 1000;  // 1 second",
            ""
        ])
        
        # Setup function
        lines.extend([
            "void setup() {",
            "  Serial.begin(115200);",
            "  while (!Serial) {",
            "    delay(10);",
            "  }",
            "  ",
            "  Serial.println(\"ProServe Arduino Service Starting...\");",
            "  Serial.print(\"Service: \");",
            "  Serial.println(SERVICE_NAME);",
            "  Serial.print(\"Platform: \");",
            "  Serial.println(PLATFORM);",
            "  ",
            "  // Initialize LED if available",
            "  #ifdef LED_BUILTIN",
            "  pinMode(LED_BUILTIN, OUTPUT);",
            "  #endif",
            "  ",
            "  Serial.println(\"Service initialized successfully!\");",
            "}",
            ""
        ])
        
        # Loop function
        lines.extend([
            "void loop() {",
            "  unsigned long currentTime = millis();",
            "  ",
            "  // Service heartbeat",
            "  if (currentTime - lastHeartbeat >= HEARTBEAT_INTERVAL) {",
            "    Serial.print(SERVICE_NAME);",
            "    Serial.println(\": Running...\");",
            "    ",
            "    #ifdef LED_BUILTIN",
            "    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));",
            "    #endif",
            "    ",
            "    lastHeartbeat = currentTime;",
            "  }",
            "  ",
            "  // Service logic would go here",
            "  ",
            "  delay(100);  // Small delay to prevent overwhelming",
            "}"
        ])
        
        return '\n'.join(lines)
    
    async def _start_device_service(self) -> bool:
        """Start service on embedded device"""
        self.logger.info("Starting service on device...")
        
        # For embedded devices, the service starts automatically when code is deployed
        # This is a placeholder for any additional startup logic
        return True
    
    async def _stop_device_service(self) -> bool:
        """Stop service on embedded device"""
        self.logger.info("Stopping service on device...")
        
        try:
            if self.isolation_manager:
                # Send interrupt signal to stop the service
                if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                    # Try to send Ctrl+C to stop the script
                    pass  # Implementation would depend on the isolation manager
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop device service: {e}")
            return False
    
    async def _disconnect_device(self) -> bool:
        """Disconnect from embedded device"""
        self.logger.info("Disconnecting from device...")
        
        try:
            if self.isolation_manager:
                await self.isolation_manager.cleanup_environment()
                
            self.connection = None
            self.isolation_manager = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Device disconnection error: {e}")
            return False
    
    async def _micropython_health_check(self) -> Dict[str, Any]:
        """MicroPython-specific health check"""
        try:
            # Simple ping test
            test_code = "print('ProServe-Health-Check')"
            result = await self.isolation_manager.execute_script(test_code)
            
            if result.get('success', False):
                return {
                    'healthy': True,
                    'platform': 'micropython',
                    'response_time': result.get('execution_time', 0)
                }
            else:
                return {
                    'healthy': False,
                    'error': result.get('error', 'Health check failed'),
                    'platform': 'micropython'
                }
                
        except Exception as e:
            return {'healthy': False, 'error': str(e), 'platform': 'micropython'}
    
    async def _arduino_health_check(self) -> Dict[str, Any]:
        """Arduino-specific health check"""
        try:
            # For Arduino, we mainly check if we can compile code
            test_code = """
            void setup() { 
                Serial.begin(9600); 
            }
            void loop() { 
                Serial.println("ProServe-Health-Check"); 
                delay(1000); 
            }
            """
            
            result = await self.isolation_manager.execute_script(test_code)
            
            if result.get('success', False):
                compilation = result.get('compilation', {})
                return {
                    'healthy': True,
                    'platform': 'arduino',
                    'compilation_success': compilation.get('success', False),
                    'sketch_size': compilation.get('sketch_size', {})
                }
            else:
                return {
                    'healthy': False,
                    'error': result.get('error', 'Health check failed'),
                    'platform': 'arduino'
                }
                
        except Exception as e:
            return {'healthy': False, 'error': str(e), 'platform': 'arduino'}
    
    async def deploy_update(self, new_code: str) -> bool:
        """Deploy code update to device"""
        self.logger.info("Deploying code update to device...")
        
        try:
            result = await self.isolation_manager.execute_script(new_code)
            
            if result.get('success', False):
                self.deployed_code = new_code
                self.logger.info("Code update deployed successfully")
                return True
            else:
                self.logger.error(f"Code update failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Code update error: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get detailed device information"""
        if not self.isolation_manager:
            return {'error': 'No device connected'}
        
        try:
            # Get platform-specific device info
            if isinstance(self.isolation_manager, MicroPythonIsolationManager):
                info_code = """
import sys
import gc
import machine
try:
    result = {
        'platform': sys.platform,
        'version': sys.version,
        'memory_free': gc.mem_free(),
        'memory_alloc': gc.mem_alloc()
    }
    print('DEVICE_INFO:', result)
except Exception as e:
    print('DEVICE_INFO_ERROR:', str(e))
"""
                result = await self.isolation_manager.execute_script(info_code)
                return result
            
            elif isinstance(self.isolation_manager, ArduinoIsolationManager):
                # Arduino device info is mainly from compilation
                return {
                    'platform': self.config.platform,
                    'board_fqbn': getattr(self.isolation_manager, 'board_fqbn', 'unknown'),
                    'compilation_tools': 'arduino-cli'
                }
                
        except Exception as e:
            return {'error': str(e)}


# Utility functions for embedded runners
def detect_platform_from_device(device_port: str) -> str:
    """Detect platform type from connected device"""
    devices = detect_connected_devices()
    
    for device in devices:
        if device.port == device_port:
            return device.platform
    
    return 'unknown'


def optimize_code_for_platform(code: str, platform: str) -> str:
    """Optimize code for specific embedded platform"""
    if platform in ['esp8266']:
        # Very memory-constrained, aggressive optimization
        lines = code.split('\n')
        optimized = []
        
        for line in lines:
            # Remove comments and extra whitespace
            line = line.strip()
            if line and not line.startswith('#'):
                optimized.append(line)
        
        return '\n'.join(optimized)
    
    elif platform in ['rp2040', 'esp32']:
        # Moderate optimization
        return code.replace('    ', '  ')  # Reduce indentation
    
    else:
        # No optimization needed
        return code
