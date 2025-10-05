# Test Toolkit API - Requirements & Features

## Overview
This module provides a Streamlit interface to test and execute Cognite Toolkit operations via Cognite Functions, enabling real toolkit functionality in Streamlit SaaS environments.

## Current Status (v17)

### ✅ Completed Features
1. **Function Execution & Monitoring**
   - Call Cognite Functions with real-time status updates
   - Real-time log streaming (22+ log entries)
   - Progress bar with elapsed time tracking
   - Proper error handling with full stack traces

2. **API Integration**
   - Fixed all Cognite SDK API calls (retrieve, get_logs)
   - Proper parameter usage (function_external_id + call_id)
   - Cached CogniteClient for instant button response

3. **Toolkit Testing**
   - Install cognite-toolkit in Functions environment
   - Verify CLI commands (cdf, cdf build, cdf deploy)
   - Test PATH configuration
   - Confirm toolkit is CLI-based (not Python library)

4. **UI/UX**
   - Clean interface with version tracking
   - Expandable debug sections
   - Comprehensive error messages
   - Response data display with JSON formatting

5. **Documentation**
   - Full trial history (v1-v17) documented in code
   - README.md with architecture and troubleshooting
   - All API fixes documented with version numbers

## Planned Features

### Phase 1: Real Deployment Workflow (NEXT)

#### 1.1 Zip File Integration
**Goal**: Download and use actual project configurations from CDF Files

**Implementation**:
- Download zip file from CDF Files API
  - Hard-coded file: `cognite-quickstart-main.zip`
  - Use external_id or file ID for retrieval
- Extract zip to temporary directory in Functions environment
- Use `config.weather.yaml` as the configuration file

**Reference Code**:
- Source: `/modules/streamlit-github-deployer/streamlit/github-repo-deployer/services/cdf_files_service.py`
- Key functions:
  - `download_zip_from_cdf()` - Downloads file by ID
  - `extract_zip_to_temp_dir()` - Extracts to temp location
  - Uses `client.files.download_bytes(id=file_id)`

**Function Updates Needed**:
```python
def handle(client, data):
    # 1. Download zip from CDF Files
    file_id = get_file_id_by_name(client, "cognite-quickstart-main.zip")
    zip_bytes = client.files.download_bytes(id=file_id)
    
    # 2. Extract to temp directory
    temp_dir = extract_zip(zip_bytes)
    
    # 3. Navigate to extracted directory
    os.chdir(temp_dir)
    
    # 4. Run toolkit commands
    # ... (see below)
```

#### 1.2 Automatic Project Detection
**Goal**: Function automatically determines CDF project name

**Implementation**:
- Use `client.config.project` to get current project
- Set environment variable: `CDF_PROJECT=<project_name>`
- Set environment variable: `CDF_CLUSTER=<cluster_from_base_url>`
- No user input required - fully automatic

```python
# Get project info from client
project = client.config.project
cluster = extract_cluster_from_url(client.config.base_url)

# Set environment variables for toolkit
os.environ['CDF_PROJECT'] = project
os.environ['CDF_CLUSTER'] = cluster
```

#### 1.3 Toolkit Command Execution
**Goal**: Run real toolkit commands with actual configuration

**Commands to Execute**:
1. `cdf build --env=dev` - Build the project
2. `cdf deploy --dry-run --env=dev` - Validate deployment
3. `cdf deploy --env=dev` - Actual deployment (optional, with confirmation)

**Configuration**:
- Use `config.weather.yaml` from zip file
- Create minimal environment config if needed
- Capture all output (stdout, stderr, return codes)

**Output Structure**:
```python
return {
    "success": True/False,
    "project": project_name,
    "cluster": cluster_name,
    "config_file": "config.weather.yaml",
    "commands": {
        "build": {
            "returncode": 0,
            "stdout": "...",
            "stderr": "...",
            "duration": 12.5
        },
        "dry_run": {...},
        "deploy": {...}
    },
    "summary": {
        "build_successful": True,
        "dry_run_successful": True,
        "deploy_successful": True,
        "resources_created": 15,
        "resources_updated": 3
    }
}
```

### Phase 2: User Configuration Selection

#### 2.1 Config File Parameter
- Allow user to specify which config file to use
- Default: `config.weather.yaml`
- Options: List all `config.*.yaml` files found in zip

#### 2.2 Zip File Selection
- Allow user to select which zip file from CDF
- List available zips in app-packages space
- Default: `cognite-quickstart-main.zip`

#### 2.3 Deployment Options
- Checkbox: Run build only
- Checkbox: Run dry-run only  
- Checkbox: Run full deployment
- Checkbox: Include drop operations
- Checkbox: Force update

### Phase 3: Advanced Features

#### 3.1 Multi-Config Deployment
- Deploy multiple configurations in sequence
- Progress tracking for each config
- Rollback on failure

#### 3.2 Deployment History
- Store deployment results in CDF
- Show previous deployments
- Compare configurations

#### 3.3 Validation & Testing
- Pre-deployment validation
- Post-deployment testing
- Resource verification

#### 3.4 Error Recovery
- Automatic retry on transient failures
- Partial deployment recovery
- Detailed error diagnostics

### Phase 4: Production Features

#### 4.1 Authentication & Authorization
- Verify user permissions before deployment
- Audit logging
- Approval workflows

#### 4.2 Scheduling
- Schedule deployments
- Recurring deployments
- Maintenance windows

#### 4.3 Notifications
- Email/Slack notifications on completion
- Error alerts
- Deployment summaries

#### 4.4 Monitoring
- Real-time resource monitoring
- Deployment metrics
- Performance tracking

