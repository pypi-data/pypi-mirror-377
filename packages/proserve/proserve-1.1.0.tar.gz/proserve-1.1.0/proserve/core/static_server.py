"""
ProServe Static Website Hosting System
Advanced static file serving with cache management, CDN integration, and API proxying
"""

import os
import json
import asyncio
import hashlib
import mimetypes
import time
import re
import importlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin, parse_qs
import aiohttp
import aiofiles
from aiohttp import web, ClientSession
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class CachePolicy:
    """Cache policy configuration for static files"""
    max_age: int = 86400  # 24 hours default
    refresh_on_version_change: bool = True
    refresh_on_startup: bool = False
    etag_validation: bool = True
    last_modified_validation: bool = True
    compress_files: bool = True
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.html', '.css', '.js', '.json', '.xml', '.txt',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot'
    ])

@dataclass 
class CDNResource:
    """CDN resource configuration"""
    url: str
    local_path: str
    version: Optional[str] = None
    fallback_url: Optional[str] = None
    integrity: Optional[str] = None  # SRI hash
    headers: Dict[str, str] = field(default_factory=dict)
    cache_policy: Optional[CachePolicy] = None

@dataclass
class APIProxyRule:
    """Advanced API proxy routing rule with header-based routing"""
    path_pattern: str
    target_url: str
    methods: List[str] = field(default_factory=lambda: ['GET', 'POST', 'PUT', 'DELETE'])
    
    # Header-based routing
    headers_filter: Dict[str, str] = field(default_factory=dict)  # Required headers
    headers_match_mode: str = "all"  # "all", "any", "exact"
    
    # Query parameter routing
    query_params_filter: Dict[str, str] = field(default_factory=dict)
    
    # Request/Response transformation
    request_transform: Optional[str] = None  # Python function path
    response_transform: Optional[str] = None  # Python function path
    
    # Security and CORS
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate limiting and circuit breaker
    rate_limit: Optional[int] = None  # requests per minute
    circuit_breaker_enabled: bool = True
    max_failures: int = 5
    failure_timeout: int = 60  # seconds
    
    # Authentication
    auth_required: bool = False
    auth_header: str = "Authorization"
    auth_validator: Optional[str] = None  # Python function path
    
    # Timeout and retry
    timeout: int = 30  # seconds
    retry_count: int = 3
    retry_delay: float = 1.0  # seconds
    
    # Path rewriting
    strip_path_prefix: bool = False
    add_path_prefix: str = ""
    
    # Load balancing (for multiple target URLs)
    target_urls: List[str] = field(default_factory=list)
    load_balance_method: str = "round_robin"  # "round_robin", "random", "least_connections"
    
    # Health checking
    health_check_url: Optional[str] = None
    health_check_interval: int = 60  # seconds

