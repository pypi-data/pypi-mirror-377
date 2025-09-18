#!/usr/bin/env python3
"""
Quick validation script for LongDLLM package.
This demonstrates the three main testing approaches without requiring specific models.
"""

import os
import sys
from pathlib import Path

def test_basic_imports():
    """Test 1: Basic import validation (5 seconds)"""
    print("🧪 Test 1: Basic Import Validation")
    print("-" * 40)
    
    try:
        import longdllm
        print(f"✅ Package version: {longdllm.__version__}")
        
        from longdllm import adapt_for_long_context
        print("✅ Core function imported")
        
        from longdllm.diffucoder_patches import patch_diffucoder_diffusion_generate
        print("✅ DiffuCoder patches imported")
        
        from longdllm.llada_patches import patch_llada_forward_methods
        print("✅ LLaDA patches imported")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_mock_functionality():
    """Test 2: Mock testing (30 seconds)"""
    print("\n🧪 Test 2: Mock Functionality")
    print("-" * 40)
    
    try:
        from unittest.mock import MagicMock
        import torch
        from longdllm import adapt_for_long_context
        
        # Create mock DiffuCoder model
        mock_diffucoder = MagicMock()
        mock_diffucoder.config.model_type = 'dream'
        mock_diffucoder.config.max_position_embeddings = 4096
        mock_diffucoder.device = torch.device('cpu')
        
        # Mock the RoPE structure
        mock_rope = MagicMock()
        mock_rope.dim = 64
        mock_rope.max_seq_len_cached = 4096
        mock_diffucoder.model.layers = [MagicMock()]
        mock_diffucoder.model.layers[0].self_attn.rotary_emb = mock_rope
        
        # Test adaptation
        adapted_model = adapt_for_long_context(mock_diffucoder, target_length=32768)
        print("✅ DiffuCoder mock adaptation successful")
        
        # Test LLaDA mock
        mock_llada = MagicMock()
        mock_llada.config.model_type = 'llada'
        mock_llada.config.max_position_embeddings = 4096
        mock_llada.device = torch.device('cpu')
        mock_llada.model.layers = [MagicMock()]
        mock_llada.model.layers[0].self_attn.rotary_emb = mock_rope
        
        adapted_llada = adapt_for_long_context(mock_llada, target_length=32768)
        print("✅ LLaDA mock adaptation successful")
        
        print("🎉 Mock testing successful!")
        return True
        
    except Exception as e:
        print(f"❌ Mock testing failed: {e}")
        return False


def test_passkey_files():
    """Test 3: Check available passkey files"""
    print("\n🧪 Test 3: Passkey File Discovery")
    print("-" * 40)
    
    # Search for passkey files
    search_paths = [
        "/home/t-albertge/v2-longrope/analysis/attention_map",
        "/home/t-albertge",
        "."
    ]
    
    found_files = []
    for search_path in search_paths:
        if os.path.exists(search_path):
            for file in os.listdir(search_path):
                if 'passkey' in file.lower() and file.endswith('.txt'):
                    full_path = os.path.join(search_path, file)
                    found_files.append(full_path)
    
    if found_files:
        print(f"✅ Found {len(found_files)} passkey test files:")
        for file in sorted(found_files):
            # Get file size for context length estimation
            try:
                file_size = os.path.getsize(file)
                # Rough estimation: ~4 chars per token
                estimated_tokens = file_size // 4
                print(f"   📄 {os.path.basename(file)} ({estimated_tokens:,} tokens est.)")
            except:
                print(f"   📄 {os.path.basename(file)}")
        
        # Show example usage
        print(f"\n💡 To test with these files, run:")
        print(f"python examples/test_passkey_evaluation.py --model YOUR_MODEL --test-files {found_files[0]}")
        
        return True
    else:
        print("❌ No passkey files found")
        print("Available .txt files:")
        for search_path in search_paths:
            if os.path.exists(search_path):
                txt_files = [f for f in os.listdir(search_path) if f.endswith('.txt')]
                print(f"   {search_path}: {txt_files}")
        return False


def show_testing_guide():
    """Show comprehensive testing guide"""
    print("\n📋 LongDLLM Testing Guide")
    print("=" * 60)
    
    print("\n🎯 RECOMMENDED TESTING WORKFLOW:")
    print("1. ✅ Basic imports (completed above)")
    print("2. ✅ Mock functionality (completed above)")
    print("3. 🧪 Real model testing (use examples below)")
    print("4. 🚀 Production validation (with your actual models)")
    
    print("\n🔧 EXAMPLE COMMANDS:")
    print()
    print("# Test with a small model for quick validation:")
    print("python examples/test_passkey_evaluation.py \\")
    print("  --model microsoft/DialoGPT-medium \\")
    print("  --target-length 8192 \\")
    print("  --max-new-tokens 10")
    print()
    print("# Test DiffuCoder model:")
    print("python examples/test_passkey_evaluation.py \\")
    print("  --model YOUR_DIFFUCODER_MODEL_PATH \\")
    print("  --target-length 32768 \\")
    print("  --max-new-tokens 20 \\")
    print("  --output-file results_diffucoder.txt")
    print()
    print("# Test LLaDA model:")
    print("python examples/test_passkey_evaluation.py \\")
    print("  --model YOUR_LLADA_MODEL_PATH \\")
    print("  --target-length 65536 \\")
    print("  --max-new-tokens 20 \\")
    print("  --show-responses")
    
    print("\n📊 WHAT TO EXPECT:")
    print("✅ Successful test shows:")
    print("   - Model loads and adapts without errors")
    print("   - diffusion_generate method is available")
    print("   - Generated response contains the correct passkey number")
    print("   - Memory usage stays reasonable for long contexts")
    
    print("\n❌ Common issues:")
    print("   - CUDA OOM: Reduce target_length or use smaller model")
    print("   - Import errors: Check model paths and dependencies")
    print("   - Wrong passkey: May indicate attention/RoPE issues")
    
    print("\n💡 DEVELOPMENT TIPS:")
    print("   - Start with short passkey files for quick iteration")
    print("   - Use --verbose flag for detailed logging")
    print("   - Save results to files for comparison")
    print("   - Test both DiffuCoder and LLaDA models if available")


def main():
    """Main validation function."""
    print("🎯 LongDLLM Package Validation")
    print("=" * 60)
    print("This script validates your LongDLLM installation and shows testing approaches.")
    
    # Run validation tests
    import_success = test_basic_imports()
    mock_success = test_mock_functionality()
    files_found = test_passkey_files()
    
    # Summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"   Basic Imports: {'✅' if import_success else '❌'}")
    print(f"   Mock Testing: {'✅' if mock_success else '❌'}")
    print(f"   Test Files: {'✅' if files_found else '❌'}")
    
    if import_success and mock_success:
        print(f"\n🎉 Package is ready for testing!")
        show_testing_guide()
    else:
        print(f"\n❌ Please fix the issues above before proceeding.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
