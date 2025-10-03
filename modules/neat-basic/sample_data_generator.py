#!/usr/bin/env python3
"""
Sample Data Generator for NEAT BasicAsset Model

This script generates sample data for testing the BasicAsset data model,
creating realistic test instances that can be used for validation and testing.
"""

import os
import sys
import json
import random
from typing import List, Dict, Any
from dataclasses import dataclass
import time

try:
    from cognite.client import CogniteClient
    from cognite.client.data_classes import NodeApply
except ImportError:
    print("❌ cognite-sdk not installed. Please install with: pip install cognite-sdk")
    sys.exit(1)


@dataclass
class AssetTemplate:
    """Template for generating asset data"""
    name: str
    description: str
    asset_type: str


class SampleDataGenerator:
    """Generator for sample BasicAsset instances"""
    
    def __init__(self, client: CogniteClient = None):
        """Initialize the generator"""
        self.client = client or self._create_client()
        self.space_id = "neat-basic"
        self.container_id = "BasicAsset"
        
        # Sample asset templates
        self.asset_templates = [
            AssetTemplate("Pump Station A", "Primary water pump station", "pump"),
            AssetTemplate("Compressor Unit 1", "Main air compressor unit", "compressor"),
            AssetTemplate("Generator Building", "Emergency power generator facility", "generator"),
            AssetTemplate("Cooling Tower North", "Northern cooling tower system", "cooling_tower"),
            AssetTemplate("Control Room", "Main facility control room", "control_room"),
            AssetTemplate("Storage Tank 001", "Primary chemical storage tank", "storage_tank"),
            AssetTemplate("Conveyor Belt A1", "Assembly line conveyor belt", "conveyor"),
            AssetTemplate("HVAC System Main", "Main building HVAC system", "hvac"),
            AssetTemplate("Fire Suppression Panel", "Emergency fire suppression control", "safety_system"),
            AssetTemplate("Electrical Substation", "Main electrical distribution point", "electrical"),
            AssetTemplate("Boiler Room", "Steam generation facility", "boiler"),
            AssetTemplate("Water Treatment Plant", "Facility water treatment system", "treatment_plant"),
            AssetTemplate("Loading Dock 1", "Primary material loading dock", "loading_dock"),
            AssetTemplate("Warehouse Section A", "Main storage warehouse area", "warehouse"),
            AssetTemplate("Quality Control Lab", "Product quality testing laboratory", "laboratory"),
        ]
        
        # Additional descriptive elements
        self.status_options = ["operational", "maintenance", "offline", "testing"]
        self.location_prefixes = ["Building A", "Building B", "Outdoor Area", "Basement Level", "Floor 2"]
        
    def _create_client(self) -> CogniteClient:
        """Create CogniteClient from environment variables"""
        project = os.getenv('CDF_PROJECT')
        cluster = os.getenv('CDF_CLUSTER', 'api')
        
        if not project:
            raise ValueError("CDF_PROJECT environment variable not set")
            
        token = os.getenv('CDF_TOKEN')
        if token:
            return CogniteClient(
                api_key=None,
                project=project,
                base_url=f"https://{cluster}.cognitedata.com",
                token=token
            )
        else:
            return CogniteClient.default_oauth_interactive(
                project=project,
                cdf_cluster=cluster
            )
    
    def generate_sample_assets(self, count: int = 10) -> List[NodeApply]:
        """Generate sample BasicAsset instances"""
        assets = []
        
        for i in range(count):
            # Select random template
            template = random.choice(self.asset_templates)
            
            # Generate unique external ID
            external_id = f"sample_asset_{int(time.time())}_{i:03d}"
            
            # Enhance description with additional details
            location = random.choice(self.location_prefixes)
            status = random.choice(self.status_options)
            enhanced_description = f"{template.description} - Located in {location}, Status: {status}"
            
            # Create node
            node = NodeApply(
                space=self.space_id,
                external_id=external_id,
                sources=[
                    {
                        "source": {
                            "space": self.space_id,
                            "externalId": self.container_id,
                            "version": "1"
                        },
                        "properties": {
                            "name": f"{template.name} ({i+1:03d})",
                            "description": enhanced_description,
                            "type": template.asset_type
                        }
                    }
                ]
            )
            
            assets.append(node)
        
        return assets
    
    def create_sample_data(self, count: int = 10, dry_run: bool = False) -> Dict[str, Any]:
        """Create sample data in CDF"""
        print(f"🏭 Generating {count} sample BasicAsset instances")
        print("=" * 60)
        
        # Generate assets
        assets = self.generate_sample_assets(count)
        
        if dry_run:
            print("🔍 DRY RUN - Would create the following assets:")
            for asset in assets:
                props = asset.sources[0]["properties"]
                print(f"  - {asset.external_id}: {props['name']} ({props['type']})")
            
            return {
                "dry_run": True,
                "would_create": len(assets),
                "assets": [
                    {
                        "external_id": asset.external_id,
                        "name": asset.sources[0]["properties"]["name"],
                        "type": asset.sources[0]["properties"]["type"]
                    }
                    for asset in assets
                ]
            }
        
        try:
            # Apply the instances
            print("🚀 Creating assets in CDF...")
            result = self.client.data_modeling.instances.apply(
                nodes=assets,
                auto_create_start_nodes=True,
                auto_create_end_nodes=True
            )
            
            created_count = len(result.nodes) if result.nodes else 0
            
            print(f"✅ Successfully created {created_count} sample assets")
            
            return {
                "dry_run": False,
                "created": created_count,
                "requested": count,
                "success": True,
                "external_ids": [node.external_id for node in result.nodes] if result.nodes else []
            }
            
        except Exception as e:
            print(f"❌ Failed to create sample data: {e}")
            return {
                "dry_run": False,
                "created": 0,
                "requested": count,
                "success": False,
                "error": str(e)
            }
    
    def list_existing_assets(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List existing BasicAsset instances"""
        try:
            query = f"""
            SELECT 
                node.externalId,
                node.name,
                node.description,
                node.type
            FROM {self.space_id}.BasicAsset as node
            LIMIT {limit}
            """
            
            result = self.client.data_modeling.instances.query(query)
            
            print(f"📋 Found {len(result)} existing BasicAsset instances:")
            for i, row in enumerate(result, 1):
                node = row['node']
                print(f"  {i:2d}. {node['name']} ({node['externalId']}) - Type: {node.get('type', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to list assets: {e}")
            return []
    
    def cleanup_sample_data(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean up sample data (assets with external_id starting with 'sample_asset_')"""
        try:
            # Find sample assets
            query = f"""
            SELECT 
                node.externalId,
                node.name
            FROM {self.space_id}.BasicAsset as node
            WHERE node.externalId LIKE 'sample_asset_%'
            """
            
            result = self.client.data_modeling.instances.query(query)
            
            if not result:
                print("🧹 No sample assets found to clean up")
                return {"cleaned": 0, "found": 0}
            
            external_ids = [row['node']['externalId'] for row in result]
            
            if dry_run:
                print(f"🔍 DRY RUN - Would delete {len(external_ids)} sample assets:")
                for ext_id in external_ids:
                    print(f"  - {ext_id}")
                
                return {
                    "dry_run": True,
                    "would_delete": len(external_ids),
                    "external_ids": external_ids
                }
            
            print(f"🧹 Cleaning up {len(external_ids)} sample assets...")
            
            # Note: In a real implementation, you would delete the instances here
            # For safety, we'll just report what would be deleted
            print("⚠️  Actual deletion not implemented for safety")
            print("   To delete, use: client.data_modeling.instances.delete()")
            
            return {
                "dry_run": False,
                "found": len(external_ids),
                "cleaned": 0,  # Not actually deleted for safety
                "external_ids": external_ids,
                "note": "Deletion not implemented for safety"
            }
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return {"error": str(e), "cleaned": 0}


def main():
    """Main function"""
    print("🏭 NEAT BasicAsset Sample Data Generator")
    print("=" * 80)
    
    # Check environment
    if not os.getenv('CDF_PROJECT'):
        print("❌ CDF_PROJECT not set!")
        print("Please run: source cdfenv.sh && cdfenv bgfast")
        sys.exit(1)
    
    print(f"✅ CDF_PROJECT: {os.getenv('CDF_PROJECT')}")
    print(f"✅ CDF_CLUSTER: {os.getenv('CDF_CLUSTER', 'api')}")
    print()
    
    try:
        generator = SampleDataGenerator()
        
        # Interactive menu
        while True:
            print("Select an option:")
            print("1. List existing assets")
            print("2. Generate sample data (dry run)")
            print("3. Generate sample data (create in CDF)")
            print("4. Cleanup sample data (dry run)")
            print("5. Cleanup sample data (delete from CDF)")
            print("6. Exit")
            print()
            
            choice = input("Enter choice (1-6): ").strip()
            
            if choice == '1':
                generator.list_existing_assets()
                
            elif choice == '2':
                count = int(input("How many sample assets to generate? (default: 10): ") or "10")
                generator.create_sample_data(count=count, dry_run=True)
                
            elif choice == '3':
                count = int(input("How many sample assets to create? (default: 10): ") or "10")
                confirm = input(f"Create {count} assets in CDF? (y/N): ")
                if confirm.lower() == 'y':
                    result = generator.create_sample_data(count=count, dry_run=False)
                    if result['success']:
                        print(f"✅ Created {result['created']} assets")
                    else:
                        print(f"❌ Creation failed: {result.get('error', 'Unknown error')}")
                else:
                    print("⏭️  Skipped creation")
                    
            elif choice == '4':
                generator.cleanup_sample_data(dry_run=True)
                
            elif choice == '5':
                confirm = input("Delete sample assets from CDF? (y/N): ")
                if confirm.lower() == 'y':
                    result = generator.cleanup_sample_data(dry_run=False)
                    print(f"🧹 Cleanup result: {result}")
                else:
                    print("⏭️  Skipped cleanup")
                    
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice, please try again")
            
            print("\n" + "=" * 80 + "\n")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
