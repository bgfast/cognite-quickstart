#!/usr/bin/env python3
"""Delete the old duplicate cognite-samples-main-mini.zip"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="delete-duplicate",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Finding old cognite-samples-main-mini.zip instances...")
print("=" * 60)

# Query data model for all cognite-samples-main-mini.zip instances
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

# Find instances with this name
to_delete = []
for instance in instances:
    props = instance.properties.get(("cdf_cdm", "CogniteFile/v1"), {})
    name = props.get("name", "")
    
    if name == "cognite-samples-main-mini.zip":
        print(f"Found instance: {instance.external_id}")
        to_delete.append(instance.external_id)

print(f"\nTotal instances to check: {len(to_delete)}")

# Now check Files API to see which file IDs map to which instance
print("\n🔍 Checking Files API...")
all_files = client.files.list(limit=1000)
samples_files = [f for f in all_files if f.name == "cognite-samples-main-mini.zip"]

print(f"Found {len(samples_files)} files named cognite-samples-main-mini.zip:")
for f in samples_files:
    status = "✅" if f.uploaded else "❌"
    print(f"  {status} ID: {f.id}, uploaded: {f.uploaded}")

# Delete the old one (ID: 2197850608780297)
old_file_id = 2197850608780297

print(f"\n🗑️  Attempting to delete old file (ID: {old_file_id})...")

# First, try to find and delete its data model instance
# Since we can't easily map file ID to instance external_id, 
# we'll delete by querying the data model

print("Step 1: Query data model to find the old file's instance...")
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

# The old file likely doesn't have a proper instance, so try to just delete via Files API
# But we need to use data modeling to delete it

print("\nStep 2: Try using CDF transformation to delete files with uploaded=False...")
print("⚠️  Manual step required:")
print("   1. Go to CDF UI > Transformations")
print("   2. Run the 'delete-unuploaded-files' transformation")
print("   OR")
print("   3. Use the CDF UI to manually delete file ID: 2197850608780297")

