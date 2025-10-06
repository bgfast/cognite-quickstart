#!/usr/bin/env python3
"""Show full paths in cognite-samples-main-mini.zip"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import NodeId
import zipfile
import io
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="show-paths",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("📥 Downloading cognite-samples-main-mini.zip...")
instance_id = NodeId(space="app-packages", external_id="cognite-samples-main-mini.zip")
content = client.files.download_bytes(instance_id=instance_id)

print("\n📂 Full paths (first 20):")
print("=" * 80)

with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
    all_files = sorted(zf.namelist())
    
    for file_path in all_files[:20]:
        print(file_path)
    
    print(f"\n... and {len(all_files) - 20} more files")

