import streamlit as st
import requests
import zipfile
import tempfile
import os
import subprocess
import json
import base64
import urllib.parse
from pathlib import Path
from cognite.client import CogniteClient
import time

# --- Global Initialization ---
CLIENT = None
IS_LOCAL_ENV = False

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:8501')

def initialize_cdf_client():
    """Initialize CogniteClient with proper error handling for local/SaaS environments"""
    global CLIENT, IS_LOCAL_ENV
    
    try:
        CLIENT = CogniteClient()
        IS_LOCAL_ENV = False
        return True
    except Exception as e:
        # Running locally without CDF authentication
        CLIENT = None
        IS_LOCAL_ENV = True
        if st.session_state.get('debug_mode', False):
            st.warning(f"Running in LOCAL MODE: {e}")
        return False

# Try to initialize CDF client
initialize_cdf_client()

def get_github_oauth_url():
    """Generate GitHub OAuth authorization URL"""
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_REDIRECT_URI,
        'scope': 'repo',
        'state': 'github_oauth_state'
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code):
    """Exchange OAuth authorization code for access token"""
    url = "https://github.com/login/oauth/access_token"
    data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI
    }
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        st.error(f"Failed to exchange code for token: {e}")
        return None

def get_github_user_info(token):
    """Get GitHub user information using access token"""
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get user info: {e}")
        return None

def parse_github_url(url):
    """Parse GitHub repository URL to extract owner and repo name"""
    import re
    
    # Remove trailing slash and .git if present
    url = url.rstrip('/').rstrip('.git')
    
    # GitHub URL patterns
    patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)',
        r'git@github\.com:([^/]+)/([^/]+)',
        r'github\.com/([^/]+)/([^/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            return owner, repo
    
    return None, None

def download_github_repo_zip(repo_owner, repo_name, branch="main", token=None):
    """Download a GitHub repository as a ZIP file with optional authentication"""
    if token:
        # Use authenticated API for private repos
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{branch}"
        headers = {'Authorization': f'token {token}'}
    else:
        # Use public ZIP URL for public repos
        url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        headers = {}
    
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Create a temporary file to store the ZIP
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        # Download the ZIP file
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name
        
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            st.error(f"Repository not found or not accessible. Make sure it exists and you have access to it.")
        elif response.status_code == 403:
            st.error(f"Access denied. This might be a private repository - please authenticate with GitHub.")
        else:
            st.error(f"Failed to download repository: {e}")
        return None

def extract_zip_to_temp_dir(zip_path, extract_to=None):
    """Extract ZIP file to a temporary directory"""
    if extract_to is None:
        extract_to = tempfile.mkdtemp()
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Find the extracted folder (GitHub adds a suffix to the folder name)
        extracted_folders = [f for f in os.listdir(extract_to) if os.path.isdir(os.path.join(extract_to, f))]
        if extracted_folders:
            return os.path.join(extract_to, extracted_folders[0])
        else:
            return extract_to
            
    except zipfile.BadZipFile as e:
        st.error(f"Failed to extract ZIP file: {e}")
        return None
    except Exception as e:
        st.error(f"Error extracting files: {e}")
        return None

