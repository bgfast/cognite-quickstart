#!/usr/bin/env python3
"""
Delete files from CogniteFile data model instances in app-packages space
"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling import NodeId
import os

# Initialize CDF client
config = ClientConfig(
    client_name="delete-dm-files-script",
    base_url=f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com",
    project=os.environ['CDF_PROJECT'],
    credentials=OAuthClientCredentials(
        token_url=os.environ['IDP_TOKEN_URL'],
        client_id=os.environ['IDP_CLIENT_ID'],
        client_secret=os.environ['IDP_CLIENT_SECRET'],
        scopes=[f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com/.default"]
    )
)
client = CogniteClient(config)

print("🔍 Querying CogniteFile instances in app-packages space...")

# Query the data model
from cognite.client.data_classes.data_modeling import query as dm_query

# List instances from the CogniteFile view
instances = client.data_modeling.instances.list(
    instance_type="node",
    sources=[{
        "source": {
            "space": "cdf_cdm",
            "externalId": "CogniteFile",
            "version": "v1",
            "type": "view"
        }
    }],
    space="app-packages",
    limit=1000
)

print(f"\n📦 Found {len(instances)} file instances in app-packages space:")
print("-" * 100)

files_info = []
for instance in instances:
    # Get properties from the CogniteFile view
    props = instance.properties.get(("cdf_cdm", "CogniteFile", "v1"), {})
    
    name = props.get("name", "N/A")
    uploaded = props.get("uploaded", None)
    uploaded_time = props.get("uploadedTime", "N/A")
    
    uploaded_status = "✅ Uploaded" if uploaded else "❌ NOT Uploaded"
    
    print(f"{uploaded_status} | {name}")
    print(f"  External ID: {instance.external_id}")
    print(f"  Space: {instance.space}")
    print(f"  Uploaded time: {uploaded_time}")
    print()
    
    files_info.append({
        "instance": instance,
        "name": name,
        "uploaded": uploaded,
        "external_id": instance.external_id,
        "space": instance.space
    })

# Find files to delete (not uploaded or duplicates)
files_to_delete = [f for f in files_info if not f["uploaded"]]

if files_to_delete:
    print(f"\n🗑️  Found {len(files_to_delete)} file(s) to delete (not uploaded):")
    for f in files_to_delete:
        print(f"  - {f['name']} (External ID: {f['external_id']})")
    
    response = input("\n⚠️  Delete these instances? (yes/no): ")
    
    if response.lower() == 'yes':
        # Delete the instances
        node_ids = [NodeId(space=f["space"], external_id=f["external_id"]) for f in files_to_delete]
        
        print(f"\n🗑️  Deleting {len(node_ids)} instance(s)...")
        result = client.data_modeling.instances.delete(nodes=node_ids)
        print(f"✅ Deleted {len(result.nodes)} instance(s)!")
    else:
        print("❌ Deletion cancelled")
else:
    print("✅ No files to delete (all files are uploaded)")

print("\n" + "=" * 100)
print("📊 Final Summary:")
print("=" * 100)

# List remaining instances
remaining_instances = client.data_modeling.instances.list(
    instance_type="node",
    sources=[{
        "source": {
            "space": "cdf_cdm",
            "externalId": "CogniteFile",
            "version": "v1",
            "type": "view"
        }
    }],
    space="app-packages",
    limit=1000
)

print(f"\n📦 Remaining file instances: {len(remaining_instances)}")
for instance in remaining_instances:
    props = instance.properties.get(("cdf_cdm", "CogniteFile", "v1"), {})
    name = props.get("name", "N/A")
    uploaded = props.get("uploaded", None)
    uploaded_status = "✅" if uploaded else "❌"
    print(f"  {uploaded_status} {name} (External ID: {instance.external_id})")
