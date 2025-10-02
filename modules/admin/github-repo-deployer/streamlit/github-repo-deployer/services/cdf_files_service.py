"""
CDF Files Service for GitHub Repo Deployer

This service handles downloading zip files from CDF Files API as an alternative
to downloading directly from GitHub.
"""

import streamlit as st
import tempfile
import os
from typing import List, Dict, Optional, Tuple
from main import CLIENT, IS_LOCAL_ENV


def get_available_zip_files() -> List[Dict]:
    """Get list of available zip files from CDF Files API"""
    if not CLIENT or IS_LOCAL_ENV:
        return []
    
    try:
        # Search for zip files - try multiple approaches
        zip_files_found = []
        
        # Approach 1: Search by mime type
        try:
            files = CLIENT.files.list(mime_type="application/zip", limit=100)
            zip_files_found.extend(files)
        except:
            pass
        
        # Approach 2: Search by name pattern if approach 1 fails
        if not zip_files_found:
            try:
                files = CLIENT.files.list(name="*.zip", limit=100)
                zip_files_found.extend(files)
            except:
                pass
        
        # Approach 3: Search in app-packages space if available
        if not zip_files_found:
            try:
                # This might not work if spaces aren't supported in files.list
                files = CLIENT.files.list(limit=100)
                zip_files_found = [f for f in files if f.name.endswith('.zip')]
            except:
                pass
        
        zip_files = []
        for file in zip_files_found:
            # Extract repository info from filename
            filename = file.name
            if filename.endswith('.zip'):
                repo_name = filename.replace('.zip', '')
                
                zip_files.append({
                    'id': file.id,
                    'external_id': file.external_id,
                    'name': file.name,
                    'repo_name': repo_name,
                    'size': file.size,
                    'uploaded_time': file.uploaded_time,
                    'metadata': file.metadata or {}
                })
        
        return sorted(zip_files, key=lambda x: x['uploaded_time'], reverse=True)
        
    except Exception as e:
        st.error(f"Failed to fetch zip files from CDF: {e}")
        return []


def render_cdf_zip_selection() -> Optional[Dict]:
    """Render UI for selecting zip files from CDF"""
    st.subheader("📦 Available Repositories from CDF")
    
    if not CLIENT or IS_LOCAL_ENV:
        st.warning("⚠️ CDF connection not available. Using GitHub direct download.")
        return None
    
    zip_files = get_available_zip_files()
    
    if not zip_files:
        st.info("📭 No zip files found in CDF. Upload some using the app-packages-zips module.")
        return None
    
    st.info(f"📋 Found {len(zip_files)} repositories in CDF")
    
    # Create selection options
    options = []
    for zf in zip_files:
        size_mb = zf['size'] / (1024 * 1024)
        upload_date = zf['uploaded_time'].strftime('%Y-%m-%d %H:%M')
        option_text = f"{zf['repo_name']} ({size_mb:.1f}MB, uploaded {upload_date})"
        options.append(option_text)
    
    selected_idx = st.selectbox(
        "Select repository:",
        range(len(options)),
        format_func=lambda x: options[x],
        key="cdf_zip_selection"
    )
    
    if selected_idx is not None:
        selected_file = zip_files[selected_idx]
        
        # Show file details
        with st.expander("📋 File Details"):
            st.write(f"**Name**: {selected_file['name']}")
            st.write(f"**Size**: {selected_file['size']:,} bytes ({selected_file['size']/(1024*1024):.1f} MB)")
            st.write(f"**Uploaded**: {selected_file['uploaded_time']}")
            st.write(f"**External ID**: {selected_file['external_id']}")
            
            if selected_file['metadata']:
                st.write("**Metadata**:")
                for key, value in selected_file['metadata'].items():
                    st.write(f"  - {key}: {value}")
        
        return selected_file
    
    return None


def download_zip_from_cdf(file_info: Dict) -> Optional[str]:
    """Download zip file from CDF Files API"""
    if not CLIENT or IS_LOCAL_ENV:
        st.error("CDF client not available")
        return None
    
    try:
        with st.status(f"📥 Downloading {file_info['name']} from CDF...", expanded=True) as status:
            status.write("Requesting file from CDF Files API...")
            
            # Download file content
            file_content = CLIENT.files.download_bytes(id=file_info['id'])
            
            status.write(f"Downloaded {len(file_content):,} bytes")
            
            # Save to temporary file
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.write(file_content)
            temp_zip.close()
            
            status.write(f"Saved to temporary file: {temp_zip.name}")
            status.update(label=f"✅ Downloaded {file_info['name']} from CDF", state="complete")
            
            st.success(f"✅ Downloaded {file_info['name']} ({len(file_content):,} bytes)")
            
            return temp_zip.name
            
    except Exception as e:
        st.error(f"Failed to download from CDF: {e}")
        return None




def get_repo_info_from_zip_name(zip_name: str) -> Tuple[str, str, str]:
    """Extract repository info from CDF zip filename"""
    # Expected format: cognite-library-pattern-mode-beta.zip
    # or: cognite-quickstart-main.zip
    # or: cognite-samples-main.zip
    
    base_name = zip_name.replace('.zip', '')
    
    # Handle known patterns
    if base_name == "cognite-library-pattern-mode-beta":
        return "cognitedata", "library", "added/pattern-mode-beta"
    elif base_name == "cognite-quickstart-main":
        return "bgfast", "cognite-quickstart", "main"
    elif base_name == "cognite-samples-main":
        return "cognitedata", "cognite-samples", "main"
    else:
        # Try to parse generic format: owner-repo-branch
        parts = base_name.split('-')
        if len(parts) >= 3:
            # Assume last part is branch, everything before is owner-repo
            branch = parts[-1]
            repo_parts = parts[:-1]
            if len(repo_parts) >= 2:
                owner = repo_parts[0]
                repo = '-'.join(repo_parts[1:])
                return owner, repo, branch
        
        # Fallback - treat as single repo name
        return "unknown", base_name, "main"
