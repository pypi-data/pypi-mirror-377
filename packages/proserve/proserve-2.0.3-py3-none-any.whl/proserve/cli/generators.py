"""
ProServe Code Generators
Modular code generation for different platforms and service types

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from ..core.manifest import ServiceManifest


class CodeGeneratorManager:
    """Manages all code generation operations"""
    
    def __init__(self):
        self.console = Console()
        
    async def generate_code(self, manifest: ServiceManifest, output_dir: str, platform: Optional[str] = None) -> bool:
        """Generate code based on manifest and platform"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Determine platform from manifest if not specified
            if not platform:
                platform = getattr(manifest, 'platform', 'standard')
            
            if platform in ['rp2040', 'raspberry_pi', 'micropython']:
                return await self._generate_micropython(manifest, output_path)
            elif platform == 'docker':
                return await self._generate_docker_app(manifest, output_path)
            else:
                return await self._generate_standard_app(manifest, output_path)
                
        except Exception as e:
            self.console.print(f"❌ Code generation failed: {e}", style="red")
            return False
    
    async def _generate_micropython(self, manifest: ServiceManifest, output_path: Path) -> bool:
        """Generate MicroPython application"""
        try:
            self.console.print("🔌 Generating MicroPython application...")
            
            # Generate main.py
            main_py = self._create_micropython_main(manifest)
            with open(output_path / "main.py", 'w') as f:
                f.write(main_py)
            
            # Generate config.py
            config_py = self._create_micropython_config(manifest)
            with open(output_path / "config.py", 'w') as f:
                f.write(config_py)
            
            # Generate handler.py
            handler_py = self._create_micropython_handler(manifest)
            with open(output_path / "handler.py", 'w') as f:
                f.write(handler_py)
            
            # Generate boot.py
            boot_py = self._create_micropython_boot(manifest)
            with open(output_path / "boot.py", 'w') as f:
                f.write(boot_py)
            
            # Generate deployment script
            deploy_script = self._create_micropython_deploy_script(manifest)
            with open(output_path / "deploy.sh", 'w') as f:
                f.write(deploy_script)
            
            # Make deploy script executable
            os.chmod(output_path / "deploy.sh", 0o755)
            
            # Generate README
            readme = self._create_micropython_readme(manifest)
            with open(output_path / "README.md", 'w') as f:
                f.write(readme)
            
            self.console.print("✅ MicroPython application generated successfully!")
            return True
            
        except Exception as e:
            self.console.print(f"❌ MicroPython generation failed: {e}", style="red")
            return False
    
    async def _generate_standard_app(self, manifest: ServiceManifest, output_path: Path) -> bool:
        """Generate standard Python application"""
        try:
            self.console.print("🐍 Generating standard Python application...")
            
            # Generate main application file
            if manifest.type == 'static':
                app_code = self._create_static_app(manifest)
                with open(output_path / "app.py", 'w') as f:
                    f.write(app_code)
                
                # Generate index.html for static sites
                index_html = self._create_static_html(manifest)
                static_dir = output_path / "static"
                static_dir.mkdir(exist_ok=True)
                with open(static_dir / "index.html", 'w') as f:
                    f.write(index_html)
            else:
                app_code = self._create_http_service(manifest)
                with open(output_path / "app.py", 'w') as f:
                    f.write(app_code)
            
            # Generate TLS certificate script if TLS enabled
            if getattr(manifest, 'enable_tls', False):
                tls_script = self._create_tls_cert_script(manifest)
                with open(output_path / "generate_certs.sh", 'w') as f:
                    f.write(tls_script)
                os.chmod(output_path / "generate_certs.sh", 0o755)
            
            # Generate requirements.txt
            requirements = self._create_requirements_txt(manifest)
            with open(output_path / "requirements.txt", 'w') as f:
                f.write(requirements)
            
            # Generate README
            readme = self._create_standard_readme(manifest)
            with open(output_path / "README.md", 'w') as f:
                f.write(readme)
            
            self.console.print("✅ Standard application generated successfully!")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Standard app generation failed: {e}", style="red")
            return False
    
    async def generate_docker(self, manifest: ServiceManifest, output_dir: str, base_image: Optional[str] = None) -> bool:
        """Generate Docker configuration"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.console.print("🐳 Generating Docker configuration...")
            
            # Generate Dockerfile
            dockerfile = self._create_dockerfile(manifest, base_image)
            with open(output_path / "Dockerfile", 'w') as f:
                f.write(dockerfile)
            
            # Generate docker-compose.yml
            docker_compose = self._create_docker_compose(manifest)
            with open(output_path / "docker-compose.yml", 'w') as f:
                f.write(docker_compose)
            
            # Generate .dockerignore
            dockerignore = self._create_dockerignore()
            with open(output_path / ".dockerignore", 'w') as f:
                f.write(dockerignore)
            
            self.console.print("✅ Docker configuration generated successfully!")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Docker generation failed: {e}", style="red")
            return False
    
    def _create_micropython_main(self, manifest: ServiceManifest) -> str:
        """Create main MicroPython application file"""
        return f'''#!/usr/bin/env micropython
"""
{manifest.name} - MicroPython Application
Generated by ProServe v2.0.0

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import gc
import time
import ujson
from machine import Pin, reset
from config import CONFIG
from handler import handle_request

