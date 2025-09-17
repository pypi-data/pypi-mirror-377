"""
ProServe Static Website Server - Main Static Website Hosting Server
Orchestrates cache management, CDN resources, and API proxying for static websites
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Optional, Any
from aiohttp import web
import structlog

from .cache_manager import CacheManager, CachePolicy
from .cdn_manager import CDNManager, CDNResource
from .api_proxy import APIProxy, APIProxyRule

logger = structlog.get_logger(__name__)


class StaticWebsiteServer:
    """Main static website hosting server with integrated caching, CDN, and API proxy"""
    
    def __init__(self, 
                 static_dir: str = "static",
                 cache_dir: str = ".proserve_cache",
                 default_policy: Optional[CachePolicy] = None):
        
        self.static_dir = Path(static_dir)
        self.static_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.cache_manager = CacheManager(cache_dir)
        self.cdn_manager = None  # Will be initialized in async context
        self.api_proxy = None    # Will be initialized in async context
        
        self.default_policy = default_policy or CachePolicy()
        
        # Initialize mimetypes
        mimetypes.init()
        
        # Configuration
        self.index_files = ['index.html', 'index.htm']
        self.error_pages = {
            404: 'errors/404.html',
            500: 'errors/500.html'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        # Initialize async components
        self.cdn_manager = CDNManager(self.cache_manager.cache)
        await self.cdn_manager.__aenter__()
        
        self.api_proxy = APIProxy()
        await self.api_proxy.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.api_proxy:
            await self.api_proxy.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.cdn_manager:
            await self.cdn_manager.__aexit__(exc_type, exc_val, exc_tb)
    
    def add_cache_policy(self, name: str, policy: CachePolicy):
        """Add a named cache policy"""
        self.cache_manager.add_policy(name, policy)
    
    def add_cdn_resource(self, local_path: str, resource: CDNResource):
        """Add CDN resource"""
        if self.cdn_manager:
            self.cdn_manager.add_resource(local_path, resource)
        else:
            logger.warning("CDN manager not initialized")
    
    def add_api_proxy_rule(self, rule: APIProxyRule):
        """Add API proxy rule"""
        if self.api_proxy:
            self.api_proxy.add_rule(rule)
        else:
            logger.warning("API proxy not initialized")
    
    def set_index_files(self, index_files: list):
        """Set list of index files to look for"""
        self.index_files = index_files
    
    def set_error_page(self, status_code: int, file_path: str):
        """Set custom error page for HTTP status code"""
        self.error_pages[status_code] = file_path
    
    async def serve_static_file(self, request: web.Request) -> web.Response:
        """Serve static file with caching and CDN fallback"""
        try:
            # Get requested path
            path = request.match_info.get('path', '')
            if path.startswith('/'):
                path = path[1:]  # Remove leading slash
            
            # Security check - prevent path traversal
            if '..' in path or path.startswith('/'):
                raise web.HTTPForbidden(text="Path traversal not allowed")
            
            # Check if it's a CDN resource first
            if self.cdn_manager and path in self.cdn_manager.resources:
                content = await self.cdn_manager.get_resource(path)
                if content:
                    content_type = self.get_content_type(path)
                    headers = {
                        'Content-Type': content_type,
                        'Cache-Control': 'public, max-age=86400',
                        'X-Served-By': 'ProServe-CDN'
                    }
                    return web.Response(body=content, headers=headers)
            
            # Look for local static file
            file_path = self.static_dir / path
            
            # If path is a directory, look for index files
            if file_path.is_dir():
                for index_file in self.index_files:
                    index_path = file_path / index_file
                    if index_path.exists():
                        file_path = index_path
                        break
                else:
                    # No index file found, return 404
                    return await self._serve_error_page(request, 404)
            
            # Check if file exists
            if not file_path.exists() or not file_path.is_file():
                return await self._serve_error_page(request, 404)
            
            # Check if file should be cached
            policy_name = request.query.get('cache_policy')  # Allow override via query param
            
            # Try to get from cache first
            file_url = f"file://{file_path}"
            cached_content = self.cache_manager.get_cached_content(file_url, policy_name)
            
            if cached_content:
                logger.debug(f"Serving cached file: {path}")
                content_type = self.get_content_type(str(file_path))
                headers = {
                    'Content-Type': content_type,
                    'Cache-Control': f'public, max-age={self.default_policy.max_age}',
                    'X-Served-By': 'ProServe-Cache'
                }
                return web.Response(body=cached_content, headers=headers)
            
            # Read file from disk
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Cache the file if policy allows
            if self.cache_manager.should_cache_file(str(file_path)):
                headers_to_cache = {
                    'Content-Type': self.get_content_type(str(file_path)),
                    'Last-Modified': str(file_path.stat().st_mtime)
                }
                self.cache_manager.cache_content(file_url, content, headers_to_cache, policy_name)
            
            # Prepare response headers
            content_type = self.get_content_type(str(file_path))
            headers = {
                'Content-Type': content_type,
                'Cache-Control': f'public, max-age={self.default_policy.max_age}',
                'Last-Modified': str(file_path.stat().st_mtime),
                'X-Served-By': 'ProServe-Static'
            }
            
            # Add ETag if enabled
            if self.default_policy.etag_validation:
                import hashlib
                etag = hashlib.md5(content).hexdigest()
                headers['ETag'] = f'"{etag}"'
                
                # Check If-None-Match header
                if_none_match = request.headers.get('If-None-Match')
                if if_none_match and etag in if_none_match:
                    return web.Response(status=304, headers=headers)
            
            logger.debug(f"Serving static file: {path} ({len(content)} bytes)")
            return web.Response(body=content, headers=headers)
            
        except web.HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error serving static file {path}: {e}")
            return await self._serve_error_page(request, 500)
    
    async def handle_api_proxy(self, request: web.Request) -> web.Response:
        """Handle API proxy requests"""
        try:
            if not self.api_proxy:
                return web.json_response({'error': 'API proxy not available'}, status=503)
            
            # Parse query parameters
            query_params = dict(request.query)
            
            # Match proxy rule
            rule = self.api_proxy.match_rule(
                request.path, 
                request.method, 
                dict(request.headers),
                query_params
            )
            
            if not rule:
                return web.json_response({'error': 'No proxy rule matched'}, status=404)
            
            # Handle CORS preflight
            if request.method == 'OPTIONS':
                return await self.api_proxy.handle_preflight(request, rule)
            
            # Proxy the request
            return await self.api_proxy.proxy_request(request, rule)
            
        except Exception as e:
            logger.error(f"API proxy error: {e}")
            return web.json_response({'error': 'API proxy failed'}, status=502)
    
    async def _serve_error_page(self, request: web.Request, status_code: int) -> web.Response:
        """Serve custom error page or default error response"""
        try:
            if status_code in self.error_pages:
                error_file = self.static_dir / self.error_pages[status_code]
                if error_file.exists():
                    with open(error_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return web.Response(
                        text=content,
                        status=status_code,
                        content_type='text/html'
                    )
            
            # Default error response
            error_messages = {
                404: 'Not Found',
                500: 'Internal Server Error',
                502: 'Bad Gateway',
                503: 'Service Unavailable'
            }
            
            message = error_messages.get(status_code, 'Error')
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{status_code} {message}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }}
                    h1 {{ color: #333; }}
                    p {{ color: #666; }}
                </style>
            </head>
            <body>
                <h1>{status_code} {message}</h1>
                <p>The requested resource could not be found or is temporarily unavailable.</p>
                <p><a href="/">Return to Home</a></p>
            </body>
            </html>
            """
            
            return web.Response(
                text=html_content,
                status=status_code,
                content_type='text/html'
            )
            
        except Exception as e:
            logger.error(f"Error serving error page: {e}")
            return web.Response(text='Internal Server Error', status=500)
    
    def get_content_type(self, path: str) -> str:
        """Get MIME type for file"""
        content_type, _ = mimetypes.guess_type(path)
        return content_type or 'application/octet-stream'
    
    def setup_routes(self, app: web.Application):
        """Setup routes for static server"""
        # API proxy routes (should be first to catch API paths)
        app.router.add_route('*', '/api/{path:.*}', self.handle_api_proxy)
        
        # Static file routes
        app.router.add_get('/', self.serve_static_file)  # Root index
        app.router.add_get('/{path:.*}', self.serve_static_file)  # All other paths
        
        logger.info("Static website server routes configured")
    
    async def preload_cdn_resources(self, resources: list = None) -> Dict[str, Any]:
        """Preload CDN resources"""
        if self.cdn_manager:
            return await self.cdn_manager.preload_resources(resources)
        else:
            logger.warning("CDN manager not available")
            return {'error': 'CDN manager not available'}
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        stats = {
            'static_directory': str(self.static_dir),
            'cache_stats': self.cache_manager.get_stats(),
            'cdn_resources': {},
            'proxy_stats': {}
        }
        
        if self.cdn_manager:
            stats['cdn_resources'] = self.cdn_manager.get_resource_info()
        
        if self.api_proxy:
            stats['proxy_stats'] = self.api_proxy.get_proxy_stats()
        
        return stats
    
    async def cleanup_cache(self) -> int:
        """Cleanup expired cache entries"""
        return self.cache_manager.cleanup()


