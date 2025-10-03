import os
import tempfile
import streamlit as st

from . import env_loader
from . import github_service
from . import readme_finder
from . import toolkit_service
from . import state

def render_step_1():
    
    # Handle environment variables silently in the background
    env_option, env_vars = env_loader.render_env_ui()
    
    # Show previous download results if they exist
    download_success, download_repo, download_message = state.get_download_results()
    if download_success is not None:
        if download_success:
            st.success(f"✅ Repository downloaded successfully (previous): {download_repo}")
            st.info(download_message)
            
            # Show that we can proceed to Step 2
            extracted_path = state.get_extracted_path()
            config_files = state.get_config_files()
            if extracted_path and config_files:
                st.success(f"✅ Found {len(config_files)} configuration files")
                
                
                # Option to download a different repository
                if st.button("🔄 Download Different Repository", type="secondary"):
                    # Clear download results to show selection again
                    st.session_state['download_success'] = None
                    st.rerun()
                return
        else:
            st.error(f"❌ Previous download failed: {download_repo}")
            st.error(download_message)
    
    # If no previous download or user wants to download different repo
    repo_input = github_service.render_repo_inputs()
    if repo_input is None:
        return
    repo_owner, repo_name, selected_branch, access_type = repo_input

    # Get CLIENT from session state
    CLIENT = st.session_state.get('cdf_client')
    
    # Debug CLIENT status
    st.sidebar.write(f"🔍 ui_steps: CLIENT from session={bool(CLIENT)}")
    if CLIENT:
        st.sidebar.write(f"🔍 ui_steps: CLIENT type={type(CLIENT).__name__}")
    
    # Download repository (returns directory path, not ZIP path)
    repo_path = github_service.render_download_section(repo_owner, repo_name, selected_branch, access_type, CLIENT)
    if not repo_path:
        return

    # Repository downloaded successfully
    config_files = github_service.find_config_files(repo_path)
    if not config_files:
        st.warning("⚠️ No config.*.yaml files found in the repository.")
        state.set_download_results(False, f"{repo_owner}/{repo_name}", "No config files found")
        return

    # Store the repository path and config files
    state.set_extracted_path(repo_path)
    state.set_config_files(config_files)
    state.set_env_vars(env_vars)
    
    # Store successful download results
    state.set_download_results(True, f"{repo_owner}/{repo_name}", f"Found {len(config_files)} configuration files")
    
    st.success(f"✅ Repository downloaded and {len(config_files)} configuration files found")


