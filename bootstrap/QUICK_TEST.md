# ⚡ Quick Test - Copy & Paste

## Test Tier 3 (One-Shot Deploy) - Start Here!

**Open CDF Jupyter and paste this:**

```python
from cognite.client import CogniteClient
import requests

client = CogniteClient()
print(f"📋 Deploying to: {client.config.project}")

deploy_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/deploy.py"
exec(requests.get(deploy_url).text)
```

**Expected**: Deployment completes in ~30-60 seconds

---

## Verify Deployment

```python
from cognite.client import CogniteClient
client = CogniteClient()

# Check all resources
dataset = client.data_sets.retrieve(external_id="streamlit-test-toolkit-dataset")
function = client.functions.retrieve(external_id="test-toolkit-function")
print(f"✅ Dataset: {dataset.name}")
print(f"✅ Function: {function.name} (status: {function.status})")
print(f"✅ Streamlit: Go to CDF UI → Apps → Streamlit → 'Test Toolkit API'")
```

---

## Test Function

```python
call_result = client.functions.call(
    external_id="test-toolkit-function",
    data={"test": "verification"}
)
print(f"✅ Function called: {call_result.id}")
print(f"   Check logs in CDF UI → Functions → test-toolkit-function")
```

---

## Open Streamlit UI

1. Go to **CDF UI** → **Apps** → **Streamlit**
2. Click **"Test Toolkit API"**
3. Click **"Call Function to Test Toolkit"**
4. Wait ~30 seconds
5. See **breakthrough confirmation** with metrics! 🎉

---

## Cleanup (After Testing)

```python
from cognite.client import CogniteClient
client = CogniteClient()

# Remove all test resources
try:
    client.streamlit.delete(external_id="test-toolkit-api")
except: 
    try: client.apps.delete(external_id="test-toolkit-api")
    except: pass

try: client.functions.delete(external_id="test-toolkit-function")
except: pass

try: client.data_sets.delete(external_id="streamlit-test-toolkit-dataset")
except: pass

print("🧹 Cleanup complete!")
```

---

**See [TESTING.md](TESTING.md) for full details and troubleshooting.**