def create_static_website_app(config: Dict[str, Any]) -> web.Application:
    """Create static website application from configuration"""
    # Extract configuration
    static_dir = config.get('static_dir', 'static')
    cache_dir = config.get('cache_dir', '.proserve_cache')
    
    # Create cache policy
    cache_config = config.get('cache', {})
    cache_policy = CachePolicy(
        max_age=cache_config.get('max_age', 86400),
        refresh_on_version_change=cache_config.get('refresh_on_version_change', True),
        etag_validation=cache_config.get('etag_validation', True),
        compress_files=cache_config.get('compress_files', True)
    )
    
    # Create server
    server = StaticWebsiteServer(static_dir, cache_dir, cache_policy)
    
    # Add CDN resources
    cdn_resources = config.get('cdn_resources', [])
    for resource_config in cdn_resources:
        resource = CDNResource(
            url=resource_config['url'],
            local_path=resource_config['local_path'],
            version=resource_config.get('version'),
            fallback_url=resource_config.get('fallback_url'),
            integrity=resource_config.get('integrity')
        )
        server.add_cdn_resource(resource.local_path, resource)
    
    # Add API proxy rules
    proxy_rules = config.get('proxy_rules', [])
    for rule_config in proxy_rules:
        rule = APIProxyRule(
            path_pattern=rule_config['path_pattern'],
            target_url=rule_config['target_url'],
            methods=rule_config.get('methods', ['GET', 'POST', 'PUT', 'DELETE']),
            cors_enabled=rule_config.get('cors_enabled', True),
            rate_limit=rule_config.get('rate_limit'),
            timeout=rule_config.get('timeout', 30)
        )
        server.add_api_proxy_rule(rule)
    
    # Create application
    app = web.Application()
    
    # Setup routes
    async def init_server(app):
        await server.__aenter__()
        server.setup_routes(app)
        app['static_server'] = server
    
    async def cleanup_server(app):
        server = app.get('static_server')
        if server:
            await server.__aexit__(None, None, None)
    
    app.on_startup.append(init_server)
    app.on_cleanup.append(cleanup_server)
    
    return app
