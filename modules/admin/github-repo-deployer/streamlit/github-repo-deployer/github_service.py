import os
import streamlit as st
import state

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
        url = st.text_input("GitHub Repository URL", placeholder="https://github.com/owner/repo")
        
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
    
    # Load available branches
    with st.spinner("Loading available branches..."):
        import requests
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
        try:
            response = requests.get(url)
            response.raise_for_status()
            branches_data = response.json()
            branches = [branch['name'] for branch in branches_data]
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
    """Render download section and handle repository download"""
    st.header("📥 Download Repository")
    
    if st.button("📥 Download Repository", type="primary"):
        with st.spinner(f"Downloading {repo_owner}/{repo_name} ({selected_branch})..."):
            # Use the working download function from main.py
            import main as legacy
            zip_path = legacy.download_github_repo_zip(repo_owner, repo_name, selected_branch)
            
            if zip_path:
                st.session_state['uploaded_zip_path'] = zip_path
                st.success("✅ Repository downloaded successfully!")
                return zip_path
            else:
                st.error("❌ Failed to download repository")
                return None
    
    return None

def extract_zip_to_temp_dir(zip_path):
    """Extract ZIP file to temporary directory"""
    import main as legacy
    return legacy.extract_zip_to_temp_dir(zip_path)

def find_config_files(root):
    """Find config.*.yaml files in the repository"""
    import main as legacy
    return legacy.find_config_files(root)