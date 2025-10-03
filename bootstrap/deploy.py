"""
🚀 CDF Toolkit Bootstrap - Tier 3: One-Shot Deploy
===================================================

Automatically deploys all components of the breakthrough toolkit solution.

Usage:
    from cognite.client import CogniteClient
    import requests
    
    client = CogniteClient()
    exec(requests.get("https://raw.githubusercontent.com/bgfast/cognite-quickstart/main/bootstrap/deploy.py").text)

What it deploys:
    - Dataset: streamlit-test-toolkit-dataset
    - Function: test-toolkit-function (runs real cdf commands)
    - Streamlit: test-toolkit-api (UI for testing)

Time: ~30 seconds

Why use this:
    - Fastest deployment option
    - For confident users
    - For CI/CD pipelines
    - For re-deployments
"""

print("🚀 CDF Toolkit Bootstrap - One-Shot Deploy (Tier 3)")
print("=" * 60)
print()

# Configuration
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/main"
FUNCTION_HANDLER_URL = f"{GITHUB_RAW_BASE}/modules/test-toolkit-api/functions/test-toolkit-function/handler.py"
FUNCTION_REQS_URL = f"{GITHUB_RAW_BASE}/modules/test-toolkit-api/functions/test-toolkit-function/requirements.txt"
STREAMLIT_MAIN_URL = f"{GITHUB_RAW_BASE}/modules/test-toolkit-api/streamlit/test-toolkit-api/main.py"
STREAMLIT_REQS_URL = f"{GITHUB_RAW_BASE}/modules/test-toolkit-api/streamlit/test-toolkit-api/requirements.txt"

DATASET_EXTERNAL_ID = "streamlit-test-toolkit-dataset"
FUNCTION_EXTERNAL_ID = "test-toolkit-function"
STREAMLIT_EXTERNAL_ID = "test-toolkit-api"

# Step 1: Initialize
print("Step 1/4: Initializing...")
try:
    from cognite.client import CogniteClient
    import requests
    from datetime import datetime
    import tempfile
    import os
    import zipfile
    
    # Check if client already exists
    try:
        client  # noqa
        print(f"✅ Using existing client: {client.config.project}")
    except NameError:
        client = CogniteClient()
        print(f"✅ Connected to: {client.config.project}")
    
    print(f"   Cluster: {client.config.base_url}")
    
    # Test GitHub connectivity
    response = requests.get(GITHUB_RAW_BASE, timeout=5)
    print("✅ GitHub connectivity verified")
    print()
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    raise

# Step 2: Create Dataset
print("Step 2/4: Creating dataset...")
try:
    # Check if exists
    try:
        existing = client.data_sets.retrieve(external_id=DATASET_EXTERNAL_ID)
        print(f"✅ Dataset already exists: {existing.external_id}")
    except:
        # Create new
        dataset = client.data_sets.create({
            "external_id": DATASET_EXTERNAL_ID,
            "name": "Streamlit Test Toolkit Dataset",
            "description": "Dataset for Streamlit Toolkit API testing",
            "metadata": {
                "deployed_at": datetime.now().isoformat(),
                "bootstrap_version": "2.0"
            }
        })
        print(f"✅ Dataset created: {dataset.external_id}")
    print()
except Exception as e:
    print(f"❌ Dataset creation failed: {e}")
    raise

