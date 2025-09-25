import os
import streamlit as st
import requests
import zipfile
import tempfile
import shutil
from . import state

def render_repo_inputs():
    """Render repository input UI and return repo details"""
    st.header("📁 Repository Configuration")
    
    # Repository input method
    input_method = st.radio("How would you like to specify the repository?", ["🔗 Paste GitHub URL", "✏️ Enter Owner & Name"])
    
    repo_owner = None
    repo_name = None
    selected_branch = "main"
    access_type = "🌐 Public Repository (No GitHub account needed)"
    
    if input_method == "🔗 Paste GitHub URL":
        url = st.text_input("GitHub Repository URL", value="https://github.com/bgfast/cognite-quickstart", placeholder="https://github.com/owner/repo")
        
        if url:
            # Parse GitHub URL
            import re
            patterns = [
                r'https?://github\.com/([^/]+)/([^/]+)',
                r'git@github\.com:([^/]+)/([^/]+)',
                r'github\.com/([^/]+)/([^/]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    repo_owner, repo_name = match.group(1), match.group(2)
                    break
            
            if not repo_owner or not repo_name:
                st.error("❌ Invalid GitHub URL. Please enter a valid GitHub repository URL.")
                return None
            else:
                st.success(f"✅ Parsed: {repo_owner}/{repo_name}")
    
    elif input_method == "✏️ Enter Owner & Name":
        col1, col2 = st.columns(2)
        with col1:
            repo_owner = st.text_input("Repository Owner", placeholder="owner")
        with col2:
            repo_name = st.text_input("Repository Name", placeholder="repo")
    
    if not repo_owner or not repo_name:
        return None
    
    # Load available branches with rate limiting
    with st.spinner("Loading available branches..."):
        try:
            from core.rate_limiter import get_github_branches_with_rate_limit
            branches = get_github_branches_with_rate_limit(repo_owner, repo_name)
        except ImportError:
            # Fallback to simple request if rate limiter not available
            import requests
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    branches_data = response.json()
                    branches = [branch['name'] for branch in branches_data]
                else:
                    st.warning(f"⚠️ Could not load branches: {response.status_code}")
                    branches = ["main"]
            except Exception as e:
                st.warning(f"⚠️ Could not load branches: {e}")
                branches = ["main"]
    
    if branches:
        selected_branch = st.selectbox("Select Branch", branches, index=0 if "main" in branches else 0)
        st.info(f"📋 Found {len(branches)} branches")
    else:
        st.warning("⚠️ Could not load branches, using 'main' as default")
        selected_branch = "main"
    
    # Store in session state
    st.session_state['repo_owner'] = repo_owner
    st.session_state['repo_name'] = repo_name
    st.session_state['selected_branch'] = selected_branch
    st.session_state['access_type'] = access_type
    
    return repo_owner, repo_name, selected_branch, access_type

def render_download_section(repo_owner, repo_name, selected_branch, access_type):
    """Render download section and handle repository download with caching"""
    st.header("📥 Download Repository")
    
    # Fast-iteration path: allow using a bundled ZIP that ships with the app
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    bundled_zip = os.path.join(base_dir, "bundled_repo.zip")
    bundled_exists = os.path.exists(bundled_zip)
    use_bundled = st.checkbox(
        "Use bundled ZIP (dev fast path)", 
        value=bundled_exists, 
        help="If present, uses bundled_repo.zip to skip GitHub download"
    )
    if use_bundled:
        if bundled_exists:
            st.info("📦 Using bundled_repo.zip to bypass download")
            extracted = extract_zip_to_temp_dir(bundled_zip)
            if extracted:
                st.session_state['extracted_path'] = extracted
                st.session_state['dev_use_bundled_zip'] = True
                st.success("✅ Repository extracted from bundled ZIP")
                return extracted
            else:
                st.error("❌ Failed to extract bundled ZIP")
                return None
        else:
            st.warning("⚠️ bundled_repo.zip not found next to main.py. Place it under streamlit/github-repo-deployer/")
    
    # Check if repository is already cached
    from core.cache_manager import is_repository_cached, get_cached_repository, cache_repository, get_cache_stats
    
    is_cached = is_repository_cached(repo_owner, repo_name, selected_branch)
    
    if is_cached:
        st.success(f"✅ Repository {repo_owner}/{repo_name}@{selected_branch} is already cached!")
        st.info("💾 Using cached version to avoid re-downloading")
        
        # Show cache stats
        cache_stats = get_cache_stats()
        st.info(f"📊 Cache: {cache_stats['total_repositories']} repos, {cache_stats['total_size_mb']} MB")
        
        if st.button("🔄 Force Re-download", help="Download fresh copy even if cached"):
            # Force download
            with st.spinner(f"Downloading {repo_owner}/{repo_name} ({selected_branch})..."):
                repo_path = download_github_repo_zip(repo_owner, repo_name, selected_branch)
                
                if repo_path:
                    st.session_state['extracted_path'] = repo_path
                    st.success("✅ Repository downloaded and cached successfully!")
                    return repo_path
                else:
                    st.error("❌ Failed to download repository")
                    return None
        else:
            # Use cached version directly (return directory path, not a ZIP)
            cached_path = get_cached_repository(repo_owner, repo_name, selected_branch)
            if cached_path:
                st.session_state['extracted_path'] = cached_path
                st.success("✅ Using cached repository!")
                return cached_path
    else:
        # Not cached, download normally
        if st.button("📥 Download Repository", type="primary"):
            with st.spinner(f"Downloading {repo_owner}/{repo_name} ({selected_branch})..."):
                repo_path = download_github_repo_zip(repo_owner, repo_name, selected_branch)
                
                if repo_path:
                    st.session_state['extracted_path'] = repo_path
                    st.success("✅ Repository downloaded and cached successfully!")
                    return repo_path
                else:
                    st.error("❌ Failed to download repository")
                    return None
    
    return None

def extract_zip_to_temp_dir(zip_path):
    """Extract ZIP file to temporary directory (for future CDF zip download feature)"""
    try:
        import zipfile
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        st.error(f"Failed to extract ZIP file: {e}")
        return None

def download_github_repo_zip(repo_owner, repo_name, branch="main"):
    """Download GitHub repository using individual file API and cache directly (browser-compatible)"""
    try:
        import time
        import base64
        
        # Get repository tree with rate limiting protection
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
        
        # Add delay to avoid rate limiting
        time.sleep(1)  # 1 second delay before API call
        
        response = requests.get(url, timeout=30)
        
        # Check for rate limiting
        if response.status_code == 403:
            error_data = response.json()
            if 'rate limit' in error_data.get('message', '').lower():
                st.warning("⚠️ GitHub API rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                response = requests.get(url, timeout=30)
        
        response.raise_for_status()
        
        tree_data = response.json()
        files = [item for item in tree_data.get('tree', []) if item['type'] == 'blob']
        
        st.info(f"📁 Found {len(files)} files in repository")
        
        # Create progress bar for download
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create temporary directory (simulating SaaS temp storage)
        temp_dir = tempfile.mkdtemp()
        repo_path = os.path.join(temp_dir, f"{repo_name}-{branch}")
        os.makedirs(repo_path, exist_ok=True)
        
        st.info(f"📂 Created temp directory: {repo_path}")
        
        # Download each file with real-time progress
        files_downloaded = 0
        important_files = ['config.all.yaml', 'config.weather.yaml', 'requirements.txt', 'README.md']
        
        for i, item in enumerate(files):
            file_path = item['path']
            
            # Update progress bar and status
            progress = (i + 1) / len(files)
            progress_bar.progress(progress)
            status_text.text(f"📥 Downloading file {i+1}/{len(files)}: {file_path}")
            
            # Add delay every 10 files to avoid rate limiting
            if i > 0 and i % 10 == 0:
                status_text.text(f"⏳ Rate limiting protection: waiting 2 seconds... (file {i}/{len(files)})")
                time.sleep(2)
            
            # Get file content
            file_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
            file_response = requests.get(file_url, timeout=10)
            
            # Check for rate limiting on individual files
            if file_response.status_code == 403:
                error_data = file_response.json()
                if 'rate limit' in error_data.get('message', '').lower():
                    status_text.text(f"⚠️ Rate limit hit on file {i+1}/{len(files)}. Waiting 30 seconds...")
                    time.sleep(30)
                    file_response = requests.get(file_url, timeout=10)
            
            if file_response.status_code == 200:
                file_data = file_response.json()
                if file_data.get('type') == 'file':
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    
                    # Create file path
                    full_path = os.path.join(repo_path, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Write file
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    files_downloaded += 1
                    
                    # Show progress for important files
                    if file_path in important_files:
                        st.info(f"  📄 Downloaded: {file_path}")
                else:
                    status_text.text(f"⏭️ Skipping non-file: {file_path}")
            else:
                status_text.text(f"❌ Failed to download: {file_path} (status: {file_response.status_code})")
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text(f"✅ Downloaded {files_downloaded} files successfully!")
        st.success(f"✅ Downloaded {files_downloaded} files successfully!")
        
        # Cache the downloaded repository directly (no ZIP creation)
        from core.cache_manager import cache_repository
        cached_path = cache_repository(repo_owner, repo_name, branch, repo_path)
        st.info(f"💾 Cached repository to: {cached_path}")
        
        # Set the extracted path in session state (not a ZIP path)
        st.session_state['extracted_path'] = repo_path
        
        # Return the directory path instead of ZIP path
        return repo_path
        
    except Exception as e:
        st.error(f"Failed to download repository: {e}")
        return None

def find_config_files(root):
    """Find config.*.yaml files in the repository"""
    config_files = []
    try:
        for root, dirs, files in os.walk(root):
            for file in files:
                if file.startswith('config.') and file.endswith('.yaml'):
                    config_files.append(os.path.join(root, file))
    except Exception as e:
        st.error(f"Failed to find config files: {e}")
    return config_files