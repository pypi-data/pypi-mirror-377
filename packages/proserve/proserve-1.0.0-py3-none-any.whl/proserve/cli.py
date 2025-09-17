"""
ProServe Command Line Interface
Advanced CLI for ProServe framework management, service discovery, and migration
"""

import os
import sys
import json
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.tree import Tree

from .core.manifest import ServiceManifest
from .core.service import ProServeService
from .core.logging import setup_logging, create_logger
from .utils.config import ProServeConfig
from .utils.helpers import get_framework_info, validate_environment


class ProServeCLI:
    """Main CLI class for ProServe framework"""
    
    def __init__(self):
        self.console = Console()
        self.config = ProServeConfig()
        self.logger = create_logger("proserve-cli")
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            prog="proserve",
            description="ProServe - Professional Service Framework CLI",
            formatter_class=argparse.RichHelpFormatter if hasattr(argparse, 'RichHelpFormatter') else argparse.HelpFormatter
        )
        
        parser.add_argument(
            "--version", 
            action="version", 
            version=f"ProServe {get_framework_info().get('version', '1.0.0')}"
        )
        
        parser.add_argument(
            "--debug", 
            action="store_true", 
            help="Enable debug logging"
        )
        
        parser.add_argument(
            "--config", 
            type=str, 
            help="Path to ProServe configuration file"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Service management commands
        self._add_service_commands(subparsers)
        
        # Discovery commands
        self._add_discovery_commands(subparsers)
        
        # Migration commands
        self._add_migration_commands(subparsers)
        
        # Platform commands
        self._add_platform_commands(subparsers)
        
        # Development commands
        self._add_dev_commands(subparsers)
        
        return parser
    
    def _add_service_commands(self, subparsers):
        """Add service management commands"""
        
        # Run service
        run_parser = subparsers.add_parser("run", help="Run a ProServe service")
        run_parser.add_argument("manifest", help="Path to service manifest file")
        run_parser.add_argument("--port", type=int, help="Override service port")
        run_parser.add_argument("--host", type=str, help="Override service host")
        run_parser.add_argument("--env", type=str, help="Environment file to load")
        
        # Create service
        create_parser = subparsers.add_parser("create", help="Create a new ProServe service")
        create_parser.add_argument("name", help="Service name")
        create_parser.add_argument("--type", choices=["http", "websocket", "micropython", "arduino"], 
                                 default="http", help="Service type")
        create_parser.add_argument("--platform", help="Target platform (for embedded services)")
        create_parser.add_argument("--board", help="Target board (for embedded services)")
        create_parser.add_argument("--port", type=int, default=8080, help="Service port")
        create_parser.add_argument("--template", help="Service template to use")
        
        # Validate service
        validate_parser = subparsers.add_parser("validate", help="Validate service manifest")
        validate_parser.add_argument("manifest", help="Path to service manifest file")
        
        # List services
        list_parser = subparsers.add_parser("list", help="List ProServe services")
        list_parser.add_argument("--directory", help="Directory to search for services")
        list_parser.add_argument("--format", choices=["table", "json", "yaml"], 
                               default="table", help="Output format")
    
    def _add_discovery_commands(self, subparsers):
        """Add service discovery commands"""
        
        # Discover services
        discover_parser = subparsers.add_parser("discover", help="Discover existing services")
        discover_parser.add_argument("path", help="Path to analyze for services")
        discover_parser.add_argument("--recursive", action="store_true", help="Recursive discovery")
        discover_parser.add_argument("--output", help="Output directory for generated manifests")
        discover_parser.add_argument("--framework", choices=["auto", "flask", "fastapi", "django", "aiohttp"], 
                                   default="auto", help="Framework to detect")
        
        # Generate manifest
        generate_parser = subparsers.add_parser("generate", help="Generate service manifest")
        generate_parser.add_argument("service_file", help="Service file to analyze")
        generate_parser.add_argument("--output", help="Output manifest file")
        generate_parser.add_argument("--name", help="Service name")
        generate_parser.add_argument("--type", help="Service type")
    
    def _add_migration_commands(self, subparsers):
        """Add migration commands"""
        
        # Migrate service
        migrate_parser = subparsers.add_parser("migrate", help="Migrate service to ProServe")
        migrate_parser.add_argument("source", help="Source service or directory")
        migrate_parser.add_argument("--target", help="Target directory for migrated service")
        migrate_parser.add_argument("--strategy", choices=["blue-green", "rolling", "immediate"], 
                                  default="blue-green", help="Migration strategy")
        migrate_parser.add_argument("--backup", action="store_true", help="Create backup before migration")
        
        # Migration status
        status_parser = subparsers.add_parser("status", help="Check migration status")
        status_parser.add_argument("--service", help="Specific service to check")
        
        # Rollback migration
        rollback_parser = subparsers.add_parser("rollback", help="Rollback migration")
        rollback_parser.add_argument("service", help="Service to rollback")
        rollback_parser.add_argument("--version", help="Version to rollback to")
    
    def _add_platform_commands(self, subparsers):
        """Add platform-specific commands"""
        
        # Platform info
        platform_parser = subparsers.add_parser("platform", help="Platform management")
        platform_subparsers = platform_parser.add_subparsers(dest="platform_command")
        
        # List platforms
        list_platforms_parser = platform_subparsers.add_parser("list", help="List supported platforms")
        
        # Detect devices
        detect_parser = platform_subparsers.add_parser("detect", help="Detect connected devices")
        detect_parser.add_argument("--platform", help="Specific platform to detect")
        
        # Flash firmware
        flash_parser = platform_subparsers.add_parser("flash", help="Flash firmware to device")
        flash_parser.add_argument("firmware", help="Firmware file to flash")
        flash_parser.add_argument("--device", help="Target device")
        flash_parser.add_argument("--platform", help="Target platform")
    
    def _add_dev_commands(self, subparsers):
        """Add development commands"""
        
        # Init project
        init_parser = subparsers.add_parser("init", help="Initialize ProServe project")
        init_parser.add_argument("directory", nargs="?", default=".", help="Project directory")
        init_parser.add_argument("--template", help="Project template")
        
        # Build project
        build_parser = subparsers.add_parser("build", help="Build ProServe project")
        build_parser.add_argument("--docker", action="store_true", help="Build Docker images")
        build_parser.add_argument("--platform", help="Target platform for build")
        
        # Test project
        test_parser = subparsers.add_parser("test", help="Test ProServe services")
        test_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
        test_parser.add_argument("--integration", action="store_true", help="Run integration tests")
        
        # Info command
        info_parser = subparsers.add_parser("info", help="Show ProServe framework information")
    
    async def run_service(self, args):
        """Run a ProServe service"""
        try:
            manifest_path = Path(args.manifest)
            if not manifest_path.exists():
                self.console.print(f"❌ Manifest file not found: {manifest_path}", style="red")
                return 1
            
            self.console.print(f"🚀 Loading service manifest: {manifest_path}", style="green")
            
            # Load and validate manifest
            manifest = ServiceManifest.from_yaml(str(manifest_path))
            
            # Override port and host if specified
            if args.port:
                manifest.port = args.port
            if args.host:
                manifest.host = args.host
            
            # Load environment file if specified
            if args.env:
                from dotenv import load_dotenv
                load_dotenv(args.env)
            
            # Create and run service
            service = ProServeService(manifest)
            
            self.console.print(Panel(
                f"Service: {manifest.name}\n"
                f"Version: {manifest.version}\n"
                f"Type: {manifest.type}\n"
                f"Platform: {manifest.platform or 'default'}\n"
                f"Isolation: {manifest.isolation.get('mode', 'none')}\n"
                f"Host: {manifest.host}:{manifest.port}",
                title="🚀 ProServe Service Starting",
                border_style="green"
            ))
            
            await service.run()
            return 0
            
        except Exception as e:
            self.console.print(f"❌ Failed to run service: {e}", style="red")
            if args.debug:
                self.console.print_exception()
            return 1
    
    def create_service(self, args):
        """Create a new ProServe service"""
        try:
            service_name = args.name
            service_dir = Path(service_name)
            
            if service_dir.exists():
                if not Confirm.ask(f"Directory {service_dir} already exists. Continue?"):
                    return 1
            else:
                service_dir.mkdir(parents=True)
            
            # Create service structure
            self._create_service_structure(service_dir, args)
            
            self.console.print(f"✅ Created ProServe service: {service_name}", style="green")
            self.console.print(f"📁 Location: {service_dir.absolute()}")
            self.console.print("\n🚀 To run your service:")
            self.console.print(f"   cd {service_name}")
            self.console.print(f"   proserve run manifest.yml")
            
            return 0
            
        except Exception as e:
            self.console.print(f"❌ Failed to create service: {e}", style="red")
            return 1
    
    def _create_service_structure(self, service_dir: Path, args):
        """Create service directory structure"""
        
        # Create directories
        (service_dir / "handlers").mkdir(exist_ok=True)
        (service_dir / "static").mkdir(exist_ok=True)
        (service_dir / "templates").mkdir(exist_ok=True)
        (service_dir / "tests").mkdir(exist_ok=True)
        
        # Create manifest
        manifest_data = {
            "name": args.name,
            "version": "1.0.0",
            "type": args.type,
            "port": args.port,
            "host": "0.0.0.0",
            "enable_cors": True,
            "enable_health": True,
            "enable_metrics": True,
            "endpoints": [
                {
                    "path": "/",
                    "method": "GET",
                    "script": "handlers/index.py"
                }
            ],
            "isolation": {
                "mode": "none",
                "timeout": 30
            }
        }
        
        # Add platform-specific settings
        if args.platform:
            manifest_data["platform"] = args.platform
            manifest_data["isolation"]["mode"] = "micropython" if args.platform.startswith(("rp2040", "esp")) else "arduino"
            manifest_data["isolation"]["platform"] = args.platform
        
        if args.board:
            manifest_data["board"] = args.board
            manifest_data["isolation"]["board"] = args.board
        
        # Write manifest
        with open(service_dir / "manifest.yml", "w") as f:
            yaml.dump(manifest_data, f, default_flow_style=False, indent=2)
        
        # Create basic handler
        handler_content = '''"""
Basic ProServe handler
"""

async def main(request, service):
    """Main handler for the root endpoint"""
    return {
        "message": "Hello from ProServe!",
        "service": service.manifest.name,
        "version": service.manifest.version,
        "platform": service.manifest.platform or "default"
    }
'''
        
        with open(service_dir / "handlers" / "index.py", "w") as f:
            f.write(handler_content)
        
        # Create requirements.txt
        requirements = [
            "proserve>=1.0.0",
            "aiohttp>=3.8.0",
            "pyyaml>=6.0",
            "python-dotenv>=1.0.0"
        ]
        
        if args.platform:
            if args.platform.startswith(("rp2040", "esp")):
                requirements.extend([
                    "pyserial>=3.5",
                    "esptool>=4.0",
                    "ampy>=1.1.0"
                ])
            elif "arduino" in args.platform:
                requirements.extend([
                    "platformio>=6.0",
                    "pyserial>=3.5"
                ])
        
        with open(service_dir / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        # Create README
        readme_content = f"""# {args.name}

ProServe service - {args.type} type

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
proserve run manifest.yml
```

## Platform

- Type: {args.type}
- Platform: {args.platform or "default"}
- Board: {args.board or "N/A"}

## Endpoints

- GET / - Main endpoint

## Development

```bash
# Test the service
proserve test

# Build for production
proserve build
```
"""
        
        with open(service_dir / "README.md", "w") as f:
            f.write(readme_content)
    
    def validate_service(self, args):
        """Validate a service manifest"""
        try:
            manifest_path = Path(args.manifest)
            if not manifest_path.exists():
                self.console.print(f"❌ Manifest file not found: {manifest_path}", style="red")
                return 1
            
            # Load and validate manifest
            manifest = ServiceManifest.from_yaml(str(manifest_path))
            errors = manifest.validate()
            
            if not errors:
                self.console.print(f"✅ Manifest is valid: {manifest_path}", style="green")
                
                # Show manifest info
                info_table = Table(title="Service Information")
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("Name", manifest.name)
                info_table.add_row("Version", manifest.version)
                info_table.add_row("Type", manifest.type)
                info_table.add_row("Platform", manifest.platform or "default")
                info_table.add_row("Port", str(manifest.port))
                info_table.add_row("Isolation Mode", manifest.isolation.get('mode', 'none'))
                info_table.add_row("Endpoints", str(len(manifest.endpoints)))
                info_table.add_row("WebSocket Handlers", str(len(manifest.websocket_handlers)))
                info_table.add_row("Background Tasks", str(len(manifest.background_tasks)))
                
                self.console.print(info_table)
                return 0
            else:
                self.console.print(f"❌ Manifest validation failed:", style="red")
                for error in errors:
                    self.console.print(f"  • {error}", style="red")
                return 1
                
        except Exception as e:
            self.console.print(f"❌ Failed to validate manifest: {e}", style="red")
            return 1
    
    def show_info(self, args):
        """Show ProServe framework information"""
        info = get_framework_info()
        env_status = validate_environment()
        
        # Framework info panel
        info_content = f"""
Version: {info['version']}
Author: {info['author']}
License: {info['license']}
URL: {info['url']}

Features:
{chr(10).join(f'  • {feature}' for feature in info['features'])}

Supported Environments:
{chr(10).join(f'  • {env}' for env in info['environments'])}
"""
        
        self.console.print(Panel(
            info_content.strip(),
            title="🚀 ProServe Framework",
            border_style="green"
        ))
        
        # Environment status
        status_style = "green" if env_status['status'] == 'ok' else "red"
        status_content = f"""
Core Available: {'✅' if env_status['core_available'] else '❌'}
MicroPython Available: {'✅' if env_status.get('micropython_available') else '❌'}
Arduino Available: {'✅' if env_status.get('arduino_available') else '❌'}
"""
        
        self.console.print(Panel(
            status_content.strip(),
            title="Environment Status",
            border_style=status_style
        ))
        
        return 0
    
    async def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 0
        
        # Configure logging
        if args.debug:
            os.environ["DEBUG"] = "true"
        
        # Load config if specified
        if args.config:
            self.config.load_from_file(args.config)
        
        # Execute command
        try:
            if args.command == "run":
                return await self.run_service(args)
            elif args.command == "create":
                return self.create_service(args)
            elif args.command == "validate":
                return self.validate_service(args)
            elif args.command == "info":
                return self.show_info(args)
            elif args.command == "discover":
                return await self.discover_services(args)
            elif args.command == "migrate":
                return await self.migrate_service(args)
            elif args.command == "platform":
                return await self.handle_platform_command(args)
            else:
                self.console.print(f"❌ Command not implemented: {args.command}", style="red")
                return 1
                
        except KeyboardInterrupt:
            self.console.print("\n👋 ProServe CLI interrupted", style="yellow")
            return 130
        except Exception as e:
            self.console.print(f"❌ Command failed: {e}", style="red")
            if args.debug:
                self.console.print_exception()
            return 1
    
    async def discover_services(self, args):
        """Discover existing services (placeholder)"""
        self.console.print("🔍 Service discovery feature coming soon!", style="yellow")
        return 0
    
    async def migrate_service(self, args):
        """Migrate service to ProServe (placeholder)"""
        self.console.print("🔄 Service migration feature coming soon!", style="yellow")
        return 0
    
    async def handle_platform_command(self, args):
        """Handle platform commands (placeholder)"""
        self.console.print("🔧 Platform management feature coming soon!", style="yellow")
        return 0


def main():
    """CLI entry point"""
    cli = ProServeCLI()
    return asyncio.run(cli.main())


if __name__ == "__main__":
    sys.exit(main())
