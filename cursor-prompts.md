# Cursor Prompts - Cognite Quickstart Project

This file contains common commands and instructions for working with the Cognite Quickstart project.

## Building and Deploying Modules

### Prerequisites

1. **Environment Setup**: Ensure you have your CDF environment configured
   ```bash
   source ~/envs/your-env-file.sh
   # or
   source cdfenv.local.sh
   ```

2. **Required Environment Variables**:
   - `CDF_PROJECT`: Your CDF project name
   - `CDF_CLUSTER`: Your CDF cluster
   - `IDP_CLIENT_ID` and `IDP_CLIENT_SECRET`: Your IDP credentials

### Build Commands

**CRITICAL**: Use `--env` flag (NOT `--config`) when specifying config files!

```bash
# ✅ CORRECT
cdf build --env=hw-function          # Uses config.hw-function.yaml
cdf deploy --env=hw-function --dry-run

# ❌ WRONG
cdf build --config config.hw-function.yaml   # Incorrect syntax
```

#### Build All Modules
```bash
cdf build
```

#### Build Specific Module with Config File (Recommended)
```bash
# Use --env flag with config file base name (without config. prefix or .yaml suffix)
cdf build --env=hw-function              # Uses config.hw-function.yaml
cdf build --env=hw-neat                  # Uses config.hw-neat.yaml
cdf build --env=all-hw                   # Uses config.all-hw.yaml
cdf build --env=app-packages-dm          # Uses config.app-packages-dm.yaml
cdf build --env=app-packages-zips        # Uses config.app-packages-zips.yaml
cdf build --env=streamlit-github-deployer # Uses config.streamlit-github-deployer.yaml
```

#### Build Specific Module with Module Path (Alternative)
```bash
# Use -m flag to specify module directory directly
cdf build -m modules/hw-function
cdf build -m modules/hw-neat
cdf build -m modules/app-packages-dm
cdf build -m modules/app-packages-zips
cdf build -m modules/admin/github-repo-deployer
cdf build -m modules/in-development/live_weather_data
cdf build -m modules/common/foundation
cdf build -m modules/common/valhall_dm
```

#### Build with Environment Type
```bash
cdf build -e dev
cdf build -e staging
cdf build -e prod
```

### Deploy Commands

**📋 DEPLOYMENT WORKFLOW: "Deploy" always means: Build → Dry-run → Deploy**

**⚠️ IMPORTANT: Always run `--dry-run` first to preview changes before actual deployment!**

**⚠️ CRITICAL: Use `--env` flag (NOT `--config`) when specifying config files!**

#### Deploy All (Full Workflow)
```bash
# Complete deployment workflow
cdf build
cdf deploy --dry-run
cdf deploy
```

#### Deploy Specific Module (Full Workflow)
```bash
# Hello World Function (uses config.hw-function.yaml)
cdf build --env=hw-function
cdf deploy --env=hw-function --dry-run
cdf deploy --env=hw-function

# Hello World NEAT (uses config.hw-neat.yaml)
cdf build --env=hw-neat
cdf deploy --env=hw-neat --dry-run
cdf deploy --env=hw-neat

# All Hello World modules (uses config.all-hw.yaml)
cdf build --env=all-hw
cdf deploy --env=all-hw --dry-run
cdf deploy --env=all-hw

# App Packages Data Model (uses config.app-packages-dm.yaml)
cdf build --env=app-packages-dm
cdf deploy --env=app-packages-dm --dry-run
cdf deploy --env=app-packages-dm

# App Packages Zip Files (uses config.app-packages-zips.yaml)
cdf build --env=app-packages-zips
cdf deploy --env=app-packages-zips --dry-run
cdf deploy --env=app-packages-zips

# GitHub Repo Deployer (uses config.dev.yaml or specific config)
cdf build -m modules/admin/github-repo-deployer
cdf deploy --dry-run
cdf deploy
```

#### Deploy with Environment (Full Workflow)
```bash
# Development
cdf build -e dev
cdf deploy -e dev --dry-run
cdf deploy -e dev

# Staging
cdf build -e staging
cdf deploy -e staging --dry-run
cdf deploy -e staging

# Production
cdf build -e prod
cdf deploy -e prod --dry-run
cdf deploy -e prod

# App packages specific environment
cdf build --env=app-packages-dm
cdf deploy --env=app-packages-dm --dry-run
cdf deploy --env=app-packages-dm
```

### Module Deployment Order

For the app packages system, deploy in this order (each "deploy" includes build → dry-run → deploy):

1. **Foundation** (if not already deployed):
   ```bash
   # Full deployment workflow for foundation
   cdf build -m modules/common/foundation
   cdf deploy -m modules/common/foundation --dry-run
   cdf deploy -m modules/common/foundation
   ```

2. **App Packages Data Model** (creates spaces and data models):
   ```bash
   # Full deployment workflow for data model
   cdf build -m modules/app-packages-dm
   cdf deploy -m modules/app-packages-dm --dry-run
   cdf deploy -m modules/app-packages-dm
   ```

3. **App Packages Zip Files** (uploads zip files):
   ```bash
   # Full deployment workflow for zip files
   cdf build -m modules/app-packages-zips
   cdf deploy -m modules/app-packages-zips --dry-run
   cdf deploy -m modules/app-packages-zips
   ```

4. **Streamlit GitHub Deployer** (Streamlit app):
   ```bash
   # Full deployment workflow for Streamlit app
   cdf build --env=streamlit-github-deployer
   cdf deploy --env=streamlit-github-deployer --dry-run
   cdf deploy --env=streamlit-github-deployer
   ```

## App Packages Workflow

### Download GitHub Repositories
```bash
cd modules/app-packages-zips/scripts/
python download_packages.py
```

### Configure Repositories
Edit `modules/app-packages-zips/scripts/repositories.yaml`:
```yaml
repositories:
  - url: "https://github.com/owner/repo/archive/refs/heads/branch.zip"
    name: "clean-filename-without-extension"
```

### GitHub Authentication
The download script automatically uses GitHub CLI authentication:
```bash
gh auth login  # If not already authenticated
```

Or set environment variable:
```bash
export GITHUB_TOKEN="your-token"
```

