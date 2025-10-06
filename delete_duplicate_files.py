#!/usr/bin/env python3
"""
Delete duplicate or problematic files from CDF Files API
"""

from cognite.client import CogniteClient
from cognite.client import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
import os

# Initialize CDF client
config = ClientConfig(
    client_name="delete-files-script",
    base_url=f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com",
    project=os.environ['CDF_PROJECT'],
    credentials=OAuthClientCredentials(
        token_url=os.environ['IDP_TOKEN_URL'],
        client_id=os.environ['IDP_CLIENT_ID'],
        client_secret=os.environ['IDP_CLIENT_SECRET'],
        scopes=[f"https://{os.environ['CDF_CLUSTER']}.cognitedata.com/.default"]
    )
)
client = CogniteClient(config)

print("🔍 Searching for files in CDF...")

# List all files
all_files = client.files.list(limit=1000)

# Find mini zips
mini_zips = [f for f in all_files if f.name and f.name.endswith("-mini.zip")]

print(f"\n📦 Found {len(mini_zips)} mini zip files:")
print("-" * 80)

for f in mini_zips:
    uploaded_status = "✅ Uploaded" if f.uploaded else "❌ NOT Uploaded"
    print(f"{uploaded_status} | {f.name}")
    print(f"  ID: {f.id}")
    print(f"  Uploaded time: {f.uploaded_time}")
    print(f"  Space: {getattr(f, 'data_set_id', 'N/A')}")
    print()

# Find files to delete (not uploaded)
files_to_delete = [f for f in mini_zips if not f.uploaded]

if files_to_delete:
    print(f"\n🗑️  Found {len(files_to_delete)} file(s) to delete (not uploaded):")
    for f in files_to_delete:
        print(f"  - {f.name} (ID: {f.id})")
    
    response = input("\n⚠️  Delete these files? (yes/no): ")
    
    if response.lower() == 'yes':
        for f in files_to_delete:
            print(f"🗑️  Deleting {f.name} (ID: {f.id})...")
            client.files.delete(id=f.id)
            print(f"✅ Deleted!")
        print("\n✅ All files deleted successfully!")
    else:
        print("❌ Deletion cancelled")
else:
    print("✅ No files to delete (all files are uploaded)")

print("\n" + "=" * 80)
print("📊 Final Summary:")
print("=" * 80)

# List remaining files
remaining_files = client.files.list(limit=1000)
remaining_mini_zips = [f for f in remaining_files if f.name and f.name.endswith("-mini.zip")]

print(f"\n📦 Remaining mini zip files: {len(remaining_mini_zips)}")
for f in remaining_mini_zips:
    uploaded_status = "✅" if f.uploaded else "❌"
    print(f"  {uploaded_status} {f.name} (ID: {f.id})")
