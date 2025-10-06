#!/usr/bin/env python3
"""Check if valhall-dm files are actually uploaded in Files API"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

# Initialize client
config = ClientConfig(
    client_name="check-valhall-files",
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
print("CHECKING VALHALL-FILES SPACE")
print("=" * 80)

# Check data model instances
print("\n📋 Data Model Instances (valhall-files space):")
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
    space="valhall-files",
    limit=10
)

print(f"Found {len(instances)} instances\n")
for inst in instances[:5]:  # Show first 5
    props = inst.properties.get(("cdf_cdm", "CogniteFile/v1"), {})
    name = props.get("name", "N/A")
    uploaded = props.get("uploaded", False)
    status = "✅" if uploaded else "❌"
    print(f"{status} {name} (uploaded: {uploaded})")

# Check Files API
print("\n" + "=" * 80)
print("FILES API - PDF files")
print("=" * 80)

all_files = client.files.list(limit=1000)
pdf_files = [f for f in all_files if f.name and f.name.endswith(".pdf")][:10]

print(f"\nFound {len(pdf_files)} PDF files (showing first 10)\n")
for f in pdf_files:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name} (uploaded: {f.uploaded}, mime: {f.mime_type})")
