"""
ProServe CLI - Simplified and Modular
New streamlined CLI that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular CLI system.
The heavy lifting is done by the cli/ package modules:
- cli/parsers.py - Argument parsing
- cli/commands.py - Command implementations  
- cli/generators.py - Code generation
- cli/helpers.py - Utilities and helpers
- cli/main_cli.py - Main orchestration

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular CLI
from .cli.main_cli import ProServeCLI, main, run_cli

# Legacy compatibility - expose the main CLI class
__all__ = ['ProServeCLI', 'main', 'run_cli']

# For backwards compatibility, we can still import this module directly
if __name__ == "__main__":
    main()
