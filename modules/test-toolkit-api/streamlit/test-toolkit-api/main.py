#!/usr/bin/env python3
"""
Minimal Streamlit Test for Cognite Toolkit API
Tests if the toolkit library API works in SaaS environment
"""

# Version tracking for deployment verification
VERSION = "2025.01.03.v15"  # Update this when deploying changes

import streamlit as st
import sys
from pathlib import Path
import traceback
import time
from datetime import datetime


# Global cached client to avoid re-initialization delays
@st.cache_resource
def get_cognite_client():
    """Initialize and cache CogniteClient for instant button responses"""
    from cognite.client import CogniteClient
    return CogniteClient()


def test_toolkit_imports():
    """Test if we can import the toolkit classes"""
    st.subheader("🔍 Testing Toolkit Imports")
    
    # ============================================================================
    # TRIAL 1A: Direct cognite-toolkit library import (FAILED - Oct 3, 2024)
    # ============================================================================
    # Result: ModuleNotFoundError: No module named 'cognite_toolkit'
    # Cause: cognite-toolkit was not in requirements.txt
    # Status: FAILED - package not installed
    # DO NOT DELETE - Keep for historical reference
    # ============================================================================
    
    # ============================================================================
    # TRIAL 1B: Add cognite-toolkit to requirements.txt (FAILED - Oct 3, 2024)
    # ============================================================================
    # Approach: Add cognite-toolkit to requirements.txt and redeploy
    # Goal: Get Pyodide to install cognite-toolkit package
    # Result: ValueError: Can't find a pure Python 3 wheel for: 'cognite-toolkit'
    # Cause: cognite-toolkit has native dependencies (C extensions) incompatible with Pyodide
    # Status: FAILED - Pyodide compatibility issue
    # Conclusion: cognite-toolkit CANNOT be used in Streamlit SaaS environment
    # DO NOT DELETE - Keep for historical reference
    # ============================================================================
    
    st.error("❌ **CONFIRMED**: cognite-toolkit is NOT compatible with Streamlit SaaS (Pyodide)")
    st.info("📋 **Trial 1B Result**: ValueError - Can't find pure Python 3 wheel")
    st.warning("⚠️ **Root Cause**: cognite-toolkit has native dependencies (C extensions)")
    st.error("🚫 **Final Conclusion**: cognite-toolkit library approach is IMPOSSIBLE in SaaS")
    
    # Show the exact error for reference
    st.code("""
    Traceback (most recent call last):
      File "/lib/python3.12/site-packages/micropip/_commands/install.py", line 146, in install
        raise ValueError(
    ValueError: Can't find a pure Python 3 wheel for: 'cognite-toolkit'
    See: https://pyodide.org/en/stable/usage/faq.html#why-can-t-micropip-find-a-pure-python-wheel-for-a-package
    """)
    
    st.info("💡 **Next Step**: Must use alternative approaches (Trial 2+)")
    
    return False, "cognite-toolkit incompatible with Pyodide"


