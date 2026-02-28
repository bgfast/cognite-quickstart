#!/usr/bin/env python3
"""Delete ALL file instances from app-packages space to start fresh"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

# Initialize client
config = ClientConfig(
    client_name="delete-all-instances",
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

print("🔍 Finding all file instances in app-packages space...")

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

print(f"📋 Found {len(instances)} instances to delete\n")

if len(instances) == 0:
    print("✅ No instances to delete")
else:
    for instance in instances:
        print(f"  🗑️  {instance.external_id}")
    
    confirm = input(f"\n⚠️  Delete ALL {len(instances)} instances? (yes/no): ")
    
    if confirm.lower() == 'yes':
        print("\n🗑️  Deleting instances...")
        for instance in instances:
            try:
                client.data_modeling.instances.delete(
                    nodes=(("app-packages", instance.external_id),)
                )
                print(f"  ✅ Deleted: {instance.external_id}")
            except Exception as e:
                print(f"  ❌ Failed to delete {instance.external_id}: {e}")
        
        print("\n✅ Cleanup complete!")
        print("\n📦 Next steps:")
        print("   1. cdf deploy --env dev modules/app-packages-zips/")
        print("   2. Check Streamlit app - should now find all 3 mini zips")
    else:
        print("❌ Cancelled")
