import os
import tempfile
import streamlit as st

from . import env_loader
from . import github_service
from . import readme_finder
from . import toolkit_service
from . import state

def render_step_1():
    st.header("⚙️ Environment Configuration")
    # Delegate environment handling to env_loader
    env_option, env_vars = env_loader.render_env_ui()
    repo_input = github_service.render_repo_inputs()
    if repo_input is None:
        return
    repo_owner, repo_name, selected_branch, access_type = repo_input

    # Download repository (returns directory path, not ZIP path)
    repo_path = github_service.render_download_section(repo_owner, repo_name, selected_branch, access_type)
    if not repo_path:
        return

    # No extraction needed - repo_path is already the extracted directory
    st.success("✅ Repository downloaded successfully!")
    
    config_files = github_service.find_config_files(repo_path)
    if not config_files:
        st.warning("⚠️ No config.*.yaml files found in the repository.")
        return

    # Store the repository path and config files
    state.set_extracted_path(repo_path)
    state.set_config_files(config_files)
    state.set_env_vars(env_vars)
    
    # Show continue button to proceed to Step 2 (Configuration Selection)
    st.success(f"✅ Found {len(config_files)} configuration files")
    if st.button("➡️ Continue to Step 2", type="primary"):
        state.set_workflow_step(2)
        st.rerun()

def render_step_2():
    st.header("📋 Step 2: Select Configuration")
    extracted_path = state.get_extracted_path()
    config_files = state.get_config_files()
    if not extracted_path or not config_files:
        st.warning("Nothing to select yet. Go back to Step 1.")
        return
    
    st.info(f"Found {len(config_files)} configuration files:")

    tabs = st.tabs([f"{cf} ({cf.replace('config.', '').replace('.yaml', '')})" for cf in config_files])
    for i, config_file in enumerate(config_files):
        with tabs[i]:
            env_name = config_file.replace('config.', '').replace('.yaml', '')
            st.info(f"🎯 Environment: {env_name}")
            readme_path = readme_finder.find_readme_for_config(extracted_path, config_file)
            if readme_path:
                with st.expander("README", expanded=True):
                    st.markdown(readme_finder.read_readme_content(readme_path))

    selected_config = st.radio(
        "Choose configuration to deploy:",
        config_files,
        format_func=lambda x: f"{x} (Environment: {x.replace('config.', '').replace('.yaml', '')})",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Download"):
            state.set_workflow_step(1)
            st.rerun()
    with col2:
        if st.button("➡️ Continue to Build", type="primary"):
            state.set_selected_config(selected_config)
            state.set_selected_env(selected_config.replace('config.', '').replace('.yaml', ''))
            state.set_workflow_step(3)
            st.rerun()

def render_step_3():
    st.subheader("🔨 Step 3: Build Package")
    extracted_path = state.get_extracted_path()
    env_vars = state.get_env_vars() or {}
    
    if st.button("🔨 Build Package", type="primary"):
        with st.spinner("Building package..."):
            ok, out, err = toolkit_service.run_cognite_toolkit_build(extracted_path, env_vars)
            if ok:
                st.success("✅ Build completed successfully")
                state.set_workflow_step(4)
                st.rerun()
            else:
                st.error("❌ Build failed")
                if err:
                    st.code(err, language="text")

def render_step_4():
    st.subheader("🚀 Step 4: Deploy Package")
    extracted_path = state.get_extracted_path()
    env_vars = state.get_env_vars() or {}
    
    if st.button("🚀 Deploy to CDF", type="primary"):
        with st.spinner("Deploying to CDF..."):
            ok, out, err = toolkit_service.run_cognite_toolkit_deploy(extracted_path, env_vars)
            if ok:
                st.success("✅ Deployment completed successfully")
                state.set_workflow_step(5)
                st.rerun()
            else:
                st.error("❌ Deployment failed")
                if err:
                    st.code(err, language="text")

def render_step_5():
    st.subheader("✅ Step 5: Deployment Complete")
    st.success("🎉 Deployment completed successfully!")
    st.info("📦 Your package has been deployed to your CDF project.")
    
    if st.button("🔄 Start New Deployment", type="primary"):
        state.reset()
        st.rerun()