## Common Troubleshooting

### Build Issues
```bash
# Clean build directory
cdf build --no-clean

# Verbose output
cdf build -v

# Check for missing environment variables
echo $CDF_PROJECT
echo $CDF_CLUSTER
```

#### Common Streamlit Build Warnings and Fixes
```bash
# Warning: Missing required parameter 'creator'
# Fix: Add creator field to Streamlit YAML
creator: your.email@company.com

# Warning: Missing dependencies in requirements.txt: pyodide-http
# Fix: Add pyodide-http to requirements.txt in each app directory

# Warning: UnusedParameterWarning for authentication, runtime, tags, etc.
# Fix: Remove unused parameters from YAML, keep only:
# - externalId, name, creator, description, entrypoint, dataSetExternalId

# Warning: 'type' is deprecated, use 'validation-type' instead
# Fix: In config file, change:
# type: dev  →  validation-type: dev

# Error: Directory structure incorrect
# Example error: "StreamlitApp directory not found in .../streamlit/hello-world-streamlit
#                 (based on externalId hello-world-streamlit)"
# Cause: Directory name doesn't match externalId in YAML
# Fix: Ensure structure matches:
# streamlit/
# ├── ExternalId/           ← Must match YAML externalId EXACTLY (case-sensitive)
# │   ├── main.py          ← Must be named main.py
# │   └── requirements.txt
# └── ExternalId.Streamlit.yaml
#
# CRITICAL: If externalId is "hw-function", directory MUST be "hw-function"
# NOT "hello-world", NOT "HelloWorld", NOT "hw-function-app"
```

### Authentication Issues
```bash
# Check GitHub authentication
gh auth status

# Check CDF authentication
# Verify your environment file has correct credentials
```

### Module Dependencies
- `app-packages-dm` must be deployed before `app-packages-zips`
- `foundation` should be deployed before other modules
- `valhall_dm` is required for weather data modules

### Code Quality and Testing Best Practices

#### Pre-Deployment Testing (MANDATORY)
```bash
# 1. SYNTAX CHECK - Always validate Python syntax first
# Option A: Use helper script (recommended)
python scripts/check_syntax.py modules/[app-name]/streamlit/[externalId]/main.py

# Option B: Direct py_compile
python -m py_compile modules/[app-name]/streamlit/[externalId]/main.py

# 2. Always test locally before deploying
cd modules/[app-name]/streamlit/[externalId]/
streamlit run main.py

# 3. Check for common errors:
# - Indentation errors (IndentationError)
# - Function signature mismatches (return value count)
# - Import errors and circular dependencies
# - Missing parameters or variables
# - YAML syntax errors (colons in descriptions need quotes)

# 4. Verify function contracts when refactoring:
# - Check what calling code expects (parameter count, types)
# - Ensure return values match expected tuple unpacking
# - Read calling functions before modifying signatures

# 5. Test error scenarios:
# - Missing CDF connection
# - Empty file lists
# - Network failures

# CRITICAL: Never deploy without syntax validation!
# Basic Python syntax errors should never reach SaaS deployment

# 6. Clean up after syntax checking
rm -rf modules/[app-name]/streamlit/[externalId]/__pycache__
```

#### Common Code Quality Issues
```bash
# Issue: ValueError - not enough values to unpack
# Cause: Function returns fewer values than caller expects
# Fix: Check calling code for expected return tuple size
# Example: ui_steps.py expects 4 values, function returned 3

# Issue: YAML syntax errors in descriptions
# Cause: Unquoted colons in YAML values
# Fix: Quote descriptions with colons: "v1.99 - Fixed: issue"

# Issue: Import errors in SaaS vs localhost
# Cause: Different Python environments or missing dependencies
# Fix: Test in both environments, check requirements.txt

# Issue: Function signature changes breaking callers
# Cause: Modifying function without checking all usage
# Fix: Search codebase for function usage before changing
```

### Streamlit Deployment Issues

#### Critical Directory Structure Requirements

```bash
# ❌ WRONG: Flat structure in streamlit directory
modules/neat-basic/streamlit/
├── neat_data_writer.py              # Wrong: not in subdirectory
├── neat_data_reader.py              # Wrong: not in subdirectory
├── NeatDataWriter.Streamlit.yaml
└── NeatDataReader.Streamlit.yaml

# ✅ CORRECT: Subdirectory structure matching externalId
modules/neat-basic/streamlit/
├── NeatDataWriter/                  # Directory name = externalId
│   ├── main.py                      # Required name
│   └── requirements.txt
├── NeatDataReader/                  # Directory name = externalId  
│   ├── main.py                      # Required name
│   └── requirements.txt
├── NeatDataWriter.Streamlit.yaml
└── NeatDataReader.Streamlit.yaml

# Key Rules:
# 1. Each app MUST be in its own subdirectory
# 2. Subdirectory name MUST exactly match externalId in YAML
# 3. Python file MUST be named main.py (not the app name)
# 4. Each subdirectory needs its own requirements.txt
# 5. YAML file MUST be in the streamlit/ directory (not module root)
# 6. Module MUST have module.toml file for toolkit recognition
```

#### Required YAML Parameters vs Warnings

```yaml
# ✅ MINIMAL YAML (no warnings)
externalId: MyApp                    # REQUIRED - matches directory name
name: My Application                 # REQUIRED - display name
creator: user@company.com            # REQUIRED - toolkit validation
description: App description         # REQUIRED - shows in CDF
entrypoint: main.py                  # REQUIRED - entry point file
dataSetExternalId: my-dataset        # REQUIRED - data governance

# ❌ PARAMETERS THAT CAUSE WARNINGS (remove these):
# runtime:                           # UnusedParameterWarning
#   version: "3.11"
# authentication:                    # UnusedParameterWarning  
#   clientId: ${IDP_CLIENT_ID}
#   clientSecret: ${IDP_CLIENT_SECRET}
# tags:                              # UnusedParameterWarning
#   - tag1
#   - tag2
# published: true                    # UnusedParameterWarning
# theme: Light                       # UnusedParameterWarning
```

#### Required Dependencies

