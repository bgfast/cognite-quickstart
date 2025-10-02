import os
import streamlit as st
import requests
import zipfile
import tempfile
import shutil
from . import state

def render_repo_inputs():
    """Simplified repo inputs - CDF zip files only"""
    # Return dummy values since we'll select the actual repo from CDF
    return "cdf", "packages", "main", "CDF Files"

def render_download_section(repo_owner, repo_name, selected_branch, access_type):
    """Render download section - handles both local and SaaS environments"""
    
    # Import CDF files service
    from services.cdf_files_service import render_cdf_zip_selection, download_zip_from_cdf
    
    # Get CLIENT and IS_LOCAL_ENV from main without importing
    import sys
    main_module = sys.modules.get('main')
    if main_module:
        CLIENT = getattr(main_module, 'CLIENT', None)
        IS_LOCAL_ENV = getattr(main_module, 'IS_LOCAL_ENV', True)
    else:
        CLIENT = None
        IS_LOCAL_ENV = True
    
    # Check environment and provide appropriate options
    if CLIENT and not IS_LOCAL_ENV:
        # SaaS environment - use CDF zip files
        
        # Step 1: Show available repositories and let user select
        selected_zip = render_cdf_zip_selection(CLIENT, IS_LOCAL_ENV)
        if not selected_zip:
            return None
        
        
        # Step 2: Show download button - only download when user clicks
        if st.button("📥 Download Repository", type="primary", key="download_from_cdf"):
            # Download and extract from CDF
            with st.spinner("📥 Downloading from CDF..."):
                zip_path = download_zip_from_cdf(selected_zip, CLIENT)
                if not zip_path:
                    st.error("Failed to download from CDF")
                    return None
                    
                extracted_path = extract_zip_to_temp_dir(zip_path)
                if not extracted_path:
                    st.error("Failed to extract zip file")
                    return None
                    
                st.session_state['extracted_path'] = extracted_path
                
                # Clean up temp zip file
                try:
                    os.unlink(zip_path)
                except:
                    pass
                    
                st.success("✅ Repository downloaded and extracted from CDF")
                return extracted_path
        
        return None
        
    else:
        # Local development - provide fallback options
        st.info("💻 **Local Development Mode**: CDF zip files not available")
        
        # Check for local bundled files or directories
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        local_repo_dir = os.path.join(base_dir, "cognite-quickstart-main")
        bundled_zip = os.path.join(base_dir, "bundled_repo.zip")
        
        if os.path.isdir(local_repo_dir):
            st.success("📂 Using local repository directory for development")
            st.session_state['extracted_path'] = local_repo_dir
            return local_repo_dir
        elif os.path.exists(bundled_zip):
            st.info("📦 Using bundled repository for development")
            if st.button("📥 Extract Bundled Repository", type="primary"):
                extracted = extract_zip_to_temp_dir(bundled_zip)
                if extracted:
                    st.session_state['extracted_path'] = extracted
                    st.success("✅ Repository extracted from bundled ZIP")
                    return extracted
                else:
                    st.error("❌ Failed to extract bundled ZIP")
            return None
        else:
            st.error("❌ No local repository or bundled files available for development")
            st.info("💡 **Options for local development:**")
            st.info("- Place a repository in `cognite-quickstart-main/` directory")
            st.info("- Add a `bundled_repo.zip` file")
            st.info("- Deploy to CDF Streamlit for full CDF integration")
            return None

def extract_zip_to_temp_dir(zip_path):
    """Extract ZIP file to temporary directory (for future CDF zip download feature)"""
    try:
        import zipfile
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # If the ZIP has a single top-level directory, use that as the root
        try:
            entries = [e for e in os.listdir(temp_dir) if not e.startswith('__MACOSX')]
            if len(entries) == 1:
                candidate = os.path.join(temp_dir, entries[0])
                if os.path.isdir(candidate):
                    import logging
                    logging.getLogger("github_repo_deployer").info(f"Bundled ZIP extracted to single dir {candidate}")
                    return candidate
        except Exception:
            pass

        import logging
        logging.getLogger("github_repo_deployer").info(f"Bundled ZIP extracted to temp dir {temp_dir}")
        return temp_dir
    except Exception as e:
        try:
            import logging
            logging.getLogger("github_repo_deployer").exception(f"Extract ZIP failed: {e}")
        except Exception:
            pass
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