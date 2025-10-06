## GitHub Repo Deployer - UI/Flow Requirements

This document baselines the expected behavior and structure of the Streamlit app so we can refactor to a predictable, non-flickering workflow.

---

## 🆕 NEW MINI ZIP WORKFLOW (Current Implementation)

**Architecture Overview:**
1. **Download Packages**: `download_packages.py` creates TWO zips per repo:
   - Full zip: `{name}.zip` (complete repo, several MB)
   - Mini zip: `{name}-mini.zip` (README files only, 10-50KB)

2. **Streamlit Flow** (3 simple steps):
   - **Step 1**: Download all mini zips → present package/config options
   - **Step 2**: Call CDF Function with `(zip_name, config_name)`
   - **Step 3**: Display deployment results

3. **CDF Function**: Does the heavy lifting:
   - Downloads full zip from CDF Files
   - Extracts and runs `cdf build/deploy`
   - Returns results to Streamlit

**Key Benefits:**
- ⚡ Fast initial load (download mini zips only)
- 🎯 Simple user flow (select package + config → deploy)
- 🔧 Function handles complexity (build/deploy logic)
- 📦 No large downloads until deployment
- ✅ Testing in stepwise manner before integration

**Quick Reference Table:**

| Step | User Action | Streamlit Action | Result |
|------|-------------|------------------|--------|
| 1 | Opens app | Download all `*-mini.zip` from CDF | Shows package/config options |
| 1 | Selects package & config | Store selections in session state | Enable Step 2 |
| 2 | Clicks "Deploy" | Call CDF Function(`zip_name`, `config_name`) | Show spinner |
| 2 | Waits 2-5 min | Poll/wait for function completion | Function deploys |
| 3 | Views results | Display function output/logs | Success or error shown |
| 3 | Optional | Click "Deploy Another" | Return to Step 1 |

**Function Parameters:**
```python
# Streamlit passes to CDF Function:
{
    "zip_name": "cognite-quickstart-main.zip",  # Full zip name
    "config_name": "weather"                     # Config to deploy
}

# Function returns:
{
    "success": True,
    "output": "Build complete...\nDeploy complete...",
    "build_summary": {...},
    "deploy_summary": {...}
}
```

**Data Flow Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│ SETUP: download_packages.py                                    │
├─────────────────────────────────────────────────────────────────┤
│ GitHub Repo → Download → Create 2 zips:                        │
│   • repo-name.zip (full, ~5MB)                                  │
│   • repo-name-mini.zip (READMEs only, ~20KB)                    │
│ → Upload both to CDF Files                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STREAMLIT: Step 1                                               │
├─────────────────────────────────────────────────────────────────┤
│ 1. List *-mini.zip from CDF Files                               │
│ 2. Download all mini zips (~20KB each = fast!)                  │
│ 3. Extract README files                                         │
│ 4. Parse config options (all, weather, etc.)                    │
│ 5. Display: Package radio + Config radio                        │
│ 6. User selects → Store in session_state                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STREAMLIT: Step 2                                               │
├─────────────────────────────────────────────────────────────────┤
│ User clicks "Deploy Configuration"                              │
│ → Call CDF Function with:                                       │
│    • zip_name: "repo-name.zip"                                  │
│    • config_name: "weather"                                     │
│ → Show spinner while waiting                                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ CDF FUNCTION: Deployment                                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Download full zip from CDF Files (~5MB)                      │
│ 2. Extract to /tmp/                                             │
│ 3. Run: cdf build --env weather                                 │
│ 4. Run: cdf deploy --env weather                                │
│ 5. Capture output and results                                   │
│ 6. Return: {success, output, summaries}                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STREAMLIT: Step 3                                               │
├─────────────────────────────────────────────────────────────────┤
│ Display function results:                                       │
│   ✅ Success message or ❌ Error                                │
│   📊 Deployment summary                                         │
│   📝 Full logs in expander                                      │
│   🔄 "Deploy Another" button                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1) Global Rules - MINI ZIP WORKFLOW

- There is a single source of truth for the current step: `st.session_state['workflow_step']` in {1..3}.
- Step tabs are clickable navigation:
  - Clicking a completed step moves to that step.
  - Clicking the current step does nothing.
  - Future steps are disabled until prerequisites are satisfied.
