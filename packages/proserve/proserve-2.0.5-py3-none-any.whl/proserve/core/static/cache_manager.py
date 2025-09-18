"""
ProServe Static Cache Manager - File Caching and Cache Policy Management
Handles static file caching with TTL validation and cache policies
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
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
                logger.debug(f"Loaded cache metadata: {len(self.metadata)} entries")
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {}
    
    def save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.debug(f"Saved cache metadata: {len(self.metadata)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def get_cached_file(self, url: str, policy: CachePolicy) -> Optional[bytes]:
        """Get cached file if valid according to policy"""
        cache_key = self.get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.cache"
        
        if not cache_file.exists():
            logger.debug(f"Cache miss: {url}")
            return None
        
        # Check metadata
        if cache_key not in self.metadata:
            logger.debug(f"Cache metadata missing: {url}")
            return None
        
        metadata = self.metadata[cache_key]
        
        # Check TTL
        cached_time = metadata.get('cached_time', 0)
        if time.time() - cached_time > policy.max_age:
            logger.debug(f"Cache expired: {url}")
            self._remove_cached_file(cache_key)
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                content = f.read()
            
            # Validate integrity if available
            if 'hash' in metadata:
                content_hash = hashlib.sha256(content).hexdigest()
                if content_hash != metadata['hash']:
                    logger.warning(f"Cache integrity check failed: {url}")
                    self._remove_cached_file(cache_key)
                    return None
            
            logger.debug(f"Cache hit: {url}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read cached file: {e}")
            self._remove_cached_file(cache_key)
            return None
    
    def cache_file(self, url: str, content: bytes, headers: Dict[str, str], policy: CachePolicy):
        """Cache file with metadata"""
        try:
            cache_key = self.get_cache_key(url)
            cache_file = self.cache_dir / f"{cache_key}.cache"
            
            # Write content to cache file
            with open(cache_file, 'wb') as f:
                f.write(content)
            
            # Store metadata
            self.metadata[cache_key] = {
                'url': url,
                'cached_time': time.time(),
                'hash': hashlib.sha256(content).hexdigest(),
                'size': len(content),
                'headers': headers,
                'policy': {
                    'max_age': policy.max_age,
                    'etag_validation': policy.etag_validation,
                    'last_modified_validation': policy.last_modified_validation
                }
            }
            
            self.save_metadata()
            logger.debug(f"Cached file: {url} ({len(content)} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to cache file: {e}")
    
    def _remove_cached_file(self, cache_key: str):
        """Remove cached file and metadata"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.cache"
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.metadata:
                del self.metadata[cache_key]
                self.save_metadata()
                
        except Exception as e:
            logger.error(f"Failed to remove cached file: {e}")
    
    def clear_cache(self):
        """Clear all cached files"""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.metadata = {}
            self.save_metadata()
            
            logger.info("Cache cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = 0
        expired_count = 0
        current_time = time.time()
        
        for cache_key, metadata in self.metadata.items():
            cache_file = self.cache_dir / f"{cache_key}.cache"
            if cache_file.exists():
                total_size += cache_file.stat().st_size
            
            # Check if expired (using default max_age if not in metadata)
            max_age = metadata.get('policy', {}).get('max_age', 86400)
            if current_time - metadata.get('cached_time', 0) > max_age:
                expired_count += 1
        
        return {
            'total_files': len(self.metadata),
            'total_size_bytes': total_size,
            'expired_files': expired_count,
            'cache_directory': str(self.cache_dir)
        }
    
    def cleanup_expired(self, policy: CachePolicy = None):
        """Remove expired cache entries"""
        if not policy:
            policy = CachePolicy()
        
        expired_keys = []
        current_time = time.time()
        
        for cache_key, metadata in self.metadata.items():
            cached_time = metadata.get('cached_time', 0)
            max_age = metadata.get('policy', {}).get('max_age', policy.max_age)
            
            if current_time - cached_time > max_age:
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove_cached_file(cache_key)
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)


class CacheManager:
    """High-level cache management with multiple policies"""
    
    def __init__(self, cache_dir: str = ".proserve_cache"):
        self.cache = StaticFileCache(cache_dir)
        self.policies: Dict[str, CachePolicy] = {}
        self.default_policy = CachePolicy()
    
    def add_policy(self, name: str, policy: CachePolicy):
        """Add a named cache policy"""
        self.policies[name] = policy
        logger.info(f"Added cache policy: {name}")
    
    def get_policy(self, name: str = None) -> CachePolicy:
        """Get cache policy by name or default"""
        if name and name in self.policies:
            return self.policies[name]
        return self.default_policy
    
    def should_cache_file(self, file_path: str, policy: CachePolicy = None) -> bool:
        """Check if file should be cached based on policy"""
        if not policy:
            policy = self.default_policy
        
        file_ext = Path(file_path).suffix.lower()
        return file_ext in policy.allowed_extensions
    
    def get_cached_content(self, url: str, policy_name: str = None) -> Optional[bytes]:
        """Get cached content using specified policy"""
        policy = self.get_policy(policy_name)
        return self.cache.get_cached_file(url, policy)
    
    def cache_content(self, url: str, content: bytes, headers: Dict[str, str], 
                     policy_name: str = None):
        """Cache content using specified policy"""
        policy = self.get_policy(policy_name)
        
        # Check if file should be cached
        if self.should_cache_file(url, policy):
            self.cache.cache_file(url, content, headers, policy)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = self.cache.get_cache_stats()
        stats['policies'] = list(self.policies.keys())
        return stats
    
    def cleanup(self):
        """Cleanup expired entries for all policies"""
        total_removed = 0
        
        # Clean with default policy
        removed = self.cache.cleanup_expired(self.default_policy)
        total_removed += removed
        
        # Clean with each specific policy
        for policy_name, policy in self.policies.items():
            removed = self.cache.cleanup_expired(policy)
            total_removed += removed
        
        return total_removed
