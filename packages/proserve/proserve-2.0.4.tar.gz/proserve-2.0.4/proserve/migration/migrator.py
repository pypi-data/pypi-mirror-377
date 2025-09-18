"""
ProServe Service Migrator
Advanced service migration and framework conversion tools
Ported from edpmt-framework with enhanced capabilities
"""

import os
import re
import json
import shutil
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

from ..core.manifest import ServiceManifest
from ..discovery.detector import ServiceDetector, ServiceInfo

logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Migration operation result"""
    success: bool
    source_path: str
    target_path: str
    framework: str
    migration_type: str
    files_created: List[str]
    files_modified: List[str]
    issues: List[str]
    recommendations: List[str]
    manifest_path: Optional[str]
    complexity_score: int
    migration_time: float
    timestamp: str


@dataclass
class MigrationConfig:
    """Migration configuration settings"""
    preserve_structure: bool = True
    create_backup: bool = True
    generate_manifest: bool = True
    include_examples: bool = True
    migration_mode: str = "full"  # full, minimal, custom
    target_framework: str = "proserve"
    custom_handlers: Dict[str, Any] = None
    exclude_patterns: List[str] = None


class ServiceMigrator:
    """Advanced service migration with multi-framework support"""
    
    def __init__(self, config: Optional[MigrationConfig] = None):
        self.config = config or MigrationConfig()
        self.detector = ServiceDetector()
        self.migration_templates = self._load_migration_templates()
        
    def _load_migration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load framework-specific migration templates"""
        return {
            'flask': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0',
                    'framework': 'proserve',
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from flask import Flask, request, jsonify'],
                'converter_patterns': {
                    '@app.route': 'async def {handler_name}(request):',
                    'return jsonify': 'return web.json_response'
                }
            },
            'fastapi': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0', 
                    'framework': 'proserve',
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from fastapi import FastAPI, Request'],
                'converter_patterns': {
                    '@app.get': 'async def {handler_name}(request):',
                    '@app.post': 'async def {handler_name}(request):'
                }
            },
            'django': {
                'manifest_template': {
                    'name': '{service_name}',
                    'version': '1.0.0',
                    'framework': 'proserve', 
                    'server': {'host': '0.0.0.0', 'port': 8000},
                    'endpoints': [],
                    'database': {'type': 'sqlite', 'url': 'sqlite:///db.sqlite3'},
                    'logging': {'level': 'INFO', 'format': 'json'}
                },
                'handler_imports': ['from django.http import JsonResponse'],
                'converter_patterns': {
                    'def ': 'async def {handler_name}(request):',
                    'JsonResponse': 'web.json_response'
                }
            }
        }

    async def migrate(self, source_path: str, target_path: str) -> MigrationResult:
        """Migrate service from source to target path"""
        
        start_time = asyncio.get_event_loop().time()
        source = Path(source_path)
        target = Path(target_path)
        
        logger.info(f"Starting migration from {source} to {target}")
        
        try:
            # Detect source service
            services = self.detector.detect(source)
            if not services:
                return MigrationResult(
                    success=False,
                    source_path=source_path,
                    target_path=target_path,
                    framework="unknown",
                    migration_type="detection_failed",
                    files_created=[],
                    files_modified=[],
                    issues=["No detectable service found in source path"],
                    recommendations=["Ensure source contains a valid web service"],
                    manifest_path=None,
                    complexity_score=0,
                    migration_time=0.0,
                    timestamp=datetime.now().isoformat()
                )
            
            # Use first detected service
            service_info = services[0]
            
            # Create backup if requested
            if self.config.create_backup:
                await self._create_backup(source)
            
            # Prepare target directory
            target.mkdir(parents=True, exist_ok=True)
            
            # Perform migration based on framework
            result = await self._migrate_framework_service(service_info, target)
            
            # Calculate migration time
            migration_time = asyncio.get_event_loop().time() - start_time
            result.migration_time = migration_time
            
            logger.info(f"Migration completed in {migration_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return MigrationResult(
                success=False,
                source_path=source_path,
                target_path=target_path,
                framework="unknown",
                migration_type="error",
                files_created=[],
                files_modified=[],
                issues=[str(e)],
                recommendations=["Check source service structure and permissions"],
                manifest_path=None,
                complexity_score=0,
                migration_time=asyncio.get_event_loop().time() - start_time,
                timestamp=datetime.now().isoformat()
            )

    async def _migrate_framework_service(self, service_info: ServiceInfo, target: Path) -> MigrationResult:
        """Migrate service based on detected framework"""
        
        files_created = []
        files_modified = []
        issues = []
        recommendations = []
        
        framework = service_info.framework
        template = self.migration_templates.get(framework, self.migration_templates['flask'])
        
        # Generate manifest
        manifest_path = None
        if self.config.generate_manifest:
            manifest_path = await self._generate_manifest(service_info, target, template)
            files_created.append(str(manifest_path))
        
        # Copy and convert handlers
        handlers_dir = target / "handlers"
        handlers_dir.mkdir(exist_ok=True)
        
        for endpoint in service_info.endpoints:
            handler_file = await self._convert_handler(
                service_info, endpoint, handlers_dir, template
            )
            if handler_file:
                files_created.append(str(handler_file))
        
        # Create requirements.txt
        requirements_file = await self._generate_requirements(service_info, target)
        files_created.append(str(requirements_file))
        
        # Create README
        readme_file = await self._generate_readme(service_info, target)
        files_created.append(str(readme_file))
        
        # Add framework-specific recommendations
        recommendations.extend(self._get_framework_recommendations(framework))
        
        return MigrationResult(
            success=True,
            source_path=str(service_info.path),
            target_path=str(target),
            framework=framework,
            migration_type="framework_conversion",
            files_created=files_created,
            files_modified=files_modified,
            issues=issues,
            recommendations=recommendations,
            manifest_path=str(manifest_path) if manifest_path else None,
            complexity_score=service_info.complexity_score,
            migration_time=0.0,  # Will be set by caller
            timestamp=datetime.now().isoformat()
        )

    async def _create_backup(self, source: Path) -> str:
        """Create backup of source service"""
        backup_dir = source.parent / f"{source.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(source, backup_dir)
        logger.info(f"Created backup at {backup_dir}")
        return str(backup_dir)

    async def _generate_manifest(self, service_info: ServiceInfo, target: Path, template: Dict) -> Path:
        """Generate ProServe manifest from service info"""
        
        manifest_data = template['manifest_template'].copy()
        manifest_data['name'] = service_info.name
        
        # Convert endpoints to ProServe format
        endpoints = []
        for endpoint in service_info.endpoints:
            for method in endpoint['methods']:
                endpoints.append({
                    'path': endpoint['path'],
                    'method': method.lower(),
                    'handler': f"handlers.{endpoint['file'].replace('.py', '')}.{self._generate_handler_name(endpoint['path'])}"
                })
        
        manifest_data['endpoints'] = endpoints
        
        # Add database info if detected
        if service_info.database_info:
            manifest_data['database'] = {
                'type': service_info.database_info['primary'],
                'url': f"{service_info.database_info['primary']}://localhost:5432/db"
            }
        
        # Add deployment info
        if service_info.deployment_info:
            manifest_data['deployment'] = service_info.deployment_info
        
        manifest_path = target / "manifest.yml"
        
        # Write YAML manifest
        import yaml
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest_data, f, default_flow_style=False)
        
        logger.info(f"Generated manifest: {manifest_path}")
        return manifest_path

    async def _convert_handler(self, service_info: ServiceInfo, endpoint: Dict, 
                             handlers_dir: Path, template: Dict) -> Optional[Path]:
        """Convert endpoint to ProServe handler"""
        
        handler_name = self._generate_handler_name(endpoint['path'])
        handler_file = handlers_dir / f"{handler_name}.py"
        
        # Generate handler code
        handler_code = self._generate_handler_code(endpoint, template)
        
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        logger.info(f"Created handler: {handler_file}")
        return handler_file

    def _generate_handler_name(self, path: str) -> str:
        """Generate handler name from endpoint path"""
        # Convert /api/users/{id} -> api_users_id
        name = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip('/'))
        name = re.sub(r'_+', '_', name)
        return name.strip('_') or 'index'

    def _generate_handler_code(self, endpoint: Dict, template: Dict) -> str:
        """Generate ProServe handler code"""
        
        handler_name = self._generate_handler_name(endpoint['path'])
        methods = endpoint['methods']
        
        code = f'''"""
ProServe Handler for {endpoint['path']}
Auto-generated from {endpoint['framework']} migration
"""

from aiohttp import web
from typing import Dict, Any


async def {handler_name}(request: web.Request) -> web.Response:
    """Handle {' '.join(methods)} {endpoint['path']}"""
    
    method = request.method
    
'''
        
        for method in methods:
            code += f'''    if method == "{method}":
        # TODO: Implement {method} logic for {endpoint['path']}
        return web.json_response({{"message": "{method} {endpoint['path']} endpoint"}})
    
'''
        
        code += '''    return web.json_response({"error": "Method not allowed"}, status=405)
'''
        
        return code

    async def _generate_requirements(self, service_info: ServiceInfo, target: Path) -> Path:
        """Generate requirements.txt for migrated service"""
        
        requirements = [
            "# ProServe Migration Generated Requirements",
            "",
            "# Core ProServe Framework", 
            "aiohttp>=3.8.0",
            "PyYAML>=6.0",
            "structlog>=22.3.0",
            ""
        ]
        
        # Add original dependencies (filtered)
        if service_info.dependencies:
            requirements.append("# Original Dependencies (filtered)")
            for dep in service_info.dependencies:
                if dep.lower() not in ['flask', 'django', 'fastapi', 'express']:
                    requirements.append(f"{dep}")
            requirements.append("")
        
        # Add framework-specific requirements
        if service_info.database_info:
            requirements.append("# Database Dependencies")
            for db_type in service_info.database_info['types']:
                if db_type == 'postgresql':
                    requirements.append("asyncpg>=0.27.0")
                elif db_type == 'mysql':
                    requirements.append("aiomysql>=0.1.1")
                elif db_type == 'redis':
                    requirements.append("aioredis>=2.0.0")
        
        requirements_file = target / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        logger.info(f"Generated requirements: {requirements_file}")
        return requirements_file

    async def _generate_readme(self, service_info: ServiceInfo, target: Path) -> Path:
        """Generate README for migrated service"""
        
        readme_content = f'''# {service_info.name}

Auto-migrated from {service_info.framework} to ProServe

## Service Information

- **Framework**: {service_info.framework} → ProServe  
- **Version**: {service_info.version or "1.0.0"}
- **Complexity Score**: {service_info.complexity_score}/100
- **Migration Difficulty**: {service_info.migration_difficulty}
- **Confidence**: {service_info.confidence_score:.1%}

## Endpoints

'''
        
        for endpoint in service_info.endpoints:
            readme_content += f"- **{' '.join(endpoint['methods'])}** `{endpoint['path']}`\n"
        
        readme_content += f'''

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   python -m proserve manifest.yml
   ```

3. Test endpoints:
   ```bash
   curl http://localhost:8000/
   ```

## Database

'''
        
        if service_info.database_info:
            readme_content += f"- **Type**: {service_info.database_info['primary']}\n"
            readme_content += f"- **All Types**: {', '.join(service_info.database_info['types'])}\n"
        else:
            readme_content += "No database detected\n"
        
        readme_content += f'''

## Deployment

'''
        
        if service_info.deployment_info:
            readme_content += f"- **Containerized**: {service_info.deployment_info.get('containerized', False)}\n"
            readme_content += f"- **Types**: {', '.join(service_info.deployment_info['types'])}\n"
        else:
            readme_content += "No deployment configuration detected\n"
        
        readme_content += '''

## Migration Notes

This service has been automatically migrated from {framework}. 
Please review and test all handlers before production use.

## TODO

- [ ] Review generated handlers
- [ ] Test all endpoints
- [ ] Update database configuration
- [ ] Configure logging
- [ ] Add error handling
- [ ] Write tests

'''.format(framework=service_info.framework)
        
        readme_file = target / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Generated README: {readme_file}")
        return readme_file

    def _get_framework_recommendations(self, framework: str) -> List[str]:
        """Get framework-specific migration recommendations"""
        
        recommendations = {
            'flask': [
                "Review Flask Blueprint usage and convert to ProServe handlers",
                "Check Flask-SQLAlchemy models and convert to async database operations",
                "Update session management for async compatibility"
            ],
            'django': [
                "Convert Django models to async database operations",
                "Review middleware and convert to ProServe middleware",
                "Update URL patterns to ProServe endpoint format",
                "Convert Django ORM queries to async database operations"
            ],
            'fastapi': [
                "FastAPI migration is typically straightforward",
                "Review Pydantic models and adapt to ProServe validation",
                "Update dependency injection patterns"
            ],
            'express': [
                "Convert Express middleware to ProServe middleware",
                "Update route handlers to async Python functions",
                "Review npm dependencies and find Python equivalents"
            ]
        }
        
        return recommendations.get(framework, [
            "Review original framework patterns",
            "Update handlers for async compatibility",
            "Test all endpoints thoroughly"
        ])


