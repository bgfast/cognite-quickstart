"""
Error Handler - Centralized error handling and recovery
"""
import streamlit as st
from typing import Optional, Callable, Any
import traceback
import logging


class WorkflowError(Exception):
    """Custom workflow error with recovery actions"""
    
    def __init__(self, message: str, recovery_action: Optional[Callable] = None, 
                 error_type: str = "workflow", details: Optional[dict] = None):
        self.message = message
        self.recovery_action = recovery_action
        self.error_type = error_type
        self.details = details or {}
        super().__init__(message)


class ErrorHandler:
    """Centralized error handling with recovery mechanisms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history = []
    
    def handle_error(self, error: Exception, context: str = "", show_recovery: bool = True):
        """Handle errors with recovery options"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        self.logger.error(f"Error in {context}: {error}")
        
        # Display error to user
        st.error(f"❌ **{context} Error**: {str(error)}")
        
        # Show recovery action if available
        if show_recovery and isinstance(error, WorkflowError) and error.recovery_action:
            st.warning("🔄 **Recovery Available**")
            if st.button("🔄 Try Recovery", key=f"recovery_{len(self.error_history)}"):
                try:
                    error.recovery_action()
                    st.success("✅ Recovery successful!")
                    st.rerun()
                except Exception as recovery_error:
                    st.error(f"❌ Recovery failed: {recovery_error}")
        
        # Show debug info if in debug mode
        if st.session_state.get('debug_mode', False):
            with st.expander("🔍 Debug Information"):
                st.code(traceback.format_exc(), language="text")
                st.json(error_info)
    
    def handle_github_error(self, error: Exception, repo_info: str = ""):
        """Handle GitHub API errors specifically"""
        if "404" in str(error):
            st.error(f"❌ **Repository Not Found**: {repo_info}")
            st.info("💡 Check the repository URL and make sure it exists")
        elif "403" in str(error):
            st.error(f"❌ **Access Denied**: {repo_info}")
            st.info("💡 This might be a private repository. Try a public repository instead")
        elif "CORS" in str(error):
            st.error(f"❌ **CORS Error**: GitHub download failed due to browser restrictions")
            st.info("💡 The app will use GitHub API instead of direct download")
        else:
            self.handle_error(error, f"GitHub API ({repo_info})")
    
    def handle_toolkit_error(self, error: Exception, operation: str = ""):
        """Handle Cognite Toolkit errors specifically"""
        if "not found" in str(error).lower():
            st.error(f"❌ **Toolkit Error**: {operation} failed - toolkit not found")
            st.info("💡 Make sure the Cognite toolkit is installed: `pip install cognite-toolkit`")
        elif "permission" in str(error).lower():
            st.error(f"❌ **Permission Error**: {operation} failed - insufficient permissions")
            st.info("💡 Check your CDF project permissions and authentication")
        elif "config" in str(error).lower():
            st.error(f"❌ **Configuration Error**: {operation} failed - invalid configuration")
            st.info("💡 Check your config files and environment variables")
        else:
            self.handle_error(error, f"Toolkit {operation}")
    
    def handle_cdf_error(self, error: Exception, operation: str = ""):
        """Handle CDF connection errors specifically"""
        if "connection" in str(error).lower():
            st.error(f"❌ **CDF Connection Error**: {operation} failed")
            st.info("💡 Check your CDF project configuration and network connection")
        elif "authentication" in str(error).lower():
            st.error(f"❌ **Authentication Error**: {operation} failed")
            st.info("💡 Check your CDF credentials and environment variables")
        else:
            self.handle_error(error, f"CDF {operation}")
    
    def get_error_history(self) -> list:
        """Get error history for debugging"""
        return self.error_history
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history = []


# Global error handler instance
error_handler = ErrorHandler()

