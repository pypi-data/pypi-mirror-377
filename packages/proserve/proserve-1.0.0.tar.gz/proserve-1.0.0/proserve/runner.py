"""
ProServe Service Runner
Main entry point for running ProServe services from command line
"""

import argparse
import asyncio
import sys
from pathlib import Path
from .core.service import ProServeService
from .core.manifest import ServiceManifest


async def main():
    """Main CLI entry point for running ProServe services"""
    parser = argparse.ArgumentParser(description='ProServe Microservice Framework')
    parser.add_argument('manifest', help='Path to service manifest YAML file')
    parser.add_argument('--port', type=int, help='Override server port')
    parser.add_argument('--host', help='Override server host')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Load manifest
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"❌ Manifest file not found: {manifest_path}")
        sys.exit(1)
    
    try:
        # Load service manifest
        manifest = ServiceManifest.from_yaml(manifest_path)
        
        # Apply CLI overrides
        if args.port:
            manifest.server['port'] = args.port
        if args.host:
            manifest.server['host'] = args.host
        if args.debug:
            manifest.logging = manifest.logging or {}
            manifest.logging['level'] = 'DEBUG'
        elif args.log_level:
            manifest.logging = manifest.logging or {}
            manifest.logging['level'] = args.log_level
        
        # Create and run service
        service = ProServeService(manifest)
        await service.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Failed to run service: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
