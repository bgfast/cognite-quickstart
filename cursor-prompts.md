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

#### Build All Modules
```bash
cdf build
```

#### Build Specific Module
```bash
# App Packages Data Model (deploy first)
cdf build -m modules/app-packages-dm

# App Packages Zip Files
cdf build -m modules/app-packages-zips

# GitHub Repo Deployer
cdf build -m modules/admin/github-repo-deployer

# Live Weather Data
cdf build -m modules/in-development/live_weather_data

# Foundation
cdf build -m modules/common/foundation

# Valhall Data Model
cdf build -m modules/common/valhall_dm
```

#### Build with Environment
```bash
cdf build -e dev
cdf build -e staging
cdf build -e prod

# App packages specific environment
cdf build --env=app-packages-dm
```

### Deploy Commands

**📋 DEPLOYMENT WORKFLOW: "Deploy" always means: Build → Dry-run → Deploy**

**⚠️ IMPORTANT: Always run `--dry-run` first to preview changes before actual deployment!**

#### Deploy All (Full Workflow)
```bash
# Complete deployment workflow
cdf build
cdf deploy --dry-run
cdf deploy
```

#### Deploy Specific Module (Full Workflow)
```bash
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

### Streamlit Deployment Issues

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
├── streamlit/
│   ├── [AppName].Streamlit.yaml     ← Version in description (shows in SaaS list)
│   └── [externalId]/
│       ├── main.py                  ← Version in page_title & caption
│       ├── requirements.txt
│       └── services/
├── data_sets/
│   └── [app-name]-dataset.DataSet.yaml
├── module.toml
└── README.md
```

### Version Management Pattern (3 Required Locations)

#### 1. Streamlit YAML Configuration
```yaml
# [AppName].Streamlit.yaml
externalId: [app-external-id]
name: [App Display Name]
creator: [your-email]
description: v[X.XX] - [Brief feature description]  # ← CRITICAL: Shows in SaaS Streamlit list
published: true
theme: Light
entrypoint: main.py
dataSetExternalId: [app-name]-dataset
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
□ 4. Build: cdf build --env=[app-config]
□ 5. Dry-run: cdf deploy --env=[app-config] --dry-run
□ 6. Deploy: cdf deploy --env=[app-config]
□ 7. Verify version shows correctly in SaaS Streamlit list
```

### Config File Pattern
```yaml
# config.[app-name].yaml
environment:
  name: [app-name]
  type: dev
  selected:
    - modules/[app-name]
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

## File Locations

### Configuration Files
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
- `modules/app-packages-dm/` - Data model for app packages (foundational)
- `modules/app-packages-zips/` - Zip file management and uploads
- `modules/streamlit-github-deployer/` - Streamlit app for CDF-integrated GitHub deployment
- `modules/neat-basic/` - Basic data model generated with neat library
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

## Quick Commands Reference

```bash
# Full deployment workflow (with dry-run)
cdf build && cdf deploy --dry-run && cdf deploy

# Download packages and deploy (with dry-run)
cd modules/app-packages-zips/scripts/ && python download_packages.py && cd ../../.. && cdf build --env=app-packages-zips && cdf deploy --env=app-packages-zips --dry-run && cdf deploy --env=app-packages-zips

# Deploy Streamlit app
cdf build --env=streamlit-github-deployer && cdf deploy --env=streamlit-github-deployer --dry-run && cdf deploy --env=streamlit-github-deployer

# Check build status
ls -la build/

# View deployment logs (with dry-run first)
cdf deploy --dry-run -v
cdf deploy -v

# Clean and rebuild
rm -rf build/ && cdf build
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

## CDF Integration Patterns

### App Packages System
```bash
# Complete app packages workflow
cd modules/app-packages-zips/scripts/ && python download_packages.py
cdf build --env=app-packages-dm && cdf deploy --env=app-packages-dm --dry-run && cdf deploy --env=app-packages-dm
cdf build --env=app-packages-zips && cdf deploy --env=app-packages-zips --dry-run && cdf deploy --env=app-packages-zips
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

### "Create new Streamlit app from template"
```
Set up a new Streamlit app following the standard pattern:
1. Create module directory structure
2. Set up YAML with version in description
3. Create main.py with SaaS-compatible CogniteClient
4. Add version in 3 required locations
5. Create config file for deployment
```

### "Fix Streamlit SaaS deployment error"
```
Check and fix st.set_page_config() placement and version number consistency
```

### "Update Streamlit app version"
```
Update version in all 3 required locations following the standard checklist
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
