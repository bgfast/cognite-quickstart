#!/usr/bin/env python3
"""Delete the old cognite-samples-main-mini.zip data model instance"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import ViewId, NodeId
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="delete-old-dm-instance",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Finding cognite-samples-main-mini.zip in Data Modeling API...")
print("=" * 80)

view_id = ViewId(space="cdf_cdm", external_id="CogniteFile", version="v1")

# List all instances in app-packages space
instances = client.data_modeling.instances.list(
    instance_type="node",
    sources=view_id,
    space="app-packages",
    limit=100
)

print(f"\n📊 Found {len(instances)} file instances in app-packages space\n")

samples_instances = []
for instance in instances:
    props = instance.properties.get(view_id, {})
    name = props.get("name", "N/A")
    
    if name == "cognite-samples-main-mini.zip":
        is_uploaded = props.get("isUploaded", None)
        external_id = instance.external_id
        samples_instances.append(instance)
        
        status = "✅" if is_uploaded else "❌"
        print(f"{status} {name}")
        print(f"   External ID: {external_id}")
        print(f"   Space: {instance.space}")
        print(f"   isUploaded: {is_uploaded}")
        print()

if len(samples_instances) > 1:
    print(f"\n⚠️  Found {len(samples_instances)} instances! Deleting the one(s) with isUploaded=False...")
    
    for instance in samples_instances:
        props = instance.properties.get(view_id, {})
        is_uploaded = props.get("isUploaded", False)
        
        if not is_uploaded:
            node_id = NodeId(space=instance.space, external_id=instance.external_id)
            print(f"\n🗑️  Deleting: {instance.external_id} (isUploaded={is_uploaded})")
            try:
                client.data_modeling.instances.delete(nodes=node_id)
                print(f"   ✅ Deleted from Data Modeling!")
            except Exception as e:
                print(f"   ❌ Error: {e}")
else:
    print(f"✅ Only 1 instance found - no duplicates to delete!")

