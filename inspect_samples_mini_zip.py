#!/usr/bin/env python3
"""Inspect the contents of cognite-samples-main-mini.zip"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import ViewId, NodeId
import zipfile
import io
import os

credentials = OAuthClientCredentials(
    token_url=os.getenv("IDP_TOKEN_URL"),
    client_id=os.getenv("IDP_CLIENT_ID"),
    client_secret=os.getenv("IDP_CLIENT_SECRET"),
    scopes=[f"{os.getenv('CDF_URL')}/.default"]
)

client_config = ClientConfig(
    client_name="inspect-samples",
    project=os.getenv("CDF_PROJECT"),
    base_url=os.getenv("CDF_URL"),
    credentials=credentials
)

client = CogniteClient(client_config)

print("📥 Downloading cognite-samples-main-mini.zip...")
instance_id = NodeId(space="app-packages", external_id="cognite-samples-main-mini.zip")
content = client.files.download_bytes(instance_id=instance_id)
print(f"✅ Downloaded {len(content):,} bytes\n")

print("📂 Files in ZIP:")
print("=" * 80)

with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
    all_files = zf.namelist()
    
    # Show directory structure
    for file_name in sorted(all_files):
        basename = file_name.split('/')[-1]
        indent = "  " * (file_name.count('/'))
        print(f"{indent}{basename if basename else '[directory]'}")
    
    print(f"\n📊 Total files: {len(all_files)}\n")
    
    # Find readme files
    print("🔍 Looking for readme.*.md files:")
    print("=" * 80)
    
    readme_files = []
    for file_name in all_files:
        basename = file_name.split('/')[-1]
        basename_lower = basename.lower()
        
        if basename_lower.startswith('readme.') and basename_lower.endswith('.md'):
            parts = basename_lower.split('.')
            if len(parts) >= 3:
                config_name = '.'.join(parts[1:-1])
                readme_files.append({
                    'path': file_name,
                    'basename': basename,
                    'config': config_name
                })
                print(f"✅ {basename}")
                print(f"   Path: {file_name}")
                print(f"   Config: {config_name}")
                print()
    
    print(f"📊 Found {len(readme_files)} readme files")

