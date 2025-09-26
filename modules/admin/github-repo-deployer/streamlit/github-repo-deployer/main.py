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
import logging
from dotenv import load_dotenv

# Import from services
from services import ui_steps

# Set page config first (must be before any other Streamlit commands)
st.set_page_config(
    page_title="GitHub Repo to CDF Deployer v1.92",
            page_icon="🚀",
            layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Initialization ---
CLIENT = None
IS_LOCAL_ENV = False

# --- Logging Setup ---
LOGGER_NAME = "github_repo_deployer"
logger = logging.getLogger(LOGGER_NAME)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_debug(msg: str) -> None:
    logger.info(msg)
    if st.session_state.get('debug_mode', False):
        try:
            st.sidebar.write(f"DBG: {msg}")
        except Exception:
            pass

# --- Env file loading ---
ENV_FILE_PATH = os.path.expanduser('~/envs/.env.bluefield.cog-bgfast.bgfast')
ENV_FILE_LOADED = False

def load_env_from_file() -> None:
    global ENV_FILE_LOADED
    try:
        if os.path.exists(ENV_FILE_PATH):
            load_dotenv(ENV_FILE_PATH, override=True)
            ENV_FILE_LOADED = True
            # Count key env vars without printing secrets
            key_count = sum(1 for k in os.environ.keys() if k.startswith('CDF_') or k.startswith('IDP_'))
            log_debug(f"Loaded env file: {ENV_FILE_PATH} (key vars present: {key_count})")
        else:
            log_debug(f"Env file not found: {ENV_FILE_PATH}")
    except Exception as e:
        logger.exception(f"Failed to load env file {ENV_FILE_PATH}: {e}")

def initialize_cdf_client():
    """Initialize CogniteClient with proper error handling for local/SaaS environments"""
    global CLIENT, IS_LOCAL_ENV
    
    try:
        # Try to initialize CDF client
        CLIENT = CogniteClient()
        IS_LOCAL_ENV = False
        st.success("✅ Connected to CDF")
        log_debug("CDF client initialized successfully")
    except Exception as e:
        CLIENT = None
        IS_LOCAL_ENV = True
        if st.session_state.get('debug_mode', False):
            st.warning(f"⚠️ CDF connection failed: {e}")
        log_debug(f"CDF client init failed: {e}")

# Load env and initialize CDF client on import
load_env_from_file()
initialize_cdf_client()

def main():
    # Reload/run tracking
    st.session_state['__run_counter'] = st.session_state.get('__run_counter', 0) + 1
    st.session_state['__last_run_ts'] = time.time()
    # Snapshot key state for diagnostics
    snapshot = {
        'step': st.session_state.get('workflow_step'),
        'extracted_path_set': bool(st.session_state.get('extracted_path')),
        'config_files_count': len(st.session_state.get('config_files', [])),
        'selected_config': st.session_state.get('selected_config'),
        'selected_env': st.session_state.get('selected_env'),
        'dev_auto_flags': {
            'step2': st.session_state.get('dev_auto_step2', False),
            'step3': st.session_state.get('dev_auto_step3', False),
            'build': st.session_state.get('dev_auto_build', False),
            'deploy': st.session_state.get('dev_auto_deploy', False),
        },
        'run_counter': st.session_state['__run_counter'],
    }
    log_debug(f"App reload. State snapshot: {snapshot}")

    st.title("🚀 GitHub Repo to CDF Deployer")
    st.markdown("Download files from public GitHub repositories and deploy them using the Cognite toolkit")
    st.caption("Version 1.92 - Added debug mode verbose build/deploy logs like shell tests")
    
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
        st.caption(f"Env file: {'loaded' if ENV_FILE_LOADED else 'missing'}")

        # GitHub API Rate Limit Status
        if st.button("🔍 Check GitHub API Status"):
            try:
                from core.rate_limiter import check_rate_limit_status
                rate_status = check_rate_limit_status()
                if rate_status['remaining'] > 0:
                    st.success(f"✅ GitHub API: {rate_status['remaining']}/{rate_status['limit']} requests remaining")
                else:
                    st.warning(f"⚠️ GitHub API rate limited. Reset at {rate_status['reset_time']}")
            except ImportError:
                st.warning("⚠️ Rate limiter not available")
        
        # Cache Management
        st.subheader("💾 Cache Management")
        try:
            from core.cache_manager import get_cache_stats, get_cache
            
            cache_stats = get_cache_stats()
            st.info(f"📊 Cached: {cache_stats['total_repositories']} repos ({cache_stats['total_size_mb']} MB)")
            
            if st.button("🗑️ Clear Cache"):
                get_cache().clear_all_cache()
                st.success("✅ Cache cleared!")
                st.rerun()
                
        except ImportError:
            st.warning("⚠️ Cache manager not available")
            
            if st.session_state['debug_mode']:
                st.markdown("**Debug Info:**")
                st.write(f"CDF Client: {'Connected' if CLIENT else 'Not Connected'}")
                st.write(f"Local Mode: {IS_LOCAL_ENV}")
    
    step = st.session_state['workflow_step']

    if step == 1:
        ui_steps.render_step_1()
        return
    elif step == 2:
        ui_steps.render_step_2()
        return
    elif step == 3:
        ui_steps.render_step_3()
        return
    elif step == 4:
        ui_steps.render_step_4()
        return
    elif step == 5:
        ui_steps.render_step_5()
        return

if __name__ == "__main__":
    main()
