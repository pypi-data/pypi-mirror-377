"""
ProServe API Server - Main API Server Implementation
Coordinates all API components to provide the complete manifest API server
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from aiohttp import web
from aiohttp_cors import setup as cors_setup, CorsConfig
import structlog

from .models import APIResponse
from .storage import AsyncManifestStore, create_async_store
from .endpoints import ManifestAPIEndpoints


logger = structlog.get_logger(__name__)


class ManifestAPIServer:
    """RESTful API server for manifest management"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080, 
                 cors_enabled: bool = True, persist_dir: Optional[Path] = None):
        self.host = host
        self.port = port
        self.cors_enabled = cors_enabled
        
        # Initialize storage
        self.store = create_async_store(persist_dir)
        
        # Initialize endpoints handler
        self.endpoints = ManifestAPIEndpoints(self.store)
        
        # Initialize web application
        self.app = None
        
    def setup_routes(self):
        """Setup API routes"""
        self.app = web.Application()
        
        # Health and documentation endpoints
        self.app.router.add_get('/health', self.endpoints.health_check)
        self.app.router.add_get('/api/docs', self.api_docs)
        
        # Project CRUD endpoints
        self.app.router.add_get('/api/projects', self.endpoints.list_projects)
        self.app.router.add_post('/api/projects', self.endpoints.create_project)
        self.app.router.add_get('/api/projects/{project_id}', self.endpoints.get_project)
        self.app.router.add_put('/api/projects/{project_id}', self.endpoints.update_project)
        self.app.router.add_delete('/api/projects/{project_id}', self.endpoints.delete_project)
        
        # Project operations
        self.app.router.add_put('/api/projects/{project_id}/manifest', self.endpoints.update_manifest)
        self.app.router.add_post('/api/projects/{project_id}/duplicate', self.endpoints.duplicate_project)
        
        # Export endpoints
        self.app.router.add_get('/api/projects/{project_id}/export/yaml', self.endpoints.export_yaml)
        self.app.router.add_get('/api/projects/{project_id}/export/json', self.endpoints.export_json)
        
        # Template endpoints
        self.app.router.add_get('/api/templates', self.endpoints.list_templates)
        self.app.router.add_post('/api/templates/create', self.endpoints.create_from_template)
        
        # Utility endpoints
        self.app.router.add_post('/api/validate', self.endpoints.validate_manifest)
        self.app.router.add_get('/api/search', self.endpoints.search_projects)
        self.app.router.add_get('/api/statistics', self.endpoints.get_statistics)
        
        # Bulk operations
        self.app.router.add_get('/api/export', self.endpoints.export_all)
        self.app.router.add_post('/api/import', self.endpoints.import_all)
        
        # Setup CORS if enabled
        if self.cors_enabled:
            cors_config = CorsConfig()
            cors_config.add("*", {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            })
            cors_setup(self.app, cors_config)
        
        logger.info("API routes configured")
    
    async def api_docs(self, request: web.Request) -> web.Response:
        """API documentation endpoint"""
        docs = {
            'title': 'ProServe Manifest API',
            'version': '1.0.0',
            'description': 'RESTful API for creating and managing ProServe service manifests',
            'base_url': f'http://{self.host}:{self.port}',
            'endpoints': {
                'health': {
                    'GET /health': 'Health check endpoint'
                },
                'projects': {
                    'GET /api/projects': 'List projects with optional filtering',
                    'POST /api/projects': 'Create new project',
                    'GET /api/projects/{id}': 'Get project by ID',
                    'PUT /api/projects/{id}': 'Update project',
                    'DELETE /api/projects/{id}': 'Delete project',
                    'PUT /api/projects/{id}/manifest': 'Update project manifest',
                    'POST /api/projects/{id}/duplicate': 'Duplicate project'
                },
                'export': {
                    'GET /api/projects/{id}/export/yaml': 'Export manifest as YAML',
                    'GET /api/projects/{id}/export/json': 'Export manifest as JSON'
                },
                'templates': {
                    'GET /api/templates': 'List available templates',
                    'POST /api/templates/create': 'Create project from template'
                },
                'utilities': {
                    'POST /api/validate': 'Validate manifest configuration',
                    'GET /api/search?q={query}': 'Search projects',
                    'GET /api/statistics': 'Get API statistics'
                },
                'bulk': {
                    'GET /api/export': 'Export all projects',
                    'POST /api/import': 'Import projects from JSON'
                }
            },
            'query_parameters': {
                'list_projects': {
                    'status': 'Filter by status (draft, published, archived)',
                    'author': 'Filter by author',
                    'tags': 'Filter by tags (comma-separated)',
                    'name_contains': 'Filter by name substring',
                    'created_after': 'Filter by creation date',
                    'created_before': 'Filter by creation date',
                    'summaries': 'Return summaries only (true/false)',
                    'page': 'Page number for pagination',
                    'per_page': 'Items per page'
                },
                'search': {
                    'q': 'Search query (required)',
                    'summaries': 'Return summaries only (true/false)'
                },
                'import': {
                    'overwrite': 'Overwrite existing projects (true/false)'
                }
            },
            'response_format': {
                'success': {
                    'success': True,
                    'data': '...',
                    'message': 'Optional success message',
                    'timestamp': 'ISO timestamp'
                },
                'error': {
                    'success': False,
                    'error': 'Error description',
                    'message': 'Optional error message',
                    'timestamp': 'ISO timestamp'
                }
            }
        }
        
        # Check if HTML format is requested
        accept_header = request.headers.get('Accept', '')
        if 'text/html' in accept_header:
            html_content = self._generate_html_docs(docs)
            return web.Response(text=html_content, content_type='text/html')
        else:
            return web.json_response(APIResponse.success_response(docs).to_dict())
    
    def _generate_html_docs(self, docs: dict) -> str:
        """Generate HTML documentation"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{docs['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #333; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .method {{ font-weight: bold; color: #007acc; }}
                .description {{ color: #666; margin-left: 20px; }}
                .section {{ margin: 30px 0; }}
                code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }}
                pre {{ background: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>{docs['title']}</h1>
            <p><strong>Version:</strong> {docs['version']}</p>
            <p><strong>Description:</strong> {docs['description']}</p>
            <p><strong>Base URL:</strong> <code>{docs['base_url']}</code></p>
            
            <div class="section">
                <h2>Endpoints</h2>
        """
        
        for category, endpoints in docs['endpoints'].items():
            html += f"<h3>{category.title()}</h3>"
            for endpoint, description in endpoints.items():
                method = endpoint.split(' ')[0]
                path = endpoint.split(' ', 1)[1] if ' ' in endpoint else endpoint
                html += f"""
                <div class="endpoint">
                    <span class="method">{method}</span> <code>{path}</code>
                    <div class="description">{description}</div>
                </div>
                """
        
        html += """
            </div>
            
            <div class="section">
                <h2>Query Parameters</h2>
        """
        
        for endpoint, params in docs['query_parameters'].items():
            html += f"<h3>{endpoint.replace('_', ' ').title()}</h3>"
            for param, description in params.items():
                html += f"<p><code>{param}</code>: {description}</p>"
        
        html += """
            </div>
            
            <div class="section">
                <h2>Response Format</h2>
                <h3>Success Response</h3>
                <pre>{
    "success": true,
    "data": {...},
    "message": "Optional success message",
    "timestamp": "2024-01-01T00:00:00.000Z"
}</pre>
                
                <h3>Error Response</h3>
                <pre>{
    "success": false,
    "error": "Error description",
    "message": "Optional error message", 
    "timestamp": "2024-01-01T00:00:00.000Z"
}</pre>
            </div>
            
        </body>
        </html>
        """
        
        return html
    
    async def start(self):
        """Start the API server"""
        logger.info(f"Starting ProServe Manifest API server on {self.host}:{self.port}")
        
        # Setup routes
        self.setup_routes()
        
        # Create and start runner
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"API server started at http://{self.host}:{self.port}")
        logger.info(f"API documentation available at http://{self.host}:{self.port}/api/docs")
        
        return runner
    
    async def stop(self, runner):
        """Stop the API server"""
        logger.info("Stopping API server...")
        await runner.cleanup()
        logger.info("API server stopped")


# Convenience functions
async def start_api_server(host: str = '0.0.0.0', port: int = 8080, 
                          cors_enabled: bool = True, persist_dir: Optional[Path] = None):
    """Start manifest API server"""
    server = ManifestAPIServer(host, port, cors_enabled, persist_dir)
    runner = await server.start()
    
    try:
        # Keep server running
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour at a time
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.stop(runner)


def create_manifest_api(host: str = '0.0.0.0', port: int = 8080, 
                       persist_dir: Optional[Path] = None) -> ManifestAPIServer:
    """Create manifest API server instance"""
    return ManifestAPIServer(host, port, persist_dir=persist_dir)


# CLI runner for the API server
async def main():
    """CLI entry point for API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ProServe Manifest API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--no-cors', action='store_true', help='Disable CORS')
    parser.add_argument('--persist-dir', type=Path, help='Directory for persistent storage')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start server
    await start_api_server(
        host=args.host,
        port=args.port,
        cors_enabled=not args.no_cors,
        persist_dir=args.persist_dir
    )


if __name__ == '__main__':
    asyncio.run(main())