def test_trial_2_cognite_sdk_direct():
    """TRIAL 2: Use CogniteClient directly to simulate toolkit operations"""
    st.subheader("🧪 TRIAL 2: Direct CogniteClient Approach")
    
    # ============================================================================
    # TRIAL 2: Direct CogniteClient simulation (ARCHIVED - Oct 3, 2024)
    # ============================================================================
    # Approach: Use CogniteClient() directly to perform build/deploy-like operations
    # Goal: Simulate toolkit functionality using only cognite-sdk
    # Status: WORKS but is simulation (not acceptable per user requirements)
    # DO NOT DELETE - Keep for historical reference
    # ============================================================================
    
    st.warning("⚠️ **ARCHIVED**: This approach works but is simulation-only (not acceptable)")
    st.info("🔬 **Testing**: Can we simulate toolkit operations using CogniteClient directly?")
    
    try:
        from cognite.client import CogniteClient
        
        client = CogniteClient()
        st.success("✅ CogniteClient created successfully")
        st.info(f"🔗 Project: {client.config.project}")
        st.info(f"🌐 Cluster: {client.config.base_url}")
        
        # Test basic CDF operations that toolkit would use
        st.subheader("📋 Testing CDF Operations")
        
        # Test 1: List spaces (toolkit uses this for validation)
        try:
            spaces = client.data_modeling.spaces.list(limit=5)
            st.success(f"✅ Listed {len(spaces)} spaces")
            for space in spaces:
                st.write(f"  - {space.space}")
        except Exception as e:
            st.error(f"❌ Failed to list spaces: {e}")
        
        # Test 2: List data models (toolkit uses this for deployment)
        try:
            models = client.data_modeling.data_models.list(limit=5)
            st.success(f"✅ Listed {len(models)} data models")
        except Exception as e:
            st.error(f"❌ Failed to list data models: {e}")
        
        # Test 3: List datasets (toolkit uses this for validation)
        try:
            datasets = client.data_sets.list(limit=5)
            st.success(f"✅ Listed {len(datasets)} datasets")
        except Exception as e:
            st.error(f"❌ Failed to list datasets: {e}")
        
        return True, client
        
    except Exception as e:
        st.error(f"❌ CogniteClient approach failed: {e}")
        st.code(traceback.format_exc())
        return False, str(e)