- Only content for the currently selected step is rendered. No cross-step content should appear.
- State required by later steps is stored in `st.session_state`:
  - `available_packages`: Dict of packages from mini zips with README content
  - `selected_package`: Package name (e.g., "cognite-quickstart-main")
  - `selected_config`: Config name (e.g., "weather")
  - `full_zip_name`: Derived full zip name (e.g., "cognite-quickstart-main.zip")
  - `deployment_result`: Result from CDF Function call
- Use `st.rerun()` only when changing steps or after function completion to show results.

### 2) Steps - NEW MINI ZIP WORKFLOW

**Overview**: Streamlit downloads lightweight mini zips from CDF, presents options to user, then deploys selected configuration by calling a CDF Function with zip name and config name.

1. Step 1: Download Mini Zips & Select Configuration
   - **Environment Configuration**:
     - Load environment variables (from uploaded file or existing connection)
     - Accept ALL file types for environment file uploads (no file type restrictions)
     - Support .env, .txt, .config, or any text file containing KEY=VALUE format
     - Show debug availability but do not request manual inputs
   
   - **Download All Mini Zips from CDF**:
     - Use Cognite SDK to list all files with pattern `*-mini.zip`
     - Download all mini zips (lightweight, typically 10-50KB each)
     - Extract README*.md files from each mini zip
     - Parse config.*.yaml references from README files
     - Store in `st.session_state['available_packages']`
     - Display progress/logging during download
   
   - **Package Selection**:
     - Display radio buttons for each available package (e.g., "cognite-quickstart-main", "cognite-samples-main")
     - For selected package, show README preview in expander
     - Display available configurations from README (e.g., "all", "weather", "neat-basic")
     - User selects: 
       - Package name (from mini zip list)
       - Configuration name (e.g., "weather" → config.weather.yaml)
     - Store selections in `st.session_state['selected_package']` and `st.session_state['selected_config']`
     - When selections made, enable Step 2

2. Step 2: Deploy
   - **Display Selection Summary**:
     - Show selected package name (e.g., "cognite-quickstart-main")
     - Show selected config name (e.g., "weather")
     - Show derived full zip name (e.g., "cognite-quickstart-main.zip")
     - Show derived config file (e.g., "config.weather.yaml")
   
   - **Deploy Button**:
     - Single "Deploy Configuration" button
     - On click, call CDF Function with parameters:
       - `zip_name`: Full zip filename (e.g., "cognite-quickstart-main.zip")
       - `config_name`: Config name (e.g., "weather")
     - Function will:
       - Download full zip from CDF Files
       - Extract to temp directory
       - Run `cdf build --env {config_name}`
       - Run `cdf deploy --env {config_name}`
       - Return results
   
   - **Wait for Completion**:
     - Show spinner/progress indicator
     - Display status: "Deploying configuration..."
     - Function execution may take 2-5 minutes
     - Poll function status or wait for completion
   
   - **Display Results**:
     - Show function output/logs in expandable section
     - Display success/failure status with clear indicators
     - Show deployment summary (resources created/updated/unchanged)
     - If successful, show next steps or "Deploy Another Configuration" option
     - If failed, show error details and troubleshooting suggestions

3. Step 3: Results & Next Actions (Optional)
   - Summary of what was deployed
   - Links to CDF UI resources (if available)
   - "Deploy Another Configuration" button to return to Step 1
   - "View Deployment Logs" expander for full details

**OLD WORKFLOW (GitHub Download)** - DEPRECATED for now:
   - Old Step 1: GitHub repo download via API
   - Old Step 2: Local extraction and config discovery
   - Old Step 3: Local build/deploy via subprocess
   - Note: This workflow may be re-enabled as alternative option in future

### 3) Architecture & File Structure
- **Clean Root Directory**: Only essential files in root:
  - `main.py` - Single entry point for Streamlit app
  - `requirements.txt` - Dependencies
  - `REQUIREMENTS.md` - This documentation
- **Modular Design**:
  - `core/` - Unified business logic (shared between Streamlit and tests)
    - `toolkit_operations.py` - Single source of truth for build/deploy operations
    - `rate_limiter.py` - GitHub API rate limiting protection
    - `cache_manager.py` - Repository caching functionality
    - `state_manager.py` - Centralized state management
    - `error_handler.py` - Comprehensive error handling
  - `services/` - Streamlit-specific services
    - `ui_steps.py` - Step rendering functions
    - `env_loader.py` - Environment file handling
    - `github_service.py` - GitHub API operations
    - `toolkit_service.py` - Streamlit wrapper for toolkit operations
    - `state.py` - Session state management
  - `tests/` - Isolated test harness (not deployed)
    - `saas_simulation_test.py` - Command line test framework
    - `syntax_check.py` - Fast AST-based syntax checker for all Streamlit app Python files
    - `run_tests.py` - Test runner
    - `run.sh` - Test execution script
