"""
ProServe Static Module - Modular Static File Serving Components
Refactored from monolithic static_server.py into focused, testable modules
"""

from .cache_manager import CachePolicy, StaticFileCache, CacheManager
from .cdn_manager import CDNResource, CDNManager
from .api_proxy import APIProxyRule, APIProxy
from .website_server import StaticWebsiteServer, create_static_website_app

__all__ = [
    # Cache Management
    'CachePolicy',
    'StaticFileCache', 
    'CacheManager',
    
    # CDN Management
    'CDNResource',
    'CDNManager',
    
    # API Proxy
    'APIProxyRule',
    'APIProxy',
    
    # Main Server
    'StaticWebsiteServer',
    'create_static_website_app'
]
