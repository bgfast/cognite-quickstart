"""
Rate Limiting Utilities for GitHub API Calls
Prevents rate limiting issues in SaaS Streamlit environment
"""
import time
import streamlit as st
from typing import Dict, Any, Optional
import requests
from functools import wraps


class GitHubRateLimiter:
    """Rate limiter for GitHub API calls with retry logic"""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 1.0  # Minimum 1 second between requests
        self.retry_delays = [1, 2, 5, 10, 30]  # Exponential backoff delays
        self.max_retries = 5
        
    def wait_if_needed(self):
        """Wait if needed to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request_with_retry(self, url: str, headers: Dict[str, str] = None, timeout: int = 30) -> Optional[requests.Response]:
        """Make GitHub API request with rate limiting and retry logic"""
        if headers is None:
            headers = {}
            
        for attempt in range(self.max_retries):
            try:
                # Wait to respect rate limits
                self.wait_if_needed()
                
                # Make the request
                response = requests.get(url, headers=headers, timeout=timeout)
                
                # Check for rate limiting
                if response.status_code == 403:
                    # Check if it's a rate limit error
                    if 'rate limit' in response.text.lower() or 'x-ratelimit-remaining' in response.headers:
                        remaining_requests = response.headers.get('x-ratelimit-remaining', '0')
                        reset_time = response.headers.get('x-ratelimit-reset', '0')
                        
                        if remaining_requests == '0':
                            # We're rate limited, wait until reset
                            reset_timestamp = int(reset_time)
                            current_timestamp = int(time.time())
                            wait_time = max(0, reset_timestamp - current_timestamp + 10)  # Add 10 second buffer
                            
                            st.warning(f"⚠️ GitHub API rate limited. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Rate limited but not exhausted, use exponential backoff
                            delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                            st.warning(f"⚠️ GitHub API rate limited. Retrying in {delay} seconds...")
                            time.sleep(delay)
                            continue
                    else:
                        # 403 but not rate limiting, return the response
                        return response
                
                # Success or other error
                return response
                
            except requests.exceptions.Timeout:
                delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                st.warning(f"⚠️ Request timeout. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
                
            except requests.exceptions.RequestException as e:
                delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                st.warning(f"⚠️ Request failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
        
        # All retries failed
        st.error("❌ GitHub API request failed after all retries")
        return None


# Global rate limiter instance
_rate_limiter = GitHubRateLimiter()


def rate_limited_request(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> Optional[requests.Response]:
    """Make a rate-limited GitHub API request"""
    return _rate_limiter.make_request_with_retry(url, headers, timeout)


def get_github_branches_with_rate_limit(owner: str, repo: str, token: str = None) -> list:
    """Get GitHub branches with rate limiting protection"""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    response = rate_limited_request(url, headers)
    if response and response.status_code == 200:
        return [branch['name'] for branch in response.json()]
    else:
        st.warning(f"⚠️ Could not load branches: {response.status_code if response else 'No response'}")
        return ["main"]  # Fallback to main branch


def get_github_tree_with_rate_limit(owner: str, repo: str, branch: str, token: str = None) -> Optional[Dict[str, Any]]:
    """Get GitHub repository tree with rate limiting protection"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    response = rate_limited_request(url, headers)
    if response and response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Failed to get repository tree: {response.status_code if response else 'No response'}")
        return None


def get_github_file_with_rate_limit(owner: str, repo: str, sha: str, token: str = None) -> Optional[Dict[str, Any]]:
    """Get GitHub file content with rate limiting protection"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    response = rate_limited_request(url, headers)
    if response and response.status_code == 200:
        return response.json()
    else:
        st.warning(f"⚠️ Failed to get file content: {response.status_code if response else 'No response'}")
        return None


def check_rate_limit_status() -> Dict[str, Any]:
    """Check current GitHub API rate limit status"""
    url = "https://api.github.com/rate_limit"
    response = rate_limited_request(url)
    
    if response and response.status_code == 200:
        data = response.json()
        return {
            'remaining': data['resources']['core']['remaining'],
            'limit': data['resources']['core']['limit'],
            'reset_time': data['resources']['core']['reset'],
            'used': data['resources']['core']['used']
        }
    else:
        return {
            'remaining': 0,
            'limit': 0,
            'reset_time': 0,
            'used': 0
        }

