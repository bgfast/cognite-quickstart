#!/usr/bin/env python3
"""Delete the old cognite-samples-main-mini.zip file with uploaded=False"""

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
    client_name="delete-old-file",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("🔍 Finding cognite-samples-main-mini.zip files in Files API...")
print("=" * 80)

all_files = client.files.list(limit=1000)
samples_files = [f for f in all_files if f.name == "cognite-samples-main-mini.zip"]

print(f"\nFound {len(samples_files)} file(s) with that name:\n")

for f in samples_files:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} ID: {f.id}, uploaded: {f.uploaded}")

# Find the one with uploaded=False
old_files = [f for f in samples_files if not f.uploaded]

if not old_files:
    print("\n✅ No files with uploaded=False found!")
else:
    print(f"\n🗑️  Deleting {len(old_files)} file(s) with uploaded=False...")
    for f in old_files:
        try:
            print(f"   Deleting file ID: {f.id}...")
            client.files.delete(id=f.id)
            print(f"   ✅ Deleted!")
        except Exception as e:
            print(f"   ❌ Error: {e}")

print("\n🔍 Remaining cognite-samples-main-mini.zip files:")
remaining = client.files.list(limit=1000)
samples_remaining = [f for f in remaining if f.name == "cognite-samples-main-mini.zip"]
for f in samples_remaining:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} ID: {f.id}, uploaded: {f.uploaded}")

