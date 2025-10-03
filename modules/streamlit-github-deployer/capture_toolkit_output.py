#!/usr/bin/env python3
"""
Capture Real Toolkit Output
This script captures the actual output from cdf commands to understand the exact format
"""

import os
import sys
import subprocess
import json
from datetime import datetime


def capture_command_output(cmd, description):
    """Capture command output and save to file"""
    print(f"📋 Capturing: {description}")
    print(f"🔧 Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "command": cmd,
            "description": description,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        # Print to console
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn Code: {result.returncode}")
        print("=" * 60)
        
        return output_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "command": cmd,
            "description": description,
            "error": str(e),
            "success": False
        }


def main():
    """Capture toolkit outputs for analysis"""
    print("📊 Cognite Toolkit Output Capture")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('CDF_PROJECT'):
        print("❌ CDF_PROJECT not set. Run: source cdfenv.sh && cdfenv bgfast")
        sys.exit(1)
    
    print(f"🔗 CDF Project: {os.getenv('CDF_PROJECT')}")
    print(f"🌐 CDF Cluster: {os.getenv('CDF_CLUSTER', 'Not set')}")
    print()
    
    # Collect all outputs
    outputs = []
    
    # 1. Capture build output
    print("1️⃣ Capturing BUILD output...")
    build_output = capture_command_output(
        "cdf build --env=weather",
        "Build weather module"
    )
    outputs.append(build_output)
    
    if build_output.get("success"):
        # 2. Capture dry-run output
        print("2️⃣ Capturing DRY-RUN output...")
        dry_run_output = capture_command_output(
            "cdf deploy --env=weather --dry-run",
            "Dry-run weather module deployment"
        )
        outputs.append(dry_run_output)
        
        # 3. Ask about actual deploy
        user_input = input("🤔 Capture actual DEPLOY output? This will modify CDF! (y/N): ")
        if user_input.lower() == 'y':
            print("3️⃣ Capturing DEPLOY output...")
            deploy_output = capture_command_output(
                "cdf deploy --env=weather",
                "Deploy weather module"
            )
            outputs.append(deploy_output)
        else:
            print("⏭️  Skipping deploy capture")
    else:
        print("❌ Build failed, skipping dry-run and deploy")
    
    # Save all outputs to file
    output_file = f"toolkit_outputs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(outputs, f, indent=2)
    
    print(f"💾 Saved outputs to: {output_file}")
    
    # Generate analysis
    print("\n📊 ANALYSIS:")
    print("=" * 40)
    
    for output in outputs:
        if output.get("success"):
            stdout = output.get("stdout", "")
            
            print(f"\n🔍 {output['description']}:")
            
            # Look for specific patterns
            if "Summary of Resources" in stdout:
                print("  ✅ Contains resource summary table")
            
            if "Would deploy" in stdout:
                print("  ✅ Contains deployment preview")
            
            if "Deploying" in stdout and "to CDF" in stdout:
                print("  ✅ Contains deployment progress")
            
            # Count lines for reference
            lines = stdout.split('\n')
            print(f"  📊 Output lines: {len(lines)}")
            
            # Show key sections
            for i, line in enumerate(lines):
                if "Summary of Resources" in line:
                    print(f"  📋 Summary table starts at line {i+1}")
                    # Show next few lines
                    for j in range(i, min(i+10, len(lines))):
                        if lines[j].strip():
                            print(f"    {lines[j]}")
                    break
    
    print(f"\n💡 Use this data to create realistic output in Streamlit!")
    print(f"📁 File: {output_file}")


if __name__ == "__main__":
    main()