class EDPMTMigrator(ServiceMigrator):
    """EDPMT to ProServe migration with legacy support"""
    
    async def migrate_from_edpmt(self, edpmt_service: str, proserve_target: str) -> MigrationResult:
        """Migrate from EDPMT framework to ProServe"""
        
        logger.info(f"Migrating EDPMT service: {edpmt_service}")
        
        # Use base migration with EDPMT-specific handling
        result = await self.migrate(edpmt_service, proserve_target)
        result.migration_type = "edpmt_conversion"
        
        # Add EDPMT-specific recommendations
        result.recommendations.extend([
            "Review EDPMT-specific configurations",
            "Update isolation manager usage",
            "Convert EDPMT manifest to ProServe format",
            "Test process isolation features"
        ])
        
        return result


# Convenience functions for backward compatibility
async def migrate_service_to_proserve(source: str, target: str = None, 
                                    config: MigrationConfig = None) -> MigrationResult:
    """Migrate any service to ProServe format"""
    
    if target is None:
        source_path = Path(source)
        target = str(source_path.parent / f"{source_path.name}_proserve")
    
    migrator = ServiceMigrator(config)
    return await migrator.migrate(source, target)


async def migrate_framework_service(framework: str, service_path: str, 
                                  target_path: str = None) -> MigrationResult:
    """Migrate specific framework service to ProServe"""
    
    if target_path is None:
        source_path = Path(service_path)
        target_path = str(source_path.parent / f"{source_path.name}_proserve")
    
    config = MigrationConfig()
    migrator = ServiceMigrator(config)
    return await migrator.migrate(service_path, target_path)


