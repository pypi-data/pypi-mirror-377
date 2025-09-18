#!/usr/bin/env python3
"""
Debug script for LongDLLM package installation issues.
This helps identify dependency conflicts and suggests solutions.
"""

import sys
import subprocess
import os

def check_current_environment():
    """Check current environment and installed packages."""
    print("🔍 Current Environment Analysis")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if in conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'None')
    print(f"Conda environment: {conda_env}")
    
    # Check key packages
    packages_to_check = [
        'torch', 'transformers', 'flash_attn', 'numpy', 'datasets'
    ]
    
    print(f"\\nInstalled packages:")
    for package in packages_to_check:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"  ✅ {package}: {version}")
        except ImportError:
            print(f"  ❌ {package}: Not installed")
    
    return True


def check_flash_attention():
    """Specifically check flash attention installation."""
    print(f"\\n🔍 Flash Attention Analysis")
    print("=" * 50)
    
    try:
        import flash_attn
        print(f"✅ flash_attn version: {flash_attn.__version__}")
        
        # Check for the problematic .so file
        import flash_attn.flash_attn_cuda
        print("✅ CUDA extension loads successfully")
        
    except ImportError as e:
        print(f"❌ flash_attn import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ flash_attn CUDA extension failed: {e}")
        print("💡 This is likely the 'undefined symbol' error")
        return False
    
    return True


def suggest_solutions():
    """Suggest solutions for common installation issues."""
    print(f"\\n💡 Solutions for Installation Issues")
    print("=" * 50)
    
    print("🎯 Option 1: Test without installation (RECOMMENDED)")
    print("   # Add to your test script:")
    print("   import sys")
    print("   sys.path.insert(0, '/home/t-albertge/longdllm')")
    print("   import longdllm")
    print("   ✅ Avoids all pip install conflicts")
    
    print(f"\\n🎯 Option 2: Minimal installation")
    print("   # Create minimal pyproject.toml with only essential deps:")
    print("   dependencies = ['torch>=2.0.0', 'transformers>=4.40.0']")
    print("   # Then: pip install -e . --no-deps")
    print("   ✅ Doesn't reinstall existing packages")
    
    print(f"\\n🎯 Option 3: Fix flash-attn conflict")
    print("   # Uninstall conflicting version:")
    print("   pip uninstall flash-attn")
    print("   # Reinstall compatible version:")
    print("   pip install flash-attn --no-cache-dir")
    print("   ✅ May resolve symbol conflicts")
    
    print(f"\\n🎯 Option 4: Clean environment (for fresh machine testing)")
    print("   conda create -n test_fresh python=3.10")
    print("   conda activate test_fresh")
    print("   pip install torch transformers flash-attn")
    print("   pip install -e /path/to/longdllm")
    print("   ✅ Simulates fresh machine installation")


def create_no_install_test_example():
    """Create an example script that doesn't require installation."""
    print(f"\\n📝 Creating No-Install Test Script")
    print("=" * 50)
    
    example_script = '''#!/usr/bin/env python3
"""
Example: Test LongDLLM without pip installation
"""
import sys
sys.path.insert(0, '/home/t-albertge/longdllm')

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import longdllm

def test_your_model():
    # Replace with your model path
    MODEL_PATH = "YOUR_MODEL_PATH_HERE"
    
    # Load model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Apply LongDLLM (this is where the dictionary error was happening)
    print("Applying LongDLLM adaptation...")
    model = longdllm.adapt_for_long_context(model, target_length=32768)
    
    # Test unified interface
    print("Testing diffusion_generate...")
    test_input = "What is the capital of France?"
    input_ids = tokenizer(test_input, return_tensors="pt").input_ids.to(model.device)
    
    outputs = model.diffusion_generate(
        input_ids=input_ids,
        max_new_tokens=10,
        temperature=0.0,
        steps=32
    )
    
    response = tokenizer.decode(outputs[0, input_ids.shape[1]:], skip_special_tokens=True)
    print(f"Response: {response}")
    
    return True

if __name__ == "__main__":
    test_your_model()
'''
    
    with open('/home/t-albertge/longdllm/test_example_no_install.py', 'w') as f:
        f.write(example_script)
    
    print("✅ Created: test_example_no_install.py")
    print("💡 Edit the MODEL_PATH and run this script to test your model")


def main():
    """Main debugging function."""
    print("🔧 LongDLLM Installation Debug")
    print("=" * 60)
    
    # Check current environment
    env_ok = check_current_environment()
    
    # Check flash attention specifically
    flash_ok = check_flash_attention()
    
    # Show solutions
    suggest_solutions()
    
    # Create example
    create_no_install_test_example()
    
    print(f"\\n📊 Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   Flash Attention: {'✅' if flash_ok else '❌'}")
    
    if not flash_ok:
        print(f"\\n⚠️  Flash Attention Issue Detected!")
        print("   This is likely causing your pip install -e . problems")
        print("   Use Option 1 (no installation) for testing")
    
    print(f"\\n🎯 Recommended Next Steps:")
    print("   1. Use test_example_no_install.py (no pip install needed)")
    print("   2. Edit the MODEL_PATH in the script")
    print("   3. Run with your actual model to test functionality")


if __name__ == "__main__":
    main()
