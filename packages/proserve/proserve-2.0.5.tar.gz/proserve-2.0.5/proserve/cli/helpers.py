"""
ProServe CLI Helpers and Utilities
Common utilities and helper functions for ProServe CLI

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.config import ProServeConfig


class CLIHelpers:
    """Common helper functions for CLI operations"""
    
    def __init__(self):
        self.console = Console()
        self.config = ProServeConfig()
    
    def load_manifest(self, manifest_path: str) -> Dict[str, Any]:
        """Load and validate manifest file"""
        try:
            path = Path(manifest_path)
            if not path.exists():
                raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
            
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported manifest format: {path.suffix}")
        
        except Exception as e:
            self.console.print(f"❌ Failed to load manifest: {e}", style="red")
            raise
    
    def save_manifest(self, manifest_data: Dict[str, Any], output_path: str) -> bool:
        """Save manifest to file"""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(manifest_data, f, default_flow_style=False, indent=2)
                elif path.suffix.lower() == '.json':
                    json.dump(manifest_data, f, indent=2)
                else:
                    raise ValueError(f"Unsupported output format: {path.suffix}")
            
            return True
        
        except Exception as e:
            self.console.print(f"❌ Failed to save manifest: {e}", style="red")
            return False
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        dependencies = {
            'python': self._check_command('python3'),
            'pip': self._check_command('pip'),
            'docker': self._check_command('docker'),
            'git': self._check_command('git'),
            'curl': self._check_command('curl'),
            'openssl': self._check_command('openssl')
        }
        
        return dependencies
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def validate_project_structure(self, project_dir: str) -> Dict[str, bool]:
        """Validate project directory structure"""
        path = Path(project_dir)
        
        structure = {
            'directory_exists': path.exists() and path.is_dir(),
            'manifest_exists': (path / 'manifest.yml').exists() or (path / 'manifest.yaml').exists(),
            'readme_exists': (path / 'README.md').exists(),
            'gitignore_exists': (path / '.gitignore').exists(),
            'requirements_exists': (path / 'requirements.txt').exists(),
            'dockerfile_exists': (path / 'Dockerfile').exists()
        }
        
        return structure
    
    def create_project_structure(self, project_dir: str, template: str = 'basic') -> bool:
        """Create basic project structure"""
        try:
            path = Path(project_dir)
            path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitignore
            gitignore_content = """# ProServe Project
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Certificates
*.pem
*.crt
*.key

# Environment
.env
.env.local

