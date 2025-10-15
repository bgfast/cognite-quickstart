#!/usr/bin/env python3
"""
Upload zip files to CDF Files API linked to data model instances.

The Cognite Toolkit creates data model instances but doesn't upload the actual
file content to Files API. This script manually uploads the files using the
upload_content method with instance_id to link them to the data model.
"""

from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling import NodeId
from cognite.client.exceptions import CogniteAPIError
import os
from pathlib import Path
import sys

def setup_client():
    """Initialize CDF client"""
    print("🔗 Initializing CDF client...")
    
    # Get environment variables
    cdf_project = os.getenv("CDF_PROJECT")
    cdf_cluster = os.getenv("CDF_CLUSTER")
    cdf_url = os.getenv("CDF_URL")
    client_id = os.getenv("IDP_CLIENT_ID")
    client_secret = os.getenv("IDP_CLIENT_SECRET")
    tenant_id = os.getenv("IDP_TENANT_ID")
    token_url = os.getenv("IDP_TOKEN_URL")
    
    if not all([cdf_project, cdf_cluster, client_id, client_secret, tenant_id, token_url]):
        print("❌ Missing required environment variables for CDF authentication")
        print(f"CDF_PROJECT: {cdf_project}")
        print(f"CDF_CLUSTER: {cdf_cluster}")
        print(f"IDP_CLIENT_ID: {client_id}")
        print(f"IDP_CLIENT_SECRET: {'***' if client_secret else None}")
        print(f"IDP_TENANT_ID: {tenant_id}")
        print(f"IDP_TOKEN_URL: {token_url}")
        sys.exit(1)
    
    # Create client configuration
    credentials = OAuthClientCredentials(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[f"{cdf_url}/.default"]
    )
    
    client_config = ClientConfig(
        client_name="App-Packages-Zip-Upload",
        project=cdf_project,
        base_url=cdf_url,
        credentials=credentials
    )
    
    return CogniteClient(client_config)

def create_data_model_instance(filename, instance_space, external_id):
    """Create a data model instance for a file"""
    instance_dict = {
        "instanceType": "node",
        "space": instance_space,
        "externalId": external_id,
        "sources": [
            {
                "source": {
                    "type": "view",
                    "space": "cdf_cdm",
                    "externalId": "CogniteFile",
                    "version": "v1",
                },
                "properties": {
                    "name": filename,
                    "mimeType": "application/zip",
                }
            }
        ]
    }
    
    return instance_dict

def upload_file_to_instance(client, file_path, instance_space, external_id):
    """Create data model instance and upload file"""
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    print(f"\n🔄 Processing: {filename}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Instance: {instance_space}/{external_id}")
    
    try:
        # Create data model instance
        print(f"📝 Creating data model instance...")
        instance_dict = create_data_model_instance(filename, instance_space, external_id)
        
        # Apply the instance
        client.data_modeling.instances.apply(nodes=[instance_dict])
        print(f"✅ Data Model Instance created: {external_id}")
        
        # Upload file content linked to data model instance
        print(f"📤 Uploading file...")
        uploaded_file = client.files.upload_content(
            path=file_path,
            instance_id=NodeId(instance_space, external_id)
        )
        
        print(f"✅ File uploaded successfully!")
        print(f"   File ID: {uploaded_file.id}")
        print(f"   Uploaded: {uploaded_file.uploaded}")
        return True
        
    except CogniteAPIError as e:
        print(f"❌ CDF API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("UPLOADING ZIP FILES TO CDF FILES API")
    print("=" * 80)
    
    # Show deployment destination
    cdf_project = os.getenv("CDF_PROJECT", "NOT SET")
    cdf_cluster = os.getenv("CDF_CLUSTER", "NOT SET")
    cdf_url = os.getenv("CDF_URL", "NOT SET")
    
    print(f"🎯 DEPLOYMENT DESTINATION:")
    print(f"   Project: {cdf_project}")
    print(f"   Cluster: {cdf_cluster}")
    print(f"   URL: {cdf_url}")
    print()
    
    # Configuration
    instance_space = "app-packages"
    downloads_dir = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart/modules/app-packages-zips/downloads")
    
    # Find all zip files in the directory
    files_to_upload = sorted([f.name for f in downloads_dir.glob("*.zip")])
    
    print(f"\nInstance Space: {instance_space}")
    print(f"Downloads Directory: {downloads_dir}")
    print(f"📂 Found {len(files_to_upload)} zip files:")
    for f in files_to_upload:
        file_size = (downloads_dir / f).stat().st_size
        print(f"   • {f} ({file_size:,} bytes)")
    print(f"\nFiles to upload: {len(files_to_upload)}")
    
    # Initialize client
    client = setup_client()
    print("✅ Client initialized\n")
    
    # Upload files
    success_count = 0
    fail_count = 0
    
    for filename in files_to_upload:
        file_path = downloads_dir / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            fail_count += 1
            continue
        
        # Use filename as external_id (matches data model instance)
        external_id = filename
        
        if upload_file_to_instance(client, str(file_path), instance_space, external_id):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {len(files_to_upload)}")
    
    if success_count > 0:
        print("\n🎉 Next steps:")
        print("1. Refresh the Streamlit app")
        print("2. Should now find mini zips with uploaded: True")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
