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

4. **GitHub Repo Deployer** (Streamlit app):
   ```bash
   # Full deployment workflow for Streamlit app
   cdf build -m modules/admin/github-repo-deployer
   cdf deploy -m modules/admin/github-repo-deployer --dry-run
   cdf deploy -m modules/admin/github-repo-deployer
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
cdf build --env=[config-name] -v

# Check for missing environment variables
echo $CDF_PROJECT
echo $CDF_CLUSTER
```

### Deployment Issues
```bash
# Missing environment variables
source cdfenv.sh
cdfenv [target-environment]

# Wrong config file being used
# Always use --env flag: cdf build --env=app-packages-dm

# CogniteFile/Node property errors
# Only use properties that exist in the CDF view (remove custom properties)
```

### Authentication Issues
```bash
# Check GitHub authentication
gh auth status

# Check CDF authentication
# Verify your environment file has correct credentials

# GitHub token for private repos
export GITHUB_TOKEN=$(gh auth token)
```

### Module Dependencies
- `app-packages-dm` must be deployed before `app-packages-zips`
- `foundation` should be deployed before other modules
- `valhall_dm` is required for weather data modules
- Don't duplicate datasets across modules (define once in base module)

### CogniteFile/Data Model Issues
```bash
# Common errors and fixes:

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
- `config.app-packages-dm.yaml` - App packages data model config
- `cdfenv.sh` - Environment variables template

### Module Directories
- `modules/app-packages-dm/` - Data model for app packages
- `modules/app-packages-zips/` - Zip file management
- `modules/admin/github-repo-deployer/` - Streamlit app for GitHub deployment
- `modules/common/foundation/` - Basic CDF setup
- `modules/common/valhall_dm/` - Valhall data model
- `modules/in-development/live_weather_data/` - Weather data integration

### Build Output
- `build/` - Generated configuration files ready for deployment

## Quick Commands Reference

```bash
# Full deployment workflow (with dry-run)
cdf build --env=[config-name] && cdf deploy --env=[config-name] --dry-run && cdf deploy --env=[config-name]

# Download packages and deploy (with dry-run)
cd modules/app-packages-zips/scripts/ && python download_packages.py && cd ../../.. && cdf build --env=app-packages-zips && cdf deploy --env=app-packages-zips --dry-run && cdf deploy --env=app-packages-zips

# Check build status
ls -la build/

# View deployment logs (with dry-run first)
cdf deploy --env=[config-name] --dry-run -v
cdf deploy --env=[config-name] -v

# Clean and rebuild
rm -rf build/ && cdf build --env=[config-name]
```

## Git Workflow

### Creating and Merging PRs
```bash
# Check current status
git status

# Add all changes (recommended approach)
git add .

# Commit with descriptive message
git commit -m "feat: description of changes"

# Push feature branch
git push origin [branch-name]

# Create PR
gh pr create --title "Title" --body "Description"

# Merge PR
gh pr merge [pr-number] --merge

# Switch to main and pull
git checkout main
git pull origin main
```

### Important Git Notes
- **Always use `git add .`** to capture all changes
- **Zip files are in .gitignore** - they're regenerated by download script
- **Include all related changes** in one PR (don't split unnecessarily)
- **Use descriptive commit messages** with feat:/fix:/docs: prefixes
- **Remove large binary files** from tracking if accidentally committed
- **Use `git rm --cached [file]`** to untrack files without deleting them

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

## Useful Cursor AI Prompts

### "Deploy app-packages-dm to bgfast"
```
Execute the full deployment workflow for app-packages-dm to bgfast environment:
1. Verify CDF_PROJECT environment variables
2. Set environment if needed (source cdfenv.sh && cdfenv bgfast)
3. Verify CDF_PROJECT matches bgfast
4. Build with --env=app-packages-dm
5. Dry-run deploy
6. Deploy
```

### "Deploy app-packages-zips to bgfast"  
```
Execute the full deployment workflow for app-packages-zips to bgfast environment with proper environment verification
```

### "Deploy all app packages modules to bgfast"
```
Deploy the complete app packages system to bgfast in order: foundation → app-packages-dm → app-packages-zips → github-repo-deployer
```

### "Download the latest GitHub repositories"
```
Run the download script in modules/app-packages-zips/scripts/ to get the latest versions of all configured repositories
```

### "Add a new repository to download"
```
Add a new GitHub repository to the repositories.yaml file and test the download
```

### "Check module deployment status"
```
Verify that all modules are built correctly and check the build directory contents
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

**CRITICAL: Always use --env flag for both build and deploy commands to ensure toolkit uses the correct config.[env].yaml file**

**Common --env values:**
- `--env=app-packages-dm` → uses `config.app-packages-dm.yaml`
- `--env=app-packages-zips` → uses `config.app-packages-zips.yaml`
- `--env=dev` → uses `config.dev.yaml`
- `--env=staging` → uses `config.staging.yaml`
- `--env=prod` → uses `config.prod.yaml`

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
