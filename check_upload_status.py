#!/usr/bin/env python3
"""Check if the file is now uploaded"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os
import time

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="check-status",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("⏳ Waiting 3 seconds for upload to complete...")
time.sleep(3)

print("\n🔍 Checking cognite-samples-main-mini.zip status:")
print("=" * 60)

# Check by ID
file_id = 7767528350302710
try:
    f = client.files.retrieve(id=file_id)
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name}")
    print(f"   ID: {f.id}")
    print(f"   Uploaded: {f.uploaded}")
    print(f"   Size: {f.uploaded_size if hasattr(f, 'uploaded_size') else 'N/A'}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔍 All mini zips:")
print("=" * 60)

all_files = client.files.list(limit=1000)
mini_zips = [f for f in all_files if f.name and f.name.endswith("-mini.zip")]

for f in mini_zips:
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name} (ID: {f.id}, uploaded: {f.uploaded})")

print(f"\nTotal mini zips: {len(mini_zips)}")
uploaded_count = sum(1 for f in mini_zips if f.uploaded)
print(f"Uploaded: {uploaded_count}/{len(mini_zips)}")

