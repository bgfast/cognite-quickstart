"""
GitHub Repo Deployer - Main Application (Modular Design)
"""
import streamlit as st
from cognite.client import CogniteClient
from core.state_manager import state_manager
from core.workflow_engine import workflow_engine
from core.error_handler import error_handler
from services.github_service import github_service
from services.toolkit_service import toolkit_service


# Set page config first (must be before any other Streamlit commands)
st.set_page_config(
    page_title="GitHub Repo to CDF Deployer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_cdf_client():
    """Initialize CogniteClient with proper error handling"""
    try:
        client = CogniteClient()
        st.success("✅ Connected to CDF")
        return client
    except Exception as e:
        if state_manager.is_debug_mode():
            st.warning(f"⚠️ CDF connection failed: {e}")
        return None


def render_step_tabs():
    """Render clickable step tabs"""
    st.subheader("🚀 GitHub Repository Deployment Workflow")
    
    steps = [
        ("📥 Download & Environment", "Download repository and configure environment"),
        ("📋 Select Configuration", "Choose deployment configuration"),
        ("🔨 Build and Deploy", "Build and deploy to CDF")
    ]
    
    # Create clickable step indicators
    cols = st.columns(len(steps))
    for i, (step_name, step_desc) in enumerate(steps):
        with cols[i]:
            step_num = i + 1
            current_step = workflow_engine.get_current_step()
            step_status = workflow_engine.get_step_status(step_num)
            
            if step_status == "current":
                # Current step - highlighted
                if st.button(f"**Step {step_num}:** {step_name}", 
                           key=f"step_{step_num}_current", type="primary"):
                    workflow_engine.advance_to_step(step_num)
                    st.rerun()
            elif step_status == "completed":
                # Completed step - clickable
                if st.button(f"**Step {step_num}:** {step_name}", 
                           key=f"step_{step_num}_completed", 
                           help=f"Go back to {step_name}"):
                    workflow_engine.advance_to_step(step_num)
                    st.rerun()
            else:
                # Future step - disabled
                st.button(f"**Step {step_num}:** {step_name}", 
                         key=f"step_{step_num}_future", disabled=True, 
                         help=f"Complete previous steps first")
    
    st.divider()


def render_sidebar():
    """Render sidebar with settings and debug info"""
    with st.sidebar:
        st.header("Settings")
        
        # Debug mode toggle
        debug_mode = st.toggle("Debug Mode", value=state_manager.is_debug_mode())
        state_manager.set_debug_mode(debug_mode)
        
        if debug_mode:
            st.markdown("**Debug Info:**")
            st.write(f"CDF Client: {'Connected' if initialize_cdf_client() else 'Not Connected'}")
            st.write(f"Toolkit Available: {toolkit_service.get_toolkit_info()['available']}")
            
            # Workflow state
            with st.expander("Workflow State"):
                summary = workflow_engine.get_workflow_summary()
                st.json(summary)


def render_step_1():
    """Step 1: Download & Environment"""
    st.header("⚙️ Step 1: Download & Environment")
    
    # Environment Configuration
    st.subheader("Environment Configuration")
    env_option = st.radio(
        "Choose how to handle environment variables:",
        ["📁 Upload .env file", "🔄 Generate from current CDF connection", "⏭️ Skip (use existing environment)"],
        help="Select how you want to provide environment variables for the deployment"
    )
    
    env_vars = {}
    
    if env_option == "📁 Upload .env file":
        st.subheader("📁 Upload Environment File")
        uploaded_file = st.file_uploader(
            "Choose an environment file",
            type=None,  # Accept all file types
            help="Upload an environment file (.env, .txt, or any text file) containing your CDF project configuration"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.getvalue().decode('utf-8')
                # Parse environment variables
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                
                if env_vars:
                    st.success("✅ Environment file parsed successfully!")
                    st.write(f"**Found {len(env_vars)} environment variables**")
                else:
                    st.warning("⚠️ No environment variables found in file")
                    
            except Exception as e:
                error_handler.handle_error(e, "Parsing environment file")
    
    elif env_option == "🔄 Generate from current CDF connection":
        st.subheader("🔄 Generate from Current CDF Connection")
        if st.button("🔄 Generate .env file"):
            # This would generate from current CDF connection
            st.info("💡 CDF connection generation not implemented yet")
    
    elif env_option == "⏭️ Skip (use existing environment)":
        st.subheader("⏭️ Use Existing Environment")
        st.info("Using environment variables from the current session.")
    
    # Store environment variables
    if env_vars:
        state_manager.set_env_vars(env_vars)
    
    # Repository Configuration
    st.subheader("Repository Configuration")
    
    # Get repository inputs
    repo_input = github_service.render_repo_inputs()
    if repo_input is None:
        st.warning("Please provide repository information to continue")
        return
    
    repo_owner, repo_name, selected_branch = repo_input
    
    # Download section
    st.subheader("📥 Download Repository")
    
    if st.button("📥 Download Repository", type="primary"):
        with st.spinner(f"Downloading {repo_owner}/{repo_name} ({selected_branch})..."):
            try:
                # Download repository
                repo_path = github_service.render_download_section(repo_owner, repo_name, selected_branch)
                
                if repo_path:
                    st.success("✅ Repository downloaded and extracted successfully!")
                    
                    # Enable Step 2
                    if st.button("➡️ Continue to Step 2", type="primary"):
                        workflow_engine.advance_to_step(2)
                        st.rerun()
                else:
                    st.error("❌ Failed to download repository")
                    
            except Exception as e:
                error_handler.handle_error(e, "Repository download")


def render_step_2():
    """Step 2: Select Configuration"""
    st.header("📋 Step 2: Select Configuration")
    
    extracted_path = state_manager.get_extracted_path()
    config_files = state_manager.get_config_files()
    
    if not extracted_path or not config_files:
        st.warning("Nothing to select yet. Go back to Step 1.")
        if st.button("⬅️ Back to Step 1"):
            workflow_engine.advance_to_step(1)
            st.rerun()
        return
    
    st.info(f"Found {len(config_files)} configuration files:")
    
    # Render sub-tabs for each config file
    tabs = st.tabs([f"{cf} ({cf.replace('config.', '').replace('.yaml', '')})" for cf in config_files])
    
    for i, config_file in enumerate(config_files):
        with tabs[i]:
            env_name = config_file.replace('config.', '').replace('.yaml', '')
            st.info(f"🎯 Environment: {env_name}")
            
            # Show README if present (simplified for now)
            st.info("📄 Configuration file details would be shown here")
    
    # Configuration selection
    selected_config = st.radio(
        "Choose configuration to deploy:",
        config_files,
        format_func=lambda x: f"{x} (Environment: {x.replace('config.', '').replace('.yaml', '')})",
    )
    
    if selected_config:
        state_manager.set_selected_config(selected_config)
        st.success(f"✅ Selected: {selected_config}")
        
        # Step 3 is always enabled as per requirements
        if st.button("➡️ Continue to Step 3", type="primary"):
            workflow_engine.advance_to_step(3)
            st.rerun()
    
    # Back button
    if st.button("⬅️ Back to Step 1"):
        workflow_engine.advance_to_step(1)
        st.rerun()


def render_step_3():
    """Step 3: Build and Deploy"""
    st.header("🔨 Step 3: Build and Deploy")
    
    selected_config = state_manager.get_selected_config()
    extracted_path = state_manager.get_extracted_path()
    env_vars = state_manager.get_env_vars()
    
    if not selected_config or not extracted_path:
        st.warning("Missing required information. Go back to previous steps.")
        return
    
    # Show selected configuration
    st.subheader("Selected Configuration")
    st.info(f"📋 **Configuration**: {selected_config}")
    st.info(f"📁 **Repository**: {extracted_path}")
    st.info(f"🔧 **Environment Variables**: {len(env_vars)} variables loaded")
    
    # Build and Deploy button
    if st.button("🔨🚀 Build and Deploy", type="primary"):
        with st.spinner("Building and deploying project..."):
            try:
                success, stdout, stderr = toolkit_service.build_and_deploy(extracted_path, env_vars)
                
                if success:
                    st.success("🎉 Build and deployment completed successfully!")
                    st.info("📦 Your package has been deployed to your CDF project.")
                    
                    # Show completion options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Start New Deployment", type="primary"):
                            workflow_engine.reset_workflow()
                            st.rerun()
                    with col2:
                        if st.button("📊 View Deployment Details"):
                            st.code(stdout, language="text")
                else:
                    st.error("❌ Build and deployment failed!")
                    if stderr:
                        st.code(stderr, language="text")
                        
            except Exception as e:
                error_handler.handle_error(e, "Build and deploy")
    
    # Back button
    if st.button("⬅️ Back to Step 2"):
        workflow_engine.advance_to_step(2)
        st.rerun()


def main():
    """Main application function"""
    st.title("🚀 GitHub Repo to CDF Deployer")
    st.markdown("Download files from public GitHub repositories and deploy them using the Cognite toolkit")
    
    # Initialize workflow
    if state_manager.get_step() == 0:
        state_manager.set_step(1)
    
    # Render step tabs
    render_step_tabs()
    
    # Render sidebar
    render_sidebar()
    
    # Render current step
    current_step = workflow_engine.get_current_step()
    
    if current_step == 1:
        render_step_1()
    elif current_step == 2:
        render_step_2()
    elif current_step == 3:
        render_step_3()
    else:
        st.error(f"Invalid step: {current_step}")


if __name__ == "__main__":
    main()
