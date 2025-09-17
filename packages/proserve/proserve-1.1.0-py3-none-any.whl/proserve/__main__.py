"""
ProServe CLI Entry Point
Allows running ProServe via `python -m proserve`
"""

import sys
import asyncio
from pathlib import Path
from .runner import main


if __name__ == '__main__':
    # Ensure we have a manifest file argument
    if len(sys.argv) < 2:
        print("Usage: python -m proserve <manifest.yml>")
        print("   or: python -m proserve run <manifest.yml>")
        sys.exit(1)
    
    # Handle 'run' subcommand
    args = sys.argv[1:]
    if args[0] == 'run':
        if len(args) < 2:
            print("Usage: python -m proserve run <manifest.yml>")
            sys.exit(1)
        args = args[1:]  # Remove 'run' subcommand
    
    # Set up sys.argv for the runner
    sys.argv = ['proserve'] + args
    
    # Run the service
    asyncio.run(main())
