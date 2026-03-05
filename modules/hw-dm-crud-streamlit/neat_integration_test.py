#!/usr/bin/env python3
"""
NEAT Integration Testing Script

This script integrates NEAT data model testing with the Cognite Toolkit workflow,
providing end-to-end testing from deployment to data operations.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Import our testing modules
from test_neat_data_model import NeatDataModelTester
from sample_data_generator import SampleDataGenerator

try:
    from cognite_toolkit._cdf_tk.commands.build_cmd import BuildCommand
    from cognite_toolkit._cdf_tk.commands.deploy import DeployCommand
    from cognite_toolkit._cdf_tk.utils.auth import EnvironmentVariables
except ImportError:
    print("❌ cognite-toolkit not available. Some features will be limited.")
    BuildCommand = None
    DeployCommand = None
    EnvironmentVariables = None


class NeatIntegrationTester:
    """Integration tester for NEAT with Cognite Toolkit"""
    
    def __init__(self):
        """Initialize the integration tester"""
        self.project_path = Path("/Users/brent.groom@cognitedata.com/p/cognite-quickstart")
        self.build_dir = self.project_path / "build"
        self.neat_module_path = self.project_path / "modules" / "hw-neat"
        self.build_env_name = "weather"  # Using existing environment
        
        self.tester = None
        self.generator = None
        self.test_results = []
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are met"""
        checks = {}
        
        # Environment variables
        checks['cdf_project'] = bool(os.getenv('CDF_PROJECT'))
        checks['cdf_cluster'] = bool(os.getenv('CDF_CLUSTER'))
        
        # Paths
        checks['project_path'] = self.project_path.exists()
        checks['neat_module'] = self.neat_module_path.exists()
        checks['build_dir'] = self.build_dir.exists()
        
        # Toolkit availability
        checks['toolkit_available'] = BuildCommand is not None
        
        # NEAT module files
        checks['neat_space'] = (self.neat_module_path / "data_models" / "hw-neat.space.yaml").exists()
        checks['neat_container'] = (self.neat_module_path / "data_models" / "containers" / "BasicAsset.container.yaml").exists()
        checks['neat_view'] = (self.neat_module_path / "data_models" / "views" / "BasicAsset.view.yaml").exists()
        
        return checks
    
    def print_prerequisites_status(self, checks: Dict[str, bool]):
        """Print status of prerequisites"""
        print("🔍 Prerequisites Check")
        print("=" * 40)
        
        for check, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"{icon} {check.replace('_', ' ').title()}: {status}")
        
        all_good = all(checks.values())
        print(f"\n{'✅ All prerequisites met!' if all_good else '❌ Some prerequisites missing'}")
        return all_good
    
    def run_toolkit_build(self) -> Dict[str, Any]:
        """Run toolkit build for hw-neat module"""
        if not BuildCommand:
            return {"success": False, "error": "Toolkit not available"}
        
        print("\n🏗️  Building NEAT module with Cognite Toolkit")
        print("=" * 60)
        
        try:
            build_cmd = BuildCommand()
            
            print(f"📁 Project: {self.project_path}")
            print(f"🏗️  Build dir: {self.build_dir}")
            print(f"📋 Environment: {self.build_env_name}")
            print(f"🎯 Module: hw-neat")
            print()
            
            # Execute build for hw-neat module only
            result = build_cmd.execute(
                verbose=True,
                organization_dir=self.project_path,
                build_dir=self.build_dir,
                selected=["hw-neat"],  # Build only hw-neat module
                build_env_name=self.build_env_name,
                no_clean=False,
                client=None,
                on_error='continue'
            )
            
            success = result is not None and len(result) > 0
            
            if success:
                print("✅ Toolkit build completed successfully!")
                return {
                    "success": True,
                    "built_modules": result,
                    "module_count": len(result)
                }
            else:
                print("❌ Toolkit build failed or no modules built")
                return {
                    "success": False,
                    "error": "No modules were built"
                }
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_toolkit_deploy(self, dry_run: bool = True) -> Dict[str, Any]:
        """Run toolkit deploy for built modules"""
        if not DeployCommand or not EnvironmentVariables:
            return {"success": False, "error": "Toolkit not available"}
        
        print(f"\n🚀 Deploying with Cognite Toolkit (dry_run={dry_run})")
        print("=" * 60)
        
        try:
            deploy_cmd = DeployCommand()
            env_vars = EnvironmentVariables()
            
            print(f"📁 Build dir: {self.build_dir}")
            print(f"📋 Environment: {self.build_env_name}")
            print(f"🔍 Dry run: {dry_run}")
            print()
            
            # Execute deploy
            result = deploy_cmd.deploy_build_directory(
                env_vars=env_vars,
                build_dir=self.build_dir,
                build_env_name=self.build_env_name,
                dry_run=dry_run,
                drop=False,
                drop_data=False,
                force_update=False,
                include=None,
                verbose=True
            )
            
            print("✅ Toolkit deploy completed!")
            return {
                "success": True,
                "result": result,
                "dry_run": dry_run
            }
            
        except Exception as e:
            print(f"❌ Deploy failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_neat_tests(self) -> Dict[str, Any]:
        """Run NEAT data model tests"""
        print("\n🧪 Running NEAT Data Model Tests")
        print("=" * 60)
        
        try:
            if not self.tester:
                self.tester = NeatDataModelTester()
            
            summary = self.tester.run_all_tests()
            return summary
            
        except Exception as e:
            print(f"❌ NEAT tests failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_sample_data_operations(self, count: int = 5) -> Dict[str, Any]:
        """Run sample data operations"""
        print(f"\n🏭 Running Sample Data Operations ({count} assets)")
        print("=" * 60)
        
        try:
            if not self.generator:
                self.generator = SampleDataGenerator()
            
            # Create sample data
            result = self.generator.create_sample_data(count=count, dry_run=False)
            
            if result['success']:
                print(f"✅ Created {result['created']} sample assets")
                
                # List existing assets
                print("\n📋 Listing existing assets:")
                assets = self.generator.list_existing_assets(limit=10)
                
                return {
                    "success": True,
                    "created": result['created'],
                    "total_assets": len(assets)
                }
            else:
                print(f"❌ Sample data creation failed: {result.get('error')}")
                return result
                
        except Exception as e:
            print(f"❌ Sample data operations failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_full_integration_test(self, deploy_for_real: bool = False) -> Dict[str, Any]:
        """Run complete integration test"""
        print("🎯 NEAT Integration Test - Full Workflow")
        print("=" * 80)
        
        results = {
            "start_time": time.time(),
            "steps": {},
            "overall_success": True
        }
        
        # Step 1: Prerequisites
        print("\n📋 Step 1: Prerequisites Check")
        checks = self.check_prerequisites()
        prereq_ok = self.print_prerequisites_status(checks)
        results["steps"]["prerequisites"] = {"success": prereq_ok, "checks": checks}
        
        if not prereq_ok:
            results["overall_success"] = False
            return results
        
        # Step 2: Build
        print("\n🏗️  Step 2: Toolkit Build")
        build_result = self.run_toolkit_build()
        results["steps"]["build"] = build_result
        
        if not build_result["success"]:
            results["overall_success"] = False
            print("❌ Build failed, stopping integration test")
            return results
        
        # Step 3: Deploy (dry run first)
        print("\n🚀 Step 3: Toolkit Deploy (Dry Run)")
        dry_deploy_result = self.run_toolkit_deploy(dry_run=True)
        results["steps"]["dry_deploy"] = dry_deploy_result
        
        if not dry_deploy_result["success"]:
            results["overall_success"] = False
            print("❌ Dry run deploy failed, stopping integration test")
            return results
        
        # Step 4: Real deploy (if requested)
        if deploy_for_real:
            print("\n🚀 Step 4: Toolkit Deploy (Real)")
            real_deploy_result = self.run_toolkit_deploy(dry_run=False)
            results["steps"]["real_deploy"] = real_deploy_result
            
            if not real_deploy_result["success"]:
                results["overall_success"] = False
                print("❌ Real deploy failed, stopping integration test")
                return results
        else:
            print("\n⏭️  Step 4: Skipping real deploy")
            results["steps"]["real_deploy"] = {"skipped": True}
        
        # Step 5: NEAT Tests
        print("\n🧪 Step 5: NEAT Data Model Tests")
        test_result = self.run_neat_tests()
        results["steps"]["neat_tests"] = test_result
        
        if test_result.get("failed", 0) > 0:
            results["overall_success"] = False
            print("❌ Some NEAT tests failed")
        
        # Step 6: Sample Data
        print("\n🏭 Step 6: Sample Data Operations")
        sample_result = self.run_sample_data_operations(count=3)
        results["steps"]["sample_data"] = sample_result
        
        if not sample_result.get("success", False):
            results["overall_success"] = False
            print("❌ Sample data operations failed")
        
        # Summary
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        for step_name, step_result in results["steps"].items():
            if step_result.get("skipped"):
                print(f"⏭️  {step_name.replace('_', ' ').title()}: Skipped")
            elif step_result.get("success", False):
                print(f"✅ {step_name.replace('_', ' ').title()}: Passed")
            else:
                print(f"❌ {step_name.replace('_', ' ').title()}: Failed")
        
        overall_icon = "✅" if results["overall_success"] else "❌"
        print(f"\n{overall_icon} Overall Result: {'SUCCESS' if results['overall_success'] else 'FAILED'}")
        print(f"⏱️  Total Duration: {results['duration']:.2f}s")
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save integration test results to file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"neat_integration_test_results_{timestamp}.json"
        
        filepath = self.neat_module_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filepath}")
        return str(filepath)


def main():
    """Main function"""
    print("🎯 NEAT Integration Testing Suite")
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
        tester = NeatIntegrationTester()
        
        # Interactive menu
        while True:
            print("Select test to run:")
            print("1. Prerequisites check only")
            print("2. Build and dry-run deploy only")
            print("3. Full integration test (no real deploy)")
            print("4. Full integration test (with real deploy)")
            print("5. NEAT tests only")
            print("6. Sample data operations only")
            print("7. Exit")
            print()
            
            choice = input("Enter choice (1-7): ").strip()
            
            if choice == '1':
                checks = tester.check_prerequisites()
                tester.print_prerequisites_status(checks)
                
            elif choice == '2':
                build_result = tester.run_toolkit_build()
                if build_result["success"]:
                    tester.run_toolkit_deploy(dry_run=True)
                
            elif choice == '3':
                results = tester.run_full_integration_test(deploy_for_real=False)
                tester.save_results(results)
                
            elif choice == '4':
                confirm = input("⚠️  This will deploy to CDF! Continue? (y/N): ")
                if confirm.lower() == 'y':
                    results = tester.run_full_integration_test(deploy_for_real=True)
                    tester.save_results(results)
                else:
                    print("⏭️  Cancelled real deployment")
                    
            elif choice == '5':
                tester.run_neat_tests()
                
            elif choice == '6':
                count = int(input("How many sample assets to create? (default: 3): ") or "3")
                tester.run_sample_data_operations(count=count)
                
            elif choice == '7':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice, please try again")
            
            print("\n" + "=" * 80 + "\n")
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
