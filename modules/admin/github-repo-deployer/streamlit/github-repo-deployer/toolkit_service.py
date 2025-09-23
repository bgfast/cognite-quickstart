import subprocess
import os
import streamlit as st

def run_command_with_env(command, env_vars=None, cwd=None):
    """Run a command with custom environment variables"""
    # Start with current environment
    env = os.environ.copy()
    
    # Add custom environment variables if provided
    if env_vars:
        env.update(env_vars)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", f"Error running command: {e}"

def run_cognite_toolkit_build(project_path, env_vars=None):
    """Run cdf build --env all command in the project directory with optional environment variables"""
    try:
        # Check if we're in a browser environment (Pyodide/emscripten)
        try:
            import js
            # We're in a browser environment, run build logic directly
            st.info("🌐 **Browser Environment Detected** - Running build logic directly")
            return run_cognite_build_direct(project_path, env_vars)
        except ImportError:
            # We're in a server environment, subprocess calls should work
            pass
        
        # Use the custom command runner with environment variables
        returncode, stdout, stderr = run_command_with_env(
            'cdf build --env all',
            env_vars=env_vars,
            cwd=project_path
        )
        
        return returncode == 0, stdout, stderr
        
    except Exception as e:
        return False, "", f"Error running build command: {e}"

def run_cognite_toolkit_deploy(project_path, env_vars=None):
    """Run cdf deploy --env all command in the project directory with optional environment variables"""
    try:
        # Check if we're in a browser environment (Pyodide/emscripten)
        try:
            import js
            # We're in a browser environment, run deploy logic directly
            st.info("🌐 **Browser Environment Detected** - Running deploy logic directly")
            return run_cognite_deploy_direct(project_path, env_vars)
        except ImportError:
            # We're in a server environment, subprocess calls should work
            pass
        
        # Use the custom command runner with environment variables
        returncode, stdout, stderr = run_command_with_env(
            'cdf deploy --env all',
            env_vars=env_vars,
            cwd=project_path
        )
        
        return returncode == 0, stdout, stderr
        
    except Exception as e:
        return False, "", f"Error running deploy command: {e}"

def run_cognite_build_direct(project_path, env_vars=None):
    """Run build logic directly (for browser environments)"""
    # This would need to be implemented for browser environments
    # For now, return a placeholder
    return False, "", "Build not implemented for browser environment"

def run_cognite_deploy_direct(project_path, env_vars=None):
    """Run deploy logic directly (for browser environments)"""
    # This would need to be implemented for browser environments
    # For now, return a placeholder
    return False, "", "Deploy not implemented for browser environment"