```txt
# requirements.txt - MUST include pyodide-http
streamlit>=1.28.0
cognite-sdk>=7.62.0
pandas>=2.0.0
plotly>=5.15.0
numpy>=1.24.0
pyodide-http                         # REQUIRED - missing causes build warning
```

#### Common Streamlit Module Setup Errors

```bash
# Error: StreamlitApp directory not found based on externalId
# Cause: Directory structure doesn't match YAML externalId
# Fix: Create directory matching externalId exactly
# Example: externalId: test-toolkit-api → directory: streamlit/test-toolkit-api/

# Error: Module not recognized by toolkit (only _build_environment.yaml created)
# Cause: Missing module.toml file
# Fix: Create module.toml in module root:
[module]
name = "module-name"
description = "Module description"
version = "1.0.0"

# Error: YAML file not found during build
# Cause: YAML file in wrong location (module root instead of streamlit/)
# Fix: Move YAML file to streamlit/ directory
# Wrong: modules/my-app/MyApp.Streamlit.yaml
# Right: modules/my-app/streamlit/MyApp.Streamlit.yaml

# Error: Dataset not found during deployment
# Cause: Missing dataset definition
# Fix: Create data_sets/[dataset-name].DataSet.yaml:
externalId: my-dataset
name: My Dataset
description: Dataset description
```

#### Critical SaaS Compatibility Fixes
```bash
# Error: StreamlitSetPageConfigMustBeFirstCommandError
# Fix: Move st.set_page_config() to be the very first Streamlit command
# Must be immediately after: import streamlit as st
# This error only appears in SaaS, not localhost

# Error: Circular import causing duplicate st.set_page_config()
# Fix: Use parameter passing instead of direct imports between modules
# Use sys.modules.get('main') for safe module access
# Never import main.py from other modules

# Error: CogniteClient initialization fails in SaaS
# Fix: Use CogniteClient() with no parameters for SaaS
# Fallback to OAuth2 credentials for local development

# Error: CDF shows "Unchanged" even when code was modified
# Fix: Bump version number in YAML description to force deployment
# Version changes are required for CDF to recognize Streamlit updates

# Error: SaaS Streamlit not reflecting latest code changes
# Fix: Always increment version number when deploying code changes
# CDF caches Streamlit apps and needs version bump to refresh
```

#### CDF Integration Patterns
```bash
# SaaS CogniteClient initialization (correct):
from cognite.client import CogniteClient
client = CogniteClient()  # No parameters needed in SaaS

# Local CogniteClient initialization (fallback):
config = ClientConfig(
    client_name="app-name",
    base_url=f"https://{cluster}.cognitedata.com",
    project=project,
    credentials=OAuthClientCredentials(...)
)
client = CogniteClient(config)

# Error: CDF Files API not finding files in spaces
# Fix: Use data modeling API for space-based file discovery
# Files in spaces are data model instances, not regular files
instances = client.data_modeling.instances.list(space='app-packages')

# Error: Environment variables not passed to deployment
# Fix: Use os.environ fallback when UI env_vars are empty
# SaaS vs localhost behavior differences
```

#### Version Management
```bash
# Always update version in both places:
# 1. GitHubRepoDeployer.Streamlit.yaml - description field
# 2. main.py - page_title and st.caption
# 3. Remove old nested files that might contain outdated versions
```

#### Module Structure Best Practices
```bash
# Streamlit apps should be top-level modules:
# ✅ modules/streamlit-github-deployer/
# ❌ modules/admin/github-repo-deployer/streamlit/

# Directory structure must match Cognite toolkit expectations:
# modules/[module-name]/streamlit/[externalId]/main.py
# Where externalId matches the YAML file's externalId field
```

## Standard Streamlit App Template

### Directory Structure Pattern
```
modules/[streamlit-app-name]/
├── module.toml                      ← REQUIRED for toolkit recognition
├── streamlit/
│   ├── [AppName].Streamlit.yaml     ← YAML config file (MUST be in streamlit/)
│   └── [externalId]/                ← Directory name MUST match externalId in YAML
│       ├── main.py                  ← Entry point (required name)
│       ├── requirements.txt         ← Python dependencies (include pyodide-http)
│       └── services/                ← Optional: additional modules
├── data_sets/
│   └── [app-name]-dataset.DataSet.yaml  ← REQUIRED if referenced in YAML
└── README.md
```

**CRITICAL**: 
- The directory name under `streamlit/` MUST exactly match the `externalId` field in the YAML file
- `module.toml` is REQUIRED in module root for toolkit to recognize the module
- YAML file MUST be in `streamlit/` directory, not module root
- Dataset MUST exist if referenced in `dataSetExternalId`

### Version Management Pattern (3 Required Locations)

#### 1. Streamlit YAML Configuration
```yaml
# [AppName].Streamlit.yaml
externalId: [app-external-id]        # ← MUST match directory name exactly
name: [App Display Name]
creator: [your-email]                # ← REQUIRED field
description: v[X.XX] - [Brief feature description]  # ← Shows in SaaS Streamlit list
entrypoint: main.py                  # ← Entry point file (required)
dataSetExternalId: [app-name]-dataset

# REMOVED unused parameters that cause warnings:
# - published, theme, runtime, authentication, tags
# Only include parameters that are actually used by the toolkit
```

#### 2. Main.py Page Configuration
```python
# main.py (MUST be FIRST Streamlit command)
import streamlit as st

st.set_page_config(
    page_title="[App Name] v[X.XX]",  # ← Browser tab title
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

#### 3. Main.py UI Caption
```python
# main.py (in main UI section)
st.title("🚀 [App Name]")
st.markdown("[App description]")
st.caption("Version [X.XX] - [Brief feature description]")  # ← Visible in app UI
```

### SaaS Compatibility Requirements
```python
# CogniteClient initialization for SaaS
def initialize_cdf_client():
    try:
        # First try SaaS connection (no parameters needed)
        from cognite.client import CogniteClient
        client = CogniteClient()
        is_local_env = False
        return client, is_local_env
    except Exception:
        # Fallback to OAuth2 for local development
        # ... OAuth2 setup code ...
        pass

# Avoid circular imports - use parameter passing
def my_function(client, is_local_env):
    # Pass client as parameter instead of importing from main
    pass
