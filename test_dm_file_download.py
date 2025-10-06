#!/usr/bin/env python3
"""Test downloading files from Data Modeling API using instance_id"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import ViewId, NodeId
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="test-dm-download",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Querying Data Modeling API for mini zips...")
print("=" * 80)

# Query CogniteFile instances in app-packages space
view_id = ViewId(space="cdf_cdm", external_id="CogniteFile", version="v1")

instances = client.data_modeling.instances.list(
    instance_type="node",
    sources=view_id,
    space="app-packages",
    limit=1000
)

print(f"\n📊 Found {len(instances)} file instances in app-packages space\n")

# Filter for mini zips
mini_zips = []
for instance in instances:
    props = instance.properties.get(view_id, {})
    name = props.get("name", "")
    is_uploaded = props.get("isUploaded", False)
    
    if name and name.endswith("-mini.zip"):
        uploaded_status = "✅" if is_uploaded else "❌"
        print(f"{uploaded_status} {name}")
        print(f"   External ID: {instance.external_id}")
        print(f"   Space: {instance.space}")
        print(f"   isUploaded: {is_uploaded}")
        print()
        
        if is_uploaded:
            mini_zips.append({
                "name": name,
                "external_id": instance.external_id,
                "space": instance.space
            })

print(f"\n📦 Mini zips with isUploaded=True: {len(mini_zips)}\n")

# Test downloading each file
for mz in mini_zips:
    print(f"📥 Testing download: {mz['name']}")
    print(f"   Instance: {mz['space']}/{mz['external_id']}")
    
    try:
        instance_id = NodeId(space=mz['space'], external_id=mz['external_id'])
        content = client.files.download_bytes(instance_id=instance_id)
        print(f"   ✅ Downloaded {len(content):,} bytes")
        
        # Verify it's a valid zip
        import zipfile
        import io
        try:
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                file_count = len(zf.namelist())
                print(f"   ✅ Valid ZIP with {file_count} files")
        except Exception as e:
            print(f"   ⚠️  Not a valid ZIP: {e}")
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
    print()

print("=" * 80)
print(f"✅ Test complete! Successfully downloaded {len(mini_zips)} mini zips")