# Build output
build/
dist/
"""
            
            with open(path / '.gitignore', 'w') as f:
                f.write(gitignore_content)
            
            self.console.print(f"✅ Project structure created in: {project_dir}")
            return True
        
        except Exception as e:
            self.console.print(f"❌ Failed to create project structure: {e}", style="red")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for debugging"""
        import platform
        
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': os.getcwd(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'environment_variables': {
                'PATH': os.getenv('PATH', ''),
                'PYTHONPATH': os.getenv('PYTHONPATH', ''),
                'VIRTUAL_ENV': os.getenv('VIRTUAL_ENV', ''),
            }
        }
    
    def show_system_info(self):
        """Display system information"""
        info = self.get_system_info()
        
        self.console.print(Panel.fit(
            f"""
🖥️  **System Information**

• OS: {info['os']} {info['os_version']}
• Architecture: {info['architecture'][0]}
• Python: {info['python_version'].split()[0]}
• User: {info['user']}
• Working Dir: {info['working_directory']}
• Virtual Env: {info['environment_variables']['VIRTUAL_ENV'] or 'None'}

Generated by ProServe v2.0.0
""",
            title="System Info",
            border_style="blue"
        ))
    
    def show_dependencies_status(self):
        """Display dependencies status"""
        deps = self.check_dependencies()
        
        table_content = []
        for name, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            table_content.append(f"• {name.ljust(10)}: {status}")
        
        self.console.print(Panel.fit(
            "\n".join(table_content),
            title="Dependencies Status",
            border_style="green" if all(deps.values()) else "yellow"
        ))
    
    def suggest_improvements(self, project_dir: str) -> List[str]:
        """Suggest project improvements"""
        suggestions = []
        structure = self.validate_project_structure(project_dir)
        
        if not structure['manifest_exists']:
            suggestions.append("📄 Create manifest.yml: proserve init")
        
        if not structure['readme_exists']:
            suggestions.append("📖 Add README.md with project description")
        
        if not structure['dockerfile_exists']:
            suggestions.append("🐳 Generate Dockerfile: proserve docker manifest.yml")
        
        if not structure['requirements_exists']:
            suggestions.append("📦 Create requirements.txt with dependencies")
        
        if not structure['gitignore_exists']:
            suggestions.append("🚫 Add .gitignore for clean git history")
        
        return suggestions
    
    def show_quick_start_guide(self):
        """Display quick start guide"""
        guide = """
🚀 **ProServe Quick Start Guide**

**1. Initialize Project**
```bash
proserve init my-service
cd my-service
```

**2. Run Service** 
```bash
proserve run manifest.yml
```

**3. Build for Deployment**
```bash
proserve build manifest.yml --output dist
```

**4. Generate Docker**
```bash
proserve docker manifest.yml
```

**5. Create Examples**
```bash
proserve examples --output examples
```

🎯 **Key Benefits:**
• 64% Less Code - YAML-driven approach
• 90% Faster Setup - Zero configuration needed
• 100% Production Ready - TLS, CORS, health checks included

📚 **Learn More:**
• Examples: proserve examples
• Validate: proserve validate manifest.yml  
• System Info: proserve --version
"""
        
        self.console.print(Panel(guide, border_style="cyan", expand=False))
    
    def show_examples_overview(self):
        """Show available examples"""
        examples = {
            'hello-world': 'Simple HTTP service with single endpoint',
            'static-site': 'Static website hosting with TLS support', 
            'api-service': 'REST API with CORS and multiple endpoints',
            'micropython-rp2040': 'MicroPython service for RP2040 boards',
            'micropython-rpi': 'MicroPython service for Raspberry Pi',
            'docker-app': 'Containerized application with Docker support',
            'serverless-function': 'Serverless function for cloud deployment'
        }
        
        content = "🎯 **Available Examples:**\n\n"
        for name, description in examples.items():
            content += f"• **{name}**: {description}\n"
        
        content += f"\n💡 Generate examples: `proserve examples --output examples`"
        
        self.console.print(Panel(content, title="ProServe Examples", border_style="magenta"))


class ProgressHelper:
    """Helper for showing progress during operations"""
    
    def __init__(self):
        self.console = Console()
    
    def show_progress(self, tasks: List[str], operation: str = "Processing"):
        """Show progress for multiple tasks"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task_id = progress.add_task(f"{operation}...", total=len(tasks))
            
            for i, task in enumerate(tasks):
                progress.update(task_id, description=f"{operation}: {task}")
                yield task
                progress.advance(task_id)
            
            progress.update(task_id, description=f"{operation} completed!")


class ConfigHelper:
    """Helper for configuration management"""
    
    def __init__(self):
        self.console = Console()
        self.config_file = Path.home() / '.proserve' / 'config.yml'
    
    def load_config(self) -> Dict[str, Any]:
        """Load user configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save user configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to save config: {e}", style="red")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'author': {
                'name': 'ProServe User',
                'email': 'user@example.com'
            },
            'defaults': {
                'host': '0.0.0.0',
                'port': 8080,
                'enable_cors': True,
                'enable_health': True,
                'tls_provider': 'selfsigned'
            },
            'paths': {
                'projects': str(Path.home() / 'proserve-projects'),
                'templates': str(Path.home() / '.proserve' / 'templates')
            }
        }
