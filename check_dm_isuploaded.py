#!/usr/bin/env python3
"""Check isUploaded property in Data Modeling API"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling import NodeId
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="check-dm-isuploaded",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Checking Data Modeling API isUploaded property:")
print("=" * 80)

# Query using the same pattern as the transformation
from cognite.client.data_classes.data_modeling.ids import ViewId

view_id = ViewId(space="cdf_cdm", external_id="CogniteFile", version="v1")

# List all instances in app-packages space
instances = client.data_modeling.instances.list(
    instance_type="node",
    sources=view_id,
    space="app-packages",
    limit=100
)

print(f"\n📊 Found {len(instances)} file instances in app-packages space\n")

for instance in instances:
    props = instance.properties.get(view_id, {})
    name = props.get("name", "N/A")
    is_uploaded = props.get("isUploaded", None)
    external_id = instance.external_id
    
    status = "✅" if is_uploaded else "❌"
    print(f"{status} {name}")
    print(f"   External ID: {external_id}")
    print(f"   isUploaded: {is_uploaded}")
    print()

# Count
uploaded_count = sum(1 for inst in instances if inst.properties.get(view_id, {}).get("isUploaded", False))
print(f"\nTotal: {len(instances)}")
print(f"Uploaded (isUploaded=true): {uploaded_count}")
print(f"Not Uploaded (isUploaded=false): {len(instances) - uploaded_count}")

