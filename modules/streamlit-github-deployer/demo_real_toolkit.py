#!/usr/bin/env python3
"""
Demo Real Cognite Toolkit API
Simple command-line demonstration of the working toolkit API
"""

import os
import sys
from pathlib import Path


def demo_build_command():
    """Demo the real BuildCommand API"""
    print("🏗️  DEMO: Real BuildCommand API")
    print("=" * 60)
    
    try:
        from cognite_toolkit._cdf_tk.commands.build_cmd import BuildCommand
        
        # Create BuildCommand instance
        build_cmd = BuildCommand()
        print("✅ BuildCommand instance created")
        
        # Parameters
        project_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart")
        build_dir = project_path / "build"
        build_env_name = "weather"
        
        print(f"📁 Project: {project_path}")
        print(f"🏗️  Build dir: {build_dir}")
        print(f"📋 Environment: {build_env_name}")
        print()
        
        print("🚀 Executing real toolkit build...")
        print("-" * 60)
        
        # Execute the real build
        result = build_cmd.execute(
            verbose=True,
            organization_dir=project_path,
            build_dir=build_dir,
            selected=None,  # Build all modules
            build_env_name=build_env_name,
            no_clean=False,
            client=None,
            on_error='continue'
        )
        
        print("-" * 60)
        print(f"✅ Build completed successfully!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Built modules: {len(result) if result else 0}")
        
        # Show what was built
        if result:
            print(f"📦 Built modules:")
            for module in result:
                print(f"  - {module}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        print(f"📊 Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def demo_deploy_command(dry_run=True):
    """Demo the real DeployCommand API"""
    print(f"\n🚀 DEMO: Real DeployCommand API (dry_run={dry_run})")
    print("=" * 60)
    
    try:
        from cognite_toolkit._cdf_tk.commands.deploy import DeployCommand
        from cognite_toolkit._cdf_tk.utils.auth import EnvironmentVariables
        
        # Create DeployCommand instance
        deploy_cmd = DeployCommand()
        print("✅ DeployCommand instance created")
        
        # Create environment variables
        env_vars = EnvironmentVariables()
        print("✅ EnvironmentVariables created")
        
        # Parameters
        project_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart")
        build_dir = project_path / "build"
        build_env_name = "weather"
        
        print(f"📁 Project: {project_path}")
        print(f"🏗️  Build dir: {build_dir}")
        print(f"📋 Environment: {build_env_name}")
        print(f"🔍 Dry run: {dry_run}")
        print()
        
        print(f"🚀 Executing real toolkit deploy (dry_run={dry_run})...")
        print("-" * 60)
        
        # Execute the real deploy
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
        
        print("-" * 60)
        print(f"✅ Deploy completed successfully!")
        print(f"📊 Result: {result}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Deploy failed: {e}")
        print(f"📊 Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def demo_simple_workflow():
    """Demo a simple build -> dry-run -> deploy workflow"""
    print("\n🎯 DEMO: Complete Workflow (Build -> Dry-Run -> Deploy)")
    print("=" * 80)
    
    # Step 1: Build
    build_success, build_result = demo_build_command()
    
    if not build_success:
        print("❌ Build failed, stopping workflow")
        return False
    
    # Step 2: Dry-run deploy
    dry_run_success, dry_run_result = demo_deploy_command(dry_run=True)
    
    if not dry_run_success:
        print("❌ Dry-run failed, stopping workflow")
        return False
    
    # Step 3: Ask about real deploy
    print(f"\n{'='*60}")
    user_input = input("🤔 Run real deploy (will modify CDF)? (y/N): ")
    
    if user_input.lower() == 'y':
        deploy_success, deploy_result = demo_deploy_command(dry_run=False)
        
        if deploy_success:
            print("\n🎉 Complete workflow successful!")
            return True
        else:
            print("\n❌ Real deploy failed")
            return False
    else:
        print("\n⏭️  Skipping real deploy - workflow complete")
        return True


def main():
    """Main demo function"""
    print("🧪 Real Cognite Toolkit API Demo")
    print("=" * 80)
    
    # Check environment
    if not os.getenv('CDF_PROJECT'):
        print("❌ CDF_PROJECT not set!")
        print("Please run: source cdfenv.sh && cdfenv bgfast")
        sys.exit(1)
    
    print(f"✅ CDF_PROJECT: {os.getenv('CDF_PROJECT')}")
    print(f"✅ CDF_CLUSTER: {os.getenv('CDF_CLUSTER', 'Not set')}")
    print()
    
    # Menu
    while True:
        print("Select demo to run:")
        print("1. Build only")
        print("2. Deploy dry-run only")
        print("3. Complete workflow (build -> dry-run -> deploy)")
        print("4. Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            demo_build_command()
        elif choice == '2':
            demo_deploy_command(dry_run=True)
        elif choice == '3':
            demo_simple_workflow()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again")
        
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
