#!/usr/bin/env python3
"""Delete old cognite-samples-main-mini.zip and re-upload it"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling import NodeId
from cognite.client.exceptions import CogniteAPIError
import os
from pathlib import Path

# Setup client
credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="delete-and-reupload",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Step 1: Delete old cognite-samples-main-mini.zip from Files API")
print("=" * 60)

# Delete from Files API
try:
    client.files.delete(id=2197850608780297)
    print("✅ Deleted old file (ID: 2197850608780297)")
except Exception as e:
    print(f"⚠️  Could not delete: {e}")

print("\n🔍 Step 2: Delete data model instance")
print("=" * 60)

# Delete data model instance if it exists
try:
    client.data_modeling.instances.delete(
        nodes=(("app-packages", "cognite-samples-main-mini.zip"),)
    )
    print("✅ Deleted data model instance")
except Exception as e:
    print(f"⚠️  Could not delete instance: {e}")

print("\n🔍 Step 3: Create new data model instance and upload file")
print("=" * 60)

filename = "cognite-samples-main-mini.zip"
instance_space = "app-packages"
external_id = filename
file_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart/modules/app-packages-zips/files") / filename

# Create instance
instance_dict = {
    "instanceType": "node",
    "space": instance_space,
    "externalId": external_id,
    "sources": [
        {
            "source": {
                "type": "view",
                "space": "cdf_cdm",
                "externalId": "CogniteFile",
                "version": "v1",
            },
            "properties": {
                "name": filename,
                "mimeType": "application/zip",
            }
        }
    ]
}

try:
    print("📝 Creating data model instance...")
    client.data_modeling.instances.apply(nodes=[instance_dict])
    print(f"✅ Instance created: {external_id}")
    
    print("📤 Uploading file...")
    uploaded_file = client.files.upload_content(
        path=str(file_path),
        instance_id=NodeId(instance_space, external_id)
    )
    
    print(f"✅ File uploaded successfully!")
    print(f"   File ID: {uploaded_file.id}")
    print(f"   Uploaded: {uploaded_file.uploaded}")
    print("\n🎉 SUCCESS! Now refresh the Streamlit app.")
    
except Exception as e:
    print(f"❌ Error: {e}")

