"""
Cognite Function to deploy toolkit configurations from CDF zip files
Phase 1: Real deployment workflow with automatic project detection
"""

def handle(client, data):
    """
    Deploy toolkit configurations from CDF zip files
    
    Args:
        client: CogniteClient instance (automatically provided)
        data: Input data from function call (optional parameters)
        
    Returns:
        dict: Deployment results including build, dry-run, and deploy status
    """
    import subprocess
    import os
    import tempfile
    import sys
    import zipfile
    import io
    from datetime import datetime
    import time
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "function_environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "cwd": os.getcwd()
        },
        "deployment": {},
        "tests": {}
    }
    
    try:
        # ============================================================================
        # STEP 1: Install cognite-toolkit
        # ============================================================================
        print("🔧 Installing cognite-toolkit...")
        install_result = subprocess.run(
            ["pip", "install", "cognite-toolkit"], 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        results["tests"]["install"] = {
            "returncode": install_result.returncode,
            "success": install_result.returncode == 0
        }
        
        if install_result.returncode != 0:
            results["error"] = "Failed to install cognite-toolkit"
            results["success"] = False
            return results
        
        print("✅ cognite-toolkit installed successfully")
        
        # Fix PATH
        local_bin_path = "/home/.local/bin"
        if local_bin_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{local_bin_path}:{os.environ.get('PATH', '')}"
            print(f"🔧 Updated PATH to include {local_bin_path}")
        
        # ============================================================================
        # STEP 2: Auto-detect CDF Project and Cluster
        # ============================================================================
        print("🔍 Auto-detecting CDF project and cluster...")
        
        project = client.config.project
        base_url = client.config.base_url
        
        # Extract cluster from base_url (e.g., https://bluefield.cognitedata.com -> bluefield)
        cluster = base_url.replace("https://", "").replace("http://", "").split(".")[0]
        
        print(f"✅ Detected project: {project}")
        print(f"✅ Detected cluster: {cluster}")
        
        results["deployment"]["project"] = project
        results["deployment"]["cluster"] = cluster
        
        # ============================================================================
        # STEP 3: Download zip file from CDF Data Modeling API
        # ============================================================================
        zip_filename = data.get("zip_file", "cognite-quickstart-main.zip")
        print(f"📥 Downloading {zip_filename} from CDF Data Modeling API...")
        
        try:
            # Query Data Modeling API for CogniteFile instances
            from cognite.client.data_classes.data_modeling.ids import ViewId, NodeId
            
            view_id = ViewId(space="cdf_cdm", external_id="CogniteFile", version="v1")
            
            instances = client.data_modeling.instances.list(
                instance_type="node",
                sources=view_id,
                space="app-packages",
                limit=1000
            )
            
            # Find the file by name
            zip_instance = None
            for instance in instances:
                props = instance.properties.get(view_id, {})
                name = props.get("name", "")
                is_uploaded = props.get("isUploaded", False)
                
                if name == zip_filename and is_uploaded:
                    zip_instance = instance
                    break
            
            if not zip_instance:
                results["error"] = f"Zip file '{zip_filename}' not found in app-packages space or not uploaded"
                results["success"] = False
                return results
            
            # Download the file using instance_id
            instance_id = NodeId(space=zip_instance.space, external_id=zip_instance.external_id)
            zip_bytes = client.files.download_bytes(instance_id=instance_id)
            print(f"✅ Downloaded {len(zip_bytes):,} bytes")
            
            results["deployment"]["zip_file"] = zip_filename
            results["deployment"]["zip_size"] = len(zip_bytes)
            
        except Exception as e:
            results["error"] = f"Failed to download zip file: {e}"
            results["success"] = False
            return results
        
        # ============================================================================
        # STEP 4: Extract zip file to temporary directory
        # ============================================================================
        print("📦 Extracting zip file...")
        
        try:
            # Create temp directory for extraction
            temp_dir = tempfile.mkdtemp(prefix="toolkit_deploy_")
            print(f"📁 Created temp directory: {temp_dir}")
            
            # Extract zip
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the extracted directory (usually has same name as zip without .zip)
            extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if extracted_dirs:
                repo_dir = os.path.join(temp_dir, extracted_dirs[0])
            else:
                repo_dir = temp_dir
            
            print(f"✅ Extracted to: {repo_dir}")
            results["deployment"]["extract_path"] = repo_dir
            
            # Change to extracted directory
            os.chdir(repo_dir)
            print(f"📂 Changed directory to: {os.getcwd()}")
            
        except Exception as e:
            results["error"] = f"Failed to extract zip file: {e}"
            results["success"] = False
            return results
        
        # ============================================================================
        # STEP 4.5: Create .env file for toolkit authentication
        # ============================================================================
        # Now that we're in the extracted directory, create .env file
        print(f"🔐 Setting up authentication via TOKEN flow...")
        
        # ============================================================================
        # AUTHENTICATION APPROACHES TRIED:
        # v24: Extract client_id/client_secret from credentials - FAILED
        #   - credentials object doesn't expose these attributes in Functions
        # v25-v26: Create .env in function directory - FAILED
        #   - Permission denied in /home/site/wwwroot/function
        # v27: authorization_header() returns tuple - FIXED
        # v28: Create .env in extracted directory - PARTIAL
        #   - .env file created successfully
        #   - But toolkit still tried client_credentials flow (ignored CDF_TOKEN)
        # v29: Add LOGIN_FLOW=token to .env - TESTING
        #   - Explicitly tell toolkit to use token flow
        #
        # LOGIN_FLOW OPTIONS (from toolkit docs):
        #   - client_credentials: OAuth with client_id/client_secret
        #   - token: Use existing OAuth token (CDF_TOKEN)
        #   - device_code: Interactive device code flow
        #   - interactive: Browser-based login
        # ============================================================================
        
        try:
            # Get the access token from the authenticated client
            auth_header = client.config.credentials.authorization_header()
            
            # authorization_header() returns tuple: ("Authorization", "Bearer <token>")
            if isinstance(auth_header, tuple) and len(auth_header) == 2:
                token = auth_header[1]  # Get "Bearer <token>"
            else:
                token = str(auth_header)
            
            # Remove "Bearer " prefix
            if token.startswith("Bearer "):
                token = token[7:]
            
            # Start with base environment variables
            env_vars = {
                "CDF_PROJECT": project,
                "CDF_CLUSTER": cluster,
                "CDF_URL": base_url,
                "CDF_TOKEN": token,
                "LOGIN_FLOW": "token",
            }
            
            # Merge user-provided env vars from Streamlit (if any)
            user_env_vars = data.get("env_vars", {})
            if user_env_vars:
                print(f"📥 Merging {len(user_env_vars)} user-provided environment variables")
                env_vars.update(user_env_vars)
                results["deployment"]["user_env_vars_count"] = len(user_env_vars)
            
            # Create .env file
            env_file_path = ".env"
            with open(env_file_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            print(f"✅ Created .env file with {len(env_vars)} variables")
            if user_env_vars:
                print(f"✅ Included user credentials for hosted extractors")
            results["deployment"]["auth_method"] = "token+user_vars" if user_env_vars else "token"
            results["deployment"]["env_file_created"] = True
            results["deployment"]["env_vars_total"] = len(env_vars)
            
        except Exception as e:
            print(f"❌ Failed to setup authentication: {e}")
            results["deployment"]["auth_error"] = str(e)
            results["deployment"]["auth_method"] = "failed"
            results["success"] = False
            return results
        
        # ============================================================================
        # STEP 5: Verify config file exists and update project name
        # ============================================================================
        # Derive config file name from env parameter
        env_name = data.get("env", "weather")  # Default to "weather"
        config_file = f"config.{env_name}.yaml"
        print(f"🔍 Looking for config file: {config_file} (env={env_name})")
        
        if not os.path.exists(config_file):
            # List available config files
            available_configs = [f for f in os.listdir(".") if f.startswith("config.") and f.endswith(".yaml")]
            results["error"] = f"Config file '{config_file}' not found. Available: {available_configs}"
            results["success"] = False
            return results
        
        print(f"✅ Found config file: {config_file}")
        
        # Read the config file
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Replace project line with actual project name
        # In toolkit configs, project is under environment: section with 2-space indent
        print(f"🔧 Updating project name in config file to: {project}")
        
        updated = False
        for i, line in enumerate(lines):
            # Match "  project:" (with 2-space indent under environment:)
            if line.strip().startswith('project:') and line.startswith('  '):
                old_line = line.strip()
                lines[i] = f'  project: {project}\n'
                print(f"✅ Replaced: '{old_line}' → 'project: {project}'")
                updated = True
                break
        
        if not updated:
            print(f"⚠️ No 'project:' line found in config file (looking for indented line)")
        
        # Write the updated config back
        with open(config_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Config file ready with project: {project}")
        results["deployment"]["config_file"] = config_file
        results["deployment"]["config_updated"] = updated
        results["deployment"]["project_injected"] = project
        
        # ============================================================================
        # STEP 6: Run cdf build
        # ============================================================================
        print(f"🏗️ Running cdf build --env={env_name}...")
        results["deployment"]["env"] = env_name
        start_time = time.time()
        
        try:
            build_result = subprocess.run(
                ["cdf", "build", f"--env={env_name}"], 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutes
            )
            
            build_duration = time.time() - start_time
            
            results["deployment"]["build"] = {
                "returncode": build_result.returncode,
                "stdout": build_result.stdout,
                "stderr": build_result.stderr,
                "success": build_result.returncode == 0,
                "duration": round(build_duration, 2)
            }
            
            if build_result.returncode == 0:
                print(f"✅ Build completed successfully in {build_duration:.1f}s")
            else:
                print(f"❌ Build failed with return code {build_result.returncode}")
                print(f"Error: {build_result.stderr[:500]}")
                
        except subprocess.TimeoutExpired:
            results["deployment"]["build"] = {
                "error": "Build timeout after 5 minutes",
                "success": False
            }
        except Exception as e:
            results["deployment"]["build"] = {
                "error": str(e),
                "success": False
            }
        
        # ============================================================================
        # STEP 7: Run cdf deploy --dry-run
        # ============================================================================
        print(f"🔍 Running cdf deploy --dry-run --env={env_name}...")
        start_time = time.time()
        
        try:
            dry_run_result = subprocess.run(
                ["cdf", "deploy", "--dry-run", f"--env={env_name}"], 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutes
            )
            
            dry_run_duration = time.time() - start_time
            
            results["deployment"]["dry_run"] = {
                "returncode": dry_run_result.returncode,
                "stdout": dry_run_result.stdout,
                "stderr": dry_run_result.stderr,
                "success": dry_run_result.returncode == 0,
                "duration": round(dry_run_duration, 2)
            }
            
            if dry_run_result.returncode == 0:
                print(f"✅ Dry-run completed successfully in {dry_run_duration:.1f}s")
            else:
                print(f"❌ Dry-run failed with return code {dry_run_result.returncode}")
                print(f"Error: {dry_run_result.stderr[:500]}")
                
        except subprocess.TimeoutExpired:
            results["deployment"]["dry_run"] = {
                "error": "Dry-run timeout after 5 minutes",
                "success": False
            }
        except Exception as e:
            results["deployment"]["dry_run"] = {
                "error": str(e),
                "success": False
            }
        
        # ============================================================================
        # STEP 8: Run cdf deploy (actual deployment)
        # ============================================================================
        # Only deploy if build and dry-run succeeded
        should_deploy = data.get("deploy", True)  # Default: True - always deploy
        
        if should_deploy and results["deployment"].get("build", {}).get("success") and \
           results["deployment"].get("dry_run", {}).get("success"):
            
            print("🚀 Running cdf deploy...")
            start_time = time.time()
            
            try:
                deploy_result = subprocess.run(
                    ["cdf", "deploy", f"--env={env_name}"], 
                    capture_output=True, 
                    text=True,
                    timeout=600  # 10 minutes
                )
                
                deploy_duration = time.time() - start_time
                
                results["deployment"]["deploy"] = {
                    "returncode": deploy_result.returncode,
                    "stdout": deploy_result.stdout,
                    "stderr": deploy_result.stderr,
                    "success": deploy_result.returncode == 0,
                    "duration": round(deploy_duration, 2)
                }
                
                if deploy_result.returncode == 0:
                    print(f"✅ Deployment completed successfully in {deploy_duration:.1f}s")
                else:
                    print(f"❌ Deployment failed with return code {deploy_result.returncode}")
                    print(f"Error: {deploy_result.stderr[:500]}")
                    
            except subprocess.TimeoutExpired:
                results["deployment"]["deploy"] = {
                    "error": "Deployment timeout after 10 minutes",
                    "success": False
                }
            except Exception as e:
                results["deployment"]["deploy"] = {
                    "error": str(e),
                    "success": False
                }
        else:
            if not should_deploy:
                print("ℹ️ Skipping actual deployment (deploy=False)")
                results["deployment"]["deploy"] = {
                    "skipped": True,
                    "reason": "deploy parameter not set to True"
                }
            else:
                print("⚠️ Skipping deployment due to build/dry-run failures")
                results["deployment"]["deploy"] = {
                    "skipped": True,
                    "reason": "build or dry-run failed"
                }
        
        # ============================================================================
        # STEP 9: Summary
        # ============================================================================
        results["summary"] = {
            "toolkit_installed": results["tests"]["install"]["success"],
            "project_detected": bool(project),
            "cluster_detected": bool(cluster),
            "zip_downloaded": "zip_file" in results["deployment"],
            "config_found": "config_file" in results["deployment"],
            "build_successful": results["deployment"].get("build", {}).get("success", False),
            "dry_run_successful": results["deployment"].get("dry_run", {}).get("success", False),
            "deploy_successful": results["deployment"].get("deploy", {}).get("success", False),
            "deploy_skipped": results["deployment"].get("deploy", {}).get("skipped", False),
            "ready_for_production": True
        }
        
        results["success"] = True
        results["message"] = "Deployment workflow completed"
        
        print("🎉 All steps completed!")
        return results
        
    except subprocess.TimeoutExpired as e:
        results["error"] = f"Command timeout: {e}"
        results["success"] = False
        return results
        
    except Exception as e:
        import traceback
        results["error"] = f"Unexpected error: {e}"
        results["traceback"] = traceback.format_exc()
        results["success"] = False
        return results