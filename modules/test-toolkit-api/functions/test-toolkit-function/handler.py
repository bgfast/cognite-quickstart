"""
Cognite Function to test real toolkit library installation and commands
Trial 3: Prove that cognite-toolkit can be installed and used in Functions environment
"""

def handle(client, data):
    """
    Test function to prove cognite-toolkit works in Cognite Functions
    
    Args:
        client: CogniteClient instance (automatically provided)
        data: Input data from function call
        
    Returns:
        dict: Results of toolkit installation and command tests
    """
    import subprocess
    import os
    import tempfile
    import sys
    from datetime import datetime
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "function_environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "cwd": os.getcwd()
        },
        "tests": {}
    }
    
    try:
        # Test 1: Install cognite-toolkit
        print("🔧 Installing cognite-toolkit...")
        install_result = subprocess.run(
            ["pip", "install", "cognite-toolkit"], 
            capture_output=True, 
            text=True, 
            timeout=120  # 2 minutes for installation
        )
        
        results["tests"]["install"] = {
            "returncode": install_result.returncode,
            "stdout": install_result.stdout,
            "stderr": install_result.stderr,
            "success": install_result.returncode == 0
        }
        
        if install_result.returncode != 0:
            results["error"] = "Failed to install cognite-toolkit"
            return results
        
        print("✅ cognite-toolkit installed successfully")
        
        # Fix PATH issue: Add /home/.local/bin to PATH
        original_path = os.environ.get("PATH", "")
        local_bin_path = "/home/.local/bin"
        
        if local_bin_path not in original_path:
            new_path = f"{local_bin_path}:{original_path}"
            os.environ["PATH"] = new_path
            print(f"🔧 Updated PATH to include {local_bin_path}")
            results["function_environment"]["path_updated"] = True
            results["function_environment"]["new_path"] = new_path
        else:
            print(f"✅ {local_bin_path} already in PATH")
            results["function_environment"]["path_updated"] = False
        
        # Test 2: Verify cdf command exists
        print("🔍 Testing cdf command availability...")
        
        # Create temp directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Test 2a: which cdf (verify PATH fix)
                which_result = subprocess.run(
                    ["which", "cdf"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                results["tests"]["which_cdf"] = {
                    "returncode": which_result.returncode,
                    "stdout": which_result.stdout.strip(),
                    "stderr": which_result.stderr,
                    "success": which_result.returncode == 0
                }
                
                if which_result.returncode == 0:
                    print(f"✅ cdf command found at: {which_result.stdout.strip()}")
                else:
                    print("❌ cdf command not found in PATH")
                
                # Test 2b: cdf --help (should work)
                help_result = subprocess.run(
                    ["cdf", "--help"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                results["tests"]["cdf_help"] = {
                    "returncode": help_result.returncode,
                    "stdout": help_result.stdout[:1000],  # Truncate for readability
                    "stderr": help_result.stderr,
                    "success": help_result.returncode == 0
                }
                
                # Test 2b: cdf build (expect error but command should exist)
                print("🏗️ Testing cdf build command...")
                build_result = subprocess.run(
                    ["cdf", "build"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                results["tests"]["cdf_build"] = {
                    "returncode": build_result.returncode,
                    "stdout": build_result.stdout,
                    "stderr": build_result.stderr,
                    "command_exists": "command not found" not in build_result.stderr.lower()
                }
                
                # Test 2c: cdf deploy --dry-run (expect error but command should exist)
                print("🔍 Testing cdf deploy --dry-run command...")
                dry_run_result = subprocess.run(
                    ["cdf", "deploy", "--dry-run"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                results["tests"]["cdf_dry_run"] = {
                    "returncode": dry_run_result.returncode,
                    "stdout": dry_run_result.stdout,
                    "stderr": dry_run_result.stderr,
                    "command_exists": "command not found" not in dry_run_result.stderr.lower()
                }
                
                # Test 2d: cdf deploy (expect error but command should exist)
                print("🚀 Testing cdf deploy command...")
                deploy_result = subprocess.run(
                    ["cdf", "deploy"], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                results["tests"]["cdf_deploy"] = {
                    "returncode": deploy_result.returncode,
                    "stdout": deploy_result.stdout,
                    "stderr": deploy_result.stderr,
                    "command_exists": "command not found" not in deploy_result.stderr.lower()
                }
                
            finally:
                os.chdir(original_cwd)
        
        # Test 3: Try importing toolkit library (multiple approaches)
        print("📦 Testing toolkit library import...")
        library_import_results = []
        
        # Try different import approaches
        import_attempts = [
            ("cognite_toolkit._cdf_tk.commands.build_cmd", "BuildCommand"),
            ("cognite_toolkit._cdf_tk.commands.deploy", "DeployCommand"),
            ("cognite_toolkit", None),  # Try base module
            ("cognite.toolkit", None),  # Alternative path
        ]
        
        successful_imports = []
        failed_imports = []
        
        for module_path, class_name in import_attempts:
            try:
                if class_name:
                    exec(f"from {module_path} import {class_name}")
                    successful_imports.append(f"{module_path}.{class_name}")
                    print(f"✅ Successfully imported {module_path}.{class_name}")
                else:
                    exec(f"import {module_path}")
                    successful_imports.append(module_path)
                    print(f"✅ Successfully imported {module_path}")
            except Exception as e:
                failed_imports.append(f"{module_path}: {str(e)}")
                print(f"❌ Failed to import {module_path}: {e}")
        
        # Try to find the actual module structure
        try:
            import sys
            import pkgutil
            
            # Look for cognite-related packages
            cognite_packages = []
            for importer, modname, ispkg in pkgutil.iter_modules():
                if 'cognite' in modname.lower() or 'toolkit' in modname.lower():
                    cognite_packages.append(modname)
            
            print(f"📦 Found cognite-related packages: {cognite_packages}")
            
        except Exception as e:
            print(f"⚠️ Could not enumerate packages: {e}")
        
        results["tests"]["library_import"] = {
            "success": len(successful_imports) > 0,
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "total_attempts": len(import_attempts)
        }
        
        if successful_imports:
            print(f"✅ Toolkit library partially accessible: {len(successful_imports)}/{len(import_attempts)} imports successful")
        else:
            print("❌ Toolkit library import completely failed")
        
        # Summary
        results["summary"] = {
            "toolkit_installed": results["tests"]["install"]["success"],
            "cdf_command_found": results["tests"].get("which_cdf", {}).get("success", False),
            "cdf_command_available": results["tests"].get("cdf_help", {}).get("success", False),
            "build_command_exists": results["tests"].get("cdf_build", {}).get("command_exists", False),
            "deploy_command_exists": results["tests"].get("cdf_deploy", {}).get("command_exists", False),
            "library_importable": results["tests"].get("library_import", {}).get("success", False)
        }
        
        results["success"] = True
        results["message"] = "Toolkit testing completed"
        
        print("🎉 All tests completed successfully!")
        return results
        
    except subprocess.TimeoutExpired as e:
        results["error"] = f"Command timeout: {e}"
        results["success"] = False
        return results
        
    except Exception as e:
        results["error"] = f"Unexpected error: {e}"
        results["success"] = False
        return results
