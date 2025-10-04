# 🧪 Bootstrap Testing Guide

## Testing from a Clean CDF Project

### Prerequisites
- ✅ Clean CDF project (or test environment)
- ✅ CogniteClient() works (authenticated)
- ✅ Required capabilities:
  - `datasets:write`
  - `functions:write`
  - `apps:write` (for Streamlit)

### Test Environment Setup

**Option A: CDF Jupyter (Recommended)**
1. Open CDF UI → **Integrate** → **Jupyter**
2. Create new notebook
3. Verify connection:
```python
from cognite.client import CogniteClient
client = CogniteClient()
print(f"Connected to: {client.config.project}")
```

**Option B: Local Jupyter**
1. Ensure environment variables are set
2. Launch Jupyter
3. Verify `CogniteClient()` works

---

## 🎯 Testing All Three Tiers

### **Test 1: Tier 3 (One-Shot Deploy)** ⚡ **Start Here**

**Why test this first**: Fastest way to verify everything works end-to-end.

```python
from cognite.client import CogniteClient
import requests

client = CogniteClient()
print(f"📋 Deploying to: {client.config.project}")

deploy_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/deploy.py"
exec(requests.get(deploy_url).text)
```

**Expected Output**:
```
🚀 CDF Toolkit Bootstrap - One-Shot Deploy (Tier 3)
============================================================

Step 1/4: Initializing...
✅ Connected to: your-project-name
   Cluster: https://your-cluster.cognitedata.com
✅ GitHub connectivity verified

Step 2/4: Creating dataset...
✅ Dataset created: streamlit-test-toolkit-dataset

Step 3/4: Deploying Cognite Function...
   📥 Fetching code from GitHub...
   ✅ Code fetched (XXXX bytes)
   🗑️  Removed existing function (if any)
   📦 Creating function package...
   ✅ Package created: XXXX bytes
   📤 Uploading to CDF Files...
   ✅ Uploaded: file_id=XXXXX
   🚀 Creating function...
✅ Function deployed: test-toolkit-function

Step 4/4: Deploying Streamlit App...
   📥 Fetching code from GitHub...
   ✅ Code fetched (XXXX bytes)
   🎨 Creating Streamlit app...
✅ Streamlit app deployed: test-toolkit-api

============================================================
🎉 DEPLOYMENT COMPLETE!
============================================================

📋 Deployed Resources:
   • Dataset: streamlit-test-toolkit-dataset
   • Function: test-toolkit-function
   • Streamlit: test-toolkit-api

🧪 Testing deployment...
✅ Function test call successful (ID: XXXXX)

🚀 Next Steps:
   1. Go to CDF UI → Apps → Streamlit
   2. Find 'Test Toolkit API' app
   3. Click 'Call Function to Test Toolkit'
   4. See the breakthrough! 🎊
```

**Time**: ~30-60 seconds

**Verification**:
1. Check CDF UI → **Integrate** → **Functions**
   - Should see `test-toolkit-function` with status "Ready"
2. Check CDF UI → **Apps** → **Streamlit**
   - Should see `test-toolkit-api` app
3. Check CDF UI → **Data management** → **Datasets**
   - Should see `streamlit-test-toolkit-dataset`

---

### **Test 2: Tier 1 (Mini Bootstrap)** 🛡️ **Most Cautious**

**Purpose**: Downloads notebook for inspection before deployment.

```python
from cognite.client import CogniteClient
import requests

client = CogniteClient()
print(f"📋 Connected to: {client.config.project}")

mini_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/mini.py"
exec(requests.get(mini_url).text)
```

**Expected Output**:
```
🚀 CDF Toolkit Bootstrap - Mini (Tier 1)
============================================================

Step 1/3: Verifying CDF connection...
✅ Connected to: your-project-name
   Cluster: https://your-cluster.cognitedata.com

Step 2/3: Downloading interactive notebook from GitHub...
   Source: https://raw.githubusercontent.com/.../toolkit_bootstrap.ipynb
✅ Downloaded notebook (XXXX bytes)
   Cells: 13

Step 3/3: Creating notebook file...
✅ Notebook created: toolkit_bootstrap.ipynb

============================================================
🎉 MINI BOOTSTRAP COMPLETE!
============================================================

📋 Next Steps:
   1. Open 'toolkit_bootstrap.ipynb' in Jupyter
   2. Review the cells to understand what they do
   3. Run the cells one-by-one to deploy
```

**Verification**:
- Check for `toolkit_bootstrap.ipynb` in your Jupyter file browser
- Open it and inspect the 13 cells
- Should see markdown and code cells with deployment logic

---

### **Test 3: Tier 2 (Interactive Notebook)** 📚 **Educational**

**Purpose**: Step-by-step deployment with explanations.

**Prerequisites**: Run Test 2 first to create the notebook, OR download directly:
```python
import requests
notebook_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/oct_mods/bootstrap/toolkit_bootstrap.ipynb"
with open("toolkit_bootstrap.ipynb", "w") as f:
    f.write(requests.get(notebook_url).text)
```

**Steps**:
1. Open `toolkit_bootstrap.ipynb` in Jupyter
2. Run cells in order (or Cell → Run All)
3. Watch each step deploy with detailed output

**Expected Cells**:
- Cell 1: Introduction
- Cell 2: Configuration
- Cell 3: Initialize & Verify
- Cell 4: Create Dataset
- Cell 5: Deploy Function
- Cell 6: Deploy Streamlit
- Cell 7: Verify & Test

---

## ✅ Full Verification Steps

After any tier completes, verify the deployment:

