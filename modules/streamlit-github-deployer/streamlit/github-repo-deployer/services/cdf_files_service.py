"""
CDF Files Service for GitHub Repo Deployer

This service handles downloading zip files from CDF Files API as an alternative
to downloading directly from GitHub.
"""

import streamlit as st
import tempfile
import os
from typing import List, Dict, Optional, Tuple


def get_available_zip_files(client, is_local_env) -> List[Dict]:
    """Get list of available zip files from app-packages space using data modeling API"""
    if not client:
        return []
    
    try:
        # Use data modeling API to find zip file instances in app-packages space
        instances = client.data_modeling.instances.list(
            instance_type='node',
            space='app-packages',
            limit=100
        )
        
        # Filter for zip file instances (exclude the app-package node definition)
        zip_instances = [inst for inst in instances if inst.external_id.endswith('.zip')]
        
        
        # Convert instances to file info for the UI
        # We need to get the actual file objects to have the file IDs for download
        zip_files = []
        all_files = client.files.list(limit=5000)
        
        for instance in zip_instances:
            # Find the corresponding file object
            filename = instance.external_id
            if filename.endswith('.zip'):
                repo_name = filename.replace('.zip', '')
                
                # Find the actual file object by name
                file_obj = None
                for f in all_files:
                    if f.name == filename:
                        file_obj = f
                        break
                
                if file_obj:
                    zip_files.append({
                        'id': file_obj.id,  # Use file ID for download
                        'external_id': instance.external_id,
                        'name': filename,
                        'repo_name': repo_name,
                        'uploaded_time': instance.created_time,
                        'metadata': file_obj.metadata or {},
                        'mime_type': file_obj.mime_type,
                        'uploaded': file_obj.uploaded,
                        'space': 'app-packages',
                        'is_data_model_file': False  # Use regular file download since we have file ID
                    })
        
        return sorted(zip_files, key=lambda x: x['uploaded_time'], reverse=True)
        
    except Exception as e:
        st.error(f"Failed to fetch zip files from CDF: {e}")
        return []


def render_cdf_zip_selection(client, is_local_env) -> Optional[Dict]:
    """Render UI for selecting zip files from CDF"""
    
    if not client or is_local_env:
        st.warning("⚠️ CDF connection not available.")
        return None
    
    zip_files = get_available_zip_files(client, is_local_env)
    
    if not zip_files:
        st.info("📭 No zip files found in CDF.")
        return None
    
    # Create selection options
    options = []
    for zf in zip_files:
        # Handle timestamp conversion (uploaded_time might be int timestamp)
        try:
            if isinstance(zf['uploaded_time'], int):
                from datetime import datetime
                upload_date = datetime.fromtimestamp(zf['uploaded_time'] / 1000).strftime('%Y-%m-%d %H:%M')
            else:
                upload_date = zf['uploaded_time'].strftime('%Y-%m-%d %H:%M')
        except:
            upload_date = "unknown"
        
        option_text = f"{zf['repo_name']} (uploaded {upload_date})"
        options.append(option_text)
    
    # Make the selectbox more prominent
    st.subheader("Select repository:")
    selected_idx = st.selectbox(
        "Choose a repository to deploy:",
        range(len(options)),
        format_func=lambda x: options[x],
        key="cdf_zip_selection",
        label_visibility="collapsed"  # Hide the label since we have the subheader
    )
    
    if selected_idx is not None:
        selected_file = zip_files[selected_idx]
        
        # Show file details
        with st.expander("📋 File Details"):
            st.write(f"**Name**: {selected_file['name']}")
            st.write(f"**MIME Type**: {selected_file['mime_type']}")
            
            # Handle timestamp display
            try:
                if isinstance(selected_file['uploaded_time'], int):
                    from datetime import datetime
                    upload_time = datetime.fromtimestamp(selected_file['uploaded_time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    upload_time = str(selected_file['uploaded_time'])
            except:
                upload_time = "unknown"
            
            st.write(f"**Uploaded**: {upload_time}")
            st.write(f"**External ID**: {selected_file['external_id']}")
            st.write(f"**Space**: {selected_file.get('space', 'unknown')}")
            
            if selected_file['metadata']:
                st.write("**Metadata**:")
                for key, value in selected_file['metadata'].items():
                    st.write(f"  - {key}: {value}")
        
        return selected_file
    
    return None


def download_zip_from_cdf(file_info: Dict, client) -> Optional[str]:
    """Download zip file from CDF - handles both regular files and data modeling files"""
    if not client:
        st.error("CDF client not available")
        return None
    
    try:
        with st.status(f"📥 Downloading {file_info['name']} from CDF...", expanded=True) as status:
            # Always download by file ID since that's what works
            status.write("Requesting file from CDF Files API...")
            file_content = client.files.download_bytes(id=file_info['id'])
            
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
