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
    'CommandGenerator', 'generate_commands_from_manifest', 'generate_documentation'
]

# Backward compatibility exports
CommandGenerator = CommandGenerator
GeneratedCommand = GeneratedCommand