- **Unified Code**: Both Streamlit app and test framework use the same `core/toolkit_operations.py`
- **Single Source of Truth**: No duplicate code between Streamlit and test harness

### 4) Non-Functional
- Minimize UI flicker: prefer containers and forms; only rerun on step change or long op completion.
- Persist critical state in `st.session_state`; avoid recomputation when navigating back to earlier steps.
- use verbose debug=true during development
- UI stability: changing selections (e.g., Step 2 radio) must not wipe other content

### 5) Acceptance Criteria
- Switching steps shows no content leakage from other steps.
- Uploading environment files (any file type) and downloading/extracting repo occur only in Step 1.
- **File Upload Acceptance:**
  - File uploader accepts ALL file types without restrictions
  - Environment files with any extension (.env, .txt, .config, etc.) are accepted
  - Files are parsed correctly regardless of file extension
- Config selection UI is visible only in Step 2.
- Build logs are confined to Step 3; deploy summary to Step 3; verification to Step 3.
- Tabs at the top reliably navigate between completed steps.
- **Test Framework Acceptance:**
  - Command line test framework passes all tests
  - GitHub API download works in test environment
  - Toolkit build/deploy works with real environment variables
  - SaaS environment simulation matches actual behavior

### 6) Testing & Validation
- **Unified Test Framework**: Command line test framework uses the same `core/toolkit_operations.py` as Streamlit app
- **SaaS Environment Simulation**: Tests must simulate actual SaaS behavior (downloading to temp directories)
- **Real Environment Testing**: Tests must use real .env files from ~/envs/ directory
- **Automated Syntax Check**: `modules/admin/github-repo-deployer/streamlit-shell-tests/syntax_check.py` must pass (no syntax errors in Streamlit app)
- **Comprehensive Test Coverage**:
  - Environment variable loading and validation
  - GitHub API connection and rate limiting
  - Repository download with caching
  - Config file discovery
  - Toolkit build with verbose logging
  - Toolkit deploy with OAuth2 authentication
- **Test Isolation**: All test files isolated in `tests/` folder (not deployed with Streamlit)
- **Success Criteria**: All tests must pass (100% success rate) before deployment to SaaS environment

### 7) Environment Variables
- Must load from ~/envs/.env.bluefield.cog-bgfast.bgfast (same as SaaS)
- Environment variables must be passed to Cognite SDK (not subprocess commands)
- Support for CDF_PROJECT, CDF_CLUSTER, IDP_CLIENT_ID, IDP_CLIENT_SECRET, etc.
- Environment validation before SDK operations
- Use OAuth2 client credentials for CDF authentication in browser environment

### 8) Error Handling & Recovery
- Comprehensive error handling for GitHub API failures
- **Rate Limiting Protection**: All GitHub API calls use rate limiting with retry logic
- **Exponential Backoff**: Automatic retry with increasing delays (1s, 2s, 5s, 10s, 30s)
- **Rate Limit Monitoring**: Real-time rate limit status display in sidebar
- Provide a "Check GitHub API Status" action in the sidebar to surface remaining/limit/reset
- Error recovery mechanisms for Cognite SDK operations
- OAuth2 authentication fallback strategies for browser environment
- Clear error messages with actionable solutions
- Debug mode for troubleshooting
- Graceful degradation when services are unavailable

### 9) Development Process
- **Unified Code Development**: All business logic must be in `core/toolkit_operations.py`
- **No Code Duplication**: Streamlit app and test framework must use the same core functions
- **Test-Driven Development**: All changes must be tested with command line test framework
- **Iterative Testing**: No new test files - iterate on existing `tests/saas_simulation_test.py` until it works
- **Real Environment Testing**: Use real .env files for testing (not mock data)
- **Success Criteria**: Test framework must pass (100% success rate) before any deployment
- **File Structure Maintenance**: Keep root directory clean with only essential files
- **Test Isolation**: Ensure test harness files are isolated in `tests/` folder
 - **Syntax Discipline**:
   - Run `syntax_check.py` before each commit and deployment
   - `st.set_page_config()` must be the first Streamlit call in `main.py` and placed at top-level indentation
   - Avoid circular imports that can cause `StreamlitSetPageConfigMustBeFirstCommandError`
   - Maintain consistent indentation; do not mix tabs/spaces

