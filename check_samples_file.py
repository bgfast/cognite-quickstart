#!/usr/bin/env python3
"""Check the cognite-samples-main-mini.zip file by ID"""

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
    client_name="check-samples",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

file_id = 5610584178489292

print(f"🔍 Checking file ID: {file_id}")
print("=" * 80)

for i in range(3):
    print(f"\n⏳ Attempt {i+1}/3 (waiting {i*2} seconds)...")
    time.sleep(i*2)
    
    try:
        f = client.files.retrieve(id=file_id)
        status = "✅" if f.uploaded else "❌"
        print(f"{status} Name: {f.name}")
        print(f"   ID: {f.id}")
        print(f"   Uploaded: {f.uploaded}")
        if hasattr(f, 'uploaded_time'):
            print(f"   Uploaded Time: {f.uploaded_time}")
        if hasattr(f, 'instance_id'):
            print(f"   Instance ID: {f.instance_id}")
        
        if f.uploaded:
            print("\n✅ File is now uploaded!")
            break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🔍 All mini zips in Files API:")
print("=" * 80)
all_files = client.files.list(limit=1000)
mini_zips = [f for f in all_files if f.name and f.name.endswith("-mini.zip")]
for f in sorted(mini_zips, key=lambda x: x.name):
    status = "✅" if f.uploaded else "❌"
    print(f"{status} {f.name} (ID: {f.id}, uploaded: {f.uploaded})")

