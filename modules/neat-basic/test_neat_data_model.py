#!/usr/bin/env python3
"""
NEAT Data Model Testing Script

This script provides comprehensive testing for the neat-basic data model,
including deployment validation, data operations, and model integrity checks.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

try:
    from cognite.client import CogniteClient
    from cognite.client.data_classes import (
        Space, Container, View, DataModelId, 
        NodeApply, EdgeApply, InstancesApply
    )
    from cognite.client.exceptions import CogniteAPIError, CogniteNotFoundError
except ImportError:
    print("❌ cognite-sdk not installed. Please install with: pip install cognite-sdk")
    sys.exit(1)


@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    duration: float = 0.0


class NeatDataModelTester:
    """Comprehensive tester for NEAT data models"""
    
    def __init__(self, client: Optional[CogniteClient] = None):
        """Initialize the tester"""
        self.client = client or self._create_client()
        self.space_id = "neat-basic"
        self.container_id = "BasicAsset"
        self.view_id = "BasicAsset"
        self.test_results: List[TestResult] = []
        
    def _create_client(self) -> CogniteClient:
        """Create CogniteClient from environment variables"""
        project = os.getenv('CDF_PROJECT')
        cluster = os.getenv('CDF_CLUSTER', 'api')
        
        if not project:
            raise ValueError("CDF_PROJECT environment variable not set")
            
        # Try to use token from environment
        token = os.getenv('CDF_TOKEN')
        if token:
            return CogniteClient(
                api_key=None,
                project=project,
                base_url=f"https://{cluster}.cognitedata.com",
                token=token
            )
        else:
            # Fall back to interactive auth
            return CogniteClient.default_oauth_interactive(
                project=project,
                cdf_cluster=cluster
            )
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test and capture results"""
        print(f"🧪 Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if isinstance(result, TestResult):
                result.duration = duration
                test_result = result
            else:
                test_result = TestResult(
                    test_name=test_name,
                    success=True,
                    message="Test passed",
                    duration=duration
                )
            
            status = "✅" if test_result.success else "❌"
            print(f"   {status} {test_result.message} ({duration:.2f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                message=f"Test failed: {str(e)}",
                duration=duration
            )
            print(f"   ❌ {test_result.message} ({duration:.2f}s)")
        
        self.test_results.append(test_result)
        return test_result
    
    def test_space_exists(self) -> TestResult:
        """Test that the neat-basic space exists"""
        try:
            space = self.client.data_modeling.spaces.retrieve(self.space_id)
            if space:
                return TestResult(
                    test_name="space_exists",
                    success=True,
                    message=f"Space '{self.space_id}' exists",
                    details={"space": space.dump()}
                )
            else:
                return TestResult(
                    test_name="space_exists",
                    success=False,
                    message=f"Space '{self.space_id}' not found"
                )
        except CogniteNotFoundError:
            return TestResult(
                test_name="space_exists",
                success=False,
                message=f"Space '{self.space_id}' not found"
            )
    
    def test_container_exists(self) -> TestResult:
        """Test that the BasicAsset container exists"""
        try:
            container = self.client.data_modeling.containers.retrieve(
                (self.space_id, self.container_id)
            )
            if container:
                # Validate container properties
                expected_props = {"name", "description", "type"}
                actual_props = set(container.properties.keys())
                
                if expected_props.issubset(actual_props):
                    return TestResult(
                        test_name="container_exists",
                        success=True,
                        message=f"Container '{self.container_id}' exists with correct properties",
                        details={
                            "container": container.dump(),
                            "properties": list(actual_props)
                        }
                    )
                else:
                    missing = expected_props - actual_props
                    return TestResult(
                        test_name="container_exists",
                        success=False,
                        message=f"Container missing properties: {missing}"
                    )
            else:
                return TestResult(
                    test_name="container_exists",
                    success=False,
                    message=f"Container '{self.container_id}' not found"
                )
        except CogniteNotFoundError:
            return TestResult(
                test_name="container_exists",
                success=False,
                message=f"Container '{self.container_id}' not found"
            )
    
    def test_view_exists(self) -> TestResult:
        """Test that the BasicAsset view exists"""
        try:
            view = self.client.data_modeling.views.retrieve(
                (self.space_id, self.view_id, "1")
            )
            if view:
                # Validate view properties
                expected_props = {"name", "description", "type"}
                actual_props = set(view.properties.keys())
                
                if expected_props.issubset(actual_props):
                    return TestResult(
                        test_name="view_exists",
                        success=True,
                        message=f"View '{self.view_id}' exists with correct properties",
                        details={
                            "view": view.dump(),
                            "properties": list(actual_props)
                        }
                    )
                else:
                    missing = expected_props - actual_props
                    return TestResult(
                        test_name="view_exists",
                        success=False,
                        message=f"View missing properties: {missing}"
                    )
            else:
                return TestResult(
                    test_name="view_exists",
                    success=False,
                    message=f"View '{self.view_id}' not found"
                )
        except CogniteNotFoundError:
            return TestResult(
                test_name="view_exists",
                success=False,
                message=f"View '{self.view_id}' not found"
            )
    
    def test_create_instance(self) -> TestResult:
        """Test creating a BasicAsset instance"""
        test_external_id = f"test_asset_{int(time.time())}"
        
        try:
            # Create test instance
            node = NodeApply(
                space=self.space_id,
                external_id=test_external_id,
                sources=[
                    {
                        "source": {
                            "space": self.space_id,
                            "externalId": self.container_id,
                            "version": "1"
                        },
                        "properties": {
                            "name": "Test Asset",
                            "description": "Test asset created by NEAT testing script",
                            "type": "test"
                        }
                    }
                ]
            )
            
            # Apply the instance
            result = self.client.data_modeling.instances.apply(
                nodes=[node],
                auto_create_start_nodes=True,
                auto_create_end_nodes=True
            )
            
            if result.nodes:
                return TestResult(
                    test_name="create_instance",
                    success=True,
                    message=f"Successfully created test instance '{test_external_id}'",
                    details={
                        "external_id": test_external_id,
                        "created_nodes": len(result.nodes)
                    }
                )
            else:
                return TestResult(
                    test_name="create_instance",
                    success=False,
                    message="No nodes were created"
                )
                
        except Exception as e:
            return TestResult(
                test_name="create_instance",
                success=False,
                message=f"Failed to create instance: {str(e)}"
            )
    
    def test_query_instances(self) -> TestResult:
        """Test querying BasicAsset instances"""
        try:
            # Query using the view
            query = f"""
            SELECT 
                node.externalId,
                node.name,
                node.description,
                node.type
            FROM {self.space_id}.{self.view_id} as node
            LIMIT 10
            """
            
            result = self.client.data_modeling.instances.query(query)
            
            return TestResult(
                test_name="query_instances",
                success=True,
                message=f"Successfully queried instances, found {len(result)} results",
                details={
                    "query": query,
                    "result_count": len(result),
                    "results": result[:5]  # First 5 results for inspection
                }
            )
            
        except Exception as e:
            return TestResult(
                test_name="query_instances",
                success=False,
                message=f"Failed to query instances: {str(e)}"
            )
    
    def test_data_validation(self) -> TestResult:
        """Test data validation constraints"""
        test_external_id = f"test_validation_{int(time.time())}"
        
        try:
            # Test 1: Try to create instance without required 'name' field
            node_invalid = NodeApply(
                space=self.space_id,
                external_id=test_external_id,
                sources=[
                    {
                        "source": {
                            "space": self.space_id,
                            "externalId": self.container_id,
                            "version": "1"
                        },
                        "properties": {
                            # Missing required 'name' field
                            "description": "Test without name",
                            "type": "test"
                        }
                    }
                ]
            )
            
            try:
                result = self.client.data_modeling.instances.apply(
                    nodes=[node_invalid],
                    auto_create_start_nodes=True,
                    auto_create_end_nodes=True
                )
                
                # If this succeeds, validation might not be working as expected
                return TestResult(
                    test_name="data_validation",
                    success=False,
                    message="Expected validation error for missing required field, but creation succeeded"
                )
                
            except CogniteAPIError as validation_error:
                # This is expected - validation should fail
                return TestResult(
                    test_name="data_validation",
                    success=True,
                    message="Data validation working correctly - rejected invalid data",
                    details={"validation_error": str(validation_error)}
                )
                
        except Exception as e:
            return TestResult(
                test_name="data_validation",
                success=False,
                message=f"Validation test failed unexpectedly: {str(e)}"
            )
    
    def cleanup_test_data(self) -> TestResult:
        """Clean up test instances created during testing"""
        try:
            # Query for test instances
            query = f"""
            SELECT 
                node.externalId
            FROM {self.space_id}.{self.view_id} as node
            WHERE node.externalId LIKE 'test_%'
            """
            
            result = self.client.data_modeling.instances.query(query)
            
            if result:
                # Delete test instances
                external_ids = [row['node']['externalId'] for row in result]
                
                # Note: In a real scenario, you'd want to delete these instances
                # For now, just report what would be cleaned up
                return TestResult(
                    test_name="cleanup_test_data",
                    success=True,
                    message=f"Found {len(external_ids)} test instances to clean up",
                    details={"test_instances": external_ids}
                )
            else:
                return TestResult(
                    test_name="cleanup_test_data",
                    success=True,
                    message="No test instances found to clean up"
                )
                
        except Exception as e:
            return TestResult(
                test_name="cleanup_test_data",
                success=False,
                message=f"Cleanup failed: {str(e)}"
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🚀 Starting NEAT Data Model Tests")
        print("=" * 60)
        
        # Test deployment
        self.run_test(self.test_space_exists, "Space Deployment")
        self.run_test(self.test_container_exists, "Container Deployment")
        self.run_test(self.test_view_exists, "View Deployment")
        
        # Test data operations
        self.run_test(self.test_create_instance, "Instance Creation")
        self.run_test(self.test_query_instances, "Instance Querying")
        self.run_test(self.test_data_validation, "Data Validation")
        
        # Cleanup
        self.run_test(self.cleanup_test_data, "Test Data Cleanup")
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.test_results)
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_duration": total_duration,
            "results": [
                {
                    "test": r.test_name,
                    "success": r.success,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.test_results
            ]
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.message}")
        
        return summary
    
    def generate_test_report(self, output_file: Optional[str] = None) -> str:
        """Generate detailed test report"""
        if not output_file:
            output_file = f"neat_test_report_{int(time.time())}.json"
        
        summary = {
            "timestamp": time.time(),
            "space_id": self.space_id,
            "container_id": self.container_id,
            "view_id": self.view_id,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details
                }
                for r in self.test_results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📄 Test report saved to: {output_file}")
        return output_file


def main():
    """Main testing function"""
    print("🧪 NEAT Data Model Testing Suite")
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
        # Create tester and run tests
        tester = NeatDataModelTester()
        summary = tester.run_all_tests()
        
        # Generate report
        report_file = tester.generate_test_report()
        
        # Exit with appropriate code
        if summary['failed'] > 0:
            print(f"\n❌ Some tests failed. See {report_file} for details.")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed! Report: {report_file}")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
