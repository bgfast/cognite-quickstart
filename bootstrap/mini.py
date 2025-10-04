"""
🚀 CDF Toolkit Bootstrap - Tier 1: Mini Bootstrap
==================================================

This script downloads the full interactive notebook from GitHub
and creates it in your Jupyter environment for inspection.

Usage:
    from cognite.client import CogniteClient
    import requests
    
    client = CogniteClient()
    exec(requests.get("https://raw.githubusercontent.com/bgfast/cognite-quickstart/main/bootstrap/mini.py").text)

What it does:
    1. Verifies you're connected to CDF
    2. Downloads the full notebook from GitHub
    3. Creates toolkit_bootstrap.ipynb in your Jupyter environment
    4. Tells you to open and run the notebook

Why use this:
    - Safest option - you can inspect the notebook before running
    - Best for first-time users
    - Best for security reviews
    - Educational - see all the steps
"""

print("🚀 CDF Toolkit Bootstrap - Mini (Tier 1)")
print("=" * 60)
print()

# Step 1: Verify CogniteClient
print("Step 1/3: Verifying CDF connection...")
try:
    from cognite.client import CogniteClient
    
    # Check if client is already initialized
    try:
        client  # noqa
        print(f"✅ Using existing client: {client.config.project}")
    except NameError:
        client = CogniteClient()
        print(f"✅ Connected to: {client.config.project}")
    
    print(f"   Cluster: {client.config.base_url}")
    print()
except Exception as e:
    print(f"❌ Failed to connect to CDF: {e}")
    print("💡 Make sure CogniteClient() works in your environment")
    raise

# Step 2: Download notebook from GitHub
print("Step 2/3: Downloading interactive notebook from GitHub...")
try:
    import requests
    import json
    
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap"
    NOTEBOOK_URL = f"{GITHUB_RAW_BASE}/toolkit_bootstrap.ipynb"
    
    print(f"   Source: {NOTEBOOK_URL}")
    
    response = requests.get(NOTEBOOK_URL, timeout=10)
    response.raise_for_status()
    
    notebook_content = response.json()
    
    print(f"✅ Downloaded notebook ({len(response.text)} bytes)")
    print(f"   Cells: {len(notebook_content.get('cells', []))}")
    print()
except requests.exceptions.RequestException as e:
    print(f"❌ Failed to download from GitHub: {e}")
    print("💡 Check internet connectivity and GitHub access")
    raise
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    raise

# Step 3: Create notebook file
print("Step 3/3: Creating notebook file...")
try:
    notebook_filename = "toolkit_bootstrap.ipynb"
    
    with open(notebook_filename, 'w', encoding='utf-8') as f:
        json.dump(notebook_content, f, indent=2)
    
    print(f"✅ Notebook created: {notebook_filename}")
    print()
except Exception as e:
    print(f"❌ Failed to create notebook file: {e}")
    print("💡 Check write permissions in current directory")
    raise

# Success!
print("=" * 60)
print("🎉 MINI BOOTSTRAP COMPLETE!")
print("=" * 60)
print()
print("📋 Next Steps:")
print(f"   1. Open '{notebook_filename}' in Jupyter")
print("   2. Review the cells to understand what they do")
print("   3. Run the cells one-by-one to deploy")
print()
print("📚 What the notebook will deploy:")
print("   • Dataset: streamlit-test-toolkit-dataset")
print("   • Function: test-toolkit-function (runs real cdf commands)")
print("   • Streamlit: test-toolkit-api (UI for testing)")
print()
print("💡 Tip: Read the cell comments to understand each step!")
print()

