import streamlit as st
from . import state
import os

def parse_env_file_content(content):
    """Parse .env file content and return as dictionary"""
    env_vars = {}
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    return env_vars

def validate_env_vars(env_vars):
    """Validate that required environment variables are present"""
    required_vars = ['CDF_PROJECT', 'CDF_CLUSTER']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    return missing_vars

def get_cdf_environment_info():
    """Get CDF environment information from current connection"""
    try:
        from cognite.client import CogniteClient
        client = CogniteClient()
        
        # Get project info
        project_info = client.config.project
        cluster_info = client.config.base_url
        
        # Extract cluster from URL
        if 'bluefield' in cluster_info:
            cluster = 'bluefield'
        elif 'greenfield' in cluster_info:
            cluster = 'greenfield'
        else:
            cluster = 'unknown'
        
        # Get authentication info (if available)
        auth_info = {}
        if hasattr(client.config, 'credentials'):
            creds = client.config.credentials
            if hasattr(creds, 'client_id'):
                auth_info['client_id'] = getattr(creds, 'client_id', '')
            if hasattr(creds, 'client_secret'):
                auth_info['client_secret'] = getattr(creds, 'client_secret', '')
            if hasattr(creds, 'tenant_id'):
                auth_info['tenant_id'] = getattr(creds, 'tenant_id', '')
            if hasattr(creds, 'scopes'):
                auth_info['scopes'] = getattr(creds, 'scopes', '')
            if hasattr(creds, 'token_url'):
                auth_info['token_url'] = getattr(creds, 'token_url', '')
        
        return {
            'project': project_info,
            'cluster': cluster,
            'base_url': cluster_info,
            **auth_info
        }
    except Exception as e:
        st.error(f"Could not get CDF environment info: {e}")
        return None

def generate_env_file_from_cdf():
    """Generate .env file content from current CDF connection"""
    env_info = get_cdf_environment_info()
    if not env_info:
        return None
    
    env_content = f"""# Generated from current CDF connection
# CDF Project Configuration
CDF_PROJECT={env_info['project']}
CDF_CLUSTER={env_info['cluster']}
CDF_URL={env_info['base_url']}

# IDP Authentication Configuration
IDP_CLIENT_ID={env_info.get('client_id', '')}
IDP_CLIENT_SECRET={env_info.get('client_secret', '')}
IDP_TENANT_ID={env_info.get('tenant_id', '')}
IDP_SCOPES={env_info.get('scopes', '')}
IDP_TOKEN_URL={env_info.get('token_url', '')}

# Optional: Function/Transformation Client Credentials
FUNCTION_CLIENT_ID=
FUNCTION_CLIENT_SECRET=
TRANSFORMATION_CLIENT_ID=
TRANSFORMATION_CLIENT_SECRET=

# Optional: Superuser Source ID
SUPERUSER_SOURCEID_ENV=
USER_IDENTIFIER=

"""
    return env_content

def render_env_ui():
    st.subheader("🔧 Environment Variables")
    st.info("Using existing environment variables from current session")
    
    # Always use existing environment - no options needed
    env_option = "⏭️ Skip (use existing environment)"
    
    # Get current environment variables
    import os
    env_vars = {
        'CDF_PROJECT': os.getenv('CDF_PROJECT', ''),
        'CDF_CLUSTER': os.getenv('CDF_CLUSTER', ''),
        'CDF_URL': os.getenv('CDF_URL', ''),
    }
    
    # Add other relevant environment variables
    for key in ['IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TENANT_ID', 'IDP_TOKEN_URL', 'IDP_SCOPES']:
        if os.getenv(key):
            env_vars[key] = os.getenv(key)
    
    if env_vars.get('CDF_PROJECT') and env_vars.get('CDF_CLUSTER'):
        st.success("✅ Found CDF project configuration in environment")
        st.write(f"**Project**: {env_vars.get('CDF_PROJECT')}")
        st.write(f"**Cluster**: {env_vars.get('CDF_CLUSTER')}")
        
        # Show OAuth2 credential status for deployment
        oauth_vars = ['IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TOKEN_URL']
        oauth_status = {var: bool(env_vars.get(var)) for var in oauth_vars}
        if all(oauth_status.values()):
            st.success("✅ OAuth2 credentials available for deployment")
        else:
            st.warning(f"⚠️ Missing OAuth2 credentials: {[k for k, v in oauth_status.items() if not v]}")
    else:
        st.warning("⚠️ CDF_PROJECT or CDF_CLUSTER not found in environment")
    
    # Store the environment variables in session state
    if env_vars:
        state.set_env_vars(env_vars)
    
    return env_option, env_vars