### 10) Current Implementation Status
- **✅ Unified Code**: `core/toolkit_operations.py` provides single source of truth for build/deploy
- **✅ Clean File Structure**: Root directory contains only essential files
- **✅ Test Framework**: Comprehensive test suite with 100% success rate
- **✅ Rate Limiting**: GitHub API protection with exponential backoff
- **✅ Repository Caching**: Efficient caching to avoid redundant downloads
- **✅ Verbose Logging**: Detailed build and deploy output for transparency
- **✅ SaaS Simulation**: Test framework accurately simulates SaaS environment
- **✅ Environment Variables**: Real .env file loading and validation
- **✅ OAuth2 Authentication**: Browser-compatible authentication for CDF
- **✅ Error Handling**: Comprehensive error handling and recovery mechanisms
 - **✅ Automated Syntax Checks**: `syntax_check.py` enforces clean syntax across app files


Expected output format and level of detail expected for build, dry-run, deploy 
brent.groom@cognitedata.com@MacBookPro:~/p/cognite-quickstart$(show_git_worktree)$ cdf build --env weather
  WARNING: Overriding environment variables with values from .env file...
You acknowledge and agree that the CLI tool may collect usage information, user environment, and crash reports for the purposes of providing services of functions that are relevant to use of the CLI tool and product improvements. To remove this message run 'cdf collect opt-in', or to stop collecting usage information run 'cdf 
collect opt-out'.
WARNING [MEDIUM]: In environment section of config.weather.yaml: 'type' is deprecated, use 'validation-type' instead.
╭──────────────────────────────────────────────────────────────────────────────────────────╮
│ Building project '/Users/brent.groom@cognitedata.com/p/cognite-quickstart':              │
│   - Toolkit Version '0.5.74'                                                             │
│   - Environment name 'weather', validation-type 'dev'.                                   │
│   - Config '/Users/brent.groom@cognitedata.com/p/cognite-quickstart/config.weather.yaml' │
│   - Module directory '/Users/brent.groom@cognitedata.com/p/cognite-quickstart/modules'   │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
INFO: Cleaned existing build directory build.
INFO: Build complete. Files are located in build/
brent.groom@cognitedata.com@MacBookPro:~/p/cognite-quickstart$(show_git_worktree)$ cdf deploy --env=weather --dry-run
  WARNING: Overriding environment variables with values from .env file...
You acknowledge and agree that the CLI tool may collect usage information, user environment, and crash reports for the purposes of providing services of functions that are relevant to use of the CLI tool and product improvements. To remove this message run 'cdf collect opt-in', or to stop collecting usage information run 'cdf 
collect opt-out'.
╭───────────────────────────────────────────────────────────╮
│ Checkingresource files from build directory.              │
│                                                           │
│ Connected to CDF Project 'bgfast' in cluster 'bluefield': │
│ CDF_URL=https://bluefield.cognitedata.com                 │
╰───────────────────────────────────────────────────────────╯
WARNING [HIGH]: Sources will always be considered different, and thus will always be redeployed.
Would deploy 1 hosted extractor sources to CDF...
Would deploy 1 hosted extractor mappings to CDF...
WARNING [HIGH]: Destinations will always be considered different, and thus will always be redeployed.
Would deploy 1 hosted extractor destinations to CDF...
Would deploy 1 transformations to CDF...
Would deploy 1 hosted extractor jobs to CDF...
Would deploy 1 workflows to CDF...
Would deploy 1 workflow versions to CDF...
                                       Summary of Resources Deploy operation:                                        
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┓
┃                       Resource ┃ Would have Created ┃ Would have Deleted ┃ Would have Changed ┃ Untouched ┃ Total ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━┩
│  hosted extractor destinations │                  0 │                  0 │                  1 │         0 │     1 │
│          hosted extractor jobs │                  0 │                  0 │                  0 │         1 │     1 │
│      hosted extractor mappings │                  0 │                  0 │                  0 │         1 │     1 │
│       hosted extractor sources │                  0 │                  0 │                  1 │         0 │     1 │
│                transformations │                  0 │                  0 │                  0 │         1 │     1 │
│              workflow versions │                  0 │                  0 │                  1 │         0 │     1 │
│                      workflows │                  0 │                  0 │                  0 │         1 │     1 │
└────────────────────────────────┴────────────────────┴────────────────────┴────────────────────┴───────────┴───────┘
brent.groom@cognitedata.com@MacBookPro:~/p/cognite-quickstart$(show_git_worktree)$ cdf deploy --env=weather          
  WARNING: Overriding environment variables with values from .env file...
