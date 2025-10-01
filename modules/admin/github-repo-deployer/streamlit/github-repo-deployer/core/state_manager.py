"""
State Manager - Centralized state management for the workflow
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import streamlit as st
import json


@dataclass
class WorkflowState:
    """Centralized workflow state"""
    step: int = 1
    extracted_path: Optional[str] = None
    config_files: List[str] = field(default_factory=list)
    selected_config: Optional[str] = None
    selected_env: Optional[str] = None
    env_vars: Dict[str, str] = field(default_factory=dict)
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    selected_branch: str = "main"
    debug_mode: bool = False
    
    def validate(self) -> bool:
        """Validate state consistency"""
        if self.step < 1 or self.step > 5:
            return False
        
        if self.step >= 2 and not self.extracted_path:
            return False
            
        if self.step >= 3 and not self.selected_config:
            return False
            
        return True
    
    def reset(self):
        """Reset to initial state"""
        self.step = 1
        self.extracted_path = None
        self.config_files = []
        self.selected_config = None
        self.selected_env = None
        self.env_vars = {}
        self.repo_owner = None
        self.repo_name = None
        self.selected_branch = "main"


class StateManager:
    """Manages workflow state with validation and persistence"""
    
    def __init__(self):
        self._state = WorkflowState()
        self._load_from_session()
    
    def _load_from_session(self):
        """Load state from Streamlit session state"""
        if 'workflow_state' in st.session_state:
            try:
                state_data = json.loads(st.session_state['workflow_state'])
                self._state = WorkflowState(**state_data)
            except Exception as e:
                st.warning(f"Failed to load state: {e}")
                self._state = WorkflowState()
    
    def _save_to_session(self):
        """Save state to Streamlit session state"""
        try:
            state_data = json.dumps(self._state.__dict__)
            st.session_state['workflow_state'] = state_data
        except Exception as e:
            st.error(f"Failed to save state: {e}")
    
    def get_state(self) -> WorkflowState:
        """Get current state"""
        return self._state
    
    def set_step(self, step: int) -> bool:
        """Set workflow step with validation"""
        if 1 <= step <= 5:
            self._state.step = step
            self._save_to_session()
            return True
        return False
    
    def set_extracted_path(self, path: str):
        """Set extracted repository path"""
        self._state.extracted_path = path
        self._save_to_session()
    
    def set_config_files(self, files: List[str]):
        """Set discovered config files"""
        self._state.config_files = files
        self._save_to_session()
    
    def set_selected_config(self, config: str):
        """Set selected configuration"""
        self._state.selected_config = config
        self._state.selected_env = config.replace('config.', '').replace('.yaml', '')
        self._save_to_session()
    
    def set_env_vars(self, env_vars: Dict[str, str]):
        """Set environment variables"""
        self._state.env_vars = env_vars
        self._save_to_session()
    
    def set_repo_info(self, owner: str, name: str, branch: str = "main"):
        """Set repository information"""
        self._state.repo_owner = owner
        self._state.repo_name = name
        self._state.selected_branch = branch
        self._save_to_session()
    
    def set_debug_mode(self, debug: bool):
        """Set debug mode"""
        self._state.debug_mode = debug
        self._save_to_session()
    
    def reset(self):
        """Reset to initial state"""
        self._state.reset()
        self._save_to_session()
    
    def validate(self) -> bool:
        """Validate current state"""
        return self._state.validate()
    
    def get_step(self) -> int:
        """Get current step"""
        return self._state.step
    
    def get_extracted_path(self) -> Optional[str]:
        """Get extracted path"""
        return self._state.extracted_path
    
    def get_config_files(self) -> List[str]:
        """Get config files"""
        return self._state.config_files
    
    def get_selected_config(self) -> Optional[str]:
        """Get selected config"""
        return self._state.selected_config
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables"""
        return self._state.env_vars
    
    def get_repo_info(self) -> tuple:
        """Get repository information"""
        return self._state.repo_owner, self._state.repo_name, self._state.selected_branch
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self._state.debug_mode


# Global state manager instance
state_manager = StateManager()

