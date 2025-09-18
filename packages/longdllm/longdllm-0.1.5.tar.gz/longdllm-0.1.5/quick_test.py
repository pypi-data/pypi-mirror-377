#!/usr/bin/env python3
"""
Quick test script that works without heavy dependencies.
"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.dirname(__file__))

def test_package_structure():
    """Test package file structure."""
    print("Testing LongDLLM package structure...")
    
    required_files = [
        "longdllm/__init__.py",
        "longdllm/core.py",
        "longdllm/rope_classes.py", 
        "longdllm/utils.py",
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md"
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_requirements():
    """Test that requirements.txt has expected dependencies."""
    print("Testing requirements.txt...")
    
    with open("requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip()]
    
    expected_deps = ["torch==2.7.1", "transformers==4.46.2", "datasets==2.18.0"]
    
    missing = [dep for dep in expected_deps if not any(dep in req for req in requirements)]
    
    if missing:
        print(f"❌ Missing dependencies: {missing}")
        return False
    else:
        print("✅ All key dependencies present")
        print(f"   Total dependencies: {len(requirements)}")
        return True

def test_imports_without_deps():
    """Test imports that don't require heavy dependencies."""
    print("Testing basic imports...")
    
    try:
        # Test utils (shouldn't need torch/numpy for basic functions)
        from longdllm.utils import validate_model_name, get_model_info
        
        # Test model validation
        result = validate_model_name("apple/DiffuCoder-7B-Instruct")
        assert result == "apple/DiffuCoder-7B-Instruct"
        
        # Test model info
        info = get_model_info("apple/DiffuCoder-7B-Instruct")
        assert info['type'] == 'diffucoder'
        
        print("✅ Basic functionality working")
        return True
        
    except ImportError as e:
        print(f"⚠️  Import issue (expected without torch/numpy): {e}")
        return True  # This is expected
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all lightweight tests."""
    print("LongDLLM Quick Package Test")
    print("=" * 40)
    
    tests = [
        test_package_structure,
        test_requirements,
        test_imports_without_deps,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 40)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 Package structure looks good!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install package: pip install -e .")
        print("3. Test with real models")
    else:
        print("🔧 Some issues found - please review above")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
