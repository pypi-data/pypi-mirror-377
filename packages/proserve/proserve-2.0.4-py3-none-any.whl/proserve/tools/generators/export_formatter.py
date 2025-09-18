"""
ProServe Export Formatter - Command Export and Documentation Generation
Formats and exports generated commands to various formats (scripts, documentation, etc.)
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .command_types import GeneratedCommand, CommandType, CommandLanguage, CommandCategory


class ExportFormatter:
    """Formats and exports generated commands to various formats"""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
    
    def export_as_script(self, commands: List[GeneratedCommand], 
                        output_path: Union[str, Path], 
                        script_type: str = 'bash') -> bool:
        """Export commands as executable script"""
        try:
            output_path = Path(output_path)
            
            if script_type.lower() == 'bash':
                content = self._generate_bash_script(commands)
            elif script_type.lower() == 'powershell':
                content = self._generate_powershell_script(commands)
            elif script_type.lower() == 'python':
                content = self._generate_python_script(commands)
            else:
                raise ValueError(f"Unsupported script type: {script_type}")
            
            with open(output_path, 'w') as f:
                f.write(content)
            
            # Make script executable on Unix systems
            if script_type.lower() in ['bash'] and hasattr(output_path, 'chmod'):
                output_path.chmod(0o755)
            
            return True
            
        except Exception as e:
            print(f"Error exporting script: {e}")
            return False
    
    def export_as_markdown(self, commands: List[GeneratedCommand], 
                          output_path: Union[str, Path],
                          title: str = "API Commands") -> bool:
        """Export commands as Markdown documentation"""
        try:
            output_path = Path(output_path)
            content = self._generate_markdown_docs(commands, title)
            
            with open(output_path, 'w') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error exporting markdown: {e}")
            return False
    
    def export_as_json(self, commands: List[GeneratedCommand], 
                      output_path: Union[str, Path]) -> bool:
        """Export commands as JSON"""
        try:
            output_path = Path(output_path)
            
            data = {
                'generated_at': self.timestamp,
                'total_commands': len(commands),
                'commands': [cmd.to_dict() for cmd in commands]
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    def export_as_postman_collection(self, commands: List[GeneratedCommand], 
                                   output_path: Union[str, Path],
                                   collection_name: str = "ProServe API") -> bool:
        """Export HTTP commands as Postman collection"""
        try:
            output_path = Path(output_path)
            
            # Filter HTTP commands
            http_commands = [cmd for cmd in commands if cmd.type in [CommandType.CURL, CommandType.HTTP]]
            
            collection = self._generate_postman_collection(http_commands, collection_name)
            
            with open(output_path, 'w') as f:
                json.dump(collection, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting Postman collection: {e}")
            return False
    
    def _generate_bash_script(self, commands: List[GeneratedCommand]) -> str:
        """Generate bash script from commands"""
        lines = [
            "#!/bin/bash",
            "#",
            "# ProServe Generated Commands Script",
            f"# Generated at: {self.timestamp}",
            "#",
            "",
            "set -e  # Exit on error",
            "",
            "# Configuration",
            "BASE_URL=${BASE_URL:-http://localhost:8000}",
            "API_TOKEN=${API_TOKEN:-}",
            "",
            "# Functions",
            "log() {",
            "    echo \"[$(date '+%Y-%m-%d %H:%M:%S')] $1\"",
            "}",
            "",
            "check_dependencies() {",
            "    command -v curl >/dev/null 2>&1 || { echo 'curl is required but not installed. Aborting.' >&2; exit 1; }",
            "}",
            "",
            "# Check dependencies",
            "check_dependencies",
            "",
            "# Generated Commands",
            ""
        ]
        
        # Group commands by type
        shell_commands = [cmd for cmd in commands if cmd.type == CommandType.SHELL]
        curl_commands = [cmd for cmd in commands if cmd.type == CommandType.CURL]
        
        # Add shell commands
        if shell_commands:
            lines.append("# Service Management Commands")
            for i, cmd in enumerate(shell_commands):
                function_name = f"command_{i+1}"
                lines.extend([
                    f"{function_name}() {{",
                    f"    log \"Running: {cmd.description}\"",
                    f"    {cmd.command}",
                    "}",
                    ""
                ])
        
        # Add API commands
        if curl_commands:
            lines.append("# API Commands")
            for i, cmd in enumerate(curl_commands):
                function_name = f"api_command_{i+1}"
                lines.extend([
                    f"{function_name}() {{",
                    f"    log \"API Call: {cmd.description}\"",
                    f"    {cmd.command}",
                    "}",
                    ""
                ])
        
        # Add usage function
        lines.extend([
            "usage() {",
            "    echo \"Usage: $0 [command]\"",
            "    echo \"Available commands:\"",
        ])
        
        for i, cmd in enumerate(commands):
            if cmd.type == CommandType.SHELL:
                lines.append(f"    echo \"  command_{i+1} - {cmd.description}\"")
            elif cmd.type == CommandType.CURL:
                lines.append(f"    echo \"  api_command_{i+1} - {cmd.description}\"")
        
        lines.extend([
            "}",
            "",
            "# Main script logic",
            "if [ $# -eq 0 ]; then",
            "    usage",
            "    exit 1",
            "fi",
            "",
            "case \"$1\" in"
        ])
        
        # Add case statements
        for i, cmd in enumerate(commands):
            if cmd.type == CommandType.SHELL:
                lines.append(f"    command_{i+1}) command_{i+1} ;;")
            elif cmd.type == CommandType.CURL:
                lines.append(f"    api_command_{i+1}) api_command_{i+1} ;;")
        
        lines.extend([
            "    *) usage; exit 1 ;;",
            "esac"
        ])
        
        return '\n'.join(lines)
    
    def _generate_powershell_script(self, commands: List[GeneratedCommand]) -> str:
        """Generate PowerShell script from commands"""
        lines = [
            "# ProServe Generated Commands Script",
            f"# Generated at: {self.timestamp}",
            "",
            "param(",
            "    [string]$BaseUrl = 'http://localhost:8000',",
            "    [string]$ApiToken = ''",
            ")",
            "",
            "# Configuration",
            "$ErrorActionPreference = 'Stop'",
            "",
            "# Functions",
            "function Write-Log {",
            "    param([string]$Message)",
            "    Write-Host \"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message\"",
            "}",
            "",
            "function Test-Dependencies {",
            "    if (-not (Get-Command curl -ErrorAction SilentlyContinue)) {",
            "        Write-Error 'curl is required but not installed'",
            "        exit 1",
            "    }",
            "}",
            "",
            "# Check dependencies",
            "Test-Dependencies",
            "",
            "# Generated Commands",
            ""
        ]
        
        # Add PowerShell functions for each command
        for i, cmd in enumerate(commands):
            function_name = f"Invoke-Command{i+1}"
            
            # Convert curl commands to PowerShell
            if cmd.type == CommandType.CURL:
                ps_command = self._convert_curl_to_powershell(cmd.command)
            else:
                ps_command = cmd.command
            
            lines.extend([
                f"function {function_name} {{",
                f"    Write-Log \"Running: {cmd.description}\"",
                f"    {ps_command}",
                "}",
                ""
            ])
        
        return '\n'.join(lines)
    
    def _generate_python_script(self, commands: List[GeneratedCommand]) -> str:
        """Generate Python script from commands"""
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            "ProServe Generated Commands Script",
            f"Generated at: {self.timestamp}",
            '"""',
            "",
            "import requests",
            "import subprocess",
            "import sys",
            "import os",
            "from datetime import datetime",
            "",
            "# Configuration",
            "BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')",
            "API_TOKEN = os.getenv('API_TOKEN', '')",
            "",
            "def log(message):",
            '    print(f"[{datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}] {message}")',
            "",
            "def check_dependencies():",
            '    """Check if required dependencies are available"""',
            "    try:",
            "        import requests",
            "    except ImportError:",
            '        print("Error: requests library is required. Install with: pip install requests")',
            "        sys.exit(1)",
            "",
            "# Generated Commands",
            ""
        ]
        
        # Add Python functions for each command
        for i, cmd in enumerate(commands):
            function_name = f"command_{i+1}"
            
            if cmd.type == CommandType.PYTHON:
                # Use the Python command directly
                cmd_lines = cmd.command.split('\n')
                lines.extend([
                    f"def {function_name}():",
                    f'    """Run: {cmd.description}"""',
                    f'    log("Running: {cmd.description}")',
                ] + [f"    {line}" for line in cmd_lines if line.strip()] + ["", ""])
            
            elif cmd.type == CommandType.CURL:
                # Convert curl to requests
                lines.extend([
                    f"def {function_name}():",
                    f'    """Run: {cmd.description}"""',
                    f'    log("Running: {cmd.description}")',
                    f"    # Original curl: {cmd.command}",
                    f"    # TODO: Convert to requests call",
                    f'    print("Command not yet converted to Python")',
                    ""
                ])
            
            else:
                # Shell command
                lines.extend([
                    f"def {function_name}():",
                    f'    """Run: {cmd.description}"""',
                    f'    log("Running: {cmd.description}")',
                    f'    subprocess.run([{repr(cmd.command)}], shell=True, check=True)',
                    ""
                ])
        
        # Add main function
        lines.extend([
            "def main():",
            "    check_dependencies()",
            "",
            '    if len(sys.argv) < 2:',
            '        print("Usage: python script.py <command_number>")',
            '        print("Available commands:")',
        ])
        
        for i, cmd in enumerate(commands):
            lines.append(f'        print(f"  {i+1}: {cmd.description}")')
        
        lines.extend([
            "        sys.exit(1)",
            "",
            "    command_num = int(sys.argv[1])",
        ])
        
        # Add command dispatch
        for i, cmd in enumerate(commands):
            lines.append(f"    if command_num == {i+1}: command_{i+1}()")
        
        lines.extend([
            "",
            'if __name__ == "__main__":',
            "    main()"
        ])
        
        return '\n'.join(lines)
    
    def _generate_markdown_docs(self, commands: List[GeneratedCommand], title: str) -> str:
        """Generate Markdown documentation from commands"""
        lines = [
            f"# {title}",
            "",
            f"Generated on: {self.timestamp}",
            "",
            "This document contains generated commands for interacting with the ProServe service.",
            "",
            "## Table of Contents",
            ""
        ]
        
        # Group commands by type
        command_groups = {}
        for cmd in commands:
            cmd_type = cmd.type.value
            if cmd_type not in command_groups:
                command_groups[cmd_type] = []
            command_groups[cmd_type].append(cmd)
        
        # Add table of contents
        for cmd_type in command_groups:
            lines.append(f"- [{cmd_type.title()} Commands](#{cmd_type.lower()}-commands)")
        
        lines.append("")
        
        # Add sections for each command type
        for cmd_type, cmds in command_groups.items():
            lines.extend([
                f"## {cmd_type.title()} Commands",
                ""
            ])
            
            for i, cmd in enumerate(cmds, 1):
                lines.extend([
                    f"### {i}. {cmd.description}",
                    "",
                    "```" + cmd.language.value,
                    cmd.command,
                    "```",
                    ""
                ])
                
                if cmd.example_output:
                    lines.extend([
                        "**Example Output:**",
                        "",
                        "```json",
                        cmd.example_output,
                        "```",
                        ""
                    ])
        
        return '\n'.join(lines)
    
    def _generate_postman_collection(self, commands: List[GeneratedCommand], 
                                   collection_name: str) -> Dict[str, Any]:
        """Generate Postman collection from HTTP commands"""
        collection = {
            "info": {
                "name": collection_name,
                "description": f"Generated Postman collection - {self.timestamp}",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        for cmd in commands:
            if cmd.type == CommandType.CURL:
                item = self._curl_to_postman_item(cmd)
                if item:
                    collection["item"].append(item)
        
        return collection
    
    def _curl_to_postman_item(self, cmd: GeneratedCommand) -> Optional[Dict[str, Any]]:
        """Convert cURL command to Postman collection item"""
        try:
            # Parse cURL command (simplified parsing)
            command = cmd.command
            
            # Extract method
            if '-X GET' in command or 'curl' in command and '-X' not in command:
                method = 'GET'
            elif '-X POST' in command:
                method = 'POST'
            elif '-X PUT' in command:
                method = 'PUT'
            elif '-X DELETE' in command:
                method = 'DELETE'
            else:
                method = 'GET'
            
            # Extract URL (simplified)
            import re
            url_match = re.search(r'(https?://[^\s]+)', command)
            if not url_match:
                return None
            
            url = url_match.group(1)
            
            item = {
                "name": cmd.description,
                "request": {
                    "method": method,
                    "header": [],
                    "url": {
                        "raw": url,
                        "protocol": "http" if url.startswith("http://") else "https",
                        "host": [url.split('://')[1].split('/')[0]],
                        "path": url.split('://')[1].split('/')[1:] if '/' in url.split('://')[1] else []
                    }
                }
            }
            
            # Extract headers
            header_matches = re.findall(r'-H\s+"([^"]+)"', command)
            for header in header_matches:
                if ':' in header:
                    key, value = header.split(':', 1)
                    item["request"]["header"].append({
                        "key": key.strip(),
                        "value": value.strip()
                    })
            
            # Extract body data for POST/PUT
            if method in ['POST', 'PUT']:
                data_match = re.search(r"-d\s+'([^']+)'", command)
                if data_match:
                    item["request"]["body"] = {
                        "mode": "raw",
                        "raw": data_match.group(1),
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
            
            return item
            
        except Exception:
            return None
    
    def _convert_curl_to_powershell(self, curl_command: str) -> str:
        """Convert cURL command to PowerShell Invoke-RestMethod"""
        # Simplified conversion
        if '-X GET' in curl_command or ('-X' not in curl_command and 'GET' not in curl_command):
            method = 'Get'
        elif '-X POST' in curl_command:
            method = 'Post'
        elif '-X PUT' in curl_command:
            method = 'Put'
        elif '-X DELETE' in curl_command:
            method = 'Delete'
        else:
            method = 'Get'
        
        # Extract URL
        import re
        url_match = re.search(r'(https?://[^\s]+)', curl_command)
        if url_match:
            url = url_match.group(1)
            return f"Invoke-RestMethod -Uri '{url}' -Method {method}"
        
        return curl_command  # Fallback


def export_commands_as_script(commands: List[GeneratedCommand], 
                            output_path: Union[str, Path],
                            script_type: str = 'bash') -> bool:
    """Convenience function to export commands as script"""
    formatter = ExportFormatter()
    return formatter.export_as_script(commands, output_path, script_type)


def export_commands_as_markdown(commands: List[GeneratedCommand], 
                              output_path: Union[str, Path],
                              title: str = "API Commands") -> bool:
    """Convenience function to export commands as Markdown"""
    formatter = ExportFormatter()
    return formatter.export_as_markdown(commands, output_path, title)
