import streamlit as st

# Version tracking
VERSION = "2025.10.06.v1"

# Set page config FIRST
st.set_page_config(
    page_title=f"CDF Package Deployer v{VERSION}",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

import zipfile
import io
import os
import time
import traceback
from typing import Dict, List, Optional
from cognite.client import CogniteClient
from dotenv import load_dotenv

# --- Env file loading ---
ENV_FILE_PATH = os.path.expanduser('~/envs/.env.bluefield.cog-bgfast.bgfast')

def load_env_from_file() -> None:
    try:
        if os.path.exists(ENV_FILE_PATH):
            load_dotenv(ENV_FILE_PATH, override=True)
    except:
        pass

load_env_from_file()

# --- Session State Initialization ---
if 'mini_zips_loaded' not in st.session_state:
    st.session_state['mini_zips_loaded'] = False
if 'all_configs' not in st.session_state:
    st.session_state['all_configs'] = []
if 'selected_config' not in st.session_state:
    st.session_state['selected_config'] = None

# --- CDF Client Initialization ---
@st.cache_resource
def get_cdf_client() -> Optional[CogniteClient]:
    """Initialize and cache CogniteClient"""
    try:
        return CogniteClient()
    except:
        try:
            from cognite.client import ClientConfig
            from cognite.client.credentials import OAuthClientCredentials
            
            config = ClientConfig(
                client_name="cdf-package-deployer",
                base_url=f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com",
                project=os.environ['CDF_PROJECT'],
                credentials=OAuthClientCredentials(
                    token_url=os.environ['IDP_TOKEN_URL'],
                    client_id=os.environ['IDP_CLIENT_ID'],
                    client_secret=os.environ['IDP_CLIENT_SECRET'],
                    scopes=[f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com/.default"]
                )
            )
            return CogniteClient(config)
        except:
            return None

# --- Mini Zip Functions ---
def download_all_mini_zips(client: CogniteClient) -> List[Dict]:
    """
    Download all mini zips from CDF and extract config information.
    
    ═══════════════════════════════════════════════════════════════════════════════
    TROUBLESHOOTING HISTORY (October 5, 2025)
    ═══════════════════════════════════════════════════════════════════════════════
    
    INITIAL PROBLEM:
    ----------------
    Files uploaded via toolkit to app-packages space were not being found by Streamlit.
    App showed "Found 0 configurations" even though files existed in CDF.
    
    SCENARIO 1: Case Sensitivity in Filename Parsing
    --------------------------------------------------
    SYMPTOM: cognite-quickstart-main-mini.zip showing "Found 0 configurations"
    HYPOTHESIS: Files named README.xyz.md (uppercase) not being detected
    ATTEMPT: Modified extract_configs_from_mini_zip() to handle both uppercase and lowercase
    CODE CHANGE: basename_lower = basename.lower() before pattern matching
    RESULT: ❌ FAILED - Still found 0 configurations
    REASON: Actual issue was files not being found at all, not parsing problem
    
    SCENARIO 2: Streamlit Cache Issue
    ----------------------------------
    SYMPTOM: Old file list being shown after redeployment
    HYPOTHESIS: st.session_state caching old mini zip list
    ATTEMPT: Added "Reload Mini Zips" button to clear cache
    CODE CHANGE: Clear session_state on button click
    RESULT: ❌ FAILED - Still only found 1-2 mini zips instead of 3
    REASON: Not a cache issue - files genuinely not being found by query
    
    SCENARIO 3: Duplicate Files with uploaded=False
    ------------------------------------------------
    SYMPTOM: Two cognite-samples-main-mini.zip files, one with uploaded: False
    HYPOTHESIS: Old failed uploads causing errors
    ATTEMPT: Created transformation to delete files where uploaded = false
    CODE CHANGE: SQL transformation with DELETE action on CogniteFile view
    SQL: SELECT externalId FROM cdf_data_models("cdf_cdm", "CogniteCore", "v1", "CogniteFile") WHERE uploaded = false
    RESULT: ✅ PARTIAL SUCCESS - Removed duplicates but still missing files
    REASON: Duplicates were a symptom, not the root cause
    
    SCENARIO 4: Files API vs Data Modeling API Mismatch
    ----------------------------------------------------
    SYMPTOM: Files show "Is uploaded: True" in CDF UI but uploaded: False in data model
    HYPOTHESIS: Data model properties not synced with Files API
    ATTEMPT 4A: Add uploaded: true to app-packages.CogniteFile.yaml template
    CODE CHANGE: Added "uploaded: true" property to YAML
    RESULT: ❌ FAILED - Property is read-only, set by system
    
    ATTEMPT 4B: Query Data Modeling API instead of Files API
    CODE CHANGE: 
        instances = client.data_modeling.instances.list(
            instance_type="node",
            sources=[{"source": {"space": "cdf_cdm", "externalId": "CogniteFile", "version": "v1", "type": "view"}}],
            space="app-packages",
            limit=1000
        )
    RESULT: ✅ Found all 3 mini zips in data model!
    BUT: ❌ FAILED to download - "Invalid id, expected int, got <class 'str'>"
    REASON: Data model returns external_id (string), Files API needs numeric id
    
    SCENARIO 5: Use external_id Parameter for Download
    ---------------------------------------------------
    SYMPTOM: TypeError when passing string external_id as 'id' parameter
    HYPOTHESIS: Need to use external_id parameter instead of id parameter
    ATTEMPT: Changed client.files.download_bytes(id=file_id) to external_id=file_id
    CODE CHANGE: content = client.files.download_bytes(external_id=file_id)
    RESULT: ❌ FAILED - "Files ids not found: cognite-library-pattern-mode-beta-mini.zip"
    ERROR: CogniteAPIError 400 - Missing: [{'externalId': 'cognite-library-pattern-mode-beta-mini.zip'}]
    REASON: Files don't exist in Files API with those external IDs!
    
    SCENARIO 6: Skip uploaded=False Files from Data Model
    ------------------------------------------------------
    SYMPTOM: All files in data model show uploaded: False
    HYPOTHESIS: Only try to download files with uploaded: True
    ATTEMPT: Filter files where uploaded == True before downloading
    CODE CHANGE: if not uploaded: st.warning(); continue
    RESULT: ❌ FAILED - Skipped ALL files (all showed uploaded: False)
    REASON: Data model 'uploaded' property not reliable/synced
    
    SCENARIO 7: Files API Returns uploaded=False Files
    ---------------------------------------------------
    SYMPTOM: Files API returns file with uploaded: False, download fails with 400
    ERROR: "Files not uploaded, ids: 2197850608780297"
    HYPOTHESIS: Files API includes metadata for files that were never actually uploaded
    ATTEMPT: Filter out files where uploaded == False from Files API results
    CODE CHANGE: mini_zips = [f for f in all_files if f.name.endswith("-mini.zip") and f.uploaded]
    RESULT: ✅ SUCCESS - Only downloads files that have actual content
    REASON: Files API 'uploaded' property IS reliable (unlike data model property)
    
    KEY INSIGHT:
    - Files API 'uploaded' property = RELIABLE (actual file upload status)
    - Data Model 'uploaded' property = UNRELIABLE (not synced)
    - Must filter Files API results by uploaded == True
    
    SCENARIO 8: Missing DataSet Configuration
    ------------------------------------------
    SYMPTOM: Toolkit creates data model instances but uploaded: False in Files API
    ROOT CAUSE: Module missing data_sets/ directory
    DISCOVERY: Compared with working valhall_dm module structure
    FIX: Created data_sets/app-packages-dataset.DataSet.yaml
    RESULT: ❌ FAILED - Still got errors on deploy
    REASON: Led to Scenario 9...
    
    SCENARIO 9: dataSetExternalId Not Supported in CogniteFile View
    ----------------------------------------------------------------
    SYMPTOM: Deploy error "Property 'dataSetExternalId' does not exist in view 'cdf_cdm:CogniteFile/v1'"
    ERROR CODE: 400 | ResourceCreationError
    HYPOTHESIS: CogniteFile.yaml needs dataSetExternalId property
    ATTEMPT: Added dataSetExternalId: app-packages-dataset to CogniteFile.yaml
    RESULT: ❌ FAILED - Property not supported by CogniteFile view schema
    DISCOVERY: Checked working examples (valhall_dm, robot_garden)
      - ✅ They have data_sets/ directory with DataSet.yaml
      - ✅ They have space definitions
      - ❌ They DO NOT have dataSetExternalId in CogniteFile.yaml
    FIX: Removed dataSetExternalId from CogniteFile.yaml
    RESULT: ✅ SUCCESS - Files upload properly
    REASON: CogniteFile view schema doesn't include dataSetExternalId property
    
    CRITICAL LESSON:
    - CogniteFile.yaml should ONLY have: space, externalId, name, mimeType
    - DataSet is defined separately but NOT referenced in file template
    - Module MUST have data_sets/ directory with DataSet.yaml
    - Space definition lives in separate module (app-packages-dm)
    - The DataSet provides governance but isn't a property of the file instance
    
    ═══════════════════════════════════════════════════════════════════════════════
    ROOT CAUSE ANALYSIS
    ═══════════════════════════════════════════════════════════════════════════════
    
    DISCOVERY:
    - Files uploaded to 'app-packages' space via toolkit CREATE data model instances
    - Data model instances have external_id matching filename
    - BUT: These files are NOT accessible via Files API using those external IDs
    - Files API returns 400 "Files ids not found" for the data model external IDs
    - The 'uploaded' property in data model is NOT synced with actual file upload status
    - Data model shows uploaded: False even when files are successfully uploaded
    
    CONCLUSION:
    - Files API and Data Modeling API are NOT properly synced for files in spaces
    - Data model instances are metadata only, not linked to actual file storage
    - Files uploaded to spaces may not be queryable via standard Files API
    
    ═══════════════════════════════════════════════════════════════════════════════
    WORKING SOLUTION (DO NOT CHANGE!)
    ═══════════════════════════════════════════════════════════════════════════════
    
    METHOD: Use Files API (client.files.list()) to find files
    STEPS:
    1. Query all files with client.files.list(limit=1000)
    2. Filter by name ending with "-mini.zip"
    3. Use the numeric 'id' property from Files API (NOT external_id)
    4. Download using client.files.download_bytes(id=file.id)
    
    WHY THIS WORKS:
    - Files API returns actual uploaded files with numeric IDs
    - These IDs work reliably for downloading file content
    - No dependency on data model sync status
    
    TESTED: October 5, 2025 - Successfully finds and downloads all mini zips
    
    ✅ NOW USING DATA MODELING API (October 6, 2025)
    ✅ This is the correct approach for files uploaded to spaces
    """
    try:
        with st.spinner("📥 Searching for mini zips in CDF Data Modeling API..."):
            # Use Data Modeling API to query CogniteFile instances in app-packages space
            from cognite.client.data_classes.data_modeling.ids import ViewId
            
            view_id = ViewId(space="cdf_cdm", external_id="CogniteFile", version="v1")
            
            instances = client.data_modeling.instances.list(
                instance_type="node",
                sources=view_id,
                space="app-packages",
                limit=1000
            )
            
            # Filter for mini zips by name and isUploaded status
            mini_zips = []
            for instance in instances:
                props = instance.properties.get(view_id, {})
                name = props.get("name", "")
                is_uploaded = props.get("isUploaded", False)
                
                if name and name.endswith("-mini.zip") and is_uploaded:
                    mini_zips.append({
                        "name": name,
                        "instance": instance,
                        "external_id": instance.external_id,
                        "space": instance.space
                    })
            
            st.info(f"🔍 Found {len(mini_zips)} mini zip files in CDF")
            
            # Debug: Show all found mini zips
            with st.expander("🔍 Debug: Mini zip files found", expanded=True):
                for mz in mini_zips:
                    st.text(f"  • {mz['name']} (space: {mz['space']}, externalId: {mz['external_id']})")
            
            if not mini_zips:
                st.warning("⚠️ No mini zips found in app-packages space")
                st.info("Showing all instances for debugging:")
                for instance in instances[:10]:  # Show first 10
                    props = instance.properties.get(view_id, {})
                    name = props.get("name", "N/A")
                    is_uploaded = props.get("isUploaded", False)
                    uploaded_status = "✅" if is_uploaded else "❌"
                    st.text(f"  {uploaded_status} {name} (isUploaded: {is_uploaded})")
                return []
            
            all_configs = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total = len(mini_zips)
            
            for idx, mz in enumerate(mini_zips):
                file_name = mz['name']
                status_text.text(f"📦 Processing {idx+1}/{total}: {file_name}")
                progress_bar.progress((idx + 1) / total)
                
                try:
                    # Download using instance_id (NodeId)
                    from cognite.client.data_classes.data_modeling.ids import NodeId
                    instance_id = NodeId(space=mz['space'], external_id=mz['external_id'])
                    
                    st.write(f"  📥 Downloading {file_name} (instance: {mz['space']}/{mz['external_id']})...")
                    content = client.files.download_bytes(instance_id=instance_id)
                    st.write(f"  ✅ Downloaded {len(content)} bytes")
                    
                    st.write(f"  🔍 Extracting configs from {file_name}...")
                    configs = extract_configs_from_mini_zip(content, file_name)
                    all_configs.extend(configs)
                    st.write(f"  ✅ {file_name}: Found {len(configs)} configurations")
                except Exception as e:
                    st.error(f"  ❌ Failed to process {file_name}: {e}")
                    st.code(traceback.format_exc())
            
            progress_bar.empty()
            status_text.empty()
            
            return all_configs
    except Exception as e:
        st.error(f"❌ Failed to download mini zips: {e}")
        st.code(traceback.format_exc())
        return []

def extract_configs_from_mini_zip(zip_content: bytes, zip_name: str) -> List[Dict]:
    """Extract configuration information from a mini zip"""
    configs = []
    package_name = zip_name.replace("-mini.zip", "")
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            all_files = zip_file.namelist()
            readme_files = {}
            for file_name in all_files:
                # Get just the filename (not the path)
                basename = file_name.split('/')[-1]
                basename_lower = basename.lower()
                
                # Check if it's a config-specific README (readme.xyz.md or README.xyz.md)
                # Pattern: readme.{config}.md or README.{config}.md
                if basename_lower.startswith('readme.') and basename_lower.endswith('.md'):
                    # Parse config name from filename
                    parts = basename_lower.split('.')
                    if len(parts) >= 3:  # readme, config, md (or readme, part1, part2, ..., md)
                        config_name = '.'.join(parts[1:-1])  # Everything between readme and .md
                        if config_name and config_name not in readme_files:
                            # Read the content
                            content = zip_file.read(file_name).decode('utf-8', errors='ignore')
                            readme_files[config_name] = {
                                'file_path': file_name,
                                'content': content
                            }
            
            # Create config entries
            for config_name, readme_info in readme_files.items():
                configs.append({
                    'package': package_name,
                    'config': config_name,
                    'full_zip': f"{package_name}.zip",
                    'config_file': f"config.{config_name}.yaml",
                    'readme_content': readme_info['content'],
                    'readme_path': readme_info['file_path']
                })
    except Exception as e:
        st.error(f"⚠️ Failed to extract configs from {zip_name}: {e}")
        st.code(traceback.format_exc())
    
    return configs

def call_deploy_function(client: CogniteClient, config: Dict):
    """Call CDF Function to deploy the selected configuration"""
    function_name = "test-toolkit-function"
    
    st.subheader("🚀 Deploying Configuration")
    
    # Prepare function data
    function_data = {
        "zip_name": config['full_zip'],
        "config_name": config['config']
    }
    
    # Add environment variables if uploaded
    env_vars = st.session_state.get('env_vars', {})
    if env_vars:
        function_data["env_vars"] = env_vars
        st.info(f"📋 Including {len(env_vars)} environment variables in function call")
    
    st.info(f"""
**Calling Function**: `{function_name}`
- **Package**: `{config['package']}`
- **Configuration**: `{config['config']}`
- **Full Zip**: `{config['full_zip']}`
- **Config File**: `{config['config_file']}`
    """)
    
    try:
        # Call the function
        with st.spinner("📞 Calling CDF Function..."):
            call_result = client.functions.call(
                external_id=function_name,
                data=function_data
            )
        
        st.success(f"✅ Function called successfully! Call ID: {call_result.id}")
        
        # Monitor function execution
        st.subheader("📋 Function Execution Logs")
        
        logs_container = st.container()
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        all_logs = []
        last_log_timestamp = None
        max_wait = 300  # 5 minutes
        poll_interval = 2
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            # Update progress
            progress = min(elapsed / max_wait, 0.95)
            progress_bar.progress(progress)
            
            # Get function status
            call_status = client.functions.calls.retrieve(
                function_external_id=function_name,
                call_id=call_result.id
            )
            
            status_placeholder.text(f"⏳ Status: {call_status.status} (elapsed: {elapsed}s)")
            
            # Get logs
            try:
                logs = client.functions.calls.get_logs(
                    function_external_id=function_name,
                    call_id=call_result.id
                )
                
                logs_list = list(logs) if logs else []
                new_logs = []
                
                for log in logs_list:
                    if last_log_timestamp is None:
                        new_logs.append(log)
                    else:
                        try:
                            log_ts = log.timestamp
                            if isinstance(log_ts, str):
                                from dateutil import parser
                                log_ts = parser.parse(log_ts).timestamp() * 1000
                            if log_ts > last_log_timestamp:
                                new_logs.append(log)
                        except:
                            new_logs.append(log)
                
                if new_logs:
                    try:
                        last_ts = new_logs[-1].timestamp
                        if isinstance(last_ts, str):
                            from dateutil import parser
                            last_log_timestamp = parser.parse(last_ts).timestamp() * 1000
                        else:
                            last_log_timestamp = last_ts
                    except:
                        pass
                
                if new_logs:
                    with logs_container:
                        for log in new_logs:
                            log_msg = log.message if hasattr(log, 'message') else str(log)
                            if hasattr(log, 'timestamp') and log.timestamp:
                                st.text(f"[{log.timestamp}] {log_msg}")
                            else:
                                st.text(log_msg)
                            all_logs.append(log_msg)
            except:
                pass
            
            # Check if completed
            if call_status.status == "Completed":
                progress_bar.progress(1.0)
                status_placeholder.text("✅ Function completed!")
                
                # Get final logs
                try:
                    logs = client.functions.calls.get_logs(
                        function_external_id=function_name,
                        call_id=call_result.id
                    )
                    logs_list = list(logs) if logs else []
                    final_new_logs = []
                    for log in logs_list:
                        if last_log_timestamp is None or log.timestamp > last_log_timestamp:
                            final_new_logs.append(log)
                    
                    if final_new_logs:
                        with logs_container:
                            for log in final_new_logs:
                                log_msg = log.message if hasattr(log, 'message') else str(log)
                                if hasattr(log, 'timestamp') and log.timestamp:
                                    st.text(f"[{log.timestamp}] {log_msg}")
                                else:
                                    st.text(log_msg)
                                all_logs.append(log_msg)
                except:
                    pass
                
                # Get the result
                result = client.functions.calls.retrieve(
                    function_external_id=function_name,
                    call_id=call_result.id
                )
                
                st.subheader("🎉 Function Results")
                
                response_data = None
                if hasattr(result, 'get_response'):
                    try:
                        response_data = result.get_response()
                    except Exception as e:
                        st.error(f"❌ Error calling get_response(): {e}")
                elif hasattr(result, 'response'):
                    response_data = result.response
                
                if response_data:
                    deployment = response_data.get('deployment', {})
                    summary = response_data.get('summary', {})
                    
                    # Show deployment info
                    if deployment:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**Project**: `{deployment.get('project', 'N/A')}`")
                        with col2:
                            st.info(f"**Cluster**: `{deployment.get('cluster', 'N/A')}`")
                        
                        st.success(f"📄 **Config**: `{deployment.get('config_file', 'N/A')}`")
                    
                    # Build Section
                    if 'build' in deployment:
                        with st.expander("🏗️ Build Output", expanded=True):
                            build = deployment['build']
                            if build.get('success'):
                                st.success(f"✅ Build completed successfully in {build.get('duration', 0)}s")
                            else:
                                st.error(f"❌ Build failed")
                            st.code(build.get('stdout', ''), language='text')
                    
                    # Dry-run Section
                    if 'dry_run' in deployment:
                        with st.expander("🔍 Dry-run Output", expanded=True):
                            dry_run = deployment['dry_run']
                            if dry_run.get('success'):
                                st.success(f"✅ Dry-run completed successfully in {dry_run.get('duration', 0)}s")
                            else:
                                st.error(f"❌ Dry-run failed")
                            st.code(dry_run.get('stdout', ''), language='text')
                    
                    # Deploy Section
                    if 'deploy' in deployment:
                        with st.expander("🚀 Deploy Output", expanded=True):
                            deploy = deployment['deploy']
                            if deploy.get('skipped'):
                                st.warning(f"⏭️ Deploy skipped: {deploy.get('reason', '')}")
                            elif deploy.get('success'):
                                st.success(f"✅ Deployment completed successfully in {deploy.get('duration', 0)}s")
                                st.balloons()
                            else:
                                st.error(f"❌ Deploy failed")
                            
                            if 'stdout' in deploy:
                                st.code(deploy.get('stdout', ''), language='text')
                            if deploy.get('stderr'):
                                st.error("Error output:")
                                st.code(deploy.get('stderr', ''), language='text')
                    
                    # Summary Section
                    st.subheader("📊 Deployment Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if summary.get('build_successful'):
                            st.metric("Build", "✅ SUCCESS")
                        else:
                            st.metric("Build", "❌ FAILED")
                    
                    with col2:
                        if summary.get('dry_run_successful'):
                            st.metric("Dry-run", "✅ SUCCESS")
                        else:
                            st.metric("Dry-run", "❌ FAILED")
                    
                    with col3:
                        if summary.get('deploy_successful'):
                            st.metric("Deploy", "✅ SUCCESS")
                        elif summary.get('deploy_skipped'):
                            st.metric("Deploy", "⏭️ SKIPPED")
                        else:
                            st.metric("Deploy", "❌ FAILED")
                    
                    # Full response in expander
                    with st.expander("🔍 Full Response Data"):
                        st.json(response_data)
                else:
                    st.error("❌ No response data received")
                
                break
                
            elif call_status.status == "Failed":
                st.error(f"❌ Function failed: {call_status}")
                st.warning("⚠️ Check the logs above for error details")
                break
        
        if elapsed >= max_wait:
            st.warning(f"⏰ Function execution timeout after {max_wait}s")
            
    except Exception as e:
        st.error(f"❌ Failed to call function: {e}")
        st.code(traceback.format_exc())

# --- Main Application ---
def main():
    st.title("📦 CDF Package Deployer")
    st.markdown("**Mini Zip Workflow** - Browse and deploy configurations from CDF")
    st.caption(f"Version {VERSION} - Automatic mini zip download and configuration selection")
    
    # Initialize CDF client
    client = get_cdf_client()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Connection Info")
        if client:
            try:
                st.success(f"✅ Connected to: {client.config.project}")
                st.caption(f"Cluster: {client.config.base_url}")
            except:
                st.warning("⚠️ Connection info unavailable")
        else:
            st.error("❌ Not connected to CDF")
            st.stop()
        
        st.divider()
        
        if st.button("🔄 Reload Mini Zips"):
            st.session_state['mini_zips_loaded'] = False
            st.session_state['all_configs'] = []
            st.session_state['selected_config'] = None
            st.rerun()
    
    # Auto-load mini zips on first run
    if not st.session_state['mini_zips_loaded']:
        configs = download_all_mini_zips(client)
        st.session_state['all_configs'] = configs
        st.session_state['mini_zips_loaded'] = True
        
        if configs:
            st.success(f"✅ Loaded {len(configs)} configurations from {len(set(c['package'] for c in configs))} packages")
        else:
            st.error("❌ No configurations found. Please check that mini zips are uploaded to CDF.")
            st.stop()
    
    # Display configuration selection
    if st.session_state['all_configs']:
        st.header("⚙️ Select Configuration")
        
        # Create formatted list
        config_options = []
        config_map = {}
        
        for config in st.session_state['all_configs']:
            label = f"{config['package']} → {config['config']}"
            config_options.append(label)
            config_map[label] = config
        
        # Select configuration
        selected_label = st.selectbox(
            "Choose a package and configuration to deploy:",
            options=config_options,
            help="Select from all available configurations"
        )
        
        if selected_label:
            selected_config = config_map[selected_label]
            st.session_state['selected_config'] = selected_config
            
            # Environment file upload
            st.subheader("🔐 Environment Configuration (Optional)")
            uploaded_env_file = st.file_uploader(
                "Upload .env file (optional - for IDP credentials)",
                type=None,
                help="Upload a .env file with IDP_CLIENT_ID, IDP_CLIENT_SECRET, IDP_TENANT_ID for hosted extractors"
            )
            
            env_vars_dict = {}
            if uploaded_env_file is not None:
                env_content = str(uploaded_env_file.read(), "utf-8")
                st.success(f"✅ Loaded {uploaded_env_file.name}")
                
                # Parse .env file into dict
                for line in env_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars_dict[key.strip()] = value.strip()
                
                st.info(f"📋 Parsed {len(env_vars_dict)} environment variables")
            
            # Store env_vars in session state for function call
            st.session_state['env_vars'] = env_vars_dict
            
            # Deploy button directly below dropdown
            if st.button("🚀 Deploy Configuration", type="primary", use_container_width=True):
                call_deploy_function(client, selected_config)
            
            st.divider()
            
            # Configuration details below
            st.subheader("📋 Configuration Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📦 Package", selected_config['package'])
                st.metric("⚙️ Configuration", selected_config['config'])
            with col2:
                st.metric("📦 Full Zip", selected_config['full_zip'])
                st.metric("📄 Config File", selected_config['config_file'])
            
            # Display README
            st.subheader(f"📖 README: {selected_config['config']}")
            with st.expander("View README Content", expanded=False):
                st.markdown(selected_config['readme_content'])
    else:
        st.error("❌ No configurations available")

if __name__ == "__main__":
    main()