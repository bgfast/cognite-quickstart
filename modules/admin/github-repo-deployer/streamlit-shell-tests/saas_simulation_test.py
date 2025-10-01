#!/usr/bin/env python3
"""
SaaS Simulation Test - Simulates the actual SaaS Streamlit environment
"""
import os
import sys

# Fix import path for core modules after refactor
streamlit_app_dir = os.path.join(os.path.dirname(__file__), '..', 'streamlit', 'github-repo-deployer')
streamlit_app_dir = os.path.abspath(streamlit_app_dir)
if streamlit_app_dir not in sys.path:
    sys.path.insert(0, streamlit_app_dir)

import subprocess
import requests
import tempfile
import base64
import shutil
import time
from typing import Dict, Any, List


class SaaSEnvironmentSimulator:
    """Simulates the SaaS Streamlit environment"""
    
    def __init__(self, env_file_path: str = None):
        self.temp_dir = None
        self.repo_path = None
        self.env_file_path = env_file_path
        self.env_vars = {}
    
    def download_repository_via_api(self, owner: str, repo: str, branch: str = "main") -> str:
        """Download repository using GitHub API with caching (same as SaaS environment)"""
        print(f"🔍 Downloading {owner}/{repo}@{branch} via GitHub API...")
        
        # Check cache first
        try:
            from core.cache_manager import is_repository_cached, get_cached_repository, cache_repository
            
            if is_repository_cached(owner, repo, branch):
                print(f"💾 Using cached repository: {owner}/{repo}@{branch}")
                cached_path = get_cached_repository(owner, repo, branch)
                if cached_path and os.path.exists(cached_path):
                    # Copy cached repository to temp directory for test
                    self.temp_dir = tempfile.mkdtemp()
                    self.repo_path = os.path.join(self.temp_dir, f"{repo}-{branch}")
                    shutil.copytree(cached_path, self.repo_path)
                    print(f"✅ Using cached repository from: {cached_path}")
                    return self.repo_path
                else:
                    print("⚠️ Cached repository not found, downloading fresh...")
            
        except ImportError:
            print("⚠️ Cache manager not available, downloading fresh...")
        
        try:
            # Get repository tree with rate limiting protection
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            
            # Add delay to avoid rate limiting
            import time
            time.sleep(1)  # 1 second delay before API call
            
            response = requests.get(url, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 403:
                error_data = response.json()
                if 'rate limit' in error_data.get('message', '').lower():
                    print("⚠️ GitHub API rate limit exceeded. Waiting 60 seconds...")
                    time.sleep(60)
                    response = requests.get(url, timeout=30)
            
            response.raise_for_status()
            
            tree_data = response.json()
            files = [item for item in tree_data.get('tree', []) if item['type'] == 'blob']
            
            print(f"📁 Found {len(files)} files in repository")
            
            # Create temporary directory (simulating SaaS temp storage)
            self.temp_dir = tempfile.mkdtemp()
            self.repo_path = os.path.join(self.temp_dir, f"{repo}-{branch}")
            os.makedirs(self.repo_path, exist_ok=True)
            
            print(f"📂 Created temp directory: {self.repo_path}")
            
            # Download each file
            files_downloaded = 0
            in_development_files = 0
            
            for i, item in enumerate(files):
                file_path = item['path']
                
                # Add delay every 10 files to avoid rate limiting
                if i > 0 and i % 10 == 0:
                    print(f"  ⏳ Rate limiting protection: waiting 2 seconds... (file {i}/{len(files)})")
                    time.sleep(2)
                
                # Get file content
                file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
                file_response = requests.get(file_url, timeout=10)
                
                # Check for rate limiting on individual files
                if file_response.status_code == 403:
                    error_data = file_response.json()
                    if 'rate limit' in error_data.get('message', '').lower():
                        print(f"  ⚠️ Rate limit hit on file {i+1}/{len(files)}. Waiting 30 seconds...")
                        time.sleep(30)
                        file_response = requests.get(file_url, timeout=10)
                
                if file_response.status_code == 200:
                    file_data = file_response.json()
                    if file_data.get('type') == 'file':
                        content = base64.b64decode(file_data['content']).decode('utf-8')
                        
                        # Create file path
                        full_path = os.path.join(self.repo_path, file_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        
                        # Write file
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        files_downloaded += 1
                        
                        # Track in-development files
                        if 'in-development' in file_path:
                            in_development_files += 1
                            print(f"  📄 Downloaded in-development file: {file_path}")
                        
                        # Show progress for important files
                        if file_path in ['config.all.yaml', 'config.weather.yaml', 'requirements.txt']:
                            print(f"  📄 Downloaded: {file_path}")
            
            print(f"✅ Downloaded {files_downloaded} files successfully!")
            print(f"📦 Downloaded {in_development_files} in-development files")
            
            # Cache the downloaded repository
            try:
                cached_path = cache_repository(owner, repo, branch, self.repo_path)
                print(f"💾 Cached repository to: {cached_path}")
            except Exception as e:
                print(f"⚠️ Failed to cache repository: {e}")
            
            return self.repo_path
            
        except Exception as e:
            print(f"❌ Repository download failed: {e}")
            return None
    
    def find_config_files(self, repo_path: str) -> List[str]:
        """Find config.*.yaml files in the downloaded repository"""
        config_files = []
        
        try:
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.startswith('config.') and file.endswith('.yaml'):
                        relative_path = os.path.relpath(os.path.join(root, file), repo_path)
                        config_files.append(relative_path)
            
            return config_files
            
        except Exception as e:
            print(f"❌ Error finding config files: {e}")
            return []
    
    def load_env_file(self):
        """Load environment variables from .env file (same as SaaS)"""
        if not self.env_file_path or not os.path.exists(self.env_file_path):
            print("⚠️ No .env file provided, using system environment")
            return True
        
        print(f"🔧 Loading environment from: {self.env_file_path}")
        
        try:
            with open(self.env_file_path, 'r') as f:
                content = f.read()
            
            # Parse environment variables
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    self.env_vars[key.strip()] = value.strip()
            
            print(f"✅ Loaded {len(self.env_vars)} environment variables")
            
            # Show key variables (without secrets)
            key_vars = ['CDF_PROJECT', 'CDF_CLUSTER', 'CDF_URL', 'IDP_TENANT_ID']
            for var in key_vars:
                if var in self.env_vars:
                    print(f"  📋 {var}: {self.env_vars[var]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load .env file: {e}")
            return False

    def test_toolkit_build(self, repo_path: str, config_file: str = "config.weather.yaml") -> bool:
        """Test toolkit build using unified operations"""
        print(f"🔨 Testing toolkit build with {config_file} using unified operations...")
        
        try:
            from core.toolkit_operations import build_project
            
            # Use unified build function
            success, output, error = build_project(
                repo_path, 
                self.env_vars, 
                env_name=config_file.replace('config.', '').replace('.yaml', ''),
                verbose=True,
                logger=print
            )
            
            if success:
                print("✅ Build completed successfully!")
                return True
            else:
                print(f"❌ Build failed: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Build test failed: {e}")
            return False
    
    def test_toolkit_deploy(self, repo_path: str, config_file: str = "config.weather.yaml") -> bool:
        """Test toolkit deploy using unified operations"""
        print(f"🚀 Testing toolkit deploy with {config_file} using unified operations...")
        
        try:
            from core.toolkit_operations import deploy_project
            
            # Use unified deploy function
            success, output, error = deploy_project(
                repo_path, 
                self.env_vars, 
                env_name=config_file.replace('config.', '').replace('.yaml', ''),
                verbose=True,
                logger=print
            )
            
            if success:
                print("✅ Deploy completed successfully!")
                return True
            else:
                print(f"❌ Deploy failed: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Deploy test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory: {self.temp_dir}")


def test_github_api_connection():
    """Test GitHub API connectivity with rate limiting"""
    print("Testing GitHub API connection...")
    
    try:
        # Use rate limiter for the test
        import sys
        import os
        
        from core.rate_limiter import rate_limited_request, check_rate_limit_status
        
        # Check rate limit status
        rate_status = check_rate_limit_status()
        print(f"📊 GitHub API rate limit: {rate_status['remaining']}/{rate_status['limit']} requests remaining")
        
        if rate_status['remaining'] < 5:
            print("⚠️ Low rate limit remaining, waiting...")
            time.sleep(10)
        
        url = "https://api.github.com/repos/bgfast/cognite-quickstart"
        response = rate_limited_request(url, timeout=10)
        
        if response and response.status_code == 200:
            print("✅ GitHub API connection successful")
            return True
        else:
            print(f"❌ GitHub API returned status {response.status_code if response else 'No response'}")
            return False
    except Exception as e:
        print(f"❌ GitHub API failed: {e}")
        return False


def test_toolkit_availability():
    """Test if Cognite Toolkit is available"""
    print("Testing Cognite Toolkit availability...")
    try:
        result = subprocess.run(['cdf', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Cognite Toolkit available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Cognite Toolkit not available")
            return False
    except Exception as e:
        print(f"❌ Toolkit test failed: {e}")
        return False


def main():
    """Run SaaS simulation tests with real .env file"""
    from datetime import datetime
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("---------------------------------")
    print("--")
    print(f"-- Testing SaaS deploy functions ({timestamp})")
    print("--")
    print("-----------------------------------")
    print()
    print("GitHub Repo Deployer - SaaS Environment Simulation with Real .env")
    print("=" * 70)
    
    # Use the actual .env file from the user's environment
    env_file = os.path.expanduser("~/envs/.env.bluefield.cog-bgfast.bgfast")
    simulator = SaaSEnvironmentSimulator(env_file)
    
    try:
        # Test 1: Load Environment Variables
        print("\n--- Test 1: Load Environment Variables ---")
        env_success = simulator.load_env_file()
        
        # Test 2: GitHub API Connection
        print("\n--- Test 2: GitHub API Connection ---")
        api_success = test_github_api_connection()
        
        # Test 3: Toolkit Availability
        print("\n--- Test 3: Toolkit Availability ---")
        toolkit_success = test_toolkit_availability()
        
        # Test 4: Repository Download (SaaS Simulation)
        print("\n--- Test 4: Repository Download (SaaS Simulation) ---")
        repo_path = simulator.download_repository_via_api("bgfast", "cognite-quickstart", "main")
        download_success = repo_path is not None
        
        if download_success:
            # Test 5: Config Files Discovery
            print("\n--- Test 5: Config Files Discovery ---")
            config_files = simulator.find_config_files(repo_path)
            config_success = len(config_files) > 0
            print(f"📋 Found config files: {config_files}")
            
            # Test 6: Toolkit Build with Environment (SaaS Simulation)
            print("\n--- Test 6: Toolkit Build with Environment (SaaS Simulation) ---")
            build_success = simulator.test_toolkit_build(repo_path, "config.weather.yaml")
            
            # Test 7: Toolkit Deploy with Environment (SaaS Simulation)
            print("\n--- Test 7: Toolkit Deploy with Environment (SaaS Simulation) ---")
            deploy_success = simulator.test_toolkit_deploy(repo_path, "config.weather.yaml")
        else:
            config_success = build_success = deploy_success = False
        
        # Summary
        print("\n--- Test Summary ---")
        tests = [
            ("Environment Variables", env_success),
            ("GitHub API Connection", api_success),
            ("Toolkit Availability", toolkit_success),
            ("Repository Download", download_success),
            ("Config Files Discovery", config_success),
            ("Toolkit Build with Env", build_success),
            ("Toolkit Deploy with Env", deploy_success)
        ]
        
        passed = sum(1 for _, success in tests if success)
        total = len(tests)
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\nPassed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed >= total * 0.8:  # 80% success rate
            print("✅ SaaS simulation test suite passed!")
            return 0
        else:
            print("❌ SaaS simulation test suite failed!")
            return 1
            
    finally:
        # Cleanup
        simulator.cleanup()


if __name__ == "__main__":
    exit(main())
