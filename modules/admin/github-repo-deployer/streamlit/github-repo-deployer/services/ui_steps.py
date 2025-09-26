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
    st.caption("[Step 1] env loaded, awaiting repo inputs…")
    repo_input = github_service.render_repo_inputs()
    if repo_input is None:
        st.caption("[Step 1] repo input incomplete")
        return
    repo_owner, repo_name, selected_branch, access_type = repo_input

    # Download repository (returns directory path, not ZIP path)
    st.caption("[Step 1] starting download section…")
    repo_path = github_service.render_download_section(repo_owner, repo_name, selected_branch, access_type)
    if not repo_path:
        st.caption("[Step 1] no repo path yet")
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
    st.caption(f"[Step 1] stored path and {len(config_files)} config(s)")
    st.success(f"✅ Found {len(config_files)} configuration files")

    if st.button("➡️ Continue to Step 2", type="primary"):
        st.caption("[Step 1] advancing to Step 2")
        state.set_workflow_step(2)
        st.rerun()

def render_step_2():
    st.header("📋 Step 2: Select Configuration")
    extracted_path = state.get_extracted_path()
    config_files = state.get_config_files()
    if not extracted_path:
        st.warning("No repository path available. Go back to Step 1.")
        if st.button("⬅️ Back to Download"):
            state.set_workflow_step(1)
            st.rerun()
        return
    
    # Always show basic debug info so the user sees progress immediately
    st.caption(f"[Step 2] Repo path: {extracted_path}")
    st.caption(f"[Step 2] Configs in state: {len(config_files)}")
    
    # If config list is empty, offer a rescan and a back button
    if not config_files:
        st.warning("No configuration files found yet.")
        col_a, col_b = st.columns([1,1])
        with col_a:
            if st.button("🔄 Rescan for config.*.yaml"):
                refreshed = github_service.find_config_files(extracted_path)
                if refreshed:
                    state.set_config_files(refreshed)
                    st.success(f"Found {len(refreshed)} configuration files")
                    st.rerun()
                else:
                    st.info("Still no configuration files detected.")
        with col_b:
            if st.button("⬅️ Back to Step 1"):
                state.set_workflow_step(1)
                st.rerun()
        return
    
    config_files = sorted(
        config_files,
        key=lambda p: (0 if os.path.basename(p) == 'config.weather.yaml' else 1, os.path.basename(p))
    )
    st.info(f"Found {len(config_files)} configuration files:")

    config_options = []
    for cf in config_files:
        label = os.path.basename(cf)
        env_name = label.replace('config.', '').replace('.yaml', '')
        config_options.append((label, cf, env_name))

    if not config_options:
        st.stop()

    default_index = 0
    for idx, (label, *_rest) in enumerate(config_options):
        if label == 'config.weather.yaml':
            default_index = idx
            break

    selected_idx = st.radio(
        "Choose configuration to deploy:",
        range(len(config_options)),
        index=default_index,
        format_func=lambda i: config_options[i][0]
    )

    selected_label, selected_path, env_name = config_options[selected_idx]

    state.set_selected_config(selected_path)
    state.set_selected_env(env_name)

    st.success(f"✅ Selected: {selected_label} (Environment: {env_name})")
    st.caption(f"Full path: {selected_path}")

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Download"):
            state.set_workflow_step(1)
            st.rerun()
    with col2:
        if st.button("➡️ Continue to Build", type="primary"):
            state.set_workflow_step(3)
            st.rerun()