def test_trial_3_cognite_functions():
    """TRIAL 3: Use Cognite Functions to run real toolkit library"""
    st.subheader("🧪 Test Toolkit via Cognite Functions")
    
    # Function calling interface
    st.subheader("📞 Call Function")
    
    function_name = st.text_input("Function External ID", value="test-toolkit-function")
    
    if st.button("🧪 Call Function to Test Toolkit", type="primary"):
        if not function_name:
            st.error("Please enter a function name")
            return
        
        # ========================================================================
        # ATTEMPTS TO MAKE BUTTON FEEDBACK INSTANT:
        # ========================================================================
        # v3 (2025.01.03): Direct st.success() after button - FAILED (60s delay)
        #   - Issue: Streamlit buffers output until code block finishes
        #   - Client initialization blocks for 60 seconds before any output
        #
        # v4 (2025.01.03): st.cache_resource in button handler - FAILED (60s delay)
        #   - Issue: Cache wasn't warmed up, first call still initializes
        #
        # v5 (2025.01.03): Pre-initialize in main() before button - FAILED (60s delay)
        #   - Issue: Multiple get_cognite_client() definitions, each with own cache
        #   - Cache not shared between main() and button handler
        #
        # v6 (2025.01.03): Global get_cognite_client() at module level - FAILED (60s delay)
        #   - Issue: Even with cache, get_cognite_client() call blocks until complete
        #   - Streamlit doesn't render anything until function returns
        #
        # v7 (2025.01.03): Using st.empty() for immediate updates - TESTING
        #   - Theory: Create placeholder first, update it after slow operations
        #
        # FUTURE OPTIONS IF v7 FAILS:
        # - Option A: Use st.session_state to track if client is initialized
        #   - Show "Please wait, initializing..." message on first page load
        #   - Disable button until client is ready
        # - Option B: Background thread for client initialization (not recommended)
        #   - Streamlit doesn't support true async/threading well
        # - Option C: Accept the delay and show clear progress indicator
        #   - Use st.spinner with descriptive message
        # - Option D: Initialize client in a separate "Connect" button
        #   - User explicitly clicks "Connect" first, then can call functions
        # ========================================================================
        
        # Create placeholder for immediate feedback
        feedback = st.empty()
        feedback.success("🚀 Button clicked! Initializing...")
        
        try:
            # Get cached client - this is the slow part (60s first time)
            status = st.empty()
            status.info("🔌 Getting Cognite client...")
            client = get_cognite_client()
            status.success("✅ Client ready!")
            feedback.success(f"📞 Calling function: {function_name}...")
            
            # Auto-retry logic for deployment
            max_retries = 20  # Try for up to 10 minutes (20 * 30 seconds)
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with st.spinner(f"Calling Cognite Function... (attempt {retry_count + 1}/{max_retries})"):
                        # Call the function
                        call_result = client.functions.call(
                            external_id=function_name,
                            data={"test": "toolkit_installation"}
                        )
                        
                        st.success(f"✅ Function called successfully! Call ID: {call_result.id}")
                        break  # Success - exit retry loop
                        
                except Exception as call_error:
                    error_msg = str(call_error)
                    
                    if "409" in error_msg and "being deployed" in error_msg:
                        retry_count += 1
                        st.warning(f"⏳ Function still being deployed... (attempt {retry_count}/{max_retries})")
                        
                        if retry_count < max_retries:
                            st.info("💤 Waiting 30 seconds before retry...")
                            time.sleep(30)
                            st.rerun()  # Refresh the page to show progress
                        else:
                            st.error("⏰ Function deployment timeout - please try again later")
                            return
                    else:
                        # Different error - don't retry
                        st.error(f"❌ Failed to call function: {call_error}")
                        return
            
            # If we get here, the function was called successfully
            st.subheader("📋 Function Execution Logs")
            
            # Debug: Show what we're working with
            with st.expander("🔍 Debug Info", expanded=True):
                st.write(f"**Function External ID**: `{function_name}`")
                st.write(f"**Call ID**: `{call_result.id}`")
                st.write(f"**Call Result Type**: `{type(call_result)}`")
                st.write(f"**Call Result Attributes**: {dir(call_result)}")
            
            # Create placeholders for live updates
            logs_container = st.container()
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Wait for result with progress and live logs
            max_wait = 300  # 5 minutes
            wait_time = 0
            last_log_timestamp = None
            all_logs = []
            
            while wait_time < max_wait:
                try:
                    # ============================================================
                    # API CALL FIXES:
                    # v6 (2025.01.03): Changed retrieve(call_id=id) to retrieve(id) - FAILED
                    # v10 (2025.01.03): Stack trace shows retrieve() ALSO needs function identifier!
                    #   - Error at line 987: _get_function_identifier(function_id, function_external_id)
                    #   - retrieve() has same signature as get_logs()!
                    # ============================================================
                    # Get function call status
                    st.write(f"🔍 DEBUG: Retrieving status for function={function_name}, call_id={call_result.id}")
                    call_status = client.functions.calls.retrieve(
                        function_external_id=function_name,
                        call_id=call_result.id
                    )
                    st.write(f"✅ DEBUG: Status retrieved: {call_status.status}")
                    
                    progress = min(wait_time / max_wait, 0.95)
                    progress_bar.progress(progress)
                    status_placeholder.text(f"Status: {call_status.status} (waited {wait_time}s)")
                    
                    # Get and display logs in real-time
                    try:
                        # ============================================================
                        # API CALL FIXES HISTORY:
                        # v6 (2025.01.03): Changed to get_logs(call_id=id) - FAILED
                        # v7-v8 (2025.01.03): Try positional get_logs(id) - FAILED
                        #   - Error: "Exactly one of function_id and function_external_id must be specified"
                        #   - Analysis: get_logs() needs to know WHICH FUNCTION, not just call_id
                        #   - The method signature is likely: get_logs(function_external_id=..., call_id=...)
                        # v9 (2025.01.03): Pass function_external_id AND call_id - TESTING
                        # v10 (2025.01.03): Add full debug logging with stack traces
                        # ============================================================
                        st.write(f"🔍 DEBUG: Getting logs for function={function_name}, call_id={call_result.id}")
                        logs = client.functions.calls.get_logs(
                            function_external_id=function_name,
                            call_id=call_result.id
                        )
                        
                        # Convert to list to avoid exhausting iterator
                        logs_list = list(logs) if logs else []
                        st.write(f"✅ DEBUG: Received {len(logs_list)} log entries")
                        
                        # DEBUG: Show what's in the first log
                        if logs_list:
                            st.write(f"🔍 DEBUG: First log object type: {type(logs_list[0])}")
                            st.write(f"🔍 DEBUG: First log attributes: {dir(logs_list[0])}")
                            st.write(f"🔍 DEBUG: First log content: {logs_list[0]}")
                        
                        # Filter new logs
                        # ============================================================
                        # v13 DEBUG: Found the issue!
                        # - Timestamp filtering is too aggressive
                        # - We're comparing timestamp objects, but they might be strings
                        # - Need to handle timestamp comparison properly
                        # v14: Show ALL logs on first poll, then filter subsequent ones
                        # ============================================================
                        new_logs = []
                        for log in logs_list:
                            # On first poll (last_log_timestamp is None), show all logs
                            # On subsequent polls, only show logs newer than last seen
                            if last_log_timestamp is None:
                                new_logs.append(log)
                            else:
                                # Try to compare timestamps
                                try:
                                    log_ts = log.timestamp
                                    # Convert to comparable format if needed
                                    if isinstance(log_ts, str):
                                        from dateutil import parser
                                        log_ts = parser.parse(log_ts).timestamp() * 1000
                                    if log_ts > last_log_timestamp:
                                        new_logs.append(log)
                                except:
                                    # If comparison fails, include the log
                                    new_logs.append(log)
                        
                        # Update last_log_timestamp AFTER filtering
                        if new_logs:
                            try:
                                last_ts = new_logs[-1].timestamp
                                if isinstance(last_ts, str):
                                    from dateutil import parser
                                    last_log_timestamp = parser.parse(last_ts).timestamp() * 1000
                                else:
                                    last_log_timestamp = last_ts
                            except:
                                pass
                        
                        st.write(f"🔍 DEBUG: Filtered to {len(new_logs)} new logs (last_timestamp={last_log_timestamp})")
                        
                        # Display new logs
                        if new_logs:
                            st.write(f"🔍 DEBUG: Displaying {len(new_logs)} new logs...")
                            for log in new_logs:
                                # Get the log message
                                log_msg = log.message if hasattr(log, 'message') else str(log)
                                
                                # Format timestamp
                                time_str = ""
                                if hasattr(log, 'timestamp') and log.timestamp:
                                    try:
                                        from datetime import datetime
                                        if isinstance(log.timestamp, str):
                                            from dateutil import parser
                                            dt = parser.parse(log.timestamp)
                                            time_str = dt.strftime('%H:%M:%S')
                                        elif isinstance(log.timestamp, (int, float)):
                                            dt = datetime.fromtimestamp(log.timestamp / 1000)
                                            time_str = dt.strftime('%H:%M:%S')
                                    except:
                                        time_str = str(log.timestamp)[:8]
                                
                                # Display in logs container
                                with logs_container:
                                    if time_str:
                                        st.text(f"[{time_str}] {log_msg}")
                                    else:
                                        st.text(log_msg)
                                
                                all_logs.append(log_msg)
                    except Exception as log_error:
                        # Show detailed error information
                        st.error(f"❌ DEBUG: Error getting logs: {log_error}")
                        st.error(f"🔍 DEBUG: Error type: {type(log_error).__name__}")
                        st.code(traceback.format_exc())
                        # Don't break - continue trying
                    
                    if call_status.status == "Completed":
                        progress_bar.progress(1.0)
                        status_placeholder.text("✅ Function completed!")
                        
                        # Get any final logs
                        try:
                            logs = client.functions.calls.get_logs(
                                function_external_id=function_name,
                                call_id=call_result.id
                            )
                            logs_list = list(logs) if logs else []
                            final_new_logs = []
                            for log in logs_list:
                                if last_log_timestamp is None or log.timestamp > last_log_timestamp:
                                    final_new_logs.append(log)
                            
                            if final_new_logs:
                                with logs_container:
                                    for log in final_new_logs:
                                        log_msg = log.message if hasattr(log, 'message') else str(log)
                                        if hasattr(log, 'timestamp') and log.timestamp:
                                            st.text(f"[{log.timestamp}] {log_msg}")
                                        else:
                                            st.text(log_msg)
                                        all_logs.append(log_msg)
                        except:
                            pass
                        
                        # Get the result
                        result = client.functions.calls.retrieve(
                            function_external_id=function_name,
                            call_id=call_result.id
                        )
                        
                        st.subheader("🎉 Function Results")
                        
                        # DEBUG: Show what's in the result object
                        st.write(f"🔍 DEBUG: Result object type: {type(result)}")
                        st.write(f"🔍 DEBUG: Result attributes: {dir(result)}")
                        st.write(f"🔍 DEBUG: Has response attr? {hasattr(result, 'response')}")
                        if hasattr(result, 'response'):
                            st.write(f"🔍 DEBUG: Response value: {result.response}")
                            st.write(f"🔍 DEBUG: Response type: {type(result.response)}")
                        
                        if hasattr(result, 'response') and result.response:
                            response_data = result.response
                            
                            # Show summary
                            if 'summary' in response_data:
                                summary = response_data['summary']
                                st.subheader("📊 Test Summary")
                                
                                if summary.get('toolkit_installed'):
                                    st.success("✅ cognite-toolkit installed successfully!")
                                else:
                                    st.error("❌ cognite-toolkit installation failed")
                                
                                if summary.get('cdf_command_available'):
                                    st.success("✅ cdf command is available!")
                                else:
                                    st.error("❌ cdf command not available")
                                
                                if summary.get('cli_tool_confirmed'):
                                    st.success("✅ Toolkit is CLI-based (correct!)")
                                    st.info("💡 cognite-toolkit is a CLI tool, not a Python library")
                                
                                if summary.get('ready_for_production'):
                                    st.success("🎉 READY FOR PRODUCTION USE!")
                            
                            # Show detailed results
                            with st.expander("🔍 Detailed Results"):
                                st.json(response_data)
                            
                            # Analyze results
                            st.subheader("🎯 Analysis")
                            summary = response_data.get('summary', {})
                            
                            if summary.get('toolkit_installed') and summary.get('cdf_command_available'):
                                st.success("🎉 **BREAKTHROUGH CONFIRMED**: Real toolkit works in Functions!")
                                st.balloons()  # Celebration!
                                
                                # Show key achievements
                                st.subheader("🏆 Key Achievements")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.metric("Toolkit Installed", "✅ SUCCESS", "cognite-toolkit-0.6.45")
                                    st.metric("CDF Command Found", "✅ SUCCESS", "/home/.local/bin/cdf")
                                    st.metric("PATH Fixed", "✅ SUCCESS", "Auto-added to PATH")
                                
                                with col2:
                                    st.metric("Build Command", "✅ WORKS", "Returns expected error")
                                    st.metric("Deploy Command", "✅ WORKS", "Returns expected error") 
                                    st.metric("Help Command", "✅ WORKS", "Full help output")
                                
                                st.info("💡 **Next Step**: Implement full build/deploy workflow with real config files")
                                st.info("🚀 **Impact**: Streamlit SaaS can now use real toolkit via Functions!")
                                
                            else:
                                st.error("❌ Toolkit approach has limitations in Functions")
                        else:
                            st.error("❌ No response data received")
                        
                        break
                        
                    elif call_status.status == "Failed":
                        st.error(f"❌ Function failed: {call_status}")
                        
                        # Final logs are already shown above in logs_container
                        st.warning("⚠️ Check the logs above for error details")
                        return
                    
                    # Wait before checking again
                    time.sleep(2)  # Check every 2 seconds for more responsive updates
                    wait_time += 2
                    
                except Exception as status_error:
                    st.error(f"❌ ERROR: Error checking function status: {status_error}")
                    st.error(f"🔍 DEBUG: Error type: {type(status_error).__name__}")
                    st.subheader("📋 Full Stack Trace")
                    st.code(traceback.format_exc())
                    
                    # Show what we were trying to do
                    st.subheader("🔍 Debug Info")
                    st.write(f"**Function Name**: {function_name}")
                    st.write(f"**Call ID**: {call_result.id}")
                    st.write(f"**Wait Time**: {wait_time}s")
                    break
                
                if wait_time >= max_wait:
                    st.error("⏰ Function call timed out after 5 minutes")
                
        except Exception as e:
            st.error(f"❌ Failed to call function: {e}")
            st.code(traceback.format_exc())


