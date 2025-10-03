#!/usr/bin/env python3
"""
Shell Test Harness for Toolkit Operations
Test dry-run and deploy operations using real cdf commands
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    print(f"🔧 Running: {cmd}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
            
        print(f"\nReturn code: {result.returncode}")
        print("=" * 60)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 5 minutes")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False, "", str(e)


def test_build_operation(project_path, env_name="weather"):
    """Test cdf build operation"""
    print(f"🏗️  Testing BUILD operation")
    print(f"📁 Project: {project_path}")
    print(f"📋 Environment: {env_name}")
    print()
    
    # Test build command
    cmd = f"cdf build --env={env_name}"
    return run_command(cmd, cwd=project_path)


def test_dry_run_operation(project_path, env_name="weather"):
    """Test cdf deploy --dry-run operation"""
    print(f"🔍 Testing DRY-RUN operation")
    print(f"📁 Project: {project_path}")
    print(f"📋 Environment: {env_name}")
    print()
    
    # Test dry-run command
    cmd = f"cdf deploy --env={env_name} --dry-run"
    return run_command(cmd, cwd=project_path)


def test_deploy_operation(project_path, env_name="weather"):
    """Test cdf deploy operation"""
    print(f"🚀 Testing DEPLOY operation")
    print(f"📁 Project: {project_path}")
    print(f"📋 Environment: {env_name}")
    print()
    
    # Test deploy command
    cmd = f"cdf deploy --env={env_name}"
    return run_command(cmd, cwd=project_path)


def setup_test_environment():
    """Setup test environment and verify CDF connection"""
    print("🔧 Setting up test environment...")
    
    # Check environment variables
    required_vars = ['CDF_PROJECT', 'CDF_CLUSTER']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please run: source cdfenv.sh && cdfenv bgfast")
        return False
    
    print(f"✅ CDF_PROJECT: {os.getenv('CDF_PROJECT')}")
    print(f"✅ CDF_CLUSTER: {os.getenv('CDF_CLUSTER')}")
    print()
    
    return True


def test_with_downloaded_repo():
    """Test with a downloaded repository from CDF"""
    print("📦 Testing with downloaded repository from CDF...")
    
    # Use temp directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🗂️  Using temp directory: {temp_dir}")
        
        # Simulate downloaded repo structure
        repo_dir = os.path.join(temp_dir, "cognite-quickstart-main")
        os.makedirs(repo_dir)
        
        # Copy weather config to temp repo
        weather_config = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart/config.weather.yaml"
        if os.path.exists(weather_config):
            shutil.copy2(weather_config, repo_dir)
            print("✅ Copied config.weather.yaml")
        
        # Copy modules directory
        source_modules = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart/modules"
        dest_modules = os.path.join(repo_dir, "modules")
        if os.path.exists(source_modules):
            shutil.copytree(source_modules, dest_modules)
            print("✅ Copied modules directory")
        
        print(f"📂 Test repo structure:")
        for root, dirs, files in os.walk(repo_dir):
            level = root.replace(repo_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Limit file listing
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")
        print()
        
        # Test operations
        print("🧪 Running toolkit operations tests...")
        print()
        
        # Test 1: Build
        build_ok, build_out, build_err = test_build_operation(repo_dir)
        
        if build_ok:
            # Test 2: Dry-run
            dry_run_ok, dry_run_out, dry_run_err = test_dry_run_operation(repo_dir)
            
            if dry_run_ok:
                # Test 3: Deploy (optional - ask user)
                user_input = input("\n🤔 Run actual deploy? This will modify CDF! (y/N): ")
                if user_input.lower() == 'y':
                    deploy_ok, deploy_out, deploy_err = test_deploy_operation(repo_dir)
                else:
                    print("⏭️  Skipping deploy operation")
            else:
                print("❌ Dry-run failed, skipping deploy")
        else:
            print("❌ Build failed, skipping other operations")


def test_streamlit_workflow():
    """Test the workflow that mimics what Streamlit does"""
    print("🎨 Testing Streamlit-like workflow...")
    print()
    
    # This would simulate:
    # 1. Download zip from CDF
    # 2. Extract to temp directory  
    # 3. Build project
    # 4. Dry-run
    # 5. Deploy
    
    # For now, use the existing project
    project_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart"
    
    print("1️⃣ Testing with weather data module...")
    
    # Test build
    build_ok, _, _ = test_build_operation(project_path, "weather")
    
    if build_ok:
        # Test dry-run
        dry_run_ok, _, _ = test_dry_run_operation(project_path, "weather")
        
        if dry_run_ok:
            print("✅ Streamlit workflow test successful!")
        else:
            print("❌ Dry-run failed")
    else:
        print("❌ Build failed")


def main():
    """Main test harness"""
    print("🧪 Cognite Toolkit Operations Test Harness")
    print("=" * 60)
    print()
    
    # Setup environment
    if not setup_test_environment():
        sys.exit(1)
    
    # Menu
    while True:
        print("Select test to run:")
        print("1. Test with downloaded repo (simulates Streamlit workflow)")
        print("2. Test with current project (weather module)")
        print("3. Test build only")
        print("4. Test dry-run only") 
        print("5. Test deploy only")
        print("6. Exit")
        print()
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            test_with_downloaded_repo()
        elif choice == '2':
            test_streamlit_workflow()
        elif choice == '3':
            project_path = input("Enter project path (or press Enter for current): ").strip()
            if not project_path:
                project_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart"
            env_name = input("Enter environment name (default: weather): ").strip() or "weather"
            test_build_operation(project_path, env_name)
        elif choice == '4':
            project_path = input("Enter project path (or press Enter for current): ").strip()
            if not project_path:
                project_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart"
            env_name = input("Enter environment name (default: weather): ").strip() or "weather"
            test_dry_run_operation(project_path, env_name)
        elif choice == '5':
            project_path = input("Enter project path (or press Enter for current): ").strip()
            if not project_path:
                project_path = "/Users/brent.groom@cognitedata.com/p/cognite-quickstart"
            env_name = input("Enter environment name (default: weather): ").strip() or "weather"
            confirm = input("⚠️  This will deploy to CDF! Are you sure? (y/N): ")
            if confirm.lower() == 'y':
                test_deploy_operation(project_path, env_name)
            else:
                print("❌ Deploy cancelled")
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again")
        
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
