"""
ProServe Main CLI
Modular CLI entry point that orchestrates all CLI functionality

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import sys
import asyncio
from typing import Dict, Any, Optional

from rich.console import Console

from .parsers import ProServeArgumentParser
from .commands import ProServeCommandManager
from .helpers import CLIHelpers, ProgressHelper, ConfigHelper
from ..core.logging import setup_logging, create_logger


class ProServeCLI:
    """
    Main CLI class for ProServe framework - Modular and Simplified
    
    This is the new modular CLI that replaces the monolithic cli.py file.
    It provides a clean, simple interface for all ProServe operations.
    """
    
    def __init__(self):
        self.console = Console()
        self.parser_manager = ProServeArgumentParser()
        self.command_manager = ProServeCommandManager()
        self.helpers = CLIHelpers()
        self.progress = ProgressHelper()
        self.config_helper = ConfigHelper()
        self.logger = create_logger("proserve-cli")
        
        # Load user configuration
        self.user_config = self.config_helper.load_config()
    
    async def main(self):
        """Main CLI entry point - Simplified and User-Friendly"""
        try:
            # Create argument parser
            parser = self.parser_manager.create_parser()
            args = parser.parse_args()
            
            # Handle no command case with helpful guidance
            if not args.command:
                self._show_welcome_message()
                self.helpers.show_quick_start_guide()
                return 0
            
            # Setup logging based on arguments
            if args.debug:
                setup_logging(level="DEBUG", enable_rich=True)
            elif args.verbose:
                setup_logging(level="INFO", enable_rich=True)
            else:
                setup_logging(level="WARNING", enable_rich=True)
            
            # Route to appropriate command handler
            return await self._route_command(args)
            
        except KeyboardInterrupt:
            self.console.print("\n👋 Goodbye!", style="yellow")
            return 0
        except Exception as e:
            self.logger.exception("CLI error occurred")
            self.console.print(f"❌ An error occurred: {e}", style="red")
            
            if hasattr(args, 'debug') and args.debug:
                raise  # Re-raise in debug mode for full traceback
            
            return 1
    
    def _show_welcome_message(self):
        """Show welcoming message for new users"""
        welcome = """
🚀 **Welcome to ProServe v2.0.0**
The YAML-Driven Web Services Revolution

🎯 **Key Benefits:**
• 64% Less Code - Pure YAML configuration
• 90% Faster Setup - Zero boilerplate needed  
• 100% Production Ready - TLS, CORS, health checks included

🏁 **Get Started in 30 seconds:**
```bash
proserve init my-service    # Create new service
proserve run manifest.yml   # Run your service
```

💡 **Need help?** Run: `proserve --help`
📚 **See examples:** Run: `proserve examples`
"""
        
        self.console.print(welcome, style="cyan")
    
    async def _route_command(self, args) -> int:
        """Route command to appropriate handler"""
        command_map = {
            # Service management
            'run': self.command_manager.run_service,
            'build': self.command_manager.build_service,
            'deploy': self.command_manager.deploy_service,
            
            # Service lifecycle
            'list': self.command_manager.list_services,
            'status': self.command_manager.service_status,
            'stop': self.command_manager.stop_service,
            'restart': self.command_manager.restart_service,
            'logs': self.command_manager.show_logs,
            
            # Code generation
            'docker': self.command_manager.generate_docker,
            'k8s': self.command_manager.generate_k8s,
            'serverless': self.command_manager.generate_serverless,
            
            # Development
            'init': self.command_manager.init_project,
            'test': self.command_manager.test_services,
            'validate': self.command_manager.validate_manifest,
            'examples': self.command_manager.generate_examples,
            
            # Special commands
            'info': self._handle_info_command,
            'config': self._handle_config_command,
            'doctor': self._handle_doctor_command,
        }
        
        handler = command_map.get(args.command)
        if not handler:
            self.console.print(f"❌ Unknown command: {args.command}", style="red")
            return 1
        
        try:
            await handler(args)
            return 0
        except Exception as e:
            self.console.print(f"❌ Command failed: {e}", style="red")
            return 1
    
    async def _handle_info_command(self, args):
        """Handle system info command"""
        self.helpers.show_system_info()
        self.helpers.show_dependencies_status()
        
        # Show project info if in project directory
        if self.helpers.validate_project_structure('.')['manifest_exists']:
            try:
                manifest = self.helpers.load_manifest('manifest.yml') 
                self.console.print(f"\n📋 **Current Project:** {manifest.get('name', 'Unknown')}")
                self.console.print(f"📦 Version: {manifest.get('version', '1.0.0')}")
                self.console.print(f"🔧 Type: {manifest.get('type', 'http')}")
            except:
                pass
    
    async def _handle_config_command(self, args):
        """Handle configuration management"""
        if hasattr(args, 'show') and args.show:
            config = self.config_helper.load_config()
            self.console.print("⚙️ **ProServe Configuration:**")
            self.console.print_json(data=config if config else self.config_helper.get_default_config())
        else:
            # Interactive config setup
            self.console.print("⚙️ **ProServe Configuration Setup**")
            config = self._interactive_config_setup()
            if self.config_helper.save_config(config):
                self.console.print("✅ Configuration saved!")
            else:
                self.console.print("❌ Failed to save configuration", style="red")
    
    async def _handle_doctor_command(self, args):
        """Handle system health check"""
        self.console.print("🏥 **ProServe System Health Check**")
        
        # Check dependencies
        self.helpers.show_dependencies_status()
        
        # Check project structure if in project
        if self.helpers.validate_project_structure('.')['directory_exists']:
            suggestions = self.helpers.suggest_improvements('.')
            if suggestions:
                self.console.print("\n💡 **Suggestions for Improvement:**")
                for suggestion in suggestions:
                    self.console.print(f"  {suggestion}")
            else:
                self.console.print("\n✅ **Project structure looks good!**")
        
        # Show configuration status
        config = self.config_helper.load_config()
        if not config:
            self.console.print("\n⚠️  **No configuration found** - Run: `proserve config`")
        else:
            self.console.print("\n✅ **Configuration found**")
    
    def _interactive_config_setup(self) -> Dict[str, Any]:
        """Interactive configuration setup for new users"""
        from rich.prompt import Prompt
        
        config = self.config_helper.get_default_config()
        
        # Author information
        name = Prompt.ask("👤 Your name", default=config['author']['name'])
        email = Prompt.ask("📧 Your email", default=config['author']['email'])
        
        config['author'] = {'name': name, 'email': email}
        
        # Default settings
        host = Prompt.ask("🌐 Default host", default=config['defaults']['host'])
        port = Prompt.ask("🚪 Default port", default=str(config['defaults']['port']))
        
        config['defaults']['host'] = host
        config['defaults']['port'] = int(port)
        
        return config


# Simplified CLI entry points for easy access
def run_cli():
    """Simple entry point for CLI execution"""
    cli = ProServeCLI()
    return asyncio.run(cli.main())


def main():
    """Main entry point - called by console_scripts"""
    try:
        exit_code = run_cli()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)


# Allow running as script
if __name__ == "__main__":
    main()