You acknowledge and agree that the CLI tool may collect usage information, user environment, and crash reports for the purposes of providing services of functions that are relevant to use of the CLI tool and product improvements. To remove this message run 'cdf collect opt-in', or to stop collecting usage information run 'cdf 
collect opt-out'.
╭───────────────────────────────────────────────────────────╮
│ Deployingresource files from build directory.             │
│                                                           │
│ Connected to CDF Project 'bgfast' in cluster 'bluefield': │
│ CDF_URL=https://bluefield.cognitedata.com                 │
╰───────────────────────────────────────────────────────────╯
WARNING [HIGH]: Sources will always be considered different, and thus will always be redeployed.
Deploying 1 hosted extractor sources to CDF...
Deploying 1 hosted extractor mappings to CDF...
WARNING [HIGH]: Destinations will always be considered different, and thus will always be redeployed.
Deploying 1 hosted extractor destinations to CDF...
Deploying 1 transformations to CDF...
Deploying 1 hosted extractor jobs to CDF...
Deploying 1 workflows to CDF...
Deploying 1 workflow versions to CDF...
                       Summary of Resources Deploy operation:                       
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┓
┃                       Resource ┃ Created ┃ Deleted ┃ Changed ┃ Unchanged ┃ Total ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━┩
│  hosted extractor destinations │       0 │       0 │       1 │         0 │     1 │
│          hosted extractor jobs │       0 │       0 │       0 │         1 │     1 │
│      hosted extractor mappings │       0 │       0 │       0 │         1 │     1 │
│       hosted extractor sources │       0 │       0 │       1 │         0 │     1 │
│                transformations │       0 │       0 │       0 │         1 │     1 │
│              workflow versions │       0 │       0 │       1 │         0 │     1 │
│                      workflows │       0 │       0 │       0 │         1 │     1 │
└────────────────────────────────┴─────────┴─────────┴─────────┴───────────┴───────┘

## 11. Unified Code Architecture (v1.79+)

### 11.1 Core Principles
- **Single Source of Truth**: All build/deploy logic centralized in `core/toolkit_operations.py`
- **Unified Approach**: Both Streamlit app and test framework use identical core functions
- **Consistent Behavior**: Same verbose logging, error handling, and output format
- **Easier Maintenance**: Changes to core operations affect both environments simultaneously

### 11.2 Architecture Requirements
- **Core Module**: `core/toolkit_operations.py` contains all build/deploy logic
- **Service Layer**: `services/toolkit_service.py` provides Streamlit interface to core functions
- **Test Framework**: `streamlit-shell-tests/saas_simulation_test.py` uses same core functions
- **No Code Duplication**: Build and deploy logic exists in only one place

### 11.3 Implementation Status
- **✅ Build Project**: Uses `core.toolkit_operations.build_project()` in both environments
- **✅ Deploy Project**: Uses `core.toolkit_operations.deploy_project()` in both environments
- **✅ Verbose Logging**: Same detailed output format with Unicode box characters
- **✅ Error Handling**: Consistent error handling and recovery across environments
- **✅ Parameter Passing**: Same function signatures and parameter validation

### 11.4 Code Verification
```python
# Test Framework Usage
from core.toolkit_operations import build_project, deploy_project
success, output, error = build_project(repo_path, env_vars, env_name=env_name, verbose=True, logger=print)
success, output, error = deploy_project(repo_path, env_vars, env_name=env_name, verbose=True, logger=print)

# Streamlit Usage  
from core.toolkit_operations import build_project, deploy_project
success, output, error = build_project(project_path, env_vars, env_name=env_name, verbose=True, logger=st.info)
success, output, error = deploy_project(project_path, env_vars, env_name=env_name, verbose=True, logger=st.info)
```

## 12. Development Guidelines & Best Practices

### 12.1 Code Development Process
- **Test First**: Always test changes with the test framework before deploying
- **Unified Development**: Make changes to `core/toolkit_operations.py` for both environments
- **No Duplication**: Never duplicate build/deploy logic in multiple files
- **Version Tracking**: Increment version number with every change
- **Import Validation**: Test all imports work correctly before deployment