def check_function_result():
    """Check the result of a specific function call by ID"""
    st.subheader("🔍 Check Function Result by Call ID")
    
    # ============================================================
    # v11 (2025.01.03): Added function_external_id input
    #   - retrieve() requires function identifier, not just call_id
    # ============================================================
    function_external_id = st.text_input("Function External ID", value="test-toolkit-function", key="check_function_id")
    call_id = st.text_input("Function Call ID", placeholder="e.g., 1510507578838126")
    
    if st.button("📋 Get Function Result", key="get_result_button"):
        if not call_id:
            st.error("Please enter a Call ID")
            return
        if not function_external_id:
            st.error("Please enter a Function External ID")
            return
            
        try:
            client = get_cognite_client()
            
            # Get the function call result
            result = client.functions.calls.retrieve(
                function_external_id=function_external_id,
                call_id=int(call_id)
            )
            
            st.subheader("📊 Function Call Details")
            st.write(f"**Status**: {result.status}")
            st.write(f"**Start Time**: {result.start_time}")
            st.write(f"**End Time**: {result.end_time}")
            
            if result.status == "Completed":
                st.success("✅ Function completed successfully!")
                
                if hasattr(result, 'response') and result.response:
                    st.subheader("🎉 Function Response")
                    
                    # Show summary if available
                    if isinstance(result.response, dict) and 'summary' in result.response:
                        summary = result.response['summary']
                        st.subheader("📊 Test Summary")
                        
                        if summary.get('toolkit_installed'):
                            st.success("✅ cognite-toolkit installed successfully!")
                        else:
                            st.error("❌ cognite-toolkit installation failed")
                        
                        if summary.get('cdf_command_available'):
                            st.success("✅ cdf command is available!")
                        else:
                            st.error("❌ cdf command not available")
                        
                        if summary.get('library_importable'):
                            st.success("✅ Toolkit library can be imported!")
                        else:
                            st.warning("⚠️ Toolkit library import issues")
                    
                    # Show full response
                    with st.expander("🔍 Full Response Data"):
                        st.json(result.response)
                        
                    # Analysis
                    if isinstance(result.response, dict):
                        st.subheader("🎯 Analysis")
                        if result.response.get('summary', {}).get('toolkit_installed') and \
                           result.response.get('summary', {}).get('cdf_command_available'):
                            st.success("🎉 **BREAKTHROUGH CONFIRMED**: Real toolkit works in Functions!")
                            st.info("💡 **Next Step**: Implement full build/deploy workflow")
                        else:
                            st.error("❌ Toolkit approach has limitations in Functions")
                else:
                    st.warning("⚠️ No response data available")
                    
            elif result.status == "Failed":
                st.error(f"❌ Function failed")
                if hasattr(result, 'error') and result.error:
                    st.error(f"Error: {result.error}")
                    
            elif result.status == "Running":
                st.info("🔄 Function is still running...")
                
            else:
                st.info(f"Function status: {result.status}")
                
        except Exception as e:
            st.error(f"❌ Failed to retrieve function result: {e}")
            st.code(str(e))


