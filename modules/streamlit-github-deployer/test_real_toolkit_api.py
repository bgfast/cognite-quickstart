#!/usr/bin/env python3
"""
Test Real Cognite Toolkit API
Using the actual BuildCommand and DeployCommand classes
"""

import os
import sys
from pathlib import Path


def test_build_command_api():
    """Test the real BuildCommand API"""
    print("🏗️  Testing BuildCommand API...")
    
    try:
        from cognite_toolkit._cdf_tk.commands.build_cmd import BuildCommand
        from cognite_toolkit._cdf_tk.client import ToolkitClient
        
        print("✅ Successfully imported BuildCommand and ToolkitClient")
        
        # Create BuildCommand instance
        build_cmd = BuildCommand()
        print("✅ BuildCommand instance created")
        
        # Test parameters
        project_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart")
        build_dir = project_path / "build"
        build_env_name = "weather"
        
        print(f"📁 Project path: {project_path}")
        print(f"🏗️  Build dir: {build_dir}")
        print(f"📋 Environment: {build_env_name}")
        
        # Try to execute build
        print("\n🧪 Attempting build.execute()...")
        try:
            result = build_cmd.execute(
                verbose=True,
                organization_dir=project_path,
                build_dir=build_dir,
                selected=None,  # Build all modules
                build_env_name=build_env_name,
                no_clean=False,
                client=None,  # Will create client internally
                on_error='continue'
            )
            
            print(f"✅ Build successful! Result type: {type(result)}")
            print(f"📊 Result: {result}")
            return True, result
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            print(f"📊 Error type: {type(e)}")
            return False, str(e)
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, str(e)


def test_deploy_command_api(dry_run=True):
    """Test the real DeployCommand API"""
    print(f"🚀 Testing DeployCommand API (dry_run={dry_run})...")
    
    try:
        from cognite_toolkit._cdf_tk.commands.deploy import DeployCommand
        from cognite_toolkit._cdf_tk.data_classes import EnvironmentVariables
        
        print("✅ Successfully imported DeployCommand and EnvironmentVariables")
        
        # Create DeployCommand instance
        deploy_cmd = DeployCommand()
        print("✅ DeployCommand instance created")
        
        # Test parameters
        project_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart")
        build_dir = project_path / "build"
        build_env_name = "weather"
        
        # Create environment variables
        env_vars = EnvironmentVariables()
        print("✅ EnvironmentVariables created")
        
        print(f"📁 Project path: {project_path}")
        print(f"🏗️  Build dir: {build_dir}")
        print(f"📋 Environment: {build_env_name}")
        print(f"🔍 Dry run: {dry_run}")
        
        # Try to execute deploy
        print(f"\n🧪 Attempting deploy.deploy_build_directory()...")
        try:
            result = deploy_cmd.deploy_build_directory(
                env_vars=env_vars,
                build_dir=build_dir,
                build_env_name=build_env_name,
                dry_run=dry_run,
                drop=False,
                drop_data=False,
                force_update=False,
                include=None,  # Deploy all resources
                verbose=True
            )
            
            print(f"✅ Deploy successful! Result: {result}")
            return True, result
            
        except Exception as e:
            print(f"❌ Deploy failed: {e}")
            print(f"📊 Error type: {type(e)}")
            return False, str(e)
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, str(e)


def test_toolkit_client():
    """Test creating a ToolkitClient"""
    print("🔗 Testing ToolkitClient creation...")
    
    try:
        from cognite_toolkit._cdf_tk.client import ToolkitClient
        
        print("✅ Successfully imported ToolkitClient")
        
        # Try to create client
        try:
            client = ToolkitClient()
            print("✅ ToolkitClient created successfully")
            print(f"📊 Client type: {type(client)}")
            
            # Test client properties
            if hasattr(client, 'config'):
                print(f"🔗 Project: {getattr(client.config, 'project', 'Unknown')}")
            
            return True, client
            
        except Exception as e:
            print(f"❌ ToolkitClient creation failed: {e}")
            return False, str(e)
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False, str(e)


def test_environment_variables():
    """Test EnvironmentVariables class"""
    print("🔧 Testing EnvironmentVariables...")
    
    try:
        from cognite_toolkit._cdf_tk.data_classes import EnvironmentVariables
        
        print("✅ Successfully imported EnvironmentVariables")
        
        # Create instance
        env_vars = EnvironmentVariables()
        print("✅ EnvironmentVariables instance created")
        print(f"📊 Type: {type(env_vars)}")
        
        # Check what's available
        print(f"📋 Available attributes: {[attr for attr in dir(env_vars) if not attr.startswith('_')]}")
        
        return True, env_vars
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, str(e)


def main():
    """Main test function"""
    print("🧪 Real Cognite Toolkit API Test")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('CDF_PROJECT'):
        print("⚠️  CDF_PROJECT not set. Some tests may fail.")
        print("Run: source cdfenv.sh && cdfenv bgfast")
    else:
        print(f"✅ CDF_PROJECT: {os.getenv('CDF_PROJECT')}")
    
    print()
    
    # Test 1: ToolkitClient
    client_success, client_result = test_toolkit_client()
    print("\n" + "="*50)
    
    # Test 2: EnvironmentVariables
    env_success, env_result = test_environment_variables()
    print("\n" + "="*50)
    
    # Test 3: BuildCommand
    build_success, build_result = test_build_command_api()
    print("\n" + "="*50)
    
    # Test 4: DeployCommand (dry-run)
    if build_success:
        deploy_success, deploy_result = test_deploy_command_api(dry_run=True)
        
        if deploy_success:
            print("\n" + "="*50)
            # Test 5: Ask about real deploy
            user_input = input("🤔 Test real deploy (not dry-run)? This will modify CDF! (y/N): ")
            if user_input.lower() == 'y':
                real_deploy_success, real_deploy_result = test_deploy_command_api(dry_run=False)
            else:
                print("⏭️  Skipping real deploy test")
    else:
        print("❌ Skipping deploy tests due to build failure")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY:")
    print(f"  ToolkitClient:         {'✅ Working' if client_success else '❌ Failed'}")
    print(f"  EnvironmentVariables:  {'✅ Working' if env_success else '❌ Failed'}")
    print(f"  BuildCommand:          {'✅ Working' if build_success else '❌ Failed'}")
    
    if build_success:
        print("\n💡 RECOMMENDATION: Use the real toolkit API!")
        print("   from cognite_toolkit._cdf_tk.commands.build_cmd import BuildCommand")
        print("   from cognite_toolkit._cdf_tk.commands.deploy import DeployCommand")
        print("   build_cmd = BuildCommand()")
        print("   deploy_cmd = DeployCommand()")
        print("   result = build_cmd.execute(...)")
        print("   result = deploy_cmd.deploy_build_directory(...)")
    else:
        print("\n💡 RECOMMENDATION: Debug the API issues first")
        print("   Check environment variables and authentication")


if __name__ == "__main__":
    main()
