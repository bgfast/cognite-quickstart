#!/usr/bin/env python3
"""
Test Cognite Toolkit Library API
Direct Python library calls instead of subprocess
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


def test_toolkit_imports():
    """Test if we can import the toolkit library"""
    print("🔍 Testing toolkit library imports...")
    
    try:
        # Try importing the main toolkit modules
        from cognite.toolkit import build
        print("✅ Successfully imported: from cognite.toolkit import build")
        
        # Get function signatures
        import inspect
        build_sig = inspect.signature(build)
        print(f"📋 build() signature: {build_sig}")
        
        return True, build
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        print("💡 Toolkit library not available - may need to install or use different approach")
        return False, None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None


def test_toolkit_deploy_imports():
    """Test if we can import deploy functions"""
    print("\n🔍 Testing deploy imports...")
    
    try:
        from cognite.toolkit import deploy
        print("✅ Successfully imported: from cognite.toolkit import deploy")
        
        import inspect
        deploy_sig = inspect.signature(deploy)
        print(f"📋 deploy() signature: {deploy_sig}")
        
        return True, deploy
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False, None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None


def test_toolkit_build_api(build_func, project_path, env_name="weather"):
    """Test the toolkit build API"""
    print(f"\n🏗️  Testing build API with library...")
    print(f"📁 Project: {project_path}")
    print(f"📋 Environment: {env_name}")
    
    try:
        # Test different ways to call build
        print("\n🧪 Attempt 1: build(source_dir=path)")
        result1 = build_func(source_dir=project_path)
        print(f"✅ Result: {result1}")
        return True, result1
        
    except Exception as e:
        print(f"❌ Attempt 1 failed: {e}")
        
        try:
            print("\n🧪 Attempt 2: build(path)")
            result2 = build_func(project_path)
            print(f"✅ Result: {result2}")
            return True, result2
            
        except Exception as e2:
            print(f"❌ Attempt 2 failed: {e2}")
            
            try:
                print(f"\n🧪 Attempt 3: build(source_dir=path, build_env_name=env)")
                result3 = build_func(source_dir=project_path, build_env_name=env_name)
                print(f"✅ Result: {result3}")
                return True, result3
                
            except Exception as e3:
                print(f"❌ Attempt 3 failed: {e3}")
                
                print(f"\n📊 All attempts failed:")
                print(f"  Attempt 1: {e}")
                print(f"  Attempt 2: {e2}")
                print(f"  Attempt 3: {e3}")
                
                return False, None


def test_toolkit_deploy_api(deploy_func, project_path, env_name="weather", dry_run=True):
    """Test the toolkit deploy API"""
    print(f"\n🚀 Testing deploy API with library...")
    print(f"📁 Project: {project_path}")
    print(f"📋 Environment: {env_name}")
    print(f"🔍 Dry run: {dry_run}")
    
    try:
        # Test different ways to call deploy
        print(f"\n🧪 Attempt 1: deploy(source_dir=path, dry_run={dry_run})")
        result1 = deploy_func(source_dir=project_path, dry_run=dry_run)
        print(f"✅ Result: {result1}")
        return True, result1
        
    except Exception as e:
        print(f"❌ Attempt 1 failed: {e}")
        
        try:
            print(f"\n🧪 Attempt 2: deploy(path, dry_run={dry_run})")
            result2 = deploy_func(project_path, dry_run=dry_run)
            print(f"✅ Result: {result2}")
            return True, result2
            
        except Exception as e2:
            print(f"❌ Attempt 2 failed: {e2}")
            
            try:
                print(f"\n🧪 Attempt 3: deploy(source_dir=path, build_env_name=env, dry_run={dry_run})")
                result3 = deploy_func(source_dir=project_path, build_env_name=env_name, dry_run=dry_run)
                print(f"✅ Result: {result3}")
                return True, result3
                
            except Exception as e3:
                print(f"❌ Attempt 3 failed: {e3}")
                
                try:
                    print(f"\n🧪 Attempt 4: deploy(source_dir=path, build_env_name=env, dry_run={dry_run}, verbose=True)")
                    result4 = deploy_func(source_dir=project_path, build_env_name=env_name, dry_run=dry_run, verbose=True)
                    print(f"✅ Result: {result4}")
                    return True, result4
                    
                except Exception as e4:
                    print(f"❌ Attempt 4 failed: {e4}")
                    
                    print(f"\n📊 All attempts failed:")
                    print(f"  Attempt 1: {e}")
                    print(f"  Attempt 2: {e2}")
                    print(f"  Attempt 3: {e3}")
                    print(f"  Attempt 4: {e4}")
                    
                    return False, None


def test_alternative_approaches():
    """Test alternative ways to access toolkit functionality"""
    print("\n🔧 Testing alternative approaches...")
    
    # Try direct module access
    try:
        import cognite.toolkit
        print("✅ Successfully imported cognite.toolkit")
        
        # List available functions
        toolkit_attrs = [attr for attr in dir(cognite.toolkit) if not attr.startswith('_')]
        print(f"📋 Available attributes: {toolkit_attrs}")
        
        # Try to find build/deploy functions
        if hasattr(cognite.toolkit, 'build'):
            print("✅ Found cognite.toolkit.build")
        if hasattr(cognite.toolkit, 'deploy'):
            print("✅ Found cognite.toolkit.deploy")
            
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import cognite.toolkit: {e}")
        
        # Try submodules
        try:
            import cognite.toolkit.loaders
            print("✅ Found cognite.toolkit.loaders")
        except ImportError:
            print("❌ No cognite.toolkit.loaders")
            
        try:
            import cognite.toolkit.cdf
            print("✅ Found cognite.toolkit.cdf")
        except ImportError:
            print("❌ No cognite.toolkit.cdf")
            
        return False


def test_cognite_client_approach():
    """Test using CogniteClient to recreate toolkit functionality"""
    print("\n🔗 Testing CogniteClient approach...")
    
    try:
        from cognite.client import CogniteClient
        
        # Try SaaS client
        client = CogniteClient()
        print(f"✅ SaaS CogniteClient created")
        print(f"📊 Project: {client.config.project}")
        print(f"🌐 Base URL: {client.config.base_url}")
        
        # Test basic operations
        try:
            # Test transformations access
            transformations = client.transformations.list(limit=1)
            print(f"✅ Can access transformations API: {len(transformations)} found")
            
            # Test workflows access (if available)
            try:
                # workflows = client.workflows.list(limit=1)
                # print(f"✅ Can access workflows API: {len(workflows)} found")
                print("📋 Workflows API test skipped (may not be available)")
            except Exception as e:
                print(f"⚠️  Workflows API not available: {e}")
            
            return True, client
            
        except Exception as e:
            print(f"❌ CogniteClient API test failed: {e}")
            return False, None
            
    except Exception as e:
        print(f"❌ CogniteClient creation failed: {e}")
        return False, None


def main():
    """Main test function"""
    print("🧪 Cognite Toolkit Library API Test")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('CDF_PROJECT'):
        print("⚠️  CDF_PROJECT not set. Some tests may fail.")
    else:
        print(f"✅ CDF_PROJECT: {os.getenv('CDF_PROJECT')}")
    
    project_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart"
    print(f"📁 Test project: {project_path}")
    print()
    
    # Test 1: Try importing toolkit library
    build_available, build_func = test_toolkit_imports()
    deploy_available, deploy_func = test_toolkit_deploy_imports()
    
    # Test 2: If available, try using the API
    if build_available and build_func:
        print("\n" + "="*50)
        success, result = test_toolkit_build_api(build_func, project_path)
        
        if success and deploy_available and deploy_func:
            # Test dry-run
            print("\n" + "="*50)
            deploy_success, deploy_result = test_toolkit_deploy_api(deploy_func, project_path, dry_run=True)
            
            if deploy_success:
                print("\n🎉 Both build and deploy APIs working!")
                
                # Ask if user wants to test real deploy
                user_input = input("\n🤔 Test real deploy (not dry-run)? This will modify CDF! (y/N): ")
                if user_input.lower() == 'y':
                    real_deploy_success, real_deploy_result = test_toolkit_deploy_api(deploy_func, project_path, dry_run=False)
                    if real_deploy_success:
                        print("✅ Real deploy also successful!")
                else:
                    print("⏭️  Skipping real deploy test")
    
    # Test 3: Alternative approaches
    print("\n" + "="*50)
    alt_success = test_alternative_approaches()
    
    # Test 4: CogniteClient fallback
    print("\n" + "="*50)
    client_success, client = test_cognite_client_approach()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY:")
    print(f"  Toolkit build API:     {'✅ Available' if build_available else '❌ Not available'}")
    print(f"  Toolkit deploy API:    {'✅ Available' if deploy_available else '❌ Not available'}")
    print(f"  Alternative modules:   {'✅ Found' if alt_success else '❌ Not found'}")
    print(f"  CogniteClient fallback: {'✅ Working' if client_success else '❌ Failed'}")
    
    if build_available and deploy_available:
        print("\n💡 RECOMMENDATION: Use toolkit library API directly")
        print("   from cognite.toolkit import build, deploy")
        print("   result = build(source_dir=path)")
        print("   result = deploy(source_dir=path, dry_run=True)")
    elif client_success:
        print("\n💡 RECOMMENDATION: Use CogniteClient to implement toolkit-like functionality")
        print("   from cognite.client import CogniteClient")
        print("   client = CogniteClient()")
        print("   # Implement build/deploy logic using client APIs")
    else:
        print("\n💡 RECOMMENDATION: Use subprocess to call cdf commands")
        print("   subprocess.run(['cdf', 'build', '--env=weather'])")


if __name__ == "__main__":
    main()