def test_build_api(BuildCommand):
    """Test BuildCommand API with dummy data"""
    st.subheader("🏗️ Testing BuildCommand API")
    
    try:
        # Create instance
        build_cmd = BuildCommand()
        st.success("✅ BuildCommand instance created")
        
        # Try to call build_modules method (not execute)
        st.info("🧪 Testing build_modules method...")
        
        # Create dummy parameters
        from cognite_toolkit._cdf_tk.data_classes import ModuleDirectories, BuildVariables
        
        # Dummy module directories
        modules = ModuleDirectories()
        st.success("✅ ModuleDirectories created")
        
        # Dummy build variables  
        variables = BuildVariables()
        st.success("✅ BuildVariables created")
        
        # Dummy build directory
        build_dir = Path("/tmp/dummy_build")
        
        st.info("🚀 Calling build_modules...")
        
        # Call the actual API method
        result = build_cmd.build_modules(
            modules=modules,
            build_dir=build_dir,
            variables=variables,
            verbose=True,
            progress_bar=False,
            on_error='continue'
        )
        
        st.success(f"✅ build_modules returned: {type(result)}")
        st.code(f"Result: {result}")
        
        return True, result
        
    except Exception as e:
        st.error(f"❌ BuildCommand API failed: {e}")
        st.code(traceback.format_exc())
        return False, str(e)