# Initialize hardware
def init_hardware():
    """Initialize GPIO pins and I2C devices"""
    print("🔌 Initializing hardware...")
    
    # GPIO pins setup
    pins = CONFIG.get('pins', {{}})
    for pin_name, pin_num in pins.items():
        globals()[f"{pin_name.upper()}_PIN"] = Pin(pin_num, Pin.OUT)
        print(f"  ✅ {pin_name}: GPIO {pin_num}")
    
    print("✅ Hardware initialized")

# Main application
def main():
    """Main application entry point"""
    try:
        print("🚀 Starting {manifest.name} v{manifest.version or '1.0.0'}")
        print(f"📟 Platform: {getattr(manifest, 'platform', 'rp2040')}")
        print(f"🏷️  Board: {getattr(manifest, 'board', 'raspberry_pi_pico')}")
        
        # Initialize hardware
        init_hardware()
        
        # Connect to WiFi if configured
        if CONFIG.get('wifi_enabled', False):
            from network import WLAN, STA_IF
            
            wlan = WLAN(STA_IF)
            wlan.active(True)
            
            if not wlan.isconnected():
                print(f"📡 Connecting to WiFi: {CONFIG['wifi_ssid']}")
                wlan.connect(CONFIG['wifi_ssid'], CONFIG['wifi_password'])
                
                # Wait for connection
                timeout = 10
                while not wlan.isconnected() and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                
                if wlan.isconnected():
                    print(f"✅ Connected! IP: {wlan.ifconfig()[0]}")
                else:
                    print("❌ WiFi connection failed")
        
        # Main service loop
        print(f"🌐 Service running on port {CONFIG['port']}")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Simple HTTP-like request handling simulation
                # In real implementation, this would use socket server
                
                # Simulate request processing
                time.sleep(1)
                
                # Memory management
                if gc.mem_free() < 1000:
                    gc.collect()
                
            except KeyboardInterrupt:
                print("\\n🛑 Service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(5)  # Wait before retry
    
    except Exception as e:
        print(f"💥 Critical error: {e}")
        print("🔄 Restarting in 10 seconds...")
        time.sleep(10)
        reset()

if __name__ == "__main__":
    main()
'''
    
    def _create_micropython_config(self, manifest: ServiceManifest) -> str:
        """Create MicroPython configuration file"""
        device_config = getattr(manifest, 'device_config', {})
        wifi_config = getattr(manifest, 'wifi_config', {})
        
        # Convert boolean values properly for MicroPython
        wifi_enabled = 'true' if wifi_config else 'false'
        auto_connect = 'true' if wifi_config.get('auto_connect', True) else 'false'
        monitoring_enabled = 'true' if getattr(manifest, 'monitoring', {}).get('enabled', False) else 'false'
        
        return f'''#!/usr/bin/env micropython
"""
Configuration for {manifest.name}
Generated by ProServe v2.0.0
"""

# Service configuration
CONFIG = {{
    'name': "{manifest.name}",
    'version': "{manifest.version or '1.0.0'}",
    'platform': "{getattr(manifest, 'platform', 'rp2040')}",
    'board': "{getattr(manifest, 'board', 'raspberry_pi_pico')}",
    'host': "{manifest.host or '0.0.0.0'}",
    'port': {manifest.port or 8080},
    
    # Hardware configuration
    'pins': {device_config.get('pins', {})},
    'i2c_devices': {device_config.get('i2c_devices', [])},
    
    # WiFi configuration
    'wifi_enabled': {wifi_enabled},
    'wifi_ssid': "{wifi_config.get('ssid', 'YOUR_WIFI_SSID')}",
    'wifi_password': "{wifi_config.get('password', 'YOUR_WIFI_PASSWORD')}",
    'auto_connect': {auto_connect},
    
    # Monitoring
    'monitoring_enabled': {monitoring_enabled},
    'metrics_interval': {getattr(manifest, 'monitoring', {}).get('interval', 30)},
}}

# Device-specific constants
if CONFIG['platform'] == 'rp2040':
    FLASH_SIZE = "2MB"
    RAM_SIZE = "264KB"
    CPU_FREQ = 125_000_000  # 125MHz
elif CONFIG['platform'] == 'raspberry_pi':
    FLASH_SIZE = "32GB+"
    RAM_SIZE = "1GB+"
    CPU_FREQ = 1_500_000_000  # 1.5GHz
else:
    FLASH_SIZE = "Unknown"
    RAM_SIZE = "Unknown"
    CPU_FREQ = 0

print(f"📋 Configuration loaded for {CONFIG['name']} v{CONFIG['version']}")
'''
    
    def _create_requirements_txt(self, manifest: ServiceManifest) -> str:
        """Create requirements.txt file"""
        return '''# ProServe Application Dependencies
# Generated by ProServe v2.0.0

proserve>=2.0.0
aiohttp>=3.8.0
aiohttp-cors>=0.8.0
pyyaml>=6.0.0
rich>=13.0.0
python-dotenv>=1.0.0
'''

    def _create_standard_readme(self, manifest: ServiceManifest) -> str:
        """Create README for standard application"""
        return f'''# {manifest.name}

{getattr(manifest, 'description', f'ProServe {manifest.type} service')}

## Generated by ProServe v2.0.0

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

### Configuration

- **Name**: {manifest.name}
- **Version**: {manifest.version or '1.0.0'}
- **Type**: {manifest.type}
- **Host**: {manifest.host or '0.0.0.0'}
- **Port**: {manifest.port or 8080}

### Author

Tom Sapletta <info@softreck.dev>

### License

Apache 2.0
'''

    def _create_dockerfile(self, manifest: ServiceManifest, base_image: Optional[str] = None) -> str:
        """Create Dockerfile"""
        base = base_image or "python:3.11-slim"
        
        return f'''# {manifest.name} - Generated by ProServe v2.0.0
FROM {base}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE {manifest.port or 8080}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{manifest.port or 8080}/health || exit 1

# Run application
CMD ["python", "app.py"]
'''

    def _create_docker_compose(self, manifest: ServiceManifest) -> str:
        """Create docker-compose.yml"""
        return f'''# {manifest.name} - Generated by ProServe v2.0.0
version: '3.8'

services:
  {manifest.name.lower().replace('_', '-')}:
    build: .
    ports:
      - "{manifest.port or 8080}:{manifest.port or 8080}"
    environment:
      - ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{manifest.port or 8080}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
'''

    def _create_dockerignore(self) -> str:
        """Create .dockerignore file"""
        return '''# Generated by ProServe v2.0.0
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

.DS_Store
.vscode
.idea
*.swp
*.swo

node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*

build/
dist/
*.egg-info/
'''