```

### Version Update Checklist
```markdown
## Streamlit Version Update (v[OLD] → v[NEW])
□ 1. Update [AppName].Streamlit.yaml description: "v[NEW] - [features]"
□ 2. Update main.py page_title: "[App Name] v[NEW]"  
□ 3. Update main.py st.caption: "Version [NEW] - [features]"
□ 4. TEST LOCALLY FIRST: streamlit run main.py
□ 5. Build: cdf build --env=[app-config]
□ 6. Dry-run: cdf deploy --env=[app-config] --dry-run
□ 7. Deploy: cdf deploy --env=[app-config]
□ 8. Verify version shows correctly in SaaS Streamlit list

CRITICAL: Always test locally before deploying to catch runtime errors!
Version bumps are REQUIRED to force CDF to recognize Streamlit changes.
```

### Config File Pattern
```yaml
# config.[app-name].yaml
environment:
  name: [app-name]
  project: bgfast                   # ← MUST be hardcoded, not ${CDF_PROJECT}
  validation-type: dev              # ← Use 'validation-type' not 'type' (deprecated)
  selected:
    - modules/[app-name]

# CRITICAL: Project field requirements:
# - Must match current CDF_PROJECT environment variable exactly
# - Cannot use ${CDF_PROJECT} variable syntax
# - Toolkit validates config project == CDF_PROJECT env var
# - Build will fail with mismatch warning if incorrect

# Common validation-type values:
# - dev: Development environment with relaxed validation
# - staging: Staging environment with moderate validation  
# - prod: Production environment with strict validation
```

### CogniteFile/Data Model Issues
```bash
# Error: Property 'owner' does not exist in view 'cdf_cdm:CogniteFile/v1'
# Fix: Remove custom properties from node definitions extending CogniteFile

# Error: Property 'metadata' does not exist in view 'cdf_cdm:CogniteFile/v1'  
# Fix: Remove metadata section from CogniteFile.yaml templates

# Only use properties that exist in the CDF view you're extending
# Check CDF documentation for valid properties of each view type
```

## Hello World Modules

### Purpose
The Hello World (hw-*) modules are educational examples demonstrating CDF development patterns:

1. **hw-function**: Function + Streamlit integration
   - Simple function that receives input and returns greeting
   - Streamlit UI for calling the function
   - Real-time status updates and logs
   - Complete request/response cycle

2. **hw-neat**: Excel-based data modeling with NEAT
   - Data model defined in Excel
   - Automated YAML generation
   - Streamlit app for CRUD operations
   - Testing and validation suite

### Naming Convention

**CRITICAL**: All Hello World modules follow the `hw-*` naming pattern consistently:

```
modules/hw-function/
├── functions/
│   ├── hw-function.Function.yaml       # externalId: hw-function
│   └── hw-function/                    # Directory matches externalId
│       └── handler.py
├── streamlit/
│   ├── hw-function.Streamlit.yaml      # externalId: hw-function
│   └── hw-function/                    # Directory matches externalId
│       └── main.py
├── data_sets/
│   └── hw-function-dataset.DataSet.yaml
└── module.toml

config.hw-function.yaml                 # Config file naming
```

**Rules for consistent naming:**
1. Module directory: `modules/hw-[name]/`
2. Config file: `config.hw-[name].yaml`
3. Function externalId: `hw-[name]`
4. Function directory: `functions/hw-[name]/`
5. Streamlit externalId: `hw-[name]` or `hw-[name]-ui`
6. Streamlit directory: `streamlit/hw-[name]/`
7. Dataset externalId: `hw-[name]-dataset`
8. All references in code use `hw-[name]`

### Deployment

```bash
# Deploy individual module
cdf build --env=hw-function
cdf deploy --env=hw-function --dry-run
cdf deploy --env=hw-function

# Deploy all Hello World modules
cdf build --env=all-hw
cdf deploy --env=all-hw --dry-run
cdf deploy --env=all-hw
```

### Documentation

- `readme.hw-function.md` - Function module guide
- `readme.hw-neat.md` - NEAT module guide
- `readme.hw-all.md` - Complete Hello World guide
- `docs/requirements.hw.md` - Comprehensive requirements checklist

## File Locations

### Configuration Files
- `config.hw-function.yaml` - Hello World Function demo
- `config.hw-neat.yaml` - Hello World NEAT demo
- `config.all-hw.yaml` - All Hello World modules
- `config.dev.yaml` - Development environment config
- `config.staging.yaml` - Staging environment config  
- `config.prod.yaml` - Production environment config
- `config.all.yaml` - All modules deployment config
- `config.app-packages-dm.yaml` - App packages data model config
- `config.app-packages-zips.yaml` - App packages zip files config
- `config.streamlit-github-deployer.yaml` - Streamlit GitHub deployer config
- `config.weather.yaml` - Weather data modules config
- `cdfenv.sh` - Environment variables template

### Module Directories
- `modules/hw-function/` - Hello World Function + Streamlit demo
- `modules/hw-neat/` - Hello World NEAT data model with Excel generation and Streamlit apps
- `modules/app-packages-dm/` - Data model for app packages (foundational)
- `modules/app-packages-zips/` - Zip file management and uploads
- `modules/streamlit-github-deployer/` - Streamlit app for CDF-integrated GitHub deployment
- `modules/neat-basic/` - (DEPRECATED: Use hw-neat) NEAT Basic data model
- `modules/common/foundation/` - Basic CDF setup (groups, datasets)
- `modules/common/valhall_dm/` - Valhall data model and transformations
- `modules/in-development/live_weather_data/` - Weather data integration

### Build Output
- `build/` - Generated configuration files ready for deployment

## Git Best Practices

### .gitignore Management
```bash
# Always add large binary files to .gitignore
echo "modules/app-packages-zips/files/*.zip" >> .gitignore

# Ignore build artifacts
echo "build/" >> .gitignore
echo "tmp/" >> .gitignore
```

### Commit Workflow
```bash
# Always use git add . for comprehensive commits
git add .
git commit -m "descriptive commit message"
git push

