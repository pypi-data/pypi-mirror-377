"""
ProServe API Proxy - Advanced API Proxy with Load Balancing and Circuit Breaker
Handles API request proxying, rate limiting, and failover management
"""

import asyncio
import time
import re
import importlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urljoin
import aiohttp
from aiohttp import web
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class APIProxyRule:
    """Advanced API proxy routing rule with header-based routing"""
    path_pattern: str
    target_url: str
    methods: List[str] = field(default_factory=lambda: ['GET', 'POST', 'PUT', 'DELETE'])
    headers_filter: Dict[str, str] = field(default_factory=dict)
    headers_match_mode: str = "all"  # "all", "any", "none"
    query_params_filter: Dict[str, str] = field(default_factory=dict)
    request_transform: Optional[str] = None  # Function path for request transformation
    response_transform: Optional[str] = None  # Function path for response transformation
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: Optional[int] = None  # requests per minute per IP
    circuit_breaker_enabled: bool = True
    max_failures: int = 5
    failure_timeout: int = 60  # seconds
    auth_required: bool = False
    auth_header: str = "Authorization"
    auth_validator: Optional[str] = None  # Function path for auth validation
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    strip_path_prefix: bool = False
    add_path_prefix: str = ""
    target_urls: List[str] = field(default_factory=list)  # For load balancing
    load_balance_method: str = "round_robin"  # "round_robin", "random", "least_connections"
    health_check_url: Optional[str] = None
    health_check_interval: int = 60


