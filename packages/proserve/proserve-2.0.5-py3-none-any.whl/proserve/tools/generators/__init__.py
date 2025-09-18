"""
ProServe Command Generators - Modular Command Generation Components
Refactored from monolithic command_generator.py into focused, testable generator modules
"""

from .command_types import (
    GeneratedCommand, CommandType, CommandLanguage, CommandTemplate, CommandCategory,
    CURL_TEMPLATES, PYTHON_TEMPLATES, JAVASCRIPT_TEMPLATES, SHELL_TEMPLATES,
    get_all_templates, get_template, validate_command
)
from .http_generator import HTTPCommandGenerator, generate_openapi_spec
from .export_formatter import (
    ExportFormatter, export_commands_as_script, export_commands_as_markdown
)
from .command_generator import (
    CommandGenerator, generate_commands_from_manifest, 
    export_commands_as_script, generate_documentation
)

__all__ = [
    # Core Types and Enums
    'GeneratedCommand', 'CommandType', 'CommandLanguage', 'CommandTemplate', 'CommandCategory',
    
    # Template Collections
    'CURL_TEMPLATES', 'PYTHON_TEMPLATES', 'JAVASCRIPT_TEMPLATES', 'SHELL_TEMPLATES',
    'get_all_templates', 'get_template', 'validate_command',
    
    # Specialized Generators
    'HTTPCommandGenerator', 'generate_openapi_spec',
    
    # Export and Formatting
    'ExportFormatter', 'export_commands_as_script', 'export_commands_as_markdown',
    
    # Main Generator
    'CommandGenerator', 'generate_commands_from_manifest', 'generate_documentation',
    
    # Backward Compatibility Command Classes
    'HTTPCommand', 'GRPCCommand', 'DatabaseCommand'
]

# Backward compatibility exports
CommandGenerator = CommandGenerator
GeneratedCommand = GeneratedCommand

# Backward compatibility aliases for missing command classes
class HTTPCommand:
    """Backward compatibility alias for HTTP command generation"""
    def __init__(self, *args, **kwargs):
        self.command_type = CommandType.HTTP
        self.args = args
        self.kwargs = kwargs

class GRPCCommand:
    """Backward compatibility alias for GRPC command generation"""
    def __init__(self, *args, **kwargs):
        self.command_type = CommandType.GRPC
        self.args = args
        self.kwargs = kwargs

class DatabaseCommand:
    """Backward compatibility alias for Database command generation"""
    def __init__(self, *args, **kwargs):
        self.command_type = CommandType.DATABASE
        self.args = args
        self.kwargs = kwargs