# For pull requests
gh pr create --title "Feature: Description" --body "Details"
gh pr merge --squash
```

### Branch Management
```bash
# Create feature branches for major changes
git checkout -b feature/streamlit-cdf-integration
# ... make changes ...
git add .
git commit -m "Add CDF Files API integration to Streamlit"
git push origin feature/streamlit-cdf-integration
```

## Deployment Best Practices

### Command Execution Rules
```bash
# ❌ NEVER bundle commands together with &&
cdf build && cdf deploy --dry-run && cdf deploy

# ✅ ALWAYS run commands individually
cdf build --env=[config]
cdf deploy --env=[config] --dry-run
cdf deploy --env=[config]

# Why individual commands:
# - See individual results and catch issues early
# - Allow user control over each step  
# - Follow proper workflow validation
# - Enable stopping if dry-run shows unexpected changes
```

### Streamlit Deployment Issues
```bash
# Issue: CDF shows "Unchanged" even when code was modified
# Solution: Bump version number to force recognition of changes

# Issue: SaaS Streamlit not reflecting latest code
# Solution: Version bump + redeploy forces app refresh in CDF

# Issue: Streamlit app cached in SaaS
# Solution: Change description in YAML to trigger deployment

# Issue: Runtime errors only appear in SaaS, not localhost
# Solution: Always test locally first, but be aware of environment differences
# SaaS may have different Python versions, missing packages, or stricter validation

# Issue: Deploying broken code due to insufficient testing
# Solution: Mandatory local testing before any deployment
# Use "streamlit run main.py" to catch errors before SaaS deployment
```

## Quick Commands Reference

```bash
# Individual deployment workflow (CORRECT)
cdf build --env=[config]
cdf deploy --env=[config] --dry-run
cdf deploy --env=[config]

# Download packages workflow
cd modules/app-packages-zips/scripts/
python download_packages.py
cd ../../..
cdf build --env=app-packages-zips
cdf deploy --env=app-packages-zips --dry-run
cdf deploy --env=app-packages-zips

# Deploy Streamlit app workflow
cdf build --env=streamlit-github-deployer
cdf deploy --env=streamlit-github-deployer --dry-run
cdf deploy --env=streamlit-github-deployer

# Check build status
ls -la build/

# View deployment logs (individual commands)
cdf deploy --env=[config] --dry-run -v
cdf deploy --env=[config] -v

# Clean and rebuild
rm -rf build/
cdf build --env=[config]
```

## Environment Files

### Development
```bash
cp cdfenv.sh cdfenv.local.sh
# Edit cdfenv.local.sh with your credentials
source cdfenv.local.sh
```

### Production
```bash
source ~/envs/prod-env.sh
cdf build -e prod
cdf deploy -e prod --dry-run
cdf deploy -e prod
```

## NEAT (Network Extraction and Analysis Tool) Integration

**Documentation**: [NEAT Installation Guide](https://cognite-neat.readthedocs-hosted.com/en/latest/gettingstarted/installation.html)

### NEAT Overview
NEAT is Cognite's tool for data modeling that processes Excel files and generates CDF Toolkit-compatible YAML files for data models.

### NEAT Installation
```bash
# Install NEAT package
pip install cognite-neat

# For local environments with enhanced features
pip install "cognite-neat[pyoxigraph]"
```

### NEAT Basic Module Structure
```
modules/neat-basic/
├── data_models/
│   ├── NeatBasic.xlsx                    # Excel data model definition
│   ├── data_models/                      # NEAT-generated files
│   │   ├── containers/
│   │   │   └── NeatBasic.container.yaml  # Generated container
│   │   ├── views/
│   │   │   └── NeatBasic.view.yaml       # Generated view
│   │   ├── EDM-COR-ALL-NEAT.space.yaml  # Generated space
│   │   └── HWNeatDM.datamodel.yaml      # Generated data model
│   └── ~$NeatBasic.xlsx                  # Excel temp file (ignore)
├── streamlit/
│   ├── neat_data_writer.py               # Streamlit app for writing data
│   ├── neat_data_reader.py               # Streamlit app for reading data
│   ├── NeatDataWriter.Streamlit.yaml     # Writer app config
│   ├── NeatDataReader.Streamlit.yaml     # Reader app config
│   ├── requirements.txt                  # Python dependencies
│   └── README.md                         # Streamlit apps documentation
├── data_sets/
│   └── neat-basic-dataset.DataSet.yaml   # Dataset for governance
├── generate_edm_yaml_files.py            # NEAT YAML generation script
├── test_neat_data_model.py               # Comprehensive testing script
├── sample_data_generator.py              # Sample data generation
├── neat_integration_test.py              # End-to-end integration tests
├── module.toml                           # Module configuration
└── README.md                             # Module documentation
```

### NEAT Workflow: Excel to Deployment

#### 1. Excel Data Model Creation
Create or modify `NeatBasic.xlsx` with your data model definition following NEAT Excel format.

#### 2. Generate YAML Files
```bash
cd modules/neat-basic

# Ensure CDF environment is set
source ../../cdfenv.sh
cdfenv bgfast

# Generate YAML files from Excel
python generate_edm_yaml_files.py
```

#### 3. Fix Common NEAT Issues
```bash
# Common issues and fixes:

# Issue: ViewValueError - View entities are None
# Fix: Ensure View column in Excel has proper values, not empty cells

# Issue: EmptyStore error
# Fix: Validate Excel format follows NEAT requirements

# Issue: Container property format errors
# Fix: Ensure container properties have proper structure:
properties:
  name:
    type:
      list: false
      collation: ucs_basic
      type: text
    immutable: false
    nullable: false
    autoIncrement: false

# Issue: View filter errors - empty 'and: []'
# Fix: Remove empty filter sections or provide valid filters
```

#### 4. Deploy NEAT Module
```bash
# Build with NEAT-specific config
cdf build --env=neat-basic

# Dry-run to verify
cdf deploy --env=neat-basic --dry-run

