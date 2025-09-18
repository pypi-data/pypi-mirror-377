"""
ProServe CLI Commands
Modular command implementations for ProServe CLI

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from ..core.manifest import ServiceManifest
from ..core.service import ProServeService
from ..utils.config import ProServeConfig
from .generators import CodeGeneratorManager


class ProServeCommandManager:
    """Manages all ProServe CLI commands"""
    
    def __init__(self):
        self.console = Console()
        self.config = ProServeConfig()
        self.generator_manager = CodeGeneratorManager()
        
    async def run_service(self, args):
        """Run ProServe service"""
        try:
            if args.manifest:
                # Load from manifest
                manifest_path = Path(args.manifest)
                if not manifest_path.exists():
                    self.console.print(f"❌ Manifest file not found: {args.manifest}", style="red")
                    return
                
                with open(manifest_path, 'r') as f:
                    manifest_data = yaml.safe_load(f)
                
                manifest = ServiceManifest(**manifest_data)
                service = ProServeService(manifest)
            else:
                # Create basic service
                service = ProServeService(
                    name="proserve-service",
                    host=args.host,
                    port=args.port
                )
            
            self.console.print(f"🚀 Starting {service.name} on {args.host}:{args.port}")
            
            # Configure SSL if provided
            if args.ssl_cert and args.ssl_key:
                service.configure_ssl(args.ssl_cert, args.ssl_key)
                self.console.print("🔒 SSL enabled")
            
            # Run service
            await service.start()
            
        except Exception as e:
            self.console.print(f"❌ Failed to start service: {e}", style="red")
    
    async def build_service(self, args):
        """Build application from manifest"""
        try:
            self.console.print(f"🔨 Building application from manifest: {args.manifest}")
            
            # Clean output directory if requested
            if args.clean and Path(args.output).exists():
                import shutil
                shutil.rmtree(args.output)
                self.console.print(f"🧹 Cleaned output directory: {args.output}")
            
            # Load manifest
            manifest_path = Path(args.manifest)
            with open(manifest_path, 'r') as f:
                manifest_data = yaml.safe_load(f)
            
            manifest = ServiceManifest(**manifest_data)
            
            # Generate code based on platform
            success = await self.generator_manager.generate_code(
                manifest, 
                args.output, 
                args.platform
            )
            
            if success:
                self.console.print(f"✅ Build completed successfully! Output: {args.output}")
            else:
                self.console.print("❌ Build failed!", style="red")
                
        except Exception as e:
            self.console.print(f"❌ Failed to build service: {e}", style="red")
    
    async def deploy_service(self, args):
        """Deploy ProServe service"""
        self.console.print("🚀 Deployment feature coming soon!", style="yellow")
    
    async def list_services(self, args):
        """List running ProServe services"""
        self.console.print("📋 Service listing feature coming soon!", style="yellow")
    
    async def service_status(self, args):
        """Check service status"""
        self.console.print("📊 Service status feature coming soon!", style="yellow")
    
    async def stop_service(self, args):
        """Stop ProServe service"""
        self.console.print("🛑 Service stop feature coming soon!", style="yellow")
    
    async def restart_service(self, args):
        """Restart ProServe service"""
        self.console.print("🔄 Service restart feature coming soon!", style="yellow")
    
    async def show_logs(self, args):
        """Show service logs"""
        self.console.print("📝 Logs feature coming soon!", style="yellow")
    
    async def generate_docker(self, args):
        """Generate Docker configuration"""
        try:
            manifest_path = Path(args.manifest)
            with open(manifest_path, 'r') as f:
                manifest_data = yaml.safe_load(f)
            
            manifest = ServiceManifest(**manifest_data)
            
            success = await self.generator_manager.generate_docker(
                manifest, 
                args.output,
                args.base_image
            )
            
            if success:
                self.console.print(f"✅ Docker configuration generated: {args.output}")
            else:
                self.console.print("❌ Docker generation failed!", style="red")
                
        except Exception as e:
            self.console.print(f"❌ Failed to generate Docker config: {e}", style="red")
    
    async def generate_k8s(self, args):
        """Generate Kubernetes manifests"""
        self.console.print("☸️ Kubernetes generation coming soon!", style="yellow")
    
    async def generate_serverless(self, args):
        """Generate serverless configuration"""
        self.console.print("⚡ Serverless generation coming soon!", style="yellow")
    
    async def init_project(self, args):
        """Initialize new ProServe project"""
        try:
            project_dir = Path(args.directory)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            self.console.print(f"📁 Initializing ProServe project in: {project_dir}")
            
            # Create basic manifest
            manifest_data = {
                "name": project_dir.name,
                "version": "1.0.0", 
                "type": "http",
                "host": "0.0.0.0",
                "port": 8080,
                "endpoints": [
                    {
                        "path": "/",
                        "method": "GET",
                        "response": {"message": "Hello from ProServe!"}
                    }
                ]
            }
            
            manifest_path = project_dir / "manifest.yml"
            with open(manifest_path, 'w') as f:
                yaml.dump(manifest_data, f, default_flow_style=False)
            
            # Create README
            readme_content = f"""# {project_dir.name}

