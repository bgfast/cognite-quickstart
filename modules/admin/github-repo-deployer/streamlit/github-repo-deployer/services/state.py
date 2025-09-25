import streamlit as st

def set_workflow_step(step: int) -> None:
    st.session_state['workflow_step'] = step

def get_workflow_step() -> int:
    return st.session_state.get('workflow_step', 1)

def set_extracted_path(path: str) -> None:
    st.session_state['extracted_path'] = path

def get_extracted_path() -> str | None:
    return st.session_state.get('extracted_path')

def set_config_files(files: list[str]) -> None:
    st.session_state['config_files'] = files

def get_config_files() -> list[str]:
    return st.session_state.get('config_files', [])

def set_env_vars(env_vars: dict) -> None:
    st.session_state['env_vars'] = env_vars

def get_env_vars() -> dict | None:
    return st.session_state.get('env_vars')

def set_selected_config(config: str) -> None:
    st.session_state['selected_config'] = config

def set_selected_env(env: str) -> None:
    st.session_state['selected_env'] = env

def get_selected_env() -> str | None:
    return st.session_state.get('selected_env')

def reset() -> None:
    for key in ['workflow_step','extracted_path','config_files','env_vars','selected_config','selected_env']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state['workflow_step'] = 1