# Deploy to CDF
cdf deploy --env=neat-basic
```

### NEAT Testing Suite

The neat-basic module includes comprehensive testing tools:

#### 1. Data Model Testing
```bash
cd modules/neat-basic
python test_neat_data_model.py
```
Tests:
- ✅ Space deployment and configuration
- ✅ Container deployment with correct properties  
- ✅ View deployment and accessibility
- ✅ Instance creation and validation
- ✅ Data querying capabilities
- ✅ Data validation constraints

#### 2. Sample Data Generation
```bash
cd modules/neat-basic
python sample_data_generator.py
```
Features:
- 🏭 Generate realistic asset instances
- 🔍 Dry-run mode to preview data
- 📋 List existing assets
- 🧹 Cleanup utilities for test data

#### 3. Integration Testing
```bash
cd modules/neat-basic
python neat_integration_test.py
```
Provides:
- 🔍 Prerequisites validation
- 🏗️ Automated toolkit build
- 🚀 Deployment testing (dry-run and real)
- 🧪 Data model validation
- 🏭 Sample data operations
- 📊 Comprehensive reporting

### NEAT Streamlit Apps

The neat-basic module includes two Streamlit applications with proper directory structure:

```
modules/neat-basic/streamlit/
├── NeatDataWriter/                  # Directory matches externalId
│   ├── main.py                      # Writer app entry point
│   └── requirements.txt             # Dependencies
├── NeatDataReader/                  # Directory matches externalId
│   ├── main.py                      # Reader app entry point  
│   └── requirements.txt             # Dependencies
├── NeatDataWriter.Streamlit.yaml    # Writer app config
├── NeatDataReader.Streamlit.yaml    # Reader app config
└── README.md                        # Documentation
```

#### NEAT Data Writer (`NeatDataWriter/main.py`)
**Purpose**: Write data to NEAT model
- ✅ Create individual instances via forms
- ✅ View and search existing data
- ✅ Bulk import from CSV files
- ✅ Data validation and error handling
- ✅ Export capabilities

#### NEAT Data Reader (`NeatDataReader/main.py`)  
**Purpose**: Read and analyze NEAT model data
- ✅ Data explorer with filtering
- ✅ Instance lookup by external ID
- ✅ Analytics dashboard with statistics
- ✅ Query builder with visual interface
- ✅ Interactive charts and visualizations

#### Streamlit YAML Configuration
```yaml
# NeatDataWriter.Streamlit.yaml
externalId: NeatDataWriter           # Matches directory name exactly
name: NEAT Data Writer
creator: brent.groom@cognitedata.com # Required field
description: Streamlit app for writing data to the NEAT Basic data model
entrypoint: main.py                  # Entry point file
dataSetExternalId: neat-basic-dataset

# NeatDataReader.Streamlit.yaml  
externalId: NeatDataReader           # Matches directory name exactly
name: NEAT Data Reader
creator: brent.groom@cognitedata.com # Required field
description: Streamlit app for reading and analyzing data from the NEAT Basic data model
entrypoint: main.py                  # Entry point file
dataSetExternalId: neat-basic-dataset
```

### NEAT Configuration

#### Config File: `config.neat-basic.yaml`
```yaml
environment:
  name: bgfast
  project: bgfast
  type: dev
  selected:
    - modules/common/foundation    # Basic setup
    - modules/neat-basic          # NEAT data model + apps

variables:
  # NEAT-specific configuration
  neat_basic_space: neat-basic
  neat_basic_container: BasicAsset  
  neat_basic_view: BasicAsset
  neat_basic_dataset: neat-basic-dataset
  
  # Testing configuration
  neat_test_asset_prefix: test_neat_
  neat_sample_asset_count: 10
  neat_cleanup_enabled: true
```

### NEAT Best Practices

#### Excel Data Model
- Follow NEAT Excel format specifications
- Ensure View column has proper values (not None/empty)
- Validate container property definitions
- Use consistent naming conventions

#### YAML Generation
- Always run `generate_edm_yaml_files.py` after Excel changes
- Review generated files for format issues
- Fix container property structures manually if needed
- Remove empty filter sections from views

#### Testing Workflow
1. **Generate YAML**: `python generate_edm_yaml_files.py`
2. **Test locally**: Run testing scripts before deployment
3. **Deploy with dry-run**: Always preview changes first
4. **Validate deployment**: Use integration tests after deployment
5. **Use Streamlit apps**: Test data operations through UI

#### Common NEAT Errors and Solutions

```bash
# Error: 'str' object has no attribute 'get'
# Cause: Container property type is string instead of object
# Fix: Update container YAML to use proper type structure

# Error: At least one filter must be provided
# Cause: Empty 'and: []' filter in view
# Fix: Remove filter section or provide valid filters

# Error: KeyError: 'list'
# Cause: Missing required fields in container property type
# Fix: Add all required fields (list, collation, type, etc.)

# Error: cognite-neat package not found
# Cause: Package not installed or wrong environment
# Fix: pip install cognite-neat (may require special access)
```

### NEAT Data Model Properties

The generated NEAT Basic model includes:
- **Space**: `EDM-COR-ALL-NEAT`
- **Container**: `NeatBasic` 
- **Properties**: `newString` (main data property)
- **Views**: `NeatBasic` (for data access)

## Cognite Toolkit Library Investigation

### **DEFINITIVE CONCLUSION: cognite-toolkit CANNOT be used in Streamlit SaaS**

#### Trial History (October 3, 2024)

**Trial 1A: Direct Import (FAILED)**
```bash
# Error: ModuleNotFoundError: No module named 'cognite_toolkit'
# Cause: Package not in requirements.txt
# Status: FAILED - package not installed
```

**Trial 1B: Added to requirements.txt (FAILED)**
```bash
# Error: ValueError: Can't find a pure Python 3 wheel for: 'cognite-toolkit'
# Cause: Native dependencies (C extensions) incompatible with Pyodide
# Status: FAILED - Pyodide compatibility issue
# Conclusion: cognite-toolkit CANNOT be used in Streamlit SaaS environment
```

**Trial 2: Direct CogniteClient Simulation (WORKS but not acceptable)**
```bash
# Approach: Use CogniteClient() directly to simulate toolkit operations
# Status: WORKS but is simulation-only (not acceptable per user requirements)
# Result: Can simulate toolkit output but not real toolkit functionality
```

**Trial 3: Cognite Functions Approach (BREAKTHROUGH CANDIDATE)**
```bash
# Approach: Deploy Cognite Function that can install cognite-toolkit
# Theory: Functions have full Python environment, can install toolkit
# Benefits: Full Python environment, subprocess support, pip install works
# Status: DEPLOYED AND READY FOR TESTING
```

#### Cognite Functions Solution Architecture

```
Streamlit SaaS → HTTP call → Cognite Function → cognite-toolkit library → CDF
```

**Function Deployment Structure:**
```
modules/[module-name]/functions/
├── [function-name].Function.yaml    # Function configuration
└── [function-name]/                 # Directory matching externalId
    ├── handler.py                   # Function code (required name)
    └── requirements.txt             # Function dependencies