class APIProxy:
    """Advanced API proxy system with header-based routing, load balancing, and circuit breaker"""
    
    def __init__(self):
        self.rules: List[APIProxyRule] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits: Dict[str, List[float]] = {}  # IP -> timestamps
        self.circuit_breakers: Dict[str, Dict] = {}  # URL -> breaker state
        self.load_balancer_state: Dict[str, int] = {}  # Rule -> round robin counter
        self.connection_counts: Dict[str, int] = {}  # URL -> active connections
        self.transform_functions: Dict[str, Callable] = {}  # Cache loaded transform functions
        self.health_check_task = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        self.session = aiohttp.ClientSession(connector=connector)
        
        # Start health check task
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Stop health check task
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
    
    def add_rule(self, rule: APIProxyRule):
        """Add API proxy rule with validation"""
        # Validate rule
        if not rule.path_pattern:
            raise ValueError("Path pattern is required")
        if not rule.target_url and not rule.target_urls:
            raise ValueError("Target URL(s) required")
        
        # Initialize circuit breaker state for target URLs
        urls_to_check = rule.target_urls if rule.target_urls else [rule.target_url]
        for url in urls_to_check:
            if url not in self.circuit_breakers:
                self.circuit_breakers[url] = {
                    'failures': 0,
                    'last_failure': 0,
                    'state': 'closed'  # closed, open, half-open
                }
        
        self.rules.append(rule)
        logger.info(f"Added API proxy rule: {rule.path_pattern} -> {rule.target_url}")
    
    def get_target_url(self, rule: APIProxyRule) -> str:
        """Get target URL using load balancing"""
        if not rule.target_urls:
            return rule.target_url
        
        if rule.load_balance_method == "round_robin":
            rule_key = id(rule)
            if rule_key not in self.load_balancer_state:
                self.load_balancer_state[rule_key] = 0
            
            index = self.load_balancer_state[rule_key] % len(rule.target_urls)
            self.load_balancer_state[rule_key] += 1
            return rule.target_urls[index]
        
        elif rule.load_balance_method == "random":
            import random
            return random.choice(rule.target_urls)
        
        elif rule.load_balance_method == "least_connections":
            # Choose URL with least active connections
            min_connections = float('inf')
            chosen_url = rule.target_urls[0]
            
            for url in rule.target_urls:
                connections = self.connection_counts.get(url, 0)
                if connections < min_connections:
                    min_connections = connections
                    chosen_url = url
            
            return chosen_url
        
        else:
            return rule.target_urls[0]
    
    def is_target_healthy(self, target_url: str, rule: APIProxyRule) -> bool:
        """Check if target is healthy using circuit breaker"""
        if not rule.circuit_breaker_enabled:
            return True
        
        breaker = self.circuit_breakers.get(target_url, {})
        state = breaker.get('state', 'closed')
        
        if state == 'closed':
            return True
        elif state == 'open':
            # Check if enough time has passed to try half-open
            last_failure = breaker.get('last_failure', 0)
            if time.time() - last_failure > rule.failure_timeout:
                breaker['state'] = 'half-open'
                logger.info(f"Circuit breaker half-open for {target_url}")
                return True
            return False
        elif state == 'half-open':
            return True
        
        return False
    
    def record_success(self, target_url: str):
        """Record successful request"""
        if target_url in self.circuit_breakers:
            breaker = self.circuit_breakers[target_url]
            breaker['failures'] = 0
            breaker['state'] = 'closed'
        
        # Decrease connection count
        if target_url in self.connection_counts:
            self.connection_counts[target_url] = max(0, self.connection_counts[target_url] - 1)
    
    def record_failure(self, target_url: str, rule: APIProxyRule):
        """Record failed request and update circuit breaker"""
        if not rule.circuit_breaker_enabled:
            return
        
        breaker = self.circuit_breakers.get(target_url, {})
        breaker['failures'] = breaker.get('failures', 0) + 1
        breaker['last_failure'] = time.time()
        
        if breaker['failures'] >= rule.max_failures:
            breaker['state'] = 'open'
            logger.warning(f"Circuit breaker opened for {target_url} after {breaker['failures']} failures")
        
        # Decrease connection count
        if target_url in self.connection_counts:
            self.connection_counts[target_url] = max(0, self.connection_counts[target_url] - 1)
    
    def check_rate_limit(self, client_ip: str, rule: APIProxyRule) -> bool:
        """Advanced rate limiting with sliding window"""
        if not rule.rate_limit:
            return True
        
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old entries
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []
        
        # Remove old timestamps
        self.rate_limits[client_ip] = [
            ts for ts in self.rate_limits[client_ip] if ts > minute_ago
        ]
        
        # Check if under limit
        if len(self.rate_limits[client_ip]) >= rule.rate_limit:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(self.rate_limits[client_ip])}/{rule.rate_limit}")
            return False
        
        # Add current timestamp
        self.rate_limits[client_ip].append(now)
        return True
    
    async def authenticate_request(self, request: web.Request, rule: APIProxyRule) -> bool:
        """Authenticate request if required"""
        if not rule.auth_required:
            return True
        
        auth_header_value = request.headers.get(rule.auth_header)
        if not auth_header_value:
            return False
        
        if rule.auth_validator:
            try:
                validator = self.load_transform_function(rule.auth_validator)
                result = await validator(request, auth_header_value) if asyncio.iscoroutinefunction(validator) else validator(request, auth_header_value)
                return bool(result)
            except Exception as e:
                logger.error(f"Authentication validation error: {e}")
                return False
        
        return True  # If no validator specified, just check presence of header
    
    def match_rule(self, path: str, method: str, headers: Dict[str, str], 
                   query_params: Dict[str, str] = None) -> Optional[APIProxyRule]:
        """Advanced rule matching with headers and query parameters"""
        query_params = query_params or {}
        
        for rule in self.rules:
            # Method matching
            if method.upper() not in [m.upper() for m in rule.methods]:
                continue
            
            # Path pattern matching
            if not self.path_matches(path, rule.path_pattern):
                continue
            
            # Header matching
            if rule.headers_filter and not self.headers_match(headers, rule.headers_filter, rule.headers_match_mode):
                continue
            
            # Query parameters matching
            if rule.query_params_filter and not self.query_params_match(query_params, rule.query_params_filter):
                continue
            
            return rule
        
        return None
    
    def path_matches(self, path: str, pattern: str) -> bool:
        """Advanced path pattern matching with wildcards and parameters"""
        # Convert pattern to regex
        # Support {param} for parameters and * for wildcards
        regex_pattern = pattern
        regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', regex_pattern)  # Replace {param} with [^/]+
        regex_pattern = regex_pattern.replace('*', '.*')  # Replace * with .*
        regex_pattern = f'^{regex_pattern}$'
        
        return bool(re.match(regex_pattern, path))
    
    def headers_match(self, headers: Dict[str, str], filter_headers: Dict[str, str], 
                     match_mode: str = "all") -> bool:
        """Advanced header matching with multiple modes"""
        matches = 0
        
        for key, expected_value in filter_headers.items():
            header_value = headers.get(key, '').lower()
            expected_value = expected_value.lower()
            
            if expected_value == '*' or header_value == expected_value:
                matches += 1
            elif expected_value.startswith('regex:'):
                regex_pattern = expected_value[6:]  # Remove 'regex:' prefix
                if re.search(regex_pattern, header_value):
                    matches += 1
        
        if match_mode == "all":
            return matches == len(filter_headers)
        elif match_mode == "any":
            return matches > 0
        elif match_mode == "none":
            return matches == 0
        
        return False
    
    def query_params_match(self, query_params: Dict[str, str], 
                          filter_params: Dict[str, str]) -> bool:
        """Check if query parameters match filter criteria"""
        for key, expected_value in filter_params.items():
            if key not in query_params:
                return False
            
            param_value = query_params[key]
            
            if expected_value == '*':
                continue
            elif expected_value != param_value:
                return False
        
        return True
    
    def load_transform_function(self, function_path: str) -> Callable:
        """Load transformation function dynamically"""
        if function_path in self.transform_functions:
            return self.transform_functions[function_path]
        
        try:
            module_path, func_name = function_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            
            self.transform_functions[function_path] = func
            return func
            
        except Exception as e:
            logger.error(f"Failed to load transform function {function_path}: {e}")
            raise
    
    def rewrite_path(self, original_path: str, rule: APIProxyRule) -> str:
        """Rewrite request path according to rule"""
        path = original_path
        
        if rule.strip_path_prefix:
            # Extract the pattern prefix and remove it
            pattern_parts = rule.path_pattern.split('/')
            path_parts = path.split('/')
            
            # Remove matching prefix parts
            for i, (pattern_part, path_part) in enumerate(zip(pattern_parts, path_parts)):
                if pattern_part == path_part or pattern_part.startswith('{'):
                    continue
                else:
                    path = '/' + '/'.join(path_parts[i:])
                    break
            else:
                path = '/' + '/'.join(path_parts[len(pattern_parts):])
        
        if rule.add_path_prefix:
            path = rule.add_path_prefix.rstrip('/') + '/' + path.lstrip('/')
        
        return path
    
    async def proxy_request(self, request: web.Request, rule: APIProxyRule) -> web.Response:
        """Advanced proxy request with all features"""
        client_ip = request.remote or '127.0.0.1'
        
        # Rate limiting
        if not self.check_rate_limit(client_ip, rule):
            return web.json_response({'error': 'Rate limit exceeded'}, status=429)
        
        # Authentication
        if not await self.authenticate_request(request, rule):
            return web.json_response({'error': 'Authentication required'}, status=401)
        
        # Get target URL with load balancing
        target_url = self.get_target_url(rule)
        
        # Circuit breaker check
        if not self.is_target_healthy(target_url, rule):
            return web.json_response({'error': 'Service unavailable'}, status=503)
        
        # Increment connection count
        self.connection_counts[target_url] = self.connection_counts.get(target_url, 0) + 1
        
        try:
            # Rewrite path
            proxy_path = self.rewrite_path(request.path_qs, rule)
            full_url = urljoin(target_url, proxy_path)
            
            # Prepare headers
            headers = dict(request.headers)
            headers.pop('Host', None)  # Remove original host header
            
            # Request transformation
            if rule.request_transform:
                try:
                    transform_func = self.load_transform_function(rule.request_transform)
                    if asyncio.iscoroutinefunction(transform_func):
                        full_url, headers = await transform_func(full_url, headers, request)
                    else:
                        full_url, headers = transform_func(full_url, headers, request)
                except Exception as e:
                    logger.error(f"Request transformation error: {e}")
            
            # Get request body
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.read()
            
            # Retry logic
            last_exception = None
            for attempt in range(rule.retry_count + 1):
                try:
                    timeout = aiohttp.ClientTimeout(total=rule.timeout)
                    async with self.session.request(
                        request.method,
                        full_url,
                        headers=headers,
                        data=body,
                        timeout=timeout
                    ) as response:
                        
                        response_body = await response.read()
                        response_headers = dict(response.headers)
                        
                        # Response transformation
                        if rule.response_transform:
                            try:
                                transform_func = self.load_transform_function(rule.response_transform)
                                if asyncio.iscoroutinefunction(transform_func):
                                    response_body, response_headers = await transform_func(response_body, response_headers, response)
                                else:
                                    response_body, response_headers = transform_func(response_body, response_headers, response)
                            except Exception as e:
                                logger.error(f"Response transformation error: {e}")
                        
                        # Add CORS headers
                        cors_headers = self.get_cors_headers(rule)
                        response_headers.update(cors_headers)
                        
                        # Record success
                        self.record_success(target_url)
                        
                        return web.Response(
                            body=response_body,
                            status=response.status,
                            headers=response_headers
                        )
                
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Proxy attempt {attempt + 1} failed for {full_url}: {e}")
                    
                    if attempt < rule.retry_count:
                        await asyncio.sleep(rule.retry_delay * (2 ** attempt))  # Exponential backoff
            
            # All retries failed
            self.record_failure(target_url, rule)
            raise last_exception
            
        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            return web.json_response({'error': 'Proxy request failed'}, status=502)
    
    def get_cors_headers(self, rule: APIProxyRule) -> Dict[str, str]:
        """Get CORS headers for response"""
        if not rule.cors_enabled:
            return {}
        
        return {
            'Access-Control-Allow-Origin': ','.join(rule.cors_origins),
            'Access-Control-Allow-Methods': ','.join(rule.cors_methods),
            'Access-Control-Allow-Headers': ','.join(rule.cors_headers),
            'Access-Control-Allow-Credentials': 'true'
        }
    
    async def handle_preflight(self, request: web.Request, rule: APIProxyRule) -> web.Response:
        """Handle CORS preflight OPTIONS requests"""
        cors_headers = self.get_cors_headers(rule)
        return web.Response(status=200, headers=cors_headers)
    
    async def _health_check_loop(self):
        """Background health check for circuit breaker targets"""
        while True:
            try:
                for rule in self.rules:
                    if rule.health_check_url:
                        await self._check_target_health(rule)
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)
    
    async def _check_target_health(self, rule: APIProxyRule):
        """Check health of a specific target"""
        urls_to_check = rule.target_urls if rule.target_urls else [rule.target_url]
        
        for target_url in urls_to_check:
            try:
                health_url = urljoin(target_url, rule.health_check_url)
                async with self.session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        # Target is healthy, reset circuit breaker if needed
                        if target_url in self.circuit_breakers:
                            breaker = self.circuit_breakers[target_url]
                            if breaker['state'] != 'closed':
                                breaker['state'] = 'closed'
                                breaker['failures'] = 0
                                logger.info(f"Circuit breaker closed for {target_url} (health check passed)")
            
            except Exception as e:
                logger.debug(f"Health check failed for {target_url}: {e}")
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get comprehensive proxy statistics"""
        return {
            'total_rules': len(self.rules),
            'circuit_breakers': {
                url: {
                    'state': breaker.get('state', 'unknown'),
                    'failures': breaker.get('failures', 0),
                    'last_failure': breaker.get('last_failure', 0)
                }
                for url, breaker in self.circuit_breakers.items()
            },
            'active_connections': dict(self.connection_counts),
            'rate_limit_tracking': {
                ip: len(timestamps) 
                for ip, timestamps in self.rate_limits.items()
            }
        }
