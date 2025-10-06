#!/usr/bin/env python3
"""
Download Application Packages as zip files for Cognite Toolkit deployment

This script downloads GitHub repositories as zip files based on URLs
in repositories.yaml and saves them in the files/ directory for the 
Cognite Toolkit to upload to CDF.

For each repository, this script creates TWO zip files:
1. Full zip: Contains the complete repository (e.g., cognite-quickstart-main.zip)
2. Mini zip: Contains only config-specific README files (e.g., cognite-quickstart-main-mini.zip)

Mini Zip Contents:
- ONLY includes: readme.{config}.md or README.{config}.md files
- Examples: readme.weather.md, readme.hw-all.md, README.all.md
- These map to: config.weather.yaml, config.hw-all.yaml, config.all.yaml
- EXCLUDES: Generic README.md files (no config suffix)

The mini zips are used by Streamlit apps to:
- Download lightweight files from CDF for quick browsing
- Present users with available configuration options
- Show configuration-specific details before downloading full repositories
- Provide a better UX by avoiding large downloads until needed

Naming Convention:
- Full zips: {repo-name}.zip
- Mini zips: {repo-name}-mini.zip

This makes it easy for Streamlit to:
1. List all available packages by downloading *-mini.zip files
2. Parse config-specific README files to show configuration options
3. Download full {repo-name}.zip only when user selects a configuration
"""

