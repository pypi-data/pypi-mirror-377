"""
ProServe Static Server - Simplified and Modular
New streamlined static server that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular static system.
The heavy lifting is done by the static/ package modules:
- static/cache_manager.py - Cache policies and management
- static/cdn_manager.py - CDN resource management
- static/api_proxy.py - API proxy functionality
- static/website_server.py - Main static website server

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the new modular static components
from .static import (
    CachePolicy,
    StaticFileCache,
    CacheManager,
    CDNResource,
    CDNManager,
    APIProxyRule,
    APIProxy,
    StaticWebsiteServer,
    create_static_website_app
)

# Legacy compatibility - expose the main classes
__all__ = [
    'CachePolicy',
    'StaticFileCache',
    'CacheManager',
    'CDNResource', 
    'CDNManager',
    'APIProxyRule',
    'APIProxy',
    'StaticWebsiteServer',
    'create_static_website_app'
]