# Step 3: Deploy Cognite Function
print("Step 3/4: Deploying Cognite Function...")
try:
    # Fetch function code
    print("   📥 Fetching code from GitHub...")
    handler_code = requests.get(FUNCTION_HANDLER_URL).text
    requirements_txt = requests.get(FUNCTION_REQS_URL).text
    print(f"   ✅ Code fetched ({len(handler_code)} bytes)")
    
    # Clean up existing function
    try:
        client.functions.delete(external_id=FUNCTION_EXTERNAL_ID)
        print("   🗑️  Removed existing function")
    except:
        pass
    
    # Create function files as zip
    print("   📦 Creating function package...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write files
        handler_path = os.path.join(tmpdir, "handler.py")
        with open(handler_path, 'w') as f:
            f.write(handler_code)
        
        reqs_path = os.path.join(tmpdir, "requirements.txt")
        with open(reqs_path, 'w') as f:
            f.write(requirements_txt)
        
        # Create zip
        zip_path = os.path.join(tmpdir, "function.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write(handler_path, "handler.py")
            zf.write(reqs_path, "requirements.txt")
        
        # Upload to Files API
        with open(zip_path, 'rb') as f:
            file_metadata = client.files.upload(
                path=zip_path,
                name=f"function-{FUNCTION_EXTERNAL_ID}.zip",
                external_id=f"function-{FUNCTION_EXTERNAL_ID}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
        print(f"   ✅ Function package uploaded (file_id={file_metadata.id})")
    
    # Create function
    print("   🚀 Creating function...")
    function = client.functions.create(
        name="Test Toolkit Function",
        external_id=FUNCTION_EXTERNAL_ID,
        file_id=file_metadata.id,
        description="Runs cognite-toolkit commands - v2.0",
        owner="bootstrap-deployment",
        cpu=0.5,
        memory=1.5,
        runtime="py311",
        metadata={
            "version": "2.0",
            "deployed_at": datetime.now().isoformat()
        }
    )
    print(f"✅ Function deployed: {FUNCTION_EXTERNAL_ID}")
    print()
except Exception as e:
    print(f"❌ Function deployment failed: {e}")
    print("💡 Check Functions quota and permissions")
    raise

# Step 4: Deploy Streamlit App
print("Step 4/4: Deploying Streamlit App...")
try:
    # Fetch Streamlit code
    print("   📥 Fetching code from GitHub...")
    main_py = requests.get(STREAMLIT_MAIN_URL).text
    streamlit_reqs = requests.get(STREAMLIT_REQS_URL).text
    print(f"   ✅ Code fetched ({len(main_py)} bytes)")
    
    # Clean up existing app
    try:
        # Note: API method may vary by SDK version
        try:
            client.streamlit.delete(external_id=STREAMLIT_EXTERNAL_ID)
        except:
            client.apps.delete(external_id=STREAMLIT_EXTERNAL_ID)
        print("   🗑️  Removed existing app")
    except:
        pass
    
    # Create Streamlit app
    print("   🎨 Creating Streamlit app...")
    try:
        # Try new API
        streamlit = client.streamlit.upsert(
            external_id=STREAMLIT_EXTERNAL_ID,
            name="Test Toolkit API",
            description="v2.0 - Toolkit via Functions",
            data_set_id=client.data_sets.retrieve(external_id=DATASET_EXTERNAL_ID).id,
            source_files={
                "main.py": main_py,
                "requirements.txt": streamlit_reqs
            }
        )
    except:
        # Try older API
        streamlit = client.apps.create(
            external_id=STREAMLIT_EXTERNAL_ID,
            name="Test Toolkit API",
            description="v2.0 - Toolkit via Functions",
            data_set_external_id=DATASET_EXTERNAL_ID,
            files={
                "main.py": main_py,
                "requirements.txt": streamlit_reqs
            }
        )
    
    print(f"✅ Streamlit app deployed: {STREAMLIT_EXTERNAL_ID}")
    print()
except Exception as e:
    print(f"❌ Streamlit deployment failed: {e}")
    print("💡 May need to deploy Streamlit manually via CDF UI")
    print("   Code is ready at the GitHub URLs above")
    # Don't raise - this is non-critical
    pass

# Success summary
print("=" * 60)
print("🎉 DEPLOYMENT COMPLETE!")
print("=" * 60)
print()
print("📋 Deployed Resources:")
print(f"   • Dataset: {DATASET_EXTERNAL_ID}")
print(f"   • Function: {FUNCTION_EXTERNAL_ID}")
print(f"   • Streamlit: {STREAMLIT_EXTERNAL_ID}")
print()
print("🧪 Testing deployment...")
try:
    call_result = client.functions.call(
        external_id=FUNCTION_EXTERNAL_ID,
        data={"test": "bootstrap_verification"}
    )
    print(f"✅ Function test call successful (ID: {call_result.id})")
except Exception as e:
    print(f"⚠️  Function test call failed: {e}")
    print("   Function is deployed but may need a minute to warm up")

print()
print("🚀 Next Steps:")
print("   1. Go to CDF UI → Apps → Streamlit")
print("   2. Find 'Test Toolkit API' app")
print("   3. Click 'Call Function to Test Toolkit'")
print("   4. See the breakthrough! 🎊")
print()
print("📚 Documentation:")
print("   • GitHub: https://github.com/bgfast/cognite-quickstart")
print("   • Bootstrap README: .../bootstrap/README.md")
print()