def render_step_3():
    st.subheader("🔨 Step 3: Build Package")
    extracted_path = state.get_extracted_path()
    env_vars = state.get_env_vars() or {}
    
    # Show previous build results if they exist
    build_success, build_output, build_error, debug_stdout, debug_stderr = state.get_build_results()
    if build_success is not None:
        if build_success:
            st.success("✅ Build completed successfully (previous run)")
            
            # Show debug output if available and debug mode is on
            if st.session_state.get('debug_mode', False):
                if debug_stdout:
                    st.subheader("📄 Previous Build Process Output")
                    st.code(debug_stdout, language="text")
                if debug_stderr:
                    st.subheader("📄 Previous Build Process Errors")
                    st.code(debug_stderr, language="text")
                if build_output:
                    st.subheader("📄 Previous Build Output")
                    st.code(build_output, language="text")
            
            st.info("🚀 Build complete! Click Step 4 tab above to proceed to deployment.")
        else:
            st.error("❌ Previous build failed")
            
            # Show debug output if available and debug mode is on
            if st.session_state.get('debug_mode', False):
                if debug_stdout:
                    st.subheader("📄 Previous Build Process Output")
                    st.code(debug_stdout, language="text")
                if debug_stderr:
                    st.subheader("📄 Previous Build Process Errors")
                    st.code(debug_stderr, language="text")
            
            if build_error:
                st.subheader("❌ Previous Build Error")
                st.code(build_error, language="text")
            if build_output:
                st.subheader("📄 Previous Build Output")
                st.code(build_output, language="text")
    
    if st.button("🔨 Build Package", type="primary"):
        selected_env = state.get_selected_env() or "weather"
        st.info(f"🔨 Building with environment: {selected_env}")
        
        # Initialize output buffers
        import io
        from contextlib import redirect_stdout, redirect_stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Always show verbose output in debug mode
        if st.session_state.get('debug_mode', False):
            st.subheader("🔍 Build Process (Debug Mode)")
            
            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    ok, out, err = toolkit_service.build_project(extracted_path, env_vars, env_name=selected_env)
                
                # Show captured output
                captured_stdout = stdout_buffer.getvalue()
                captured_stderr = stderr_buffer.getvalue()
                
                if captured_stdout:
                    st.subheader("📄 Build Process Output")
                    st.code(captured_stdout, language="text")
                if captured_stderr:
                    st.subheader("📄 Build Process Errors")
                    st.code(captured_stderr, language="text")
                
            except Exception as e:
                st.error(f"❌ Build process failed: {e}")
                ok, out, err = False, "", str(e)
        else:
            # Non-debug mode
            with st.spinner("Building package..."):
                ok, out, err = toolkit_service.build_project(extracted_path, env_vars, env_name=selected_env)
        
        # Store and show results (including debug output)
        debug_stdout_val = stdout_buffer.getvalue()
        debug_stderr_val = stderr_buffer.getvalue()
        state.set_build_results(ok, out, err, debug_stdout_val, debug_stderr_val)
        
        if ok:
            st.success("✅ Build completed successfully")
            if out and st.session_state.get('debug_mode', False):
                st.subheader("📄 Build Output")
                st.code(out, language="text")
            
            st.info("🚀 Build complete! Click Step 4 tab above to proceed to deployment.")
        else:
            st.error("❌ Build failed - fix errors and try again")
            if err:
                st.subheader("❌ Build Error Details")
                st.code(err, language="text")
            if out:
                st.subheader("📄 Build Output")
                st.code(out, language="text")

def render_step_4():
    st.subheader("🚀 Step 4: Deploy Package")
    extracted_path = state.get_extracted_path()
    env_vars = state.get_env_vars() or {}
    
    # Show previous deploy results if they exist
    deploy_success, deploy_output, deploy_error = state.get_deploy_results()
    if deploy_success is not None:
        if deploy_success:
            st.success("✅ Deployment completed successfully (previous run)")
            if deploy_output and st.session_state.get('debug_mode', False):
                st.subheader("📄 Previous Deploy Output")
                st.code(deploy_output, language="text")
            st.info("✅ Deploy complete! Click Step 5 tab above to verify deployment.")
        else:
            st.error("❌ Previous deployment failed")
            if deploy_error:
                st.subheader("❌ Previous Deploy Error")
                st.code(deploy_error, language="text")
            if deploy_output:
                st.subheader("📄 Previous Deploy Output")
                st.code(deploy_output, language="text")
    
    if st.button("🚀 Deploy to CDF", type="primary"):
        selected_env = state.get_selected_env() or "weather"
        st.info(f"🚀 Deploying with environment: {selected_env}")
        
        # Always show verbose output in debug mode
        if st.session_state.get('debug_mode', False):
            st.subheader("🔍 Deploy Process (Debug Mode)")
            
            # Capture verbose logging
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            # Create string buffers to capture output
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            try:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    ok, out, err = toolkit_service.deploy_project(extracted_path, env_vars, env_name=selected_env)
                
                # Show captured output
                captured_stdout = stdout_buffer.getvalue()
                captured_stderr = stderr_buffer.getvalue()
                
                if captured_stdout:
                    st.subheader("📄 Deploy Process Output")
                    st.code(captured_stdout, language="text")
                if captured_stderr:
                    st.subheader("📄 Deploy Process Errors")
                    st.code(captured_stderr, language="text")
                
            except Exception as e:
                st.error(f"❌ Deploy process failed: {e}")
                ok, out, err = False, "", str(e)
        else:
            # Non-debug mode
            with st.spinner("Deploying to CDF..."):
                ok, out, err = toolkit_service.deploy_project(extracted_path, env_vars, env_name=selected_env)
        
        # Store and show results
        state.set_deploy_results(ok, out, err)
        
        if ok:
            st.success("✅ Deployment completed successfully")
            if out and st.session_state.get('debug_mode', False):
                st.subheader("📄 Deploy Output")
                st.code(out, language="text")
            
            st.info("✅ Deploy complete! Click Step 5 tab above to verify deployment.")
        else:
            st.error("❌ Deployment failed - fix errors and try again")
            if err:
                st.subheader("❌ Deploy Error Details")
                st.code(err, language="text")
            if out:
                st.subheader("📄 Deploy Output")
                st.code(out, language="text")

def render_step_5():
    st.subheader("✅ Step 5: Deployment Complete")
    st.success("🎉 Deployment completed successfully!")
    st.info("📦 Your package has been deployed to your CDF project.")
    
    if st.button("🔄 Start New Deployment", type="primary"):
        state.reset()
        st.rerun()


