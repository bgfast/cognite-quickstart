"""
Workflow Engine - Manages the 3-step workflow logic
"""
import streamlit as st
from typing import Optional, List, Dict, Any
from .state_manager import state_manager
from .error_handler import error_handler, WorkflowError


class WorkflowEngine:
    """Manages the 3-step workflow execution"""
    
    def __init__(self):
        self.steps = {
            1: "Download & Environment",
            2: "Select Configuration", 
            3: "Build and Deploy"
        }
    
    def get_current_step(self) -> int:
        """Get current workflow step"""
        return state_manager.get_step()
    
    def can_advance_to_step(self, target_step: int) -> bool:
        """Check if we can advance to a specific step"""
        current_step = self.get_current_step()
        
        if target_step <= current_step:
            return True  # Can go back to previous steps
        
        # Check prerequisites for advancing
        if target_step == 2:
            return state_manager.get_extracted_path() is not None
        
        if target_step == 3:
            return (state_manager.get_extracted_path() is not None and 
                   state_manager.get_selected_config() is not None)
        
        return False
    
    def advance_to_step(self, target_step: int) -> bool:
        """Advance to a specific step if possible"""
        if self.can_advance_to_step(target_step):
            state_manager.set_step(target_step)
            return True
        else:
            st.warning(f"⚠️ Cannot advance to step {target_step}. Prerequisites not met.")
            return False
    
    def get_step_status(self, step: int) -> str:
        """Get status of a specific step"""
        current_step = self.get_current_step()
        
        if step < current_step:
            return "completed"
        elif step == current_step:
            return "current"
        else:
            return "future"
    
    def get_step_requirements(self, step: int) -> List[str]:
        """Get requirements for a specific step"""
        requirements = {
            1: ["Repository URL", "Environment variables"],
            2: ["Extracted repository", "Config files discovered"],
            3: ["Selected configuration", "Environment variables"]
        }
        return requirements.get(step, [])
    
    def validate_step_completion(self, step: int) -> bool:
        """Validate that a step is properly completed"""
        if step == 1:
            return (state_manager.get_extracted_path() is not None and 
                   len(state_manager.get_config_files()) > 0)
        
        elif step == 2:
            return state_manager.get_selected_config() is not None
        
        elif step == 3:
            return (state_manager.get_selected_config() is not None and
                   len(state_manager.get_env_vars()) > 0)
        
        return False
    
    def get_next_step(self) -> Optional[int]:
        """Get the next step in the workflow"""
        current_step = self.get_current_step()
        
        if current_step < 3:
            return current_step + 1
        
        return None  # Workflow complete
    
    def is_workflow_complete(self) -> bool:
        """Check if the workflow is complete"""
        return self.get_current_step() == 3 and self.validate_step_completion(3)
    
    def reset_workflow(self):
        """Reset the workflow to step 1"""
        state_manager.reset()
        st.rerun()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of the current workflow state"""
        return {
            "current_step": self.get_current_step(),
            "step_name": self.steps.get(self.get_current_step(), "Unknown"),
            "extracted_path": state_manager.get_extracted_path(),
            "config_files": state_manager.get_config_files(),
            "selected_config": state_manager.get_selected_config(),
            "repo_info": state_manager.get_repo_info(),
            "is_complete": self.is_workflow_complete()
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()