```

**Function YAML Format:**
```yaml
- name: Function Display Name
  externalId: function-external-id   # Must match directory name
  owner: user@company.com
  description: Function description
  cpu: 0.5                          # Will be adjusted by CDF
  memory: 1.5                       # Will be adjusted by CDF
  metadata:
    version: "1.0"
  runtime: py311
  functionPath: handler.py           # Required name
```

**Function Calling from Streamlit:**
```python
from cognite.client import CogniteClient
client = CogniteClient()

# Call function
call_result = client.functions.call(
    external_id="function-name",
    data={"input": "data"}
)

# Monitor progress
call_status = client.functions.calls.get_status(call_result.id)

# Get results
result = client.functions.calls.get_response(call_result.id)
```

#### Key Learnings

1. **cognite-toolkit has native dependencies** that are incompatible with Pyodide (Streamlit SaaS)
2. **Cognite Functions provide full Python environment** where toolkit can be installed
3. **Function deployment requires specific directory structure** matching externalId
4. **Functions can run subprocess calls** and install packages dynamically
5. **Real toolkit functionality may be possible via Functions** (pending test results)

## CDF Integration Patterns

### App Packages System
```bash
# Complete app packages workflow
cd modules/app-packages-zips/scripts/ && python download_packages.py
cdf build --env=app-packages-dm && cdf deploy --env=app-packages-dm --dry-run && cdf deploy --env=app-packages-dm
cdf build --env=app-packages-zips && cdf deploy --env=app-packages-zips --dry-run && cdf deploy --env=app-packages-zips
```

### NEAT Basic System
```bash
# Complete NEAT workflow: Excel → YAML → Deploy → Apps
cd modules/neat-basic
python generate_edm_yaml_files.py
cd ../..
cdf build --env=neat-basic
cdf deploy --env=neat-basic --dry-run  
cdf deploy --env=neat-basic

# Access Streamlit apps in CDF for data operations
```

### Streamlit CDF Integration
```bash
# Deploy Streamlit app with CDF zip file integration
cdf build --env=streamlit-github-deployer && cdf deploy --env=streamlit-github-deployer --dry-run && cdf deploy --env=streamlit-github-deployer

# Key patterns:
# - Use CogniteClient() with no parameters in SaaS
# - Use data modeling API for space-based file discovery
# - Files in spaces are instances, not regular files
# - Environment variables must flow from UI to deployment process
# - Avoid circular imports between modules
# - st.set_page_config() must be first Streamlit command
```

## Useful Cursor AI Prompts

### "Deploy streamlit-github-deployer to bgfast"
```
Execute the full deployment workflow for the Streamlit app to bgfast environment:
1. Verify environment (bgfast/bluefield)
2. Build with --env=streamlit-github-deployer
3. Dry-run deploy
4. Deploy
```

### "Deploy app-packages system to bgfast"
```
Deploy the complete app packages system: download repos → deploy dm → deploy zips → deploy streamlit
```

### "Download the latest GitHub repositories"
```
Run the download script in modules/app-packages-zips/scripts/ to get the latest versions of all configured repositories
```

### "Create a new neat-basic data model"
```
Set up a new data model module using neat library with basic containers and views
```

### "Generate YAML from NEAT Excel file"
```
Process NeatBasic.xlsx using NEAT library to generate CDF Toolkit YAML files:
1. Run python generate_edm_yaml_files.py in neat-basic module
2. Fix any Excel format issues (View definitions, empty filters)
3. Correct container property formats (add list, collation, etc.)
4. Deploy with config.neat-basic.yaml
```

### "Deploy NEAT Basic module with Streamlit apps"
```
Deploy the complete NEAT Basic system: Excel → YAML → Deploy → Streamlit apps
1. Generate YAML from Excel: python generate_edm_yaml_files.py
2. Build: cdf build --env=neat-basic
3. Dry-run: cdf deploy --env=neat-basic --dry-run
4. Deploy: cdf deploy --env=neat-basic
5. Access Streamlit apps in CDF for data read/write operations
```

### "Create new Streamlit app from template"
```
Set up a new Streamlit app following the standard pattern:
1. Create module directory structure with module.toml
2. Choose consistent naming convention (e.g., hw-myapp for all components)
3. Create streamlit/[externalId]/ directory matching YAML externalId EXACTLY
   - If YAML has externalId: hw-function, directory MUST be hw-function
   - Case-sensitive, no variations allowed
4. Place YAML file in streamlit/ directory (not module root)
   - Name: [externalId].Streamlit.yaml (e.g., hw-function.Streamlit.yaml)
5. Create data_sets/[dataset-name].DataSet.yaml if referenced
6. Set up YAML with version in description (quote if contains colons)
7. Create main.py with SaaS-compatible CogniteClient
8. Add pyodide-http to requirements.txt
9. Add version in 3 required locations
10. Create config file for deployment with hardcoded project name
    - Name: config.[module-name].yaml (e.g., config.hw-function.yaml)
11. Use consistent externalIds throughout:
    - Function: hw-function
    - Streamlit: hw-function (or hw-function-ui if multiple apps)
    - Dataset: hw-function-dataset
12. TEST LOCALLY: streamlit run main.py before deploying
13. Build with: cdf build --env=[module-name] (not --config)
```

### "Fix Streamlit SaaS deployment error"
```
Check and fix st.set_page_config() placement and version number consistency
```

### "Fix Streamlit directory structure"
```
Correct Streamlit app directory structure to match Cognite Toolkit requirements:

CRITICAL: Directory name MUST exactly match externalId in YAML file!

Example error: "StreamlitApp directory not found in .../streamlit/hello-world
              (based on externalId hello-world-streamlit)"
