#!/usr/bin/env python3
"""
Fast syntax checker for Streamlit app
Run this before deploying to catch syntax errors quickly
"""

import ast
import sys
import os

def check_syntax(file_path):
    """Check Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source, filename=file_path)
        print(f"✅ {file_path}: Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path}: Syntax Error")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        if e.offset:
            print(f"   Position: {' ' * (e.offset - 1)}^")
        return False
        
    except Exception as e:
        print(f"❌ {file_path}: Error - {e}")
        return False

def check_all_python_files():
    """Check all Python files in the Streamlit app directory"""
    print("🔍 Checking Python syntax...")
    print("=" * 50)
    
    all_good = True
    python_files = []
    
    # Check the Streamlit app directory
    streamlit_dir = '../streamlit/github-repo-deployer'
    
    # Find all Python files in the Streamlit app
    for root, dirs, files in os.walk(streamlit_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Check each file
    for file_path in sorted(python_files):
        if not check_syntax(file_path):
            all_good = False
    
    print("=" * 50)
    if all_good:
        print("🎉 All Python files have valid syntax!")
        return True
    else:
        print("💥 Some files have syntax errors!")
        return False

if __name__ == "__main__":
    success = check_all_python_files()
    sys.exit(0 if success else 1)
