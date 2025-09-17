"""
ProServe Command Generator - Main Command Generation Coordinator
Orchestrates all command generators to create comprehensive command sets from manifests
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from ...core.manifest import ServiceManifest
from .command_types import GeneratedCommand, CommandType, CommandCategory
from .http_generator import HTTPCommandGenerator, generate_openapi_spec
from .export_formatter import ExportFormatter


class CommandGenerator:
    """Main command generator that coordinates all specialized generators"""
    
    def __init__(self, manifest: Union[ServiceManifest, Dict[str, Any], str, Path]):
        """Initialize with manifest data"""
        if isinstance(manifest, (str, Path)):
            # Load from file
            content = Path(manifest).read_text()
            if str(manifest).endswith(('.yml', '.yaml')):
                self.manifest_data = yaml.safe_load(content)
            else:
                self.manifest_data = json.loads(content)
        elif isinstance(manifest, ServiceManifest):
            # Convert ServiceManifest to dict
            self.manifest_data = self._service_manifest_to_dict(manifest)
        else:
            self.manifest_data = manifest
        
        # Extract common configuration
        self.service_name = self.manifest_data.get('name', 'service')
        self.server_config = self.manifest_data.get('server', {'host': 'localhost', 'port': 8000})
        self.base_url = f"http://{self.server_config['host']}:{self.server_config['port']}"
        
        # Initialize specialized generators
        self.http_generator = HTTPCommandGenerator(self.base_url)
        self.export_formatter = ExportFormatter()
        
        # Command categories
        self.categories = {}
        self._setup_categories()
    
    def _service_manifest_to_dict(self, manifest: ServiceManifest) -> Dict[str, Any]:
        """Convert ServiceManifest object to dictionary"""
        try:
            # Try to use dataclass asdict if available
            from dataclasses import asdict
            return asdict(manifest)
        except:
            # Fallback to manual conversion
            return {
                'name': getattr(manifest, 'name', 'service'),
                'version': getattr(manifest, 'version', '1.0.0'),
                'server': getattr(manifest, 'server', {}),
                'endpoints': getattr(manifest, 'endpoints', []),
                'background_tasks': getattr(manifest, 'background_tasks', []),
                'databases': getattr(manifest, 'databases', []),
                'grpc_services': getattr(manifest, 'grpc_services', [])
            }
    
    def _setup_categories(self):
        """Setup command categories"""
        self.categories = {
            'service': CommandCategory('Service Management', 'Commands for managing the service lifecycle'),
            'http': CommandCategory('HTTP API', 'Commands for interacting with HTTP endpoints'),
            'grpc': CommandCategory('gRPC API', 'Commands for interacting with gRPC services'),
            'database': CommandCategory('Database', 'Commands for database operations'),
            'monitoring': CommandCategory('Monitoring', 'Commands for health checks and metrics'),
            'testing': CommandCategory('Testing', 'Commands for testing the service'),
            'deployment': CommandCategory('Deployment', 'Commands for deploying the service')
        }
    
    def generate_all(self) -> List[GeneratedCommand]:
        """Generate all types of commands"""
        all_commands = []
        
        # Service management commands
        service_commands = self.generate_service_commands()
        all_commands.extend(service_commands)
        self.categories['service'].commands.extend(service_commands)
        
        # HTTP endpoint commands
        http_commands = self.generate_http_commands()
        all_commands.extend(http_commands)
        self.categories['http'].commands.extend(http_commands)
        
        # gRPC commands
        grpc_commands = self.generate_grpc_commands()
        all_commands.extend(grpc_commands)
        self.categories['grpc'].commands.extend(grpc_commands)
        
        # Database commands
        database_commands = self.generate_database_commands()
        all_commands.extend(database_commands)
        self.categories['database'].commands.extend(database_commands)
        
        # Monitoring commands
        monitoring_commands = self.generate_monitoring_commands()
        all_commands.extend(monitoring_commands)
        self.categories['monitoring'].commands.extend(monitoring_commands)
        
        # Testing commands
        testing_commands = self.generate_testing_commands()
        all_commands.extend(testing_commands)
        self.categories['testing'].commands.extend(testing_commands)
        
        # Deployment commands
        deployment_commands = self.generate_deployment_commands()
        all_commands.extend(deployment_commands)
        self.categories['deployment'].commands.extend(deployment_commands)
        
        return all_commands
    
    def generate_service_commands(self) -> List[GeneratedCommand]:
        """Generate service lifecycle commands"""
        commands = []
        
        # Start service
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='python -m proserve run manifest.yml',
            description='Start ProServe service'
        ))
        
        # Start in development mode
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='python -m proserve run manifest.yml --dev --reload',
            description='Start service in development mode with auto-reload'
        ))
        
        # Stop service
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='pkill -f "proserve"',
            description='Stop ProServe service'
        ))
        
        return commands
    
    def generate_http_commands(self) -> List[GeneratedCommand]:
        """Generate HTTP endpoint commands"""
        endpoints = self.manifest_data.get('endpoints', [])
        if not endpoints:
            return []
        
        commands = []
        
        # Generate endpoint-specific commands
        commands.extend(self.http_generator.generate_endpoint_commands(endpoints))
        
        # Generate health check commands
        commands.extend(self.http_generator.generate_health_check_commands())
        
        # Generate metrics commands
        commands.extend(self.http_generator.generate_metrics_commands())
        
        return commands
    
    def generate_grpc_commands(self) -> List[GeneratedCommand]:
        """Generate gRPC service commands"""
        grpc_services = self.manifest_data.get('grpc_services', [])
        if not grpc_services:
            return []
        
        commands = []
        
        for service in grpc_services:
            service_name = service.get('name', 'Service')
            package = service.get('package', '')
            methods = service.get('methods', [])
            
            # Generate grpcurl commands for each method
            for method in methods:
                method_name = method.get('name', 'Method')
                full_service_name = f"{package}.{service_name}" if package else service_name
                
                commands.append(GeneratedCommand(
                    type=CommandType.GRPC,
                    command=f'grpcurl -plaintext -d \'{{"key": "value"}}\' {self.server_config["host"]}:{self.server_config.get("grpc_port", 50051)} {full_service_name}/{method_name}',
                    description=f'Call gRPC method {method_name}',
                    example_output='{"result": "success"}'
                ))
        
        return commands
    
    def generate_database_commands(self) -> List[GeneratedCommand]:
        """Generate database management commands"""
        databases = self.manifest_data.get('databases', [])
        if not databases:
            return []
        
        commands = []
        
        for db in databases:
            db_type = db.get('type', 'postgresql')
            db_name = db.get('database', 'mydb')
            
            if db_type == 'postgresql':
                commands.extend([
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command=f'psql -h localhost -U postgres -d {db_name} -c "SELECT version();"',
                        description='Check PostgreSQL connection',
                        example_output='PostgreSQL 13.7 on x86_64-pc-linux-gnu'
                    ),
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command=f'pg_dump -h localhost -U postgres {db_name} > backup.sql',
                        description='Backup PostgreSQL database'
                    )
                ])
            
            elif db_type == 'mysql':
                commands.extend([
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command=f'mysql -h localhost -u root -p {db_name} -e "SELECT VERSION();"',
                        description='Check MySQL connection',
                        example_output='8.0.30'
                    ),
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command=f'mysqldump -h localhost -u root -p {db_name} > backup.sql',
                        description='Backup MySQL database'
                    )
                ])
            
            elif db_type == 'redis':
                commands.extend([
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command='redis-cli ping',
                        description='Check Redis connection',
                        example_output='PONG'
                    ),
                    GeneratedCommand(
                        type=CommandType.SHELL,
                        command='redis-cli info',
                        description='Get Redis server information'
                    )
                ])
        
        return commands
    
    def generate_monitoring_commands(self) -> List[GeneratedCommand]:
        """Generate monitoring and observability commands"""
        commands = []
        
        # Health check (already handled by HTTP generator, but add shell version)
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command=f'curl -f {self.base_url}/health || echo "Service is unhealthy"',
            description='Health check with shell script',
            example_output='{"status": "healthy"}'
        ))
        
        # Service logs
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='tail -f proserve.log',
            description='Follow service logs'
        ))
        
        # Process monitoring
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command='ps aux | grep proserve',
            description='Check ProServe processes'
        ))
        
        # Port monitoring
        port = self.server_config.get('port', 8000)
        commands.append(GeneratedCommand(
            type=CommandType.SHELL,
            command=f'netstat -tlnp | grep :{port}',
            description=f'Check if port {port} is listening'
        ))
        
        return commands
    
    def generate_testing_commands(self) -> List[GeneratedCommand]:
        """Generate testing commands"""
        commands = []
        endpoints = self.manifest_data.get('endpoints', [])
        
        # Generate testing commands using HTTP generator
        if endpoints:
            commands.extend(self.http_generator.generate_testing_commands(endpoints))
        
        # Add generic test commands
        commands.extend([
            GeneratedCommand(
                type=CommandType.SHELL,
                command='python -m pytest tests/ -v',
                description='Run all tests',
                example_output='test_api.py::test_get_users PASSED\n2 passed in 0.15s'
            ),
            GeneratedCommand(
                type=CommandType.SHELL,
                command='python -m pytest tests/ --cov=proserve',
                description='Run tests with coverage',
                example_output='Name                Stmts   Miss  Cover\nproserve/__init__.py    10      0   100%'
            )
        ])
        
        return commands
    
    def generate_deployment_commands(self) -> List[GeneratedCommand]:
        """Generate deployment commands"""
        commands = []
        
        deployment = self.manifest_data.get('deployment', {})
        target = deployment.get('target', 'local')
        
        if target == 'docker':
            commands.extend([
                GeneratedCommand(
                    type=CommandType.SHELL,
                    command='docker build -t proserve-app .',
                    description='Build Docker image'
                ),
                GeneratedCommand(
                    type=CommandType.SHELL,
                    command=f'docker run -p {self.server_config["port"]}:{self.server_config["port"]} proserve-app',
                    description='Run Docker container'
                )
            ])
        
        elif target == 'kubernetes':
            commands.extend([
                GeneratedCommand(
                    type=CommandType.SHELL,
                    command='kubectl apply -f k8s/',
                    description='Deploy to Kubernetes'
                ),
                GeneratedCommand(
                    type=CommandType.SHELL,
                    command='kubectl get pods -l app=proserve',
                    description='Check Kubernetes pods'
                )
            ])
        
        # Generic deployment commands
        commands.extend([
            GeneratedCommand(
                type=CommandType.SHELL,
                command='pip install -r requirements.txt',
                description='Install dependencies'
            ),
            GeneratedCommand(
                type=CommandType.SHELL,
                command='python -m proserve validate manifest.yml',
                description='Validate manifest before deployment'
            )
        ])
        
        return commands
    
    def get_commands_by_category(self, category: str) -> List[GeneratedCommand]:
        """Get commands for a specific category"""
        if category in self.categories:
            return self.categories[category].commands
        return []
    
    def get_all_categories(self) -> Dict[str, CommandCategory]:
        """Get all command categories"""
        return self.categories
    
    def export_commands(self, output_path: Union[str, Path], 
                       format_type: str = 'markdown',
                       commands: List[GeneratedCommand] = None) -> bool:
        """Export commands to file"""
        if commands is None:
            commands = self.generate_all()
        
        if format_type.lower() == 'markdown':
            return self.export_formatter.export_as_markdown(
                commands, output_path, f"{self.service_name} Commands"
            )
        elif format_type.lower() == 'json':
            return self.export_formatter.export_as_json(commands, output_path)
        elif format_type.lower() in ['bash', 'shell']:
            return self.export_formatter.export_as_script(commands, output_path, 'bash')
        elif format_type.lower() == 'powershell':
            return self.export_formatter.export_as_script(commands, output_path, 'powershell')
        elif format_type.lower() == 'python':
            return self.export_formatter.export_as_script(commands, output_path, 'python')
        elif format_type.lower() == 'postman':
            return self.export_formatter.export_as_postman_collection(
                commands, output_path, f"{self.service_name} API"
            )
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        return generate_openapi_spec(self.manifest_data, self.base_url)
    
    def get_command_summary(self) -> Dict[str, Any]:
        """Get summary of all generated commands"""
        all_commands = self.generate_all()
        
        summary = {
            'service_name': self.service_name,
            'base_url': self.base_url,
            'total_commands': len(all_commands),
            'commands_by_type': {},
            'commands_by_category': {}
        }
        
        # Count by type
        for cmd in all_commands:
            cmd_type = cmd.type.value
            summary['commands_by_type'][cmd_type] = summary['commands_by_type'].get(cmd_type, 0) + 1
        
        # Count by category
        for category_name, category in self.categories.items():
            summary['commands_by_category'][category_name] = len(category.commands)
        
        return summary


# Convenience functions for backward compatibility
def generate_commands_from_manifest(manifest_path: Union[str, Path]) -> List[GeneratedCommand]:
    """Generate commands from manifest file"""
    generator = CommandGenerator(manifest_path)
    return generator.generate_all()


def export_commands_as_script(manifest_path: Union[str, Path], 
                            output_path: Union[str, Path],
                            script_type: str = 'bash') -> bool:
    """Export commands as executable script"""
    generator = CommandGenerator(manifest_path)
    commands = generator.generate_all()
    return generator.export_formatter.export_as_script(commands, output_path, script_type)


def generate_documentation(manifest_path: Union[str, Path],
                         output_path: Union[str, Path],
                         format_type: str = 'markdown') -> bool:
    """Generate documentation from manifest"""
    generator = CommandGenerator(manifest_path)
    return generator.export_commands(output_path, format_type)
