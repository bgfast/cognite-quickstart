# 🚀 CDF Toolkit Bootstrap

**One-command deployment of the breakthrough Functions-based toolkit solution**

This bootstrap deploys a working solution that enables real `cognite-toolkit` functionality from Streamlit SaaS by using Cognite Functions as a backend.

## 🎯 What Gets Deployed

When you run the bootstrap, it deploys:

1. **Cognite Function**: `test-toolkit-function`
   - Installs and runs real `cognite-toolkit` CLI commands
   - Executes `cdf build`, `cdf deploy`, `cdf deploy --dry-run`
   - Full Python environment with subprocess support

2. **Streamlit App**: `test-toolkit-api`
   - User interface for testing toolkit functionality
   - Calls the Function and displays results
   - Shows breakthrough confirmation with metrics

3. **Dataset**: `streamlit-test-toolkit-dataset`
   - Required dataset for Streamlit app

## 📋 Requirements

### CDF Prerequisites
- ✅ CogniteClient() authentication working
- ✅ Functions write capability
- ✅ Streamlit write capability
- ✅ DataSets write capability
- ✅ Internet access to GitHub

### Environment
- **CDF Jupyter** (Recommended) - Works in CDF's Jupyter environment
- **Local Jupyter** - Works in local Jupyter with CDF credentials
- **Python REPL** - Works in any Python environment with CogniteClient

### Python Requirements
```python
cognite-sdk >= 7.0
requests >= 2.0
```

## 🚀 Quick Start - Choose Your Approach

### Tier 1: Mini Bootstrap (Safest - 7 lines)
**For cautious users who want to inspect before deploying**

Copy and paste into CDF Jupyter:

```python
# 🚀 CDF Toolkit Bootstrap - Tier 1: Mini Bootstrap
from cognite.client import CogniteClient
import requests

client = CogniteClient()
print(f"📋 Connected to: {client.config.project}")

mini_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/mini.py"
exec(requests.get(mini_url).text)
```

**What happens:**
- Downloads the full interactive notebook from GitHub
- Creates `toolkit_bootstrap.ipynb` in your Jupyter environment
- You can then **inspect the notebook** before running it
- Run the notebook cells step-by-step with full visibility

**When to use:** First time deploying, want to understand each step, security review required

---

### Tier 2: Interactive Notebook (Recommended)
**For users who want step-by-step deployment with explanations**

1. Run Tier 1 Mini Bootstrap (above) to create the notebook
2. Open `toolkit_bootstrap.ipynb` in Jupyter
3. Run cells one-by-one to deploy each component
4. See detailed progress and explanations at each step

**What you'll see:**
- Cell 1: Setup & validation
- Cell 2: Create dataset
- Cell 3: Deploy Cognite Function
- Cell 4: Deploy Streamlit app
- Cell 5: Verify & test deployment
- Cell 6: Next steps & documentation

**When to use:** Interactive deployment, learning how it works, troubleshooting

---

### Tier 3: One-Shot Deploy (Fastest)
**For confident users who trust the process**

Copy and paste into CDF Jupyter:

```python
# 🚀 CDF Toolkit Bootstrap - Tier 3: One-Shot Deploy
from cognite.client import CogniteClient
import requests

client = CogniteClient()
print(f"📋 Deploying to: {client.config.project}")

deploy_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/deploy.py"
exec(requests.get(deploy_url).text)

# ✅ Done! Check Apps → Streamlit → "Test Toolkit API"
```

**What happens:**
- Automatically deploys all components
- Shows progress for each step
- Runs verification tests
- Prints success message with next steps
- **~30 seconds total time**

**When to use:** Re-deployment, CI/CD pipelines, automated setup, experienced users

---

## 📂 File Structure

```
bootstrap/
├── README.md                           # This file
├── mini.py                            # Tier 1: Bootstrap the bootstrap
├── toolkit_bootstrap.ipynb            # Tier 2: Interactive notebook
├── deploy.py                          # Tier 3: One-shot deployment
├── generate_notebook.py               # Helper: Regenerate notebook from template
└── .gitignore                         # Exclude cache files
```

**Note**: Both `toolkit_bootstrap.ipynb` and `generate_notebook.py` are tracked in Git. Edit the notebook directly in Jupyter or use Cursor's `edit_notebook` tool. Use `generate_notebook.py` only for major structural changes.

## 🔧 Configuration Options

All tiers support optional configuration:

```python
# Custom external IDs
DATASET_EXTERNAL_ID = "my-custom-dataset"
FUNCTION_EXTERNAL_ID = "my-custom-function"
STREAMLIT_EXTERNAL_ID = "my-custom-streamlit"

# Then run bootstrap with environment variables or modify the scripts
```

## ✅ Verification

After deployment, verify everything works:

### Manual Verification
1. Go to **CDF UI → Integrate → Functions**
   - Find `test-toolkit-function`
   - Check status is "Ready"

2. Go to **CDF UI → Apps → Streamlit**
   - Find `test-toolkit-api`
   - Click to open the app

