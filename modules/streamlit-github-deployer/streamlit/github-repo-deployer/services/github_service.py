"""
GitHub Service for Repository Management

This service handles repository selection and download from CDF Files API.
All repositories are stored as zip files in the app-packages space in CDF.
"""

import streamlit as st
import tempfile
import os
from services.cdf_files_service import render_cdf_zip_selection, download_zip_from_cdf


def render_repo_inputs():
    """Render repository input section - simplified for CDF-only approach"""
    # We don't need GitHub URL inputs anymore since we use CDF Files API
    # Return dummy values for compatibility (repo_owner, repo_name, selected_branch, access_type)
    return "cognite", "cognite-quickstart", "main", "public"


def render_download_section(repo_owner, repo_name, selected_branch, access_type, client=None):
    """Render the download section using CDF Files API"""
    
    CLIENT = client
    
    # Debug info
    if st.session_state.get('debug_mode', False):
        st.sidebar.write(f"🔍 Debug: CLIENT={bool(CLIENT)}")
    
    # Key all logic around having a valid CogniteClient
    if CLIENT:
        try:
            # Client is valid - show CDF repository selection
            st.subheader("📦 Select Repository from CDF")
            
            # Step 1: Show available repositories and let user select
            selected_zip = render_cdf_zip_selection()
            if not selected_zip:
                return None
            
            # Step 2: Download button
            if st.button("📥 Download Repository", type="primary"):
                with st.spinner("Downloading repository from CDF..."):
                    zip_path = download_zip_from_cdf(selected_zip)
                    if not zip_path:
                        st.error("❌ Failed to download repository from CDF")
                        return None
                        
                    extracted_path = extract_zip_to_temp_dir(zip_path)
                    if not extracted_path:
                        st.error("❌ Failed to extract zip file")
                        return None
                        
                    st.session_state['extracted_path'] = extracted_path
                    
                    # Clean up temp zip file
                    try:
                        import os
                        os.unlink(zip_path)
                    except:
                        pass
                        
                    st.success("✅ Repository downloaded and extracted from CDF")
                    return extracted_path
            
            # Return existing path if already downloaded
            return st.session_state.get('extracted_path')
            
        except Exception as e:
            st.error(f"❌ CDF client error: {e}")
            return None
    else:
        st.error("❌ No CDF connection available. Cannot access repository files.")
        st.info("💡 Please check CDF authentication and try refreshing the page.")
        return None


def extract_zip_to_temp_dir(zip_path):
    """Extract zip file to temporary directory"""
    try:
        import zipfile
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="repo_")
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory (usually has a single subdirectory)
        extracted_items = os.listdir(temp_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
            return os.path.join(temp_dir, extracted_items[0])
        else:
            return temp_dir
            
    except Exception as e:
        st.error(f"❌ Failed to extract ZIP file: {e}")
        return None


def find_config_files(repo_path):
    """Find all config.*.yaml files in the repository"""
    import os
    import glob
    
    if not repo_path or not os.path.exists(repo_path):
        st.error(f"❌ repo_path does not exist: {repo_path}")
        return []
    
    # DEBUG: Show the extracted structure
    st.info(f"🔍 DEBUG: Searching for config files starting from: {repo_path}")
    
    # Show what's in the repo_path directory
    if os.path.exists(repo_path):
        items = os.listdir(repo_path)
        st.info(f"🔍 DEBUG: Contents of {repo_path}:")
        for item in sorted(items):
            item_path = os.path.join(repo_path, item)
            if os.path.isdir(item_path):
                st.text(f"  📁 {item}/")
            else:
                st.text(f"  📄 {item}")
    
    # Look for config files in multiple locations:
    search_paths = [
        repo_path,                           # Current directory
        os.path.dirname(repo_path),          # Parent directory  
        os.path.dirname(os.path.dirname(repo_path))  # Grandparent directory
    ]
    
    config_files = []
    for i, search_path in enumerate(search_paths):
        if os.path.exists(search_path):
            st.info(f"🔍 DEBUG: Searching in path {i+1}: {search_path}")
            
            # Show all files in this directory
            try:
                all_items = os.listdir(search_path)
                yaml_files = [f for f in all_items if f.endswith('.yaml') or f.endswith('.yml')]
                if yaml_files:
                    st.text(f"  YAML files found: {yaml_files}")
                else:
                    st.text(f"  No YAML files found")
                
                # Look specifically for config files
                config_pattern = os.path.join(search_path, "config.*.yaml")
                found_configs = glob.glob(config_pattern)
                if found_configs:
                    st.success(f"  ✅ Config files found: {[os.path.basename(f) for f in found_configs]}")
                else:
                    st.text(f"  No config.*.yaml files found")
                    
                config_files.extend(found_configs)
            except Exception as e:
                st.error(f"  Error listing directory: {e}")
    
    # Remove duplicates and return relative paths for display
    unique_configs = list(set(config_files))
    relative_configs = []
    for config_file in unique_configs:
        relative_path = os.path.basename(config_file)
        relative_configs.append(relative_path)
    
    st.info(f"🔍 DEBUG: Final result - found {len(relative_configs)} config files: {relative_configs}")
    return sorted(relative_configs)


def extract_zip_to_memory(zip_path):
    """Extract ZIP file contents to memory and return config files directly"""
    try:
        import zipfile
        import os
        
        config_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            st.info(f"🔍 DEBUG: Found {len(file_list)} files in zip")
            
            # Find config files
            for file_path in file_list:
                filename = os.path.basename(file_path)
                if filename.startswith('config.') and filename.endswith('.yaml'):
                    config_files.append(filename)
                    st.info(f"🔍 DEBUG: Found config file: {filename}")
            
            # Store the zip file path for later use (for deployment commands)
            # We'll work directly with the zip instead of extracting
            st.session_state['zip_file_path'] = zip_path
            st.session_state['config_files'] = config_files
            
        st.success(f"✅ Found {len(config_files)} config files in zip")
        return config_files
        
    except Exception as e:
        st.error(f"❌ Failed to read ZIP file: {e}")
        return []