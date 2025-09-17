"""
ProServe Manifest API Server
RESTful API for remote manifest creation and management
JSON-based alternative to YAML configuration
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from aiohttp import web, ClientSession
from aiohttp.web import Request, Response, json_response
from aiohttp_cors import setup as cors_setup, CorsConfig

from .manifest_builder import (
    ManifestBuilder, EndpointBuilder, DatabaseBuilder, LoggingBuilder,
    GrpcServiceBuilder, from_template, TEMPLATES
)
from ..core.manifest import ServiceManifest

logger = logging.getLogger(__name__)


@dataclass
class ManifestProject:
    """Represents a manifest project with metadata"""
    id: str
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    author: str
    tags: List[str]
    manifest: Dict[str, Any]
    status: str = 'draft'  # draft, published, archived


class ManifestStore:
    """In-memory storage for manifest projects"""
    
    def __init__(self):
        self._projects: Dict[str, ManifestProject] = {}
        
    def create_project(self, project: ManifestProject) -> None:
        """Store a new project"""
        self._projects[project.id] = project
        
    def get_project(self, project_id: str) -> Optional[ManifestProject]:
        """Get project by ID"""
        return self._projects.get(project_id)
        
    def update_project(self, project_id: str, project: ManifestProject) -> bool:
        """Update existing project"""
        if project_id in self._projects:
            self._projects[project_id] = project
            return True
        return False
        
    def delete_project(self, project_id: str) -> bool:
        """Delete project by ID"""
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False
        
    def list_projects(self, status: str = None, tags: List[str] = None) -> List[ManifestProject]:
        """List projects with optional filtering"""
        projects = list(self._projects.values())
        
        if status:
            projects = [p for p in projects if p.status == status]
            
        if tags:
            projects = [p for p in projects if any(tag in p.tags for tag in tags)]
            
        return projects
        
    def export_all(self) -> Dict[str, Any]:
        """Export all projects"""
        return {pid: asdict(project) for pid, project in self._projects.items()}
        
    def import_all(self, data: Dict[str, Any]) -> None:
        """Import projects from data"""
        for pid, project_data in data.items():
            project = ManifestProject(**project_data)
            self._projects[pid] = project


class ManifestAPIServer:
    """RESTful API server for manifest management"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, 
                 cors_enabled: bool = True):
        self.host = host
        self.port = port
        self.cors_enabled = cors_enabled
        self.store = ManifestStore()
        self.app = None
        
    def setup_routes(self) -> web.Application:
        """Setup API routes"""
        app = web.Application()
        
        # Health check
        app.router.add_get('/health', self.health_check)
        
        # API documentation
        app.router.add_get('/', self.api_docs)
        app.router.add_get('/docs', self.api_docs)
        
        # Projects CRUD
        app.router.add_get('/api/v1/projects', self.list_projects)
        app.router.add_post('/api/v1/projects', self.create_project)
        app.router.add_get('/api/v1/projects/{project_id}', self.get_project)
        app.router.add_put('/api/v1/projects/{project_id}', self.update_project)
        app.router.add_delete('/api/v1/projects/{project_id}', self.delete_project)
        
        # Manifest operations
        app.router.add_post('/api/v1/projects/{project_id}/manifest', self.update_manifest)
        app.router.add_get('/api/v1/projects/{project_id}/manifest/yaml', self.export_yaml)
        app.router.add_get('/api/v1/projects/{project_id}/manifest/json', self.export_json)
        
        # Template operations
        app.router.add_get('/api/v1/templates', self.list_templates)
        app.router.add_post('/api/v1/templates/{template_name}', self.create_from_template)
        
        # Builder operations
        app.router.add_post('/api/v1/builder/endpoint', self.build_endpoint)
        app.router.add_post('/api/v1/builder/database', self.build_database)
        app.router.add_post('/api/v1/builder/logging', self.build_logging)
        app.router.add_post('/api/v1/builder/grpc-service', self.build_grpc_service)
        
        # Validation
        app.router.add_post('/api/v1/validate', self.validate_manifest)
        
        # Import/Export
        app.router.add_get('/api/v1/export', self.export_all)
        app.router.add_post('/api/v1/import', self.import_all)
        
        # Setup CORS if enabled
        if self.cors_enabled:
            cors = cors_setup(app, defaults={
                "*": CorsConfig(
                    allow_all_methods=True,
                    allow_all_headers=True,
                    allow_credentials=True
                )
            })
            
        self.app = app
        return app
        
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        return json_response({
            'status': 'healthy',
            'service': 'ProServe Manifest API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'projects_count': len(self.store._projects)
        })
        
    async def api_docs(self, request: Request) -> Response:
        """API documentation endpoint"""
        docs = {
            'title': 'ProServe Manifest API',
            'version': '1.0.0',
            'description': 'RESTful API for creating and managing ProServe service manifests',
            'endpoints': {
                'GET /health': 'Health check',
                'GET /': 'API documentation',
                'GET /api/v1/projects': 'List all projects',
                'POST /api/v1/projects': 'Create new project',
                'GET /api/v1/projects/{id}': 'Get project by ID',
                'PUT /api/v1/projects/{id}': 'Update project',
                'DELETE /api/v1/projects/{id}': 'Delete project',
                'POST /api/v1/projects/{id}/manifest': 'Update project manifest',
                'GET /api/v1/projects/{id}/manifest/yaml': 'Export manifest as YAML',
                'GET /api/v1/projects/{id}/manifest/json': 'Export manifest as JSON',
                'GET /api/v1/templates': 'List available templates',
                'POST /api/v1/templates/{name}': 'Create project from template',
                'POST /api/v1/builder/*': 'Build manifest components',
                'POST /api/v1/validate': 'Validate manifest',
                'GET /api/v1/export': 'Export all projects',
                'POST /api/v1/import': 'Import projects'
            },
            'examples': {
                'create_project': {
                    'method': 'POST',
                    'url': '/api/v1/projects',
                    'body': {
                        'name': 'my-service',
                        'description': 'My awesome service',
                        'version': '1.0.0',
                        'author': 'developer@example.com',
                        'tags': ['api', 'microservice']
                    }
                },
                'update_manifest': {
                    'method': 'POST',
                    'url': '/api/v1/projects/{id}/manifest',
                    'body': {
                        'name': 'my-service',
                        'version': '1.0.0',
                        'server': {'host': '0.0.0.0', 'port': 8000},
                        'endpoints': [
                            {'path': '/api/users', 'method': 'get', 'handler': 'handlers.users.list'}
                        ]
                    }
                }
            }
        }
        
        # Return HTML documentation for browsers, JSON for API clients
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            html_docs = self._generate_html_docs(docs)
            return web.Response(text=html_docs, content_type='text/html')
        else:
            return json_response(docs)
        
    def _generate_html_docs(self, docs: Dict[str, Any]) -> str:
        """Generate HTML documentation"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{docs['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .endpoint {{ margin: 20px 0; padding: 10px; background: #f5f5f5; }}
                .example {{ background: #e8f4f8; padding: 10px; margin: 10px 0; }}
                pre {{ background: #f0f0f0; padding: 10px; overflow: auto; }}
                h1 {{ color: #333; }}
                h2 {{ color: #555; }}
                .method {{ color: #007acc; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>{docs['title']} v{docs['version']}</h1>
            <p>{docs['description']}</p>
            
            <h2>Endpoints</h2>
        """
        
        for endpoint, desc in docs['endpoints'].items():
            method = endpoint.split(' ')[0]
            path = endpoint.split(' ', 1)[1] if ' ' in endpoint else endpoint
            html += f'<div class="endpoint"><span class="method">{method}</span> {path} - {desc}</div>'
            
        html += """
            <h2>Examples</h2>
        """
        
        for name, example in docs['examples'].items():
            html += f"""
            <div class="example">
                <h3>{name.replace('_', ' ').title()}</h3>
                <p><span class="method">{example['method']}</span> {example['url']}</p>
                <pre>{json.dumps(example.get('body', {}), indent=2)}</pre>
            </div>
            """
            
        html += """
        </body>
        </html>
        """
        return html
        
    async def list_projects(self, request: Request) -> Response:
        """List all projects with optional filtering"""
        status = request.query.get('status')
        tags = request.query.get('tags')
        if tags:
            tags = [t.strip() for t in tags.split(',')]
            
        projects = self.store.list_projects(status=status, tags=tags)
        return json_response([asdict(p) for p in projects])
        
    async def create_project(self, request: Request) -> Response:
        """Create new project"""
        try:
            data = await request.json()
            
            # Generate unique ID
            import uuid
            project_id = str(uuid.uuid4())
            
            # Create project
            project = ManifestProject(
                id=project_id,
                name=data.get('name', 'unnamed-service'),
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                author=data.get('author', 'anonymous'),
                tags=data.get('tags', []),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                manifest=data.get('manifest', {
                    'name': data.get('name', 'unnamed-service'),
                    'version': data.get('version', '1.0.0'),
                    'framework': 'proserve'
                })
            )
            
            self.store.create_project(project)
            
            return json_response(asdict(project), status=201)
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def get_project(self, request: Request) -> Response:
        """Get project by ID"""
        project_id = request.match_info['project_id']
        project = self.store.get_project(project_id)
        
        if not project:
            return json_response({'error': 'Project not found'}, status=404)
            
        return json_response(asdict(project))
        
    async def update_project(self, request: Request) -> Response:
        """Update existing project"""
        try:
            project_id = request.match_info['project_id']
            data = await request.json()
            
            existing = self.store.get_project(project_id)
            if not existing:
                return json_response({'error': 'Project not found'}, status=404)
                
            # Update project fields
            updated = ManifestProject(
                id=project_id,
                name=data.get('name', existing.name),
                description=data.get('description', existing.description),
                version=data.get('version', existing.version),
                author=data.get('author', existing.author),
                tags=data.get('tags', existing.tags),
                status=data.get('status', existing.status),
                created_at=existing.created_at,
                updated_at=datetime.now().isoformat(),
                manifest=data.get('manifest', existing.manifest)
            )
            
            self.store.update_project(project_id, updated)
            return json_response(asdict(updated))
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def delete_project(self, request: Request) -> Response:
        """Delete project by ID"""
        project_id = request.match_info['project_id']
        
        if not self.store.delete_project(project_id):
            return json_response({'error': 'Project not found'}, status=404)
            
        return json_response({'message': 'Project deleted successfully'})
        
    async def update_manifest(self, request: Request) -> Response:
        """Update project manifest"""
        try:
            project_id = request.match_info['project_id']
            manifest_data = await request.json()
            
            project = self.store.get_project(project_id)
            if not project:
                return json_response({'error': 'Project not found'}, status=404)
                
            # Update manifest
            project.manifest = manifest_data
            project.updated_at = datetime.now().isoformat()
            
            self.store.update_project(project_id, project)
            
            return json_response({
                'message': 'Manifest updated successfully',
                'manifest': manifest_data
            })
            
        except Exception as e:
            logger.error(f"Error updating manifest: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def export_yaml(self, request: Request) -> Response:
        """Export manifest as YAML"""
        project_id = request.match_info['project_id']
        project = self.store.get_project(project_id)
        
        if not project:
            return json_response({'error': 'Project not found'}, status=404)
            
        try:
            import yaml
            yaml_content = yaml.dump(project.manifest, default_flow_style=False)
            
            return web.Response(
                text=yaml_content,
                content_type='application/x-yaml',
                headers={'Content-Disposition': f'attachment; filename="{project.name}.yml"'}
            )
            
        except Exception as e:
            logger.error(f"Error exporting YAML: {e}")
            return json_response({'error': str(e)}, status=500)
            
    async def export_json(self, request: Request) -> Response:
        """Export manifest as JSON"""
        project_id = request.match_info['project_id']
        project = self.store.get_project(project_id)
        
        if not project:
            return json_response({'error': 'Project not found'}, status=404)
            
        return web.Response(
            text=json.dumps(project.manifest, indent=2),
            content_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="{project.name}.json"'}
        )
        
    async def list_templates(self, request: Request) -> Response:
        """List available templates"""
        templates = {}
        for name, template_class in TEMPLATES.items():
            templates[name] = {
                'name': name,
                'description': template_class.__doc__ or f"Template for {name} services",
                'class': template_class.__name__
            }
            
        return json_response(templates)
        
    async def create_from_template(self, request: Request) -> Response:
        """Create project from template"""
        try:
            template_name = request.match_info['template_name']
            data = await request.json()
            
            if template_name not in TEMPLATES:
                return json_response({'error': f'Template not found: {template_name}'}, status=404)
                
            # Create manifest from template
            builder = from_template(template_name, **data)
            manifest = builder.build()
            
            # Create project
            import uuid
            project_id = str(uuid.uuid4())
            
            project = ManifestProject(
                id=project_id,
                name=data.get('name', f'{template_name}-service'),
                description=data.get('description', f'Service created from {template_name} template'),
                version=data.get('version', '1.0.0'),
                author=data.get('author', 'anonymous'),
                tags=data.get('tags', [template_name]),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                manifest=manifest
            )
            
            self.store.create_project(project)
            
            return json_response(asdict(project), status=201)
            
        except Exception as e:
            logger.error(f"Error creating from template: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def build_endpoint(self, request: Request) -> Response:
        """Build endpoint configuration"""
        try:
            data = await request.json()
            
            builder = EndpointBuilder(
                path=data.get('path', '/'),
                method=data.get('method', 'GET')
            )
            
            if 'handler' in data:
                builder.with_handler(data['handler'])
            if 'middleware' in data:
                builder.with_middleware(*data['middleware'])
            if 'auth' in data:
                builder.with_auth(**data['auth'])
            if 'rate_limit' in data:
                builder.with_rate_limit(**data['rate_limit'])
                
            config = builder.build()
            return json_response(config)
            
        except Exception as e:
            logger.error(f"Error building endpoint: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def build_database(self, request: Request) -> Response:
        """Build database configuration"""
        try:
            data = await request.json()
            
            builder = DatabaseBuilder(data.get('type', 'postgresql'))
            
            if 'url' in data:
                builder.with_url(data['url'])
            if 'host' in data and 'port' in data:
                builder.with_host(data['host'], data['port'])
            if 'credentials' in data:
                builder.with_credentials(**data['credentials'])
            if 'pool' in data:
                builder.with_pool(**data['pool'])
                
            config = builder.build()
            return json_response(config)
            
        except Exception as e:
            logger.error(f"Error building database: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def build_logging(self, request: Request) -> Response:
        """Build logging configuration"""
        try:
            data = await request.json()
            
            builder = LoggingBuilder(level=data.get('level', 'INFO'))
            
            if 'format' in data:
                builder.with_format(data['format'])
            if 'handlers' in data:
                for handler in data['handlers']:
                    handler_type = handler.get('type')
                    if handler_type == 'console':
                        builder.with_console_handler(**handler.get('config', {}))
                    elif handler_type == 'file':
                        builder.with_file_handler(**handler.get('config', {}))
                        
            config = builder.build()
            return json_response(config)
            
        except Exception as e:
            logger.error(f"Error building logging: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def build_grpc_service(self, request: Request) -> Response:
        """Build gRPC service configuration"""
        try:
            data = await request.json()
            
            builder = GrpcServiceBuilder(data.get('name', 'Service'))
            
            if 'package' in data:
                builder.with_package(data['package'])
            if 'methods' in data:
                for method in data['methods']:
                    builder.with_method(**method)
                    
            config = builder.build()
            return json_response(config)
            
        except Exception as e:
            logger.error(f"Error building gRPC service: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def validate_manifest(self, request: Request) -> Response:
        """Validate manifest configuration"""
        try:
            manifest_data = await request.json()
            
            # Try to create ServiceManifest instance for validation
            try:
                manifest = ServiceManifest(**manifest_data)
                return json_response({
                    'valid': True,
                    'message': 'Manifest is valid',
                    'manifest': asdict(manifest)
                })
            except Exception as validation_error:
                return json_response({
                    'valid': False,
                    'error': str(validation_error),
                    'field_errors': []  # Could be enhanced with field-level validation
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def export_all(self, request: Request) -> Response:
        """Export all projects"""
        try:
            export_data = self.store.export_all()
            
            return web.Response(
                text=json.dumps(export_data, indent=2),
                content_type='application/json',
                headers={'Content-Disposition': 'attachment; filename="proserve-projects.json"'}
            )
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return json_response({'error': str(e)}, status=500)
            
    async def import_all(self, request: Request) -> Response:
        """Import projects from JSON"""
        try:
            import_data = await request.json()
            
            self.store.import_all(import_data)
            
            return json_response({
                'message': f'Successfully imported {len(import_data)} projects',
                'count': len(import_data)
            })
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return json_response({'error': str(e)}, status=400)
            
    async def start(self) -> None:
        """Start the API server"""
        app = self.setup_routes()
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"ProServe Manifest API Server started on http://{self.host}:{self.port}")
        logger.info(f"API Documentation: http://{self.host}:{self.port}/docs")


# Convenience functions
async def start_api_server(host: str = '0.0.0.0', port: int = 8080, 
                          cors_enabled: bool = True) -> ManifestAPIServer:
    """Start manifest API server"""
    server = ManifestAPIServer(host, port, cors_enabled)
    await server.start()
    return server


def create_manifest_api(host: str = '0.0.0.0', port: int = 8080) -> ManifestAPIServer:
    """Create manifest API server instance"""
    return ManifestAPIServer(host, port)


# CLI runner for the API server
async def main():
    """CLI entry point for API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ProServe Manifest API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--cors', action='store_true', help='Enable CORS')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Start server
    server = await start_api_server(args.host, args.port, args.cors)
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down API server...")


if __name__ == '__main__':
    asyncio.run(main())
