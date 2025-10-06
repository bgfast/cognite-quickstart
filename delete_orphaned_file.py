#!/usr/bin/env python3
"""Try to delete the orphaned file by checking its instance_id and deleting via DM"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import NodeId
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="delete-orphaned",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Checking the orphaned file...")
print("=" * 80)

# Get the file details
file_id = 2197850608780297
f = client.files.retrieve(id=file_id)

print(f"File: {f.name}")
print(f"ID: {f.id}")
print(f"Uploaded: {f.uploaded}")

# Check if it has an instance_id
if hasattr(f, 'instance_id') and f.instance_id:
    print(f"Instance ID: {f.instance_id}")
    
    # Try to delete via Data Modeling using the instance_id
    print(f"\n🗑️  Attempting to delete via Data Modeling API...")
    try:
        # The instance_id should be a NodeId
        client.data_modeling.instances.delete(nodes=f.instance_id)
        print("✅ Deleted via Data Modeling!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative: Try deleting via Files API with ignore_unknown_ids=True")
        try:
            client.files.delete(id=file_id, ignore_unknown_ids=True)
            print("✅ Deleted via Files API!")
        except Exception as e2:
            print(f"❌ Error: {e2}")
else:
    print("No instance_id found - trying direct Files API delete...")
    try:
        client.files.delete(id=file_id)
        print("✅ Deleted!")
    except Exception as e:
        print(f"❌ Error: {e}")