### 12.2 File Structure Maintenance
- **Root Directory**: Only `main.py`, `requirements.txt`, `REQUIREMENTS.md` in root
- **Core Directory**: Contains `toolkit_operations.py` and other core functionality
- **Services Directory**: Contains Streamlit-specific service wrappers
- **Tests Directory**: Located as sibling to `streamlit/` to prevent deployment
- **Clean Deployment**: No `__pycache__`, `.pyc`, or test files in deployment

### 12.3 Error Prevention
- **Circular Imports**: Avoid circular imports by using direct function calls
- **Module Structure**: Ensure all directories have `__init__.py` files
- **Import Paths**: Use relative imports within packages, absolute imports for core modules
- **Dependency Management**: Keep dependencies minimal and well-documented

### 12.4 Testing Requirements
- **Test Framework**: Must pass 100% of tests before deployment
- **SaaS Simulation**: Test framework must accurately simulate SaaS environment
- **Environment Variables**: Use real `.env` files for testing
- **GitHub API**: Test with rate limiting protection and caching
- **Cognite SDK**: Test OAuth2 authentication and CDF connectivity

## 13. Backlog & Future Enhancements

### 13.1 High Priority
- **✅ Unified Code Architecture**: Completed in v1.79
- **✅ Test Framework**: Comprehensive test suite with 100% success rate
- **✅ Verbose Logging**: Detailed output matching `cdf` CLI format
- **✅ Rate Limiting**: GitHub API protection with exponential backoff
- **✅ Repository Caching**: Efficient caching to avoid redundant downloads

### 13.2 Medium Priority
- **🔄 3-Step Workflow**: Implement complete step-based UI workflow
- **🔄 Error Recovery**: Enhanced error recovery and user guidance
- **🔄 Progress Indicators**: Real-time progress indicators for long operations
- **🔄 Configuration Validation**: Enhanced config file validation and error messages

### 13.3 Low Priority
- **📋 Documentation**: Comprehensive user documentation and help system
- **📋 Performance**: Optimize for large repositories and slow connections
- **📋 Accessibility**: Improve accessibility and keyboard navigation
- **📋 Internationalization**: Support for multiple languages

### 13.4 Future Requirements
- **🔮 CDF Integration**: Direct CDF file download and upload capabilities
- **🔮 CDF Zip Download**: Download ZIP files from CDF and extract them (uses `extract_zip_to_temp_dir()`)
- **🔮 Advanced Caching**: Intelligent caching with cache invalidation
- **🔮 Batch Operations**: Support for multiple repository operations
- **🔮 Custom Templates**: Support for custom deployment templates

### 13.5 Current vs Future Download Methods
- **Current (GitHub)**: Individual file download via GitHub API → direct directory caching
- **Future (CDF)**: ZIP file download from CDF → extract using `extract_zip_to_temp_dir()` → directory
- **Future Choice**: Users will be able to choose between CDF zip download or Git repo download
- **ZIP Logic**: Kept `extract_zip_to_temp_dir()` function for future CDF zip download feature

### 13.6 Future Download Source Selection
- **Step 1 Enhancement**: Add radio button to choose download source:
  - 🔗 **GitHub Repository**: Current individual file download approach
  - 📦 **CDF Zip File**: Future ZIP download and extraction approach
- **Unified Workflow**: Both sources lead to the same Step 2 (Configuration Selection)
- **Source Detection**: Automatically detect source type and use appropriate download method

## 14. Mini Zip Architecture (NEW)

### 14.1 Overview
The download_packages.py script now creates TWO zip files for each repository:
1. **Full zip**: Complete repository (e.g., `cognite-quickstart-main.zip`)
2. **Mini zip**: README files only (e.g., `cognite-quickstart-main-mini.zip`)

### 14.2 Naming Convention
- **Full zips**: `{repo-name}.zip`
  - Example: `cognite-quickstart-main.zip`
  - Contains: Complete repository with all files
  - Size: Several MB
  - Usage: Downloaded only when user selects to install

- **Mini zips**: `{repo-name}-mini.zip`
  - Example: `cognite-quickstart-main-mini.zip`
  - Contains: Only README*.md files (case-insensitive)
  - Size: Few KB (typically 10-50KB)
  - Usage: Downloaded on Step 1 to present installation options

