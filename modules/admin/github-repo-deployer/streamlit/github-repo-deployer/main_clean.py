import streamlit as st
import requests
import zipfile
import tempfile
import os
import subprocess
import json
import base64
import urllib.parse
import re
from pathlib import Path
from cognite.client import CogniteClient
import time
from dotenv import load_dotenv

# Set page config first (must be before any other Streamlit commands)
st.set_page_config(
    page_title="GitHub Repo to CDF Deployer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Initialization ---
CLIENT = None
IS_LOCAL_ENV = False

def initialize_cdf_client():
    """Initialize CogniteClient with proper error handling for local/SaaS environments"""
    global CLIENT, IS_LOCAL_ENV
    
    try:
        # Try to initialize CDF client
        CLIENT = CogniteClient()
        IS_LOCAL_ENV = False
        st.success("✅ Connected to CDF")
    except Exception as e:
        CLIENT = None
        IS_LOCAL_ENV = True
        if st.session_state.get('debug_mode', False):
            st.warning(f"⚠️ CDF connection failed: {e}")

# Try to initialize CDF client
initialize_cdf_client()

def main():
    
    st.title("🚀 GitHub Repo to CDF Deployer")
    st.markdown("Download files from public GitHub repositories and deploy them using the Cognite toolkit")
    
    # Initialize workflow step
    if 'workflow_step' not in st.session_state:
        st.session_state['workflow_step'] = 1
    
    # Workflow Steps - ALWAYS AT THE TOP
    st.subheader("🚀 GitHub Repository Deployment Workflow")
    
    # Step indicators as clickable tabs
    steps = [
        ("📥 Download Repository", "Download and extract repository files"),
        ("📋 Select Configuration", "Choose deployment configuration"),
        ("🔨 Build Package", "Build the deployment package"),
        ("🚀 Deploy Package", "Deploy to CDF"),
        ("✅ Verify Deployment", "Confirm successful deployment")
    ]
    
    # Create clickable step indicators
    cols = st.columns(len(steps))
    for i, (step_name, step_desc) in enumerate(steps):
        with cols[i]:
            step_num = i + 1
            if step_num == st.session_state['workflow_step']:
                # Current step - highlighted
                if st.button(f"**Step {step_num}:** {step_name}", key=f"step_{step_num}_current", type="primary"):
                    st.session_state['workflow_step'] = step_num
                    st.rerun()
            elif step_num < st.session_state['workflow_step']:
                # Completed step - clickable
                if st.button(f"**Step {step_num}:** {step_name}", key=f"step_{step_num}_completed", help=f"Go back to {step_name}"):
                    st.session_state['workflow_step'] = step_num
                    st.rerun()
            else:
                # Future step - disabled
                st.button(f"**Step {step_num}:** {step_name}", key=f"step_{step_num}_future", disabled=True, help=f"Complete previous steps first")
    
    st.divider()
    
    # Debug mode toggle
    if 'debug_mode' not in st.session_state:
        st.session_state['debug_mode'] = False
    
    with st.sidebar:
        st.header("Settings")
        st.session_state['debug_mode'] = st.toggle("Debug Mode", value=st.session_state['debug_mode'])
        
        if st.session_state['debug_mode']:
            st.markdown("**Debug Info:**")
            st.write(f"CDF Client: {'Connected' if CLIENT else 'Not Connected'}")
            st.write(f"Local Mode: {IS_LOCAL_ENV}")
    
    # Step 1: Download & Environment
    if st.session_state['workflow_step'] == 1:
        import ui_steps
        ui_steps.render_step_1()
        return
    
    # Step 2: Select Configuration
    if st.session_state['workflow_step'] == 2:
        import ui_steps
        ui_steps.render_step_2()
        return
    
    # Step 3: Build Package
    if st.session_state['workflow_step'] == 3:
        import ui_steps
        ui_steps.render_step_3()
        return
    
    # Step 4: Deploy Package
    if st.session_state['workflow_step'] == 4:
        import ui_steps
        ui_steps.render_step_4()
        return
    
    # Step 5: Verify Deployment
    if st.session_state['workflow_step'] == 5:
        import ui_steps
        ui_steps.render_step_5()
        return

if __name__ == "__main__":
    main()
