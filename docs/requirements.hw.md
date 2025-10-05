# Hello World Modules - Requirements & Checklist

This document provides a comprehensive guide to deploying and verifying the Hello World modules for Cognite Data Fusion.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Module Overview](#module-overview)
3. [Installation Steps](#installation-steps)
4. [Configuration Files](#configuration-files)
5. [Deployment Checklist](#deployment-checklist)
6. [Verification Steps](#verification-steps)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| Python | 3.11+ | Runtime environment | [python.org](https://www.python.org/) |
| CDF Toolkit | Latest | Deployment tool | `pip install cognite-toolkit` |
| NEAT | Latest | Data modeling (hw-neat only) | `pip install cognite-neat` |
| Git | 2.0+ | Version control | [git-scm.com](https://git-scm.com/) |

### Required Access

- ✅ CDF Project access with appropriate permissions
- ✅ OAuth credentials (Client ID and Secret)
- ✅ Function deployment permissions
- ✅ Streamlit app deployment permissions
- ✅ Data model deployment permissions (for hw-neat)

### Environment Variables

Create a `.env` file or `cdfenv.sh` script with:

```bash
# CDF Connection
export CDF_PROJECT=your-project-name
export CDF_CLUSTER=your-cluster  # e.g., westeurope-1

# Authentication
export IDP_CLIENT_ID=your-client-id
export IDP_CLIENT_SECRET=your-client-secret
export IDP_SCOPES=your-scopes
export IDP_TENANT_ID=your-tenant-id
export IDP_TOKEN_URL=your-token-url

# Functions
export FUNCTION_CLIENT_ID=your-function-client-id
export FUNCTION_CLIENT_SECRET=your-function-client-secret
export TRANSFORMATION_CLIENT_ID=your-transformation-client-id
export TRANSFORMATION_CLIENT_SECRET=your-transformation-client-secret

# User Identity
export USER_IDENTIFIER=your-email@example.com
export SUPERUSER_SOURCEID_ENV=your-source-id
```

## Module Overview

### Hello World Modules

| Module | Purpose | Complexity | Time to Deploy | Dependencies |
|--------|---------|------------|----------------|--------------|
| **hw-function** | Function + Streamlit integration demo | Simple | 5 min | None |
| **hw-neat** | Excel-based data modeling with NEAT | Moderate | 10 min | NEAT library |

### What Gets Deployed

#### hw-function Module
- ✅ 1 Cognite Function (`hello-world-function`)
- ✅ 1 Streamlit App (`hello-world-streamlit`)
- ✅ 1 Dataset (`hw-function-dataset`)

#### hw-neat Module
- ✅ 1 Data Model Space (`hw-neat`)
- ✅ 1 Container (`HWNeatBasic`)
- ✅ 1 View (`HWNeatBasic`)
- ✅ 1 Data Model (`HWNeatDM`)
- ✅ 1 Streamlit App (`hw-neat`)
- ✅ 1 Dataset (`hw-neat-dataset`)

## Installation Steps

### Step 1: Clone or Download Repository

```bash
# If using git
git clone <repository-url>
cd cognite-quickstart

# Verify structure
ls -la modules/hw-function
ls -la modules/hw-neat
```

### Step 2: Install Dependencies

```bash
# Install CDF Toolkit
pip install cognite-toolkit

# Install NEAT (required for hw-neat module)
pip install cognite-neat

# Verify installations
cdf --version
python -c "import cognite.neat; print('NEAT OK')"
```

### Step 3: Configure Environment

```bash
# Option A: Use existing environment file
source ~/envs/your-env-file.sh

# Option B: Create new environment file
cp cdfenv.sh cdfenv.local.sh
# Edit cdfenv.local.sh with your credentials
source cdfenv.local.sh

# Verify environment
echo $CDF_PROJECT
echo $CDF_CLUSTER
```

### Step 4: Generate NEAT YAML Files (hw-neat only)

```bash
# Navigate to hw-neat module
cd modules/hw-neat

# Generate YAML files from Excel
python generate_edm_yaml_files.py

# Verify generation
ls -la data_models/data_models/
```

## Configuration Files

### Available Configurations

| Config File | Purpose | Modules Deployed |
|-------------|---------|------------------|
| `config.hw-function.yaml` | Function demo only | hw-function |
| `config.hw-neat.yaml` | NEAT demo only | hw-neat |
| `config.all-hw.yaml` | All Hello World modules | hw-function, hw-neat |

### Configuration Selection Guide

**Use `config.hw-function.yaml` when:**
- Learning Function-Streamlit integration
- Quick demo (5 minutes)
- No data modeling required

**Use `config.hw-neat.yaml` when:**
- Learning NEAT data modeling
- Excel-based model design
- CRUD operations via Streamlit

**Use `config.all-hw.yaml` when:**
- Comprehensive demo environment
- Learning multiple patterns
- Complete Hello World experience

## Deployment Checklist

### Pre-Deployment

- [ ] Python 3.11+ installed
- [ ] CDF Toolkit installed
- [ ] NEAT installed (if deploying hw-neat)
- [ ] Environment variables configured
- [ ] Authentication tested
- [ ] YAML files generated (for hw-neat)

### Deployment Commands

#### Option 1: Deploy All Hello World Modules

```bash
# Build
cdf build --config config.all-hw.yaml

# Dry run (recommended first)
cdf deploy --config config.all-hw.yaml --dry-run

# Deploy
cdf deploy --config config.all-hw.yaml
```

#### Option 2: Deploy Individual Modules

```bash
# Deploy hw-function only
cdf build --config config.hw-function.yaml
cdf deploy --config config.hw-function.yaml

# Deploy hw-neat only
cdf build --config config.hw-neat.yaml
cdf deploy --config config.hw-neat.yaml
```

### Post-Deployment

- [ ] Check deployment logs for errors
- [ ] Verify resources in CDF UI
- [ ] Test Streamlit apps
- [ ] Run verification tests
- [ ] Check function logs

## Verification Steps

### 1. Verify hw-function Module

#### A. Check Function Deployment

```bash
# Using CDF Toolkit
cdf functions list | grep hello-world-function
```

**In CDF UI:**
1. Navigate to **Functions**
2. Look for `hello-world-function`
3. Verify status is "Ready"

#### B. Check Streamlit App

**In CDF UI:**
1. Navigate to **Streamlit**
2. Look for `Hello World Function Demo`
3. Click to open the app

#### C. Test Function Call

1. Open the Streamlit app
2. Enter a name (e.g., "Test User")
3. Click **"Call Hello World Function"**
4. Verify you see:
   - ✅ "Function called! Call ID: ..."
   - ✅ "Status: Completed"
   - ✅ Function logs displayed
   - ✅ Greeting message: "Hello, Test User!"
   - ✅ Response metadata

#### D. Expected Response Structure

```json
{
  "greeting": "Hello, Test User!",
  "message": "This is a response from a Cognite Function",
  "timestamp": "2025-10-04T...",
  "metadata": {
    "python_version": "3.11.x",
    "project": "your-project",
    "function_id": "hello-world-function"
  },
  "success": true
}
```

### 2. Verify hw-neat Module

#### A. Check Data Model Deployment

```bash
# Check space
cdf spaces list | grep hw-neat

# Check data model
cdf data-models list | grep HWNeatDM

# Using Python
python -c "
from cognite.client import CogniteClient
client = CogniteClient()
spaces = client.data_modeling.spaces.list()
print('Spaces:', [s.space for s in spaces if 'hw-neat' in s.space])
"
```

**In CDF UI:**
1. Navigate to **Data Models**
2. Look for space `EDM-COR-ALL-NEAT` or `hw-neat`
3. Verify data model `HWNeatDM` exists
4. Check container `HWNeatBasic`
5. Verify view `HWNeatBasic`

#### B. Check Streamlit App

**In CDF UI:**
1. Navigate to **Streamlit**
2. Look for `Hello World NEAT` or similar
3. Click to open the app

#### C. Test CRUD Operations

**Create Instance:**
1. Open the Streamlit app
2. Select "Create New Instance" mode
3. Enter an external ID (e.g., `hw_test_001`)
4. Enter a string value (e.g., "Test data")
5. Click **"Create Instance"**
6. Verify success message

**View Instance:**
1. Switch to "View Existing Instances" mode
2. Look for your created instance
3. Verify data displays correctly

**Update Instance:**
1. Find your instance
2. Click edit/update
3. Modify the string value
4. Save changes
5. Verify update succeeded

**Delete Instance:**
1. Find your instance
2. Click delete
3. Confirm deletion
4. Verify instance is removed

#### D. Run Tests

```bash
# Navigate to module
cd modules/hw-neat

# Run test suite
python test_hw_neat.py

# Expected output
# ✅ Space tests passed
# ✅ Container tests passed
# ✅ View tests passed
# ✅ CRUD tests passed
# ✅ All tests passed!
```

### 3. Verify Complete Deployment (All Modules)

Run this verification script:

```bash
#!/bin/bash
echo "Verifying Hello World Modules..."

# Check hw-function
echo "Checking hw-function..."
cdf functions list | grep -q hello-world-function && echo "✅ Function deployed" || echo "❌ Function missing"

# Check hw-neat data model
echo "Checking hw-neat data model..."
cdf spaces list | grep -q hw-neat && echo "✅ Data model space deployed" || echo "❌ Space missing"

# Check Streamlit apps
echo "Checking Streamlit apps..."
cdf streamlit list | grep -q "Hello World" && echo "✅ Streamlit apps deployed" || echo "❌ Apps missing"

echo "Verification complete!"
```

## Troubleshooting

### Common Issues

#### Issue: "Module not found" during build

**Symptoms:**
```
Error: Cannot find module at modules/hw-function
```

**Solution:**
```bash
# Verify module exists
ls -la modules/hw-function

# Check you're in the correct directory
pwd  # Should show cognite-quickstart root

# Verify config file references correct path
grep "selected:" config.hw-function.yaml
```

#### Issue: Authentication fails

**Symptoms:**
```
Error: Unauthorized (401)
Error: Could not authenticate with CDF
```

**Solution:**
```bash
# Verify environment variables
echo $CDF_PROJECT
echo $IDP_CLIENT_ID

# Re-source environment file
source cdfenv.sh

# Test authentication
cdf auth verify
```

#### Issue: NEAT import error (hw-neat)

**Symptoms:**
```
ModuleNotFoundError: No module named 'cognite.neat'
```

**Solution:**
```bash
# Install NEAT
pip install cognite-neat

# Verify installation
python -c "import cognite.neat; print(cognite.neat.__version__)"
```

#### Issue: YAML generation fails (hw-neat)

**Symptoms:**
```
Error reading NeatBasic.xlsx
Error: File not found
```

**Solution:**
```bash
# Verify Excel file exists
ls -la modules/hw-neat/data_models/NeatBasic.xlsx

# Check file permissions
chmod 644 modules/hw-neat/data_models/NeatBasic.xlsx

# Regenerate
cd modules/hw-neat
python generate_edm_yaml_files.py
```

#### Issue: Function call timeout

**Symptoms:**
```
Function call timed out after 60 seconds
```

**Solution:**
1. Check function logs in CDF UI
2. Verify function is not in "Deploying" state
3. Wait for function to finish deploying
4. Try again after 2-3 minutes

#### Issue: Streamlit app won't load

**Symptoms:**
- Blank page
- "App failed to start" error
- Connection errors

**Solution:**
1. Check app status in CDF UI
2. View app logs (click app → Logs)
3. Verify authentication is configured
4. Check data model is deployed (for hw-neat)
5. Redeploy the module:
   ```bash
   cdf deploy --config config.hw-function.yaml --force
   ```

### Debug Commands

```bash
# Verbose build
cdf build --config config.all-hw.yaml -v

# Verbose deployment
cdf deploy --config config.all-hw.yaml -v

# Check build output
ls -la build/

# View specific resource
cdf functions retrieve hello-world-function
cdf streamlit retrieve hello-world-streamlit
cdf spaces retrieve hw-neat

# Check logs
cdf functions logs hello-world-function --tail 50
```

## File Management Reference

### Manually Maintained Files

**hw-function module:**
- `modules/hw-function/module.toml`
- `modules/hw-function/README.md`
- `modules/hw-function/functions/hello-world-function/handler.py`
- `modules/hw-function/functions/hello-world-function/requirements.txt`
- `modules/hw-function/functions/hello-world-function.Function.yaml`
- `modules/hw-function/streamlit/hello-world/main.py`
- `modules/hw-function/streamlit/hello-world/requirements.txt`
- `modules/hw-function/streamlit/HelloWorld.Streamlit.yaml`
- `modules/hw-function/data_sets/hw-function-dataset.DataSet.yaml`

**hw-neat module:**
- `modules/hw-neat/module.toml`
- `modules/hw-neat/README.md`
- `modules/hw-neat/data_models/HWNeatBasic.xlsx` ⭐ **SOURCE OF TRUTH**
- `modules/hw-neat/generate_edm_yaml_files.py`
- `modules/hw-neat/test_hw_neat.py`
- `modules/hw-neat/sample_data_generator.py`
- `modules/hw-neat/streamlit/hw-neat/main.py`
- `modules/hw-neat/streamlit/hw-neat/requirements.txt`
- `modules/hw-neat/streamlit/hw-neat.Streamlit.yaml`
- `modules/hw-neat/data_sets/hw-neat-dataset.DataSet.yaml`

### Generated Files (Do Not Edit)

**hw-neat module only:**
- `modules/hw-neat/data_models/data_models/**/*.yaml` - All YAML files in this directory
- Regenerate by running: `python modules/hw-neat/generate_edm_yaml_files.py`

## Quick Reference

### Deploy Everything

```bash
source cdfenv.sh
cdf build --config config.all-hw.yaml
cdf deploy --config config.all-hw.yaml
```

### Update Function Code

```bash
# Edit modules/hw-function/functions/hello-world-function/handler.py
cdf build --config config.hw-function.yaml
cdf deploy --config config.hw-function.yaml
```

### Update Data Model

```bash
# Edit modules/hw-neat/data_models/HWNeatBasic.xlsx
cd modules/hw-neat
python generate_edm_yaml_files.py
cd ../..
cdf build --config config.hw-neat.yaml
cdf deploy --config config.hw-neat.yaml
```

### Clean Up

```bash
# Remove deployed resources
cdf clean --config config.all-hw.yaml

# Remove build artifacts
rm -rf build/
```

## Success Criteria

Your Hello World deployment is successful when:

### hw-function Module ✅
- [ ] Function visible in CDF Functions list
- [ ] Streamlit app loads without errors
- [ ] Can enter name and call function
- [ ] Function executes and returns within 10 seconds
- [ ] Response shows greeting message
- [ ] Logs display in real-time
- [ ] Metadata includes correct project and function ID

### hw-neat Module ✅
- [ ] Space exists in CDF (verify in Data Models)
- [ ] Container deployed with correct properties
- [ ] View is queryable
- [ ] Streamlit app loads
- [ ] Can create new instances
- [ ] Can view existing instances
- [ ] Can update instances
- [ ] Can delete instances
- [ ] Test suite passes all tests

### Overall ✅
- [ ] All modules deploy without errors
- [ ] All Streamlit apps are accessible
- [ ] Documentation is clear and helpful
- [ ] Can successfully demonstrate to others

---

## Additional Resources

- **Main Documentation**: `README.md`
- **Function Module**: `readme.hw-function.md`
- **NEAT Module**: `readme.hw-neat.md`
- **Complete Guide**: `readme.hw-all.md`
- **Module READMEs**: 
  - `modules/hw-function/README.md`
  - `modules/hw-neat/README.md`

## Support

For issues or questions:
1. Check this requirements document
2. Review module-specific READMEs
3. Check CDF function and app logs
4. Consult [Cognite Developer Portal](https://developer.cognite.com)

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained By**: Cognite Quickstart Project
