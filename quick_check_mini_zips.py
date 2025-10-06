#!/usr/bin/env python3
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
    client_name="quick-check",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("\n🔍 ALL FILES ENDING WITH '-mini.zip':")
print("=" * 60)

all_files = client.files.list(limit=1000)
mini_zips = [f for f in all_files if f.name and f.name.endswith("-mini.zip")]

for f in mini_zips:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name}")
    print(f"   ID: {f.id}")
    print(f"   Uploaded: {f.uploaded}")
    print()

print(f"Total: {len(mini_zips)}")

