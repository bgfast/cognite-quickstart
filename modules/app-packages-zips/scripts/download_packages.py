#!/usr/bin/env python3
"""
Download Application Packages as zip files for Cognite Toolkit deployment

This script downloads GitHub repositories as zip files based on URLs
in repositories.yaml and saves them in the files/ directory for the 
Cognite Toolkit to upload to CDF.
"""

import os
import sys
import requests
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import time


class AppPackageDownloader:
    """Download application packages as zip files for Cognite Toolkit"""
    
    def __init__(self):
        """Initialize the downloader"""
        self.session = requests.Session()
        self.files_dir = Path(__file__).parent.parent / "files"
        self.config_file = Path(__file__).parent / "repositories.yaml"
        self.files_dir.mkdir(exist_ok=True)
        
        # Set up GitHub authentication
        github_token = self.get_github_token()
        if github_token:
            self.session.headers.update({'Authorization': f'token {github_token}'})
            print("🔑 GitHub authentication configured")
        else:
            print("⚠️ No GitHub authentication - may fail for private repositories")
        
        # Load repository list
        self.config = self.load_config()
        self.repositories = self.config.get('repositories', [])
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment variable or GitHub CLI"""
        # First, check environment variable
        token = os.getenv('GITHUB_TOKEN')
        if token:
            print("📋 Using GitHub token from GITHUB_TOKEN environment variable")
            return token
        
        # Try to get token from GitHub CLI
        try:
            result = subprocess.run(['gh', 'auth', 'token'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print("📋 Using GitHub token from GitHub CLI (gh auth token)")
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        print("💡 No GitHub token found. Set GITHUB_TOKEN env var or run 'gh auth login'")
        return None
    
    def load_config(self) -> Dict:
        """Load simple repository configuration from YAML file"""
        try:
            if not self.config_file.exists():
                print(f"❌ Config file not found: {self.config_file}")
                print("💡 Creating default config...")
                return self.create_default_config()
            
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config with {len(config.get('repositories', []))} repositories")
                return config
                
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            print("💡 Using default config...")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default config if none exists"""
        return {
            'repositories': [
                {
                    'url': 'https://github.com/cognitedata/library/archive/refs/heads/added/pattern-mode-beta.zip',
                    'name': 'cognite-library-pattern-mode-beta'
                },
                {
                    'url': 'https://github.com/bgfast/cognite-quickstart/archive/refs/heads/main.zip',
                    'name': 'cognite-quickstart-main'
                },
                {
                    'url': 'https://github.com/cognitedata/cognite-samples/archive/refs/heads/main.zip',
                    'name': 'cognite-samples-main'
                }
            ],
            'config': {
                'keep_versions': 5,
                'cleanup_older_than_days': 30
            }
        }
    
    def download_zip_file(self, url: str, name: str) -> bytes:
        """Download zip file from URL"""
        try:
            print(f"📥 Downloading {name}...")
            print(f"🔗 URL: {url}")
            print(f"⏳ Initiating HTTP request...")
            
            # Add rate limiting
            time.sleep(1)
            
            print(f"🌐 Connecting to GitHub...")
            response = self.session.get(url, timeout=300, stream=True)
            
            print(f"📡 Response status: {response.status_code}")
            response.raise_for_status()
            
            # Get content length if available
            content_length = response.headers.get('content-length')
            if content_length:
                print(f"📦 Expected file size: {int(content_length):,} bytes")
            
            print(f"⬇️ Downloading content...")
            content = response.content
            
            print(f"✅ Downloaded {len(content):,} bytes")
            print(f"🔍 Content type: {response.headers.get('content-type', 'unknown')}")
            return content
            
        except requests.RequestException as e:
            print(f"❌ Failed to download {name}: {e}")
            if "404" in str(e):
                print(f"💡 Repository '{name}' may not exist or is private")
                print(f"🔍 Check if the repository URL is correct")
            elif "403" in str(e):
                print(f"🔒 Access denied - repository may be private")
            elif "timeout" in str(e).lower():
                print(f"⏰ Download timed out - try again later")
            raise
    
    def generate_filename(self, base_filename: str) -> str:
        """Generate filename"""
        return f"{base_filename}.zip"
    
    
    def cleanup_old_files(self) -> None:
        """Clean up old zip files - with simple names, we just overwrite existing files"""
        print("🧹 Cleanup: Files will be overwritten if they already exist")
    
    def save_to_files_dir(self, content: bytes, filename: str) -> bool:
        """Save zip file to files directory for Cognite Toolkit"""
        try:
            file_path = self.files_dir / filename
            print(f"💾 Saving {filename}...")
            print(f"📁 Target directory: {self.files_dir}")
            print(f"📄 Full path: {file_path}")
            print(f"💽 Writing {len(content):,} bytes to disk...")
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Verify file was written correctly
            actual_size = file_path.stat().st_size
            print(f"✅ File saved successfully!")
            print(f"📊 File size on disk: {actual_size:,} bytes")
            
            if actual_size != len(content):
                print(f"⚠️ Size mismatch! Expected: {len(content):,}, Got: {actual_size:,}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {filename}: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            return False
    
    def download_repository(self, repo_info: Dict[str, str]) -> bool:
        """Download a single repository"""
        try:
            print(f"🎯 Processing repository: {repo_info['name']}")
            print(f"🔗 URL: {repo_info['url']}")
            
            # Download zip file
            zip_content = self.download_zip_file(repo_info["url"], repo_info["name"])
            
            # Generate filename with timestamp
            filename = self.generate_filename(repo_info["name"])
            print(f"🏷️ Generated filename: {filename}")
            
            # Save to files directory
            success = self.save_to_files_dir(zip_content, filename)
            
            if success:
                print(f"🎉 Successfully processed {repo_info['name']}")
            else:
                print(f"💥 Failed to save {repo_info['name']}")
                
            return success
            
        except Exception as e:
            print(f"❌ Failed to process {repo_info['name']}: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            return False
    
    def run(self) -> None:
        """Run the download process for all repositories"""
        print("=" * 60)
        print("🚀 GitHub Repository Download Process")
        print("=" * 60)
        print(f"📋 Total repositories to process: {len(self.repositories)}")
        print(f"📁 Target directory: {self.files_dir}")
        print(f"📄 Config file: {self.config_file}")
        print()
        
        # Check if target directory exists and is writable
        if not self.files_dir.exists():
            print(f"📁 Creating target directory: {self.files_dir}")
            self.files_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Target directory ready: {self.files_dir}")
        print()
        
        # Run cleanup before downloading new files
        self.cleanup_old_files()
        print()
        
        success_count = 0
        total_count = len(self.repositories)
        
        for i, repo_info in enumerate(self.repositories, 1):
            print(f"{'=' * 50}")
            print(f"📦 Repository {i}/{total_count}: {repo_info['name']}")
            print(f"🔗 URL: {repo_info['url']}")
            print(f"{'=' * 50}")
            
            if self.download_repository(repo_info):
                success_count += 1
                print(f"✅ Repository {i}/{total_count} completed successfully")
            else:
                print(f"❌ Repository {i}/{total_count} failed")
            
            print()  # Add spacing between downloads
        
        print("=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        print(f"✅ Successful downloads: {success_count}/{total_count}")
        print(f"❌ Failed downloads: {total_count - success_count}/{total_count}")
        print(f"📈 Success rate: {(success_count/total_count)*100:.1f}%")
        
        # Show downloaded files
        zip_files = list(self.files_dir.glob("*.zip"))
        print(f"📁 Files in directory: {len(zip_files)} zip files")
        
        if success_count == total_count:
            print()
            print("🎉 All repositories downloaded successfully!")
            print("💡 Next steps:")
            print("   1. Run 'cdf build --env your-env modules/app-packages-zips/'")
            print("   2. Run 'cdf deploy --env your-env modules/app-packages-zips/'")
            print("   3. Files will be uploaded to CDF Files API automatically")
            print("   4. Use the GitHub Repo Deployer Streamlit app to access files")
        else:
            print()
            print("⚠️ Some repositories failed to download")
            print("💡 Check the error messages above for details")
        
        print("=" * 60)


def main():
    """Main entry point"""
    try:
        downloader = AppPackageDownloader()
        downloader.run()
    except Exception as e:
        print(f"❌ Download process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