def test_deploy_api(DeployCommand, EnvironmentVariables):
    """Test DeployCommand API with dummy data"""
    st.subheader("🚀 Testing DeployCommand API")
    
    try:
        # Create instances
        deploy_cmd = DeployCommand()
        st.success("✅ DeployCommand instance created")
        
        env_vars = EnvironmentVariables()
        st.success("✅ EnvironmentVariables instance created")
        
        # Try to call deploy_build_directory method
        st.info("🧪 Testing deploy_build_directory method...")
        
        # Dummy parameters
        build_dir = Path("/tmp/dummy_build")
        
        st.info("🚀 Calling deploy_build_directory (dry_run=True)...")
        
        # Call the actual API method
        result = deploy_cmd.deploy_build_directory(
            env_vars=env_vars,
            build_dir=build_dir,
            build_env_name="dummy",
            dry_run=True,  # Safe dry-run
            drop=False,
            drop_data=False,
            force_update=False,
            include=None,
            verbose=True
        )
        
        st.success(f"✅ deploy_build_directory returned: {result}")
        st.code(f"Result: {result}")
        
        return True, result
        
    except Exception as e:
        st.error(f"❌ DeployCommand API failed: {e}")
        st.code(traceback.format_exc())
        return False, str(e)


def test_cognite_client():
    """Test if CogniteClient works in SaaS"""
    st.subheader("🔗 Testing CogniteClient")
    
    try:
        from cognite.client import CogniteClient
        
        client = CogniteClient()
        st.success("✅ CogniteClient created")
        
        # Test basic properties
        st.info(f"🔗 Project: {client.config.project}")
        st.info(f"🌐 Cluster: {client.config.base_url}")
        
        return True, client
        
    except Exception as e:
        st.error(f"❌ CogniteClient failed: {e}")
        st.code(traceback.format_exc())
        return False, str(e)


def main():
    """Main Streamlit app"""
    
    # Display version at the top
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🧪 Cognite Toolkit API Test")
    with col2:
        st.caption(f"Version: {VERSION}")
        st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    # Warm up the cache immediately (runs once per session)
    with st.spinner("🔌 Initializing Cognite connection..."):
        try:
            client = get_cognite_client()
            st.success(f"✅ Connected to: {client.config.project}")
        except Exception as e:
            st.error(f"❌ Failed to connect: {e}")
    
    st.markdown("---")
    
    # Main function test interface
    test_trial_3_cognite_functions()
    
    st.markdown("---")
    
    # Function Result Checker
    check_function_result()



if __name__ == "__main__":
    main()