This means: directory is "hello-world" but externalId is "hello-world-streamlit"

Fix steps:
1. Check externalId in YAML file (e.g., externalId: hw-function)
2. Rename directory to match EXACTLY (e.g., mv hello-world hw-function)
3. Verify directory name matches externalId character-by-character
4. Create module.toml in module root if missing
5. Move YAML file to streamlit/ directory if in module root
6. Rename YAML to [externalId].Streamlit.yaml (e.g., hw-function.Streamlit.yaml)
7. Ensure Python file inside directory is named main.py
8. Copy requirements.txt to subdirectory if missing
9. Update YAML entrypoint to main.py
10. Add required creator field to YAML
11. Remove unused YAML parameters that cause warnings
12. Add pyodide-http to requirements.txt
13. Create dataset YAML if referenced in dataSetExternalId
14. Use consistent naming across all module components

Naming consistency example (hw-function module):
- Module directory: modules/hw-function/
- Function externalId: hw-function
- Function directory: functions/hw-function/
- Streamlit externalId: hw-function
- Streamlit directory: streamlit/hw-function/
- Dataset externalId: hw-function-dataset
- Config file: config.hw-function.yaml
```

### "Fix Streamlit build warnings"
```
Resolve common Streamlit build warnings:
1. Add missing 'creator' field to YAML
2. Remove unused parameters (runtime, authentication, tags, published, theme)
3. Add pyodide-http to requirements.txt
4. Ensure externalId matches directory name exactly
5. Use validation-type instead of deprecated type in config
```

### "Update Streamlit app version"
```
Update version in all 3 required locations following the standard checklist:
1. YAML description (critical for SaaS recognition) - quote if contains colons
2. Page title (browser tab)
3. UI caption (visible in app)
4. TEST LOCALLY before deploying
Example: v1.95 → v1.96 with meaningful description of changes
```

### "Debug Streamlit runtime error"
```
When Streamlit fails in SaaS but works locally:
1. Check function signatures - do return values match caller expectations?
2. Verify YAML syntax - quote descriptions with colons
3. Test locally first: streamlit run main.py
4. Check imports and dependencies
5. Look for environment-specific differences
6. Add debug output to identify the exact failure point
```

## Build and Deploy Command Reference

### **CRITICAL: Use --env flag, NOT --config flag**

```bash
# ✅ CORRECT: Use --env with just the environment name
cdf build --env=hw-function          # Looks for config.hw-function.yaml
cdf deploy --env=hw-function --dry-run
cdf deploy --env=hw-function

# ❌ WRONG: Don't use --config with full filename
cdf build --config config.hw-function.yaml   # INCORRECT SYNTAX
```

The toolkit automatically adds "config." prefix and ".yaml" suffix when using --env flag.

### **Hello World Modules Deployment**

```bash
# Deploy hw-function (Function + Streamlit demo)
cdf build --env=hw-function
cdf deploy --env=hw-function --dry-run
cdf deploy --env=hw-function

# Deploy hw-neat (NEAT data model demo)
cdf build --env=hw-neat
cdf deploy --env=hw-neat --dry-run
cdf deploy --env=hw-neat

# Deploy all Hello World modules
cdf build --env=all-hw
cdf deploy --env=all-hw --dry-run
cdf deploy --env=all-hw
```

## Deployment Workflow Definition

**When you say "deploy [module] to [environment]", this always means:**

### **Step 1: Verify Environment Variables**
```bash
# Check if CDF_PROJECT is set and matches target environment
echo $CDF_PROJECT
echo $CDF_CLUSTER
```

### **Step 2: Set Environment (if not set)**
```bash
# If environment variables are not set or don't match target:
source cdfenv.sh
cdfenv [target-environment]  # e.g., cdfenv bgfast
```

### **Step 3: Verify Environment Variables Again**
```bash
# Confirm CDF_PROJECT matches target environment
echo $CDF_PROJECT  # Should show target environment name
echo $CDF_CLUSTER
```

### **Step 4: Build with Environment**
```bash
cdf build --env=[environment-config]  # e.g., --env=app-packages-dm
# This points toolkit to config.[environment-config].yaml file

# CRITICAL: Config file project field must be hardcoded
# ❌ WRONG: project: ${CDF_PROJECT}
# ✅ CORRECT: project: bgfast (actual project name)
# The toolkit validates that config project matches CDF_PROJECT env var
```

### **Step 5: Dry-run Deploy**
```bash
cdf deploy --env=[environment-config] --dry-run
# This uses the same config.[environment-config].yaml file
```

### **Step 6: Deploy**
```bash
cdf deploy --env=[environment-config]
# This uses the same config.[environment-config].yaml file
```

**IMPORTANT: Always use --env flag for both build and deploy commands to ensure toolkit uses the correct config.[env].yaml file**

**This ensures:**
- ✅ Correct environment is targeted
- ✅ Environment variables are properly set
- ✅ Latest code is built with correct config
- ✅ Changes are previewed before deployment
- ✅ Safe, intentional deployments to correct CDF project

### **Example: Deploy app-packages-dm to bgfast**
```bash
# Step 1: Check environment
echo $CDF_PROJECT
echo $CDF_CLUSTER

# Step 2: Set environment (if needed)
source cdfenv.sh
cdfenv bgfast

# Step 3: Verify environment
echo $CDF_PROJECT  # Should show "bgfast"

# Step 4: Build (uses config.app-packages-dm.yaml)
cdf build --env=app-packages-dm

# Step 5: Dry-run (uses config.app-packages-dm.yaml)
cdf deploy --env=app-packages-dm --dry-run

# Step 6: Deploy (uses config.app-packages-dm.yaml)
cdf deploy --env=app-packages-dm
```

### **Example: Deploy app-packages-zips to bgfast**
```bash
# Step 1-3: Same environment setup as above

# Step 4: Build (uses config.app-packages-zips.yaml)
cdf build --env=app-packages-zips

# Step 5: Dry-run (uses config.app-packages-zips.yaml)
cdf deploy --env=app-packages-zips --dry-run

# Step 6: Deploy (uses config.app-packages-zips.yaml)
cdf deploy --env=app-packages-zips
```