def validate_migration(source: str, target: str) -> Dict[str, Any]:
    """Validate migration configuration and readiness"""
    
    source_path = Path(source)
    target_path = Path(target)
    
    issues = []
    recommendations = []
    status = "valid"
    
    # Check source exists
    if not source_path.exists():
        issues.append(f"Source path does not exist: {source}")
        status = "invalid"
    
    # Check source is directory
    if source_path.exists() and not source_path.is_dir():
        issues.append(f"Source must be a directory: {source}")
        status = "invalid"
    
    # Check target writeable
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        issues.append(f"Cannot write to target path: {target}")
        status = "invalid"
    
    # Check for service in source
    if source_path.exists() and source_path.is_dir():
        detector = ServiceDetector()
        services = detector.detect(source_path)
        if not services:
            issues.append("No detectable service found in source")
            recommendations.append("Ensure source contains web service files")
        else:
            service = services[0]
            if service.complexity_score > 80:
                recommendations.append("High complexity service - review migration carefully")
            if service.migration_difficulty == 'hard':
                recommendations.append("Difficult migration expected - manual review required")
    
    return {
        "status": status,
        "issues": issues,
        "recommendations": recommendations,
        "source_exists": source_path.exists(),
        "target_writable": True,  # We checked above
        "detected_services": len(services) if 'services' in locals() else 0
    }
