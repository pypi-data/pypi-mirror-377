"""
ProServe CDN Manager - CDN Resource Management
Handles CDN resource fetching, validation, and fallback support
"""

import hashlib
import base64
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from urllib.parse import urlparse
import aiohttp
import structlog

from .cache_manager import CachePolicy, StaticFileCache

logger = structlog.get_logger(__name__)


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


class CDNManager:
    """CDN resource management with fallback and integrity validation"""
    
    def __init__(self, cache: StaticFileCache):
        self.cache = cache
        self.resources: Dict[str, CDNResource] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_timeout = 30
        self.max_retries = 3
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.default_timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def add_resource(self, local_path: str, resource: CDNResource):
        """Add CDN resource configuration"""
        self.resources[local_path] = resource
        logger.info(f"Added CDN resource: {local_path} -> {resource.url}")
    
    async def fetch_resource(self, resource: CDNResource) -> Optional[bytes]:
        """Fetch resource from CDN with fallback support"""
        if not self.session:
            logger.error("CDN Manager session not initialized")
            return None
        
        urls_to_try = [resource.url]
        if resource.fallback_url:
            urls_to_try.append(resource.fallback_url)
        
        for attempt, url in enumerate(urls_to_try):
            for retry in range(self.max_retries):
                try:
                    logger.debug(f"Fetching CDN resource: {url} (attempt {retry + 1})")
                    
                    headers = dict(resource.headers) if resource.headers else {}
                    
                    # Add version parameter if specified
                    request_url = url
                    if resource.version and '?' not in url:
                        request_url = f"{url}?v={resource.version}"
                    
                    async with self.session.get(request_url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # Validate integrity if provided
                            if resource.integrity:
                                if not self.validate_integrity(content, resource.integrity):
                                    logger.warning(f"Integrity validation failed for {url}")
                                    if attempt == 0 and resource.fallback_url:
                                        logger.info(f"Trying fallback URL: {resource.fallback_url}")
                                        break  # Try fallback URL
                                    continue  # Retry same URL
                            
                            logger.info(f"Successfully fetched CDN resource: {url} ({len(content)} bytes)")
                            return content
                        
                        else:
                            logger.warning(f"CDN resource fetch failed: {url} (HTTP {response.status})")
                
                except Exception as e:
                    logger.warning(f"CDN fetch error for {url}: {e}")
                
                # Wait before retry (exponential backoff)
                if retry < self.max_retries - 1:
                    await asyncio.sleep(2 ** retry)
        
        logger.error(f"Failed to fetch CDN resource after all attempts: {resource.url}")
        return None
    
    def validate_integrity(self, content: bytes, integrity: str) -> bool:
        """Validate SRI integrity hash"""
        try:
            # Parse SRI format: "sha256-base64hash" or "sha384-base64hash" etc.
            if '-' not in integrity:
                logger.warning(f"Invalid integrity format: {integrity}")
                return False
            
            algorithm, expected_hash = integrity.split('-', 1)
            
            # Calculate hash based on algorithm
            if algorithm == 'sha256':
                calculated = hashlib.sha256(content)
            elif algorithm == 'sha384':
                calculated = hashlib.sha384(content)
            elif algorithm == 'sha512':
                calculated = hashlib.sha512(content)
            else:
                logger.warning(f"Unsupported integrity algorithm: {algorithm}")
                return False
            
            # Compare base64 encoded hashes
            calculated_b64 = base64.b64encode(calculated.digest()).decode()
            
            if calculated_b64 == expected_hash:
                logger.debug("Integrity validation passed")
                return True
            else:
                logger.warning("Integrity validation failed: hash mismatch")
                return False
                
        except Exception as e:
            logger.error(f"Integrity validation error: {e}")
            return False
    
    async def get_resource(self, local_path: str) -> Optional[bytes]:
        """Get resource with caching and fallback"""
        if local_path not in self.resources:
            logger.warning(f"CDN resource not configured: {local_path}")
            return None
        
        resource = self.resources[local_path]
        cache_policy = resource.cache_policy or CachePolicy()
        
        # Try to get from cache first
        cached_content = self.cache.get_cached_file(resource.url, cache_policy)
        if cached_content:
            logger.debug(f"Serving CDN resource from cache: {local_path}")
            return cached_content
        
        # Fetch from CDN
        content = await self.fetch_resource(resource)
        if content:
            # Cache the content
            headers = {
                'Content-Type': self._guess_content_type(local_path),
                'CDN-Source': resource.url
            }
            self.cache.cache_file(resource.url, content, headers, cache_policy)
            return content
        
        return None
    
    def _guess_content_type(self, path: str) -> str:
        """Guess content type from file extension"""
        import mimetypes
        content_type, _ = mimetypes.guess_type(path)
        return content_type or 'application/octet-stream'
    
    async def preload_resources(self, resources: List[str] = None):
        """Preload specified CDN resources or all configured resources"""
        resources_to_load = resources or list(self.resources.keys())
        
        results = []
        for local_path in resources_to_load:
            if local_path in self.resources:
                try:
                    content = await self.get_resource(local_path)
                    results.append({
                        'path': local_path,
                        'success': content is not None,
                        'size': len(content) if content else 0
                    })
                except Exception as e:
                    logger.error(f"Failed to preload CDN resource {local_path}: {e}")
                    results.append({
                        'path': local_path,
                        'success': False,
                        'error': str(e)
                    })
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"CDN preload completed: {successful}/{len(results)} resources loaded")
        return results
    
    def get_resource_info(self, local_path: str = None) -> Dict:
        """Get information about CDN resources"""
        if local_path:
            if local_path in self.resources:
                resource = self.resources[local_path]
                return {
                    'url': resource.url,
                    'fallback_url': resource.fallback_url,
                    'version': resource.version,
                    'has_integrity': bool(resource.integrity),
                    'cache_policy': {
                        'max_age': resource.cache_policy.max_age if resource.cache_policy else None
                    }
                }
            else:
                return {'error': 'Resource not found'}
        else:
            # Return info for all resources
            return {
                path: {
                    'url': res.url,
                    'fallback_url': res.fallback_url,
                    'version': res.version,
                    'has_integrity': bool(res.integrity)
                }
                for path, res in self.resources.items()
            }
    
    async def validate_all_resources(self) -> Dict[str, bool]:
        """Validate all configured CDN resources"""
        results = {}
        
        for local_path, resource in self.resources.items():
            try:
                content = await self.fetch_resource(resource)
                results[local_path] = content is not None
            except Exception as e:
                logger.error(f"Validation failed for {local_path}: {e}")
                results[local_path] = False
        
        return results
    
    def remove_resource(self, local_path: str):
        """Remove CDN resource configuration"""
        if local_path in self.resources:
            del self.resources[local_path]
            logger.info(f"Removed CDN resource: {local_path}")
        else:
            logger.warning(f"CDN resource not found for removal: {local_path}")
    
    def clear_all_resources(self):
        """Clear all CDN resource configurations"""
        count = len(self.resources)
        self.resources.clear()
        logger.info(f"Cleared all CDN resources: {count} removed")