import os
import sys
import requests
import yaml
import subprocess
import zipfile
import io
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
    
    def generate_mini_filename(self, base_filename: str) -> str:
        """Generate filename for mini zip (README files only)"""
        return f"{base_filename}-mini.zip"
    
    def create_mini_zip(self, full_zip_content: bytes, base_filename: str) -> Optional[bytes]:
        """
        Create a mini zip containing only config-specific README files from the full zip.
        Only includes README.{config}.md or readme.{config}.md files that map to config.{config}.yaml.
        Excludes generic README.md files.
        
        This mini zip is used by Streamlit to present installation options to users.
        
        Args:
            full_zip_content: The full zip file content
            base_filename: Base filename for logging
            
        Returns:
            bytes: Mini zip content, or None if no config README files found
        """
        try:
            print(f"📝 Creating mini zip with config-specific README files...")
            
            # Read the full zip
            with zipfile.ZipFile(io.BytesIO(full_zip_content), 'r') as full_zip:
                # Find only config-specific README files (README.xyz.md or readme.xyz.md)
                # Pattern: readme.{something}.md where {something} maps to config.{something}.yaml
                # Exclude: README.md, readme.md (no suffix after readme)
                readme_files = []
                for name in full_zip.namelist():
                    basename = os.path.basename(name).lower()
                    # Must end with .md and contain 'readme'
                    if basename.endswith('.md') and basename.startswith('readme'):
                        # Check if it has a config suffix (readme.xyz.md, not just readme.md)
                        # Pattern: readme.{config}.md where config is not empty
                        parts = basename.split('.')
                        # Should be: ['readme', 'config-name', 'md'] (3 parts minimum)
                        if len(parts) >= 3 and parts[0] == 'readme' and parts[-1] == 'md':
                            # Has a config suffix (e.g., readme.weather.md, readme.hw-all.md)
                            readme_files.append(name)
                
                readme_files = sorted(readme_files)
                
                if not readme_files:
                    print(f"⚠️ No config-specific README files found in {base_filename}")
                    return None
                
                print(f"📋 Found {len(readme_files)} config-specific README files")
                
                # Create mini zip in memory
                mini_zip_buffer = io.BytesIO()
                with zipfile.ZipFile(mini_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as mini_zip:
                    for readme_file in readme_files:
                        content = full_zip.read(readme_file)
                        mini_zip.writestr(readme_file, content)
                
                mini_zip_content = mini_zip_buffer.getvalue()
                print(f"✅ Mini zip created: {len(mini_zip_content):,} bytes")
                return mini_zip_content
                
        except Exception as e:
            print(f"❌ Failed to create mini zip for {base_filename}: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            return None
    
    
    def add_custom_files_to_zip(self, zip_content: bytes, custom_files: Dict[str, str], base_filename: str) -> Optional[bytes]:
        """
        Add custom files to an existing zip file.
        
        Args:
            zip_content: The original zip file content
            custom_files: Dict mapping destination paths in zip to source file paths on disk
            base_filename: Base filename for logging
            
        Returns:
            bytes: Updated zip content with custom files added, or None on error
        """
        try:
            print(f"📝 Adding {len(custom_files)} custom file(s) to {base_filename}...")
            
            # Read the original zip
            original_zip = zipfile.ZipFile(io.BytesIO(zip_content), 'r')
            
            # Create new zip with original content + custom files
            new_zip_buffer = io.BytesIO()
            with zipfile.ZipFile(new_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # Copy all original files
                for item in original_zip.namelist():
                    content = original_zip.read(item)
                    new_zip.writestr(item, content)
                
                # Add custom files
                for dest_path, source_path in custom_files.items():
                    if os.path.exists(source_path):
                        with open(source_path, 'rb') as f:
                            content = f.read()
                        new_zip.writestr(dest_path, content)
                        print(f"   ✓ Added: {dest_path} (from {source_path})")
                    else:
                        print(f"   ✗ Skipped: {source_path} (file not found)")
            
            original_zip.close()
            new_zip_content = new_zip_buffer.getvalue()
            print(f"✅ Updated zip created: {len(new_zip_content):,} bytes")
            return new_zip_content
            
        except Exception as e:
            print(f"❌ Failed to add custom files to {base_filename}: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            return None
    
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
        """Download a single repository and create both full and mini zips"""
        try:
            print(f"🎯 Processing repository: {repo_info['name']}")
            print(f"🔗 URL: {repo_info['url']}")
            
            # Download zip file
            zip_content = self.download_zip_file(repo_info["url"], repo_info["name"])
            
            # Check if this is the cognite-library-pattern-mode-beta repo and add custom files
            if repo_info['name'] == 'cognite-library-pattern-mode-beta':
                print()
                print("🎯 Detected cognite-library-pattern-mode-beta repository")
                print("📝 Adding custom cdf_file_annotation files...")
                
                # Define custom files to add (both readme and config)
                script_dir = Path(__file__).parent
                custom_files = {
                    'library-added-pattern-mode-beta/readme.cdf_file_annotation.md': str(script_dir / 'readme.cdf_file_annotation.md'),
                    'library-added-pattern-mode-beta/config.cdf_file_annotation.yaml': str(script_dir / 'config.cdf_file_annotation.yaml')
                }
                
                # Add custom files to the full zip
                updated_zip_content = self.add_custom_files_to_zip(zip_content, custom_files, repo_info["name"])
                if updated_zip_content:
                    zip_content = updated_zip_content
                    print(f"✅ Custom files added to full zip")
                else:
                    print(f"⚠️ Failed to add custom files, continuing with original zip")
                print()
            
            # Generate filename for full zip
            filename = self.generate_filename(repo_info["name"])
            print(f"🏷️ Generated filename: {filename}")
            
            # Save full zip to files directory
            success = self.save_to_files_dir(zip_content, filename)
            
            if not success:
                print(f"💥 Failed to save full zip for {repo_info['name']}")
                return False
            
            print(f"✅ Full zip saved successfully")
            print()
            
            # Create and save mini zip with README files
            mini_zip_content = self.create_mini_zip(zip_content, repo_info["name"])
            
            if mini_zip_content:
                mini_filename = self.generate_mini_filename(repo_info["name"])
                print(f"🏷️ Generated mini filename: {mini_filename}")
                
                mini_success = self.save_to_files_dir(mini_zip_content, mini_filename)
                
                if mini_success:
                    print(f"✅ Mini zip saved successfully")
                else:
                    print(f"⚠️ Failed to save mini zip (full zip saved successfully)")
            else:
                print(f"⚠️ Skipping mini zip creation (no README files found)")
            
            print(f"🎉 Successfully processed {repo_info['name']}")
            return True
            
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
        full_zip_files = [f for f in self.files_dir.glob("*.zip") if not f.name.endswith("-mini.zip")]
        mini_zip_files = list(self.files_dir.glob("*-mini.zip"))
        print(f"📁 Files in directory:")
        print(f"   • Full zips: {len(full_zip_files)} files")
        print(f"   • Mini zips (README only): {len(mini_zip_files)} files")
        print(f"   • Total: {len(full_zip_files) + len(mini_zip_files)} files")
        
        if success_count == total_count:
            print()
            print("🎉 All repositories downloaded successfully!")
            print("💡 Next steps:")
            print("   1. Run 'cdf build --env your-env modules/app-packages-zips/'")
            print("   2. Run 'cdf deploy --env your-env modules/app-packages-zips/'")
            print("   3. Files will be uploaded to CDF Files API automatically")
            print("   4. Streamlit app will download mini zips to present installation options")
            print("   5. Use the GitHub Repo Deployer Streamlit app to deploy selected configs")
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
