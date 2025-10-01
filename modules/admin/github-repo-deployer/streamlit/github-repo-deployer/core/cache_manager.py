"""
Repository Cache Manager
Handles caching of downloaded repositories to avoid re-downloading
"""
import os
import json
import hashlib
import tempfile
import shutil
import streamlit as st
from typing import Optional, Dict, Any
from pathlib import Path
import time


class RepositoryCache:
    """Manages repository caching for both SaaS and test environments"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Custom cache directory. If None, uses system temp directory
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use system temp directory with a subdirectory for our cache
            self.cache_dir = Path(tempfile.gettempdir()) / "github-repo-deployer-cache"
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass  # Fail silently if can't save metadata
    
    def _get_cache_key(self, owner: str, repo: str, branch: str) -> str:
        """Generate cache key for repository"""
        key_string = f"{owner}/{repo}@{branch}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache directory path for a repository"""
        return self.cache_dir / cache_key
    
    def is_cached(self, owner: str, repo: str, branch: str) -> bool:
        """Check if repository is cached"""
        cache_key = self._get_cache_key(owner, repo, branch)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_key not in self.metadata:
            return False
        
        # Check if cache directory still exists
        if not cache_path.exists():
            # Remove from metadata if directory doesn't exist
            del self.metadata[cache_key]
            self._save_metadata()
            return False
        
        # Check if cache is not too old (24 hours)
        cache_time = self.metadata[cache_key].get('timestamp', 0)
        current_time = time.time()
        if current_time - cache_time > 86400:  # 24 hours
            self.remove_cache(owner, repo, branch)
            return False
        
        return True
    
    def get_cache_info(self, owner: str, repo: str, branch: str) -> Optional[Dict[str, Any]]:
        """Get cache information for a repository"""
        cache_key = self._get_cache_key(owner, repo, branch)
        if cache_key in self.metadata:
            return self.metadata[cache_key]
        return None
    
    def cache_repository(self, owner: str, repo: str, branch: str, source_path: str) -> str:
        """
        Cache a downloaded repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            source_path: Path to the downloaded repository
            
        Returns:
            Path to cached repository
        """
        cache_key = self._get_cache_key(owner, repo, branch)
        cache_path = self._get_cache_path(cache_key)
        
        # Remove existing cache if it exists
        if cache_path.exists():
            shutil.rmtree(cache_path)
        
        # Copy repository to cache
        shutil.copytree(source_path, cache_path)
        
        # Update metadata
        self.metadata[cache_key] = {
            'owner': owner,
            'repo': repo,
            'branch': branch,
            'timestamp': time.time(),
            'cache_path': str(cache_path),
            'size': self._get_directory_size(cache_path)
        }
        self._save_metadata()
        
        return str(cache_path)
    
    def get_cached_repository(self, owner: str, repo: str, branch: str) -> Optional[str]:
        """
        Get cached repository path
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            Path to cached repository or None if not cached
        """
        if not self.is_cached(owner, repo, branch):
            return None
        
        cache_key = self._get_cache_key(owner, repo, branch)
        cache_path = self._get_cache_path(cache_key)
        return str(cache_path)
    
    def remove_cache(self, owner: str, repo: str, branch: str) -> bool:
        """Remove repository from cache"""
        cache_key = self._get_cache_key(owner, repo, branch)
        cache_path = self._get_cache_path(cache_key)
        
        # Remove directory
        if cache_path.exists():
            shutil.rmtree(cache_path)
        
        # Remove from metadata
        if cache_key in self.metadata:
            del self.metadata[cache_key]
            self._save_metadata()
            return True
        
        return False
    
    def clear_all_cache(self):
        """Clear all cached repositories"""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata = {}
        self._save_metadata()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_size = 0
        cache_count = 0
        
        for cache_key, info in self.metadata.items():
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                total_size += info.get('size', 0)
                cache_count += 1
        
        return {
            'total_repositories': cache_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_directory': str(self.cache_dir)
        }
    
    def _get_directory_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except (OSError, IOError):
            pass
        return total_size


# Global cache instance
_cache_instance = None


def get_cache() -> RepositoryCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RepositoryCache()
    return _cache_instance


def cache_repository(owner: str, repo: str, branch: str, source_path: str) -> str:
    """Cache a repository using global cache instance"""
    return get_cache().cache_repository(owner, repo, branch, source_path)


def get_cached_repository(owner: str, repo: str, branch: str) -> Optional[str]:
    """Get cached repository using global cache instance"""
    return get_cache().get_cached_repository(owner, repo, branch)


def is_repository_cached(owner: str, repo: str, branch: str) -> bool:
    """Check if repository is cached using global cache instance"""
    return get_cache().is_cached(owner, repo, branch)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics using global cache instance"""
    return get_cache().get_cache_stats()

