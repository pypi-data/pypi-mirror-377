"""
ProServe Command Generator - Simplified and Modular
New streamlined command generator that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular generator system.
The heavy lifting is done by the generators/ package modules:
- generators/command_types.py - Command data structures and types
- generators/command_generator.py - Main command generation logic
- generators/http_generator.py - HTTP/REST API command generation
- generators/export_formatter.py - Command output formatting and export

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular command generator components
from .generators import (
    CommandType,
    GeneratedCommand,
    CommandLanguage,
    CommandTemplate,
    CommandCategory,
    CommandGenerator,
    HTTPCommandGenerator,
    ExportFormatter,
    generate_commands_from_manifest,
    export_commands_as_script,
    export_commands_as_markdown,
    generate_documentation,
    CURL_TEMPLATES,
    PYTHON_TEMPLATES,
    JAVASCRIPT_TEMPLATES,
    SHELL_TEMPLATES,
    get_all_templates,
    get_template,
    validate_command
)

# Legacy compatibility - expose the main classes
__all__ = [
    'CommandType',
    'GeneratedCommand',
    'CommandLanguage',
    'CommandTemplate',
    'CommandCategory',
    'CommandGenerator',
    'HTTPCommandGenerator',
    'ExportFormatter',
    'generate_commands_from_manifest',
    'export_commands_as_script',
    'export_commands_as_markdown',
    'generate_documentation',
    'CURL_TEMPLATES',
    'PYTHON_TEMPLATES',
    'JAVASCRIPT_TEMPLATES',
    'SHELL_TEMPLATES',
    'get_all_templates',
    'get_template',
    'validate_command'
]
