"""
ProServe CLI Argument Parsers
Modular argument parsing for ProServe CLI

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

import argparse
from ..utils.helpers import get_framework_info


class ProServeArgumentParser:
    """Main argument parser for ProServe CLI"""
    
    def __init__(self):
        self.parser = None
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            prog="proserve",
            description="ProServe - Professional Service Framework CLI",
            formatter_class=argparse.RichHelpFormatter if hasattr(argparse, 'RichHelpFormatter') else argparse.HelpFormatter
        )
        
        parser.add_argument(
            "--version", 
            action="version", 
            version=f"ProServe {get_framework_info().get('version', '1.0.0')}"
        )
        
        parser.add_argument(
            "--config", 
            type=str, 
            help="Path to configuration file"
        )
        
        parser.add_argument(
            "--verbose", "-v", 
            action="store_true", 
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--debug", 
            action="store_true", 
            help="Enable debug mode"
        )
        
        # Create subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Add all command groups
        self._add_service_commands(subparsers)
        self._add_management_commands(subparsers)
        self._add_platform_commands(subparsers)
        self._add_dev_commands(subparsers)
        
        self.parser = parser
        return parser
    
    def _add_service_commands(self, subparsers):
        """Add service management commands"""
        # Run service
        run_parser = subparsers.add_parser("run", help="Run ProServe service")
        run_parser.add_argument("manifest", nargs="?", help="Service manifest file")
        run_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
        run_parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
        run_parser.add_argument("--workers", type=int, default=1, help="Number of workers")
        run_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
        run_parser.add_argument("--ssl-cert", help="SSL certificate file")
        run_parser.add_argument("--ssl-key", help="SSL private key file")
        
        # Build service
        build_parser = subparsers.add_parser("build", help="Build application from manifest")
        build_parser.add_argument("manifest", help="Service manifest file")
        build_parser.add_argument("--output", "-o", default="build", help="Output directory")
        build_parser.add_argument("--platform", help="Target platform (docker, k8s, serverless)")
        build_parser.add_argument("--clean", action="store_true", help="Clean output directory first")
        
        # Deploy service
        deploy_parser = subparsers.add_parser("deploy", help="Deploy ProServe service")
        deploy_parser.add_argument("manifest", help="Service manifest file")
        deploy_parser.add_argument("--target", help="Deployment target")
        deploy_parser.add_argument("--env", help="Environment (dev, staging, prod)")
        
    def _add_management_commands(self, subparsers):
        """Add management commands"""
        # List services
        list_parser = subparsers.add_parser("list", help="List ProServe services")
        list_parser.add_argument("--format", choices=["table", "json"], default="table")
        
        # Service status
        status_parser = subparsers.add_parser("status", help="Check service status")
        status_parser.add_argument("service", nargs="?", help="Service name")
        
        # Stop service
        stop_parser = subparsers.add_parser("stop", help="Stop ProServe service")
        stop_parser.add_argument("service", help="Service name or ID")
        
        # Restart service
        restart_parser = subparsers.add_parser("restart", help="Restart ProServe service")
        restart_parser.add_argument("service", help="Service name or ID")
        
        # Logs
        logs_parser = subparsers.add_parser("logs", help="View service logs")
        logs_parser.add_argument("service", nargs="?", help="Service name")
        logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow logs")
        logs_parser.add_argument("--tail", type=int, default=100, help="Number of lines to show")
        
    def _add_platform_commands(self, subparsers):
        """Add platform-specific commands"""
        # Generate Docker
        docker_parser = subparsers.add_parser("docker", help="Generate Docker configuration")
        docker_parser.add_argument("manifest", help="Service manifest file")
        docker_parser.add_argument("--output", "-o", default=".", help="Output directory")
        docker_parser.add_argument("--base-image", help="Base Docker image")
        
        # Generate Kubernetes
        k8s_parser = subparsers.add_parser("k8s", help="Generate Kubernetes manifests")
        k8s_parser.add_argument("manifest", help="Service manifest file")
        k8s_parser.add_argument("--output", "-o", default="k8s", help="Output directory")
        k8s_parser.add_argument("--namespace", help="Kubernetes namespace")
        
        # Generate Serverless
        serverless_parser = subparsers.add_parser("serverless", help="Generate serverless configuration")
        serverless_parser.add_argument("manifest", help="Service manifest file")
        serverless_parser.add_argument("--provider", choices=["aws", "gcp", "azure"], help="Cloud provider")
        
    def _add_dev_commands(self, subparsers):
        """Add development commands"""
        # Initialize project
        init_parser = subparsers.add_parser("init", help="Initialize new ProServe project")
        init_parser.add_argument("directory", nargs="?", default=".", help="Project directory")
        init_parser.add_argument("--template", help="Project template")
        
        # Note: build command is defined in _add_service_commands for manifest code generation
        
        # Test project
        test_parser = subparsers.add_parser("test", help="Test ProServe services")
        test_parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
        test_parser.add_argument("--integration", action="store_true", help="Run integration tests")
        
        # Validate manifest
        validate_parser = subparsers.add_parser("validate", help="Validate service manifest")
        validate_parser.add_argument("manifest", help="Service manifest file")
        
        # Generate examples
        examples_parser = subparsers.add_parser("examples", help="Generate example projects")
        examples_parser.add_argument("type", nargs="?", help="Example type")
        examples_parser.add_argument("--output", "-o", default="examples", help="Output directory")