A ProServe service

## Usage

```bash
# Run the service
proserve run manifest.yml

# Build for deployment
proserve build manifest.yml --output dist

# Generate Docker
proserve docker manifest.yml
```

## Generated by ProServe v2.0.0
"""
            
            readme_path = project_dir / "README.md"
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            
            self.console.print("✅ Project initialized successfully!")
            self.console.print(f"📄 Created: {manifest_path}")
            self.console.print(f"📖 Created: {readme_path}")
            self.console.print(f"\n🚀 Get started: cd {project_dir} && proserve run manifest.yml")
            
        except Exception as e:
            self.console.print(f"❌ Failed to initialize project: {e}", style="red")
    
    async def test_services(self, args):
        """Test ProServe services"""
        self.console.print("🧪 Testing feature coming soon!", style="yellow")
    
    async def validate_manifest(self, args):
        """Validate service manifest"""
        try:
            manifest_path = Path(args.manifest)
            if not manifest_path.exists():
                self.console.print(f"❌ Manifest file not found: {args.manifest}", style="red")
                return
            
            with open(manifest_path, 'r') as f:
                manifest_data = yaml.safe_load(f)
            
            # Validate by creating ServiceManifest instance
            manifest = ServiceManifest(**manifest_data)
            
            self.console.print("✅ Manifest is valid!", style="green")
            
            # Show manifest info
            table = Table(title="Manifest Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Name", manifest.name)
            table.add_row("Version", manifest.version or "1.0.0")
            table.add_row("Type", manifest.type)
            table.add_row("Host", manifest.host or "0.0.0.0")
            table.add_row("Port", str(manifest.port or 8080))
            
            if hasattr(manifest, 'endpoints') and manifest.endpoints:
                table.add_row("Endpoints", str(len(manifest.endpoints)))
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ Manifest validation failed: {e}", style="red")
    
    async def generate_examples(self, args):
        """Generate example projects"""
        try:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.console.print(f"📚 Generating examples in: {output_dir}")
            
            examples = {
                "hello-world": {
                    "name": "hello-world",
                    "version": "1.0.0",
                    "type": "http",
                    "host": "0.0.0.0",
                    "port": 8080,
                    "endpoints": [
                        {
                            "path": "/",
                            "method": "GET", 
                            "response": {"message": "Hello World!"}
                        }
                    ]
                },
                "static-site": {
                    "name": "static-site",
                    "version": "1.0.0", 
                    "type": "static",
                    "host": "0.0.0.0",
                    "port": 8080,
                    "static_hosting": {
                        "directory": "public",
                        "index": "index.html"
                    }
                },
                "api-service": {
                    "name": "api-service",
                    "version": "1.0.0",
                    "type": "http",
                    "host": "0.0.0.0", 
                    "port": 8080,
                    "enable_cors": True,
                    "endpoints": [
                        {
                            "path": "/api/users",
                            "method": "GET",
                            "response": {"users": []}
                        },
                        {
                            "path": "/api/users",
                            "method": "POST", 
                            "response": {"created": True}
                        }
                    ]
                }
            }
            
            for name, manifest_data in examples.items():
                example_dir = output_dir / name
                example_dir.mkdir(exist_ok=True)
                
                # Create manifest
                manifest_path = example_dir / "manifest.yml"
                with open(manifest_path, 'w') as f:
                    yaml.dump(manifest_data, f, default_flow_style=False)
                
                # Create README
                readme_content = f"""# {name}

{manifest_data.get('description', f'ProServe {name} example')}

## Usage

```bash
proserve run manifest.yml
```

Generated by ProServe v2.0.0
"""
                
                readme_path = example_dir / "README.md"
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                
                self.console.print(f"✅ Created example: {name}")
            
            self.console.print(f"\n🎯 Examples generated in: {output_dir}")
            
        except Exception as e:
            self.console.print(f"❌ Failed to generate examples: {e}", style="red")
