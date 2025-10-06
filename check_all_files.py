#!/usr/bin/env python3
"""Check all file instances in app-packages space"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

# Initialize client
config = ClientConfig(
    client_name="check-all-files",
    base_url=os.getenv("CDF_URL", "https://bluefield.cognitedata.com"),
    project=os.getenv("CDF_PROJECT"),
    credentials=OAuthClientCredentials(
        token_url=os.getenv("IDP_TOKEN_URL"),
        client_id=os.getenv("IDP_CLIENT_ID"),
        client_secret=os.getenv("IDP_CLIENT_SECRET"),
        scopes=[f"{os.getenv('CDF_URL')}/.default"],
    )
)

client = CogniteClient(config)

print("=" * 80)
print("DATA MODEL INSTANCES (app-packages space)")
print("=" * 80)

# Query data model for file instances
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

print(f"\n🔍 Found {len(instances)} file instances in data model\n")

for instance in instances:
    props = instance.properties.get(("cdf_cdm", "CogniteFile/v1"), {})
    name = props.get("name", "N/A")
    uploaded = props.get("uploaded", False)
    ext_id = instance.external_id
    
    status = "✅" if uploaded else "❌"
    print(f"{status} {name}")
    print(f"   External ID: {ext_id}")
    print(f"   Uploaded: {uploaded}")
    print()

print("=" * 80)
print("FILES API (all files)")
print("=" * 80)

# Query Files API
all_files = client.files.list(limit=1000)
zip_files = [f for f in all_files if f.name and f.name.endswith(".zip")]

print(f"\n🔍 Found {len(zip_files)} zip files in Files API\n")

for f in zip_files:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name}")
    print(f"   ID: {f.id}")
    print(f"   External ID: {f.external_id}")
    print(f"   Uploaded: {f.uploaded}")
    print(f"   MIME Type: {f.mime_type}")
    print()