3. In the Streamlit app:
   - Click "Call Function to Test Toolkit"
   - Wait for function to complete (~30 seconds)
   - See breakthrough confirmation with metrics

### Programmatic Verification
```python
from cognite.client import CogniteClient
client = CogniteClient()

# Verify dataset
dataset = client.data_sets.retrieve(external_id="streamlit-test-toolkit-dataset")
print(f"✅ Dataset: {dataset.name}")

# Verify function
function = client.functions.retrieve(external_id="test-toolkit-function")
print(f"✅ Function: {function.name}")

# Verify Streamlit
streamlit = client.apps.retrieve(external_id="test-toolkit-api")
print(f"✅ Streamlit: {streamlit.name}")

# Test function call
result = client.functions.call(
    external_id="test-toolkit-function",
    data={"test": "verification"}
)
print(f"✅ Function call: {result.id}")
```

## 🗑️ Cleanup

To remove all deployed resources:

```python
from cognite.client import CogniteClient
client = CogniteClient()

# Remove Streamlit app
try:
    client.apps.delete(external_id="test-toolkit-api")
    print("✅ Streamlit app removed")
except: pass

# Remove Function
try:
    client.functions.delete(external_id="test-toolkit-function")
    print("✅ Function removed")
except: pass

# Remove Dataset (optional - only if not used by other resources)
try:
    client.data_sets.delete(external_id="streamlit-test-toolkit-dataset")
    print("✅ Dataset removed")
except: pass
```

## 🐛 Troubleshooting

### "Cannot reach GitHub"
- Check internet connectivity
- Verify firewall allows GitHub access
- Try accessing the raw GitHub URL in a browser

### "Missing capabilities"
- Ensure your user/service account has:
  - `functions:write`
  - `apps:write` (for Streamlit)
  - `datasets:write`

### "Function deployment failed"
- Check function code downloaded correctly
- Verify handler.py syntax
- Check Functions quota limits

### "Streamlit app not visible"
- Wait 1-2 minutes for deployment
- Refresh the Streamlit apps page
- Check dataset was created successfully

### "Function call failed"
- Function may still be deploying (wait 1-2 minutes)
- Check function logs in CDF UI
- Verify function has correct requirements.txt

## 📚 What's Next

After successful deployment:

1. **Test the Breakthrough**
   - Open the Streamlit app
   - Click "Call Function to Test Toolkit"
   - See real `cdf` commands working!

2. **Understand the Architecture**
   - Read the function code to see how it works
   - Understand the Streamlit → Function → Toolkit flow
   - See how PATH is fixed for CLI commands

3. **Build on It**
   - Extend the function to accept config files
   - Add real build/deploy workflows
   - Integrate with your own Streamlit apps

4. **Share the Knowledge**
   - This proves toolkit works in Functions!
   - CLI-based approach is the correct pattern
   - No need to import toolkit as Python library

## 🎓 Background

### The Breakthrough

This solution solves a fundamental challenge: **How to use cognite-toolkit from Streamlit SaaS?**

**The Problem:**
- Streamlit SaaS runs in Pyodide (browser Python)
- cognite-toolkit has native dependencies
- Cannot install toolkit in Pyodide
- Cannot use subprocess in browser

**The Solution:**
- Use Cognite Functions (full Python environment)
- Install toolkit in Functions (works!)
- Call Functions from Streamlit via HTTP
- Functions run CLI commands and return results

**The Discovery:**
- cognite-toolkit is a **CLI tool**, not a Python library
- The `cdf` command is what matters
- Trying to import it as a library was the wrong approach
- CLI via subprocess is the correct pattern

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Streamlit SaaS (Pyodide - Limited Environment)         │
│  - User interface                                       │
│  - Display results                                      │
│  - Call Functions via HTTP                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ HTTP Function Call
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Cognite Functions (Full Python - Unlimited)            │
│  - pip install cognite-toolkit ✅                       │
│  - subprocess.run(['cdf', 'build']) ✅                  │
│  - Full file system access ✅                           │
│  - All Python libraries ✅                              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ subprocess
                  ▼
┌─────────────────────────────────────────────────────────┐
│ cognite-toolkit CLI                                     │
│  - cdf build                                            │
│  - cdf deploy --dry-run                                 │
│  - cdf deploy                                           │
└─────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

Found an issue or want to improve the bootstrap?

1. File an issue in the GitHub repo
2. Submit a pull request with improvements
3. Share your experience and learnings

## 📄 License

This bootstrap solution is part of the cognite-quickstart project.

## 🔗 Links

- **GitHub Repo**: https://github.com/bgfast/cognite-quickstart
- **Function Code**: [modules/test-toolkit-api/functions/test-toolkit-function/](../modules/test-toolkit-api/functions/test-toolkit-function/)
- **Streamlit Code**: [modules/test-toolkit-api/streamlit/test-toolkit-api/](../modules/test-toolkit-api/streamlit/test-toolkit-api/)
- **Documentation**: [cursor-prompts.md](../cursor-prompts.md)

---

**Made with ❤️ for the Cognite community**

*Last updated: October 3, 2025*