### 14.3 Mini Zip Contents
Mini zips contain **ONLY config-specific README files**:
- **Included**: `README.{config}.md` or `readme.{config}.md` files
  - Examples: `README.all.md`, `readme.weather.md`, `readme.hw-all.md`, `readme.neat-basic.md`
  - These map to: `config.all.yaml`, `config.weather.yaml`, `config.hw-all.yaml`, `config.neat-basic.yaml`
- **Excluded**: Generic `README.md` files (no config suffix)
- **Excluded**: Module READMEs from subdirectories
- **Purpose**: Each README describes one specific configuration option for deployment

### 14.4 Streamlit Workflow with Mini Zips

**Step 1: Download Mini Zips and Present Options**
```python
# Download all mini zips from CDF (lightweight, fast)
mini_zips = client.files.list(external_id_prefix="app-packages-", name_contains="-mini.zip")
available_packages = {}

for mini_zip in mini_zips:
    # Download mini zip (few KB each)
    content = client.files.download_bytes(id=mini_zip.id)
    
    # Extract README files
    readme_files = extract_readmes_from_zip(content)
    
    # Parse available configs from README files
    # e.g., README.all.md, README.weather.md → configs: ["all", "weather"]
    configs = parse_configs_from_readmes(readme_files)
    
    # Store package info
    package_name = mini_zip.name.replace("-mini.zip", "")
    available_packages[package_name] = {
        "readmes": readme_files,
        "configs": configs,
        "full_zip_name": f"{package_name}.zip"
    }

# Present to user
selected_package = st.radio("Select Package", options=available_packages.keys())
selected_config = st.radio("Select Configuration", 
                           options=available_packages[selected_package]["configs"])

# Store selections
st.session_state['selected_package'] = selected_package
st.session_state['selected_config'] = selected_config
st.session_state['full_zip_name'] = available_packages[selected_package]["full_zip_name"]
```

**Step 2: Call CDF Function to Deploy**
```python
# User clicks "Deploy Configuration" button
if st.button("Deploy Configuration"):
    # Call CDF Function with parameters
    function_call = client.functions.call(
        external_id="toolkit-deployer-function",
        data={
            "zip_name": st.session_state['full_zip_name'],  # e.g., "cognite-quickstart-main.zip"
            "config_name": st.session_state['selected_config']  # e.g., "weather"
        }
    )
    
    # Wait for completion
    with st.spinner("Deploying configuration..."):
        result = function_call.wait()
    
    # Display results
    if result.success:
        st.success("✅ Deployment successful!")
        st.json(result.response)
    else:
        st.error("❌ Deployment failed")
        st.error(result.error)
```

### 14.5 Benefits
- **Fast Initial Load**: Download only mini zips (KB vs MB)
- **Better UX**: Show all options without large downloads
- **Bandwidth Efficient**: Download full zips only when needed
- **Scalable**: Can have dozens of packages without performance impact
- **Preview Capability**: Users can read READMEs before committing to download

### 14.6 Implementation Status

**Completed:**
- **✅ Script Updated**: `download_packages.py` creates both full and mini zips
- **✅ Naming Convention**: Clear `-mini.zip` suffix for identification  
- **✅ Documentation**: Complete workflow documented in this file
- **✅ Requirements Defined**: Function interface and Streamlit flow specified

**In Progress (Testing Phase):**
- **🔄 Mini Zip Upload**: Test mini zips uploaded to CDF Files
- **🔄 Streamlit Download**: Test downloading mini zips from CDF
- **🔄 CDF Function**: Create and test deployment function
- **🔄 Integration**: Connect Streamlit to function

**Approach:**
- Testing each component independently (stepwise)
- No code changes to production Streamlit yet
- Validate each phase before integration
- Full integration after all components tested

### 14.7 CDF Function Requirements

The Streamlit app calls a CDF Function to perform the actual deployment. This function must:

**Function Specification:**
- **External ID**: `toolkit-deployer-function` (or configurable)
- **Runtime**: Python with `cognite-toolkit` installed
- **Timeout**: 5-10 minutes (deployments can be slow)
- **Environment Variables**: CDF credentials (auto-provided by Functions runtime)

**Input Parameters:**
```python
{
    "zip_name": str,      # e.g., "cognite-quickstart-main.zip"
    "config_name": str    # e.g., "weather" (maps to config.weather.yaml)
}
```

