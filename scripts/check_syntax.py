#!/usr/bin/env python3
"""
Syntax Checker for Python Files

Pre-deployment syntax validation tool as per cursor-prompts.md guidelines.

Usage:
    python scripts/check_syntax.py path/to/file.py
    python scripts/check_syntax.py modules/hw-function/streamlit/hw-function-ui/main.py
"""

import sys
import py_compile
import shutil
from pathlib import Path


def check_syntax(file_path: str) -> bool:
    """
    Check Python file syntax and clean up temporary files.
    
    Args:
        file_path: Full path to Python file to check
        
    Returns:
        bool: True if syntax is valid, False otherwise
    """
    file_path = Path(file_path)
    
    # Validate file exists
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    # Validate it's a Python file
    if file_path.suffix != '.py':
        print(f"❌ Error: Not a Python file: {file_path}")
        return False
    
    print(f"🔍 Checking syntax: {file_path}")
    
    try:
        # Compile the Python file
        py_compile.compile(str(file_path), doraise=True)
        print(f"✅ Syntax check passed!")
        
        # Clean up __pycache__ directory
        pycache_dir = file_path.parent / '__pycache__'
        if pycache_dir.exists():
            shutil.rmtree(pycache_dir)
            print(f"🧹 Cleaned up: {pycache_dir}")
        
        # Clean up .pyc file if it exists in same directory
        pyc_file = file_path.with_suffix('.pyc')
        if pyc_file.exists():
            pyc_file.unlink()
            print(f"🧹 Cleaned up: {pyc_file}")
        
        return True
        
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error found:")
        print(f"\n{e}\n")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_syntax.py <file_path>")
        print("\nExample:")
        print("  python scripts/check_syntax.py modules/hw-function/streamlit/hw-function-ui/main.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("=" * 70)
    print("Python Syntax Checker")
    print("=" * 70)
    
    success = check_syntax(file_path)
    
    print("=" * 70)
    
    if success:
        print("✅ Ready for deployment!")
        sys.exit(0)
    else:
        print("❌ Fix syntax errors before deploying!")
        print("\nReminder from cursor-prompts.md:")
        print("  'CRITICAL: Never deploy without syntax validation!'")
        print("  'Basic Python syntax errors should never reach SaaS deployment'")
        sys.exit(1)


if __name__ == "__main__":
    main()
