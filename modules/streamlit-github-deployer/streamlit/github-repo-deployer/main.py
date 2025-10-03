import streamlit as st

# Set page config FIRST (must be before any other Streamlit commands or imports that use Streamlit)
st.set_page_config(
    page_title="GitHub Repo to CDF Deployer v2.35",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now safe to import everything else
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

# --- Global Initialization ---
CLIENT = None

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
    """Initialize CogniteClient - try SaaS first, then local with env vars"""
    global CLIENT
    
    from cognite.client import CogniteClient
    
    # Debug environment info
    if st.session_state.get('debug_mode', False):
        import platform
        st.sidebar.write(f"🔍 Python: {platform.python_version()}")
        st.sidebar.write(f"🔍 Platform: {platform.system()}")
        st.sidebar.write(f"🔍 CDF_PROJECT env: {os.environ.get('CDF_PROJECT', 'Not set')}")
    
    # Method 1: Try SaaS CogniteClient (no parameters)
    try:
        CLIENT = CogniteClient()
        log_debug("✅ CDF client initialized via SaaS")
        st.sidebar.success("✅ SaaS CogniteClient() successful")
        try:
            # Try to get project info for debug (but don't fail if this doesn't work)
            st.sidebar.text(f"Project: {CLIENT.config.project}")
        except:
            pass
        return
    except Exception as saas_error:
        error_type = type(saas_error).__name__
        error_msg = str(saas_error)
        log_debug(f"❌ SaaS CogniteClient failed: {error_type}: {error_msg}")
        st.sidebar.error(f"❌ SaaS failed: {error_type}")
        st.sidebar.text(f"Error: {error_msg}")
    
    # Method 2: Try local CogniteClient with environment variables
    try:
        from cognite.client import ClientConfig
        from cognite.client.credentials import OAuthClientCredentials
        
        config = ClientConfig(
            client_name="streamlit-github-deployer",
            base_url=f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com",
            project=os.environ['CDF_PROJECT'],
            credentials=OAuthClientCredentials(
                token_url=os.environ['IDP_TOKEN_URL'],
                client_id=os.environ['IDP_CLIENT_ID'],
                client_secret=os.environ['IDP_CLIENT_SECRET'],
                scopes=[f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com/.default"]
            )
        )
        CLIENT = CogniteClient(config)
        log_debug("✅ CDF client initialized via OAuth2")
        st.sidebar.success("✅ OAuth2 CogniteClient successful")
        try:
            # Try to get project info for debug (but don't fail if this doesn't work)
            st.sidebar.text(f"Project: {CLIENT.config.project}")
        except:
            pass
        return
    except Exception as oauth_error:
        error_type = type(oauth_error).__name__
        error_msg = str(oauth_error)
        log_debug(f"❌ OAuth2 CogniteClient failed: {error_type}: {error_msg}")
        st.sidebar.error(f"❌ OAuth2 failed: {error_type}")
        st.sidebar.text(f"Error: {error_msg}")
        # Show which env vars are missing
        required_vars = ['CDF_PROJECT', 'CDF_CLUSTER', 'IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TOKEN_URL']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            st.sidebar.text(f"Missing env vars: {missing_vars}")
    
    # Both methods failed
    CLIENT = None
    error_msg = "❌ Failed to initialize CogniteClient via SaaS or OAuth2"
    log_debug(error_msg)
    st.sidebar.error(error_msg)
    st.error(error_msg)

# Load env on import
load_env_from_file()

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

    # Initialize CDF client directly (like your working code)
    st.sidebar.write("🔍 About to initialize CDF client...")
    from cognite.client import CogniteClient
    try:
        CLIENT = CogniteClient()
        st.sidebar.success("✅ SaaS CogniteClient() successful")
        st.sidebar.write(f"🔍 After init: CLIENT={bool(CLIENT)}")
        
        # Test data_modeling access immediately
        try:
            test_instances = CLIENT.data_modeling.instances.list(limit=1)
            st.sidebar.success("✅ data_modeling API accessible")
        except Exception as dm_error:
            st.sidebar.error(f"❌ data_modeling failed: {dm_error}")
            
    except Exception as e:
        CLIENT = None
        st.sidebar.error(f"❌ CogniteClient failed: {e}")
    
    # Store CLIENT in session state for cross-module access
    st.session_state['cdf_client'] = CLIENT
    st.sidebar.write(f"🔍 Stored in session: {bool(st.session_state.get('cdf_client'))}")

    st.title("🚀 GitHub Repo to CDF Deployer")
    st.markdown("Download files from public GitHub repositories and deploy them using the Cognite toolkit")
    st.caption("Version 2.41 - Realistic toolkit-style output showing dynamic resource discovery and deployment")
    
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
    
    # Create always-clickable step indicators
    cols = st.columns(len(steps))
    for i, (step_name, step_desc) in enumerate(steps):
        with cols[i]:
            step_num = i + 1
            is_current = step_num == st.session_state['workflow_step']
            button_type = "primary" if is_current else "secondary"
            
            if st.button(f"**Step {step_num}:** {step_name}", key=f"step_{step_num}", type=button_type, help=step_desc):
                st.session_state['workflow_step'] = step_num
                st.rerun()
    
    st.divider()
    
    # Debug mode toggle
    if 'debug_mode' not in st.session_state:
        st.session_state['debug_mode'] = True  # Default to True for development
    
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
