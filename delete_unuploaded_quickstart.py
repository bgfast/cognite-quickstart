#!/usr/bin/env python3
"""Delete cognite-quickstart-main-mini.zip file instances where uploaded=False"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

# Initialize client
config = ClientConfig(
    client_name="delete-unuploaded-files",
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

print("🔍 Searching for cognite-quickstart-main-mini.zip instances in app-packages space...")

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

# Find instances with uploaded: False and matching name
to_delete = []
for instance in instances:
    props = instance.properties.get(("cdf_cdm", "CogniteFile/v1"), {})
    name = props.get("name")
    uploaded = props.get("uploaded", False)
    
    if name == "cognite-quickstart-main-mini.zip" and not uploaded:
        print(f"  ❌ Found: {name} (uploaded: {uploaded}, externalId: {instance.external_id})")
        to_delete.append(instance.external_id)

if not to_delete:
    print("✅ No unuploaded cognite-quickstart-main-mini.zip instances found")
else:
    print(f"\n🗑️  Deleting {len(to_delete)} instance(s)...")
    for ext_id in to_delete:
        client.data_modeling.instances.delete(
            nodes=(("app-packages", ext_id),)
        )
        print(f"  ✅ Deleted: {ext_id}")
    
    print("\n✅ Cleanup complete! Now redeploy the module:")
    print("   cdf deploy --env dev modules/app-packages-zips/")
