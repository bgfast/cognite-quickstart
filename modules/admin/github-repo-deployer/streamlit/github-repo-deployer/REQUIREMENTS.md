## GitHub Repo Deployer - UI/Flow Requirements

This document baselines the expected behavior and structure of the Streamlit app so we can refactor to a predictable, non-flickering workflow.

### 1) Global Rules
- There is a single source of truth for the current step: `st.session_state['workflow_step']` in {1..5}.
- Step tabs are clickable navigation:
  - Clicking a completed step moves to that step.
  - Clicking the current step does nothing.
  - Future steps are disabled until prerequisites are satisfied.
- Only content for the currently selected step is rendered. No cross-step content should appear.
- State required by later steps is stored in `st.session_state` (e.g., `extracted_path`, `config_files`, `selected_config`, `selected_env`, `env_vars_loaded`).
- Use `st.rerun()` only when changing steps or after finishes of long operations (download/extract/build/deploy) to reveal the next step.

### 2) Steps
1. Step 1: Download & Environment
   - Show Environment Configuration only in Step 1.
   - Load environment variables (from uploaded file or repo path), show debug availability, but do not request manual inputs.
   - **File Upload Requirements:**
     - Accept ALL file types for environment file uploads (no file type restrictions)
     - Support .env, .txt, .config, or any text file containing environment variables
     - Parse files with KEY=VALUE format regardless of file extension
   - accept a repo url - use this as default: https://github.com/bgfast/cognite-quickstart
   - Use GitHub API to download all files in the repo (no ZIP download due to CORS issues)
   - Download repo to temporary directory (simulating SaaS behavior)
   - extract, set `st.session_state['extracted_path']`.
   - Discover `config.*.yaml` and store list in `st.session_state['config_files']`.
   - provide a download button
   - show logging information from download
   - When complete, enable Step 2.
   - future requirement - connect to a private repo 
   - future requirement - download a zip from the current cdf project

2. Step 2: Select Configuration
   - future - Render sub-tabs, one per `config.*.yaml` file; show associated README if present.
   - Selecting a config sets `st.session_state['selected_config']` and `st.session_state['selected_env']`.
   - step 3 is always enabled because no action is required on step 2. one is selected by default. the user can change it if they want but are not required to
   - Radio selection must not clear or collapse other UI elements; provide immediate visual feedback ("Selected: <file>") and a "Configuration Details" expander
   - future - No rerun on radio change; only rerun on navigation buttons
   - for v1 - only display radio choices - one for each config file.

3. Step 3: Build and Deploy
   - show the name of the selected config
   - provide a build/deploy button
   - use the Cognite SDK directly (no subprocess calls - SaaS Streamlit runs in browser)
   - Build: Create build directory, copy modules, generate metadata (same as toolkit)
   - Deploy: Use Cognite SDK to deploy resources to CDF (OAuth2 client credentials)
   - **Verbose Logging**: Show detailed build and deploy logs with:
     - Environment variables and configuration details
     - File operations and directory structure
     - Module copying and metadata generation
     - OAuth2 authentication process
     - Resource deployment simulation
   - Show build detailed log/output within this step only.
   - Show deploy detailed logs within this step only.
   - On success, advance to Step 5.

future 4. Step 4: Verify
   - Run each of the verify tests from each module.
   - Summarize results (selected config, env, versions, success status).
   - Offer "Start New Deployment" to reset state and return to Step 1.

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

## 14. Quality Assurance Checklist

### 14.1 Pre-Deployment Checklist
- [ ] All tests pass in test framework
- [ ] No circular imports or module errors
- [ ] Version number incremented
- [ ] No compiled files (`__pycache__`, `.pyc`) in deployment
- [ ] All imports work correctly
- [ ] File structure is clean and organized

### 14.2 Post-Deployment Verification
- [ ] Streamlit app loads without errors
- [ ] All workflow steps function correctly
- [ ] GitHub download works with rate limiting
- [ ] Build and deploy operations work correctly
- [ ] Verbose logging displays properly
- [ ] Error handling works as expected

### 14.3 Maintenance Tasks
- [ ] Regular test framework execution
- [ ] Monitor GitHub API rate limits
- [ ] Update dependencies as needed
- [ ] Clean up temporary files and caches
- [ ] Review and update documentation

## 15. Troubleshooting Guide

### 15.1 Common Issues
- **Import Errors**: Check `__init__.py` files and import paths
- **Circular Imports**: Use direct function calls instead of imports
- **Module Not Found**: Verify file structure and Python path
- **Rate Limiting**: Implement delays and retry logic
- **Authentication**: Verify OAuth2 credentials and CDF connectivity

### 15.2 Debug Mode
- **Verbose Logging**: Enable detailed logging for troubleshooting
- **Error Messages**: Provide clear, actionable error messages
- **Stack Traces**: Include relevant stack trace information
- **Environment Info**: Log environment variables and system information

### 15.3 Recovery Procedures
- **Git Reset**: Use git to restore from known working states
- **Cache Clear**: Clear repository cache to force fresh downloads
- **Environment Reset**: Reload environment variables and restart
- **Service Restart**: Restart Streamlit service if needed