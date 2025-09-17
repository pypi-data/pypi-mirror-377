"""
ProServe Static File Handler - Static File Serving and Management
Handles static file serving, directory mapping, and file caching
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from aiohttp import web
import structlog


class StaticFileHandler:
    """Handles static file serving with caching and security features"""
    
    def __init__(self, service_core, manifest):
        """Initialize static file handler"""
        self.service_core = service_core
        self.manifest = manifest
        self.logger = service_core.get_logger()
        self.app = service_core.get_app()
        
        # Static file configuration
        self.static_directories = {}
        self.static_files = {}
        self.enable_directory_listing = False
        
        # Security settings
        self.allowed_extensions = set()
        self.blocked_paths = set()
        
        # Setup static file serving
        self._setup_static_files()
    
    def _setup_static_files(self):
        """Setup static file serving based on manifest configuration"""
        static_config = getattr(self.manifest, 'static', None)
        if not static_config:
            return
        
        # Setup static directories
        static_dirs = static_config.get('directories', [])
        for dir_config in static_dirs:
            self._setup_static_directory(dir_config)
        
        # Setup individual static files
        static_files = static_config.get('files', [])
        for file_config in static_files:
            self._setup_static_file(file_config)
        
        # Setup security settings
        self._setup_security_settings(static_config)
        
        # Setup default routes if specified
        self._setup_default_routes(static_config)
    
    def _setup_static_directory(self, dir_config: Dict[str, Any]):
        """Setup serving for a static directory"""
        local_path = dir_config['path']
        url_path = dir_config.get('url_path', '/static')
        
        # Convert relative path to absolute
        if not os.path.isabs(local_path):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                local_path = str(manifest_dir / local_path)
            else:
                local_path = str(Path.cwd() / local_path)
        
        if not Path(local_path).exists():
            self.logger.warning(f"Static directory does not exist: {local_path}")
            return
        
        # Add static resource
        self.app.router.add_static(url_path, local_path, name='static')
        
        # Track the directory
        self.static_directories[url_path] = {
            'local_path': local_path,
            'config': dir_config
        }
        
        self.logger.info(f"Static directory registered: {url_path} -> {local_path}")
    
    def _setup_static_file(self, file_config: Dict[str, Any]):
        """Setup serving for an individual static file"""
        local_file = file_config['file']
        url_path = file_config['url_path']
        
        # Convert relative path to absolute
        if not os.path.isabs(local_file):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                local_file = str(manifest_dir / local_file)
            else:
                local_file = str(Path.cwd() / local_file)
        
        if not Path(local_file).exists():
            self.logger.warning(f"Static file does not exist: {local_file}")
            return
        
        # Create handler for the file
        async def file_handler(request):
            return await self._serve_file(local_file, file_config)
        
        # Register route
        self.app.router.add_get(url_path, file_handler)
        
        # Track the file
        self.static_files[url_path] = {
            'local_file': local_file,
            'config': file_config,
            'handler': file_handler
        }
        
        self.logger.info(f"Static file registered: {url_path} -> {local_file}")
    
    def _setup_security_settings(self, static_config: Dict[str, Any]):
        """Setup security settings for static file serving"""
        security = static_config.get('security', {})
        
        # Allowed file extensions
        allowed_exts = security.get('allowed_extensions', [])
        if allowed_exts:
            self.allowed_extensions = set(ext.lower() for ext in allowed_exts)
        
        # Blocked paths
        blocked_paths = security.get('blocked_paths', [])
        self.blocked_paths = set(blocked_paths)
        
        # Directory listing
        self.enable_directory_listing = security.get('enable_directory_listing', False)
        
        self.logger.info("Static file security settings configured")
    
    def _setup_default_routes(self, static_config: Dict[str, Any]):
        """Setup default routes for common patterns"""
        # Index file serving
        index_file = static_config.get('index_file')
        if index_file:
            async def index_handler(request):
                return await self._serve_index_file(index_file)
            
            self.app.router.add_get('/', index_handler)
            self.logger.info(f"Index route registered: / -> {index_file}")
        
        # Favicon
        favicon = static_config.get('favicon')
        if favicon:
            async def favicon_handler(request):
                return await self._serve_file(favicon, {'cache_control': 'max-age=86400'})
            
            self.app.router.add_get('/favicon.ico', favicon_handler)
            self.logger.info(f"Favicon route registered: /favicon.ico -> {favicon}")
    
    async def _serve_file(self, file_path: str, config: Dict[str, Any] = None) -> web.Response:
        """Serve a single file with proper headers and caching"""
        config = config or {}
        
        try:
            # Security checks
            if not self._is_file_allowed(file_path):
                raise web.HTTPForbidden(text="File access denied")
            
            if not Path(file_path).exists():
                raise web.HTTPNotFound(text="File not found")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create response
            response = web.FileResponse(
                path=file_path,
                headers=self._get_file_headers(file_path, config)
            )
            
            # Set content type
            response.content_type = content_type
            
            return response
            
        except (OSError, IOError) as e:
            self.logger.error(f"Error serving file {file_path}: {e}")
            raise web.HTTPInternalServerError(text="Error serving file")
    
    async def _serve_index_file(self, index_file: str) -> web.Response:
        """Serve index file with special handling"""
        # Convert relative path to absolute
        if not os.path.isabs(index_file):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                index_file = str(manifest_dir / index_file)
            else:
                index_file = str(Path.cwd() / index_file)
        
        return await self._serve_file(index_file, {'cache_control': 'no-cache'})
    
    def _is_file_allowed(self, file_path: str) -> bool:
        """Check if file is allowed to be served based on security settings"""
        file_path = Path(file_path)
        
        # Check blocked paths
        for blocked_path in self.blocked_paths:
            if blocked_path in str(file_path):
                return False
        
        # Check allowed extensions
        if self.allowed_extensions:
            file_ext = file_path.suffix.lower()
            if file_ext not in self.allowed_extensions:
                return False
        
        # Check for hidden files (starting with .)
        if file_path.name.startswith('.'):
            return False
        
        return True
    
    def _get_file_headers(self, file_path: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Get appropriate headers for file serving"""
        headers = {}
        
        # Cache control
        cache_control = config.get('cache_control', 'public, max-age=3600')
        headers['Cache-Control'] = cache_control
        
        # Security headers
        headers['X-Content-Type-Options'] = 'nosniff'
        
        # Custom headers from config
        custom_headers = config.get('headers', {})
        headers.update(custom_headers)
        
        return headers
    
    async def serve_directory_listing(self, request, directory_path: str) -> web.Response:
        """Serve directory listing if enabled"""
        if not self.enable_directory_listing:
            raise web.HTTPForbidden(text="Directory listing disabled")
        
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                raise web.HTTPNotFound(text="Directory not found")
            
            # Generate directory listing HTML
            html_content = self._generate_directory_listing_html(directory, request.path)
            
            return web.Response(
                text=html_content,
                content_type='text/html',
                headers={'Cache-Control': 'no-cache'}
            )
            
        except Exception as e:
            self.logger.error(f"Error serving directory listing: {e}")
            raise web.HTTPInternalServerError(text="Error generating directory listing")
    
    def _generate_directory_listing_html(self, directory: Path, url_path: str) -> str:
        """Generate HTML for directory listing"""
        items = []
        
        # Add parent directory link if not root
        if url_path != '/':
            parent_path = str(Path(url_path).parent)
            items.append(f'<li><a href="{parent_path}">../</a></li>')
        
        # Add directory contents
        try:
            for item in sorted(directory.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                item_url = f"{url_path.rstrip('/')}/{item.name}"
                
                if item.is_dir():
                    items.append(f'<li><a href="{item_url}/">{item.name}/</a></li>')
                else:
                    size = item.stat().st_size
                    items.append(f'<li><a href="{item_url}">{item.name}</a> ({size} bytes)</li>')
        
        except PermissionError:
            items.append('<li>Permission denied</li>')
        
        items_html = '\n'.join(items)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Directory Listing: {url_path}</title>
            <style>
                body {{ font-family: monospace; margin: 40px; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ margin: 5px 0; }}
                a {{ text-decoration: none; color: #0066cc; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Directory Listing: {url_path}</h1>
            <ul>
                {items_html}
            </ul>
        </body>
        </html>
        """
    
    def add_static_directory(self, url_path: str, local_path: str, **kwargs):
        """Add a static directory at runtime"""
        dir_config = {
            'path': local_path,
            'url_path': url_path,
            **kwargs
        }
        self._setup_static_directory(dir_config)
    
    def add_static_file(self, url_path: str, local_file: str, **kwargs):
        """Add a static file at runtime"""
        file_config = {
            'file': local_file,
            'url_path': url_path,
            **kwargs
        }
        self._setup_static_file(file_config)
    
    def get_static_info(self) -> Dict[str, Any]:
        """Get information about configured static files and directories"""
        return {
            'directories': {
                url_path: {
                    'local_path': info['local_path'],
                    'exists': Path(info['local_path']).exists()
                }
                for url_path, info in self.static_directories.items()
            },
            'files': {
                url_path: {
                    'local_file': info['local_file'],
                    'exists': Path(info['local_file']).exists()
                }
                for url_path, info in self.static_files.items()
            },
            'security': {
                'allowed_extensions': list(self.allowed_extensions),
                'blocked_paths': list(self.blocked_paths),
                'directory_listing_enabled': self.enable_directory_listing
            }
        }
