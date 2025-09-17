"""
ProServe Shell Command Handler
Handles execution of shell commands for endpoints and data conversion
"""

import os
import json
import xml.etree.ElementTree as ET
import subprocess
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
import importlib.util
import tempfile
import yaml
import csv
from io import StringIO

logger = logging.getLogger(__name__)


class ShellCommandHandler:
    """Handler for executing shell commands and converting outputs"""
    
    def __init__(self, shell_config: Dict[str, Any] = None, converters: Dict[str, Dict[str, Any]] = None):
        self.shell_config = shell_config or {}
        self.converters = converters or {}
        self.default_timeout = self.shell_config.get('timeout', 30)
        self.default_shell = self.shell_config.get('shell', '/bin/bash')
        self.working_dir = self.shell_config.get('working_dir', os.getcwd())
        
        # Built-in converters
        self._builtin_converters = {
            'json': self._to_json,
            'xml': self._to_xml,
            'yaml': self._to_yaml,
            'csv': self._to_csv,
            'html': self._to_html,
            'plain': self._to_plain,
            'lines': self._to_lines,
            'docker_ps': self._docker_ps_to_json,
            'docker_images': self._docker_images_to_json,
            'systemctl': self._systemctl_to_json,
            'ps': self._ps_to_json,
            'df': self._df_to_json,
            'free': self._free_to_json,
            'netstat': self._netstat_to_json
        }
    
    async def execute_shell_command(
        self, 
        command: str, 
        parameters: Dict[str, Any] = None,
        converter: str = None,
        timeout: int = None,
        env_vars: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Execute shell command and optionally convert output
        
        Args:
            command: Shell command to execute
            parameters: Parameters to substitute in command
            converter: Output converter name
            timeout: Command timeout in seconds
            env_vars: Additional environment variables
            
        Returns:
            Dict containing command result and converted output
        """
        try:
            # Prepare command with parameters
            processed_command = self._process_command(command, parameters)
            
            # Set up environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Execute command
            result = await self._execute_command(
                processed_command, 
                timeout or self.default_timeout,
                env
            )
            
            # Convert output if converter specified
            converted_output = await self._convert_output(result['stdout'], converter)
            
            return {
                'success': result['returncode'] == 0,
                'command': processed_command,
                'returncode': result['returncode'],
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'converted_output': converted_output,
                'converter_used': converter,
                'execution_time': result.get('execution_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Shell command execution failed: {e}")
            return {
                'success': False,
                'command': command,
                'error': str(e),
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'converted_output': None,
                'converter_used': converter,
                'execution_time': 0
            }
    
    def _process_command(self, command: str, parameters: Dict[str, Any] = None) -> str:
        """Process command template with parameters"""
        if not parameters:
            return command
        
        try:
            # Simple parameter substitution
            for key, value in parameters.items():
                placeholder = f"{{{key}}}"
                if placeholder in command:
                    # Ensure proper shell escaping
                    escaped_value = str(value).replace("'", "'\"'\"'")
                    command = command.replace(placeholder, f"'{escaped_value}'")
            
            return command
        except Exception as e:
            logger.error(f"Command parameter processing failed: {e}")
            return command
    
    async def _execute_command(self, command: str, timeout: int, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute shell command asynchronously"""
        import time
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
                env=env,
                shell=True
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return {
                'returncode': process.returncode,
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'execution_time': execution_time
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Command timeout after {timeout}s: {command}")
            return {
                'returncode': -2,
                'stdout': '',
                'stderr': f'Command timeout after {timeout} seconds',
                'execution_time': timeout
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution error: {e}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': execution_time
            }
    
    async def _convert_output(self, output: str, converter: str = None) -> Any:
        """Convert shell command output to specified format"""
        if not converter or not output.strip():
            return output
        
        try:
            # Check for built-in converter
            if converter in self._builtin_converters:
                return await self._builtin_converters[converter](output)
            
            # Check for custom converter
            if converter in self.converters:
                return await self._apply_custom_converter(output, converter)
            
            logger.warning(f"Unknown converter: {converter}")
            return output
            
        except Exception as e:
            logger.error(f"Output conversion failed with {converter}: {e}")
            return {
                'error': f'Conversion failed: {str(e)}',
                'raw_output': output
            }
    
    async def _apply_custom_converter(self, output: str, converter_name: str) -> Any:
        """Apply custom converter function"""
        converter_config = self.converters[converter_name]
        
        if 'script' in converter_config:
            # Execute converter script
            return await self._execute_converter_script(output, converter_config['script'])
        elif 'function' in converter_config:
            # Call converter function
            return await self._call_converter_function(output, converter_config['function'])
        else:
            logger.error(f"Invalid converter config for {converter_name}")
            return output
    
    async def _execute_converter_script(self, output: str, script_path: str) -> Any:
        """Execute converter script with output as input"""
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(output)
                input_file = f.name
            
            # Execute converter script
            result = await self._execute_command(
                f"python3 '{script_path}' '{input_file}'",
                timeout=10,
                env=os.environ.copy()
            )
            
            # Clean up
            os.unlink(input_file)
            
            if result['returncode'] == 0:
                # Try to parse as JSON
                try:
                    return json.loads(result['stdout'])
                except json.JSONDecodeError:
                    return result['stdout']
            else:
                return {
                    'error': f"Converter script failed: {result['stderr']}",
                    'raw_output': output
                }
                
        except Exception as e:
            logger.error(f"Converter script execution failed: {e}")
            return {'error': str(e), 'raw_output': output}
    
    async def _call_converter_function(self, output: str, function_path: str) -> Any:
        """Call converter function dynamically"""
        try:
            # Import and call function
            module_path, function_name = function_path.rsplit('.', 1)
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                raise ImportError(f"Module {module_path} not found")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            converter_func = getattr(module, function_name)
            result = converter_func(output)
            
            # Handle async functions
            if asyncio.iscoroutine(result):
                result = await result
            
            return result
            
        except Exception as e:
            logger.error(f"Converter function call failed: {e}")
            return {'error': str(e), 'raw_output': output}
    
    # Built-in converters
    async def _to_json(self, output: str) -> Union[Dict, List, str]:
        """Convert output to JSON"""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Try to parse as key-value pairs
            lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
            result = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
            return result if result else {'raw': output}
    
    async def _to_xml(self, output: str) -> Dict[str, Any]:
        """Convert output to XML structure"""
        try:
            root = ET.fromstring(output)
            return {'root': self._xml_to_dict(root)}
        except ET.ParseError:
            # Wrap in XML
            return {'data': output}
    
    async def _to_yaml(self, output: str) -> Any:
        """Convert output to YAML"""
        try:
            return yaml.safe_load(output)
        except yaml.YAMLError:
            return {'raw': output}
    
    async def _to_csv(self, output: str) -> List[Dict[str, str]]:
        """Convert CSV output to list of dictionaries"""
        try:
            reader = csv.DictReader(StringIO(output))
            return list(reader)
        except Exception:
            # Try simple comma-separated parsing
            lines = output.strip().split('\n')
            if len(lines) < 2:
                return [{'raw': output}]
            
            headers = [h.strip() for h in lines[0].split(',')]
            result = []
            for line in lines[1:]:
                values = [v.strip() for v in line.split(',')]
                row = {}
                for i, header in enumerate(headers):
                    row[header] = values[i] if i < len(values) else ''
                result.append(row)
            return result
    
    async def _to_html(self, output: str) -> str:
        """Convert output to HTML"""
        return f"<pre>{output}</pre>"
    
    async def _to_plain(self, output: str) -> str:
        """Return plain text"""
        return output
    
    async def _to_lines(self, output: str) -> List[str]:
        """Convert output to list of lines"""
        return [line.strip() for line in output.strip().split('\n') if line.strip()]
    
    # Specialized converters for common commands
    async def _docker_ps_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert docker ps output to JSON"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = ['CONTAINER_ID', 'IMAGE', 'COMMAND', 'CREATED', 'STATUS', 'PORTS', 'NAMES']
        containers = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 7:
                container = {}
                for i, header in enumerate(headers):
                    container[header] = parts[i] if i < len(parts) else ''
                containers.append(container)
        
        return containers
    
    async def _docker_images_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert docker images output to JSON"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = ['REPOSITORY', 'TAG', 'IMAGE_ID', 'CREATED', 'SIZE']
        images = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                image = {}
                for i, header in enumerate(headers):
                    image[header] = parts[i] if i < len(parts) else ''
                images.append(image)
        
        return images
    
    async def _systemctl_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert systemctl status output to JSON"""
        lines = output.strip().split('\n')
        services = []
        
        for line in lines:
            if 'Active:' in line:
                parts = line.split()
                if len(parts) >= 2:
                    services.append({
                        'status': parts[1],
                        'description': ' '.join(parts[2:]) if len(parts) > 2 else ''
                    })
        
        return services
    
    async def _ps_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert ps output to JSON"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split()
        processes = []
        
        for line in lines[1:]:
            parts = line.split(None, len(headers) - 1)
            if len(parts) >= len(headers):
                process = {}
                for i, header in enumerate(headers):
                    process[header] = parts[i] if i < len(parts) else ''
                processes.append(process)
        
        return processes
    
    async def _df_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert df output to JSON"""
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = ['FILESYSTEM', 'SIZE', 'USED', 'AVAIL', 'USE%', 'MOUNTED_ON']
        filesystems = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                filesystem = {}
                for i, header in enumerate(headers):
                    filesystem[header] = parts[i] if i < len(parts) else ''
                filesystems.append(filesystem)
        
        return filesystems
    
    async def _free_to_json(self, output: str) -> Dict[str, Any]:
        """Convert free memory output to JSON"""
        lines = output.strip().split('\n')
        result = {}
        
        for line in lines:
            if 'Mem:' in line:
                parts = line.split()
                if len(parts) >= 7:
                    result['memory'] = {
                        'total': parts[1],
                        'used': parts[2],
                        'free': parts[3],
                        'shared': parts[4],
                        'buff_cache': parts[5],
                        'available': parts[6]
                    }
            elif 'Swap:' in line:
                parts = line.split()
                if len(parts) >= 4:
                    result['swap'] = {
                        'total': parts[1],
                        'used': parts[2],
                        'free': parts[3]
                    }
        
        return result
    
    async def _netstat_to_json(self, output: str) -> List[Dict[str, str]]:
        """Convert netstat output to JSON"""
        lines = output.strip().split('\n')
        connections = []
        
        for line in lines:
            if 'tcp' in line.lower() or 'udp' in line.lower():
                parts = line.split()
                if len(parts) >= 6:
                    connections.append({
                        'proto': parts[0],
                        'recv_q': parts[1],
                        'send_q': parts[2],
                        'local_address': parts[3],
                        'foreign_address': parts[4],
                        'state': parts[5] if len(parts) > 5 else ''
                    })
        
        return connections
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary"""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_dict = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        
        return result
