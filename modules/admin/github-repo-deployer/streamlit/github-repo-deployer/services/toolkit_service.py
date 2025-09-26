"""
Toolkit Service - Handles Cognite Toolkit operations using unified core operations
"""
import os
import streamlit as st
from typing import Optional, Tuple, Dict, Any
from core.toolkit_operations import build_project, deploy_project


class ToolkitService:
    """Service for Cognite Toolkit operations"""
    
    def __init__(self):
        self.toolkit_available = self._check_toolkit_availability()
    
    def _check_toolkit_availability(self) -> bool:
        """Check if Cognite Toolkit is available"""
        try:
            result = subprocess.run(['cdf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_command_with_env(self, command: str, env_vars: Dict[str, str] = None, 
                            cwd: str = None) -> Tuple[bool, str, str]:
        """Run command with environment variables"""
        try:
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Run command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                env=env,
                cwd=cwd,
                timeout=300  # 5 minute timeout
            )
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out after 5 minutes"
        except Exception as e:
            return False, "", str(e)
    
    def build_project(self, project_path: str, env_vars: Dict[str, str] = None, env_name: str = "weather") -> Tuple[bool, str, str]:
        """Build project using unified core operations (same as test framework)"""
        try:
            # Merge environment variables with loaded env file
            merged_env_vars = os.environ.copy()
            if env_vars:
                merged_env_vars.update(env_vars)
            
            # Use unified build function with verbose logging
            success, output, error = build_project(
                project_path, 
                merged_env_vars, 
                env_name=env_name,
                verbose=True,
                logger=st.info
            )
            
            if success:
                st.success("✅ Build completed successfully!")
                return True, output, ""
            else:
                st.error(f"❌ Build failed: {error}")
                return False, output, error
                
        except Exception as e:
            st.error(f"❌ Build failed: {e}")
            return False, "", str(e)
    
    def deploy_project(self, project_path: str, env_vars: Dict[str, str] = None, env_name: str = "weather") -> Tuple[bool, str, str]:
        """Deploy project using unified core operations (same as test framework)"""
        try:
            # Merge environment variables with loaded env file
            merged_env_vars = os.environ.copy()
            if env_vars:
                merged_env_vars.update(env_vars)
            
            # Debug: show what OAuth2 vars we have
            oauth_vars = ['IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TOKEN_URL']
            available_oauth = {var: bool(merged_env_vars.get(var)) for var in oauth_vars}
            st.info(f"🔐 OAuth2 credentials check: {available_oauth}")
            
            # Use unified deploy function with verbose logging
            success, output, error = deploy_project(
                project_path, 
                merged_env_vars, 
                env_name=env_name,
                verbose=True,
                logger=st.info
            )
            
            if success:
                st.success("✅ Deployment completed successfully!")
                return True, output, ""
            else:
                st.error(f"❌ Deployment failed: {error}")
                return False, output, error
                
        except Exception as e:
            st.error(f"❌ Deploy failed: {e}")
            return False, "", str(e)
    
    def build_and_deploy(self, project_path: str, env_vars: Dict[str, str] = None, env_name: str = "weather") -> Tuple[bool, str, str]:
        """Build and deploy project in one operation"""
        try:
            st.info("🔨🚀 Building and deploying project...")
            
            # Build first
            build_success, build_stdout, build_stderr = self.build_project(project_path, env_vars, env_name)
            
            if not build_success:
                return False, build_stdout, build_stderr
            
            # Deploy if build succeeded
            deploy_success, deploy_stdout, deploy_stderr = self.deploy_project(project_path, env_vars, env_name)
            
            if deploy_success:
                st.success("🎉 Build and deployment completed successfully!")
                return True, f"{build_stdout}\n{deploy_stdout}", ""
            else:
                st.error("❌ Build succeeded but deployment failed!")
                return False, f"{build_stdout}\n{deploy_stdout}", deploy_stderr
                
        except Exception as e:
            st.error(f"Toolkit error during build and deploy: {e}")
            return False, "", str(e)
    
    def _install_toolkit_guide(self):
        """Show guide for installing Cognite Toolkit"""
        st.info("💡 **Install Cognite Toolkit:**")
        st.code("pip install cognite-toolkit", language="bash")
        st.info("📚 **Documentation:** https://docs.cognite.com/cdf/tools/toolkit/")
    
    def get_toolkit_info(self) -> Dict[str, Any]:
        """Get information about the toolkit installation"""
        return {
            "available": self.toolkit_available,
            "version": self._get_toolkit_version() if self.toolkit_available else None
        }
    
    def _get_toolkit_version(self) -> Optional[str]:
        """Get toolkit version"""
        try:
            result = subprocess.run(['cdf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


# Global toolkit service instance
toolkit_service = ToolkitService()
