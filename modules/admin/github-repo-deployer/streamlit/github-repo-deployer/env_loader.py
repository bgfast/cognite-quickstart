import streamlit as st
import state

def render_env_ui():
    env_option = st.radio(
        "Choose how to handle environment variables:",
        ["📁 Upload .env file", "🔄 Generate from current CDF connection", "⏭️ Skip (use existing environment)"],
        help="Select how you want to provide environment variables for the deployment"
    )
    env_vars = state.get_env_vars() or {}
    # Minimal placeholder to keep refactor incremental; reuse main.py handlers.
    return env_option, env_vars


