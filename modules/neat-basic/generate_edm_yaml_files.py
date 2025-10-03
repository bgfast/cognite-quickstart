#!/usr/bin/env python3
"""
Generate NEAT Basic YAML files using NEAT (Network Extraction and Analysis Tool)
This script processes the NeatBasic.xlsx data model file and generates CDF Toolkit YAML files.

Usage:
    cd modules/neat-basic
    python generate_edm_yaml_files.py

Requirements:
    - cognite-neat package installed
    - cdfenv.sh environment variables set
    - NeatBasic.xlsx file in data_models/ directory
"""

import os
import sys
from pathlib import Path
from cognite.neat import NeatSession
from cognite.client import CogniteClient
from cognite.client.credentials import OAuthClientCredentials

def get_cognite_client():
    """
    Initialize CogniteClient using cdfenv.sh environment variables
    """
    # Get environment variables from cdfenv.sh
    cdf_project = os.environ.get('CDF_PROJECT')
    cdf_cluster = os.environ.get('CDF_CLUSTER')
    cdf_url = os.environ.get('CDF_URL')
    
    if not all([cdf_project, cdf_cluster, cdf_url]):
        raise ValueError(
            "Missing required environment variables. "
            "Please run: source cdfenv.sh && cdfenv <environment-name>"
        )
    
    # Use OAuth credentials from cdfenv.sh environment variables
    print("🔐 Setting up OAuth credentials...")
    
    try:
        credentials = OAuthClientCredentials(
            token_url=os.environ.get('IDP_TOKEN_URL'),
            client_id=os.environ.get('IDP_CLIENT_ID'),
            client_secret=os.environ.get('IDP_CLIENT_SECRET'),
            scopes=[os.environ.get('IDP_SCOPES')]
        )
        
        from cognite.client.config import ClientConfig
        config = ClientConfig(
            client_name="edm-yaml-generator",
            project=cdf_project,
            credentials=credentials,
            base_url=cdf_url
        )
        
        client = CogniteClient(config)
        
        print(f"✅ Connected to CDF project: {cdf_project}")
        return client
        
    except Exception as e:
        print(f"⚠️  OAuth setup failed: {e}")
        print("Falling back to interactive login...")
        
        from cognite.client.config import ClientConfig
        config = ClientConfig(
            client_name="edm-yaml-generator",
            project=cdf_project,
            credentials=None,  # Will prompt for interactive login
            base_url=cdf_url
        )
        
        client = CogniteClient(config)
        
        print(f"✅ Connected to CDF project: {cdf_project}")
        return client

def process_excel_data_model(excel_file_path, output_dir=None):
    """
    Process Excel data model file using NEAT and generate YAML files
    
    Args:
        excel_file_path (str): Path to the Excel file containing data model
        output_dir (str): Directory to output YAML files (defaults to same directory as Excel file)
    """
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(excel_file_path)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"📁 Processing Excel file: {excel_file_path}")
    print(f"📁 Output directory: {output_path}")
    
    try:
        # Initialize CDF client
        client = get_cognite_client()
        
        # Create NEAT session
        print("🧪 Creating NEAT session...")
        neat = NeatSession(client)
        
        # Process the Excel file with NEAT
        print("📊 Processing Excel data model with NEAT...")
        
        # Read the Excel file into NEAT with manual edit enabled
        print("📖 Reading Excel file...")
        neat.read.excel(
            excel_file_path,
            enable_manual_edit=True,
        )
        
        # Inspect for any issues
        print("🔍 Inspecting for issues...")
        neat.inspect.issues()
        
        # Generate YAML files in toolkit format
        print("📝 Generating YAML files...")
        neat.to.yaml(output_path, format="toolkit")
        
        print("✅ Excel data model processed successfully!")
        print(f"📁 YAML files generated in: {output_path}")
        
        # List generated files
        print("\n📋 Generated files:")
        for yaml_file in output_path.rglob("*.yaml"):
            relative_path = yaml_file.relative_to(output_path)
            print(f"  - {relative_path}")
        
        # Close the NEAT session
        neat.close()
        print("🔒 NEAT session closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing Excel data model: {e}")
        return False

def main():
    """
    Main function to run the NEAT Basic YAML generation
    """
    print("🚀 NEAT Basic YAML File Generator")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    excel_file = current_dir / "data_models" / "NeatBasic.xlsx"
    
    if not excel_file.exists():
        print(f"⚠️  Excel file not found at: {excel_file}")
        print("Please run this script from the neat-basic module directory")
        print("Expected file: data_models/NeatBasic.xlsx")
        return
    
    print(f"📊 Found NEAT Basic Excel file: {excel_file}")
    
    # Set output directory to data_models
    output_dir = current_dir / "data_models"
    
    # Process the Excel file
    success = process_excel_data_model(str(excel_file), str(output_dir))
    
    if success:
        print("\n🎉 NEAT Basic YAML generation completed successfully!")
        print("📁 Generated files are in the data_models/ directory")
        print("\n🔧 Next steps:")
        print("  1. Deploy using: cdf-tk build --env neat-basic")
        print("  2. Test deployment: cdf-tk deploy --env neat-basic --dry-run")
        print("  3. Deploy for real: cdf-tk deploy --env neat-basic")
        print("  4. Run tests: python test_neat_data_model.py")
        print("  5. Generate sample data: python sample_data_generator.py")
        print("  6. Run integration tests: python neat_integration_test.py")
        
        # Ask if user wants to run tests
        print("\n" + "=" * 60)
        run_tests = input("🧪 Would you like to run the integration test now? (y/N): ")
        
        if run_tests.lower() == 'y':
            try:
                print("\n🚀 Running NEAT integration test...")
                from neat_integration_test import NeatIntegrationTester
                
                tester = NeatIntegrationTester()
                results = tester.run_full_integration_test(deploy_for_real=False)
                
                if results["overall_success"]:
                    print("\n✅ Integration test completed successfully!")
                else:
                    print("\n❌ Integration test had some failures. Check the results above.")
                    
            except ImportError:
                print("⚠️  Integration test module not found. Please run manually.")
            except Exception as e:
                print(f"⚠️  Integration test failed: {e}")
        else:
            print("⏭️  Skipping integration test. You can run it later with:")
            print("     python neat_integration_test.py")
            
    else:
        print("\n❌ NEAT Basic YAML generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
