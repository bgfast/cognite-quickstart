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
    env_option = st.radio(
        "Choose how to handle environment variables:",
        ["📁 Upload .env file", "🔄 Generate from current CDF connection", "⏭️ Skip (use existing environment)"],
        help="Select how you want to provide environment variables for the deployment"
    )
    
    env_vars = {}
    
    if env_option == "📁 Upload .env file":
        st.subheader("📁 Upload Environment File")
        uploaded_file = st.file_uploader(
            "Choose an environment file",
            type=None,
            help="Upload an environment file (.env, .txt, or any text file) containing your CDF project configuration"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file content
                content = uploaded_file.getvalue().decode('utf-8')
                
                # Parse the environment variables
                env_vars = parse_env_file_content(content)
                
                # Validate the environment variables
                missing_vars = validate_env_vars(env_vars)
                
                if missing_vars:
                    st.warning(f"⚠️ Missing required environment variables: {', '.join(missing_vars)}")
                    st.info("💡 Make sure your .env file contains CDF_PROJECT and CDF_CLUSTER")
                else:
                    st.success("✅ Environment file parsed successfully!")
                    st.write(f"**Found {len(env_vars)} environment variables**")
                    
                    # Show a preview of the environment variables (without sensitive values)
                    with st.expander("📋 Environment Variables Preview"):
                        for key, value in env_vars.items():
                            if 'secret' in key.lower() or 'password' in key.lower() or 'token' in key.lower():
                                st.write(f"**{key}**: `***hidden***`")
                            else:
                                st.write(f"**{key}**: `{value}`")
                
            except Exception as e:
                st.error(f"❌ Error reading .env file: {e}")
                st.info("💡 Make sure the file is a valid .env file with KEY=VALUE format")
    
    elif env_option == "🔄 Generate from current CDF connection":
        st.subheader("🔄 Generate from Current CDF Connection")
        st.info("This will generate a .env file based on your current CDF connection settings.")
        
        if st.button("🔄 Generate .env file"):
            with st.spinner("Generating .env file from current CDF connection..."):
                env_content = generate_env_file_from_cdf()
                
                if env_content:
                    st.success("✅ Generated .env file from current CDF connection!")
                    
                    # Parse the generated content
                    env_vars = parse_env_file_content(env_content)
                    
                    # Show the generated content
                    with st.expander("📋 Generated .env file content"):
                        st.code(env_content, language='bash')
                    
                    # Allow download
                    st.download_button(
                        label="📥 Download .env file",
                        data=env_content,
                        file_name="cdf_connection.env",
                        mime="text/plain"
                    )
                else:
                    st.error("❌ Could not generate .env file from current CDF connection")
                    st.info("💡 Make sure you're connected to a CDF project")
    
    elif env_option == "⏭️ Skip (use existing environment)":
        st.subheader("⏭️ Use Existing Environment")
        st.info("Using environment variables from the current session.")
        
        # Get current environment variables
        import os
        env_vars = {
            'CDF_PROJECT': os.getenv('CDF_PROJECT', ''),
            'CDF_CLUSTER': os.getenv('CDF_CLUSTER', ''),
            'CDF_URL': os.getenv('CDF_URL', ''),
        }
        
        # Add other relevant environment variables
        for key in ['IDP_CLIENT_ID', 'IDP_CLIENT_SECRET', 'IDP_TENANT_ID']:
            if os.getenv(key):
                env_vars[key] = os.getenv(key)
        
        if env_vars.get('CDF_PROJECT') and env_vars.get('CDF_CLUSTER'):
            st.success("✅ Found CDF project configuration in environment")
            st.write(f"**Project**: {env_vars.get('CDF_PROJECT')}")
            st.write(f"**Cluster**: {env_vars.get('CDF_CLUSTER')}")
        else:
            st.warning("⚠️ CDF_PROJECT or CDF_CLUSTER not found in environment")
    
    # Store the environment variables in session state
    if env_vars:
        state.set_env_vars(env_vars)
    
    return env_option, env_vars