**Function Logic:**
1. Download zip file from CDF Files using `zip_name`
2. Extract to temporary directory
3. Run `cdf build --env {config_name}`
4. Run `cdf deploy --env {config_name}`
5. Capture output and return results

**Output/Response:**
```python
{
    "success": bool,
    "output": str,           # Combined build + deploy output
    "build_summary": dict,   # Files built, modules processed
    "deploy_summary": dict,  # Resources created/updated/unchanged
    "error": str,           # Error message if failed
    "duration_seconds": float
}
```

**Error Handling:**
- Validate zip exists in CDF Files
- Validate config file exists in extracted repo
- Catch and return build/deploy errors
- Clean up temporary files on success or failure

### 14.8 Testing Strategy (Stepwise Integration)

**Phase 1: Test Mini Zip Creation** ✅
- Run `download_packages.py` script
- Verify both full and mini zips are created
- Verify mini zips contain all README files
- Upload to CDF Files for testing

**Phase 2: Test Mini Zip Download in Streamlit**
- Create simple Streamlit test that:
  - Lists all `*-mini.zip` files from CDF
  - Downloads mini zips
  - Extracts and displays README files
  - Parses config names from READMEs
- Test independently before integration

**Phase 3: Test CDF Function**
- Create standalone function that:
  - Accepts `zip_name` and `config_name` parameters
  - Downloads full zip from CDF Files
  - Extracts and runs `cdf build/deploy`
  - Returns structured results
- Test function independently with test zip

**Phase 4: Test Streamlit → Function Integration**
- Test function call from Streamlit:
  - Call function with test parameters
  - Wait for completion
  - Display results
- Test error handling and timeouts

**Phase 5: Full Integration**
- Combine all components
- Test complete user flow
- Test error cases and edge conditions
- Performance testing with multiple packages

**Testing Guidelines:**
- ✅ Test each component independently first
- ✅ Use real CDF environment with test data
- ✅ Verify error handling at each step
- ✅ Test with multiple package types
- ✅ Validate function timeout handling
- ✅ Ensure proper cleanup on errors

### 14.9 Future Enhancements
- **Metadata File**: Add package metadata JSON to mini zips
- **Version Info**: Include version information in mini zips
- **Dependency Info**: Show module dependencies in mini zips
- **Config Parsing**: Automatically parse config.*.yaml references from READMEs
- **Function Status Streaming**: Stream function logs to Streamlit in real-time
- **Deployment History**: Track and display previous deployments
- **Rollback Support**: Enable rollback to previous configurations
- **Multi-Config Deploy**: Deploy multiple configs in one operation
- **Dry Run Mode**: Preview changes before deployment
- **Scheduled Deployments**: Schedule deployments for later execution

## 15. Quality Assurance Checklist

### 15.1 Pre-Deployment Checklist
- [ ] All tests pass in test framework
- [ ] No circular imports or module errors
- [ ] Version number incremented
- [ ] No compiled files (`__pycache__`, `.pyc`) in deployment
- [ ] All imports work correctly
- [ ] File structure is clean and organized

### 15.2 Post-Deployment Verification
- [ ] Streamlit app loads without errors
- [ ] All workflow steps function correctly
- [ ] GitHub download works with rate limiting
- [ ] Build and deploy operations work correctly
- [ ] Verbose logging displays properly
- [ ] Error handling works as expected

### 15.3 Maintenance Tasks
- [ ] Regular test framework execution
- [ ] Monitor GitHub API rate limits
- [ ] Update dependencies as needed
- [ ] Clean up temporary files and caches
- [ ] Review and update documentation

## 16. Troubleshooting Guide

### 16.1 Common Issues
- **Import Errors**: Check `__init__.py` files and import paths
- **Circular Imports**: Use direct function calls instead of imports
- **Module Not Found**: Verify file structure and Python path
- **Rate Limiting**: Implement delays and retry logic
- **Authentication**: Verify OAuth2 credentials and CDF connectivity

### 16.2 Debug Mode
- **Verbose Logging**: Enable detailed logging for troubleshooting
- **Error Messages**: Provide clear, actionable error messages
- **Stack Traces**: Include relevant stack trace information
- **Environment Info**: Log environment variables and system information

### 16.3 Recovery Procedures
- **Git Reset**: Use git to restore from known working states
- **Cache Clear**: Clear repository cache to force fresh downloads
- **Environment Reset**: Reload environment variables and restart
- **Service Restart**: Restart Streamlit service if needed