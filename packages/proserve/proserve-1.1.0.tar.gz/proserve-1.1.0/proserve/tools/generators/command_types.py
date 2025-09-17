"""
ProServe Command Types - Command Data Structures and Base Classes
Defines command types and base classes for command generation
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class CommandType(Enum):
    """Types of commands that can be generated"""
    SHELL = "shell"
    CURL = "curl"  
    GRPC = "grpc"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    HTTP = "http"
    SQL = "sql"


class CommandLanguage(Enum):
    """Programming languages for code generation"""
    BASH = "bash"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    POWERSHELL = "powershell"
    ZSH = "zsh"
    FISH = "fish"


@dataclass
class GeneratedCommand:
    """Represents a generated command"""
    type: CommandType
    command: str
    description: str
    example_output: Optional[str] = None
    language: CommandLanguage = CommandLanguage.BASH
    parameters: Dict[str, Any] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.headers is None:
            self.headers = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'type': self.type.value,
            'command': self.command,
            'description': self.description,
            'example_output': self.example_output,
            'language': self.language.value,
            'parameters': self.parameters,
            'headers': self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratedCommand':
        """Create from dictionary"""
        return cls(
            type=CommandType(data['type']),
            command=data['command'],
            description=data['description'],
            example_output=data.get('example_output'),
            language=CommandLanguage(data.get('language', 'bash')),
            parameters=data.get('parameters', {}),
            headers=data.get('headers', {})
        )


@dataclass
class CommandTemplate:
    """Template for generating commands"""
    name: str
    template: str
    description: str
    parameters: List[str]
    example_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.example_parameters is None:
            self.example_parameters = {}
    
    def render(self, **kwargs) -> str:
        """Render template with parameters"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing parameter for template '{self.name}': {e}")


class CommandCategory:
    """Category of related commands"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.commands: List[GeneratedCommand] = []
        self.templates: List[CommandTemplate] = []
    
    def add_command(self, command: GeneratedCommand):
        """Add command to category"""
        self.commands.append(command)
    
    def add_template(self, template: CommandTemplate):
        """Add template to category"""
        self.templates.append(template)
    
    def get_commands_by_type(self, command_type: CommandType) -> List[GeneratedCommand]:
        """Get commands of specific type"""
        return [cmd for cmd in self.commands if cmd.type == command_type]
    
    def get_commands_by_language(self, language: CommandLanguage) -> List[GeneratedCommand]:
        """Get commands for specific language"""
        return [cmd for cmd in self.commands if cmd.language == language]


# Predefined command templates
CURL_TEMPLATES = {
    'get': CommandTemplate(
        name='curl_get',
        template='curl -X GET {base_url}{path}',
        description='GET request using cURL',
        parameters=['base_url', 'path']
    ),
    'post': CommandTemplate(
        name='curl_post',
        template='curl -X POST {base_url}{path} -H "Content-Type: application/json" -d \'{data}\'',
        description='POST request using cURL',
        parameters=['base_url', 'path', 'data'],
        example_parameters={'data': '{"key": "value"}'}
    ),
    'put': CommandTemplate(
        name='curl_put',
        template='curl -X PUT {base_url}{path} -H "Content-Type: application/json" -d \'{data}\'',
        description='PUT request using cURL',
        parameters=['base_url', 'path', 'data'],
        example_parameters={'data': '{"key": "updated_value"}'}
    ),
    'delete': CommandTemplate(
        name='curl_delete',
        template='curl -X DELETE {base_url}{path}',
        description='DELETE request using cURL',
        parameters=['base_url', 'path']
    )
}

PYTHON_TEMPLATES = {
    'get': CommandTemplate(
        name='python_get',
        template='''import requests

url = "{base_url}{path}"
response = requests.get(url)
print(response.json())''',
        description='GET request using Python requests',
        parameters=['base_url', 'path']
    ),
    'post': CommandTemplate(
        name='python_post',
        template='''import requests

url = "{base_url}{path}"
data = {data}
response = requests.post(url, json=data)
print(response.json())''',
        description='POST request using Python requests',
        parameters=['base_url', 'path', 'data'],
        example_parameters={'data': '{"key": "value"}'}
    ),
    'put': CommandTemplate(
        name='python_put',
        template='''import requests

url = "{base_url}{path}"
data = {data}
response = requests.put(url, json=data)
print(response.json())''',
        description='PUT request using Python requests',
        parameters=['base_url', 'path', 'data'],
        example_parameters={'data': '{"key": "updated_value"}'}
    ),
    'delete': CommandTemplate(
        name='python_delete',
        template='''import requests

url = "{base_url}{path}"
response = requests.delete(url)
print(response.json())''',
        description='DELETE request using Python requests',
        parameters=['base_url', 'path']
    )
}

JAVASCRIPT_TEMPLATES = {
    'get': CommandTemplate(
        name='javascript_get',
        template='''fetch('{base_url}{path}')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));''',
        description='GET request using JavaScript fetch',
        parameters=['base_url', 'path']
    ),
    'post': CommandTemplate(
        name='javascript_post',
        template='''fetch('{base_url}{path}', {{
  method: 'POST',
  headers: {{
    'Content-Type': 'application/json',
  }},
  body: JSON.stringify({data})
}})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));''',
        description='POST request using JavaScript fetch',
        parameters=['base_url', 'path', 'data'],
        example_parameters={'data': '{"key": "value"}'}
    )
}

SHELL_TEMPLATES = {
    'start_service': CommandTemplate(
        name='start_service',
        template='python -m proserve {manifest_path}',
        description='Start ProServe service',
        parameters=['manifest_path'],
        example_parameters={'manifest_path': 'manifest.yml'}
    ),
    'start_dev': CommandTemplate(
        name='start_dev',
        template='python -m proserve {manifest_path} --dev --reload',
        description='Start service in development mode',
        parameters=['manifest_path'],
        example_parameters={'manifest_path': 'manifest.yml'}
    ),
    'docker_build': CommandTemplate(
        name='docker_build',
        template='docker build -t {image_name} .',
        description='Build Docker image',
        parameters=['image_name']
    ),
    'docker_run': CommandTemplate(
        name='docker_run',
        template='docker run -p {host_port}:{container_port} {image_name}',
        description='Run Docker container',
        parameters=['host_port', 'container_port', 'image_name']
    )
}


def get_all_templates() -> Dict[str, Dict[str, CommandTemplate]]:
    """Get all predefined command templates"""
    return {
        'curl': CURL_TEMPLATES,
        'python': PYTHON_TEMPLATES,
        'javascript': JAVASCRIPT_TEMPLATES,
        'shell': SHELL_TEMPLATES
    }


def get_template(category: str, name: str) -> Optional[CommandTemplate]:
    """Get specific template by category and name"""
    templates = get_all_templates()
    return templates.get(category, {}).get(name)


def validate_command(command: GeneratedCommand) -> List[str]:
    """Validate a generated command and return list of issues"""
    issues = []
    
    if not command.command:
        issues.append("Command cannot be empty")
    
    if not command.description:
        issues.append("Description is required")
    
    if command.type == CommandType.CURL:
        if 'curl' not in command.command:
            issues.append("cURL command must contain 'curl'")
    
    elif command.type == CommandType.PYTHON:
        if command.language != CommandLanguage.PYTHON:
            issues.append("Python command must have python language")
    
    elif command.type == CommandType.SHELL:
        if command.language not in [CommandLanguage.BASH, CommandLanguage.ZSH, CommandLanguage.FISH, CommandLanguage.POWERSHELL]:
            issues.append("Shell command must have appropriate shell language")
    
    return issues
