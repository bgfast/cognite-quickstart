#!/usr/bin/env python3
"""Force delete and recreate cognite-samples-main-mini.zip"""

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
    client_name="force-delete",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

space = "app-packages"
external_id = "cognite-samples-main-mini.zip"
node_id = NodeId(space=space, external_id=external_id)

print(f"🗑️  Deleting data model instance: {space}/{external_id}")
try:
    client.data_modeling.instances.delete(nodes=node_id)
    print("✅ Instance deleted!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n⏳ Waiting 2 seconds...")
import time
time.sleep(2)

print("\n📤 Re-uploading file with proper instance...")
file_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart/modules/app-packages-zips/files/cognite-samples-main-mini.zip"

# Create instance first
instance_dict = {
    "instanceType": "node",
    "space": space,
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
                "name": external_id,
                "mimeType": "application/zip",
            }
        }
    ]
}

try:
    print(f"📝 Creating new instance...")
    client.data_modeling.instances.apply(nodes=[instance_dict])
    print(f"✅ Instance created!")
    
    print(f"📤 Uploading file content...")
    uploaded_file = client.files.upload_content(
        path=file_path,
        instance_id=node_id
    )
    print(f"✅ File uploaded!")
    print(f"   ID: {uploaded_file.id}")
    print(f"   Uploaded: {uploaded_file.uploaded}")
    
except Exception as e:
    print(f"❌ Error: {e}")

