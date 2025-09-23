import os
import streamlit as st
from . import state

# Thin wrappers that call existing functions left in main.py via st.session_state bridges if needed.

def render_repo_inputs():
    # Minimal placeholder UI to keep refactor incremental.
    # Expect main.py to still present inputs and set these in session.
    repo_owner = st.session_state.get('repo_owner')
    repo_name = st.session_state.get('repo_name')
    selected_branch = st.session_state.get('selected_branch', 'main')
    access_type = st.session_state.get('access_type', '🌐 Public Repository (No GitHub account needed)')
    if not repo_owner or not repo_name:
        return None
    return repo_owner, repo_name, selected_branch, access_type

def render_download_section(repo_owner, repo_name, selected_branch, access_type):
    # Expect main.py handlers to have performed the download already.
    return st.session_state.get('uploaded_zip_path')

def extract_zip_to_temp_dir(path):
    from . import main as legacy
    return legacy.extract_zip_to_temp_dir(path)

def find_config_files(root):
    from . import main as legacy
    return legacy.find_config_files(root)


