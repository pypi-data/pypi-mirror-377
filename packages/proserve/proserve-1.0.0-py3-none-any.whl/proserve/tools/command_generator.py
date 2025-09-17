"""
ProServe Command Generator
Generate shell commands, REST API calls, and gRPC client code from manifests
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from ..core.manifest import ServiceManifest


@dataclass
class GeneratedCommand:
    """Represents a generated command"""
    type: str  # shell, curl, grpc, python
    command: str
    description: str
    example_output: Optional[str] = None
    language: str = 'bash'


class CommandGenerator:
    """Generate commands from ProServe manifests"""
    
    def __init__(self, manifest: Union[ServiceManifest, Dict[str, Any], str, Path]):
        if isinstance(manifest, (str, Path)):
            # Load from file
            content = Path(manifest).read_text()
            if str(manifest).endswith(('.yml', '.yaml')):
                self.manifest_data = yaml.safe_load(content)
            else:
                self.manifest_data = json.loads(content)
        elif isinstance(manifest, ServiceManifest):
            from dataclasses import asdict
            self.manifest_data = asdict(manifest)
        else:
            self.manifest_data = manifest
            
        self.service_name = self.manifest_data.get('name', 'service')
        self.server_config = self.manifest_data.get('server', {'host': 'localhost', 'port': 8000})
        self.base_url = f"http://{self.server_config['host']}:{self.server_config['port']}"
        
    def generate_all(self) -> List[GeneratedCommand]:
        """Generate all types of commands"""
        commands = []
        
        # Service management commands
        commands.extend(self.generate_service_commands())
        
        # HTTP endpoint commands
        commands.extend(self.generate_http_commands())
        
        # gRPC commands
        commands.extend(self.generate_grpc_commands())
        
        # Database commands
        commands.extend(self.generate_database_commands())
        
        # Monitoring commands
        commands.extend(self.generate_monitoring_commands())
        
        return commands
        
    def generate_service_commands(self) -> List[GeneratedCommand]:
        """Generate service lifecycle commands"""
        commands = []
        
        # Start service
        commands.append(GeneratedCommand(
            type='shell',
            command=f'python -m proserve manifest.yml',
            description='Start ProServe service',
            example_output='Service started on http://localhost:8000'
        ))
        
        # Start in development mode
        commands.append(GeneratedCommand(
            type='shell', 
            command=f'python -m proserve manifest.yml --dev --reload',
            description='Start service in development mode with auto-reload',
            example_output='Development server started with auto-reload enabled'
        ))
        
        # Health check
        commands.append(GeneratedCommand(
            type='curl',
            command=f'curl -X GET {self.base_url}/health',
            description='Check service health',
            example_output='{"status": "healthy", "service": "' + self.service_name + '"}'
        ))
        
        # Service info
        commands.append(GeneratedCommand(
            type='curl',
            command=f'curl -X GET {self.base_url}/info',
            description='Get service information',
            example_output='{"name": "' + self.service_name + '", "version": "1.0.0"}'
        ))
        
        return commands
        
    def generate_http_commands(self) -> List[GeneratedCommand]:
        """Generate HTTP endpoint commands"""
        commands = []
        endpoints = self.manifest_data.get('endpoints', [])
        
        for endpoint in endpoints:
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'get').upper()
            
            # cURL command
            if method == 'GET':
                curl_cmd = f'curl -X GET {self.base_url}{path}'
            elif method == 'POST':
                curl_cmd = f'curl -X POST {self.base_url}{path} -H "Content-Type: application/json" -d \'{{"key": "value"}}\''
            elif method == 'PUT':
                curl_cmd = f'curl -X PUT {self.base_url}{path} -H "Content-Type: application/json" -d \'{{"key": "updated_value"}}\''
            elif method == 'DELETE':
                curl_cmd = f'curl -X DELETE {self.base_url}{path}'
            else:
                curl_cmd = f'curl -X {method} {self.base_url}{path}'
                
            commands.append(GeneratedCommand(
                type='curl',
                command=curl_cmd,
                description=f'{method} {path} endpoint',
                example_output='{"result": "success"}'
            ))
            
            # Python requests command
            python_cmd = self._generate_python_request(method, path)
            commands.append(GeneratedCommand(
                type='python',
                command=python_cmd,
                description=f'Python request to {method} {path}',
                language='python'
            ))
            
        return commands
        
    def _generate_python_request(self, method: str, path: str) -> str:
        """Generate Python requests code"""
        base_code = f'''import requests

url = "{self.base_url}{path}"
'''
        
        if method.upper() == 'GET':
            code = base_code + f'''response = requests.get(url)
print(response.json())'''
        elif method.upper() in ['POST', 'PUT']:
            code = base_code + f'''data = {{"key": "value"}}
response = requests.{method.lower()}(url, json=data)
print(response.json())'''
        elif method.upper() == 'DELETE':
            code = base_code + f'''response = requests.delete(url)
print(response.json())'''
        else:
            code = base_code + f'''response = requests.request("{method.upper()}", url)
print(response.json())'''
            
        return code
        
    def generate_grpc_commands(self) -> List[GeneratedCommand]:
        """Generate gRPC client commands"""
        commands = []
        
        # Check if gRPC is configured
        grpc_port = self.manifest_data.get('grpc_port')
        grpc_services = self.manifest_data.get('grpc_services', [])
        
        if not grpc_port and not grpc_services:
            return commands
            
        grpc_port = grpc_port or 50051
        grpc_host = self.server_config.get('host', 'localhost')
        
        # gRPC server info using grpcurl
        commands.append(GeneratedCommand(
            type='grpc',
            command=f'grpcurl -plaintext {grpc_host}:{grpc_port} list',
            description='List available gRPC services',
            example_output='grpc.health.v1.Health\nmyservice.UserService'
        ))
        
        # Health check
        commands.append(GeneratedCommand(
            type='grpc', 
            command=f'grpcurl -plaintext {grpc_host}:{grpc_port} grpc.health.v1.Health/Check',
            description='gRPC health check',
            example_output='{"status": "SERVING"}'
        ))
        
        # Generate commands for each gRPC service
        for service in grpc_services:
            service_name = service.get('name', 'Service')
            package = service.get('package', '')
            full_name = f"{package}.{service_name}" if package else service_name
            
            # List service methods
            commands.append(GeneratedCommand(
                type='grpc',
                command=f'grpcurl -plaintext {grpc_host}:{grpc_port} list {full_name}',
                description=f'List methods for {service_name}',
                example_output=f'{full_name}.GetUser\n{full_name}.ListUsers'
            ))
            
            # Generate method calls
            methods = service.get('methods', [])
            for method in methods:
                method_name = method.get('name')
                full_method = f"{full_name}.{method_name}"
                
                commands.append(GeneratedCommand(
                    type='grpc',
                    command=f'grpcurl -plaintext -d \'{{"id": 1}}\' {grpc_host}:{grpc_port} {full_method}',
                    description=f'Call {method_name} method',
                    example_output='{"id": 1, "name": "John Doe"}'
                ))
                
                # Python gRPC client code
                python_grpc = self._generate_python_grpc_client(grpc_host, grpc_port, full_method)
                commands.append(GeneratedCommand(
                    type='python',
                    command=python_grpc,
                    description=f'Python gRPC client for {method_name}',
                    language='python'
                ))
                
        return commands
        
    def _generate_python_grpc_client(self, host: str, port: int, method: str) -> str:
        """Generate Python gRPC client code"""
        return f'''import grpc
import json

# Generated gRPC client for {method}
def call_grpc_method():
    channel = grpc.insecure_channel('{host}:{port}')
    
    # TODO: Import the generated client stub
    # stub = YourServiceStub(channel)
    
    # TODO: Create request message
    # request = YourRequest(id=1)
    
    # TODO: Make the call
    # response = stub.{method.split('.')[-1]}(request)
    
    print("gRPC call completed")
    
if __name__ == "__main__":
    call_grpc_method()'''
    
    def generate_database_commands(self) -> List[GeneratedCommand]:
        """Generate database-related commands"""
        commands = []
        db_config = self.manifest_data.get('database')
        
        if not db_config:
            return commands
            
        db_type = db_config.get('type', 'postgresql')
        db_url = db_config.get('url', f'{db_type}://localhost:5432/db')
        
        if db_type == 'postgresql':
            # PostgreSQL commands
            commands.append(GeneratedCommand(
                type='shell',
                command=f'psql "{db_url}" -c "SELECT version();"',
                description='Test PostgreSQL connection',
                example_output='PostgreSQL 14.5 on x86_64-pc-linux-gnu'
            ))
            
            commands.append(GeneratedCommand(
                type='shell',
                command=f'pg_dump "{db_url}" > backup.sql',
                description='Create database backup',
                example_output='Database backup created: backup.sql'
            ))
            
        elif db_type == 'mysql':
            # MySQL commands  
            commands.append(GeneratedCommand(
                type='shell',
                command='mysql -u username -p -e "SELECT VERSION();"',
                description='Test MySQL connection',
                example_output='8.0.30-0ubuntu0.22.04.1'
            ))
            
        elif db_type == 'redis':
            # Redis commands
            commands.append(GeneratedCommand(
                type='shell',
                command='redis-cli ping',
                description='Test Redis connection', 
                example_output='PONG'
            ))
            
            commands.append(GeneratedCommand(
                type='shell',
                command='redis-cli info server',
                description='Get Redis server info',
                example_output='redis_version:7.0.4'
            ))
            
        # Python database connection
        python_db = self._generate_python_db_connection(db_type, db_url)
        commands.append(GeneratedCommand(
            type='python',
            command=python_db,
            description=f'Python {db_type} connection test',
            language='python'
        ))
        
        return commands
        
    def _generate_python_db_connection(self, db_type: str, db_url: str) -> str:
        """Generate Python database connection code"""
        if db_type == 'postgresql':
            return f'''import asyncpg
import asyncio

async def test_postgres():
    conn = await asyncpg.connect("{db_url}")
    version = await conn.fetchval("SELECT version()")
    print(f"PostgreSQL version: {{version}}")
    await conn.close()

asyncio.run(test_postgres())'''
        elif db_type == 'mysql':
            return f'''import aiomysql
import asyncio

async def test_mysql():
    conn = await aiomysql.connect(host='localhost', port=3306,
                                 user='user', password='password', db='database')
    cursor = await conn.cursor()
    await cursor.execute("SELECT VERSION()")
    version = await cursor.fetchone()
    print(f"MySQL version: {{version[0]}}")
    conn.close()

asyncio.run(test_mysql())'''
        elif db_type == 'redis':
            return f'''import aioredis
import asyncio

async def test_redis():
    redis = aioredis.from_url("{db_url}")
    pong = await redis.ping()
    print(f"Redis ping: {{pong}}")
    await redis.close()

asyncio.run(test_redis())'''
        else:
            return f'''# Database connection code for {db_type}
# TODO: Implement connection for {db_type}
print("Database type: {db_type}")'''
    
    def generate_monitoring_commands(self) -> List[GeneratedCommand]:
        """Generate monitoring and observability commands"""
        commands = []
        
        # Metrics endpoint
        metrics_endpoint = self.manifest_data.get('metrics', {}).get('endpoint', '/metrics')
        commands.append(GeneratedCommand(
            type='curl',
            command=f'curl -X GET {self.base_url}{metrics_endpoint}',
            description='Get Prometheus metrics',
            example_output='# HELP http_requests_total Total HTTP requests\nhttp_requests_total{{method="GET"}} 42'
        ))
        
        # Health endpoint
        health_endpoint = self.manifest_data.get('health', {}).get('endpoint', '/health')
        commands.append(GeneratedCommand(
            type='curl',
            command=f'curl -X GET {self.base_url}{health_endpoint}',
            description='Detailed health check',
            example_output='{"status": "healthy", "checks": {"database": "ok", "external_api": "ok"}}'
        ))
        
        # Log monitoring (if file logging is configured)
        logging_config = self.manifest_data.get('logging', {})
        handlers = logging_config.get('handlers', [])
        
        for handler in handlers:
            if handler.get('type') == 'file':
                filename = handler.get('filename', f'{self.service_name}.log')
                commands.append(GeneratedCommand(
                    type='shell',
                    command=f'tail -f {filename}',
                    description='Follow log file in real-time',
                    example_output='2023-01-01 12:00:00 INFO Starting service...'
                ))
                
                commands.append(GeneratedCommand(
                    type='shell',
                    command=f'grep ERROR {filename} | tail -10',
                    description='Show recent errors from logs',
                    example_output='2023-01-01 12:05:30 ERROR Database connection failed'
                ))
        
        # Docker commands if deployment is configured
        deployment = self.manifest_data.get('deployment', {})
        if deployment.get('target') == 'docker':
            commands.append(GeneratedCommand(
                type='shell',
                command=f'docker logs -f {self.service_name}',
                description='Follow Docker container logs',
                example_output='Service started successfully'
            ))
            
            commands.append(GeneratedCommand(
                type='shell',
                command=f'docker stats {self.service_name}',
                description='Monitor container resource usage',
                example_output='CONTAINER CPU % MEM USAGE / LIMIT MEM % NET I/O'
            ))
            
        return commands
        
    def export_as_script(self, commands: List[GeneratedCommand], 
                        script_type: str = 'bash') -> str:
        """Export commands as executable script"""
        if script_type == 'bash':
            return self._export_bash_script(commands)
        elif script_type == 'python':
            return self._export_python_script(commands)
        else:
            raise ValueError(f"Unsupported script type: {script_type}")
            
    def _export_bash_script(self, commands: List[GeneratedCommand]) -> str:
        """Export as bash script"""
        script = f'''#!/bin/bash
# Generated commands for {self.service_name}
# ProServe Command Generator

set -e  # Exit on error

echo "ProServe Service Commands for {self.service_name}"
echo "=============================================="

'''
        
        for cmd in commands:
            if cmd.type in ['shell', 'curl', 'grpc']:
                script += f'''
# {cmd.description}
echo "Running: {cmd.description}"
{cmd.command}
echo ""
'''
        
        return script
        
    def _export_python_script(self, commands: List[GeneratedCommand]) -> str:
        """Export as Python script"""
        script = f'''#!/usr/bin/env python3
"""
Generated Python client for {self.service_name}
ProServe Command Generator
"""

import requests
import json
import subprocess
import sys

BASE_URL = "{self.base_url}"

def run_command(cmd, description):
    """Run shell command with description"""
    print(f"Running: {{description}}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {{result.stderr}}")
    except Exception as e:
        print(f"Failed to run command: {{e}}")
    print()

def make_http_request(method, path, data=None):
    """Make HTTP request"""
    url = f"{{BASE_URL}}{{path}}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        else:
            response = requests.request(method, url, json=data)
            
        print(f"{{method.upper()}} {{path}}: {{response.status_code}}")
        if response.headers.get('content-type', '').startswith('application/json'):
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)
    except Exception as e:
        print(f"HTTP request failed: {{e}}")
    print()

def main():
    """Main function with all generated commands"""
    print(f"ProServe Service Client for {self.service_name}")
    print("=" * 50)
    
'''
        
        # Add HTTP commands as functions
        for cmd in commands:
            if cmd.type == 'curl' and 'curl' in cmd.command:
                # Parse curl command to Python
                method, path = self._parse_curl_command(cmd.command)
                script += f'''    # {cmd.description}
    make_http_request("{method}", "{path}")
    
'''
        
        script += '''
if __name__ == "__main__":
    main()
'''
        
        return script
        
    def _parse_curl_command(self, curl_cmd: str) -> tuple:
        """Parse curl command to extract method and path"""
        # Simple parsing - could be enhanced
        if '-X GET' in curl_cmd or ('curl' in curl_cmd and '-X' not in curl_cmd):
            method = 'GET'
        elif '-X POST' in curl_cmd:
            method = 'POST'
        elif '-X PUT' in curl_cmd:
            method = 'PUT'
        elif '-X DELETE' in curl_cmd:
            method = 'DELETE'
        else:
            method = 'GET'
            
        # Extract path from URL
        import re
        url_match = re.search(r'https?://[^/]+(/[^\s]*)', curl_cmd)
        path = url_match.group(1) if url_match else '/'
        
        return method, path
        
    def generate_documentation(self, format: str = 'markdown') -> str:
        """Generate documentation for all commands"""
        if format == 'markdown':
            return self._generate_markdown_docs()
        elif format == 'html':
            return self._generate_html_docs()
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_markdown_docs(self) -> str:
        """Generate Markdown documentation"""
        commands = self.generate_all()
        
        doc = f'''# {self.service_name} - Generated Commands

This documentation contains auto-generated commands for testing and interacting with the {self.service_name} service.

## Service Information

- **Name**: {self.service_name}
- **Base URL**: {self.base_url}
- **Generated**: {str(Path.cwd())}

## Available Commands

'''
        
        # Group commands by type
        grouped = {}
        for cmd in commands:
            if cmd.type not in grouped:
                grouped[cmd.type] = []
            grouped[cmd.type].append(cmd)
            
        for cmd_type, type_commands in grouped.items():
            doc += f'\n### {cmd_type.upper()} Commands\n\n'
            
            for cmd in type_commands:
                doc += f'''#### {cmd.description}

```{cmd.language}
{cmd.command}
```

'''
                if cmd.example_output:
                    doc += f'''**Example Output:**
```
{cmd.example_output}
```

'''
                    
        return doc
        
    def _generate_html_docs(self) -> str:
        """Generate HTML documentation"""
        commands = self.generate_all()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{self.service_name} - Generated Commands</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .command {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-left: 4px solid #007acc; }}
        .command-type {{ background: #007acc; color: white; padding: 5px 10px; margin: 10px 0; }}
        pre {{ background: #f0f0f0; padding: 10px; overflow: auto; }}
        .example {{ background: #e8f4f8; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{self.service_name} - Generated Commands</h1>
    <p>Auto-generated commands for testing and interacting with the {self.service_name} service.</p>
    
    <h2>Service Information</h2>
    <ul>
        <li><strong>Name:</strong> {self.service_name}</li>
        <li><strong>Base URL:</strong> {self.base_url}</li>
    </ul>
'''
        
        # Group and display commands
        grouped = {}
        for cmd in commands:
            if cmd.type not in grouped:
                grouped[cmd.type] = []
            grouped[cmd.type].append(cmd)
            
        for cmd_type, type_commands in grouped.items():
            html += f'<div class="command-type">{cmd_type.upper()} Commands</div>'
            
            for cmd in type_commands:
                html += f'''
                <div class="command">
                    <h3>{cmd.description}</h3>
                    <pre><code>{cmd.command}</code></pre>
'''
                if cmd.example_output:
                    html += f'''
                    <div class="example">
                        <strong>Example Output:</strong>
                        <pre>{cmd.example_output}</pre>
                    </div>
'''
                html += '</div>'
                
        html += '''
</body>
</html>'''
        
        return html


# Convenience functions
def generate_commands_from_manifest(manifest_path: Union[str, Path]) -> List[GeneratedCommand]:
    """Generate commands from manifest file"""
    generator = CommandGenerator(manifest_path)
    return generator.generate_all()


def export_commands_as_script(manifest_path: Union[str, Path], 
                            output_path: Union[str, Path],
                            script_type: str = 'bash') -> None:
    """Export commands as executable script"""
    generator = CommandGenerator(manifest_path)
    commands = generator.generate_all()
    script_content = generator.export_as_script(commands, script_type)
    
    Path(output_path).write_text(script_content)
    
    # Make executable if bash script
    if script_type == 'bash':
        import stat
        Path(output_path).chmod(Path(output_path).stat().st_mode | stat.S_IEXEC)


def generate_documentation(manifest_path: Union[str, Path],
                         output_path: Union[str, Path],
                         format: str = 'markdown') -> None:
    """Generate documentation from manifest"""
    generator = CommandGenerator(manifest_path)
    docs = generator.generate_documentation(format)
    Path(output_path).write_text(docs)