## Technical Architecture

### Current Architecture
```
Streamlit SaaS (Pyodide)
  ↓ (calls)
Cognite Functions (Full Python)
  ↓ (installs)
cognite-toolkit (CLI)
  ↓ (executes)
cdf build/deploy commands
```

### Planned Architecture (Phase 1)
```
Streamlit SaaS
  ↓ (calls with config selection)
Cognite Functions
  ↓ (downloads)
CDF Files API (zip file)
  ↓ (extracts)
Temp Directory
  ↓ (reads)
config.weather.yaml
  ↓ (executes)
cdf build/deploy
  ↓ (deploys to)
CDF Project (auto-detected)
```

## Implementation Plan

### Step 1: Update Function Handler (Priority 1)
**File**: `modules/test-toolkit-api/functions/test-toolkit-function/handler.py`

**Changes**:
1. Add zip download logic (from cdf_files_service.py)
2. Add zip extraction logic
3. Add project auto-detection
4. Add environment variable setup
5. Add real toolkit command execution
6. Update response structure

**Estimated Effort**: 2-3 hours

### Step 2: Update Streamlit UI (Priority 2)
**File**: `modules/test-toolkit-api/streamlit/test-toolkit-api/main.py`

**Changes**:
1. Update response data display for new structure
2. Add deployment status indicators
3. Show build/deploy results
4. Add error handling for deployment failures

**Estimated Effort**: 1-2 hours

### Step 3: Testing (Priority 3)
1. Test with config.weather.yaml
2. Verify project auto-detection
3. Test build command
4. Test dry-run command
5. Test actual deployment (in dev environment)

**Estimated Effort**: 2-3 hours

### Step 4: Documentation (Priority 4)
1. Update README.md with new features
2. Document configuration requirements
3. Add troubleshooting guide
4. Create user guide

**Estimated Effort**: 1 hour

## Dependencies

### Required CDF Resources
- **File**: `cognite-quickstart-main.zip` in CDF Files
  - Must contain `config.weather.yaml`
  - Must contain `modules/` directory structure
- **Function**: `test-toolkit-function` deployed and accessible
- **Permissions**: Function needs read access to Files API

### Required Environment Variables (Auto-Set)
- `CDF_PROJECT` - Auto-detected from client
- `CDF_CLUSTER` - Auto-detected from client
- `PATH` - Updated to include `/home/.local/bin`

### Python Dependencies (Function)
- `cognite-sdk` - Already installed
- `cognite-toolkit` - Installed by function
- `python-dateutil` - For timestamp parsing

## Success Criteria

### Phase 1 Success Criteria
- ✅ Function downloads zip from CDF Files
- ✅ Function extracts zip to temp directory
- ✅ Function auto-detects project and cluster
- ✅ Function runs `cdf build` successfully
- ✅ Function runs `cdf deploy --dry-run` successfully
- ✅ Function returns detailed results
- ✅ Streamlit displays build/deploy results
- ✅ All logs stream in real-time
- ✅ Errors are clearly reported

## Configuration Management Pattern

### Project Name Injection (CRITICAL)

**Requirement**: All config files must have the real project name injected, not variables.

**Why**: Config files often contain placeholders like:
- `project: ${CDF_PROJECT}`
- `project: {{ CDF_PROJECT }}`
- `project: <change-me>`
- `project: your-project-here`

**Solution**: The function automatically replaces ANY value in the `project:` field with the actual project name from `client.config.project`.

**Implementation**:
```python
# Auto-detect project
project = client.config.project

# Read config file
with open(config_file, 'r') as f:
    lines = f.readlines()

# Replace project line (always at start of line, no indentation)
for i, line in enumerate(lines):
    if line.startswith('project:'):
        lines[i] = f'project: {project}\n'
        break

# Write back
with open(config_file, 'w') as f:
    f.writelines(lines)
```

**Result**: 
- Before: `project: ${CDF_PROJECT}`
- After: `project: bluefield-test`

**Benefits**:
- ✅ Works against any CDF project
- ✅ No manual configuration needed
- ✅ Portable across environments
- ✅ Handles all placeholder patterns

**Pattern for Future**: This same approach will be used for ALL config files we work with.

## Open Questions (Deferred)

These questions are documented but not being addressed in Phase 1:

1. **Deployment Safety**: Should we require explicit user confirmation for actual deployment (not dry-run)?
2. **Config Validation**: Should we validate config files before deployment?
3. **Resource Limits**: What timeout should we set for deployment operations?
4. **Error Handling**: How should we handle partial deployments?
5. **Logging**: Should we store deployment logs in CDF for audit trail?

## Version History

- **v1-v2**: Initial trials (Pyodide incompatibility discovered)
- **v3-v6**: Button feedback optimization
- **v7-v11**: API call fixes
- **v12-v14**: Log display fixes
- **v15**: Response data debugging
- **v16**: Fixed get_response() method
- **v17**: Display full response data
- **v18+**: Real deployment workflow (planned)

## References

### Code References
- Zip download: `modules/streamlit-github-deployer/streamlit/github-repo-deployer/services/cdf_files_service.py`
- Extraction logic: Same file, `extract_zip_to_temp_dir()`
- Client initialization: `modules/streamlit-github-deployer/streamlit/github-repo-deployer/main.py`

### Documentation
- Cognite Toolkit: https://docs.cognite.com/cdf/deploy/cdf_toolkit/
- Cognite SDK: https://cognite-sdk-python.readthedocs-hosted.com/
- Functions API: https://docs.cognite.com/api/v1/#tag/Functions