def run_cognite_toolkit_build(project_path):
    """Run cdf build command in the project directory"""
    try:
        # Change to the project directory and run cdf build
        result = subprocess.run(
            ['cdf', 'build'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Build command timed out after 5 minutes"
    except FileNotFoundError:
        return False, "", "Cognite toolkit (cdf) not found. Please install it first."
    except Exception as e:
        return False, "", f"Error running build command: {e}"

def run_cognite_toolkit_deploy(project_path):
    """Run cdf deploy command in the project directory"""
    try:
        # Change to the project directory and run cdf deploy
        result = subprocess.run(
            ['cdf', 'deploy'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Deploy command timed out after 10 minutes"
    except FileNotFoundError:
        return False, "", "Cognite toolkit (cdf) not found. Please install it first."
    except Exception as e:
        return False, "", f"Error running deploy command: {e}"

def get_github_branches(repo_owner, repo_name, token=None):
    """Get available branches from a GitHub repository"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        branches = [branch["name"] for branch in response.json()]
        return branches
        
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            st.error(f"Repository not found or not accessible. Make sure it exists and you have access to it.")
        elif response.status_code == 403:
            st.error(f"Access denied. This might be a private repository - please authenticate with GitHub.")
        else:
            st.error(f"Failed to fetch branches: {e}")
        return []

def handle_oauth_callback():
    """Handle OAuth callback and store token"""
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        if query_params['state'] == 'github_oauth_state':
            code = query_params['code']
            token = exchange_code_for_token(code)
            
            if token:
                user_info = get_github_user_info(token)
                if user_info:
                    st.session_state['github_token'] = token
                    st.session_state['github_user'] = user_info
                    st.success(f"✅ Successfully authenticated as {user_info.get('login', 'Unknown')}")
                    # Clear the URL parameters
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Failed to get user information")
            else:
                st.error("Failed to exchange code for token")

def main():
    st.set_page_config(
        page_title="GitHub Repo to CDF Deployer",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 GitHub Repo to CDF Deployer")
    st.markdown("Download files from GitHub repositories (public or private) and deploy them using the Cognite toolkit")
    
    # Handle OAuth callback
    handle_oauth_callback()
    
    # Debug mode toggle
    if 'debug_mode' not in st.session_state:
        st.session_state['debug_mode'] = False
    
    with st.sidebar:
        st.header("Settings")
        st.session_state['debug_mode'] = st.toggle("Debug Mode", value=st.session_state['debug_mode'])
        
        if st.session_state['debug_mode']:
            st.markdown("**Debug Info:**")
            st.write(f"CDF Client: {'Connected' if CLIENT else 'Not Connected'}")
            st.write(f"Local Mode: {IS_LOCAL_ENV}")
            st.write(f"GitHub OAuth: {'Configured' if GITHUB_CLIENT_ID else 'Not Configured'}")
        
        # GitHub Authentication Section
        st.markdown("---")
        st.header("🔐 GitHub Authentication")
        
        if 'github_token' in st.session_state:
            user = st.session_state.get('github_user', {})
            st.success(f"✅ Authenticated as: {user.get('login', 'Unknown')}")
            st.write(f"**Name:** {user.get('name', 'N/A')}")
            st.write(f"**Email:** {user.get('email', 'N/A')}")
            
            if st.button("🚪 Logout"):
                del st.session_state['github_token']
                del st.session_state['github_user']
                st.rerun()
        else:
            st.info("🔓 Not authenticated")
            st.write("Authenticate to access private repositories")
            
            if GITHUB_CLIENT_ID:
                oauth_url = get_github_oauth_url()
                st.markdown(f'<a href="{oauth_url}" target="_self">🔑 Login with GitHub</a>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ GitHub OAuth not configured")
                st.write("Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables")
    
    # Repository configuration
    st.header("📁 Repository Configuration")
    
    # Input method selection
    input_method = st.radio(
        "How would you like to specify the repository?",
        ["🔗 Paste GitHub URL", "✏️ Enter Owner & Name"],
        help="Choose how you want to specify the repository"
    )
    
    # Repository access type selection
    access_type = st.radio(
        "Choose repository access type:",
        ["🌐 Public Repository (No GitHub account needed)", "🔐 Private Repository (Requires GitHub account)"],
        help="Select whether you want to access a public or private repository"
    )
    
    # Initialize repo_owner and repo_name
    repo_owner = ""
    repo_name = ""
    
    # Show different UI based on input method and access type
    if "Paste GitHub URL" in input_method:
        # URL input method
        if "Public Repository" in access_type:
            st.info("🌐 **Public Repository Mode** - No GitHub account or authentication required")
            
            github_url = st.text_input(
                "GitHub Repository URL",
                value="https://github.com/cognitedata/cognite-samples",
                help="Paste the GitHub repository URL (e.g., https://github.com/owner/repo)",
                key="public_github_url"
            )
            
            # Clear any GitHub authentication for public mode
            if 'github_token' in st.session_state:
                del st.session_state['github_token']
                del st.session_state['github_user']
        else:  # Private Repository
            st.info("🔐 **Private Repository Mode** - GitHub authentication required")
            
            # Check if user is authenticated
            if 'github_token' not in st.session_state:
                st.warning("⚠️ **Authentication Required**")
                st.write("You need to authenticate with GitHub to access private repositories.")
                st.write("Please use the login button in the sidebar to authenticate.")
                
                github_url = st.text_input(
                    "GitHub Repository URL",
                    value="",
                    help="Paste the GitHub repository URL (requires authentication)",
                    key="private_github_url",
                    disabled=True
                )
            else:
                github_url = st.text_input(
                    "GitHub Repository URL",
                    value="",
                    help="Paste the GitHub repository URL (e.g., https://github.com/owner/repo)",
                    key="private_github_url"
                )
        
        # Parse the URL
        if github_url:
            parsed_owner, parsed_repo = parse_github_url(github_url)
            if parsed_owner and parsed_repo:
                repo_owner = parsed_owner
                repo_name = parsed_repo
                st.success(f"✅ Parsed: **{repo_owner}/{repo_name}**")
            else:
                st.error("❌ Invalid GitHub URL. Please use a valid GitHub repository URL.")
                st.info("Example: `https://github.com/cognitedata/cognite-samples`")
    
    else:  # Manual input method
        if "Public Repository" in access_type:
            st.info("🌐 **Public Repository Mode** - No GitHub account or authentication required")
            
            col1, col2 = st.columns(2)
            
            with col1:
                repo_owner = st.text_input(
                    "Repository Owner",
                    value="cognitedata",
                    help="GitHub username or organization name",
                    key="public_repo_owner"
                )
            
            with col2:
                repo_name = st.text_input(
                    "Repository Name",
                    value="cognite-samples",
                    help="Name of the GitHub repository",
                    key="public_repo_name"
                )
            
            # Clear any GitHub authentication for public mode
            if 'github_token' in st.session_state:
                del st.session_state['github_token']
                del st.session_state['github_user']
        
        else:  # Private Repository
            st.info("🔐 **Private Repository Mode** - GitHub authentication required")
            
            # Check if user is authenticated
            if 'github_token' not in st.session_state:
                st.warning("⚠️ **Authentication Required**")
                st.write("You need to authenticate with GitHub to access private repositories.")
                st.write("Please use the login button in the sidebar to authenticate.")
                
                # Disable repository inputs
                repo_owner = st.text_input(
                    "Repository Owner",
                    value="",
                    help="GitHub username or organization name (requires authentication)",
                    key="private_repo_owner",
                    disabled=True
                )
                
                repo_name = st.text_input(
                    "Repository Name",
                    value="",
                    help="Name of the GitHub repository (requires authentication)",
                    key="private_repo_name",
                    disabled=True
                )
            else:
                # User is authenticated, show normal inputs
                col1, col2 = st.columns(2)
                
                with col1:
                    repo_owner = st.text_input(
                        "Repository Owner",
                        value="",
                        help="GitHub username or organization name",
                        key="private_repo_owner"
                    )
                
                with col2:
                    repo_name = st.text_input(
                        "Repository Name",
                        value="",
                        help="Name of the GitHub repository",
                        key="private_repo_name"
                    )
    
    # Branch selection
    if st.button("🔄 Load Branches"):
        if not repo_owner or not repo_name:
            st.error("Please provide both repository owner and name")
        else:
            with st.spinner("Loading branches..."):
                # For public repos, don't use token; for private repos, use token if available
                token = None
                if "Private Repository" in access_type:
                    token = st.session_state.get('github_token')
                    if not token:
                        st.error("Authentication required for private repositories. Please login with GitHub first.")
                        return
                
                branches = get_github_branches(repo_owner, repo_name, token)
                if branches:
                    st.session_state['available_branches'] = branches
                    st.success(f"Found {len(branches)} branches")
                else:
                    st.error("Failed to load branches")
    
    # Show branch selector if branches are loaded
    if 'available_branches' in st.session_state:
        selected_branch = st.selectbox(
            "Select Branch",
            st.session_state['available_branches'],
            index=0 if "main" not in st.session_state['available_branches'] else st.session_state['available_branches'].index("main")
        )
    else:
        selected_branch = st.text_input("Branch", value="main")
    
    st.markdown("---")
    
    # Download and deploy section
    st.header("⬇️ Download & Deploy")
    
    if st.button("🚀 Download Repository & Deploy", type="primary"):
        if not repo_owner or not repo_name:
            st.error("Please provide both repository owner and name")
            return
        
        # Check authentication for private repos
        if "Private Repository" in access_type and 'github_token' not in st.session_state:
            st.error("Authentication required for private repositories. Please login with GitHub first.")
            return
        
        # Step 1: Download repository
        with st.spinner(f"Downloading {repo_owner}/{repo_name} from branch {selected_branch}..."):
            # For public repos, don't use token; for private repos, use token
            token = None
            if "Private Repository" in access_type:
                token = st.session_state.get('github_token')
            
            zip_path = download_github_repo_zip(repo_owner, repo_name, selected_branch, token)
            
            if not zip_path:
                st.error("Failed to download repository")
                return
            
            st.success("✅ Repository downloaded successfully")
        
        # Step 2: Extract files
        with st.spinner("Extracting files..."):
            extracted_path = extract_zip_to_temp_dir(zip_path)
            
            if not extracted_path:
                st.error("Failed to extract files")
                return
            
            st.success("✅ Files extracted successfully")
            
            if st.session_state['debug_mode']:
                st.info(f"Extracted to: {extracted_path}")
        
        # Step 3: Check for config files
        config_files = []
        for config_name in ['config.all.yaml', 'config.yaml', 'config.yml']:
            config_path = os.path.join(extracted_path, config_name)
            if os.path.exists(config_path):
                config_files.append(config_name)
        
        if config_files:
            st.success(f"✅ Found configuration files: {', '.join(config_files)}")
        else:
            st.warning("⚠️ No configuration files found. The repository might not be a Cognite toolkit project.")
        
        # Step 4: Run cdf build
        st.subheader("🔨 Building Project")
        with st.spinner("Running cdf build..."):
            build_success, build_stdout, build_stderr = run_cognite_toolkit_build(extracted_path)
            
            if build_success:
                st.success("✅ Build completed successfully")
                if st.session_state['debug_mode'] and build_stdout:
                    with st.expander("Build Output"):
                        st.code(build_stdout)
            else:
                st.error("❌ Build failed")
                if build_stderr:
                    st.error(f"Error: {build_stderr}")
                if build_stdout:
                    with st.expander("Build Output"):
                        st.code(build_stdout)
                return
        
        # Step 5: Deploy to CDF
        st.subheader("🚀 Deploying to CDF")
        
        # Check if CDF client is available
        if not CLIENT:
            st.warning("⚠️ CDF client not available. Make sure you have:")
            st.markdown("""
            - Set up your environment variables (CDF_PROJECT, CDF_CLUSTER, etc.)
            - Or run `source cdfenv.sh` if you have a local environment file
            - Or configure authentication in your CDF project
            """)
            
            if st.button("🔄 Retry with CDF Client"):
                initialize_cdf_client()
                if CLIENT:
                    st.success("✅ CDF client initialized successfully")
                    st.rerun()
                else:
                    st.error("❌ Still unable to initialize CDF client")
                    return
        
        with st.spinner("Running cdf deploy..."):
            deploy_success, deploy_stdout, deploy_stderr = run_cognite_toolkit_deploy(extracted_path)
            
            if deploy_success:
                st.success("🎉 Deployment completed successfully!")
                if st.session_state['debug_mode'] and deploy_stdout:
                    with st.expander("Deploy Output"):
                        st.code(deploy_stdout)
            else:
                st.error("❌ Deployment failed")
                if deploy_stderr:
                    st.error(f"Error: {deploy_stderr}")
                if deploy_stdout:
                    with st.expander("Deploy Output"):
                        st.code(deploy_stdout)
        
        # Cleanup
        try:
            os.unlink(zip_path)  # Delete the ZIP file
            if st.session_state['debug_mode']:
                st.info(f"Cleaned up temporary files")
        except:
            pass
    
    # Information section
    st.markdown("---")
    st.header("ℹ️ Information")
    
    with st.expander("How to use this tool"):
        st.markdown("""
        This tool allows you to:
        
        1. **Download** any GitHub repository (public or private) as a ZIP file
        2. **Extract** the files to a temporary directory
        3. **Build** the project using `cdf build`
        4. **Deploy** to CDF using `cdf deploy`
        
        **Two Access Modes:**
        
        🌐 **Public Repository Mode** (Recommended for most users):
        - No GitHub account required
        - No authentication needed
        - Works with any public repository
        - Perfect for trying out Cognite samples and public projects
        
        🔐 **Private Repository Mode**:
        - Requires GitHub account and authentication
        - Access to private repositories you own or have access to
        - Use the login button in the sidebar to authenticate
        
        **Requirements:**
        - The repository should contain Cognite toolkit configuration files
        - You need to have the Cognite toolkit (`cdf`) installed
        - CDF authentication must be configured
        
        **Popular Public Repositories to Try:**
        - `cognitedata/cognite-samples` - Official Cognite samples
        - `cognitedata/cog-demos` - Cognite demo projects
        - Any other public repository with Cognite configuration
        """)
    
    with st.expander("GitHub OAuth Setup"):
        st.markdown("""
        To enable private repository access, you need to set up GitHub OAuth:
        
        1. **Create a GitHub OAuth App:**
           - Go to GitHub → Settings → Developer settings → OAuth Apps
           - Click "New OAuth App"
           - Set Authorization callback URL to: `http://localhost:8501`
        
        2. **Set Environment Variables:**
           ```bash
           export GITHUB_CLIENT_ID=your_client_id
           export GITHUB_CLIENT_SECRET=your_client_secret
           export GITHUB_REDIRECT_URI=http://localhost:8501
           ```
        
        3. **Required Scopes:**
           - `repo` (Full control of private repositories)
        """)
    
    with st.expander("Troubleshooting"):
        st.markdown("""
        **Common issues:**
        
        - **"Repository not found"**: Check repository name and owner
        - **"Access denied"**: Authenticate with GitHub for private repos
        - **"Cognite toolkit not found"**: Install with `pip install cognite-toolkit`
        - **"CDF client not available"**: Set up environment variables or authentication
        - **"Build failed"**: Check if the repository contains valid Cognite configuration
        - **"Deploy failed"**: Verify CDF project permissions and configuration
        
        **Environment setup:**
        ```bash
        # Option 1: Use environment file
        source cdfenv.sh
        
        # Option 2: Set environment variables
        export CDF_PROJECT=your-project
        export CDF_CLUSTER=your-cluster
        export IDP_CLIENT_ID=your-client-id
        export IDP_CLIENT_SECRET=your-client-secret
        ```
        """)

if __name__ == "__main__":
    main()