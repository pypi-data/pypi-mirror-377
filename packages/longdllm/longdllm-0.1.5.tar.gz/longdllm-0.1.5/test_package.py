#!/usr/bin/env python3
"""
Test script to validate the LongDLLM package structure.
"""

import sys
import os

# Add the package to Python path for testing
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing LongDLLM package imports...")
    
    try:
        from longdllm import adapt_for_long_context
        print("✓ Main function import successful")
    except ImportError as e:
        print(f"✗ Main function import failed: {e}")
        return False
    
    try:
        from longdllm.rope_classes import LongRoPEScaledRotaryEmbedding, YaRNScaledRotaryEmbedding
        print("✓ RoPE classes import successful")
    except ImportError as e:
        print(f"✗ RoPE classes import failed: {e}")
        return False
    
    try:
        from longdllm.utils import get_model_info, validate_model_name
        print("✓ Utils import successful")
    except ImportError as e:
        print(f"✗ Utils import failed: {e}")
        return False
    
    return True

def test_model_info():
    """Test model information utilities."""
    print("\nTesting model information utilities...")
    
    try:
        from longdllm.utils import get_model_info, validate_model_name
        
        # Test supported models
        info = get_model_info("apple/DiffuCoder-7B-Instruct")
        assert info['type'] == 'diffucoder'
        print("✓ DiffuCoder info retrieval successful")
        
        info = get_model_info("GSAI-ML/LLaDA-8B-Instruct")
        assert info['type'] == 'llada'
        print("✓ LLaDA info retrieval successful")
        
        # Test validation
        normalized = validate_model_name("diffucoder-local-path")
        assert normalized == "apple/DiffuCoder-7B-Instruct"
        print("✓ Model name validation successful")
        
        return True
    except Exception as e:
        print(f"✗ Model info test failed: {e}")
        return False

def test_package_structure():
    """Test that package structure is correct."""
    print("\nTesting package structure...")
    
    required_files = [
        "longdllm/__init__.py",
        "longdllm/core.py", 
        "longdllm/rope_classes.py",
        "longdllm/utils.py",
        "longdllm/data/example_rescale_factors.txt",
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def main():
    """Run all tests."""
    print("LongDLLM Package Structure Test")
    print("=" * 50)
    
    tests = [
        test_package_structure,
        test_imports,
        test_model_info,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! Package structure is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