### 1. Check Dataset
```python
from cognite.client import CogniteClient
client = CogniteClient()

dataset = client.data_sets.retrieve(external_id="streamlit-test-toolkit-dataset")
print(f"✅ Dataset: {dataset.name}")
print(f"   ID: {dataset.id}")
```

### 2. Check Function
```python
function = client.functions.retrieve(external_id="test-toolkit-function")
print(f"✅ Function: {function.name}")
print(f"   Status: {function.status}")
print(f"   ID: {function.id}")
```

### 3. Check Streamlit
```python
# Try both API methods depending on SDK version
try:
    streamlit = client.streamlit.retrieve(external_id="test-toolkit-api")
except:
    streamlit = client.apps.retrieve(external_id="test-toolkit-api")
print(f"✅ Streamlit: Test Toolkit API")
print(f"   External ID: {streamlit.external_id}")
```

### 4. Test Function Call
```python
call_result = client.functions.call(
    external_id="test-toolkit-function",
    data={"test": "verification"}
)
print(f"✅ Function call successful!")
print(f"   Call ID: {call_result.id}")
print(f"   Status: {call_result.status}")

# Wait for completion (optional)
import time
for i in range(30):
    status = client.functions.calls.retrieve(function_call_id=call_result.id)
    if status.status in ["Completed", "Failed"]:
        print(f"   Final status: {status.status}")
        if status.status == "Completed":
            print(f"   Response: {status.response}")
        break
    time.sleep(2)
```

### 5. Test Streamlit UI
1. Go to **CDF UI** → **Apps** → **Streamlit**
2. Find **Test Toolkit API** app
3. Click to open the app
4. Should see "Trial 3: Cognite Functions Approach"
5. Click **"Call Function to Test Toolkit"** button
6. Wait ~30 seconds
7. Should see breakthrough confirmation with metrics:
   - ✅ Toolkit installed
   - ✅ cdf command available
   - ✅ PATH fixed
   - ✅ Build/deploy commands tested

---

## 🐛 Troubleshooting

### Issue: "Cannot reach GitHub"
```
❌ Failed to download from GitHub: HTTPError 404
```
**Fix**: Branch name may be wrong. Try:
```python
# Try main branch instead of oct_mods
deploy_url = "https://raw.githubusercontent.com/bgfast/cognite-quickstart/main/bootstrap/deploy.py"
```

### Issue: "Missing capabilities"
```
❌ CogniteAPIError: Missing required capability
```
**Fix**: 
1. Check your user/service account has required capabilities
2. Contact CDF admin to grant:
   - `datasets:write`
   - `functions:write`
   - `apps:write`

### Issue: Function deployment fails
```
❌ Function deployment failed: Quota exceeded
```
**Fix**:
1. Check Functions quota in CDF
2. Delete unused functions
3. Contact support to increase quota

### Issue: Streamlit API error
```
❌ AttributeError: 'CogniteClient' object has no attribute 'streamlit'
```
**Fix**:
- SDK version may be old
- Deploy Streamlit manually via CDF UI
- Use the code from GitHub URLs shown in output

### Issue: Function call times out
```
⚠️ Function test call failed: Timeout
```
**Fix**:
- Function is deployed but needs warm-up time
- Wait 1-2 minutes and try again
- Check function logs in CDF UI → Functions

---

## 🧹 Cleanup (After Testing)

To remove all deployed resources:

```python
from cognite.client import CogniteClient
client = CogniteClient()

# Remove Streamlit
try:
    client.streamlit.delete(external_id="test-toolkit-api")
    print("✅ Streamlit removed")
except:
    try:
        client.apps.delete(external_id="test-toolkit-api")
        print("✅ Streamlit removed")
    except: pass

# Remove Function
try:
    client.functions.delete(external_id="test-toolkit-function")
    print("✅ Function removed")
except: pass

# Remove Dataset (optional - only if not used elsewhere)
try:
    client.data_sets.delete(external_id="streamlit-test-toolkit-dataset")
    print("✅ Dataset removed")
except: pass

print("\n🧹 Cleanup complete!")
```

---

## 📊 Success Criteria

Bootstrap is successful if:
- ✅ All 3 resources deployed (dataset, function, streamlit)
- ✅ Function status shows "Ready"
- ✅ Function call succeeds and returns results
- ✅ Streamlit app opens and displays UI
- ✅ Streamlit can call function and show results
- ✅ Function logs show toolkit commands executed

---

## 📝 Test Report Template

```
Bootstrap Test Report
=====================
Date: YYYY-MM-DD
Tester: Your Name
CDF Project: your-project-name
Branch: oct_mods

Tier 1 (Mini Bootstrap):
[ ] Downloaded notebook successfully
[ ] Notebook has 13 cells
[ ] Can open in Jupyter

Tier 2 (Interactive Notebook):
[ ] All cells run without errors
[ ] Dataset created
[ ] Function deployed
[ ] Streamlit deployed
[ ] Verification passed

Tier 3 (One-Shot Deploy):
[ ] Script completed in <60s
[ ] Dataset created
[ ] Function deployed
[ ] Streamlit deployed
[ ] Test function call succeeded

Final Verification:
[ ] Streamlit UI opens
[ ] Can call function from UI
[ ] Function returns breakthrough metrics
[ ] All components working end-to-end

Issues Found:
(list any problems encountered)

Notes:
(any observations or improvements)
```

---

## 🚀 Ready to Test!

**Recommended Testing Order**:
1. **Start with Tier 3** (fastest verification)
2. **Then try Tier 1** (inspect notebook)
3. **Then run Tier 2** (understand each step)

**Good luck!** 🎉