class StaticFileCache:
    """Advanced file caching system with TTL and validation"""
    
    def __init__(self, cache_dir: str = ".proserve_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata: Dict[str, Dict] = {}
        self.load_metadata()
        
    def load_metadata(self):
        """Load cache metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            logger.warning("Failed to load cache metadata", error=str(e))
            self.metadata = {}
    
    def save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error("Failed to save cache metadata", error=str(e))
    
    def get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    async def get_cached_file(self, url: str, policy: CachePolicy) -> Optional[Tuple[bytes, Dict[str, str]]]:
        """Get cached file if valid according to policy"""
        cache_key = self.get_cache_key(url)
        cache_path = self.cache_dir / cache_key
        
        if not cache_path.exists():
            return None
            
        # Check metadata
        metadata = self.metadata.get(cache_key, {})
        cached_time = metadata.get('cached_time', 0)
        
        # Check if cache is expired
        if time.time() - cached_time > policy.max_age:
            logger.debug("Cache expired", url=url, age=time.time() - cached_time)
            return None
            
        try:
            async with aiofiles.open(cache_path, 'rb') as f:
                content = await f.read()
            
            headers = metadata.get('headers', {})
            logger.debug("Cache hit", url=url, size=len(content))
            return content, headers
            
        except Exception as e:
            logger.error("Failed to read cached file", url=url, error=str(e))
            return None
    
    async def cache_file(self, url: str, content: bytes, headers: Dict[str, str], policy: CachePolicy):
        """Cache file with metadata"""
        cache_key = self.get_cache_key(url)
        cache_path = self.cache_dir / cache_key
        
        try:
            # Save file content
            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(content)
            
            # Update metadata
            self.metadata[cache_key] = {
                'url': url,
                'cached_time': time.time(),
                'size': len(content),
                'headers': headers,
                'etag': headers.get('etag'),
                'last_modified': headers.get('last-modified')
            }
            
            self.save_metadata()
            logger.debug("File cached", url=url, cache_key=cache_key, size=len(content))
            
        except Exception as e:
            logger.error("Failed to cache file", url=url, error=str(e))

class CDNManager:
    """CDN resource management with fallback and integrity validation"""
    
    def __init__(self, cache: StaticFileCache):
        self.cache = cache
        self.resources: Dict[str, CDNResource] = {}
        self.session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        self.session = ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_resource(self, local_path: str, resource: CDNResource):
        """Add CDN resource configuration"""
        self.resources[local_path] = resource
        logger.info("CDN resource added", local_path=local_path, url=resource.url)
    
    async def fetch_resource(self, resource: CDNResource) -> Optional[Tuple[bytes, Dict[str, str]]]:
        """Fetch resource from CDN with fallback support"""
        if not self.session:
            self.session = ClientSession()
        
        urls_to_try = [resource.url]
        if resource.fallback_url:
            urls_to_try.append(resource.fallback_url)
        
        for url in urls_to_try:
            try:
                async with self.session.get(url, headers=resource.headers) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Validate integrity if provided
                        if resource.integrity:
                            if not self.validate_integrity(content, resource.integrity):
                                logger.error("Integrity validation failed", url=url)
                                continue
                        
                        headers = dict(response.headers)
                        logger.info("CDN resource fetched", url=url, size=len(content))
                        return content, headers
                        
            except Exception as e:
                logger.error("Failed to fetch CDN resource", url=url, error=str(e))
                continue
        
        return None
    
    def validate_integrity(self, content: bytes, integrity: str) -> bool:
        """Validate SRI integrity hash"""
        try:
            algorithm, expected_hash = integrity.split('-', 1)
            if algorithm == 'sha256':
                actual_hash = hashlib.sha256(content).hexdigest()
                return actual_hash == expected_hash
            elif algorithm == 'sha384':
                actual_hash = hashlib.sha384(content).hexdigest()  
                return actual_hash == expected_hash
        except Exception as e:
            logger.error("Integrity validation error", error=str(e))
        return False
    
    async def get_resource(self, local_path: str) -> Optional[Tuple[bytes, Dict[str, str]]]:
        """Get resource with caching and fallback"""
        if local_path not in self.resources:
            return None
            
        resource = self.resources[local_path]
        policy = resource.cache_policy or CachePolicy()
        
        # Try cache first
        cached = await self.cache.get_cached_file(resource.url, policy)
        if cached:
            return cached
        
        # Fetch from CDN
        fetched = await self.fetch_resource(resource)
        if fetched:
            content, headers = fetched
            await self.cache.cache_file(resource.url, content, headers, policy)
            return fetched
        
        return None

class APIProxy:
    """Advanced API proxy system with header-based routing, load balancing, and circuit breaker"""
    
    def __init__(self):
        self.rules: List[APIProxyRule] = []
        self.session: Optional[ClientSession] = None
        self.rate_limits: Dict[str, List[float]] = {}  # IP -> timestamps
        self.circuit_breakers: Dict[str, Dict] = {}  # URL -> breaker state
        self.load_balancer_state: Dict[str, int] = {}  # Rule -> round robin counter
        self.connection_counts: Dict[str, int] = {}  # URL -> active connections
        self.transform_functions: Dict[str, Callable] = {}  # Cache loaded transform functions
    
    async def __aenter__(self):
        self.session = ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_rule(self, rule: APIProxyRule):
        """Add API proxy rule with validation"""
        # Initialize load balancer state
        rule_key = f"{rule.path_pattern}:{rule.target_url}"
        self.load_balancer_state[rule_key] = 0
        
        # Initialize circuit breaker for each target
        targets = rule.target_urls if rule.target_urls else [rule.target_url]
        for target in targets:
            if target not in self.circuit_breakers:
                self.circuit_breakers[target] = {
                    'failures': 0,
                    'last_failure_time': 0,
                    'state': 'closed'  # closed, open, half_open
                }
        
        self.rules.append(rule)
        logger.info("Advanced API proxy rule added", 
                   pattern=rule.path_pattern, 
                   target=rule.target_url,
                   targets=len(targets),
                   features={
                       'headers_filter': bool(rule.headers_filter),
                       'auth_required': rule.auth_required,
                       'load_balancing': len(targets) > 1,
                       'circuit_breaker': rule.circuit_breaker_enabled,
                       'rate_limiting': rule.rate_limit is not None
                   })
    
    def get_target_url(self, rule: APIProxyRule) -> Optional[str]:
        """Get target URL using load balancing"""
        targets = rule.target_urls if rule.target_urls else [rule.target_url]
        
        if len(targets) == 1:
            return targets[0] if self.is_target_healthy(targets[0], rule) else None
        
        # Load balancing
        rule_key = f"{rule.path_pattern}:{rule.target_url}"
        
        if rule.load_balance_method == "round_robin":
            for _ in range(len(targets)):
                idx = self.load_balancer_state[rule_key] % len(targets)
                self.load_balancer_state[rule_key] += 1
                target = targets[idx]
                if self.is_target_healthy(target, rule):
                    return target
        
        elif rule.load_balance_method == "random":
            import random
            available_targets = [t for t in targets if self.is_target_healthy(t, rule)]
            if available_targets:
                return random.choice(available_targets)
        
        elif rule.load_balance_method == "least_connections":
            available_targets = [(t, self.connection_counts.get(t, 0)) 
                               for t in targets if self.is_target_healthy(t, rule)]
            if available_targets:
                return min(available_targets, key=lambda x: x[1])[0]
        
        return None
    
    def is_target_healthy(self, target_url: str, rule: APIProxyRule) -> bool:
        """Check if target is healthy using circuit breaker"""
        if not rule.circuit_breaker_enabled:
            return True
            
        breaker = self.circuit_breakers.get(target_url, {'state': 'closed'})
        
        if breaker['state'] == 'closed':
            return True
        elif breaker['state'] == 'open':
            # Check if failure timeout has passed
            if time.time() - breaker['last_failure_time'] > rule.failure_timeout:
                breaker['state'] = 'half_open'
                return True
            return False
        elif breaker['state'] == 'half_open':
            return True
        
        return False
    
    def record_success(self, target_url: str):
        """Record successful request"""
        if target_url in self.circuit_breakers:
            self.circuit_breakers[target_url]['failures'] = 0
            self.circuit_breakers[target_url]['state'] = 'closed'
    
    def record_failure(self, target_url: str, rule: APIProxyRule):
        """Record failed request and update circuit breaker"""
        if target_url not in self.circuit_breakers:
            return
            
        breaker = self.circuit_breakers[target_url]
        breaker['failures'] += 1
        breaker['last_failure_time'] = time.time()
        
        if breaker['failures'] >= rule.max_failures:
            breaker['state'] = 'open'
            logger.warning("Circuit breaker opened", 
                         target=target_url, 
                         failures=breaker['failures'])
    
    def check_rate_limit(self, client_ip: str, rule: APIProxyRule) -> bool:
        """Advanced rate limiting with sliding window"""
        if not rule.rate_limit:
            return True
            
        now = time.time()
        minute_ago = now - 60
        
        # Clean old timestamps
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip] = [
                ts for ts in self.rate_limits[client_ip] if ts > minute_ago
            ]
        else:
            self.rate_limits[client_ip] = []
        
        # Check limit
        if len(self.rate_limits[client_ip]) >= rule.rate_limit:
            logger.warning("Rate limit exceeded", client_ip=client_ip, rule=rule.path_pattern)
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        return True
    
    async def authenticate_request(self, request: web.Request, rule: APIProxyRule) -> bool:
        """Authenticate request if required"""
        if not rule.auth_required:
            return True
            
        auth_header = request.headers.get(rule.auth_header)
        if not auth_header:
            return False
            
        if rule.auth_validator:
            validator = await self.load_transform_function(rule.auth_validator)
            if validator:
                return await validator(request, auth_header)
        
        return True
    
    def match_rule(self, path: str, method: str, headers: Dict[str, str], 
                   query_params: Dict[str, str] = None) -> Optional[APIProxyRule]:
        """Advanced rule matching with headers and query parameters"""
        query_params = query_params or {}
        
        for rule in self.rules:
            # Check method
            if method not in rule.methods:
                continue
                
            # Check path pattern
            if not self.path_matches(path, rule.path_pattern):
                continue
                
            # Check headers filter
            if not self.headers_match(headers, rule.headers_filter, rule.headers_match_mode):
                continue
                
            # Check query parameters filter
            if not self.query_params_match(query_params, rule.query_params_filter):
                continue
                
            return rule
        
        return None
    
    def path_matches(self, path: str, pattern: str) -> bool:
        """Advanced path pattern matching with wildcards and parameters"""
        # Convert pattern to regex
        # Support: * (any chars), ** (any path segments), {param} (named parameters)
        regex_pattern = pattern
        regex_pattern = regex_pattern.replace('**', '__DOUBLE_WILDCARD__')
        regex_pattern = regex_pattern.replace('*', '[^/]*')
        regex_pattern = regex_pattern.replace('__DOUBLE_WILDCARD__', '.*')
        regex_pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', regex_pattern)
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, path))
    
    def headers_match(self, headers: Dict[str, str], filter_headers: Dict[str, str], 
                     match_mode: str = "all") -> bool:
        """Advanced header matching with multiple modes"""
        if not filter_headers:
            return True
            
        headers_lower = {k.lower(): v for k, v in headers.items()}
        matches = []
        
        for key, expected_pattern in filter_headers.items():
            actual_value = headers_lower.get(key.lower(), '')
            
            # Support regex patterns
            if expected_pattern.startswith('regex:'):
                pattern = expected_pattern[6:]
                matches.append(bool(re.search(pattern, actual_value)))
            # Support exact match
            elif expected_pattern.startswith('exact:'):
                expected = expected_pattern[6:]
                matches.append(actual_value == expected)
            # Support contains (default)
            else:
                matches.append(expected_pattern in actual_value)
        
        if match_mode == "all":
            return all(matches)
        elif match_mode == "any":
            return any(matches)
        elif match_mode == "exact":
            return len(matches) == len(filter_headers) and all(matches)
        
        return False
    
    def query_params_match(self, query_params: Dict[str, str], 
                          filter_params: Dict[str, str]) -> bool:
        """Check if query parameters match filter criteria"""
        if not filter_params:
            return True
            
        for key, expected_value in filter_params.items():
            actual_value = query_params.get(key, '')
            if expected_value not in actual_value:
                return False
        
        return True
    
    async def load_transform_function(self, function_path: str) -> Optional[Callable]:
        """Load transformation function dynamically"""
        if function_path in self.transform_functions:
            return self.transform_functions[function_path]
            
        try:
            module_path, function_name = function_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)
            self.transform_functions[function_path] = func
            return func
        except Exception as e:
            logger.error("Failed to load transform function", 
                        path=function_path, error=str(e))
            return None
    
    def rewrite_path(self, original_path: str, rule: APIProxyRule) -> str:
        """Rewrite request path according to rule"""
        path = original_path
        
        if rule.strip_path_prefix:
            # Strip the pattern prefix from path
            pattern_base = rule.path_pattern.rstrip('*').rstrip('/')
            if path.startswith(pattern_base):
                path = path[len(pattern_base):]
        
        if rule.add_path_prefix:
            path = rule.add_path_prefix.rstrip('/') + '/' + path.lstrip('/')
            
        return path
    
    async def proxy_request(self, request: web.Request, rule: APIProxyRule) -> web.Response:
        """Advanced proxy request with all features"""
        # Check authentication
        if not await self.authenticate_request(request, rule):
            return web.json_response(
                {"error": "Authentication required"}, 
                status=401,
                headers=self.get_cors_headers(rule)
            )
        
        # Check rate limit
        client_ip = request.remote or '127.0.0.1'
        if not self.check_rate_limit(client_ip, rule):
            return web.json_response(
                {"error": "Rate limit exceeded"}, 
                status=429,
                headers=self.get_cors_headers(rule)
            )
        
        # Get target URL with load balancing
        target_base = self.get_target_url(rule)
        if not target_base:
            return web.json_response(
                {"error": "Service unavailable"}, 
                status=503,
                headers=self.get_cors_headers(rule)
            )
        
        # Track connection
        self.connection_counts[target_base] = self.connection_counts.get(target_base, 0) + 1
        
        try:
            # Rewrite path
            rewritten_path = self.rewrite_path(request.path, rule)
            target_url = urljoin(target_base.rstrip('/') + '/', rewritten_path.lstrip('/'))
            
            if request.query_string:
                target_url += '?' + request.query_string.decode()
            
            # Prepare headers
            headers = dict(request.headers)
            headers.pop('host', None)  # Remove host header
            
            # Transform request if needed
            request_data = await request.read()
            if rule.request_transform:
                transformer = await self.load_transform_function(rule.request_transform)
                if transformer:
                    request_data, headers = await transformer(request, request_data, headers)
            
            # Make proxy request with retry
            for attempt in range(rule.retry_count + 1):
                try:
                    async with self.session.request(
                        request.method,
                        target_url,
                        headers=headers,
                        data=request_data,
                        timeout=aiohttp.ClientTimeout(total=rule.timeout)
                    ) as response:
                        content = await response.read()
                        response_headers = dict(response.headers)
                        
                        # Transform response if needed
                        if rule.response_transform:
                            transformer = await self.load_transform_function(rule.response_transform)
                            if transformer:
                                content, response_headers = await transformer(
                                    response, content, response_headers)
                        
                        # Add CORS headers
                        response_headers.update(self.get_cors_headers(rule))
                        
                        # Record success
                        self.record_success(target_base)
                        
                        logger.info("API request proxied successfully", 
                                  source=request.path,
                                  target=target_url, 
                                  status=response.status,
                                  attempt=attempt + 1)
                        
                        return web.Response(
                            body=content,
                            status=response.status,
                            headers=response_headers
                        )
                        
                except asyncio.TimeoutError:
                    logger.warning("Proxy request timeout", 
                                 target=target_url, attempt=attempt + 1)
                    if attempt == rule.retry_count:
                        raise
                    await asyncio.sleep(rule.retry_delay * (attempt + 1))
                    
                except Exception as e:
                    logger.warning("Proxy request failed", 
                                 target=target_url, 
                                 attempt=attempt + 1,
                                 error=str(e))
                    if attempt == rule.retry_count:
                        raise
                    await asyncio.sleep(rule.retry_delay * (attempt + 1))
            
        except Exception as e:
            # Record failure for circuit breaker
            self.record_failure(target_base, rule)
            logger.error("API proxy error", target=target_url, error=str(e))
            
            return web.json_response(
                {"error": "Proxy request failed", "details": str(e)}, 
                status=502,
                headers=self.get_cors_headers(rule)
            )
            
        finally:
            # Decrement connection count
            self.connection_counts[target_base] = max(0, 
                self.connection_counts.get(target_base, 1) - 1)
    
    def get_cors_headers(self, rule: APIProxyRule) -> Dict[str, str]:
        """Get CORS headers for response"""
        if not rule.cors_enabled:
            return {}
            
        return {
            'Access-Control-Allow-Origin': ', '.join(rule.cors_origins),
            'Access-Control-Allow-Methods': ', '.join(rule.cors_methods),
            'Access-Control-Allow-Headers': ', '.join(rule.cors_headers),
            'Access-Control-Max-Age': '3600'
        }
    
    async def handle_preflight(self, request: web.Request, rule: APIProxyRule) -> web.Response:
        """Handle CORS preflight OPTIONS requests"""
        return web.Response(
            status=204,
            headers=self.get_cors_headers(rule)
        )

class StaticWebsiteServer:
    """Main static website hosting server"""
    
    def __init__(self, 
                 static_dir: str = "static",
                 cache_dir: str = ".proserve_cache",
                 default_policy: Optional[CachePolicy] = None):
        self.static_dir = Path(static_dir)
        self.static_dir.mkdir(exist_ok=True)
        
        self.cache = StaticFileCache(cache_dir)
        self.cdn_manager = CDNManager(self.cache)
        self.api_proxy = APIProxy()
        self.default_policy = default_policy or CachePolicy()
        
        # Initialize mimetypes
        mimetypes.init()
        
    async def __aenter__(self):
        await self.cdn_manager.__aenter__()
        await self.api_proxy.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cdn_manager.__aexit__(exc_type, exc_val, exc_tb)
        await self.api_proxy.__aexit__(exc_type, exc_val, exc_tb)
    
    def add_cdn_resource(self, local_path: str, resource: CDNResource):
        """Add CDN resource"""
        self.cdn_manager.add_resource(local_path, resource)
    
    def add_api_proxy_rule(self, rule: APIProxyRule):
        """Add API proxy rule"""
        self.api_proxy.add_rule(rule)
    
    async def serve_static_file(self, request: web.Request) -> web.Response:
        """Serve static file with caching"""
        path = request.path.lstrip('/')
        if not path:
            path = 'index.html'
        
        # Security check - prevent directory traversal
        if '..' in path or path.startswith('/'):
            return web.Response(status=403, text="Forbidden")
        
        # Try CDN resource first
        cdn_result = await self.cdn_manager.get_resource(path)
        if cdn_result:
            content, headers = cdn_result
            content_type = headers.get('content-type') or self.get_content_type(path)
            
            return web.Response(
                body=content,
                headers={
                    'Content-Type': content_type,
                    'Cache-Control': f'max-age={self.default_policy.max_age}',
                    **headers
                }
            )
        
        # Try local file
        file_path = self.static_dir / path
        if file_path.exists() and file_path.is_file():
            try:
                async with aiofiles.open(file_path, 'rb') as f:
                    content = await f.read()
                
                content_type = self.get_content_type(path)
                
                return web.Response(
                    body=content,
                    headers={
                        'Content-Type': content_type,
                        'Cache-Control': f'max-age={self.default_policy.max_age}'
                    }
                )
                
            except Exception as e:
                logger.error("Failed to serve static file", path=path, error=str(e))
                return web.Response(status=500, text="Internal Server Error")
        
        return web.Response(status=404, text="Not Found")
    
    async def handle_api_proxy(self, request: web.Request) -> web.Response:
        """Handle API proxy requests"""
        rule = self.api_proxy.match_rule(
            request.path, 
            request.method, 
            dict(request.headers)
        )
        
        if rule:
            return await self.api_proxy.proxy_request(request, rule)
        
        return web.Response(status=404, text="API endpoint not found")
    
    def get_content_type(self, path: str) -> str:
        """Get MIME type for file"""
        content_type, _ = mimetypes.guess_type(path)
        return content_type or 'application/octet-stream'
    
    def setup_routes(self, app: web.Application):
        """Setup routes for static server"""
        # API proxy routes (higher priority)
        app.router.add_route('*', '/api/{path:.*}', self.handle_api_proxy)
        
        # Static file routes (catch-all)
        app.router.add_route('GET', '/{path:.*}', self.serve_static_file)


async def create_static_website_app(config: Dict[str, Any]) -> web.Application:
    """Create static website application from configuration"""
    app = web.Application()
    
    # Initialize static server
    static_server = StaticWebsiteServer(
        static_dir=config.get('static_dir', 'static'),
        cache_dir=config.get('cache_dir', '.proserve_cache')
    )
    
    # Add CDN resources
    for resource_config in config.get('cdn_resources', []):
        resource = CDNResource(**resource_config)
        static_server.add_cdn_resource(resource.local_path, resource)
    
    # Add API proxy rules
    for rule_config in config.get('api_proxy_rules', []):
        rule = APIProxyRule(**rule_config)
        static_server.add_api_proxy_rule(rule)
    
    # Setup routes
    static_server.setup_routes(app)
    
    # Store server reference for cleanup
    app['static_server'] = static_server
    
    return app