def render_step_2():
    st.header("📋 Step 2: Select Configuration")
    extracted_path = state.get_extracted_path()
    config_files = state.get_config_files()
    if not extracted_path:
        st.warning("No repository path available. Go back to Step 1.")
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
    
    # If env_vars is empty, use the current environment (same as CDF client)
    if not env_vars:
        import os
        env_vars = {
            'CDF_PROJECT': os.getenv('CDF_PROJECT', ''),
            'CDF_CLUSTER': os.getenv('CDF_CLUSTER', ''),
            'CDF_URL': os.getenv('CDF_URL', ''),
            'IDP_CLIENT_ID': os.getenv('IDP_CLIENT_ID', ''),
            'IDP_CLIENT_SECRET': os.getenv('IDP_CLIENT_SECRET', ''),
            'IDP_TOKEN_URL': os.getenv('IDP_TOKEN_URL', ''),
            'IDP_SCOPES': os.getenv('IDP_SCOPES', ''),
            'IDP_TENANT_ID': os.getenv('IDP_TENANT_ID', ''),
        }
        # Remove empty values
        env_vars = {k: v for k, v in env_vars.items() if v}
    
    # Debug: Show what env_vars will be used for deployment
    if st.session_state.get('debug_mode', False):
        st.info(f"🔍 **Debug**: Using {len(env_vars)} environment variables for deployment")
        if env_vars:
            oauth_vars = ['CDF_PROJECT', 'CDF_CLUSTER', 'IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TOKEN_URL']
            oauth_status = {var: bool(env_vars.get(var)) for var in oauth_vars}
            st.info(f"🔐 **OAuth2 Status for Deployment**: {oauth_status}")
            st.info(f"📋 **Project**: {env_vars.get('CDF_PROJECT', 'NOT SET')}")
            st.info(f"🌐 **Cluster**: {env_vars.get('CDF_CLUSTER', 'NOT SET')}")
        else:
            st.warning("⚠️ **Debug**: Still no environment variables for deployment!")
    
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
    
    # Follow proper deployment workflow: dry-run → deploy
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Dry Run (Preview Changes)", type="secondary"):
            st.session_state['show_dry_run'] = True
            st.rerun()
    
    with col2:
        # Deploy button is shown after dry-run section
        st.write("")  # Placeholder for layout
                
    # Handle dry-run
    if st.session_state.get('show_dry_run', False):
        st.subheader("🔍 Deployment Preview (Dry Run)")
        
        # Get SaaS client
        client = st.session_state.get('cdf_client')
        if not client:
            st.error("❌ No CDF client available. Please refresh the app.")
            return
            
        with st.spinner("Running dry-run to preview changes..."):
            try:
                # Get environment and client info
                selected_env = state.get_selected_env() or "weather"
                project = client.config.project
                cluster = client.config.base_url

                st.info(f"🔗 Connected to project '{project}' on {cluster}")
                st.info(f"📁 Analyzing: {extracted_path}")
                st.info(f"📋 Environment: {selected_env}")

                # Capture dry-run output in a list for display
                dry_run_output = []
                def capture_logger(msg):
                    dry_run_output.append(str(msg))
                    st.write(msg)  # Also show in real-time
                
                # Call real dry-run comparison using toolkit library
                from core.toolkit_operations import dry_run_project as core_dry_run
                ok, out, err = core_dry_run(client, extracted_path, env_vars, env_name=selected_env, verbose=True, logger=capture_logger)
                
                if not ok:
                    st.error(f"❌ Dry-run failed: {err}")
                    if dry_run_output:
                        st.subheader("📄 Dry-run Output")
                        st.code("\n".join(dry_run_output), language="text")
                    return
                else:
                    st.success("✅ Dry-run completed - real comparison with live CDF system")
                    if dry_run_output:
                        st.subheader("📊 Dry-run Comparison Results")
                        st.code("\n".join(dry_run_output), language="text")
                
            except Exception as e:
                st.error(f"❌ Dry-run failed: {e}")
                return
            
        # Show deploy button after successful dry-run
        if st.button("🚀 Deploy to CDF", type="primary", key="deploy_button_main"):
            st.session_state['show_deploy'] = True
            st.rerun()
        
        # Handle actual deployment if deploy button was clicked
        if st.session_state.get('show_deploy', False):
            st.subheader("🚀 Deploying to CDF")
            selected_env = state.get_selected_env() or "weather"
            
            # Get SaaS client
            client = st.session_state.get('cdf_client')
            if not client:
                st.error("❌ No CDF client available. Please refresh the app.")
                return
                
            with st.spinner("Deploying to CDF using real toolkit library..."):
                try:
                    # Get client info
                    project = client.config.project
                    cluster = client.config.base_url
                    
                    st.info(f"🔗 Connected to project '{project}' on {cluster}")
                    st.info(f"📁 Deploying: {extracted_path}")
                    st.info(f"📋 Environment: {selected_env}")
                    
                    # Capture deployment output in a list for display
                    deploy_output = []
                    def capture_deploy_logger(msg):
                        deploy_output.append(str(msg))
                        st.write(msg)  # Also show in real-time
                    
                    # Call real deployment using toolkit library
                    from core.toolkit_operations import deploy_project as core_deploy
                    ok, out, err = core_deploy(client, extracted_path, env_vars, env_name=selected_env, verbose=True, logger=capture_deploy_logger)
                    
                    if ok:
                        st.success("✅ Deployment completed successfully!")
                        if deploy_output:
                            st.subheader("📊 Deployment Results")
                            st.code("\n".join(deploy_output), language="text")
                        st.info("✅ Deploy complete! Click Step 5 tab above to verify deployment.")
                    else:
                        st.error(f"❌ Deployment failed: {err}")
                        if deploy_output:
                            st.subheader("📄 Deployment Output")
                            st.code("\n".join(deploy_output), language="text")
                    
                    # Store results
                    state.set_deploy_results(ok, out, err)
                    
                except Exception as e:
                    st.error(f"❌ Deployment failed: {e}")
                    state.set_deploy_results(False, "", str(e))

def render_step_5():
    st.subheader("✅ Step 5: Deployment Complete")
    st.success("🎉 Deployment completed successfully!")
    st.info("📦 Your package has been deployed to your CDF project.")
    
    if st.button("🔄 Start New Deployment", type="primary"):
        state.reset()
        st.rerun()


